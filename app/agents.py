from datetime import datetime, timezone
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, StrictBool
from app.schemas import SlotCandidate

class ScopedToolAgent:
    allowed_tools: frozenset[str] = frozenset()
    def __init__(self, tools: dict): self.tools={k:v for k,v in tools.items() if k in self.allowed_tools}
    def call(self, name: str, *args, **kwargs):
        if name not in self.allowed_tools or name not in self.tools: raise PermissionError(f"tool_not_allowed:{name}")
        return self.tools[name](*args,**kwargs)

class PolicyRAGAgent(ScopedToolAgent):
    allowed_tools=frozenset({"query_clinic_policies"})
    def answer(self, question: str) -> dict:
        chunks=self.call("query_clinic_policies",question)
        valid={x["chunk_id"] for x in chunks}
        grounded=[x for x in chunks if x["distance"] <= 0.75]
        answer=" ".join(x["content"] for x in grounded)
        confidence=0.85 if answer else 0.2
        return {"draft":answer,"chunks":chunks,"valid_chunk_ids":valid,"confidence":confidence}

class BookingDiscoveryAgent(ScopedToolAgent):
    allowed_tools=frozenset({"search_doctor_slots"})
    def discover(self, specialty: str): return self.call("search_doctor_slots",specialty)

class AllocatorAgent(ScopedToolAgent):
    allowed_tools=frozenset({"stage_slot_lease"})
    def allocate(self, slots: list[SlotCandidate]):
        if not slots: raise ValueError("no_slots")
        return self.call("stage_slot_lease",slots[0].slot_id)

class SafetyCritic(BaseModel):
    model_config=ConfigDict(extra="forbid", frozen=True)
    confidence: float=Field(ge=0,le=1)
    acute_red_flag: StrictBool
    scope_violation: StrictBool
    grounding_valid: StrictBool
    decision: str
    reason: str=Field(min_length=1)
    def allowed(self): return self.confidence >= 0.7 and not self.acute_red_flag and not self.scope_violation and self.grounding_valid

class Escalation(BaseModel):
    request_id: UUID
    reason: str
    confidence: float=Field(ge=0,le=1)
    acute_red_flag: bool
    scope_violation: bool
    context: str=Field(max_length=1000)
    timestamp: datetime

