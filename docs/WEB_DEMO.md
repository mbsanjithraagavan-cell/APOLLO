# APOLLO web demo

Run both commands from D:\APOLLO. Keep service configuration in the API terminal only.
The API inherits DATABASE_URL and REDIS_URL from that terminal; never put these values
in frontend environment variables or paste them into source.

## Start

Backend (existing APOLLO virtual environment):

```powershell
D:\APOLLO\.venv\Scripts\python.exe -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload
```

Frontend (second terminal):

```powershell
Set-Location D:\APOLLO\frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. Vite proxies /api to the loopback API at port 8000.
API documentation is at http://127.0.0.1:8000/api/docs.

## Workflow

Choose a backend-provided treatment, clinician, and explicit slot. Review the
server-calculated bill, then press Confirm booking. The API delegates preview to MCP
search and Gatekeeper, and commit to ApolloRuntime through the existing MCP transport.
It rechecks the selected clinician/slot and runs safety before booking side effects.

The browser re-queries slot availability after a successful commit and checks the
specific booked slot ID is absent. Notification file URLs expose only UUID-selected
HTML/PDF files, not filesystem paths or arbitrary output directories. Both email
notifications are simulations.

Ask APOLLO uses the existing PolicyRAGAgent, PolicyService (external embedder and
pgvector), LocalGemma, citation validation, and SafetyCritic. A missing citation
allows one bounded regeneration; failure still escalates instead of inventing sources.

Agent Activity displays completed backend events for the latest request. Health reports
reachability and model loading separately; file presence is not represented as a loaded model.
Confirmation metadata and request traces are available for the current API process.
A reload clears in-memory metadata, but generated UUID-named HTML/PDF files remain available.

The API is a loopback-only fictional demo, without production user authentication.
Do not expose it publicly. Only fictional PATIENT-001 is supported by the web confirm endpoint.
Demo reset is disabled unless APOLLO_ENABLE_DEMO_RESET=1 is explicitly set in the API
terminal. POST /api/demo/reset delegates to the existing scoped reset; there is no normal
patient-facing reset button.

## Verify

```powershell
D:\APOLLO\.venv\Scripts\python.exe -m pytest -q
Set-Location D:\APOLLO\frontend
npm run build
```

The new web tests use real Client(server) MCP transport and explicitly substituted database
records. They are not a substitute for live Docker verification. The existing live MCP
test needs DATABASE_URL and REDIS_URL in its own pytest terminal.

External model directories remain C:\SLM-WORKSHOP\models\it and
C:\SLM-WORKSHOP\models\embedder. No workshop files or model weights are copied or modified.

