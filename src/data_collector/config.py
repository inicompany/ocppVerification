# 데이터베이스 설정
DB_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'your_server',
    'database': 'EVCS_MS',
    'username': 'your_username',
    'password': 'your_password'
}

# Elasticsearch 설정
ES_CONFIG = {
    'hosts': ['http://10.162.1.16:52900'],
    'index_pattern': 'ocpp_msg_tr_{year}{month:02d}'
}

# 데이터 수집 설정
COLLECTION_CONFIG = {
    'batch_size': 200,
    'default_days': 1  # 기본 수집 기간 (일)
} 