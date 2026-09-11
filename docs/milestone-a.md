# Milestone A — Core Agent Foundation

STATUS: COMPLETE

Implemented local Gemma loading, strict JSON/Pydantic generation, booking intent extraction, conservative PII redaction, deterministic early safety, intent routing, and a compiled LangGraph StateGraph. The graph sanitizes before safety, halts emergency/clinical/unknown requests before intent or side effects, and routes booking/policy requests to fail-closed integration placeholders.

Tests: `49 passed in 1.35s` with `D:\APOLLO\.venv\Scripts\python.exe -m pytest -q`.

Real Gemma smoke test: loaded `Gemma3ForCausalLM` from `C:\SLM-WORKSHOP\models\it`, generated and validated a BookingIntent JSON object for cardiology, and confirmed the external base checkpoint was used. No adapter or workshop package bridge was used.

Key files: `docs/APOLLO_SPEC.md`, `app/generation.py`, `app/intent.py`, `app/safety.py`, `app/graph.py`, `app/config.py`, `app/schemas.py`, `app/state.py`, `tests/test_milestone_a.py`.

The local tracing baseline remains structured JSON; no Langfuse or remote tracing was added. The graph has no database, Redis, MCP, or booking side effects yet.

## Milestone B boundary

Docker is not installed (`docker` was not found on PATH). PostgreSQL/pgvector and Redis cannot be started or honestly tested without Docker or an explicitly approved local installation. No infrastructure was faked, installed, pulled, or started. The existing Compose file remains ready for the user action.

To continue, install Docker Desktop with Compose support, then rerun the Milestone B request. No GitHub push or commit was performed.
