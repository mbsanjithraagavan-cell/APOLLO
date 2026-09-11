# APOLLO

Agentic Patient & Outpatient Logistics Orchestrator.

Project and Git root: D:\APOLLO. Verified standalone environment: D:\APOLLO\.venv.
Runtime installation and Phase 2 contracts are complete; 45 tests passed. Booking remains disabled.

External read-only resources:
- C:\SLM-WORKSHOP\models\it
- C:\SLM-WORKSHOP\models\embedder

Do not copy workshop models, adapters, datasets, or databases. The new environment
has its own runtime packages; do not link workshop site-packages.
See [runtime report](docs/runtime-environment.md), [path audit](docs/path-audit.md),
and [architecture](docs/architecture.md).

## Environment creation reference

The environment already exists. For a future approved clean setup, run in PowerShell:

```powershell
Set-Location D:\APOLLO
$env:PYTHONDONTWRITEBYTECODE='1'
$env:TEMP='D:\APOLLO\scripts\tmp'
$env:TMP=$env:TEMP
New-Item -ItemType Directory -Force $env:TEMP | Out-Null
& 'C:\SLM-WORKSHOP\venv\Scripts\python.exe' -B -m venv D:\APOLLO\.venv
& 'D:\APOLLO\.venv\Scripts\python.exe' --version
& 'D:\APOLLO\.venv\Scripts\python.exe' -B -m pip install --no-cache-dir --only-binary=:all: -r D:\APOLLO\requirements.txt
& 'D:\APOLLO\.venv\Scripts\python.exe' -B -m pip check
```

No --system-site-packages or .pth bridge. requirements.txt lists inference and
application dependencies plus pytest; dependencies resolve transitively.
The old workshop-wide constraint snapshots are historical, not installation inputs.

The app reads environment variables explicitly; .env.example is a reference,
not a real secrets file. Keep external model paths on C:. The readiness CLI is
`python -B -m app.cli`; it does not perform a booking. The graph and services
remain Phase 0 boundaries. Docker, database integration, and Phases 3–5 are not
implemented by this migration/report task.

Local structured JSON tracing is the baseline for later implementation.
Langfuse is not included. LangGraph's transitive LangSmith package does not
authorize remote tracing; keep tracing disabled and do not configure cloud keys.



See [Phase 2 results](docs/phase-2.md) for contracts, validation limits, and exact executed checks.
