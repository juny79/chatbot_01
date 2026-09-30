"""Create BGE-M3 embeddings and persist a FAISS index."""

from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from app.chunking import DocumentChunk
from app.config import settings


class EmbeddingIndex:
    """Small local FAISS index for the FAQ prototype."""

    def __init__(self, model_id: str | None = None, device: str | None = None):
        if device:
            model_device = device
        elif settings.device == "cpu":
            model_device = "cpu"
        else:
            model_device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(
            model_id or settings.embedding_model_id,
            device=model_device,
        )

    def encode(self, texts: list[str], batch_size: int = 4) -> np.ndarray:
        if not texts:
            return np.empty((0, 0), dtype="float32")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )
        return np.asarray(embeddings, dtype="float32")

    def build(self, chunks: list[DocumentChunk], batch_size: int = 4) -> faiss.Index:
        vectors = self.encode([chunk.text for chunk in chunks], batch_size)
        if not len(vectors):
            raise ValueError("임베딩할 Chunk가 없습니다.")
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        return index

    @staticmethod
    def save(index: faiss.Index, chunks: list[DocumentChunk], directory: str | Path) -> None:
        output = Path(directory)
        output.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(output / "index.faiss"))
        metadata = [
            {"text": chunk.text, **chunk.metadata}
            for chunk in chunks
        ]
        (output / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
