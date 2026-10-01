# 문서기반 FAQ 챗봇 실습 로드맵

이 프로젝트는 `microsoft/Phi-3.5-mini-instruct` 오픈소스 모델과 문서 검색 기술을 결합해 문서기반 FAQ 챗봇을 단계적으로 구현하는 것을 목표로 합니다.

## 프로젝트 목표

- 문서에서 사용자 질문과 관련된 내용을 검색한다.
- 검색된 문서 내용을 근거로 Phi-3.5-mini-instruct가 답변을 생성한다.
- 답변에 참조한 문서명과 출처를 표시한다.
- 관련 근거가 부족할 때는 모른다고 답하도록 구성한다.
- 개발 과정을 GitHub 커밋으로 단계별 기록한다.

## 전체 아키텍처

```text
사용자 질문
    ↓
질문 임베딩 생성
    ↓
벡터 저장소에서 관련 문서 검색
    ↓
검색 결과를 프롬프트에 삽입
    ↓
Phi-3.5-mini-instruct 답변 생성
    ↓
답변 + 참조 문서/출처 반환
```

## 단계별 계획

### 0단계. 개발 환경 및 프로젝트 초기화

- 운영체제, Python 버전, GPU 및 CUDA 환경 확인
- GitHub 저장소와 로컬 저장소 연결
- Python 가상환경 생성
- 기본 프로젝트 폴더 구조 생성
- `.gitignore` 및 기본 README 작성
- 초기 커밋 생성

### 1단계. Phi-3.5-mini-instruct 모델 실행

- Hugging Face 모델 ID 확인
  - `microsoft/Phi-3.5-mini-instruct`
- Transformers 기반 모델 로딩
- 단일 질문에 대한 텍스트 생성 테스트
- 한국어 질문 응답 확인
- GPU 메모리 부족 시 4비트 양자화 검토
- 모델 실행 결과를 실습 기록으로 남김

### 2단계. 문서 수집 및 텍스트 추출

- PDF 문서 처리
- Word 문서 처리
- Markdown 및 TXT 문서 처리
- HTML 문서 처리
- 문서명, 페이지, 섹션 등 출처 메타데이터 보존
- 원본 문서와 전처리 문서 분리 관리

### 3단계. 문서 분할 및 임베딩

- 긴 문서를 검색 가능한 Chunk로 분할
- Chunk 크기와 overlap 설정
- 한국어 문서에 적합한 임베딩 모델 비교
  - `BAAI/bge-m3`
  - `intfloat/multilingual-e5-large`
  - `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
- 각 Chunk에 문서명, 페이지, 섹션 메타데이터 추가

### 4단계. 벡터 저장소 및 RAG 검색 구현

- FAISS 또는 Chroma 도입
- 문서 Chunk 임베딩 저장
- 사용자 질문 임베딩 생성
- 유사도 기반 관련 문서 검색
- Top-k 검색 결과 확인
- 검색 결과가 없거나 낮은 경우 처리

### 5단계. 검색 결과 기반 답변 생성

- 검색된 문서를 프롬프트의 Context로 삽입
- Phi-3.5-mini-instruct로 답변 생성
- 문서 근거가 없는 추측 방지
- 답변과 출처를 함께 반환
- 한국어 답변 품질 개선

### 6단계. API 및 웹 UI 구성

- FastAPI 기반 질문 응답 API 구현
- Streamlit 또는 Gradio 기반 웹 UI 구현
- 대화 이력 관리
- 문서 업로드 기능 검토
- 질문, 검색 결과, 답변 로그 관리

### 7단계. 평가 및 개선

- 대표 FAQ 질문셋 작성
- 검색 정확도 평가
- 답변의 근거성 평가
- 정답을 찾지 못했을 때의 동작 평가
- 응답 시간과 메모리 사용량 측정
- 프롬프트와 Chunk 전략 개선

### 8단계. 배포 및 운영

- Docker 환경 구성
- 환경변수 및 비밀정보 관리
- GPU 서버 또는 클라우드 배포 검토
- 벡터 DB와 문서 저장소 운영 방식 결정
- 모델 및 데이터 버전 관리
- 운영 로그와 오류 처리 구성

## 확정 모델 및 하드웨어 프로파일

| 영역 | 선택 |
|---|---|
| 언어 모델 | `microsoft/Phi-3.5-mini-instruct` |
| 임베딩 모델 | `BAAI/bge-m3` |
| 음성 인식 모델 | `openai/whisper-large-v3-turbo` |
| GPU | VRAM 10GB |
| API | FastAPI |
| 웹 UI | Streamlit 또는 Gradio |
| 형상 관리 | GitHub |

### VRAM 10GB 운영 원칙

- Phi-3.5-mini-instruct는 우선 8비트 또는 4비트 추론을 기준으로 구성한다.
- 긴 Context, 큰 Batch, 동시 다중 요청은 사용하지 않는다.
- 모델 실행 시 최대 입력 길이와 생성 토큰 수를 제한한다.
- `BAAI/bge-m3` 임베딩은 문서를 작은 Batch로 처리하고, 필요하면 CPU Offload를 사용한다.
- Whisper large-v3-turbo는 짧은 음성 전사를 우선 지원하고, 긴 음성은 구간 분할 처리한다.
- 7B 이상 모델의 BF16 추론과 대형 QLoRA 학습은 이 장비의 기본 범위에서 제외한다.

## 권장 초기 기술 스택

| 영역 | 기술 |
|---|---|
| 언어 | Python 3.10 이상 |
| 생성 모델 | `microsoft/Phi-3.5-mini-instruct` |
| 음성 인식 | `openai/whisper-large-v3-turbo` |
| 임베딩 | `BAAI/bge-m3` |
| 모델 실행 | Hugging Face Transformers, Accelerate, BitsAndBytes |
| 벡터 검색 | FAISS 또는 Chroma |
| API | FastAPI |
| 웹 UI | Streamlit 또는 Gradio |
| 형상 관리 | GitHub |

## 음성 기능 추가 계획

음성 기능은 핵심 문서기반 FAQ RAG가 안정화된 뒤 추가한다.

1. 짧은 음성 파일 업로드
2. Whisper로 한국어 음성 전사
3. 전사 결과를 FAQ 질문으로 사용
4. 동일한 문서 검색 및 RAG 답변 수행
5. 답변 음성화는 후속 단계에서 검토

## 버전별 진행 보고서

구현 과정은 `docs/REPORT_vX.Y.Z_*.md` 형식으로 기록합니다.

- [v0.1.0 Phi 기본 추론](REPORT_v0.1.0_phi-inference.md)
- [v0.2.0 대화형 CLI](REPORT_v0.2.0_interactive-cli.md)
- [v0.3.0 문서 로더](REPORT_v0.3.0_document-loader.md)
- [v0.4.0 Chunk 및 BGE-M3 임베딩](REPORT_v0.4.0_chunking-embedding.md)
- [v0.5.0 FAISS 벡터 검색](REPORT_v0.5.0_vector-search.md)
- [v0.6.0 RAG 답변 생성](REPORT_v0.6.0_rag-generation.md)

각 보고서는 목표, 구현 내용, 실행 방법, 확인 항목, 제한사항, 다음 계획을 포함합니다.

## GitHub 기록 원칙

각 단계가 끝날 때 다음 항목을 기록합니다.

- 구현한 기능
- 실행 방법
- 확인한 결과
- 발생한 문제와 해결 방법
- 다음 단계 계획

커밋 메시지는 다음과 같이 단계가 드러나도록 작성합니다.

```text
chore: initialize project
feat: add phi model inference
feat: add document loader
feat: add document chunking
feat: add vector search
feat: add rag answer generation
feat: add chatbot api
feat: add web ui
```

## 현재 진행 상태

- [x] GitHub 원격 저장소 생성
- [x] 로컬 저장소와 GitHub 원격 저장소 연결
- [ ] 개발 환경 확인
- [x] 기본 프로젝트 구조 생성
- [x] Phi-3.5-mini-instruct 모델 실행 코드 작성
- [ ] Phi-3.5-mini-instruct 실제 추론 확인
- [x] 대화형 CLI 인터페이스 구현
- [x] 문서 로더 및 텍스트 추출 코드 작성
- [ ] 문서 수집 및 실제 파일 테스트
- [x] 문서 Chunk 및 임베딩 코드 작성
- [ ] 실제 문서 임베딩 및 인덱스 생성 확인
- [x] 벡터 검색 코드 작성
- [ ] 실제 인덱스 Top-k 검색 확인
- [x] RAG 답변 생성 코드 작성
- [ ] 실제 문서 기반 RAG 답변 확인
- [x] API 및 UI 코드 작성
- [ ] API 및 UI 실제 실행 확인
- [ ] 평가
- [ ] 배포
