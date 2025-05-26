# 충전 프로세스 기본 검증 모델 문서

## 1. 개요
이 모델은 전기차 충전 프로세스의 정상성을 검증하기 위한 기본 모델입니다. OCPP 프로토콜의 StartTransaction, MeterValues, StopTransaction 메시지를 분석하여 충전 프로세스의 패턴을 학습하고 검증합니다.

## 2. 모델 구조

### 2.1 데이터 수집 (OCPPDataCollector)
- **StartTransaction 수집**
  - 충전 시작 시점 데이터
  - 충전소 ID, 충전기 ID, 트랜잭션 ID 정보 포함
  - 충전 시작 시간 기록

- **MeterValues 수집**
  - 충전 중 측정값 데이터
  - 전력, 누적 전력량, 충전 시간 등 포함
  - 주기적인 측정값 기록

- **StopTransaction 수집**
  - 충전 종료 시점 데이터
  - 최종 충전량, 종료 시간, 종료 사유 등 포함

### 2.2 트랜잭션 세트 구성 (TransactionSetCollector)
- StartTransaction, MeterValues, StopTransaction을 하나의 세트로 구성
- 각 트랜잭션 ID별로 관련 데이터 그룹화
- 시간 순서대로 정렬하여 충전 프로세스 흐름 파악

### 2.3 패턴 학습 (TransactionPatternLearner)
- 정상 충전 프로세스 패턴 학습
- 주요 학습 항목:
  - 충전 시작/종료 시간
  - 충전량 변화 패턴
  - 충전 시간 패턴
  - 전력 사용 패턴

## 3. 데이터베이스 구조

### 3.1 TRANSACTION_PATTERNS 테이블
```sql
CREATE TABLE TRANSACTION_PATTERNS (
    pattern_id INT IDENTITY(1,1) PRIMARY KEY,
    rechgst_id VARCHAR(50),          -- 충전소 ID
    rechgr_id VARCHAR(50),           -- 충전기 ID
    transaction_id INT,              -- 트랜잭션 ID
    start_time DATETIME,             -- 충전 시작 시간
    meter_values_count INT,          -- 측정값 개수
    stop_time DATETIME,              -- 충전 종료 시간
    meter_values_pattern NVARCHAR(MAX), -- 측정값 패턴 (JSON)
    created_at DATETIME              -- 패턴 생성 시간
)
```

## 4. 검증 프로세스

### 4.1 정상 패턴 학습
1. 정상 충전소/충전기 데이터 수집
2. 트랜잭션 세트 구성
3. 패턴 분석 및 저장

### 4.2 이상 탐지
1. 새로운 트랜잭션 데이터 수집
2. 저장된 정상 패턴과 비교
3. 이상 패턴 탐지 및 보고

## 5. 사용 방법

### 5.1 데이터 수집
```python
collector = TransactionSetCollector(es_client)
transaction_sets = collector.collect_transaction_set(
    rechgst_id="000245",
    rechgr_id="01",
    start_date="2025-05-07 00:00:00",
    end_date="2025-05-08 00:00:00"
)
```

### 5.2 패턴 학습
```python
learner = TransactionPatternLearner(db_connection)
for tx_set in transaction_sets:
    pattern = learner.analyze_pattern(tx_set)
    learner.save_pattern(pattern)
```

## 6. 향후 개선 사항
1. 실시간 모니터링 기능 추가
2. 이상 패턴 자동 분류 기능
3. 알림 시스템 연동
4. 성능 최적화
5. 추가 메트릭 분석 기능

## 7. 주의사항
1. 충분한 정상 데이터 수집 필요
2. 정기적인 패턴 업데이트 필요
3. 시스템 리소스 모니터링 필요
4. 데이터 백업 정책 수립 필요 