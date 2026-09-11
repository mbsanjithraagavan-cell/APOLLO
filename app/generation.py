"""Local Gemma wrapper with strict structured JSON output and bounded generation."""
import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.config import Settings
from app.llm import load_base_model

T = TypeVar("T", bound=BaseModel)


class LocalGemma:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model, self.tokenizer = load_base_model(settings)

    def _prompt(self, instruction: str) -> str:
        return self.tokenizer.apply_chat_template(
            [{"role": "system", "content": "Return only valid JSON. Never provide diagnosis or medication advice. Use the requested schema exactly; omit optional fields."},
             {"role": "user", "content": instruction}],
            tokenize=False, add_generation_prompt=True,
        )

    def generate_json(self, instruction: str, schema: type[T]) -> T:
        import torch
        prompt = self._prompt(instruction)
        inputs = self.tokenizer([prompt], return_tensors="pt")
        with torch.inference_mode():
            output = self.model.generate(**inputs, max_new_tokens=self.settings.max_new_tokens, do_sample=False)
        text = self.tokenizer.decode(output[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise ValueError("Model did not return a JSON object")
        try:
            return schema.model_validate(json.loads(match.group(0)))
        except (json.JSONDecodeError, ValidationError) as exc:
            raise ValueError("Model JSON failed schema validation") from exc
