import requests
from bs4 import BeautifulSoup
import json
import logging
import re
from datetime import datetime
import time
import os
from src.utils.db_connector import DatabaseConnector
from src.utils.data_processor import ChargerStatusProcessor

class OCPPDataCollector:
    def __init__(self):
        """OCPP 데이터 수집기 초기화"""
        self.db_connector = DatabaseConnector()
        self.processor = ChargerStatusProcessor()
        self.sources = [
            "https://www.openchargealliance.org/downloads",
            "https://github.com/ChargeTimeEU/OCPP-S",
            "https://github.com/ChargeTimeEU/OCPP-J"
        ]
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/ocpp_collector.log'),
                logging.StreamHandler()
            ]
        )
    
    def search_ocpp_messages(self):
        """OCPP 메시지 검색 및 수집"""
        collected_data = []
        
        for source in self.sources:
            try:
                # 웹 페이지 요청
                response = requests.get(source)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # OCPP 메시지 패턴 검색
                ocpp_patterns = [
                    r'StatusNotification',
                    r'ChargePointDataTransfer',
                    r'Heartbeat',
                    r'Authorize',
                    r'StartTransaction',
                    r'StopTransaction'
                ]
                
                # 텍스트에서 OCPP 메시지 추출
                text = soup.get_text()
                for pattern in ocpp_patterns:
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        # 메시지 주변 컨텍스트 추출
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end]
                        
                        # JSON 형식의 데이터 추출
                        json_matches = re.finditer(r'\{[^{}]*\}', context)
                        for json_match in json_matches:
                            try:
                                data = json.loads(json_match.group())
                                if self._is_valid_ocpp_message(data):
                                    collected_data.append(self._format_message(data))
                            except json.JSONDecodeError:
                                continue
                
                logging.info(f"{source}에서 OCPP 메시지 검색 완료")
                
            except Exception as e:
                logging.error(f"{source} 검색 중 오류 발생: {str(e)}")
        
        return collected_data
    
    def _is_valid_ocpp_message(self, data: dict) -> bool:
        """OCPP 메시지 유효성 검사"""
        required_fields = ['messageTypeId', 'messageId', 'data']
        return all(field in data for field in required_fields)
    
    def _format_message(self, data: dict) -> dict:
        """메시지 형식 변환"""
        return {
            'msg_uuid': f"COLLECTED_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'msg_time': datetime.now().isoformat(),
            'msg_name': 'ChargePointDataTransfer',
            'payload': {
                'messageTypeId': data.get('messageTypeId'),
                'messageId': data.get('messageId'),
                'data': json.dumps(data.get('data', {}))
            }
        }
    
    def save_to_database(self, data: list):
        """수집된 데이터를 데이터베이스에 저장"""
        if not data:
            return
        
        try:
            # 데이터베이스에 저장
            for item in data:
                self.db_connector.insert_charger_status(item)
            
            logging.info(f"{len(data)}개의 OCPP 메시지를 데이터베이스에 저장했습니다.")
            
        except Exception as e:
            logging.error(f"데이터베이스 저장 중 오류 발생: {str(e)}")
    
    def run(self, interval: int = 3600):  # 1시간마다 실행
        """데이터 수집 및 저장 실행"""
        logging.info("OCPP 데이터 수집을 시작합니다.")
        
        while True:
            try:
                # OCPP 메시지 수집
                collected_data = self.search_ocpp_messages()
                
                if collected_data:
                    # 데이터베이스에 저장
                    self.save_to_database(collected_data)
                
                # 대기
                time.sleep(interval)
                
            except Exception as e:
                logging.error(f"데이터 수집 중 오류 발생: {str(e)}")
                time.sleep(interval)

def main():
    # 로그 디렉토리 생성
    os.makedirs('logs', exist_ok=True)
    
    # 데이터 수집기 시작
    collector = OCPPDataCollector()
    collector.run()

if __name__ == "__main__":
    main() 