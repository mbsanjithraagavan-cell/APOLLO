import re
_CITATION=re.compile(r"\[(chunk_[a-z0-9_]+)\]")
def validate_citations(draft: str, valid_chunk_ids: set[str]) -> tuple[bool,list[str],str]:
    citations=_CITATION.findall(draft)
    unknown=[x for x in citations if x not in valid_chunk_ids]
    factual=[line for line in draft.splitlines() if line.strip() and not line.strip().startswith("#")]
    missing=bool(factual) and not citations
    if unknown or missing: return False,citations,"invalid_or_missing_citation"
    return True,citations,"ok"

