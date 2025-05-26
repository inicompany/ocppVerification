import pyodbc
import elasticsearch
from elasticsearch import Elasticsearch
import json
from datetime import datetime, timedelta
import logging
import configparser
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StartTransactionCollector:
    def __init__(self):
        # 설정 파일 읽기
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
        
        # DB 설정 읽기
        db_config = configparser.ConfigParser()
        db_config.read(os.path.join(config_path, 'db.properties'), encoding='utf-8')
        print("DB CONFIG:", dict(db_config['DEFAULT']))  # 실제 읽은 값 출력
        
        # collection 설정 읽기
        collection_config = configparser.ConfigParser()
        collection_config.read(os.path.join(config_path, 'collection.properties'), encoding='utf-8')
        
        # DB 연결 문자열 생성
        conn_str = (
            f'DRIVER={{{db_config.get("DEFAULT", "driver")}}};'
            f'SERVER={db_config.get("DEFAULT", "server")};'
            f'DATABASE={db_config.get("DEFAULT", "database")};'
            f'UID={db_config.get("DEFAULT", "username")};'
            f'PWD={db_config.get("DEFAULT", "password")};'
            f'TrustServerCertificate={db_config.get("DEFAULT", "trust_server_certificate")};'
            f'ApplicationIntent={db_config.get("DEFAULT", "application_intent")};'
            f'AutoReconnect={db_config.get("DEFAULT", "auto_reconnect")}'
        )
        
        # DB 연결 설정
        self.db_conn = pyodbc.connect(conn_str)
        
        # Elasticsearch 연결 설정
        self.es = Elasticsearch(['http://10.162.1.16:52900'])
        
        # 날짜 설정
        self.start_date = collection_config.get('DEFAULT', 'start_date', fallback=None)
        self.end_date = collection_config.get('DEFAULT', 'end_date', fallback=None)
        if not self.start_date or not self.end_date:
            raise ValueError('start_date, end_date 값을 collection.properties에 설정하세요.')
        
    def get_target_chargers(self):
        """대상 충전소/충전기 목록 조회"""
        query = """
        SELECT RECHGST_ID, RECHGR_ID 
        FROM EVCS_MS.DBO.COMM_RECHGR
        """
        
        with self.db_conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    
    def create_es_query(self, start_time, end_time, rechgst_id, rechgr_id):
        """Elasticsearch 쿼리 생성"""
        return {
            "size": 200,
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "msgDateTime": {
                                    "gte": start_time,
                                    "lte": end_time
                                }
                            }
                        },
                        {
                            "term": {
                                "rechgstId": rechgst_id
                            }
                        },
                        {
                            "term": {
                                "rechgrId": rechgr_id
                            }
                        },
                        {
                            "match": {
                                "msgName": "StartTransaction"
                            }
                        }
                    ]
                }
            }
        }
    
    def insert_to_db(self, data):
        """데이터를 DB에 저장"""
        insert_query = """
        INSERT INTO EVCS_MS.DBO.START_TRANSACTION_DATA (
            rechgst_id, rechgr_id, connector_id, transaction_id,
            id_tag, meter_start, reservation_id, start_timestamp,
            msg_uuid, server_ip, session_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        with self.db_conn.cursor() as cursor:
            cursor.execute(insert_query, (
                data['rechgstId'],
                data['rechgrId'],
                data.get('connectorId'),
                data.get('transactionId'),
                data.get('idTag'),
                data.get('meterStart'),
                data.get('reservationId'),
                data['msgDateTime'],
                data['msgUuid'],
                data['serverIp'],
                data['sessionStatus']
            ))
        self.db_conn.commit()
    
    def collect_data(self):
        """데이터 수집 실행"""
        try:
            # 대상 충전기 목록 조회
            chargers = self.get_target_chargers()
            logger.info(f"총 {len(chargers)}개의 충전기 대상")
            
            for rechgst_id, rechgr_id in chargers:
                logger.info(f"충전소 {rechgst_id}, 충전기 {rechgr_id} 데이터 수집 시작")
                
                # ES 쿼리 실행
                query = self.create_es_query(
                    self.start_date,
                    self.end_date,
                    rechgst_id,
                    rechgr_id
                )
                
                response = self.es.search(
                    index="ocpp_msg_tr_202505",
                    body=query
                )
                
                # 결과 처리
                hits = response['hits']['hits']
                logger.info(f"검색 결과: {len(hits)}건")
                
                for hit in hits:
                    source = hit['_source']
                    self.insert_to_db(source)
                
                logger.info(f"충전소 {rechgst_id}, 충전기 {rechgr_id} 데이터 수집 완료")
                
        except Exception as e:
            logger.error(f"데이터 수집 중 오류 발생: {str(e)}")
            raise
        finally:
            self.db_conn.close()

def main():
    collector = StartTransactionCollector()
    collector.collect_data()

if __name__ == "__main__":
    main() 