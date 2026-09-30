"""Phi-3.5-mini-instruct tokenizer and model loading utilities."""

from __future__ import annotations

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from app.config import settings


def resolve_device() -> str:
    """Resolve the configured device without hiding a CUDA configuration error."""
    if settings.device == "cpu":
        return "cpu"
    if settings.device == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("DEVICE=cuda 이지만 CUDA를 사용할 수 없습니다.")
        return "cuda"
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_phi_model():
    """Load the tokenizer and model with conservative settings for 10GB VRAM."""
    device = resolve_device()
    tokenizer = AutoTokenizer.from_pretrained(settings.model_id)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model_kwargs = {
        "low_cpu_mem_usage": True,
    }

    if device == "cuda" and settings.load_in_8bit:
        model_kwargs.update(
            {
                "device_map": "auto",
                "quantization_config": BitsAndBytesConfig(load_in_8bit=True),
                "torch_dtype": torch.float16,
            }
        )
    elif device == "cuda":
        model_kwargs.update(
            {
                "device_map": "auto",
                "torch_dtype": torch.float16,
            }
        )
    else:
        model_kwargs.update({"torch_dtype": torch.float32})

    model = AutoModelForCausalLM.from_pretrained(settings.model_id, **model_kwargs)
    if device == "cpu":
        model.to(device)
    model.eval()
    return tokenizer, model
