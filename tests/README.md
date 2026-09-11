# Phase 2 tests

Run from D:\APOLLO:
```powershell
& 'D:\APOLLO\.venv\Scripts\python.exe' -m pytest -q
```

test_phase2.py validates configuration, confidence and lease bounds, booking
confirmation, Decimal billing, safety assessments, slot/lease coherence,
notifications, state serialization, and LLM-view privacy. The completed run
passed all 45 cases. These tests do not load models or connect to infrastructure.

Future phases must separately test early safety rejection before any lease,
billing or commit; citations; lease ownership/expiry; concurrency; idempotency;
and post-commit failure handling. None of those services is implemented here.

