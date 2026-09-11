from uuid import UUID
from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, StrictBool
from app.booking import Gatekeeper
from app.config import Settings
from app.services.database import DatabaseService
from app.services.redis import RedisLeaseService
from app.schemas import SlotCandidate, LeaseResult

server = FastMCP("APOLLO", instructions="Outpatient administration only. No clinical advice.")
settings = Settings.from_environment()
database = DatabaseService(settings.database_url.get_secret_value()) if settings.database_url else None
leases = RedisLeaseService(settings.redis_url.get_secret_value(), settings.redis_lease_seconds) if settings.redis_url else None
gatekeeper = Gatekeeper(database) if database else None

class SlotSearchInput(BaseModel):
    model_config=ConfigDict(extra="forbid", frozen=True)
    specialty: str = Field(min_length=1,max_length=100)
class DoctorSearchInput(BaseModel):
    model_config=ConfigDict(extra="forbid", frozen=True)
    specialty: str = Field(min_length=1,max_length=100)
class DoctorSlotsInput(BaseModel):
    model_config=ConfigDict(extra="forbid", frozen=True)
    doctor_id: UUID

class LeaseInput(BaseModel):
    model_config=ConfigDict(extra="forbid", frozen=True)
    slot_id: UUID
class BookingInput(BaseModel):
    model_config=ConfigDict(extra="forbid", frozen=True)
    patient_id: UUID
    slot_id: UUID
    idempotency_key: UUID
    lease_token: UUID
    explicit_confirmation: StrictBool

@server.tool
def capabilities() -> dict[str,str|bool]:
    return {"phase":"booking","booking_enabled":database is not None and leases is not None}

@server.tool
def search_doctor_slots(request: SlotSearchInput) -> list[SlotCandidate]:
    if database is None: raise RuntimeError("database_not_configured")
    return database.search_slots(" ".join(request.specialty.strip().lower().split()))

@server.tool
def stage_slot_lease(request: LeaseInput) -> LeaseResult:
    if leases is None: raise RuntimeError("redis_not_configured")
    return leases.stage(request.slot_id)

@server.tool
def list_available_doctors(request: DoctorSearchInput) -> list[dict]:
    if database is None:
        raise RuntimeError("database_not_configured")
    return database.list_available_doctors(request.specialty.strip().lower())

@server.tool
def list_available_slots(request: DoctorSlotsInput) -> list[dict]:
    if database is None:
        raise RuntimeError("database_not_configured")
    return database.list_available_slots(request.doctor_id)

@server.tool
def commit_slot_booking(request: BookingInput) -> UUID:
    if database is None or leases is None or gatekeeper is None: raise RuntimeError("booking_not_configured")
    key=f"apollo:lease:{request.slot_id}"
    token=leases.client.get(key)
    if token != str(request.lease_token): raise ValueError("invalid_or_expired_lease")
    with database.connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id,doctor_id,starts_at,ends_at,(SELECT amount FROM tariffs WHERE code='CONSULT'),(SELECT currency FROM tariffs WHERE code='CONSULT') FROM slots WHERE id=%s AND is_booked=FALSE",(request.slot_id,))
        row=cur.fetchone()
        if not row: raise ValueError("slot_unavailable")
        slot=__import__("app.schemas",fromlist=["SlotCandidate"]).SlotCandidate(slot_id=row[0],doctor_id=row[1],starts_at=row[2],ends_at=row[3],fee=row[4],currency=row[5])
        from app.schemas import BookingIntent
        intent=BookingIntent(patient_reference=request.patient_id,slot_id=request.slot_id,idempotency_key=request.idempotency_key,specialty="unknown")
        gatekeeper.validate(intent,slot,explicit_confirmation=request.explicit_confirmation)
        cur.execute("UPDATE slots SET is_booked=TRUE WHERE id=%s AND is_booked=FALSE RETURNING id",(request.slot_id,))
        if not cur.fetchone(): raise ValueError("slot_unavailable")
        appointment_id=__import__("uuid").uuid4()
        cur.execute("INSERT INTO appointments(id,patient_id,slot_id,tariff_code,amount,currency,idempotency_key) VALUES (%s,%s,%s,'CONSULT',(SELECT amount FROM tariffs WHERE code='CONSULT'),(SELECT currency FROM tariffs WHERE code='CONSULT'),%s) ON CONFLICT (idempotency_key) DO NOTHING RETURNING id",(appointment_id,request.patient_id,request.slot_id,request.idempotency_key))
        result=cur.fetchone()
        if not result:
            cur.execute("SELECT id FROM appointments WHERE idempotency_key=%s",(request.idempotency_key,)); result=cur.fetchone()
        conn.commit()
    leases.client.delete(key)
    return result[0]

if __name__=="__main__": server.run(transport="stdio")








