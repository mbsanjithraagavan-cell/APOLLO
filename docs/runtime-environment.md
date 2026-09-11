> Installation and Phase 2 are now complete. See phase-2.md for executed verification; the dependency planning details below are retained for reference.
# Standalone runtime and migration report

## Verified workspace
Get-Location returned D:\APOLLO. A temporary write probe succeeded and was removed.
Git root returned D:/APOLLO; branch main has no commits. Scaffold files are present.
Both C:\SLM-WORKSHOP\models\it and C:\SLM-WORKSHOP\models\embedder were readable.
No workshop files were modified or copied. D:\APOLLO\.venv has now been created and verified.
The requested environment is a directory inside the project, exactly as specified.

## Complete path audit
[path-audit.md](path-audit.md) records every original occurrence, with filename,
line number, and original text: **117 occurrences on 115 lines**.
- README.md: 7 lines (8 occurrences).
- scripts/prepare_environment.py: 2 lines.
- docs/phase-0.md: 1 line (2 occurrences).
- docs/installation.log: 105 lines.

Updated active project-root instructions and replaced the obsolete package-link
bootstrap with a standalone venv bootstrap. The Phase 0 report is marked historical
and its project paths were updated. The original installation log is evidence of
a past run, not an active project path; its 105 matching lines are preserved.
The audit also intentionally preserves the original matches. All other searched
files are free of the old project-root spelling. Searches included hidden and
ignored files and Git metadata, with ordinary and escaped backslashes and forward
slashes. Binary files are not interpreted as text. No workshop path was replaced.

## Exact direct requirements

| Package | Version | Purpose | Compatible wheel |
| --- | --- | --- | --- |
| torch | 2.14.0 | Gemma and embedder inference | cp313 Windows AMD64 |
| transformers | 5.16.1 | Gemma loader/tokenizer/generation | Universal Python |
| sentence-transformers | 6.0.1 | Local embedder inference | Universal Python |
| pydantic | 2.13.5 | Validated application contracts | Universal; native core resolved |
| langgraph | 1.2.11 | StateGraph orchestration | Universal Python |
| fastmcp | 4.0.3 | MCP server and client | Universal Python |
| psycopg[binary] | 3.3.5 | PostgreSQL driver and bundled libpq | Driver universal; binary cp313 Windows AMD64 |
| pgvector | 0.5.0 | PostgreSQL vector adaptation | Universal Python |
| redis | 8.1.0 | Lease client | Universal Python |
| pytest | 9.1.1 | Requested runnable tests (development dependency) | Universal Python |
| reportlab | 5.0.1 | Confirmation PDFs | Universal Python |
| websockets | 16.0 | Compatible shared LangGraph/FastMCP transport dependency | cp313 Windows AMD64 |

requirements.txt contains these 12 pins and references
[the exact 130-distribution constraint set](runtime-constraints.txt).
The old apollo-constraints.txt and environment-constraints.txt are historical
workshop snapshots and are no longer used by installation.

Transitive packages supply numpy, scipy, scikit-learn, tokenizers, safetensors,
Jinja2, Hugging Face Hub, MCP, and langchain-core. Do not add full LangChain.
Do not enable Transformers or SentenceTransformers training/dev/vision extras.
No PEFT, TRL, datasets, bitsandbytes, Accelerate, or Langfuse was resolved.
The fast tokenizer JSON already present in the model directory avoids a need for
the optional SentencePiece conversion stack. Transformers 5.16.1 ignores
low_cpu_mem_usage; CPU loading without device_map/GGUF does not need Accelerate.
These conclusions are for the current text-only local inference path.

Local structured JSON tracing remains the implementation baseline. LangSmith and
OpenTelemetry API are transitive dependencies, not authorization to enable remote
tracing. No Langfuse or cloud tracing configuration was added.

## Compatibility evidence and limits
Executed a pip dry-run with --ignore-installed, --only-binary=:all: and
--no-cache-dir using Python 3.13.7 on this Windows host. It successfully resolved
130 packages entirely from wheels without installing any package. This checks a
clean dependency set instead of inheriting the workshop environment.

The selected FastMCP API is from fastmcp import FastMCP, Client; it resolves MCP
2.2.0. LangGraph resolves langchain-core 1.6.2 and langgraph-sdk 0.4.4.
websockets 16.0 satisfies both; 17.1 from the workshop must not be carried into
the standalone environment. Pydantic 2.13.5 satisfies the selected dependencies.
All native transitive wheels, including numpy, scipy, scikit-learn, tokenizers,
pydantic-core, and psycopg-binary, passed binary-only resolution.

Some transitive versions differ from the workshop, including huggingface-hub
1.31.0 and scikit-learn 1.9.1. The new constraint file pins the resolved choices.
This is resolver compatibility, not proof of runtime model behavior in the new
environment. After approved installation, run pip check, imports, Gemma loading,
and the one-text embedding test; expected prior measured shape is (1, 384).
No model test or application phase was executed as part of this migration task.

## Exact future commands (not executed)
Run in PowerShell:

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

The clean venv has its own packages. Do not create a .pth bridge or use
--system-site-packages. Keep APOLLO_MODEL_DIR and APOLLO_EMBEDDER_DIR pointing
to the external workshop model directories. Do not download model weights.

## Disk usage
Official PyPI metadata for all 130 selected wheel URLs totals **254,003,648 bytes**
(about **242.2 MiB**) compressed. See wheel-sizes.json for each wheel.
Estimated installed venv size: **1–2 GiB**, allowing for unpacked native libraries
and Python metadata. Reserve **3 GiB free** for the environment and temporary
installation files. This is an estimate, not an installed-size measurement.
About 175 GiB was free on D: at inspection. Additional model weight storage is
**zero**: the existing external models remain in place.

## Git safety
Executed git check-ignore for .venv/, .env, nested __pycache__/, *.pyc,
.pytest_cache/, logs/, output/*.pdf, *.gguf, *.safetensors, *.bin, models/,
checkpoints/, adapter*/, and chroma_db/: every probe was ignored.
The local .venv directory is excluded by .gitignore. No files were staged, committed,
or pushed. Git has no commits on main.

## Sources
- https://pypi.org/pypi/torch/2.14.0/json
- https://pypi.org/pypi/transformers/5.16.1/json
- https://pypi.org/pypi/sentence-transformers/6.0.1/json
- https://pypi.org/pypi/fastmcp/4.0.3/json
- https://pypi.org/pypi/langgraph/1.2.11/json
- https://pypi.org/pypi/psycopg-binary/3.3.5/json

The remaining package/version endpoints and exact wheel filenames are captured in
runtime-metadata.json, standalone-resolution.json, and wheel-sizes.json.



