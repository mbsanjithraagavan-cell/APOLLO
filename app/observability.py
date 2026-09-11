import json, re
from datetime import datetime, timezone
from pathlib import Path
class JSONTracer:
    def __init__(self, path="logs/apollo-trace.jsonl"):
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
    def emit(self,event,node,**fields):
        raw=json.dumps(fields,default=str)
        raw=re.sub(r"[w.+-]+@[w.-]+\.[A-Za-z]{2,}", "[EMAIL]", raw)
        raw=re.sub(r"\b\+?\d[\d ()-]{8,}\d\b", "[PHONE]", raw)
        record={"event":event,"node":node,"occurred_at":datetime.now(timezone.utc).isoformat(),"fields":json.loads(raw)}
        with self.path.open("a",encoding="utf-8") as f: f.write(json.dumps(record,sort_keys=True)+"\n")

