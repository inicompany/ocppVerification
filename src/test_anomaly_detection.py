import torch
from src.models.detector import OCPPAnomalyDetectionSystem
from src.utils.sample_data_generator import load_sample_data, generate_sample_data
import json
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """테스트용 샘플 데이터 생성"""
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
                'msg_time': current_time,
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
                'msg_time': current_time,
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

def test_anomaly_detection():
    # 샘플 데이터 로드 또는 생성
    status_data = load_sample_data()
    if status_data is None:
        print("샘플 데이터를 생성합니다...")
        status_data = generate_sample_data()
    
    print(f"총 {len(status_data)}개의 샘플 데이터를 사용합니다.")
    
    # 이상 탐지 시스템 초기화
    detector = OCPPAnomalyDetectionSystem()
    
    try:
        # 저장된 모델 로드
        detector.load_model('saved_models/charger_status_anomaly_detector.pth')
        print("모델을 성공적으로 로드했습니다.")
    except Exception as e:
        print(f"모델 로드 중 오류 발생: {str(e)}")
        return
    
    # 이상 탐지 수행
    anomalies = detector.detect_anomaly(status_data, threshold=0.1)
    
    # 결과 분석
    total_samples = len(anomalies)
    anomaly_count = sum(anomalies)
    anomaly_percentage = (anomaly_count / total_samples) * 100
    
    print("\n=== 이상 탐지 결과 ===")
    print(f"총 데이터 수: {total_samples}")
    print(f"이상 데이터 수: {anomaly_count}")
    print(f"이상 비율: {anomaly_percentage:.2f}%")
    
    # 이상 데이터 상세 정보 출력
    if anomaly_count > 0:
        print("\n=== 이상 데이터 상세 정보 ===")
        for i, (data, is_anomaly) in enumerate(zip(status_data, anomalies)):
            if is_anomaly:
                try:
                    inner_data = json.loads(data['payload']['data'])
                    print(f"\n이상 데이터 #{i+1}:")
                    print(f"충전기 ID: {data['rechgr_id']}")
                    print(f"커넥터 ID: {inner_data.get('connectorId', 'N/A')}")
                    print(f"상태: {inner_data.get('status', 'N/A')}")
                    print(f"시간: {data['msg_time']}")
                    print(f"오류 코드: {inner_data.get('errorCode', 'N/A')}")
                except json.JSONDecodeError:
                    print(f"데이터 파싱 오류: {data['payload']['data']}")

if __name__ == "__main__":
    test_anomaly_detection() 