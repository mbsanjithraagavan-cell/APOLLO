from app.agents import Escalation, PolicyRAGAgent, SafetyCritic
from app.citations import validate_citations
from datetime import datetime, timezone
from uuid import UUID

def answer_policy(question: str, request_id: UUID, policy_agent: PolicyRAGAgent) -> dict:
    result=policy_agent.answer(question)
    ok,citations,reason=validate_citations(result["draft"],result["valid_chunk_ids"])
    critic=SafetyCritic(confidence=result["confidence"] if ok else 0.2,acute_red_flag=False,scope_violation=False,grounding_valid=ok,decision="allow" if ok and result["confidence"] >= 0.7 else "escalate",reason=reason)
    if critic.allowed(): return {**result,"citations":citations,"critic":critic,"escalation":None}
    return {**result,"citations":citations,"critic":critic,"escalation":Escalation(request_id=request_id,reason=reason,confidence=critic.confidence,acute_red_flag=False,scope_violation=False,context=question[:1000],timestamp=datetime.now(timezone.utc))}

