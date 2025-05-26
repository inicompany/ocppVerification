import pyodbc
import json
from datetime import datetime, timedelta
import os
import random

class SampleDataLoader:
    def __init__(self):
        self.connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=127.0.0.1,1433;"
            "DATABASE=EVCS_MS;"
            "UID=sa;"
            "PWD=1q2w3e4r!;"
            "TrustServerCertificate=yes;"
        )
    
    def create_table(self):
        """샘플 데이터 테이블 생성"""
        create_table_sql = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'OCPP_MSG_SAMPLE')
        BEGIN
            CREATE TABLE OCPP_MSG_SAMPLE (
                MSG_UUID VARCHAR(50) PRIMARY KEY,
                RECHGST_ID VARCHAR(20) NOT NULL,
                RECHGR_ID VARCHAR(20) NOT NULL,
                MSG_TIME DATETIME NOT NULL,
                MSG_NAME VARCHAR(50) NOT NULL DEFAULT 'ChargePointDataTransfer',
                PAYLOAD NVARCHAR(MAX) NOT NULL,
                CREATED_AT DATETIME DEFAULT GETDATE()
            );

            CREATE INDEX IDX_OCPP_MSG_SAMPLE_TIME ON OCPP_MSG_SAMPLE(MSG_TIME);
            CREATE INDEX IDX_OCPP_MSG_SAMPLE_CHARGER ON OCPP_MSG_SAMPLE(RECHGR_ID);
        END
        """
        
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute(create_table_sql)
                conn.commit()
                print("테이블이 성공적으로 생성되었습니다.")
        except Exception as e:
            print(f"테이블 생성 중 오류 발생: {str(e)}")
    
    def generate_sample_data(self):
        """샘플 데이터 생성"""
        # 정상적인 상태 전이 시퀀스
        normal_states = [
            ("IM", "A"),  # 초기화 -> 사용가능
            ("A", "P"),   # 사용가능 -> 준비중
            ("P", "C"),   # 준비중 -> 충전중
            ("C", "F"),   # 충전중 -> 종료중
            ("F", "A"),   # 종료중 -> 사용가능
        ]
        
        # 이상 상태 전이 시퀀스
        abnormal_states = [
            ("A", "F"),   # 사용가능 -> 오류
            ("C", "U"),   # 충전중 -> 사용불가
            ("P", "DM"),  # 준비중 -> 유지보수
            ("A", "DM"),  # 사용가능 -> 유지보수
            ("C", "DM"),  # 충전중 -> 유지보수
        ]
        
        sample_data = []
        current_time = datetime.now()
        
        # 정상 데이터 생성 (80%)
        for _ in range(80):
            state_sequence = random.choice(normal_states)
            for state in state_sequence:
                current_time += timedelta(minutes=random.randint(1, 5))
                sample_data.append({
                    'msg_uuid': f"uuid_{len(sample_data)}",
                    'rechgst_id': f"station_{random.randint(1, 5)}",
                    'rechgr_id': f"charger_{random.randint(1, 10)}",
                    'msg_time': current_time.isoformat(),
                    'payload': {
                        'data': json.dumps({
                            'connectorId': random.randint(1, 2),
                            'status': state,
                            'errorCode': None
                        })
                    }
                })
        
        # 이상 데이터 생성 (20%)
        for _ in range(20):
            state_sequence = random.choice(abnormal_states)
            for state in state_sequence:
                current_time += timedelta(minutes=random.randint(1, 5))
                sample_data.append({
                    'msg_uuid': f"uuid_{len(sample_data)}",
                    'rechgst_id': f"station_{random.randint(1, 5)}",
                    'rechgr_id': f"charger_{random.randint(1, 10)}",
                    'msg_time': current_time.isoformat(),
                    'payload': {
                        'data': json.dumps({
                            'connectorId': random.randint(1, 2),
                            'status': state,
                            'errorCode': 'InternalError' if state in ['F', 'U'] else None
                        })
                    }
                })
        
        # 시간순 정렬
        sample_data.sort(key=lambda x: x['msg_time'])
        return sample_data
    
    def save_to_db(self, sample_data):
        """샘플 데이터를 DB에 저장"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                # 기존 데이터 삭제
                cursor.execute("DELETE FROM OCPP_MSG_SAMPLE")
                
                # 데이터 삽입
                for data in sample_data:
                    insert_sql = """
                    INSERT INTO OCPP_MSG_SAMPLE (
                        MSG_UUID, RECHGST_ID, RECHGR_ID, MSG_TIME, PAYLOAD
                    ) VALUES (?, ?, ?, ?, ?)
                    """
                    
                    cursor.execute(insert_sql, (
                        data['msg_uuid'],
                        data['rechgst_id'],
                        data['rechgr_id'],
                        datetime.fromisoformat(data['msg_time']),
                        json.dumps(data['payload'])
                    ))
                
                conn.commit()
                print(f"총 {len(sample_data)}개의 샘플 데이터가 DB에 저장되었습니다.")
                
        except Exception as e:
            print(f"데이터 저장 중 오류 발생: {str(e)}")

def main():
    loader = SampleDataLoader()
    
    # 테이블 생성
    loader.create_table()
    
    # 샘플 데이터 생성
    print("샘플 데이터를 생성합니다...")
    sample_data = loader.generate_sample_data()
    
    # DB에 저장
    print("생성된 데이터를 DB에 저장합니다...")
    loader.save_to_db(sample_data)

if __name__ == "__main__":
    main() 