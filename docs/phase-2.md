# Phase 2 completion

Environment: D:\APOLLO\.venv, Python 3.13.7, Windows AMD64.
Installation succeeded using the approved requirements and constraints.
Executed pip check: No broken requirements found.

Every requested package imported successfully and its distribution location was
verified under D:\APOLLO\.venv\Lib\site-packages. Exact versions and model results
are in [runtime-verification.json](runtime-verification.json).

| Package | Verified version |
| --- | --- |
| torch | 2.14.0 |
| transformers | 5.16.1 |
| sentence-transformers | 6.0.1 |
| pydantic | 2.13.5 |
| langgraph | 1.2.11 |
| langchain-core | 1.6.2 |
| fastmcp | 4.0.3 |
| mcp | 2.2.0 |
| psycopg | 3.3.5 |
| pgvector | 0.5.0 |
| redis | 8.1.0 |
| pytest | 9.1.1 |
| reportlab | 5.0.1 |
| websockets | 16.0 |

## Executed model checks
The APOLLO interpreter loaded AutoTokenizer and Gemma3ForCausalLM directly from
C:\SLM-WORKSHOP\models\it, in CPU float32, local-files-only mode. Loaded parameter
count: 999,885,952. No adapter config was present, no PEFT config was loaded, and
the model reported no loaded PEFT adapter. No oil-field adapter was selected.

SentenceTransformer loaded C:\SLM-WORKSHOP\models\embedder and encoded
["APOLLO embedding dimension test"]. Actual shape: (1, 384).
No generation test was performed. Workshop resources were neither copied nor
modified; -B/PYTHONDONTWRITEBYTECODE and offline settings were used.

## Implemented contracts
- app/config.py: all requested environment variables, bounded confidence [0,1],
  finite values, RAG_TOP_K 1–20, lease duration 1–300 seconds (default 45),
  absolute resource paths, masked service credentials. Configuration never enters state.
- app/schemas.py: IntentType, BookingIntent, SlotCandidate, LeaseResult,
  BillingItem, BillingBreakdown, PolicyChunk, SafetyAssessment, EscalationRecord,
  NotificationPayload. Booking confirmation is a strict boolean and requires
  opaque patient/slot/idempotency references. Monetary values are Decimal; float,
  nonfinite, negative, and overprecision inputs are rejected. Totals are derived.
- app/state.py: LangGraph-compatible TypedDict, Pydantic validation adapter,
  fresh request/session creation, all shared workflow fields, and a restricted
  LLM view. State uses opaque references, not names, addresses, credentials,
  Redis ownership tokens, or raw exception messages.
- tests/test_phase2.py: 45 executed cases covering requested validation plus
  date ordering, timezone-aware slots, consistent leases, serialization, and privacy.

create_state requires already-sanitized text; no sanitizer is implemented in
Phase 2. TypedDict does not validate arbitrary direct mutations: use STATE_ADAPTER
at workflow boundaries. LLM-facing callers must use llm_view instead of dumping
the complete shared state. For lossless Pydantic state serialization, use
round_trip=True to omit derived billing fields from serialized inputs.
SafetyAssessment records a decision; Phase 2 does not implement the early gate.
TraceEvent/WorkflowError are bounded local tracing/error contracts; no remote
tracing or Langfuse setup was added.

## Tests executed
From D:\APOLLO:

```powershell
& 'D:\APOLLO\.venv\Scripts\python.exe' -m pytest -q
```

Result: **45 passed in 0.11s; 0 failed**. First run passed.
Runtime verification is a separate executed script, not included in that test count.

## Files changed in this run
- app/config.py
- app/schemas.py
- app/state.py
- tests/test_phase2.py (new)
- .env.example
- README.md
- scripts/prepare_environment.py
- scripts/verify_runtime.py (new)
- tests/README.md
- docs/runtime-environment.md
- docs/phase-2.md (this report, new)
- docs/runtime-verification.json (new evidence)

Ignored execution logs: docs/installation-d.log, docs/runtime-verification.log,
docs/phase2-tests.log. The .venv directory is ignored.
requirements.txt and pinned runtime constraints were not changed during installation.

## Stop boundary and Git
Stopped after Phase 2. No Docker, database/Redis integration, new MCP
implementation, full LangGraph, or later phase was started.
Git root: D:/APOLLO; branch main; no commits, staged files, or remote.
git check-ignore .venv/Scripts/python.exe succeeded.
git status shows scaffold files as untracked and does not show .venv.

