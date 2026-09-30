"""Inspect documents loaded from data/raw or a supplied directory."""

import argparse

from app.document_loader import load_directory


def main() -> None:
    parser = argparse.ArgumentParser(description="Test document loading")
    parser.add_argument("directory", nargs="?", default="data/raw")
    args = parser.parse_args()

    documents = load_directory(args.directory)
    print(f"로드된 문서 레코드: {len(documents)}개")
    for index, document in enumerate(documents, start=1):
        preview = " ".join(document.text.split())[:120]
        print(f"[{index}] {document.metadata} | {preview}")


if __name__ == "__main__":
    main()
