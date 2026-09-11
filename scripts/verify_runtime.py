"""Verify the installed standalone runtime and read-only model resources."""
import gc
import importlib
import importlib.metadata as metadata
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / ".venv"
if Path(sys.prefix).resolve() != EXPECTED.resolve():
    raise SystemExit("Run with the APOLLO-local virtual environment")
modules = ["torch", "transformers", "sentence_transformers", "pydantic", "langgraph",
           "langchain_core", "fastmcp", "mcp", "psycopg", "pgvector", "redis",
           "pytest", "reportlab", "websockets"]
results = {"python": sys.version, "prefix": sys.prefix, "packages": {}}
for name in modules:
    module = importlib.import_module(name)
    distribution = metadata.distribution(name.replace("_", "-"))
    location = Path(distribution.locate_file("")).resolve()
    if not location.is_relative_to(EXPECTED.resolve()):
        raise RuntimeError(f"{name} is outside APOLLO: {location}")
    version = distribution.version
    results["packages"][name] = version
    print(f"{name}=={version} IMPORT OK ({location})", flush=True)

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
model_path = Path(r"C:\SLM-WORKSHOP\models\it")
if (model_path / "adapter_config.json").exists():
    raise RuntimeError("Adapter configuration found in base model directory")
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True, trust_remote_code=False)
model = AutoModelForCausalLM.from_pretrained(
    model_path, local_files_only=True, trust_remote_code=False, dtype=torch.float32
).eval()
assert not getattr(model, "peft_config", None)
assert not getattr(model, "_hf_peft_config_loaded", False)
results["gemma"] = {"path": str(model_path), "class": type(model).__name__,
                    "parameters": model.num_parameters(), "adapter_loaded": False}
print("GEMMA", results["gemma"], flush=True)
del model, tokenizer
gc.collect()

from sentence_transformers import SentenceTransformer
embedder = SentenceTransformer(r"C:\SLM-WORKSHOP\models\embedder",
                              local_files_only=True, device="cpu")
embedding = embedder.encode(["APOLLO embedding dimension test"])
assert embedding.shape == (1, 384), embedding.shape
results["embedding_shape"] = list(embedding.shape)
print("embedding.shape", embedding.shape, flush=True)
(ROOT / "docs" / "runtime-verification.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8")

