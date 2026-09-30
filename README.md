# 문서기반 FAQ 챗봇

Microsoft의 `Phi-3.5-mini-instruct` 언어 모델과 문서 검색 기술을 결합한 문서기반 FAQ 챗봇 실습 프로젝트입니다. 사용자의 질문과 관련된 문서를 검색한 뒤 검색 결과를 근거로 답변을 생성하고, 최종적으로 웹 UI와 음성 질문 기능까지 확장하는 것을 목표로 합니다.

## 프로젝트 목표

- PDF, Word, Markdown, TXT 등 업무 문서를 검색 가능한 형태로 처리합니다.
- 문서를 Chunk로 나누고 임베딩하여 벡터 검색을 수행합니다.
- `Phi-3.5-mini-instruct`가 검색된 문서만 근거로 답변하도록 구성합니다.
- 답변에 참조 문서와 출처를 표시합니다.
- 근거가 부족한 경우 추측하지 않고 안내하도록 구성합니다.
- CLI, 웹 UI, API, 음성 입력으로 단계적으로 확장합니다.
- 모든 구현 과정을 버전별 보고서와 Git 커밋으로 기록합니다.

## 아키텍처

```text
문서 수집
  ↓
텍스트 추출 및 Chunk 분할
  ↓
BAAI/bge-m3 임베딩
  ↓
FAISS 또는 Chroma 벡터 검색
  ↓
검색 결과를 Context로 구성
  ↓
Phi-3.5-mini-instruct 답변 생성
  ↓
답변 + 참조 문서 반환
```

음성 질문 기능은 다음 흐름으로 확장합니다.

```text
음성 입력
  ↓
Whisper large-v3-turbo 전사
  ↓
문서 검색 및 RAG 답변
```

## 사용 모델

| 구분 | 모델 |
|---|---|
| 언어 모델 | `microsoft/Phi-3.5-mini-instruct` |
| 임베딩 모델 | `BAAI/bge-m3` |
| 음성 인식 모델 | `openai/whisper-large-v3-turbo` |

## 하드웨어 및 운영 기준

- GPU VRAM: 10GB
- Phi 모델: 8비트 또는 4비트 추론 우선
- 입력 Context: 기본 최대 2,048 토큰
- 생성 토큰: 기본 최대 256 토큰
- 큰 Batch, 긴 Context, 동시 다중 요청은 피합니다.
- BGE-M3와 Whisper는 작은 Batch 또는 짧은 음성 구간 중심으로 사용합니다.

## 프로젝트 구조

```text
chatbot_01/
├── app/
│   ├── config.py          # 환경 설정
│   ├── model_loader.py    # Phi 모델 로딩
│   └── inference.py       # 단일/대화형 추론
├── data/
│   ├── raw/               # 원본 문서, Git 제외
│   └── processed/         # 전처리 결과, Git 제외
├── docs/
│   ├── ROADMAP.md         # 전체 로드맵
│   ├── REPORT_v0.1.0_phi-inference.md
│   ├── REPORT_v0.2.0_interactive-cli.md
│   └── REPORT_v0.3.0_document-loader.md
├── scripts/
│   ├── test_phi_model.py       # 단일 질문 테스트
│   ├── chat_cli.py             # 대화형 CLI
│   └── test_document_loader.py # 문서 로더 테스트
├── tests/
├── requirements.txt
└── README.md
```

## 환경 구성

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

NVIDIA GPU 환경에서는 PyTorch를 CUDA 버전에 맞춰 먼저 설치한 뒤 나머지 패키지를 설치합니다. 설치 후 CUDA를 확인합니다.

```bash
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

## 실행 방법

### 단일 질문 테스트

```bash
source .venv/bin/activate
python -m scripts.test_phi_model
```

질문을 직접 입력할 수도 있습니다.

```bash
python -m scripts.test_phi_model "휴가 신청 절차를 알려주세요."
```

### 대화형 CLI

```bash
python -m scripts.chat_cli
```

실행 후 질문을 입력하고, `exit`, `quit` 또는 `종료`를 입력하면 종료합니다.

현재 CLI는 모델 기본 추론과 대화 이력 확인을 위한 단계이며, 문서 검색 기능은 이후 RAG 단계에서 연결합니다.

### 문서 로더 테스트

문서를 `data/raw/`에 넣은 후 지원 형식의 텍스트 추출을 확인합니다.

```bash
python -m scripts.test_document_loader
```

지원 형식은 TXT, Markdown, PDF, DOCX, HTML입니다. PDF는 페이지별로 출처 메타데이터를 보존합니다.

## Hugging Face 인증

공개 모델은 인증 없이 다운로드될 수 있지만 안정적인 접근을 위해 Read 권한 토큰 사용을 권장합니다.

```bash
pip install -U huggingface_hub
hf auth login
hf auth whoami
```

또는 로컬 `.env`에 `HF_TOKEN`을 설정할 수 있습니다. `.env`는 절대로 GitHub에 커밋하지 않습니다.

## 개발 로드맵 및 보고서

- 전체 계획: [docs/ROADMAP.md](docs/ROADMAP.md)
- 버전별 보고서: [docs/](docs/)

주요 계획은 문서 처리, BGE-M3 임베딩, 벡터 검색, RAG 답변, Streamlit UI, FastAPI API, Whisper 음성 입력 순서로 진행합니다.

## GitHub 기록 규칙

```bash
git add -A
git commit -m "feat: describe implemented feature"
git push origin main
```

커밋과 버전별 보고서에는 구현 내용, 실행 방법, 확인 결과, 문제점, 다음 계획을 기록합니다.

## 보안 및 데이터 관리

- `.env`, Hugging Face 토큰, GitHub 토큰을 커밋하지 않습니다.
- 모델 가중치, 원본 문서, 벡터 저장소는 Git에 올리지 않습니다.
- 공개하면 안 되는 업무 문서는 `data/raw/`에 저장하되 Git에서 제외합니다.
- 10GB VRAM 환경에서는 긴 Context와 큰 Batch를 피합니다.
