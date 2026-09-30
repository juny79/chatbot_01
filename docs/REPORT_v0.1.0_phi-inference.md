# 진행 보고서 v0.1.0 — Phi 기본 추론

- 작성일: 2025-02-14
- 단계: 1단계 모델 실행
- 상태: 코드 구현 완료 / 실환경 추론 확인 필요

## 1. 목표

`microsoft/Phi-3.5-mini-instruct`를 로딩하고 단일 한국어 질문에 답변하는 기본 추론 기능을 구현한다.

## 2. 구현 내용

- Hugging Face Transformers 기반 tokenizer와 causal language model 로딩
- `DEVICE=auto` 설정을 통한 CUDA/CPU 자동 선택
- 10GB VRAM 환경을 고려한 8비트 로딩 지원
- 입력 토큰 수 2,048개 제한
- 생성 토큰 수 256개 제한
- 한국어 FAQ 도우미 시스템 프롬프트 적용
- 단일 질문 실행 스크립트 추가

## 3. 관련 파일

```text
app/model_loader.py
app/inference.py
scripts/test_phi_model.py
```

## 4. 실행 방법

```bash
source .venv/bin/activate
python -m scripts.test_phi_model
```

질문을 직접 지정하는 방법:

```bash
python -m scripts.test_phi_model "문서기반 FAQ 챗봇이란 무엇인가요?"
```

## 5. 환경 기준

- 언어 모델: `microsoft/Phi-3.5-mini-instruct`
- GPU VRAM: 10GB
- 기본 로딩: CUDA 환경에서 8비트
- CPU 환경: float32 fallback

## 6. 확인 항목

- [ ] Python 가상환경 활성화
- [ ] PyTorch CUDA 사용 가능 여부 확인
- [ ] Hugging Face 모델 다운로드 성공
- [ ] 단일 질문 응답 생성 성공
- [ ] VRAM 사용량 확인

## 7. 제한사항

이 버전은 문서 검색을 사용하지 않는다. 따라서 모델 자체의 일반 지식에 기반한 답변만 생성하며, 문서 출처를 제공하지 않는다.

## 8. 다음 계획

- 대화 이력을 유지하는 CLI 구현
- 문서 수집 및 텍스트 추출
- 문서 Chunk 분할
