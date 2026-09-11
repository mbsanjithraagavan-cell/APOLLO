"""Pydantic v2 workflow contracts. Identifiers are opaque; money never uses floats."""
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    AwareDatetime, BaseModel, BeforeValidator, ConfigDict, Field, StrictBool,
    computed_field, model_validator,
)


def reject_inexact_money(value):
    if isinstance(value, (float, bool)):
        raise ValueError("Use Decimal, a decimal string, or integer for money")
    return value


Money = Annotated[
    Decimal, BeforeValidator(reject_inexact_money),
    Field(ge=0, max_digits=12, decimal_places=2, allow_inf_nan=False),
]
Confidence = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
Code = Annotated[str, Field(min_length=1, max_length=80, pattern=r"^[a-z0-9_]+$")]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True, allow_inf_nan=False)


class IntentType(StrEnum):
    POLICY = "policy"
    BOOKING = "booking"
    DISCOVERY = "discovery"
    SLOT_SEARCH = "slot_search"
    ESCALATION = "escalation"
    UNKNOWN = "unknown"


class BookingIntent(Contract):
    intent: Literal[IntentType.BOOKING] = IntentType.BOOKING
    patient_reference: UUID | None = None
    doctor_id: UUID | None = None
    specialty: str | None = Field(default=None, min_length=1, max_length=100)
    date_from: date | None = None
    date_to: date | None = None
    slot_id: UUID | None = None
    idempotency_key: UUID | None = None
    explicit_confirmation: StrictBool = False

    @model_validator(mode="after")
    def coherent_booking(self):
        if not (self.specialty or self.doctor_id or self.slot_id):
            raise ValueError("Provide a specialty, doctor, or slot")
        if self.date_to and not self.date_from:
            raise ValueError("date_to requires date_from")
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise ValueError("Booking date range is reversed")
        if self.explicit_confirmation and not all(
            (self.patient_reference, self.slot_id, self.idempotency_key)
        ):
            raise ValueError("Confirmation requires patient, slot, and idempotency references")
        return self


class SlotCandidate(Contract):
    slot_id: UUID
    doctor_id: UUID
    starts_at: AwareDatetime
    ends_at: AwareDatetime
    fee: Money
    currency: str = Field(default="INR", pattern=r"^[A-Z]{3}$")

    @model_validator(mode="after")
    def chronological(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("Slot must end after it starts")
        return self


class LeaseResult(Contract):
    acquired: StrictBool
    slot_id: UUID
    lease_reference: UUID | None = None
    expires_at: AwareDatetime | None = None
    # Ownership tokens/Redis credentials belong in a private service, never graph state.
    failure_code: Code | None = None

    @model_validator(mode="after")
    def consistent_result(self):
        if self.acquired:
            if self.lease_reference is None or self.expires_at is None or self.failure_code:
                raise ValueError("Acquired lease needs reference/expiry and no failure")
        elif self.lease_reference is not None or self.expires_at is not None or not self.failure_code:
            raise ValueError("Failed lease needs a failure code and no active lease")
        return self


class BillingItem(Contract):
    code: Code
    description: str = Field(min_length=1, max_length=160)
    quantity: int = Field(default=1, strict=True, ge=1, le=10000)
    unit_amount: Money

    @computed_field
    @property
    def line_total(self) -> Decimal:
        return (self.unit_amount * self.quantity).quantize(Decimal("0.01"))


class BillingBreakdown(Contract):
    currency: str = Field(default="INR", pattern=r"^[A-Z]{3}$")
    items: tuple[BillingItem, ...] = Field(min_length=1)
    discount: Money = Decimal("0.00")
    tax: Money = Decimal("0.00")

    @computed_field
    @property
    def subtotal(self) -> Decimal:
        return sum((item.line_total for item in self.items), Decimal("0.00"))

    @computed_field
    @property
    def total(self) -> Decimal:
        return (self.subtotal - self.discount + self.tax).quantize(Decimal("0.01"))

    @model_validator(mode="after")
    def valid_discount(self):
        if self.discount > self.subtotal:
            raise ValueError("Discount cannot exceed subtotal")
        return self


class PolicyChunk(Contract):
    policy_id: str = Field(min_length=1, max_length=120)
    revision: str = Field(min_length=1, max_length=80)
    chunk_id: str = Field(min_length=1, max_length=160)
    content: str = Field(min_length=1, max_length=16000)
    source: str = Field(min_length=1, max_length=500)
    similarity: Confidence | None = None


class SafetyAssessment(Contract):
    disposition: Literal["allow", "emergency", "out_of_scope", "escalate"]
    confidence: Confidence
    reason_code: Code
    # Code-only reasons prevent raw user text being echoed into traces.


class EscalationRecord(Contract):
    escalation_id: UUID
    request_id: UUID
    reason_code: Code
    created_at: AwareDatetime
    priority: Literal["routine", "urgent", "emergency"] = "routine"
    status: Literal["pending", "acknowledged", "resolved"] = "pending"


class NotificationPayload(Contract):
    notification_id: UUID
    booking_reference: UUID
    recipient_reference: UUID
    template: Literal["appointment_confirmation"] = "appointment_confirmation"
    channel: Literal["simulation"] = "simulation"
    # Contact addresses and free-text patient information are intentionally excluded.


class TraceEvent(Contract):
    event: Code
    node: Code
    occurred_at: AwareDatetime


class WorkflowError(Contract):
    code: Code
    node: Code
    retryable: StrictBool = False

