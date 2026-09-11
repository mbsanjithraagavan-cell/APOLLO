# Integration tests

Future tests require explicitly started APOLLO PostgreSQL and Redis instances.
Use synthetic patients, isolated test data, competing booking transactions,
expired leases, idempotent retries, and notification failure recovery.
Never connect these tests to workshop databases or a hospital production system.
