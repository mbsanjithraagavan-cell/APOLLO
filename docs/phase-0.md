> Historical Phase 0 report. Setup strategy below is superseded by runtime-environment.md; do not run historical commands.
# Phase 0 inspection — 2026-09-10

## Executed environment checks

Authoritative interpreter: C:\SLM-WORKSHOP\venv\Scripts\python.exe --version
returned **Python 3.13.7**. Initial sandbox execution was denied; approved
execution outside the sandbox succeeded. Imports and model checks used -B,
PYTHONDONTWRITEBYTECODE, and offline Hugging Face settings. Workshop scripts
were read as text, not executed, because several write logs, databases, or models.

| Requested package | Installed version / import result |
| --- | --- |
| pydantic | 2.13.5, import succeeded |
| torch | 2.14.0, import succeeded |
| transformers | 5.16.1, import succeeded |
| sentence_transformers | 6.0.1, import succeeded |
| langgraph | missing distribution |
| langchain_core | missing distribution |
| fastmcp | missing distribution |
| mcp | missing distribution |
| psycopg | missing distribution |
| pgvector | missing distribution |
| redis | missing distribution |
| pytest | missing distribution |
| reportlab | missing distribution |
| langfuse | missing distribution |

The complete 117-distribution metadata snapshot is environment-constraints.txt.
It contains version metadata only, not copied workshop content.

## Model checks

Loaded the tokenizer and base checkpoint directly from C:\SLM-WORKSHOP\models\it
with local_files_only=True, AutoModelForCausalLM, CPU float32, and low-memory
loading. Result: Gemma3ForCausalLM, 999,885,952 parameters. No adapter was loaded;
no generation benchmark was run. Model identity is consistent with the workshop's
google/gemma-3-1b-it setting and local config; no upstream weight hash verification
was performed. Here “base” means the original instruction-tuned checkpoint before
the workshop's oil-field adaptation.

Loaded C:\SLM-WORKSHOP\models\embedder with SentenceTransformer on CPU.
Encoded ["APOLLO embedding dimension test"]. Actual embedding.shape: **(1, 384)**.
The SQL policy vector column therefore uses vector(384).

## Oil-field behavior source

Inspected requirements.txt, verify_setup.py, tests/test_00_base_slm.py,
01_rag_baseline.py, 02_finetune_qlora.py, 04_gguf_rag.py, and config.py.
Also inspected the adapter/merge path in 03_quantize_gguf.py to resolve GGUF provenance.

- config.py supplies BASE_SYSTEM_PROMPT, RAG_SYSTEM_PROMPT, and
  EXACT_RAG_SYSTEM_PROMPT with explicit oil-field roles and output formats.
- tests/test_00_base_slm.py loads the original checkpoint, supplies the base
  oil-field prompt, and uses a crude-transfer pump troubleshooting question.
  Oil-field replies in that test do not imply the base weights were fine-tuned.
- 01_rag_baseline.py embeds data/rag documents into ChromaDB collection
  workshop_knowledge; existing collections are reused unless explicitly rebuilt.
- 02_finetune_qlora.py trains LoRA using data/finetune/train.jsonl, an oil-field
  system instruction, and formatted maintenance resolution answers. It writes
  models/adapter_<timestamp>, not the original model directory.
- 03_quantize_gguf.py selects the newest adapter, loads it with PeftModel,
  merges it into a separate checkpoint, and produces the quantized output.
- 04_gguf_rag.py selects the newest matching GGUF, retrieves workshop Chroma
  context, and chooses an oil-field system prompt based on retrieval distance.

Thus prompts, corpus, and adapted GGUF collectively produce the workshop's
domain behavior. APOLLO references the unadapted checkpoint and embedder only.
This establishes the scripted provenance; it does not certify the historical
origin of every existing GGUF or the exact contents of every weight tensor.

## Local infrastructure

docker, psql, pg_isready, and redis-cli were not found on PATH. Consequently
docker --version and docker compose version could not be executed; Compose is
unavailable through the current PATH. No PostgreSQL/Redis/Docker-named service
was found. Elevated listener inspection found no listeners on TCP 5432 or 6379.
This does not exclude installations elsewhere or services on non-default ports.
No infrastructure was installed, pulled, or started.

## Dependency decision

PyPI version metadata confirmed that all seven proposed candidate releases exist
and allow Python 3.13. A psycopg-binary 3.3.5 cp313 Windows AMD64 wheel exists.
FastMCP 4.0.3 depends on fastmcp-slim[client,server]==4.0.3, MCP >=2,<3,
and Pydantic >=2.12, compatible with installed 2.13.5. Use
`from fastmcp import FastMCP, Client`, `@server.tool`, `server.run`, and
`async with Client(...)`. Do not use the SDK v1 mcp.server.fastmcp import.
These interfaces were checked in current official documentation but not imported
locally, because FastMCP remains uninstalled.

LangGraph 1.2.11 directly requires langchain-core >=1.4.7,<2, checkpoint
>=4.1,<5, prebuilt >=1.1,<1.2, SDK >=0.4.2,<0.5, Pydantic >=2.7.4,
and xxhash >=3.5. Let its dependencies supply langchain-core; do not add full
langchain. Langfuse is deferred because optional tracing is not needed in Phase 0.

The first attempt encountered a network reset. A completed strict dry-run then
found a real conflict: installed websockets 17.1 violates langgraph-sdk's <17
requirement. A second completed dry-run preserved all other installed version
constraints and successfully resolved **websockets 16.0** with all seven candidates.
It selected langchain-core 1.6.2, langgraph-sdk 0.4.4, MCP 2.2.0 and their transitives.
No packages were installed. Dry-run downloaded metadata/wheels temporarily inside
APOLLO, not workshop resources. Resolver logs and the full JSON report are ignored
local evidence. A successful resolver is not a runtime integration test.

Use an APOLLO-local venv referencing workshop site-packages through a .pth file,
then install additions/overrides only into APOLLO. The bootstrap is written but
has not been executed. See README.md for the preparation command and environment
variables. Exact proposed pip command, after that preparation:

```powershell
& 'D:\APOLLO\.venv\Scripts\python.exe' -B -m pip install --no-cache-dir --only-binary=:all: -r D:\APOLLO\requirements.txt
```

Sources checked:
- https://pypi.org/pypi/fastmcp/4.0.3/json
- https://pypi.org/pypi/fastmcp-slim/4.0.3/json
- https://pypi.org/pypi/langgraph/1.2.11/json
- https://pypi.org/pypi/psycopg-binary/3.3.5/json
- https://gofastmcp.com/servers/server
- https://gofastmcp.com/clients/client

## Verification limits

Base model load, the single embedding, requested installed-package imports,
CLI readiness, and syntax parsing were executed. No generation benchmark,
pytest run, MCP runtime call, SQL execution, Compose launch, or booking workflow
was executed. The graph file is a documented implementation boundary, not a
working graph. Git initialization and final access checks are recorded in the
completion response. No commit, staging, remote, or GitHub repository creation
is requested for Phase 0.

