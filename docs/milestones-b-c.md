# Milestones B and C

MILESTONE: B + C
STATUS: COMPLETE
TESTS: Docker Compose healthy; PostgreSQL vector extension/tables/seed data verified; Redis SET/GET/TTL verified; FastMCP in-process client verified; real search, lease collision, commit, invalid-token rejection, and PostgreSQL two-connection concurrency test passed; pytest 49 passed.

Infrastructure uses named volumes `apollo_postgres_data` and `apollo_redis_data`, loopback ports, health checks, environment-based PostgreSQL credentials, and read-only schema mounting. `database/init_db.sql` creates pgvector, doctors, slots, patients, tariffs, clinic_policies with vector(384), policy_chunks, and appointments with fictional seed rows.

`DatabaseService` uses parameterized SQL and PostgreSQL is final authority. The commit path atomically updates `slots` with `is_booked=FALSE`, reads trusted tariff data, and inserts an appointment with a unique idempotency key. RedisLeaseService uses only a 45-second NX/EX staging lease. FastMCP exposes typed search_doctor_slots, stage_slot_lease, and commit_slot_booking tools; the client was exercised against the in-process server. Invalid/expired leases and occupied slots fail closed.

Live results: PostgreSQL and Redis containers healthy; vector extension present; required tables present; 2 doctors and 2 slots seeded; Redis returned SET=True, GET=ok, TTL=45; search returned 1 cardiology slot; first lease acquired and second collided; booking committed one appointment; reuse with the old lease was rejected; concurrent PostgreSQL updates returned [False, True], exactly one winner.

Full pytest suite: 49 passed in 1.74s. No Docker or database test was faked. No Git commit or push.

BLOCKER: none for B/C. Continue with D: pgvector policy ingestion/retrieval and specialized agents.
