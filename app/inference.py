"""Basic text generation with Phi-3.5-mini-instruct."""

from __future__ import annotations

from typing import Sequence

import torch

from app.config import settings
from app.model_loader import load_phi_model, resolve_device


class PhiInference:
    """Lazy-loading inference wrapper for a single-user local demo."""

    def __init__(self) -> None:
        self.tokenizer = None
        self.model = None

    def load(self) -> None:
        if self.model is None or self.tokenizer is None:
            self.tokenizer, self.model = load_phi_model()

    def generate(
        self,
        question: str,
        history: Sequence[dict[str, str]] | None = None,
        system_prompt: str | None = None,
    ) -> str:
        if not question.strip():
            raise ValueError("질문은 비어 있을 수 없습니다.")

        self.load()
        messages = [
            {
                "role": "system",
                "content": system_prompt
                or "당신은 정확하고 간결하게 답변하는 한국어 FAQ 도우미입니다.",
            }
        ]
        if history:
            messages.extend(history[-6:])
        messages.append({"role": "user", "content": question.strip()})
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=settings.max_input_tokens,
        )
        device = resolve_device()
        if device == "cuda" and not hasattr(self.model, "hf_device_map"):
            inputs = {key: value.to(device) for key, value in inputs.items()}
        elif device == "cuda":
            first_device = next(self.model.parameters()).device
            inputs = {key: value.to(first_device) for key, value in inputs.items()}
        else:
            inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.inference_mode():
            output = self.model.generate(
                **inputs,
                max_new_tokens=settings.max_new_tokens,
                do_sample=settings.temperature > 0,
                temperature=max(settings.temperature, 0.01),
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        prompt_length = inputs["input_ids"].shape[-1]
        answer_tokens = output[0][prompt_length:]
        return self.tokenizer.decode(answer_tokens, skip_special_tokens=True).strip()
