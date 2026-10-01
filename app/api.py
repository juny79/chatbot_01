"""FastAPI interface for document-grounded FAQ answers."""

from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.rag import RAGService


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="사용자 질문")
    top_k: int = Field(default=3, ge=1, le=10, description="검색할 근거 수")
    min_score: float = Field(default=0.3, ge=-1.0, le=1.0, description="최소 유사도")


class SourceResponse(BaseModel):
    source: str
    file_type: str
    page: int | None
    chunk_id: int
    score: float
    text: str


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]


app = FastAPI(
    title="문서기반 FAQ 챗봇 API",
    version="0.7.0",
    description="검색된 문서 근거를 사용해 FAQ 답변을 생성합니다.",
)


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    return RAGService(vectorstore="vectorstore", embedding_device="cpu")


@app.get("/health")
def health() -> dict[str, str]:
    """Return a lightweight process health check without loading model weights."""
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="질문은 비어 있을 수 없습니다.")

    try:
        response = get_rag_service().answer(
            question,
            top_k=request.top_k,
            min_score=request.min_score,
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail="답변 생성 중 오류가 발생했습니다.") from error

    return AskResponse(
        answer=response.answer,
        sources=[
            SourceResponse(
                source=item.source,
                file_type=item.file_type,
                page=item.page,
                chunk_id=item.chunk_id,
                score=item.score,
                text=item.text,
            )
            for item in response.sources
        ],
    )
