"""Build a local BGE-M3 + FAISS index from data/raw documents."""

import argparse

from app.chunking import chunk_documents
from app.document_loader import load_directory
from app.embedding import EmbeddingIndex


def main() -> None:
    parser = argparse.ArgumentParser(description="Build FAQ embedding index")
    parser.add_argument("--input", default="data/raw")
    parser.add_argument("--output", default="vectorstore")
    parser.add_argument("--chunk-size", type=int, default=800)
    parser.add_argument("--chunk-overlap", type=int, default=120)
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()

    documents = load_directory(args.input)
    chunks = chunk_documents(documents, args.chunk_size, args.chunk_overlap)
    print(f"문서 레코드: {len(documents)}개, Chunk: {len(chunks)}개")
    if not chunks:
        raise SystemExit("data/raw에 지원되는 문서가 없습니다.")

    embedder = EmbeddingIndex()
    index = embedder.build(chunks, batch_size=args.batch_size)
    embedder.save(index, chunks, args.output)
    print(f"FAISS 인덱스를 저장했습니다: {args.output}")


if __name__ == "__main__":
    main()
