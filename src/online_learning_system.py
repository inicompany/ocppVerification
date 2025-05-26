import torch
import torch.nn as nn
import torch.optim as optim
from src.models.detector import OCPPAnomalyDetectionSystem
from src.utils.db_connector import DatabaseConnector
from src.utils.data_processor import ChargerStatusProcessor
import json
from datetime import datetime, timedelta
import time
import logging
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/online_learning.log'),
        logging.StreamHandler()
    ]
)

class OnlineLearningSystem:
    def __init__(self, learning_interval: int = 300):  # 5분마다 학습
        """
        온라인 학습 시스템 초기화
        
        Args:
            learning_interval: 학습 간격(초)
        """
        self.learning_interval = learning_interval
        self.detector = OCPPAnomalyDetectionSystem()
        self.db_connector = DatabaseConnector()
        self.processor = ChargerStatusProcessor()
        self.last_learning_time = None
        self.last_data_time = None
        
        # 모델 로드
        try:
            self.detector.load_model('saved_models/charger_status_anomaly_detector.pth')
            logging.info("기존 모델을 성공적으로 로드했습니다.")
        except Exception as e:
            logging.info("기존 모델이 없어 새로운 모델을 초기화합니다.")
            self.detector.model = self.detector.model = nn.Sequential(
                nn.Linear(3, 64),
                nn.ReLU(),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 64),
                nn.ReLU(),
                nn.Linear(64, 3)
            )
    
    def get_new_data(self) -> list:
        """새로운 데이터 조회"""
        if self.last_data_time is None:
            # 첫 실행시 최근 1시간 데이터 조회
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
        else:
            # 마지막 확인 이후의 데이터 조회
            start_time = self.last_data_time
            end_time = datetime.now()
        
        data = self.db_connector.get_charger_status_data(
            start_time=start_time,
            end_time=end_time
        )
        
        if data:
            self.last_data_time = end_time
        
        return data
    
    def update_model(self, new_data: list):
        """모델 업데이트"""
        if not new_data:
            return
        
        try:
            # 데이터 전처리
            processed_data = self.processor.process_status_data(new_data)
            normalized_data = self.processor.normalize_data(processed_data)
            
            # 텐서 변환
            data_tensor = torch.FloatTensor(normalized_data)
            
            # 모델 학습
            self.detector.model.train()
            criterion = nn.MSELoss()
            optimizer = optim.Adam(self.detector.model.parameters(), lr=0.001)
            
            # 미니배치 학습
            batch_size = 32
            for i in range(0, len(data_tensor), batch_size):
                batch = data_tensor[i:i + batch_size]
                
                # 순전파
                output = self.detector.model(batch)
                loss = criterion(output, batch)
                
                # 역전파
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            
            # 모델 저장
            self.detector.save_model()
            
            logging.info(f"모델이 {len(new_data)}개의 새로운 데이터로 업데이트되었습니다.")
            
        except Exception as e:
            logging.error(f"모델 업데이트 중 오류 발생: {str(e)}")
    
    def detect_anomalies(self, data: list) -> list:
        """이상 데이터 탐지"""
        if not data:
            return []
        
        try:
            # 데이터 전처리
            processed_data = self.processor.process_status_data(data)
            normalized_data = self.processor.normalize_data(processed_data)
            
            # 이상 탐지
            anomalies = self.detector.detect_anomaly(normalized_data)
            
            # 이상 데이터 상세 정보 수집
            anomaly_details = []
            for i, (item, is_anomaly) in enumerate(zip(data, anomalies)):
                if is_anomaly:
                    try:
                        inner_data = json.loads(item['payload']['data'])
                        anomaly_details.append({
                            'msg_uuid': item['msg_uuid'],
                            'rechgr_id': item['rechgr_id'],
                            'connector_id': inner_data.get('connectorId'),
                            'status': inner_data.get('status'),
                            'error_code': inner_data.get('errorCode'),
                            'msg_time': item['msg_time']
                        })
                    except json.JSONDecodeError:
                        logging.error(f"데이터 파싱 오류: {item['payload']['data']}")
            
            return anomaly_details
            
        except Exception as e:
            logging.error(f"이상 탐지 중 오류 발생: {str(e)}")
            return []
    
    def run(self):
        """온라인 학습 시스템 실행"""
        logging.info("온라인 학습 시스템을 시작합니다.")
        
        while True:
            try:
                # 새로운 데이터 조회
                new_data = self.get_new_data()
                
                if new_data:
                    logging.info(f"새로운 데이터 {len(new_data)}개를 확인했습니다.")
                    
                    # 이상 탐지
                    anomalies = self.detect_anomalies(new_data)
                    
                    if anomalies:
                        logging.warning(f"이상 데이터 {len(anomalies)}개가 감지되었습니다.")
                        for anomaly in anomalies:
                            logging.warning(
                                f"이상 감지 - 충전기: {anomaly['rechgr_id']}, "
                                f"커넥터: {anomaly['connector_id']}, "
                                f"상태: {anomaly['status']}, "
                                f"오류: {anomaly['error_code']}, "
                                f"시간: {anomaly['msg_time']}"
                            )
                    
                    # 주기적으로 모델 업데이트
                    current_time = datetime.now()
                    if (self.last_learning_time is None or 
                        (current_time - self.last_learning_time).total_seconds() >= self.learning_interval):
                        self.update_model(new_data)
                        self.last_learning_time = current_time
                
                # 대기
                time.sleep(60)  # 1분마다 새로운 데이터 확인
                
            except Exception as e:
                logging.error(f"시스템 실행 중 오류 발생: {str(e)}")
                time.sleep(60)

def main():
    # 로그 디렉토리 생성
    os.makedirs('logs', exist_ok=True)
    
    # 온라인 학습 시스템 시작
    system = OnlineLearningSystem()
    system.run()

if __name__ == "__main__":
    main() 