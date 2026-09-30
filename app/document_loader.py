"""Load common document formats while preserving source metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from pypdf import PdfReader


@dataclass(frozen=True)
class LoadedDocument:
    """A document or page ready for later chunking."""

    text: str
    source: str
    file_type: str
    page: int | None = None

    @property
    def metadata(self) -> dict[str, str | int | None]:
        return {
            "source": self.source,
            "file_type": self.file_type,
            "page": self.page,
        }


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").strip()


def load_document(path: str | Path) -> list[LoadedDocument]:
    """Load one supported file into one or more source-aware records."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"문서 파일을 찾을 수 없습니다: {file_path}")

    suffix = file_path.suffix.lower()
    source = file_path.name

    if suffix in {".txt", ".md", ".markdown"}:
        text = _read_text(file_path)
        return [LoadedDocument(text, source, suffix.lstrip("."))] if text else []

    if suffix == ".pdf":
        documents: list[LoadedDocument] = []
        for page_number, page in enumerate(PdfReader(str(file_path)).pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                documents.append(LoadedDocument(text, source, "pdf", page_number))
        return documents

    if suffix == ".docx":
        document = DocxDocument(str(file_path))
        text = "\n".join(
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )
        return [LoadedDocument(text, source, "docx")] if text else []

    if suffix in {".html", ".htm"}:
        soup = BeautifulSoup(file_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        text = soup.get_text("\n", strip=True)
        return [LoadedDocument(text, source, "html")] if text else []

    raise ValueError(f"지원하지 않는 문서 형식입니다: {suffix}")


def load_directory(directory: str | Path) -> list[LoadedDocument]:
    """Load supported documents recursively from a directory."""
    root = Path(directory)
    if not root.is_dir():
        raise NotADirectoryError(f"문서 디렉터리를 찾을 수 없습니다: {root}")

    supported = {".txt", ".md", ".markdown", ".pdf", ".docx", ".html", ".htm"}
    documents: list[LoadedDocument] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in supported:
            documents.extend(load_document(path))
    return documents
