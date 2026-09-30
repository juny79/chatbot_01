"""Retrieval-augmented generation using FAISS results and Phi."""

from __future__ import annotations

from dataclasses import dataclass

from app.inference import PhiInference
from app.vector_search import SearchResult, VectorSearcher


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
    def _context(results: list[SearchResult]) -> str:
        sections = []
        for index, result in enumerate(results, start=1):
            location = result.source
            if result.page:
                location += f" (p.{result.page})"
            sections.append(f"[근거 {index} | {location}]\n{result.text}")
        return "\n\n".join(sections)

    def answer(
        self,
        question: str,
        top_k: int = 3,
        min_score: float = 0.3,
    ) -> RAGResponse:
        results = self.searcher.search(question, top_k=top_k, min_score=min_score)
        if not results:
            return RAGResponse(
                answer="관련 문서에서 답변의 근거를 찾지 못했습니다.",
                sources=[],
            )

        system_prompt = (
            "당신은 문서 근거 기반 한국어 FAQ 도우미입니다.\n"
            "아래 CONTEXT에 포함된 정보만 사용해 질문에 답하세요.\n"
            "근거가 부족하면 추측하지 말고 '제공된 문서에서 확인할 수 없습니다'라고 답하세요.\n"
            "답변 본문에 문서에 없는 내용을 추가하지 마세요.\n\n"
            f"CONTEXT:\n{self._context(results)}"
        )
        answer = self.generator.generate(question, system_prompt=system_prompt)
        return RAGResponse(answer=answer, sources=results)
