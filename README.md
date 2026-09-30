# 문서기반 FAQ 챗봇

`microsoft/Phi-3.5-mini-instruct`와 `BAAI/bge-m3`를 활용하는 문서기반 FAQ 챗봇 실습 프로젝트입니다. 이후 `openai/whisper-large-v3-turbo`를 이용한 짧은 음성 질문 전사 기능을 추가합니다.

## 현재 환경 기준

- GPU VRAM: 10GB
- 언어 모델: `microsoft/Phi-3.5-mini-instruct`
- 임베딩 모델: `BAAI/bge-m3`
- 음성 인식 모델: `openai/whisper-large-v3-turbo`
- 추론 전략: 작은 Batch, 짧은 Context, 8비트 또는 4비트 로딩

## 진행 상태

- Phi-3.5-mini-instruct 기본 추론 코드 작성
- 다음 단계: 환경 설치 후 단일 질문 추론 실행 및 VRAM 확인

## Phi 기본 추론 실행

가상환경을 활성화하고 패키지를 설치한 뒤 실행합니다.

```bash
source .venv/bin/activate
pip install -r requirements.txt
python scripts/test_phi_model.py
```

질문을 직접 지정할 수도 있습니다.

```bash
python scripts/test_phi_model.py "휴가 신청 절차를 알려주세요."
```

첫 실행에서는 모델 가중치를 Hugging Face에서 다운로드합니다. 10GB VRAM 환경에서는 기본적으로 8비트 로딩과 입력 2,048 토큰, 생성 256 토큰 제한을 사용합니다.

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
