import asyncio
from uuid import UUID, uuid4
from app.booking import Gatekeeper
from app.config import Settings
from app.observability import JSONTracer
from app.services.database import DatabaseService
from app.services.redis import RedisLeaseService
from app.notifications import NotificationDispatcher
from app.schemas import BookingIntent, SlotCandidate, LeaseResult
from fastmcp import Client
from app.mcp_client import unwrap_tool_result
from app.mcp_server import server

def canonical_specialty(value): return ' '.join(value.strip().lower().split())
class ApolloRuntime:
    def __init__(self):
        s=Settings.from_environment(); self.db=DatabaseService(s.database_url); self.redis=RedisLeaseService((s.redis_url.get_secret_value() if s.redis_url else 'redis://localhost:6379/0'),s.redis_lease_seconds); self.gate=Gatekeeper(self.db); self.trace=JSONTracer()
    def discover_doctors(self,specialty):
        async def call():
            async with Client(server) as c: return unwrap_tool_result(await c.call_tool('list_available_doctors',{'request':{'specialty':canonical_specialty(specialty)}}))
        return asyncio.run(call())
    def discover_slots(self,doctor_id):
        async def call():
            async with Client(server) as c: return unwrap_tool_result(await c.call_tool('list_available_slots',{'request':{'doctor_id':str(doctor_id)}}))
        return asyncio.run(call())
    async def _mcp_book(self,patient_reference,specialty,confirmation,selected_slot=None,details=None):
        if confirmation is not True:
            return {'status':'confirmation_required'}
        async with Client(server) as client:
            found=unwrap_tool_result(await client.call_tool('search_doctor_slots',{'request':{'specialty':canonical_specialty(specialty)}})) or []
            slots=[x if hasattr(x,'slot_id') else SlotCandidate.model_validate(x) for x in found]
            slot=(next((x for x in slots if x.slot_id==selected_slot),None) if selected_slot else (slots[0] if slots else None))
            if slot is None: return {'status':'no_available_slots'}
            lease=unwrap_tool_result(await client.call_tool('stage_slot_lease',{'request':{'slot_id':str(slot.slot_id)}})); lease=lease if isinstance(lease,LeaseResult) else LeaseResult.model_validate(lease)
            if not lease.acquired: return {'status':'lease_unavailable','lease':lease.model_dump(mode='json')}
            intent=BookingIntent(patient_reference=patient_reference,specialty=canonical_specialty(specialty),slot_id=slot.slot_id,idempotency_key=uuid4(),explicit_confirmation=confirmation); bill=self.gate.validate(intent,slot,explicit_confirmation=confirmation)
            aid=unwrap_tool_result(await client.call_tool('commit_slot_booking',{'request':{'patient_id':str(patient_reference),'slot_id':str(slot.slot_id),'idempotency_key':str(intent.idempotency_key),'lease_token':str(lease.lease_reference),'explicit_confirmation':confirmation}})); aid=aid[0] if isinstance(aid,list) else aid
            details = details or {}
            packet=NotificationDispatcher().render_dual(aid,patient_reference,'Fictional Patient One',details.get('treatment', specialty),details.get('doctor_name','Assigned clinician'),canonical_specialty(specialty),slot.starts_at,details.get('location','Location not provided'),bill)
            self.trace.emit('booking_committed','mcp_client',tool_calls=['search_doctor_slots','stage_slot_lease','commit_slot_booking'],appointment_id=aid,slot_id=slot.slot_id,total=str(bill.total))
            return {'status':'booked','slot':slot.model_dump(mode='json'),'billing':bill.model_dump(mode='json'),'appointment_id':str(aid),'notification':packet,'mcp_tools':['search_doctor_slots','stage_slot_lease','commit_slot_booking']}
    def book(self,patient_reference,specialty='cardiology',confirmation=True,selected_slot=None,details=None):
        try:return asyncio.run(self._mcp_book(patient_reference,specialty,confirmation,selected_slot,details))
        except Exception as e:return {'status':'booking_error','error':type(e).__name__}
    def reset_fictional_demo(self):
        slot_id=UUID('00000000-0000-0000-0000-000000000101'); patient=UUID('00000000-0000-0000-0000-000000000011')
        with self.db.connection() as conn, conn.cursor() as cur:
            cur.execute('DELETE FROM appointments WHERE patient_id=%s AND slot_id=%s',(patient,slot_id)); cur.execute('UPDATE slots SET is_booked=FALSE WHERE id=%s',(slot_id,)); conn.commit()
        self.redis.client.delete(f'apollo:lease:{slot_id}'); return {'status':'reset','slot_id':str(slot_id)}

