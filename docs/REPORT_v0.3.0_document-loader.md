# 진행 보고서 v0.3.0 — 문서 로더 및 텍스트 추출

- 단계: 문서 수집 및 전처리 1차
- 상태: 코드 구현 완료 / 샘플 문서 테스트 필요

## 1. 목표

PDF, DOCX, Markdown, TXT, HTML 문서를 읽고 이후 Chunk 및 임베딩 단계에서 사용할 수 있는 텍스트 레코드로 변환한다.

## 2. 구현 내용

- `LoadedDocument` 데이터 구조 추가
- TXT, Markdown 파일 UTF-8 추출
- PDF 페이지별 텍스트 추출
- DOCX 문단별 텍스트 추출
- HTML에서 script/style 요소를 제외한 본문 추출
- 파일명, 확장자, PDF 페이지 번호 메타데이터 보존
- `data/raw` 하위 문서 재귀 검색
- 지원하지 않는 파일 형식 오류 처리

## 3. 관련 파일

```text
app/document_loader.py
scripts/test_document_loader.py
requirements.txt
```

## 4. 추가 패키지

```text
pypdf
python-docx
beautifulsoup4
```

## 5. 실행 방법

먼저 테스트할 문서를 `data/raw/`에 넣습니다. 원본 문서는 개인정보와 보안등급을 확인한 뒤 사용해야 하며 Git에는 저장하지 않습니다.

```bash
source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.test_document_loader
```

다른 디렉터리를 지정하는 방법:

```bash
python -m scripts.test_document_loader ./sample_documents
```

## 6. 확인 항목

- [ ] TXT 로딩
- [ ] Markdown 로딩
- [ ] PDF 페이지별 로딩
- [ ] DOCX 로딩
- [ ] HTML 본문 로딩
- [ ] 출처 및 페이지 메타데이터 확인
- [ ] 빈 문서 처리 확인

## 7. 현재 한계

- 표와 이미지 속 텍스트는 별도 OCR 처리가 필요하다.
- PDF 스캔본은 텍스트 추출이 되지 않을 수 있다.
- 문서 Chunk 분할은 아직 적용하지 않았다.
- 원본 문서의 접근 권한 및 개인정보 필터링은 수동 확인이 필요하다.

## 8. 다음 계획

1. 문서 Chunk 분할
2. Chunk overlap 및 길이 설정
3. BGE-M3 임베딩 생성
4. FAISS 벡터 인덱스 저장
