from typing import Dict, List, Optional
from datetime import datetime
import json

class OCPPValidator:
    def __init__(self):
        self.required_fields = {
            'StartTransaction': [
                'connectorId',
                'idTag',
                'meterStart',
                'timestamp'
            ],
            'MeterValue': [
                'connectorId',
                'transactionId',
                'meterValue',
                'timestamp'
            ],
            'StopTransaction': [
                'transactionId',
                'meterStop',
                'timestamp',
                'reason'
            ],
            'Payment': [
                'transactionId',
                'amount',
                'currency',
                'timestamp'
            ]
        }
        
        self.field_types = {
            'connectorId': int,
            'idTag': str,
            'meterStart': int,
            'meterStop': int,
            'meterValue': int,
            'transactionId': int,
            'amount': float,
            'currency': str,
            'timestamp': str,
            'reason': str
        }
        
        self.current_transaction = None
        self.transaction_history = []
    
    def validate_message(self, message: Dict) -> Dict:
        """
        OCPP 메시지의 유효성을 검증
        
        Args:
            message: OCPP 메시지 딕셔너리
            
        Returns:
            Dict: 검증 결과
        """
        result = {
            'is_valid': True,
            'errors': []
        }
        
        # 1. 메시지 타입 검증
        msg_type = message.get('messageType')
        if not msg_type or msg_type not in self.required_fields:
            result['is_valid'] = False
            result['errors'].append(f"Invalid message type: {msg_type}")
            return result
        
        # 2. 필수 필드 검증
        for field in self.required_fields[msg_type]:
            if field not in message:
                result['is_valid'] = False
                result['errors'].append(f"Missing required field: {field}")
        
        # 3. 필드 타입 검증
        for field, value in message.items():
            if field in self.field_types:
                if not isinstance(value, self.field_types[field]):
                    result['is_valid'] = False
                    result['errors'].append(
                        f"Invalid type for {field}: expected {self.field_types[field]}, got {type(value)}"
                    )
        
        # 4. 비즈니스 로직 검증
        if result['is_valid']:
            business_errors = self._validate_business_logic(msg_type, message)
            if business_errors:
                result['is_valid'] = False
                result['errors'].extend(business_errors)
        
        return result
    
    def _validate_business_logic(self, msg_type: str, message: Dict) -> List[str]:
        """비즈니스 로직 검증"""
        errors = []
        
        if msg_type == 'StartTransaction':
            # idTag 형식 검증 (예: 20자 이하)
            if len(message['idTag']) > 20:
                errors.append("idTag must be 20 characters or less")
            
            # meterStart가 0 이상인지 검증
            if message['meterStart'] < 0:
                errors.append("meterStart must be greater than or equal to 0")
            
            # 새로운 트랜잭션 시작
            self.current_transaction = {
                'start_time': message['timestamp'],
                'meter_start': message['meterStart'],
                'connector_id': message['connectorId']
            }
            
        elif msg_type == 'MeterValue':
            if not self.current_transaction:
                errors.append("MeterValue received without active transaction")
            else:
                # meterValue가 이전 값보다 큰지 검증
                if message['meterValue'] < self.current_transaction['meter_start']:
                    errors.append("meterValue must be greater than meterStart")
                
                # transactionId가 현재 트랜잭션과 일치하는지 검증
                if message['transactionId'] != self.current_transaction.get('transaction_id'):
                    errors.append("Invalid transactionId for MeterValue")
        
        elif msg_type == 'StopTransaction':
            if not self.current_transaction:
                errors.append("StopTransaction received without active transaction")
            else:
                # meterStop이 meterStart보다 큰지 검증
                if message['meterStop'] <= self.current_transaction['meter_start']:
                    errors.append("meterStop must be greater than meterStart")
                
                # 트랜잭션 종료 시간이 시작 시간보다 이후인지 검증
                stop_time = datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))
                start_time = datetime.fromisoformat(self.current_transaction['start_time'].replace('Z', '+00:00'))
                if stop_time <= start_time:
                    errors.append("Stop time must be after start time")
        
        elif msg_type == 'Payment':
            if not self.current_transaction:
                errors.append("Payment received without active transaction")
            else:
                # 금액이 0보다 큰지 검증
                if message['amount'] <= 0:
                    errors.append("Payment amount must be greater than 0")
                
                # 통화 코드가 유효한지 검증 (예: 3자리)
                if len(message['currency']) != 3:
                    errors.append("Invalid currency code")
        
        return errors
    
    def validate_transaction_sequence(self, messages: List[Dict]) -> Dict:
        """
        트랜잭션 시퀀스의 유효성을 검증
        
        Args:
            messages: OCPP 메시지 리스트
            
        Returns:
            Dict: 검증 결과
        """
        result = {
            'is_valid': True,
            'errors': []
        }
        
        expected_sequence = ['StartTransaction', 'MeterValue', 'StopTransaction', 'Payment']
        current_sequence = []
        
        for message in messages:
            msg_type = message.get('messageType')
            if msg_type in expected_sequence:
                current_sequence.append(msg_type)
        
        # 시퀀스 순서 검증
        if current_sequence != expected_sequence:
            result['is_valid'] = False
            result['errors'].append(
                f"Invalid message sequence. Expected: {expected_sequence}, Got: {current_sequence}"
            )
        
        return result

def test_validator():
    validator = OCPPValidator()
    
    # 테스트 메시지
    start_msg = {
        'messageType': 'StartTransaction',
        'connectorId': 1,
        'idTag': 'TEST123',
        'meterStart': 0,
        'timestamp': '2024-05-10T10:00:00Z'
    }
    
    meter_msg = {
        'messageType': 'MeterValue',
        'connectorId': 1,
        'transactionId': 1,
        'meterValue': 100,
        'timestamp': '2024-05-10T10:05:00Z'
    }
    
    stop_msg = {
        'messageType': 'StopTransaction',
        'transactionId': 1,
        'meterStop': 200,
        'timestamp': '2024-05-10T10:10:00Z',
        'reason': 'Local'
    }
    
    payment_msg = {
        'messageType': 'Payment',
        'transactionId': 1,
        'amount': 1000.0,
        'currency': 'KRW',
        'timestamp': '2024-05-10T10:11:00Z'
    }
    
    # 개별 메시지 검증
    print("StartTransaction 검증:", validator.validate_message(start_msg))
    print("MeterValue 검증:", validator.validate_message(meter_msg))
    print("StopTransaction 검증:", validator.validate_message(stop_msg))
    print("Payment 검증:", validator.validate_message(payment_msg))
    
    # 시퀀스 검증
    messages = [start_msg, meter_msg, stop_msg, payment_msg]
    print("\n시퀀스 검증:", validator.validate_transaction_sequence(messages))

if __name__ == "__main__":
    test_validator() 