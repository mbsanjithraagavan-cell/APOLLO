"""LangGraph-compatible state with validated creation and an explicit LLM projection.

Only sanitized text may enter this contract. Phase 2 does not implement a PII
sanitizer. Do not persist raw requests, service URLs, credentials, lease ownership
tokens, contact information, or unrestricted exception messages.
"""
from typing import Literal
from uuid import UUID, uuid4

from pydantic import ConfigDict, Field, TypeAdapter, with_config
from typing import Annotated
from typing_extensions import Required, TypedDict

from app.schemas import (
    BillingBreakdown, BookingIntent, EscalationRecord, IntentType, LeaseResult,
    NotificationPayload, PolicyChunk, SafetyAssessment, SlotCandidate, TraceEvent,
    WorkflowError,
)


@with_config(ConfigDict(extra="forbid"))
class ApolloState(TypedDict, total=False):
    request_id: Required[UUID]
    session_id: Required[UUID]
    sanitized_input: Required[Annotated[str, Field(min_length=1, max_length=16000)]]
    redaction_count: Annotated[int, Field(ge=0)]
    intent: IntentType
    booking_intent: BookingIntent | None
    early_safety: SafetyAssessment | None
    final_safety: SafetyAssessment | None
    rag_query: str | None
    policy_chunks: tuple[PolicyChunk, ...]
    citations: tuple[str, ...]
    draft_response: str | None
    slots: tuple[SlotCandidate, ...]
    selected_slot: SlotCandidate | None
    lease: LeaseResult | None
    billing: BillingBreakdown | None
    booking_reference: UUID | None
    booking_status: Literal["not_started", "pending", "committed", "failed"]
    notification: NotificationPayload | None
    notification_status: Literal["not_started", "pending", "simulated", "failed"]
    escalation: EscalationRecord | None
    trace: tuple[TraceEvent, ...]
    errors: tuple[WorkflowError, ...]
    response: str | None
    status: Literal["needs_integration", "escalated", "emergency", "out_of_scope"]


STATE_ADAPTER = TypeAdapter(ApolloState)


def create_state(sanitized_input: str, *, session_id: UUID | None = None) -> ApolloState:
    """Create a fresh request state. Caller must supply already sanitized input."""
    return STATE_ADAPTER.validate_python({
        "request_id": uuid4(), "session_id": session_id or uuid4(),
        "sanitized_input": sanitized_input, "redaction_count": 0,
        "intent": IntentType.UNKNOWN, "booking_intent": None,
        "early_safety": None, "final_safety": None, "rag_query": None,
        "policy_chunks": (), "citations": (), "draft_response": None,
        "slots": (), "selected_slot": None, "lease": None, "billing": None,
        "booking_reference": None, "booking_status": "not_started",
        "notification": None, "notification_status": "not_started",
        "escalation": None, "trace": (), "errors": (), "response": None,
        "status": "needs_integration",
    })


def llm_view(state: ApolloState) -> dict[str, str]:
    """Return only sanitized routing input; private workflow references stay out."""
    return {"sanitized_input": state["sanitized_input"],
            "intent": IntentType(state.get("intent", IntentType.UNKNOWN)).value}

