# Milestone D — RAG and specialized agents

MILESTONE: D
STATUS: COMPLETE
TESTS: 59 passed. Ten D-specific tests cover retrieval, valid/fabricated citations, no-evidence escalation, multi-chunk grounding, tool scopes, confidence threshold, acute red flags, and scope violations.

Implemented fictional policy data in data/policies/demo_policies.json; stable chunk IDs include chunk_prep_01, chunk_fasting_01, chunk_cancel_01, chunk_checkin_01, and chunk_visit_01. PolicyService embeds with the external C:\SLM-WORKSHOP\models\embedder and stores/querys real vector(384) records in PostgreSQL clinic_policies using parameterized SQL.

PolicyRAGAgent can call only query_clinic_policies. BookingDiscoveryAgent can call only search_doctor_slots. AllocatorAgent can call only stage_slot_lease. Scope is enforced by allowed_tools in code. SafetyCritic requires confidence >= 0.7, no acute red flag, no scope violation, and grounded citations. Failed grounding produces a bounded escalation record with request ID, confidence, flags, redacted context, and timestamp.

RAG SMOKE: Query “What preparation is required before this procedure?” retrieved chunk_checkin_01, chunk_fasting_01, chunk_prep_01 with distances 0.6535, 0.6625, and 0.7085. The first Gemma draft omitted citations and correctly routed to human escalation at confidence 0.2. One bounded regeneration produced a grounded draft citing [chunk_checkin_01], [chunk_fasting_01], and [chunk_prep_01]. Citation validation passed; final confidence 0.85; final routing allow. No answer was hard-coded.

Docker PostgreSQL/pgvector and Redis remained healthy during the smoke. No Milestone A/B/C work was redone. No commit or push was performed.

NEXT: Stop after D as requested. Milestone E has not started.
