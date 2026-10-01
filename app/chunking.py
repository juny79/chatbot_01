"""Split loaded documents into source-aware chunks."""

from __future__ import annotations

from dataclasses import dataclass

from app.document_loader import LoadedDocument


@dataclass(frozen=True)
class DocumentChunk:
    text: str
    chunk_id: int
    source: str
    file_type: str
    page: int | None = None

    @property
    def metadata(self) -> dict[str, str | int | None]:
        return {
            "chunk_id": self.chunk_id,
            "source": self.source,
            "file_type": self.file_type,
            "page": self.page,
        }


def split_document(
    document: LoadedDocument,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[DocumentChunk]:
    """Split text by character windows while retaining source metadata."""
    if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_size는 양수이고 chunk_overlap은 chunk_size보다 작아야 합니다.")


    # Keep line boundaries so Markdown tables, headings, and flow descriptions
    # remain interpretable after extraction.
    text = "\n".join(
        line.strip() for line in document.text.splitlines() if line.strip()
    )
    chunks: list[DocumentChunk] = []
    start = 0
    chunk_id = 0
    step = chunk_size - chunk_overlap

    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        content = text[start:end].strip()
        if content:
            chunks.append(
                DocumentChunk(
                    text=content,
                    chunk_id=chunk_id,
                    source=document.source,
                    file_type=document.file_type,
                    page=document.page,
                )
            )
            chunk_id += 1
        if end >= len(text):
            break
        start = max(start + step, end - chunk_overlap)

    return chunks


def chunk_documents(
    documents: list[LoadedDocument],
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[DocumentChunk]:
    """Split all loaded documents."""
    chunks: list[DocumentChunk] = []
    for document in documents:
        chunks.extend(split_document(document, chunk_size, chunk_overlap))
    return chunks
