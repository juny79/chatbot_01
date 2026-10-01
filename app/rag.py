"""Retrieval-augmented generation using FAISS results and Phi."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from app.config import settings
from app.inference import PhiInference
from app.vector_search import SearchResult, VectorSearcher


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RAGResponse:
    answer: str
    sources: list[SearchResult]


class RAGService:
    def __init__(self, vectorstore: str = "vectorstore", embedding_device: str = "cpu"):
        # CPU embeddings leave GPU memory available for the 8-bit Phi model.
        self.searcher = VectorSearcher(vectorstore, embedding_device=embedding_device)
        self.generator = PhiInference()

    @staticmethod
    def _select_results(results: list[SearchResult], limit: int) -> list[SearchResult]:
        """Remove near-duplicate chunks while preserving the best scores."""
        selected: list[SearchResult] = []
        seen: set[tuple[str, int | None, str]] = set()
        for result in results:
            key = (result.source, result.page, result.text[:160])
            if key in seen:
                continue
            seen.add(key)
            selected.append(result)
            if len(selected) >= limit:
                break
        return selected

    @staticmethod
    def _context(results: list[SearchResult]) -> str:
        sections: list[str] = []
        used_chars = 0
        for index, result in enumerate(results, start=1):
            location = result.source
            if result.page:
                location += f" (p.{result.page})"
            section = f"[근거 {index} | {location} | 유사도 {result.score:.3f}]\n{result.text}"
            remaining = settings.max_context_chars - used_chars
            if remaining <= 0:
                break
            sections.append(section[:remaining])
            used_chars += len(section)
        return "\n\n".join(sections)

    def answer(
        self,
        question: str,
        top_k: int = 3,
        min_score: float = 0.3,
    ) -> RAGResponse:
        started = time.perf_counter()
        candidate_k = min(max(top_k * 3, top_k), 12)
        candidates = self.searcher.search(
            question,
            top_k=candidate_k,
            min_score=min_score,
        )
        results = self._select_results(candidates, top_k)
        logger.info(
            "RAG retrieval: candidates=%d selected=%d elapsed_ms=%.1f",
            len(candidates),
            len(results),
            (time.perf_counter() - started) * 1000,
        )
        if not results:
            return RAGResponse(
                answer="관련 문서에서 답변의 근거를 찾지 못했습니다.",
                sources=[],
            )

        system_prompt = (
            "당신은 대형 SI 프로젝트 문서를 근거로 답하는 한국어 FAQ 도우미입니다.\n"
            "CONTEXT에 있는 내용만 사용하고, 문서에 없는 사실·수치·일정·담당자를 만들지 마세요.\n"
            "질문에 바로 답하고, 절차는 번호 목록으로 간결하게 정리하세요.\n"
            "답변이 여러 근거를 사용하면 문장 끝에 [근거 1]처럼 표시하세요.\n"
            "근거가 부족하면 '제공된 문서에서 확인할 수 없습니다'라고 답하고 추측하지 마세요.\n\n"
            f"CONTEXT:\n{self._context(results)}"
        )
        generation_started = time.perf_counter()
        answer = self.generator.generate(question, system_prompt=system_prompt)
        logger.info(
            "RAG generation: elapsed_ms=%.1f answer_chars=%d",
            (time.perf_counter() - generation_started) * 1000,
            len(answer),
        )
        return RAGResponse(answer=answer, sources=results)
