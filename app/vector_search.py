"""FAISS top-k search over the local BGE-M3 index."""

from __future__ import annotations

import json
import re
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


_TOKEN_PATTERN = re.compile(r"[가-힣A-Za-z0-9_]+")


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in _TOKEN_PATTERN.findall(text) if len(token) > 1}


def _keyword_score(query_tokens: set[str], text: str) -> float:
    if not query_tokens:
        return 0.0
    text_tokens = _tokens(text)
    return len(query_tokens & text_tokens) / len(query_tokens)


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

        # Retrieve a wider semantic candidate set, then promote exact project IDs,
        # system names, and other terms that vector similarity can under-rank.
        candidate_k = min(max(top_k * 4, 20), self.index.ntotal)
        vector = self.embedder.encode([query.strip()])
        scores, indices = self.index.search(vector, candidate_k)
        query_tokens = _tokens(query)
        ranked: list[tuple[float, SearchResult]] = []
        for semantic_score, index in zip(scores[0], indices[0]):
            semantic = float(semantic_score)
            if index < 0 or semantic < min_score:
                continue
            item = self.metadata[int(index)]
            lexical = _keyword_score(query_tokens, item["text"])
            combined = semantic * 0.75 + lexical * 0.25
            ranked.append(
                (
                    combined,
                    SearchResult(
                        score=combined,
                        text=item["text"],
                        source=item["source"],
                        file_type=item["file_type"],
                        page=item.get("page"),
                        chunk_id=int(item["chunk_id"]),
                    ),
                )
            )
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [result for _, result in ranked[:top_k]]
