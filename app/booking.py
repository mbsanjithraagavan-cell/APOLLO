from decimal import Decimal, ROUND_HALF_UP
from app.schemas import BillingBreakdown, BillingItem, BookingIntent, SlotCandidate
from app.services.database import DatabaseService

class Gatekeeper:
    def __init__(self, database: DatabaseService): self.database=database
    def quote(self, slot: SlotCandidate) -> BillingBreakdown:
        subtotal=slot.fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        tax=(subtotal * Decimal('0.05')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return BillingBreakdown(currency=slot.currency, items=(BillingItem(code='consult',description='Outpatient consultation',unit_amount=subtotal),), tax=tax)
    def validate(self, intent: BookingIntent, slot: SlotCandidate, *, explicit_confirmation: bool) -> BillingBreakdown:
        if not explicit_confirmation or not intent.patient_reference or not intent.idempotency_key: raise ValueError('explicit_confirmation_required')
        if intent.slot_id and intent.slot_id != slot.slot_id: raise ValueError('slot_mismatch')
        return self.quote(slot)
