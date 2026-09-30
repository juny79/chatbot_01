# 문서기반 FAQ 챗봇

`microsoft/Phi-3.5-mini-instruct`와 `BAAI/bge-m3`를 활용하는 문서기반 FAQ 챗봇 실습 프로젝트입니다. 이후 `openai/whisper-large-v3-turbo`를 이용한 짧은 음성 질문 전사 기능을 추가합니다.

## 현재 환경 기준

- GPU VRAM: 10GB
- 언어 모델: `microsoft/Phi-3.5-mini-instruct`
- 임베딩 모델: `BAAI/bge-m3`
- 음성 인식 모델: `openai/whisper-large-v3-turbo`
- 추론 전략: 작은 Batch, 짧은 Context, 8비트 또는 4비트 로딩

## 진행 상태

- 프로젝트 기본 구조 및 모델 설정 준비
- 다음 단계: Phi-3.5-mini-instruct 단일 질문 추론 테스트

상세한 계획은 [docs/ROADMAP.md](docs/ROADMAP.md)를 참고하세요.

## 로컬 실행

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python -m app.main
```

## 주의사항

- 모델 가중치, 원본 문서, 벡터 저장소는 Git에 커밋하지 않습니다.
- 10GB VRAM 환경에서는 긴 Context와 큰 Batch를 피합니다.
- `bitsandbytes`는 NVIDIA CUDA 환경을 기준으로 합니다.
- `BAAI/bge-m3`와 Whisper 모델은 필요한 시점에 다운로드합니다.
