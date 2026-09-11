from langgraph.graph import END, START, StateGraph
from app.intent import extract_booking_intent
from app.safety import early_safety, route_intent, sanitize_pii, is_prompt_injection
from app.state import ApolloState
from app.rag import answer_policy

def sanitize_node(state):
    result=sanitize_pii(state["sanitized_input"]); return {"sanitized_input":result.text,"redaction_count":result.redaction_count}
def safety_node(state):
    if is_prompt_injection(state["sanitized_input"]): return {"early_safety": __import__("app.schemas",fromlist=["SafetyAssessment"]).SafetyAssessment(disposition="escalate",confidence=.99,reason_code="prompt_injection")}
    return {"early_safety":early_safety(state["sanitized_input"])}
def safety_route(state): return "continue" if state["early_safety"].disposition=="allow" else "halt"
def intent_node(state):
    intent=route_intent(state["sanitized_input"]); u={"intent":intent}
    if intent=="booking": u["booking_intent"]=extract_booking_intent(state["sanitized_input"])
    return u
def halt_node(state):
    a=state["early_safety"]; return {"status":"emergency" if a.disposition=="emergency" else "escalated","response":f"Request stopped: {a.reason_code}. Please contact the appropriate human service."}
def policy_node(state):
    try:
        result=answer_policy(state["sanitized_input"])
        return {"status":result.routing,"response":result.answer,"citations":result.citations}
    except Exception as exc: return {"status":"escalated","response":"Policy answer requires human review.","errors":[{"code":"policy_failed","detail":str(exc)}]}
def booking_node(state):
    return {"status":"needs_integration","response":"Booking requires an explicit confirmation and patient reference."}
def route_node(state): return "booking" if state["intent"]=="booking" else "policy"
def build_graph():
    b=StateGraph(ApolloState)
    for n,f in [("sanitize",sanitize_node),("safety",safety_node),("halt",halt_node),("intent",intent_node),("policy",policy_node),("booking",booking_node)]: b.add_node(n,f)
    b.add_edge(START,"sanitize"); b.add_edge("sanitize","safety"); b.add_conditional_edges("safety",safety_route,{"continue":"intent","halt":"halt"}); b.add_conditional_edges("intent",route_node,{"booking":"booking","policy":"policy"}); b.add_edge("halt",END); b.add_edge("policy",END); b.add_edge("booking",END); return b.compile()


