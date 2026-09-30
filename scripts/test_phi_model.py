"""Run one local Phi-3.5-mini-instruct inference test."""

import argparse

from app.inference import PhiInference


def main() -> None:
    parser = argparse.ArgumentParser(description="Test Phi-3.5-mini-instruct inference")
    parser.add_argument(
        "question",
        nargs="?",
        default="문서기반 FAQ 챗봇이란 무엇인가요?",
        help="질문 문장",
    )
    args = parser.parse_args()

    print("모델을 로딩합니다. 첫 실행에서는 모델 다운로드 시간이 필요합니다.")
    answer = PhiInference().generate(args.question)
    print("\n[질문]")
    print(args.question)
    print("\n[답변]")
    print(answer)


if __name__ == "__main__":
    main()
