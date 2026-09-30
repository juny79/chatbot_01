"""Interactive command-line chat client for the Phi model."""

from app.inference import PhiInference

EXIT_COMMANDS = {"exit", "quit", "종료"}


def main() -> None:
    print("문서기반 FAQ 챗봇을 시작합니다.")
    print("종료하려면 'exit', 'quit' 또는 '종료'를 입력하세요.\n")

    chatbot = PhiInference()
    history: list[dict[str, str]] = []

    while True:
        try:
            question = input("질문: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n챗봇을 종료합니다.")
            break

        if not question:
            continue
        if question.lower() in EXIT_COMMANDS:
            print("챗봇을 종료합니다.")
            break

        try:
            answer = chatbot.generate(question, history=history)
        except Exception as error:
            print(f"오류가 발생했습니다: {error}")
            continue

        print(f"답변: {answer}\n")
        history.extend(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ]
        )


if __name__ == "__main__":
    main()
