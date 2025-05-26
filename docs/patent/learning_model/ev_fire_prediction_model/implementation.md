# 전기차 화재 예측 학습 모델 구현 상세

## 1. 데이터 수집 및 전처리

### 1.1 OCPP 메시지 수집
```python
class OCPPDataCollector:
    def __init__(self):
        self.data_buffer = []
        self.buffer_size = 100
        
    def collect_meter_values(self, message):
        # 전류, 전압, 온도 데이터 수집
        current = message.get('current', 0)
        voltage = message.get('voltage', 0)
        temperature = message.get('temperature', 0)
        return {'current': current, 'voltage': voltage, 'temperature': temperature}
        
    def collect_status(self, message):
        # 충전기 상태 정보 수집
        status_code = message.get('status_code', 0)
        error_code = message.get('error_code', 0)
        return {'status_code': status_code, 'error_code': error_code}
```

### 1.2 특성 추출
```python
class FeatureExtractor:
    def extract_features(self, data):
        # 기본 특성
        current = data['current']
        voltage = data['voltage']
        temperature = data['temperature']
        
        # 파생 특성
        power = current * voltage
        temperature_rate = self._calculate_temperature_rate(temperature)
        current_variance = self._calculate_current_variance(current)
        
        return {
            'current': current,
            'voltage': voltage,
            'temperature': temperature,
            'power': power,
            'temperature_rate': temperature_rate,
            'current_variance': current_variance
        }
```

## 2. 모델 아키텍처

### 2.1 LSTM 모델 구현
```python
class FirePredictionModel(nn.Module):
    def __init__(self, input_size=10, hidden_size=64, num_layers=2):
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
```

### 2.2 위험도 계산
```python
class RiskCalculator:
    def __init__(self):
        self.warning_threshold = 0.7
        self.critical_threshold = 0.9
        
    def calculate_risk(self, prediction):
        if prediction >= self.critical_threshold:
            return "심각", prediction
        elif prediction >= self.warning_threshold:
            return "경고", prediction
        else:
            return "정상", prediction
```

## 3. 학습 프로세스

### 3.1 학습 설정
```python
class ModelTrainer:
    def __init__(self, model):
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters())
        self.criterion = nn.BCELoss()
        
    def train_epoch(self, data_loader):
        self.model.train()
        total_loss = 0
        for batch in data_loader:
            self.optimizer.zero_grad()
            output = self.model(batch['features'])
            loss = self.criterion(output, batch['target'])
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
        return total_loss / len(data_loader)
```

### 3.2 검증 프로세스
```python
class ModelValidator:
    def validate(self, model, data_loader):
        model.eval()
        predictions = []
        targets = []
        with torch.no_grad():
            for batch in data_loader:
                output = model(batch['features'])
                predictions.extend(output.numpy())
                targets.extend(batch['target'].numpy())
        return self.calculate_metrics(predictions, targets)
```

## 4. 실시간 예측 시스템

### 4.1 예측 파이프라인
```python
class PredictionPipeline:
    def __init__(self, model, feature_extractor, risk_calculator):
        self.model = model
        self.feature_extractor = feature_extractor
        self.risk_calculator = risk_calculator
        
    def predict(self, ocpp_message):
        # 데이터 전처리
        features = self.feature_extractor.extract_features(ocpp_message)
        
        # 예측 수행
        with torch.no_grad():
            prediction = self.model(features)
            
        # 위험도 계산
        risk_level, risk_score = self.risk_calculator.calculate_risk(prediction)
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'timestamp': datetime.now()
        }
```

### 4.2 알림 시스템
```python
class AlertSystem:
    def __init__(self):
        self.alert_levels = {
            '심각': self._handle_critical_alert,
            '경고': self._handle_warning_alert,
            '정상': self._handle_normal_alert
        }
        
    def process_alert(self, prediction_result):
        alert_handler = self.alert_levels[prediction_result['risk_level']]
        return alert_handler(prediction_result)
```

## 5. 모델 성능 모니터링

### 5.1 성능 지표 추적
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'accuracy': [],
            'precision': [],
            'recall': [],
            'f1_score': []
        }
        
    def update_metrics(self, predictions, targets):
        self.metrics['accuracy'].append(accuracy_score(targets, predictions))
        self.metrics['precision'].append(precision_score(targets, predictions))
        self.metrics['recall'].append(recall_score(targets, predictions))
        self.metrics['f1_score'].append(f1_score(targets, predictions))
```

### 5.2 자동 최적화
```python
class ModelOptimizer:
    def optimize_hyperparameters(self, model, train_data, val_data):
        param_grid = {
            'learning_rate': [0.001, 0.0001],
            'hidden_size': [32, 64, 128],
            'num_layers': [1, 2, 3]
        }
        
        best_params = None
        best_score = float('-inf')
        
        for params in ParameterGrid(param_grid):
            model = self._create_model_with_params(params)
            score = self._evaluate_model(model, train_data, val_data)
            
            if score > best_score:
                best_score = score
                best_params = params
                
        return best_params
``` 