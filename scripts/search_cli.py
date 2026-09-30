"""Search the local FAQ vector index from the command line."""

import argparse

from app.vector_search import VectorSearcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Search the FAQ vector index")
    parser.add_argument("query", help="검색 질문")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--min-score", type=float, default=0.0)
    args = parser.parse_args()

    searcher = VectorSearcher()
    results = searcher.search(args.query, args.top_k, args.min_score)
    if not results:
        print("검색 결과가 없습니다.")
        return

    for rank, result in enumerate(results, start=1):
        page = f", page={result.page}" if result.page else ""
        print(f"[{rank}] score={result.score:.4f}, source={result.source}{page}")
        print(result.text)
        print()


if __name__ == "__main__":
    main()
