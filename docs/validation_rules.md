# OCPP 메시지 검증 규칙

## 1. 하이브리드 검증 시스템

### 1.1 규칙 기반 검증
기본적인 메시지 구조와 비즈니스 로직을 검증합니다.

### 1.2 AI 기반 검증
LSTM-Autoencoder와 SHAP를 활용한 패턴 기반 검증을 수행합니다.

## 2. 메시지 구조 검증

### 2.1 필수 필드 검증
각 메시지 타입별 필수 필드 존재 여부를 검증합니다.

#### StartTransaction
- connectorId: 충전기 커넥터 ID
- idTag: 사용자 인증 태그
- meterStart: 시작 시 미터 값
- timestamp: 시작 시간

#### MeterValue
- connectorId: 충전기 커넥터 ID
- transactionId: 트랜잭션 ID
- meterValue: 현재 미터 값
- timestamp: 측정 시간

#### StopTransaction
- transactionId: 트랜잭션 ID
- meterStop: 종료 시 미터 값
- timestamp: 종료 시간
- reason: 종료 사유

#### Payment
- transactionId: 트랜잭션 ID
- amount: 결제 금액
- currency: 통화 코드
- timestamp: 결제 시간

### 2.2 필드 타입 및 범위 검증
각 필드의 데이터 타입과 허용 범위를 검증합니다.

| 필드명 | 타입 | 최대값/길이 | 검증 내용 |
|--------|------|------------|-----------|
| connectorId | int | 100 | 0~100 사이의 정수 |
| idTag | str | 20 | 20자 이하 문자열 |
| meterStart | int | 1,000,000 | 0 이상의 정수 |
| meterStop | int | 1,000,000 | meterStart보다 큰 정수 |
| meterValue | int | 1,000,000 | meterStart보다 큰 정수 |
| transactionId | int | 1,000,000 | 양의 정수 |
| amount | float | 1,000,000.0 | 0보다 큰 실수 |
| currency | str | 3 | 3자리 통화 코드 |
| timestamp | str | - | ISO 8601 형식 |
| reason | str | 50 | 50자 이하 문자열 |

## 3. AI 기반 패턴 검증

### 3.1 LSTM-Autoencoder 모델
- **입력 특성**:
  - 메시지 타입 (원-핫 인코딩)
  - 시간 간격
  - 미터 값 변화율
  - 금액 정보
  - 기타 메타데이터

- **모델 구조**:
  - 인코더: 입력 시퀀스를 잠재 공간으로 압축
  - 디코더: 잠재 공간에서 원본 시퀀스로 복원
  - LSTM 레이어: 시계열 패턴 학습

- **학습 방식**:
  - 비지도 학습: 정상 패턴만으로 학습
  - 재구성 오차 기반 이상 탐지
  - 적응형 임계값 설정

### 3.2 SHAP 기반 설명 가능성
- **특성 중요도 분석**:
  - 각 특성이 이상 판단에 미친 영향력 계산
  - 긍정적/부정적 기여도 수치화

- **설명 제공**:
  - 이상 판단의 주요 원인 식별
  - 각 특성의 기여도 시각화
  - 구체적인 개선 방향 제시

### 3.3 이상 탐지 기준
- **재구성 오차**:
  - 기본 임계값: 0.1
  - 동적 임계값: 이동 평균 기반 조정

- **특성 기여도**:
  - 주요 특성의 기여도가 0.3 이상
  - 다중 특성의 복합적 영향 고려

## 4. 검증 결과

### 4.1 규칙 기반 결과
- is_valid: 기본 검증 통과 여부
- errors: 검증 실패 시 오류 메시지

### 4.2 AI 기반 결과
- anomaly_score: 이상 점수 (0~1)
- reconstruction_error: 재구성 오차
- feature_importance: 특성별 기여도
- explanation: 이상 원인 설명

### 4.3 통합 결과
- final_decision: 최종 판단
- confidence: 신뢰도 점수
- detailed_explanation: 상세 설명

## 5. 예외 처리

### 5.1 규칙 기반 예외
- 메시지 타입 오류
- 필수 필드 누락
- 잘못된 필드 타입
- 시퀀스 오류
- 비즈니스 규칙 위반

### 5.2 AI 기반 예외
- 패턴 이상
- 비정상적인 특성 조합
- 학습되지 않은 패턴
- 모델 신뢰도 부족

### 5.3 통합 예외 처리
- 규칙과 AI 결과의 충돌 해결
- 우선순위 기반 판단
- 불확실한 경우의 처리 