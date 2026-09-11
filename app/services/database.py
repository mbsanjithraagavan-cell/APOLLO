from decimal import Decimal
from uuid import UUID, uuid4
import psycopg
from app.schemas import SlotCandidate

class DatabaseService:
    def __init__(self, dsn: str): self.dsn = dsn.get_secret_value() if hasattr(dsn, "get_secret_value") else dsn
    def connection(self): return psycopg.connect(self.dsn)
    def search_slots(self, specialty: str) -> list[SlotCandidate]:
        with self.connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT s.id,s.doctor_id,s.starts_at,s.ends_at,t.amount,t.currency FROM slots s JOIN doctors d ON d.id=s.doctor_id JOIN tariffs t ON t.code='CONSULT' WHERE lower(trim(d.specialty))=lower(trim(%s)) AND s.is_booked=FALSE ORDER BY s.starts_at", (specialty,))
            return [SlotCandidate(slot_id=r[0], doctor_id=r[1], starts_at=r[2], ends_at=r[3], fee=Decimal(r[4]), currency=r[5].strip()) for r in cur.fetchall()]
    def commit_booking(self, patient_id: UUID, slot_id: UUID, idempotency_key: UUID) -> UUID:
        with self.connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT id FROM appointments WHERE idempotency_key=%s", (idempotency_key,))
            existing=cur.fetchone()
            if existing: return existing[0]
            cur.execute("UPDATE slots SET is_booked=TRUE WHERE id=%s AND is_booked=FALSE RETURNING id", (slot_id,))
            if not cur.fetchone(): raise ValueError("slot_unavailable")
            cur.execute("SELECT amount,currency FROM tariffs WHERE code='CONSULT'")
            amount,currency=cur.fetchone()
            appointment_id=uuid4()
            cur.execute("INSERT INTO appointments(id,patient_id,slot_id,tariff_code,amount,currency,idempotency_key) VALUES (%s,%s,%s,'CONSULT',%s,%s,%s)", (appointment_id,patient_id,slot_id,amount,currency,idempotency_key))
            conn.commit()
            return appointment_id



