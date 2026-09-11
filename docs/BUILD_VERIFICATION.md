# Build verification

Observed final verification results:

- Docker PostgreSQL: healthy.
- Docker Redis: healthy.
- FastMCP live booking: succeeded.
- MCP tools invoked: `search_doctor_slots`, `stage_slot_lease`, `commit_slot_booking`.
- Cardiology slot 101 booked successfully.
- PostgreSQL appointment created.
- Redis lease consumed; `EXISTS` returned `0`.
- Deterministic billing: subtotal INR 350.00, tax INR 17.50, total INR 367.50.
- Notification HTML and PDF generated.
- Email and calendar outputs marked `SIMULATED`.
- Real pgvector RAG succeeded with chunks `chunk_checkin_01`, `chunk_prep_01`, and `chunk_visit_01`.
- Citations validated; RAG confidence `0.85`; SafetyCritic decision `allow`.
- Safety demo: disposition `emergency`, confidence `0.99`.
- Live MCP integration test passed.
- Complete test suite: `86 passed`; one non-fatal FastMCP/Pydantic warning.

No credentials, service URLs, or Redis lease tokens are recorded here.
