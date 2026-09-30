"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    model_id: str = os.getenv("MODEL_ID", "microsoft/Phi-3.5-mini-instruct")
    embedding_model_id: str = os.getenv("EMBEDDING_MODEL_ID", "BAAI/bge-m3")
    whisper_model_id: str = os.getenv(
        "WHISPER_MODEL_ID", "openai/whisper-large-v3-turbo"
    )
    device: str = os.getenv("DEVICE", "auto")
    max_input_tokens: int = int(os.getenv("MAX_INPUT_TOKENS", "2048"))
    max_new_tokens: int = int(os.getenv("MAX_NEW_TOKENS", "256"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.2"))
    load_in_8bit: bool = os.getenv("LOAD_IN_8BIT", "true").lower() == "true"


settings = Settings()


