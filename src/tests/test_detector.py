import unittest
import torch
from src.models import OCPPAnomalyDetectionSystem

class TestOCPPAnomalyDetector(unittest.TestCase):
    def setUp(self):
        """테스트에 필요한 초기 설정"""
        self.detector = OCPPAnomalyDetectionSystem()
        
        # 정상 시퀀스 생성
        self.normal_sequence = [
            {
                'messageType': 'StartTransaction',
                'connectorId': 1,
                'idTag': 'TEST001',
                'meterStart': 0,
                'timestamp': '2024-03-20T10:00:00Z'
            },
            {
                'messageType': 'MeterValue',
                'connectorId': 1,
                'transactionId': 1,
                'meterValue': 1000,
                'timestamp': '2024-03-20T10:05:00Z'
            },
            {
                'messageType': 'StopTransaction',
                'transactionId': 1,
                'meterStop': 2000,
                'timestamp': '2024-03-20T10:10:00Z',
                'reason': 'Normal'
            }
        ]
        
        # 이상 시퀀스 생성 (미터 값이 비정상적으로 큰 경우)
        self.anomaly_sequence = [
            {
                'messageType': 'StartTransaction',
                'connectorId': 1,
                'idTag': 'TEST001',
                'meterStart': 0,
                'timestamp': '2024-03-20T10:00:00Z'
            },
            {
                'messageType': 'MeterValue',
                'connectorId': 1,
                'transactionId': 1,
                'meterValue': 1000000,  # 비정상적으로 큰 값
                'timestamp': '2024-03-20T10:05:00Z'
            },
            {
                'messageType': 'StopTransaction',
                'transactionId': 1,
                'meterStop': 2000000,  # 비정상적으로 큰 값
                'timestamp': '2024-03-20T10:10:00Z',
                'reason': 'Normal'
            }
        ]

    def test_model_training(self):
        """모델 학습 테스트"""
        # 학습 데이터 준비
        training_sequences = [self.normal_sequence] * 10  # 정상 시퀀스 10개
        
        # 모델 학습
        self.detector.train(training_sequences, epochs=10, batch_size=2)
        
        # 모델이 제대로 학습되었는지 확인
        self.assertIsNotNone(self.detector.model)
        self.assertTrue(isinstance(self.detector.model, torch.nn.Module))

    def test_anomaly_detection(self):
        """이상 탐지 테스트"""
        # 모델 학습
        self.detector.train([self.normal_sequence] * 10, epochs=10, batch_size=2)
        
        # 정상 시퀀스 테스트
        normal_result = self.detector.detect_anomaly(self.normal_sequence)
        self.assertFalse(normal_result['is_anomaly'])
        
        # 이상 시퀀스 테스트
        anomaly_result = self.detector.detect_anomaly(self.anomaly_sequence)
        self.assertTrue(anomaly_result['is_anomaly'])
        
        # 재구성 오차 확인
        self.assertGreater(anomaly_result['reconstruction_error'], 
                          normal_result['reconstruction_error'])

    def test_model_save_load(self):
        """모델 저장 및 로드 테스트"""
        # 모델 학습
        self.detector.train([self.normal_sequence] * 10, epochs=10, batch_size=2)
        
        # 모델 저장
        self.detector.save_model()
        
        # 새로운 detector 인스턴스 생성
        new_detector = OCPPAnomalyDetectionSystem()
        
        # 모델 로드
        new_detector.load_model()
        
        # 로드된 모델로 이상 탐지 테스트
        result = new_detector.detect_anomaly(self.normal_sequence)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main() 