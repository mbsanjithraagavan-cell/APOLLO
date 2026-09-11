"""Thin, local-only HTTP interface to APOLLO orchestration."""
from pathlib import Path
from uuid import UUID, uuid4
from typing import Literal
import os

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, ConfigDict, Field, StrictBool
from app import web_workflow as workflow
from app.treatments import TREATMENTS, specialty_for_treatment

app = FastAPI(title="APOLLO local demo", docs_url="/api/docs")


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BookingPreview(Contract):
    treatment: str = Field(min_length=1, max_length=100)
    doctor_id: UUID
    slot_id: UUID
    message: str = Field(default="Book appointment", min_length=1, max_length=2000)


class BookingConfirm(BookingPreview):
    patient_id: UUID = UUID("00000000-0000-0000-0000-000000000011")
    confirmed: StrictBool


class PolicyRequest(Contract):
    question: str = Field(min_length=1, max_length=2000)


class SafetyRequest(Contract):
    message: str = Field(min_length=1, max_length=2000)

class AgentBookingRequest(Contract):
    message: str = Field(min_length=1, max_length=2000)

class AgentBookingConfirm(Contract):
    treatment: str
    doctor_id: UUID
    slot_id: UUID
    confirmed: StrictBool
    message: str = Field(min_length=1, max_length=2000)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse(status_code=422, content={"detail": "Check the required fields and select a supported value."})


@app.exception_handler(Exception)
async def service_error(request, exc):
    return JSONResponse(status_code=503, content={"detail": "APOLLO could not reach a required local service. Check the backend terminal and service configuration."})


@app.exception_handler(ValueError)
async def conflict(request, exc):
    return JSONResponse(status_code=409, content={"detail": "The selection is unavailable or invalid. Refresh availability and choose again."})


@app.get("/api/health")
def health(): return workflow.health()


@app.get("/api/treatments")
def treatments(): return [{"name": k, "specialty": v} for k, v in TREATMENTS.items()]


@app.get("/api/doctors")
def doctors(treatment: str):
    specialty = specialty_for_treatment(treatment)
    return workflow.mcp_call("list_available_doctors", {"specialty": specialty}, uuid4())


@app.get("/api/doctors/{doctor_id}/slots")
def slots(doctor_id: UUID):
    return workflow.mcp_call("list_available_slots", {"doctor_id": str(doctor_id)}, uuid4())


@app.post("/api/booking/preview")
def preview(request: BookingPreview):
    return workflow.preview(request.treatment, request.doctor_id, request.slot_id, request.message, uuid4())


@app.post("/api/booking/confirm")
def confirm(request: BookingConfirm):
    if not request.confirmed:
        raise HTTPException(422, "Explicit confirmation is required.")
    if request.patient_id != UUID("00000000-0000-0000-0000-000000000011"):
        raise HTTPException(422, "This local demo supports only the fictional demo patient.")
    return workflow.confirm(request, uuid4())

@app.post("/api/agent/booking/plan")
def agent_booking_plan(request: AgentBookingRequest):
    return workflow.agent_booking_plan(request.message, uuid4())

@app.post("/api/agent/booking/confirm")
def agent_booking_confirm(request: AgentBookingConfirm):
    if not request.confirmed:
        raise HTTPException(422, "Explicit confirmation is required.")
    return workflow.confirm(BookingConfirm(treatment=request.treatment, doctor_id=request.doctor_id,
                            slot_id=request.slot_id, message=request.message, confirmed=True), uuid4())


@app.post("/api/policy/query")
def policy(request: PolicyRequest): return workflow.policy(request.question, uuid4())


@app.post("/api/safety/check")
def safety(request: SafetyRequest): return workflow.assessment_result(request.message, uuid4())


@app.get("/api/traces/{request_id}")
def traces(request_id: UUID):
    return {"request_id": str(request_id), "events": workflow.TRACES.get(str(request_id), [])}


@app.get("/api/appointments/{appointment_id}")
def appointment(appointment_id: UUID):
    result = workflow.RESULTS.get(str(appointment_id))
    if result is None:
        raise HTTPException(404, "Confirmation is not available in this local session.")
    return result


@app.get("/api/confirmations/{appointment_id}/{kind}")
def confirmation_file(appointment_id: UUID, kind: Literal["html", "pdf"]):
    path = workflow.OUTPUT / f"appointment-{appointment_id}.{kind}"
    if not path.is_file():
        raise HTTPException(404, "Confirmation file is not available.")
    return FileResponse(path, media_type="text/html" if kind == "html" else "application/pdf",
                        headers={"Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'"})


@app.post("/api/demo/reset")
def reset():
    if os.getenv("APOLLO_ENABLE_DEMO_RESET") != "1":
        raise HTTPException(404, "Demo reset is disabled.")
    return workflow.ApolloRuntime().reset_fictional_demo()
