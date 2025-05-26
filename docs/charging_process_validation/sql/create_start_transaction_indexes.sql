-- StartTransaction 테이블 인덱스 생성
USE EVCS_MS
GO

-- 충전소/충전기 복합 인덱스
CREATE NONCLUSTERED INDEX idx_start_transaction_rechgst_rechgr 
ON DBO.START_TRANSACTION_DATA (rechgst_id, rechgr_id)
GO

-- 시작 시간 인덱스
CREATE NONCLUSTERED INDEX idx_start_transaction_timestamp 
ON DBO.START_TRANSACTION_DATA (start_timestamp)
GO

-- 트랜잭션 ID 인덱스 (트랜잭션 조회용)
CREATE NONCLUSTERED INDEX idx_start_transaction_transaction_id 
ON DBO.START_TRANSACTION_DATA (transaction_id)
GO

-- 메시지 UUID 인덱스 (메시지 추적용)
CREATE NONCLUSTERED INDEX idx_start_transaction_msg_uuid 
ON DBO.START_TRANSACTION_DATA (msg_uuid)
GO 