# APOLLO architecture
Requests enter a LangGraph StateGraph, are PII-sanitized, classified by the early safety gate, and then routed to policy RAG or booking. Booking uses scoped FastMCP tools, Redis for a 45-second staging lease, and PostgreSQL as the authoritative commit store. The final slot update is conditional on `is_booked = FALSE`, so concurrent requests cannot both commit.

Policy retrieval uses the external SentenceTransformer model at `C:\SLM-WORKSHOP\models\embedder`; Gemma remains external at `C:\SLM-WORKSHOP\models\it`. No model files are copied into APOLLO.
