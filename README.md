# APOLLO

**Agentic Patient & Outpatient Logistics Orchestrator**

APOLLO is a local hackathon prototype for fictional outpatient appointment coordination. Patients can describe what they need in natural language; APOLLO finds real local availability, recommends an option, previews trusted billing, and books only after explicit confirmation.

## Overview

APOLLO separates language understanding from trusted operational decisions. Local Gemma interprets supported booking requests and drafts grounded policy answers. FastMCP, PostgreSQL, Redis, and deterministic services own availability, pricing, leases, booking state, and notifications.

## Key features

- Default conversational **Book with APOLLO** experience, plus a manual browsing fallback.
- Local Gemma structured booking interpretation with Pydantic validation, bounded normalization, and deterministic fallback.
- FastMCP discovery of real available doctors and slots.
- PostgreSQL authoritative booking state and atomic conditional booking.
- Redis 45-second staging lease for temporary contention protection.
- Deterministic `Decimal` billing with 5% tax.
- Patient and doctor confirmation artifacts with simulated delivery statuses.
- Policy RAG with pgvector retrieval, citation validation, bounded retry, and deterministic grounded fallback.
- PII sanitization, early safety routing, explicit confirmation, and real workflow traces.

## The four agents

| Agent | Responsibility |
| --- | --- |
| Booking / Discovery Agent | Interprets supported booking requests and requests real availability. |
| Allocator Agent | Ranks only real returned options by time, earliest, and clinician preferences. |
| Policy RAG Agent | Retrieves clinic-policy chunks and drafts grounded administrative answers. |
| Safety Critic | Reviews policy-answer grounding and safety constraints. |

The PII sanitizer, intent router, billing engine, Redis lease service, PostgreSQL service, Gatekeeper, notification dispatcher, FastAPI layer, and MCP transport are deterministic services, not agents.

## Booking workflow

```text
Patient request
  -> PII sanitizer
  -> early safety gate
  -> intent router
  -> local Gemma structured booking interpretation
  -> supported treatment/specialty validation
  -> Booking / Discovery Agent
  -> FastMCP doctor and slot discovery
  -> PostgreSQL availability
  -> Allocator Agent recommendation + billing preview
  -> explicit user confirmation
  -> Redis temporary lease
  -> Gatekeeper + deterministic billing
  -> FastMCP booking commit
  -> PostgreSQL atomic booking
  -> patient and doctor notification artifacts
  -> observability / Agent Activity trace
```

Gemma does **not** decide doctor availability, slot availability, price, booking result, appointment ID, or database state. Those values come only from trusted backend tools and data.

## MCP and trusted data

FastMCP exposes scoped operational tools:

- `list_available_doctors`
- `list_available_slots`
- `search_doctor_slots`
- `stage_slot_lease`
- `commit_slot_booking`

PostgreSQL is the final source of truth for doctors, slots, appointments, tariffs, and clinic policies. Its atomic conditional slot update prevents final double booking. Redis holds only a temporary lease and is never the final booking record. pgvector stores and retrieves 384-dimensional clinic-policy embeddings.

## Trust & safety

- PII is sanitized before LLM-facing workflow steps.
- Early safety runs before discovery, leasing, billing, or booking mutations. Emergency-like requests escalate instead of booking.
- APOLLO does not diagnose, prescribe, or make treatment recommendations.
- Explicit confirmation is required before the lease and booking commit path.
- Billing uses trusted tariff data and deterministic calculations; the LLM cannot set totals.
- Policy answers must cite current retrieved clinic-policy chunks. A deterministic extractive fallback is used only for administrative policy RAG when model citations fail.
- Model booking output is Pydantic-validated against supported treatments and specialties.

## Policy RAG

For clinic-policy questions, APOLLO retrieves current policy chunks with pgvector and a local SentenceTransformer embedder. Gemma generates a structured answer with sources restricted to retrieved chunk IDs. Citations are validated programmatically. After one failed retry, APOLLO can return an extractive answer composed only of retrieved policy content with deterministic citations.

This is for administrative clinic policy only, never diagnosis, prescriptions, treatment recommendations, or emergency assessment.

## Frontend

The React/Vite interface includes:

1. **Book with APOLLO** — the default conversational booking experience.
2. **Browse Manually** — treatment, clinician, and time-slot selection.
3. **Ask APOLLO** — grounded clinic-policy RAG.
4. **My Confirmation** — appointment and HTML/PDF confirmation links when available.
5. **Agent Activity** — real backend events for the latest request.

Recommendations show trusted clinician, specialty, date/time, billing, and allocator rationale. A booking is not made until the user selects **Confirm Booking**.

## Technology stack

| Area | Technology |
| --- | --- |
| Backend | Python, FastAPI, Pydantic |
| Orchestration | LangGraph, FastMCP |
| Local AI | Gemma 3 1B Instruct, Transformers, PyTorch |
| Retrieval | Sentence Transformers, PostgreSQL 16, pgvector |
| Coordination | Redis 7.2, psycopg |
| Frontend | React, Vite, Lucide |
| Infrastructure | Docker Compose |
| Verification | Pytest |

## Demo scenarios

| Request | Expected behavior |
| --- | --- |
| `I need a skin specialist tomorrow morning.` | Plans a real dermatology option and requires confirmation. |
| `Find me the earliest cardiologist appointment.` | Recommends the earliest real cardiology option. |
| `What preparation is required before my appointment?` | Returns a cited grounded policy answer. |
| Emergency-like input | Stops before discovery, leasing, billing, and booking. |

## Project structure

```text
app/        FastAPI, LangGraph workflow, agents, MCP server, services, safety
frontend/   React/Vite interface
database/   PostgreSQL schema and policy seed SQL
data/       Fictional policy seed data
tests/      Unit, API, MCP-contract, and workflow tests
docs/       Architecture, security, demo, and verification documentation
```

## Setup

Model weights are **not included** in this repository. Provide compatible local Gemma and embedder directories, then keep their paths and all secrets in an uncommitted `.env` file.

```bash
git clone <your-repository-url>
cd APOLLO
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

cd frontend
npm install
cd ..

docker compose up -d
```

## Environment variables

Copy `.env.example` to `.env` and replace placeholders. Never commit `.env`.

```dotenv
APOLLO_MODEL_DIR=C:/path/to/gemma
APOLLO_EMBEDDER_DIR=C:/path/to/embedder
APOLLO_EMBEDDING_DIMENSION=384
DATABASE_URL=postgresql://apollo:YOUR_PASSWORD@127.0.0.1:5432/apollo
REDIS_URL=redis://127.0.0.1:6379/0
POSTGRES_PASSWORD=YOUR_PASSWORD
APOLLO_ENV=development
APOLLO_LOG_LEVEL=INFO
RAG_TOP_K=3
SAFETY_CONFIDENCE_THRESHOLD=0.7
REDIS_LEASE_SECONDS=45
APOLLO_MAX_NEW_TOKENS=96
```

Both model variables must be absolute paths. Never commit model weights, credentials, generated confirmation files, database volumes, or Redis data.

## Running APOLLO

Start the API from the repository root:

```bash
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload
```

In a second terminal:

```bash
cd frontend
npm run dev
```

- Frontend: <http://localhost:5173>
- API documentation: <http://127.0.0.1:8000/api/docs>

## Testing

```bash
python -m pytest -q

cd frontend
npm run build
```

Latest verified result: **113 passed, 0 failed, 0 skipped, 2 warnings**. The frontend production build passes. Live supported booking interpretation has been verified with `interpretation_mode = gemma` and `gemma_parse_status = success`.

## Screenshots

<!-- Add verified screenshots when available. Do not commit fabricated images. -->

<!-- docs/images/book-with-apollo.png -->
<!-- docs/images/confirmation.png -->
<!-- docs/images/agent-activity.png -->
<!-- docs/images/policy-rag.png -->

## Prototype notes

APOLLO is a hackathon prototype using fictional clinic data. Patient and doctor delivery is simulated unless an external provider is explicitly configured. It is not a production hospital system and does not provide diagnosis, prescriptions, or medical decision-making.

## License

Add a license appropriate for your repository before public distribution.

