import numpy as np
import pandas as pd
import json
from typing import List, Dict, Any

class ChargerStatusProcessor:
    def __init__(self):
        self.normalization_params = None
    
    def process_status_data(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """
        충전기 상태 알림 데이터를 처리하여 학습 가능한 형태로 변환
        
        Args:
            data: 충전기 상태 알림 메시지 리스트
            
        Returns:
            np.ndarray: 처리된 데이터
        """
        processed_data = []
        for msg in data:
            try:
                # data 필드가 JSON 문자열이므로 파싱
                inner_data = json.loads(msg['payload']['data'])
                
                # 상태값을 숫자로 변환
                status_map = {
                    "IM": 1,  # Initializing
                    "A": 2,   # Available
                    "P": 3,   # Preparing
                    "C": 4,   # Charging
                    "F": 5,   # Finishing
                    "R": 6,   # Reserved
                    "U": 7,   # Unavailable
                    "F": 8,   # Faulted
                    "DM": 9   # DeMaintenance
                }
                
                # 충전기 ID에서 숫자만 추출
                charger_id = msg['rechgr_id']
                if isinstance(charger_id, str):
                    charger_id = int(''.join(filter(str.isdigit, charger_id)))
                
                features = [
                    charger_id,  # 충전기 ID
                    inner_data.get('connectorId', 0),  # 커넥터 ID
                    status_map.get(inner_data.get('status', ''), 0)  # 상태값
                ]
                processed_data.append(features)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"데이터 처리 중 오류 발생: {str(e)}")
                continue
        
        return np.array(processed_data)
    
    def normalize_data(self, data: np.ndarray) -> np.ndarray:
        """
        데이터 정규화
        
        Args:
            data: 원본 데이터
            
        Returns:
            np.ndarray: 정규화된 데이터
        """
        if self.normalization_params is None:
            self.normalization_params = {
                'mean': np.mean(data, axis=0),
                'std': np.std(data, axis=0)
            }
        
        return (data - self.normalization_params['mean']) / self.normalization_params['std']
    
    def create_sequences(self, data: np.ndarray, sequence_length: int = 10) -> np.ndarray:
        """
        시계열 시퀀스 생성
        
        Args:
            data: 정규화된 데이터
            sequence_length: 시퀀스 길이
            
        Returns:
            np.ndarray: 시퀀스 데이터
        """
        sequences = []
        for i in range(len(data) - sequence_length + 1):
            sequences.append(data[i:i + sequence_length])
        return np.array(sequences) 