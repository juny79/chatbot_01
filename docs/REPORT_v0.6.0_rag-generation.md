# 진행 보고서 v0.6.0 — 문서 기반 RAG 답변 생성

- 단계: 검색 결과와 Phi 모델 연결
- 상태: 코드 구현 완료 / 실제 문서 기반 테스트 필요

## 1. 목표

FAISS에서 검색한 관련 문서 Chunk를 Phi-3.5-mini-instruct의 Context로 전달하고, 근거 문서 기반 답변과 출처를 반환한다.

## 2. 구현 내용

- 질문 → BGE-M3 임베딩 → FAISS Top-k 검색 연결
- 검색 결과를 Context로 조합
- 문서 밖의 추측을 제한하는 시스템 프롬프트 적용
- 검색 결과가 임계값보다 낮으면 근거 부족 응답
- 답변과 출처 목록을 함께 반환
- RAG 실행 시 BGE-M3를 CPU에서 실행하여 10GB GPU에서 Phi 메모리 확보
- 기본 `top_k=3`, `min_score=0.3`

## 3. 관련 파일

```text
app/rag.py
app/inference.py
app/vector_search.py
scripts/rag_cli.py
```

## 4. 실행 방법

먼저 문서 인덱스를 생성합니다.

```bash
python -m scripts.build_embeddings --batch-size 2
```

RAG 질문을 실행합니다.

```bash
python -m scripts.rag_cli "휴가 신청 절차는 무엇인가요?"
```

검색 개수와 유사도 기준 조정:

```bash
python -m scripts.rag_cli "휴가 신청 절차는 무엇인가요?" --top-k 5 --min-score 0.35
```

## 5. 출력 내용

- 문서 근거를 바탕으로 한 답변
- 참조 문서명
- PDF 페이지
- 검색 유사도 점수

## 6. 확인 항목

- [ ] 인덱스 로딩
- [ ] 검색 결과 Context 전달
- [ ] 문서 근거 기반 답변 생성
- [ ] 답변 출처 출력
- [ ] 무관한 질문의 근거 부족 처리
- [ ] 10GB VRAM 사용량 확인

## 7. 현재 한계

- CLI 단일 질문만 지원한다.
- 대화 이력과 RAG를 결합하지 않았다.
- `min_score`는 데이터셋별 평가가 필요하다.
- 웹 UI와 API는 아직 구현하지 않았다.

## 8. 다음 계획

1. Streamlit 기반 웹 UI
2. 문서 업로드 및 인덱스 재생성
3. 대화 이력과 RAG 연결
4. FastAPI API 제공
