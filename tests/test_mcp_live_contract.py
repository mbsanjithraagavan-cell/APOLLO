import os, asyncio
import pytest
import psycopg
import redis
from fastmcp import Client
from app.mcp_server import server
from app.mcp_client import unwrap_tool_result

SLOT='00000000-0000-0000-0000-000000000101'
PATIENT='00000000-0000-0000-0000-000000000011'
@pytest.fixture
def fictional_demo_state():
    dsn=os.getenv('DATABASE_URL'); rurl=os.getenv('REDIS_URL')
    if not dsn or not rurl: pytest.skip('DATABASE_URL/REDIS_URL not configured for live integration')
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute('DELETE FROM appointments WHERE patient_id=%s AND slot_id=%s',(PATIENT,SLOT))
        cur.execute('UPDATE slots SET is_booked=FALSE WHERE id=%s',(SLOT,)); conn.commit()
    redis.Redis.from_url(rurl,decode_responses=True).delete(f'apollo:lease:{SLOT}')
    yield

def test_fastmcp_search_returns_seeded_cardiology_slot(fictional_demo_state):
    async def call():
        async with Client(server) as client:
            return await client.call_tool('search_doctor_slots',{'request':{'specialty':'CARDIOLOGY'}})
    rows=unwrap_tool_result(asyncio.run(call()))
    assert any(str(getattr(x,'slot_id',x.get('slot_id') if isinstance(x,dict) else '')).endswith('0101') for x in rows)
