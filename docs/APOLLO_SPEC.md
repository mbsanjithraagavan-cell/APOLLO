# APOLLO specification

APOLLO is an outpatient administration and logistics orchestrator. It can answer approved preparation and policy questions, discover doctors and slots, stage a short Redis lease, quote deterministic billing, obtain explicit confirmation, and commit an appointment transactionally. It is never a doctor: it must not diagnose, prescribe, or recommend medication changes.

The safety order is mandatory: sanitize PII, run an early safety/scope gate, route intent, then perform policy retrieval or booking work. Emergency, clinical, out-of-scope, ambiguous, and low-confidence requests stop before lease, billing, or database side effects. A final critic cannot undo a committed transaction.

The local Gemma 3 1B instruction checkpoint and 384-dimensional SentenceTransformer embedder remain external read-only resources under `C:\SLM-WORKSHOP`. APOLLO uses a local structured Pydantic generation wrapper and never loads the oil-field adapter.

Milestone A provides the foundation: JSON generation, booking extraction, conservative PII redaction, deterministic safety, intent routing, and a compiled LangGraph StateGraph. Later milestones add real PostgreSQL/pgvector, Redis, FastMCP tools, policy ingestion, booking transactions, notifications, and evaluation. Missing integrations fail closed.

Observability is local structured JSON only. Request IDs and redacted event fields are allowed; secrets, raw PII, credentials, lease ownership tokens, and unrestricted model output are not persisted.
