from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
import redis
from app.schemas import LeaseResult

class RedisLeaseService:
    def __init__(self, url: str, seconds: int = 45):
        self.client=redis.Redis.from_url(url, decode_responses=True); self.seconds=seconds
    def stage(self, slot_id: UUID) -> LeaseResult:
        token=str(uuid4()); key=f"apollo:lease:{slot_id}"
        if not self.client.set(key, token, nx=True, ex=self.seconds): return LeaseResult(acquired=False,slot_id=slot_id,failure_code="busy")
        ttl=self.client.ttl(key)
        return LeaseResult(acquired=True,slot_id=slot_id,lease_reference=UUID(token),expires_at=datetime.now(timezone.utc)+timedelta(seconds=ttl))

