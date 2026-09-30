# 진행 보고서 v0.5.0 — FAISS Top-k 벡터 검색

- 단계: 벡터 저장소 및 검색
- 상태: 코드 구현 완료 / 실제 인덱스 검색 테스트 필요

## 1. 목표

사용자 질문을 BGE-M3 임베딩으로 변환하고, 저장된 FAISS 인덱스에서 유사한 문서 Chunk를 Top-k로 검색한다.

## 2. 구현 내용

- FAISS 인덱스 및 metadata.json 로딩
- 질문 임베딩 생성
- Inner Product 기반 유사도 검색
- Top-k 결과 반환
- 최소 유사도 점수 필터 지원
- 문서명, 파일 형식, PDF 페이지, Chunk ID, 유사도 보존
- 인덱스와 metadata 개수 불일치 검증

## 3. 관련 파일

```text
app/vector_search.py
scripts/search_cli.py
```

## 4. 실행 방법

먼저 문서를 넣고 인덱스를 생성합니다.

```bash
python -m scripts.build_embeddings --batch-size 2
```

검색을 실행합니다.

```bash
python -m scripts.search_cli "휴가 신청 방법은 무엇인가요?"
```

Top-k와 최소 점수를 지정할 수 있습니다.

```bash
python -m scripts.search_cli "휴가 신청 방법은 무엇인가요?" --top-k 5 --min-score 0.3
```

## 5. 출력 예시

```text
[1] score=0.8123, source=faq.md
휴가 신청은 사내 인사 시스템에서 진행합니다...
```

## 6. 확인 항목

- [ ] 인덱스 파일 로딩
- [ ] 질문 임베딩 생성
- [ ] Top-k 검색 결과 확인
- [ ] 유사도 점수 확인
- [ ] 문서명 및 페이지 출처 확인
- [ ] 관련 문서가 없을 때 빈 결과 확인

## 7. 현재 한계

- 검색 결과를 Phi 모델 프롬프트에 아직 연결하지 않았다.
- 검색 점수 임계값은 데이터셋에 맞춘 평가가 필요하다.
- 단순 유사도 검색만 사용하며 재순위화는 적용하지 않았다.

## 8. 다음 계획

1. 검색 결과를 Context로 조합
2. Phi 모델에 Context 기반 프롬프트 전달
3. 근거 부족 시 모른다고 답하는 정책 적용
4. 답변과 출처를 함께 반환
