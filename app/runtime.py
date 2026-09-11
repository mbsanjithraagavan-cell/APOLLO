import asyncio
from uuid import UUID, uuid4
from app.booking import Gatekeeper
from app.config import Settings
from app.observability import JSONTracer
from app.services.database import DatabaseService
from app.services.redis import RedisLeaseService
from app.notifications import NotificationDispatcher
from app.schemas import BookingIntent
from fastmcp import Client
from app.mcp_client import unwrap_tool_result
from app.mcp_server import server

def canonical_specialty(value: str) -> str:
    return ' '.join(value.strip().lower().split())

class ApolloRuntime:
    def __init__(self):
        s=Settings.from_environment(); self.db=DatabaseService(s.database_url); self.redis=RedisLeaseService((s.redis_url.get_secret_value() if s.redis_url else 'redis://localhost:6379/0'),s.redis_lease_seconds); self.gate=Gatekeeper(self.db); self.trace=JSONTracer()
    async def _mcp_book(self, patient_reference, specialty, confirmation):
        async with Client(server) as client:
            found=await client.call_tool('search_doctor_slots', {'request': {'specialty': canonical_specialty(specialty)}})
            slots=unwrap_tool_result(found) or []
            if not slots: return {'status':'no_available_slots','specialty':canonical_specialty(specialty)}
            raw=slots[0]; slot=raw if hasattr(raw,'slot_id') else __import__('app.schemas',fromlist=['SlotCandidate']).SlotCandidate.model_validate(raw)
            lease_result=await client.call_tool('stage_slot_lease', {'request': {'slot_id': str(slot.slot_id)}})
            lease=unwrap_tool_result(lease_result)
            if isinstance(lease,dict): lease=__import__('app.schemas',fromlist=['LeaseResult']).LeaseResult.model_validate(lease)
            if not lease.acquired: return {'status':'lease_unavailable','lease':lease.model_dump(mode='json')}
            intent=BookingIntent(patient_reference=patient_reference,specialty=canonical_specialty(specialty),slot_id=slot.slot_id,idempotency_key=uuid4(),explicit_confirmation=confirmation)
            bill=self.gate.validate(intent,slot,explicit_confirmation=confirmation)
            aid_result=await client.call_tool('commit_slot_booking', {'request': {'patient_id':str(patient_reference),'slot_id':str(slot.slot_id),'idempotency_key':str(intent.idempotency_key),'lease_token':str(lease.lease_reference),'explicit_confirmation':confirmation}})
            aid=unwrap_tool_result(aid_result)
            if isinstance(aid,list): aid=aid[0]
            self.trace.emit('booking_committed','mcp_client',tool_calls=['search_doctor_slots','stage_slot_lease','commit_slot_booking'],appointment_id=aid,slot_id=slot.slot_id,total=str(bill.total))
            packet=NotificationDispatcher().render(aid,patient_reference,'Assigned clinician',canonical_specialty(specialty),slot.starts_at,'Room A',bill)
            return {'status':'booked','doctor_id':str(slot.doctor_id),'slot':slot.model_dump(mode='json'),'lease':lease.model_dump(mode='json'),'billing':bill.model_dump(mode='json'),'appointment_id':str(aid),'notification':packet,'mcp_tools':['search_doctor_slots','stage_slot_lease','commit_slot_booking']}
    def book(self, patient_reference: UUID, specialty='cardiology', confirmation=True):
        try: return asyncio.run(self._mcp_book(patient_reference, specialty, confirmation))
        except Exception as exc: return {'status':'booking_error','error':type(exc).__name__,'detail':str(exc)}
    def reset_fictional_demo(self):
        slot_id=UUID('00000000-0000-0000-0000-000000000101'); patient=UUID('00000000-0000-0000-0000-000000000011')
        with self.db.connection() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM appointments WHERE patient_id=%s AND slot_id=%s",(patient,slot_id)); cur.execute("UPDATE slots SET is_booked=FALSE WHERE id=%s",(slot_id,)); conn.commit()
        self.redis.client.delete(f'apollo:lease:{slot_id}')
        return {'slot_id':str(slot_id),'patient_id':str(patient),'status':'reset'}

