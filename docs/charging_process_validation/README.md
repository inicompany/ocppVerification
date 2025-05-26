# 충전 프로세스 검증 모델

## 1. 모델 개요
이 모델은 OCPP 프로토콜의 트랜잭션 데이터를 분석하여 충전 프로세스의 정상성을 검증하는 모델입니다.

## 2. 검증 대상
- StartTransaction
- MeterValues
- StopTransaction

## 3. 데이터 수집 방법
### 3.1 StartTransaction
- 충전소 ID (rechgstId)
- 충전기 ID (rechgrId)
- 트랜잭션 ID
- 시작 시간

### 3.2 MeterValues
- 전력 (power)
- 누적 전력량 (accWh)
- 충전 시간 (rechgHr)
- 측정 시간 (timestamp)

### 3.3 StopTransaction
- 종료 시간
- 종료 사유
- 최종 충전량

## 4. 검증 프로세스
1. 정상 충전소/충전기 데이터 수집
2. 트랜잭션 세트 구성
   - StartTransaction으로 시작
   - MeterValues로 중간 데이터
   - StopTransaction으로 종료
3. 패턴 분석
   - 충전 시간 패턴
   - 전력 사용 패턴
   - 충전량 변화 패턴

## 5. 데이터베이스 구조
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

## 6. 검증 기준
1. 충전 시간 검증
   - 정상 충전 시간 범위
   - 비정상적으로 긴/짧은 충전 시간

2. 전력 사용 패턴 검증
   - 정상 전력 사용 범위
   - 급격한 전력 변화

3. 충전량 변화 검증
   - 정상 충전량 증가 패턴
   - 비정상적인 충전량 변화

## 7. 구현 계획
1. 데이터 수집 모듈
   - OCPPDataCollector
   - TransactionSetCollector

2. 패턴 학습 모듈
   - TransactionPatternLearner
   - PatternAnalyzer

3. 검증 모듈
   - TransactionValidator
   - AnomalyDetector

## 8. 향후 개선 사항
1. 실시간 모니터링 기능
2. 이상 패턴 자동 분류
3. 알림 시스템 연동
4. 성능 최적화
5. 추가 메트릭 분석 