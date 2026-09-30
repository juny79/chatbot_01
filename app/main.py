"""Initial application entry point."""

from app.config import settings


def main() -> None:
    print("FAQ chatbot project is ready.")
    print(f"Language model: {settings.model_id}")
    print(f"Embedding model: {settings.embedding_model_id}")
    print(f"Whisper model: {settings.whisper_model_id}")
    print(f"Device: {settings.device}")
    print(f"8-bit loading: {settings.load_in_8bit}")


if __name__ == "__main__":
    main()
