import torch
import torch.nn as nn
import torch.optim as optim
from src.utils.data_processor import MeterValuesProcessor
from src.utils.db_connector import DatabaseConnector
from src.models.autoencoder import LSTMAutoencoder
import numpy as np
from typing import List, Dict, Any

def train_meter_values_model(
    data: List[Dict[str, Any]],
    input_dim: int = 4,
    hidden_dim: int = 64,
    num_layers: int = 2,
    batch_size: int = 32,
    epochs: int = 100,
    learning_rate: float = 0.001
):
    # 데이터 처리
    processor = MeterValuesProcessor()
    processed_data = processor.process_meter_values(data)
    normalized_data = processor.normalize_data(processed_data)
    sequences = processor.create_sequences(normalized_data)
    
    # 데이터를 텐서로 변환
    sequences = torch.FloatTensor(sequences)
    
    # 모델 초기화
    model = LSTMAutoencoder(input_dim, hidden_dim, num_layers)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # 학습
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for i in range(0, len(sequences), batch_size):
            batch = sequences[i:i + batch_size]
            
            # 순전파
            output = model(batch)
            loss = criterion(output, batch)
            
            # 역전파
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        # 에포크별 손실 출력
        avg_loss = total_loss / (len(sequences) / batch_size)
        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}')
    
    return model, processor

if __name__ == "__main__":
    # 데이터베이스에서 데이터 가져오기
    db_connector = DatabaseConnector()
    meter_values_data = db_connector.get_meter_values_data()
    
    if not meter_values_data:
        print("데이터베이스에서 MeterValues 데이터를 가져오지 못했습니다.")
        exit(1)
    
    print(f"총 {len(meter_values_data)}개의 MeterValues 데이터를 가져왔습니다.")
    
    # 모델 학습
    model, processor = train_meter_values_model(meter_values_data)
    
    # 모델 저장
    torch.save({
        'model_state_dict': model.state_dict(),
        'processor': processor
    }, 'saved_models/meter_values_anomaly_detector.pth')
    
    print("모델 학습이 완료되었습니다.") 