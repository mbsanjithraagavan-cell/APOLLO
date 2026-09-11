from datetime import datetime, timezone
from uuid import uuid4
import pytest

from app import web_workflow as workflow
from app.web_workflow import BookingInterpretation, _allocate, _fallback_interpretation

def option(doctor, hour, slot=None):
    return {"doctor":{"doctor_id":doctor,"doctor_name":doctor}, "specialty":"cardiology",
      "slot":{"slot_id":slot or str(uuid4()),"start_time":datetime(2026,9,12,hour,tzinfo=timezone.utc).isoformat()}}

def test_booking_interpretation_schema_rejects_trusted_fields():
    assert BookingInterpretation(intent="BOOK_APPOINTMENT",treatment="Heart Consultation",specialty="cardiology").specialty == "cardiology"
    with pytest.raises(Exception): BookingInterpretation(intent="BOOK_APPOINTMENT",doctor_id="x")

def test_observed_gemma_json_shape_is_narrowly_normalized():
    parsed=BookingInterpretation.model_validate({"intent":"Skin Consultation","specialty":"dermatology","date_preference":"tomorrow","time_preference":"morning","doctor_preference":None,"selection_preference":None})
    assert parsed.intent == "BOOK_APPOINTMENT" and parsed.treatment == "Skin Consultation"

def test_observed_cardiology_alias_is_narrowly_normalized():
    parsed=BookingInterpretation.model_validate({"intent":"FIND_APPOINTMENT","treatment":"Cardiology","specialty":"general","date_preference":"2026-09-12","time_preference":"morning","doctor_preference":None,"selection_preference":None})
    assert (parsed.intent,parsed.treatment,parsed.specialty)==("BOOK_APPOINTMENT","Heart Consultation","cardiology")

def test_deterministic_fallback_supports_cardiology_and_dermatology():
    assert _fallback_interpretation("cardiologist tomorrow").treatment == "Heart Consultation"
    assert _fallback_interpretation("skin specialist tomorrow morning").specialty == "dermatology"
    assert _fallback_interpretation("unsupported neurology").specialty is None

def test_allocator_ranks_real_slots_by_preference_and_time():
    morning, afternoon = option("Dr A",9), option("Dr B",15)
    intent=BookingInterpretation(intent="BOOK_APPOINTMENT", specialty="cardiology", time_preference="morning")
    selected,_=_allocate([afternoon,morning],intent); assert selected is morning
    intent.time_preference="afternoon"; selected,_=_allocate([morning,afternoon],intent); assert selected is afternoon
    intent.time_preference=None; intent.selection_preference="earliest"; selected,_=_allocate([afternoon,morning],intent); assert selected is morning
    intent.doctor_preference="Dr B"; selected,_=_allocate([morning,afternoon],intent); assert selected is afternoon
    assert selected in [morning,afternoon]

def test_safety_short_circuits_before_interpretation_or_mcp(monkeypatch):
    called=[]
    monkeypatch.setattr(workflow,"_interpret_booking",lambda *a: called.append("gemma"))
    monkeypatch.setattr(workflow,"mcp_call",lambda *a: called.append("mcp"))
    result=workflow.agent_booking_plan("I cannot breathe and have chest pain",uuid4())
    assert result["status"] == "emergency" and called == []

def test_plan_never_books_and_requires_confirmation(monkeypatch):
    doctor={"doctor_id":str(uuid4()),"doctor_name":"Dr Demo"}; slot={"slot_id":str(uuid4()),"start_time":"2026-09-12T09:00:00+00:00"}
    monkeypatch.setattr(workflow,"_interpret_booking",lambda *a:(BookingInterpretation(intent="BOOK_APPOINTMENT",treatment="Heart Consultation",specialty="cardiology"),"gemma"))
    monkeypatch.setattr(workflow,"mcp_call",lambda name,req,rid:[doctor] if name=="list_available_doctors" else [slot])
    monkeypatch.setattr(workflow,"preview",lambda *a,**k:{"status":"preview","doctor":doctor,"slot":slot,"billing":{}})
    result=workflow.agent_booking_plan("book cardiology",uuid4())
    assert result["requires_confirmation"] is True and result["status"] == "planned"
