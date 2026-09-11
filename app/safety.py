import re
from dataclasses import dataclass
from app.schemas import SafetyAssessment
_PATTERNS=((re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",re.I),"[EMAIL]"),(re.compile(r"(?<![+\d])(?:\d[ -]*?){4}\s?(?:\d[ -]*?){4}\s?(?:\d[ -]*?){4}(?!\d)"),"[NATIONAL_ID]"),(re.compile(r"\b(?:\+?\d[\d .()\-]{7,}\d)\b"),"[PHONE]"),(re.compile(r"\b(?:\d[ -]*?){13,19}\b"),"[CARD]"),(re.compile(r"\b(?:address|home address|street address)\s*:\s*[^,;\n]+",re.I),"[ADDRESS]"))
_EMERGENCY=re.compile(r"\b(chest pain|can't breathe|cannot breathe|severe bleeding|stroke|unconscious|suicid|emergency|overdose)\b",re.I)
_CLINICAL=re.compile(r"\b(diagnos|prescrib|medication change|change my dose|what disease|should i take)\w*\b",re.I)
_BOOKING=re.compile(r"\b(book|booking|appointment|schedule|slot|doctor|specialist|cardiolog)\w*\b",re.I)
_POLICY=re.compile(r"\b(policy|prepare|preparation|bring|document|requirement|clinic rule)\w*\b",re.I)
_INJECTION=re.compile(r"ignore\s+(all|any|previous)|reveal\s+(the\s+)?system|bypass\s+safety|drop\s+table|select\s+\*|change\s+the\s+fee|pretend\s+you\s+are",re.I)
@dataclass(frozen=True)
class SanitizedText: text:str; redaction_count:int
def sanitize_pii(text:str)->SanitizedText:
    if not isinstance(text,str) or not text.strip(): raise ValueError("Input must be non-empty text")
    result=text.strip(); count=0
    for pattern,replacement in _PATTERNS: result,m=pattern.subn(replacement,result); count+=m
    return SanitizedText(result[:16000],count)
def is_prompt_injection(text:str)->bool: return bool(_INJECTION.search(text))
def early_safety(text:str)->SafetyAssessment:
    if _EMERGENCY.search(text): return SafetyAssessment(disposition="emergency",confidence=.99,reason_code="emergency_signal")
    if _CLINICAL.search(text): return SafetyAssessment(disposition="out_of_scope",confidence=.98,reason_code="clinical_scope")
    if not (_BOOKING.search(text) or _POLICY.search(text)): return SafetyAssessment(disposition="escalate",confidence=.75,reason_code="unknown_scope")
    return SafetyAssessment(disposition="allow",confidence=.95,reason_code="administrative_scope")
def route_intent(text:str)->str:
    if _BOOKING.search(text): return "booking"
    if _POLICY.search(text): return "policy"
    return "escalate"

