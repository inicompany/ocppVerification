-- StartTransaction 데이터 저장 테이블
CREATE TABLE EVCS_MS.DBO.START_TRANSACTION_DATA (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    rechgst_id VARCHAR(50) NOT NULL,          -- 충전소 ID
    rechgr_id VARCHAR(50) NOT NULL,           -- 충전기 ID
    connector_id INT,                         -- 커넥터 ID
    transaction_id INT,                       -- 트랜잭션 ID
    id_tag VARCHAR(50),                       -- 사용자 ID 태그
    meter_start INT,                          -- 시작 시 미터 값
    reservation_id INT,                       -- 예약 ID
    start_timestamp DATETIME2,                -- 시작 시간
    msg_uuid VARCHAR(50),                     -- 메시지 UUID
    server_ip VARCHAR(50),                    -- 서버 IP
    session_status VARCHAR(20),               -- 세션 상태
    created_at DATETIME2 DEFAULT GETDATE(),   -- 데이터 생성 시간
    
    -- 인덱스 생성
    CONSTRAINT idx_start_transaction_rechgst_rechgr 
    NONCLUSTERED (rechgst_id, rechgr_id),
    
    CONSTRAINT idx_start_transaction_timestamp 
    NONCLUSTERED (start_timestamp)
)

-- 테이블 설명 추가
EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'StartTransaction 데이터 저장 테이블', 
    @level0type = N'SCHEMA', @level0name = N'DBO', 
    @level1type = N'TABLE',  @level1name = N'START_TRANSACTION_DATA'

-- 컬럼 설명 추가
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'충전소 ID', @level0type = N'SCHEMA', @level0name = N'DBO', @level1type = N'TABLE', @level1name = N'START_TRANSACTION_DATA', @level2type = N'COLUMN', @level2name = N'rechgst_id'
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'충전기 ID', @level0type = N'SCHEMA', @level0name = N'DBO', @level1type = N'TABLE', @level1name = N'START_TRANSACTION_DATA', @level2type = N'COLUMN', @level2name = N'rechgr_id'
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'커넥터 ID', @level0type = N'SCHEMA', @level0name = N'DBO', @level1type = N'TABLE', @level1name = N'START_TRANSACTION_DATA', @level2type = N'COLUMN', @level2name = N'connector_id'
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'트랜잭션 ID', @level0type = N'SCHEMA', @level0name = N'DBO', @level1type = N'TABLE', @level1name = N'START_TRANSACTION_DATA', @level2type = N'COLUMN', @level2name = N'transaction_id'
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'사용자 ID 태그', @level0type = N'SCHEMA', @level0name = N'DBO', @level1type = N'TABLE', @level1name = N'START_TRANSACTION_DATA', @level2type = N'COLUMN', @level2name = N'id_tag'
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'시작 시 미터 값', @level0type = N'SCHEMA', @level0name = N'DBO', @level1type = N'TABLE', @level1name = N'START_TRANSACTION_DATA', @level2type = N'COLUMN', @level2name = N'meter_start'
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'예약 ID', @level0type = N'SCHEMA', @level0name = N'DBO', @level1type = N'TABLE', @level1name = N'START_TRANSACTION_DATA', @level2type = N'COLUMN', @level2name = N'reservation_id'
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'시작 시간', @level0type = N'SCHEMA', @level0name = N'DBO', @level1type = N'TABLE', @level1name = N'START_TRANSACTION_DATA', @level2type = N'COLUMN', @level2name = N'start_timestamp'
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'메시지 UUID', @level0type = N'SCHEMA', @level0name = N'DBO', @level1type = N'TABLE', @level1name = N'START_TRANSACTION_DATA', @level2type = N'COLUMN', @level2name = N'msg_uuid'
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'서버 IP', @level0type = N'SCHEMA', @level0name = N'DBO', @level1type = N'TABLE', @level1name = N'START_TRANSACTION_DATA', @level2type = N'COLUMN', @level2name = N'server_ip'
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'세션 상태', @level0type = N'SCHEMA', @level0name = N'DBO', @level1type = N'TABLE', @level1name = N'START_TRANSACTION_DATA', @level2type = N'COLUMN', @level2name = N'session_status'
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'데이터 생성 시간', @level0type = N'SCHEMA', @level0name = N'DBO', @level1type = N'TABLE', @level1name = N'START_TRANSACTION_DATA', @level2type = N'COLUMN', @level2name = N'created_at' 