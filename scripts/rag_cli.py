"""Ask questions against the local document index with Phi."""

import argparse

from app.rag import RAGService


def main() -> None:
    parser = argparse.ArgumentParser(description="Run document-grounded FAQ chat")
    parser.add_argument("question", help="질문")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--min-score", type=float, default=0.3)
    parser.add_argument("--vectorstore", default="vectorstore")
    args = parser.parse_args()

    service = RAGService(vectorstore=args.vectorstore)
    response = service.answer(args.question, args.top_k, args.min_score)
    print("[답변]")
    print(response.answer)
    print("\n[출처]")
    if not response.sources:
        print("없음")
        return
    for source in response.sources:
        location = source.source
        if source.page:
            location += f" p.{source.page}"
        print(f"- {location} (score={source.score:.4f})")


if __name__ == "__main__":
    main()
