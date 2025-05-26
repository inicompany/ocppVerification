# OCPP 이상 탐지 시스템

이 프로젝트는 OCPP(Open Charge Point Protocol) 메시지를 실시간으로 모니터링하고 이상을 탐지하는 시스템입니다.

## 주요 기능

### 1. 자동 데이터 수집 및 학습
- OCPP 메시지를 자동으로 수집하고 학습
- Open Charge Alliance, GitHub 등에서 OCPP 메시지 패턴 수집
- 수집된 데이터를 자동으로 학습에 반영

### 2. 실시간 이상 탐지
- 충전기 상태 변화를 실시간으로 모니터링
- 이상 패턴 자동 감지 및 알림
- 학습된 모델을 통한 정확한 이상 탐지

### 3. 지속적 학습 시스템
- 새로운 데이터를 자동으로 학습에 반영
- 모델 성능 자동 개선
- 실시간 데이터 처리 및 분석

## 시스템 구성

- `src/utils/ocpp_data_collector.py`: OCPP 메시지 자동 수집기
- `src/utils/db_connector.py`: 데이터베이스 연결 및 관리
- `src/utils/data_processor.py`: 데이터 전처리 및 정규화
- `src/models/detector.py`: 이상 탐지 모델
- `src/online_learning_system.py`: 온라인 학습 시스템

## 설치 및 실행

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 데이터베이스 설정:
- MSSQL 서버 설정
- 데이터베이스 연결 정보 설정

3. 시스템 실행:
```bash
# 데이터 수집기 실행
python -m src.utils.ocpp_data_collector

# 온라인 학습 시스템 실행
python -m src.online_learning_system
```

## 로그 확인

- 데이터 수집 로그: `logs/ocpp_collector.log`
- 학습 시스템 로그: `logs/online_learning.log`
- 이상 탐지 로그: `logs/anomaly_detection.log` 