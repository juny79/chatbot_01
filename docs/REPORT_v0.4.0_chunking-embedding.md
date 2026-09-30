# 진행 보고서 v0.4.0 — 문서 Chunk 및 BGE-M3 임베딩

- 단계: 문서 분할 및 임베딩
- 상태: 코드 구현 완료 / 실제 문서와 모델로 테스트 필요

## 1. 목표

문서 로더의 결과를 검색 가능한 Chunk로 분할하고, `BAAI/bge-m3` 임베딩을 생성하여 FAISS 인덱스로 저장한다.

## 2. 구현 내용

- 문자 기반 Chunk 분할
- 기본 Chunk 크기 800자
- 기본 overlap 120자
- Chunk별 원본 파일명 및 PDF 페이지 메타데이터 유지
- BGE-M3 SentenceTransformer 로딩
- 작은 Batch 기본값 4
- 정규화 임베딩 생성
- FAISS Inner Product 인덱스 생성
- `vectorstore/index.faiss`와 `metadata.json` 저장

## 3. 관련 파일

```text
app/chunking.py
app/embedding.py
scripts/build_embeddings.py
```

## 4. 실행 방법

먼저 문서를 `data/raw/`에 넣고 패키지를 설치합니다.

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

임베딩 인덱스를 생성합니다.

```bash
python -m scripts.build_embeddings
```

10GB VRAM 환경에서 Batch를 더 줄이려면:

```bash
python -m scripts.build_embeddings --batch-size 2
```

생성 결과:

```text
vectorstore/index.faiss
vectorstore/metadata.json
```

## 5. VRAM 운영 기준

- 기본 Batch는 4로 설정한다.
- VRAM 부족 시 `--batch-size 2` 또는 `--batch-size 1`을 사용한다.
- 대량 문서는 여러 번 나누어 처리한다.
- 벡터 저장소는 Git에 커밋하지 않는다.

## 6. 확인 항목

- [ ] BGE-M3 다운로드 성공
- [ ] 문서 Chunk 수 확인
- [ ] 임베딩 생성 성공
- [ ] FAISS 인덱스 저장 확인
- [ ] metadata.json의 출처 확인
- [ ] GPU 메모리 사용량 확인

## 7. 현재 한계

- Chunk 분할은 문자 기반이며 문장 단위 최적화는 아직 적용하지 않았다.
- 검색 질의와 Top-k 검색 API는 다음 단계에서 구현한다.
- 표, 이미지, OCR 결과의 의미 구조는 별도 개선이 필요하다.

## 8. 다음 계획

1. FAISS Top-k 검색 구현
2. 검색 유사도와 출처 출력
3. 질문 임베딩 생성
4. 검색 결과를 Phi 프롬프트에 연결
