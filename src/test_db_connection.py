from src.utils.db_connector import DatabaseConnector

def test_connection():
    try:
        db = DatabaseConnector()
        conn = db.get_connection()
        print("데이터베이스 연결 성공!")
        
        # 테스트 쿼리 실행
        cursor = conn.cursor()
        cursor.execute("""
        SELECT TOP 1
            A.MSG_UUID,
            A.RECHGST_ID,
            A.RECHGR_ID,
            JSON_VALUE(A.PAYLOAD_MSG, '$.transactionId') AS TRN_ID,
            JSON_VALUE(A.PAYLOAD_MSG, '$.idTag') AS IDTAG,
            A.PAYLOAD_MSG
        FROM EVCS_OCPP.DBO.OCPP_MSG_TR_ES A WITH(NOLOCK)
        WHERE A.MSG_NAME = 'ChargePointDataTransfer'
            AND JSON_VALUE(A.PAYLOAD_MSG, '$.messageId') = 'statusnoti'
        """)
        row = cursor.fetchone()
        
        if row:
            print("충전기 상태 알림 데이터 조회 성공!")
            print(f"MSG_UUID: {row[0]}")
            print(f"RECHGST_ID: {row[1]}")
            print(f"RECHGR_ID: {row[2]}")
            print(f"TRN_ID: {row[3]}")
            print(f"IDTAG: {row[4]}")
            print(f"PAYLOAD_MSG: {row[5][:100]}...")  # 처음 100자만 출력
        else:
            print("충전기 상태 알림 데이터가 없습니다.")
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_connection() 