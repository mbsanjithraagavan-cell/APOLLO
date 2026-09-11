from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.config import Settings
from app.schemas import (
    BillingBreakdown, BillingItem, BookingIntent, EscalationRecord, IntentType,
    LeaseResult, NotificationPayload, PolicyChunk, SafetyAssessment, SlotCandidate,
)
from app.state import STATE_ADAPTER, create_state, llm_view


@pytest.fixture(autouse=True)
def clean_config_environment(monkeypatch):
    for key in ("APOLLO_MODEL_DIR", "APOLLO_EMBEDDER_DIR", "APOLLO_EMBEDDING_DIMENSION",
                "DATABASE_URL", "REDIS_URL", "APOLLO_ENV", "APOLLO_LOG_LEVEL",
                "RAG_TOP_K", "SAFETY_CONFIDENCE_THRESHOLD", "REDIS_LEASE_SECONDS"):
        monkeypatch.delenv(key, raising=False)


def test_config_defaults():
    config = Settings.from_environment()
    assert str(config.model_dir) == r"C:\SLM-WORKSHOP\models\it"
    assert str(config.embedder_dir) == r"C:\SLM-WORKSHOP\models\embedder"
    assert config.safety_confidence_threshold == 0.7
    assert config.redis_lease_seconds == 45
    assert config.database_url is None
    assert config.redis_url is None


def test_config_loads_all_environment_fields(monkeypatch):
    values = {"APOLLO_MODEL_DIR": r"D:\resources\gemma",
              "APOLLO_EMBEDDER_DIR": r"D:\resources\embedder",
              "DATABASE_URL": "postgresql://user:private-password@localhost/apollo",
              "REDIS_URL": "rediss://localhost:6379/0", "APOLLO_ENV": "test",
              "APOLLO_LOG_LEVEL": "DEBUG", "RAG_TOP_K": "5",
              "SAFETY_CONFIDENCE_THRESHOLD": "0.85", "REDIS_LEASE_SECONDS": "60"}
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    config = Settings.from_environment()
    assert str(config.model_dir) == values["APOLLO_MODEL_DIR"]
    assert str(config.embedder_dir) == values["APOLLO_EMBEDDER_DIR"]
    assert config.database_url.get_secret_value() == values["DATABASE_URL"]
    assert config.redis_url.get_secret_value() == values["REDIS_URL"]
    assert (config.environment, config.log_level, config.rag_top_k) == ("test", "DEBUG", 5)
    assert (config.safety_confidence_threshold, config.redis_lease_seconds) == (0.85, 60)
    assert "private-password" not in repr(config)
    assert "private-password" not in config.model_dump_json()


@pytest.mark.parametrize("value", ["1.01", "-0.01", "nan", "inf"])
def test_invalid_confidence_config(monkeypatch, value):
    monkeypatch.setenv("SAFETY_CONFIDENCE_THRESHOLD", value)
    with pytest.raises(ValidationError):
        Settings.from_environment()


@pytest.mark.parametrize("value", ["0", "-1", "301", "1.5", "not-an-int"])
def test_invalid_lease_duration(monkeypatch, value):
    monkeypatch.setenv("REDIS_LEASE_SECONDS", value)
    with pytest.raises(ValidationError):
        Settings.from_environment()


@pytest.mark.parametrize("value", [1, 45, 300])
def test_valid_lease_duration(value):
    assert Settings(redis_lease_seconds=value).redis_lease_seconds == value


@pytest.mark.parametrize("values", [
    {"rag_top_k": 0}, {"model_dir": "relative/model"}, {"environment": "typo"},
    {"database_url": "https://localhost"}, {"redis_url": "redis://"},
    {"redis_lease_seconds": True},
])
def test_invalid_config_fields(values):
    with pytest.raises(ValidationError):
        Settings(**values)


def test_booking_intent_can_start_without_patient_pii():
    intent = BookingIntent(specialty="cardiology", date_from=date(2026, 10, 1))
    assert intent.intent == IntentType.BOOKING
    assert intent.explicit_confirmation is False
    assert intent.patient_reference is None


@pytest.mark.parametrize("values", [
    {}, {"specialty": ""}, {"specialty": "cardiology", "explicit_confirmation": "yes"},
    {"specialty": "cardiology", "explicit_confirmation": True},
    {"specialty": "cardiology", "patient_reference": "invalid"},
    {"specialty": "cardiology", "date_from": "2026-10-02", "date_to": "2026-10-01"},
    {"specialty": "cardiology", "patient_name": "Raw Patient Name"},
])
def test_booking_intent_rejects_invalid_or_pii_fields(values):
    with pytest.raises(ValidationError):
        BookingIntent(**values)


def test_explicit_booking_confirmation_contract():
    intent = BookingIntent(patient_reference=uuid4(), slot_id=uuid4(),
                           idempotency_key=uuid4(), explicit_confirmation=True)
    assert intent.explicit_confirmation is True


def test_decimal_billing_is_exact_and_not_user_supplied_total():
    item = BillingItem(code="consultation", description="Consultation",
                       quantity=3, unit_amount="0.10")
    bill = BillingBreakdown(items=(item,), discount="0.05", tax=Decimal("0.02"))
    assert isinstance(item.unit_amount, Decimal)
    assert item.line_total == Decimal("0.30")
    assert bill.subtotal == Decimal("0.30")
    assert bill.total == Decimal("0.27")
    roundtrip = BillingBreakdown.model_validate_json(bill.model_dump_json(round_trip=True))
    assert roundtrip.total == Decimal("0.27")
    with pytest.raises(ValidationError):
        BillingBreakdown(items=(item,), total="0.00")
    with pytest.raises(ValidationError):
        BillingBreakdown(items=(item,), discount="0.31")


@pytest.mark.parametrize("amount", [0.1, True, "-0.01", "0.001", "NaN", "Infinity"])
def test_inexact_or_invalid_money_is_rejected(amount):
    with pytest.raises(ValidationError):
        BillingItem(code="fee", description="Fee", unit_amount=amount)


@pytest.mark.parametrize("confidence", [-0.01, 1.01, float("nan"), float("inf")])
def test_safety_confidence_is_bounded(confidence):
    with pytest.raises(ValidationError):
        SafetyAssessment(disposition="allow", confidence=confidence, reason_code="scope_ok")


def test_safety_assessment_contract():
    assessment = SafetyAssessment(disposition="emergency", confidence=0.9,
                                  reason_code="emergency_signal")
    assert assessment.disposition == "emergency"
    with pytest.raises(ValidationError):
        SafetyAssessment(disposition="diagnose", confidence=1, reason_code="scope_ok")
    with pytest.raises(ValidationError):
        SafetyAssessment(disposition="allow", confidence=1, reason_code="User said private text")


def test_slot_and_lease_validation():
    start = datetime(2026, 10, 1, 10, tzinfo=timezone.utc)
    slot = SlotCandidate(slot_id=uuid4(), doctor_id=uuid4(), starts_at=start,
                         ends_at=start + timedelta(minutes=30), fee="350.00")
    assert slot.fee == Decimal("350.00")
    with pytest.raises(ValidationError):
        SlotCandidate(slot_id=slot.slot_id, doctor_id=slot.doctor_id,
                      starts_at=start, ends_at=start, fee="350.00")
    with pytest.raises(ValidationError):
        SlotCandidate(slot_id=slot.slot_id, doctor_id=slot.doctor_id,
                      starts_at=start.replace(tzinfo=None), ends_at=start, fee="350.00")
    lease = LeaseResult(acquired=True, slot_id=slot.slot_id,
                        lease_reference=uuid4(), expires_at=start + timedelta(seconds=45))
    assert lease.acquired
    with pytest.raises(ValidationError):
        LeaseResult(acquired=True, slot_id=slot.slot_id)
    assert not LeaseResult(acquired=False, slot_id=slot.slot_id, failure_code="busy").acquired


def test_policy_escalation_and_notification_contracts():
    chunk = PolicyChunk(policy_id="prep", revision="1", chunk_id="prep-1",
                        content="Bring the appointment reference.", source="approved/prep.md",
                        similarity=0.8)
    assert chunk.revision == "1"
    escalation = EscalationRecord(escalation_id=uuid4(), request_id=uuid4(),
                                 reason_code="clinical_scope", created_at=datetime.now(timezone.utc))
    assert escalation.status == "pending"
    notification = NotificationPayload(notification_id=uuid4(), booking_reference=uuid4(),
                                       recipient_reference=uuid4())
    assert notification.channel == "simulation"
    with pytest.raises(ValidationError):
        NotificationPayload(notification_id=uuid4(), booking_reference=uuid4(),
                            recipient_reference=uuid4(), email="patient@example.test")


def test_apollo_state_creation_and_serialization():
    session = uuid4()
    state = create_state("Find an outpatient appointment", session_id=session)
    other = create_state("Policy question", session_id=session)
    assert state["session_id"] == other["session_id"]
    assert state["request_id"] != other["request_id"]
    assert state["booking_status"] == "not_started"
    assert state["intent"] == IntentType.UNKNOWN
    assert state["errors"] == ()
    restored = STATE_ADAPTER.validate_json(STATE_ADAPTER.dump_json(state, round_trip=True))
    assert restored == state
    for field in ("early_safety", "policy_chunks", "slots", "lease", "billing",
                  "booking_reference", "notification", "trace", "errors"):
        assert field in state


def test_state_forbids_secrets_and_llm_view_excludes_private_references():
    state = create_state("Find a slot for [PERSON]")
    with pytest.raises(ValidationError):
        STATE_ADAPTER.validate_python({**state, "database_url": "private-secret"})
    state["booking_intent"] = BookingIntent(specialty="cardiology", patient_reference=uuid4())
    view = llm_view(state)
    assert set(view) == {"sanitized_input", "intent"}
    assert "patient_reference" not in str(view)
    assert "session_id" not in view
    with pytest.raises(ValidationError):
        create_state("")

