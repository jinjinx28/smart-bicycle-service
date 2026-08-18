import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

print("weather.csv 및 seoul_bike_stations.csv 불러오는 중")

# 파일 로드 
try:
    weather_df = pd.read_csv("weather.csv", encoding="cp949")
except:
    weather_df = pd.read_csv("weather.csv", encoding="utf-8")
weather_df.columns = weather_df.columns.str.strip()

try:
    bike_df = pd.read_csv("seoul_bike_stations.csv", encoding="cp949")
except:
    bike_df = pd.read_csv("seoul_bike_stations.csv", encoding="utf-8")
bike_df.columns = bike_df.columns.str.strip()

print(" 데이터 전처리 및 병합 중")

# 날짜/시간(일시) 컬럼 형식 통일
weather_df['일시'] = pd.to_datetime(weather_df['일시'])
weather_df['hour'] = weather_df['일시'].dt.hour

# 데이터 길이 맞추기
min_len = min(len(weather_df), len(bike_df))
weather_df = weather_df.iloc[:min_len]
bike_df = bike_df.iloc[:min_len]

# 피처(X) 및 정답(y) 설정 
X = pd.DataFrame()
X['hour'] = weather_df['hour']
X['temperature'] = weather_df['기온(°C)']
X['rainfall'] = weather_df['강수량(mm)'].fillna(0)
X['wind_speed'] = weather_df['풍속(m/s)'].fillna(0)
X = X.fillna(0)

# 대여시간에서 시간대(hour)를 추출한 뒤, 시간당 대여 총 건수를 집계
bike_df['hour'] = bike_df['대여시간'].astype(str).str.zfill(4).str[:2].astype(int)

# 시간대별 대여 기록 개수를 집계하여 진짜 수요(y)로 사용
hourly_counts = bike_df.groupby('hour').size().reset_index(name='rental_count')
merged_df = pd.merge(weather_df, hourly_counts, on='hour', how='left').fillna({'rental_count': 15}) # 데이터가 없으면 기본 15건

y = merged_df['rental_count']

print("실제 데이터 기반 랜덤 포레스트 모델 학습 시작")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# 모델 저장
os.makedirs("artifacts", exist_ok=True)
joblib.dump(model, "bike_rf_model.pkl")
print("모델 학습 및 'bike_rf_model.pkl' 저장 완료!")