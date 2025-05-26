import torch
import torch.nn as nn
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
import json

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fire_prediction.log'),
        logging.StreamHandler()
    ]
)

class FirePredictionModel(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int):
        super(FirePredictionModel, self).__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True
        )
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]
        out = self.fc(last_hidden)
        return self.sigmoid(out)

class FirePredictionSystem:
    def __init__(self, model_path: str = None):
        self.model = FirePredictionModel(
            input_size=10,  # 입력 특성 수
            hidden_size=64,
            num_layers=2
        )
        if model_path:
            self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        
        # 위험도 임계값
        self.warning_threshold = 0.7
        self.critical_threshold = 0.9
        
        # 데이터 버퍼
        self.data_buffer = []
        self.buffer_size = 100  # 100개 데이터 포인트 유지

    def preprocess_data(self, meter_values: Dict, status: Dict, diagnostics: Dict) -> torch.Tensor:
        """OCPP 메시지 데이터 전처리"""
        try:
            # 전류/전압 데이터 추출
            current = float(meter_values.get('current', 0))
            voltage = float(meter_values.get('voltage', 0))
            temperature = float(meter_values.get('temperature', 0))
            
            # 상태 정보 추출
            status_code = int(status.get('status_code', 0))
            error_code = int(status.get('error_code', 0))
            
            # 진단 정보 추출
            diagnostic_code = int(diagnostics.get('diagnostic_code', 0))
            system_health = float(diagnostics.get('system_health', 0))
            
            # 추가 특성 계산
            power = current * voltage
            temperature_rate = self._calculate_temperature_rate(temperature)
            current_variance = self._calculate_current_variance(current)
            
            # 특성 벡터 생성
            features = torch.tensor([
                current, voltage, temperature,
                power, temperature_rate, current_variance,
                status_code, error_code,
                diagnostic_code, system_health
            ], dtype=torch.float32)
            
            return features.unsqueeze(0)  # 배치 차원 추가
            
        except Exception as e:
            logging.error(f"데이터 전처리 중 오류 발생: {str(e)}")
            return None

    def _calculate_temperature_rate(self, current_temp: float) -> float:
        """온도 변화율 계산"""
        if not self.data_buffer:
            return 0.0
        
        prev_temp = self.data_buffer[-1][2]  # 이전 온도
        return (current_temp - prev_temp) / 1.0  # 1초당 변화율

    def _calculate_current_variance(self, current: float) -> float:
        """전류 변동성 계산"""
        if len(self.data_buffer) < 2:
            return 0.0
        
        currents = [data[0] for data in self.data_buffer[-10:]]  # 최근 10개 전류값
        return np.var(currents)

    def predict_fire_risk(self, meter_values: Dict, status: Dict, diagnostics: Dict) -> Tuple[float, str]:
        """화재 위험도 예측"""
        try:
            # 데이터 전처리
            features = self.preprocess_data(meter_values, status, diagnostics)
            if features is None:
                return 0.0, "데이터 처리 오류"
            
            # 예측 수행
            with torch.no_grad():
                risk_score = self.model(features).item()
            
            # 위험도 판단
            if risk_score >= self.critical_threshold:
                risk_level = "심각"
            elif risk_score >= self.warning_threshold:
                risk_level = "경고"
            else:
                risk_level = "정상"
            
            # 데이터 버퍼 업데이트
            self._update_buffer(features.squeeze().numpy())
            
            return risk_score, risk_level
            
        except Exception as e:
            logging.error(f"위험도 예측 중 오류 발생: {str(e)}")
            return 0.0, "예측 오류"

    def _update_buffer(self, new_data: np.ndarray):
        """데이터 버퍼 업데이트"""
        self.data_buffer.append(new_data)
        if len(self.data_buffer) > self.buffer_size:
            self.data_buffer.pop(0)

    def train(self, training_data: List[Dict]):
        """모델 학습"""
        try:
            self.model.train()
            optimizer = torch.optim.Adam(self.model.parameters())
            criterion = nn.BCELoss()
            
            for epoch in range(100):  # 100 에포크 학습
                total_loss = 0
                for data in training_data:
                    features = self.preprocess_data(
                        data['meter_values'],
                        data['status'],
                        data['diagnostics']
                    )
                    if features is None:
                        continue
                        
                    target = torch.tensor([data['fire_occurred']], dtype=torch.float32)
                    
                    optimizer.zero_grad()
                    output = self.model(features)
                    loss = criterion(output, target)
                    loss.backward()
                    optimizer.step()
                    
                    total_loss += loss.item()
                
                if (epoch + 1) % 10 == 0:
                    logging.info(f"Epoch {epoch+1}, Loss: {total_loss/len(training_data):.4f}")
            
            # 학습된 모델 저장
            torch.save(self.model.state_dict(), 'models/fire_prediction_model.pth')
            logging.info("모델 학습 완료 및 저장")
            
        except Exception as e:
            logging.error(f"모델 학습 중 오류 발생: {str(e)}")

def main():
    # 시스템 초기화
    system = FirePredictionSystem()
    
    # 예시 데이터
    meter_values = {
        'current': 32.5,
        'voltage': 220.0,
        'temperature': 45.0
    }
    
    status = {
        'status_code': 1,
        'error_code': 0
    }
    
    diagnostics = {
        'diagnostic_code': 0,
        'system_health': 0.95
    }
    
    # 위험도 예측
    risk_score, risk_level = system.predict_fire_risk(meter_values, status, diagnostics)
    logging.info(f"위험도 점수: {risk_score:.4f}, 위험 수준: {risk_level}")

if __name__ == "__main__":
    main() 