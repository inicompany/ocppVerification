# OCPP 메시지 검증 시스템

OCPP(Open Charge Point Protocol) 메시지의 이상 탐지 및 검증을 위한 하이브리드 시스템입니다.

## 프로젝트 구조

```
/
├── src/                    # 소스 코드
│   ├── models/            # 모델 코드
│   │   ├── __init__.py
│   │   ├── encoder.py     # OCPP 메시지 인코더
│   │   ├── autoencoder.py # LSTM-Autoencoder 모델
│   │   └── detector.py    # 이상 탐지 시스템
│   ├── utils/             # 유틸리티 함수
│   │   ├── __init__.py
│   │   └── data_processor.py
│   ├── config/            # 설정 파일
│   │   ├── __init__.py
│   │   └── model_config.py
│   └── tests/             # 테스트 코드
│       ├── __init__.py
│       └── test_detector.py
├── saved_models/          # 학습된 모델 저장
├── docs/                  # 문서
│   └── validation_rules.md
└── README.md
```

## 주요 기능

1. **하이브리드 검증 시스템**
   - 규칙 기반 검증
   - AI 기반 패턴 검증 (LSTM-Autoencoder)
   - SHAP 기반 설명 가능성

2. **메시지 구조 검증**
   - 필수 필드 검증
   - 필드 타입 및 범위 검증
   - 시퀀스 검증

3. **AI 기반 패턴 검증**
   - LSTM-Autoencoder를 통한 시계열 패턴 학습
   - 재구성 오차 기반 이상 탐지
   - SHAP를 통한 이상 원인 분석

## 설치 방법

1. Python 3.8 이상 설치
2. 필요한 패키지 설치:
   ```bash
   pip install torch numpy shap
   ```

## 사용 방법

1. 모델 학습:
   ```python
   from src.models.detector import OCPPAnomalyDetectionSystem
   
   detector = OCPPAnomalyDetectionSystem()
   detector.train(normal_sequences)
   ```

2. 이상 탐지:
   ```python
   result = detector.detect_anomaly(sequence)
   if result['is_anomaly']:
       print(f"이상 탐지: {result['explanation']}")
   ```

## 검증 규칙

자세한 검증 규칙은 [validation_rules.md](docs/validation_rules.md) 문서를 참조하세요.

## 라이선스

MIT License 