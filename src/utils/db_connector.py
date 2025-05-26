import pyodbc
import json
from typing import List, Dict, Any
import logging

class DatabaseConnector:
    def __init__(self):
        self.connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=127.0.0.1,1433;"
            "DATABASE=EVCS_MS;"
            "UID=sa;"
            "PWD=1q2w3e4r!;"
            "TrustServerCertificate=yes;"
        )
    
    def get_connection(self):
        return pyodbc.connect(self.connection_string)
    
    def get_charger_status_data(self, start_time=None, end_time=None):
        """
        충전기 상태 알림 데이터 조회
        
        Args:
            start_time: 시작 시간 (datetime 객체)
            end_time: 종료 시간 (datetime 객체)
            
        Returns:
            list: 충전기 상태 알림 데이터 리스트
        """
        try:
            query = """
            SELECT 
                MSG_UUID,
                RECHGST_ID,
                RECHGR_ID,
                MSG_TIME,
                JSON_VALUE(PAYLOAD, '$.data') as data
            FROM OCPP_MSG
            WHERE MSG_NAME = 'ChargePointDataTransfer'
            AND JSON_VALUE(PAYLOAD, '$.messageId') = 'statusnoti'
            """
            
            params = []
            if start_time and end_time:
                query += " AND MSG_TIME BETWEEN ? AND ?"
                params.extend([start_time, end_time])
            
            query += " ORDER BY MSG_TIME DESC"
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [{
                    'msg_uuid': row[0],
                    'rechgst_id': row[1],
                    'rechgr_id': row[2],
                    'msg_time': row[3],
                    'payload': {
                        'data': row[4]
                    }
                } for row in rows]
            
        except Exception as e:
            print(f"데이터 조회 중 오류 발생: {str(e)}")
            return [] 

    def insert_charger_status(self, data: dict):
        """
        충전기 상태 데이터를 데이터베이스에 삽입
        
        Args:
            data: 삽입할 데이터 딕셔너리
        """
        try:
            cursor = self.conn.cursor()
            
            # SQL 쿼리 작성
            query = """
            INSERT INTO OCPP_MSG (
                MSG_UUID,
                MSG_TIME,
                MSG_NAME,
                PAYLOAD
            ) VALUES (?, ?, ?, ?)
            """
            
            # 데이터 준비
            values = (
                data['msg_uuid'],
                data['msg_time'],
                data['msg_name'],
                json.dumps(data['payload'])
            )
            
            # 쿼리 실행
            cursor.execute(query, values)
            self.conn.commit()
            
        except Exception as e:
            logging.error(f"데이터 삽입 중 오류 발생: {str(e)}")
            raise 