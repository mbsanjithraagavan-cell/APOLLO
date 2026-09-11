from uuid import uuid4
from app.agents import AllocatorAgent, BookingDiscoveryAgent, PolicyRAGAgent, SafetyCritic
from app.citations import validate_citations
from app.rag import answer_policy

def test_relevant_policy_retrieval():
    agent=PolicyRAGAgent({"query_clinic_policies":lambda q:[{"chunk_id":"chunk_prep_01","category":"prep","content":"Bring the reference. [chunk_prep_01]","distance":0.2}]})
    result=agent.answer("preparation")
    assert result["chunks"][0]["chunk_id"]=="chunk_prep_01"

def test_valid_citations_only():
    assert validate_citations("Bring the reference. [chunk_prep_01]",{"chunk_prep_01"})[0]

def test_fabricated_citation_rejected():
    assert not validate_citations("Bring it. [chunk_fake_99]",{"chunk_prep_01"})[0]

def test_no_evidence_escalates():
    result=answer_policy("unknown",uuid4(),PolicyRAGAgent({"query_clinic_policies":lambda q:[]}))
    assert result["critic"].decision=="escalate"
    assert result["escalation"] is not None

def test_multi_chunk_grounded_answer():
    agent=PolicyRAGAgent({"query_clinic_policies":lambda q:[
      {"chunk_id":"chunk_a","category":"a","content":"Bring reference. [chunk_a]","distance":0.1},
      {"chunk_id":"chunk_b","category":"b","content":"Arrive early. [chunk_b]","distance":0.2}]})
    result=agent.answer("prep")
    assert "chunk_a" in result["draft"] and "chunk_b" in result["draft"]

def test_tool_scope_enforcement():
    policy=PolicyRAGAgent({"query_clinic_policies":lambda q:[], "commit_slot_booking":lambda:None})
    discovery=BookingDiscoveryAgent({"search_doctor_slots":lambda s:[], "stage_slot_lease":lambda s:None})
    allocator=AllocatorAgent({"stage_slot_lease":lambda s:"lease", "commit_slot_booking":lambda:None})
    for agent,name in [(policy,"commit_slot_booking"),(discovery,"stage_slot_lease"),(allocator,"commit_slot_booking")]:
        try: agent.call(name,None); assert False
        except PermissionError: pass

def test_safety_threshold_allows_at_seventy():
    assert SafetyCritic(confidence=.7,acute_red_flag=False,scope_violation=False,grounding_valid=True,decision="allow",reason="grounded").allowed()

def test_safety_below_threshold_escalates():
    assert not SafetyCritic(confidence=.69,acute_red_flag=False,scope_violation=False,grounding_valid=True,decision="escalate",reason="low").allowed()

def test_acute_red_flag_escalates():
    assert not SafetyCritic(confidence=.99,acute_red_flag=True,scope_violation=False,grounding_valid=True,decision="escalate",reason="acute").allowed()

def test_scope_violation_escalates():
    assert not SafetyCritic(confidence=.99,acute_red_flag=False,scope_violation=True,grounding_valid=True,decision="escalate",reason="scope").allowed()

