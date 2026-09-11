"""Lazy, local-only base Gemma loading; no adapters, GGUF, or workshop imports."""
from app.config import Settings


def load_base_model(settings: Settings):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    path = settings.model_dir
    if (path / "adapter_config.json").exists():
        raise ValueError("APOLLO requires the base checkpoint, not an adapter directory")
    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        path, local_files_only=True, trust_remote_code=False,
        dtype=torch.float32, low_cpu_mem_usage=True,
    ).eval()
    return model, tokenizer
