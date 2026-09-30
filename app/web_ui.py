"""Streamlit web UI for the document-grounded FAQ chatbot."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.chunking import chunk_documents
from app.document_loader import load_directory
from app.embedding import EmbeddingIndex
from app.rag import RAGService

RAW_DIR = Path("data/raw")
VECTORSTORE_DIR = Path("vectorstore")
SUPPORTED_TYPES = ["pdf", "docx", "txt", "md", "markdown", "html", "htm"]


st.set_page_config(
    page_title="문서기반 FAQ 챗봇",
    page_icon="?",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { max-width: 1180px; padding-top: 2rem; }
    [data-testid="stChatMessage"] { border-radius: 14px; padding: 0.8rem 1rem; }
    .hero { padding: 1.2rem 1.4rem; border-radius: 16px; background: linear-gradient(135deg, #eef4ff, #f8faff); border: 1px solid #dbe7ff; margin-bottom: 1.2rem; }
    .hero h1 { margin: 0; color: #173b7a; }
    .hero p { margin: 0.4rem 0 0; color: #52627a; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def get_rag_service() -> RAGService:
    return RAGService(vectorstore=str(VECTORSTORE_DIR), embedding_device="cpu")


def build_vectorstore() -> tuple[int, int]:
    documents = load_directory(RAW_DIR)
    chunks = chunk_documents(documents)
    if not chunks:
        raise ValueError("data/raw에 지원되는 문서가 없습니다.")
    embedder = EmbeddingIndex(device="cpu")
    index = embedder.build(chunks, batch_size=2)
    embedder.save(index, chunks, VECTORSTORE_DIR)
    return len(documents), len(chunks)


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander(f"참조 문서 {len(sources)}개", expanded=False):
        for source in sources:
            location = source["source"]
            if source.get("page"):
                location += f" · {source['page']}페이지"
            st.markdown(f"**{location}** · 유사도 `{source['score']:.3f}`")
            st.caption(source["text"][:400])


def main() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "안녕하세요. 등록된 문서를 근거로 답변하는 FAQ 챗봇입니다. 궁금한 내용을 질문해 주세요.",
                "sources": [],
            }
        ]

    with st.sidebar:
        st.markdown("## 챗봇 설정")
        st.caption("문서 기반 검색·답변 시스템")
        st.divider()

        index_exists = (VECTORSTORE_DIR / "index.faiss").exists()
        if index_exists:
            st.success("검색 인덱스 준비됨")
        else:
            st.warning("검색 인덱스가 없습니다")

        st.markdown("### 문서 관리")
        uploads = st.file_uploader(
            "문서 추가",
            type=SUPPORTED_TYPES,
            accept_multiple_files=True,
            help="PDF, DOCX, TXT, Markdown, HTML 파일을 추가할 수 있습니다.",
        )
        if uploads and st.button("문서 저장 및 인덱스 재생성", use_container_width=True):
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            for upload in uploads:
                (RAW_DIR / upload.name).write_bytes(upload.getvalue())
            with st.spinner("문서를 분석하고 검색 인덱스를 생성하는 중입니다..."):
                try:
                    document_count, chunk_count = build_vectorstore()
                    get_rag_service.clear()
                    st.success(f"문서 {document_count}개, Chunk {chunk_count}개를 반영했습니다.")
                    st.rerun()
                except Exception as error:
                    st.error(f"인덱스 생성에 실패했습니다: {error}")

        st.divider()
        if st.button("대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.caption("10GB VRAM 기준: BGE-M3 검색은 CPU, Phi 답변은 GPU 우선")

    st.markdown(
        '<div class="hero"><h1>문서기반 FAQ 챗봇</h1><p>등록된 문서를 찾아 근거와 함께 답변합니다.</p></div>',
        unsafe_allow_html=True,
    )

    if not index_exists:
        st.info("왼쪽 사이드바에서 문서를 업로드하고 '문서 저장 및 인덱스 재생성'을 눌러 시작하세요.")
        st.markdown("#### 빠른 시작")
        st.markdown("1. PDF, DOCX, TXT, Markdown 또는 HTML 문서를 업로드합니다.\n2. 검색 인덱스를 생성합니다.\n3. 아래 입력창에서 질문합니다.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            render_sources(message.get("sources", []))

    prompt = st.chat_input("문서에 대해 질문해 주세요...")
    if prompt:
        if not index_exists:
            st.warning("먼저 문서를 업로드하고 검색 인덱스를 생성해 주세요.")
            return

        st.session_state.messages.append({"role": "user", "content": prompt, "sources": []})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("관련 문서를 찾고 답변을 작성하는 중입니다..."):
                try:
                    response = get_rag_service().answer(prompt)
                    sources = [
                        {
                            "source": item.source,
                            "page": item.page,
                            "score": item.score,
                            "text": item.text,
                        }
                        for item in response.sources
                    ]
                    st.markdown(response.answer)
                    render_sources(sources)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response.answer, "sources": sources}
                    )
                except Exception as error:
                    message = f"처리 중 오류가 발생했습니다: {error}"
                    st.error(message)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": message, "sources": []}
                    )


if __name__ == "__main__":
    main()
