"""FAISS top-k search over the local BGE-M3 index."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import faiss

from app.embedding import EmbeddingIndex


@dataclass(frozen=True)
class SearchResult:
    score: float
    text: str
    source: str
    file_type: str
    page: int | None
    chunk_id: int


class VectorSearcher:
    def __init__(
        self,
        directory: str | Path = "vectorstore",
        embedding_device: str | None = None,
    ):
        root = Path(directory)
        index_path = root / "index.faiss"
        metadata_path = root / "metadata.json"
        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(
                "벡터 인덱스가 없습니다. 먼저 python -m scripts.build_embeddings를 실행하세요."
            )
        self.index = faiss.read_index(str(index_path))
        self.metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if self.index.ntotal != len(self.metadata):
            raise ValueError("FAISS 인덱스와 metadata.json의 개수가 다릅니다.")
        self.embedder = EmbeddingIndex(device=embedding_device)

    def search(self, query: str, top_k: int = 3, min_score: float = 0.0) -> list[SearchResult]:
        if not query.strip():
            raise ValueError("검색 질문은 비어 있을 수 없습니다.")
        if top_k <= 0:
            raise ValueError("top_k는 1 이상이어야 합니다.")

        vector = self.embedder.encode([query.strip()])
        scores, indices = self.index.search(vector, min(top_k, self.index.ntotal))
        results: list[SearchResult] = []
        for score, index in zip(scores[0], indices[0]):
            if index < 0 or float(score) < min_score:
                continue
            item = self.metadata[int(index)]
            results.append(
                SearchResult(
                    score=float(score),
                    text=item["text"],
                    source=item["source"],
                    file_type=item["file_type"],
                    page=item.get("page"),
                    chunk_id=int(item["chunk_id"]),
                )
            )
        return results
