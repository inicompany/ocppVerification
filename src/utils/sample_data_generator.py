import json
import random
from datetime import datetime, timedelta
import os

def generate_sample_data(save_path: str = 'data/sample_data.json'):
    """
    테스트용 샘플 데이터 생성 및 저장
    
    Args:
        save_path: 샘플 데이터 저장 경로
    """
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
                'msg_time': current_time.isoformat(),
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
                'msg_time': current_time.isoformat(),
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
    
    # 데이터 저장
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print(f"샘플 데이터가 {save_path}에 저장되었습니다.")
    return sample_data

def load_sample_data(load_path: str = 'data/sample_data.json'):
    """
    저장된 샘플 데이터 로드
    
    Args:
        load_path: 샘플 데이터 파일 경로
        
    Returns:
        list: 샘플 데이터 리스트
    """
    try:
        with open(load_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 문자열 시간을 datetime 객체로 변환
            for item in data:
                item['msg_time'] = datetime.fromisoformat(item['msg_time'])
            return data
    except FileNotFoundError:
        print(f"샘플 데이터 파일을 찾을 수 없습니다: {load_path}")
        return None
    except json.JSONDecodeError:
        print(f"샘플 데이터 파일 형식이 올바르지 않습니다: {load_path}")
        return None

if __name__ == "__main__":
    # 샘플 데이터 생성 및 저장
    generate_sample_data() 