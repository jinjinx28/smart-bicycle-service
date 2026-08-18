import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, Any
from app.services.ai_models import get_bike_analysis_data, predict_demand

router = APIRouter(prefix="/ai", tags=["AI"])

# 서버가 실행될 때 미리 학습된 랜덤 포레스트 모델 로드
try:
    rf_model = joblib.load("bike_rf_model.pkl")
except Exception as e:
    rf_model = None

@router.get("/bike/analysis")
def get_analysis_data():
    try:
        result = get_bike_analysis_data()
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# 예측 요청을 위한 스키마 정의
class ForecastRequest(BaseModel):
    station_id: Optional[Any] = None  
    date: Optional[Any] = None
    hour: Optional[Any] = None
    is_holiday: Optional[Any] = None
    temperature: Optional[Any] = None
    humidity: Optional[Any] = None
    rainfall: Optional[Any] = None
    wind_speed: Optional[Any] = None
    recent_1h_rental_count: Optional[Any] = None
    prev_day_same_hour_rental_count: Optional[Any] = None
    rolling_7d_same_hour_avg: Optional[Any] = None

    @field_validator("station_id", mode="before")
    def parse_station_id(cls, v):
        if v is not None:
            return str(v)
        return "ST-01"

    class Config:
        extra = "allow"

@router.post("/bike/forecast")
def predict_bike_demand(payload: ForecastRequest):
    
    # 형변환 함수 
    def safe_float(val, default):
        try:
            if val is None or val == "":
                return default
            return float(val)
        except (ValueError, TypeError):
            return default

    def safe_int(val, default):
        try:
            if val is None or val == "":
                return default
            return int(val)
        except (ValueError, TypeError):
            return default

    # 입력 데이터 추출
    hour = safe_int(payload.hour, 12)
    temp = safe_float(payload.temperature, 20.0)
    rain = safe_float(payload.rainfall, 0.0)
    wind_speed = safe_float(payload.wind_speed, 2.0)

    # 머신러닝 모델을 이용한 수요 예측 
    if rf_model is not None:
        input_features = pd.DataFrame([[
            hour, temp, rain, wind_speed
        ]], columns=['hour', 'temperature', 'rainfall', 'wind_speed'])
        
        predicted_demand = float(rf_model.predict(input_features)[0])
    else:
        predicted_demand = 15.0

    # 시간대별 가중치 후처리
    HOUR_WEIGHTS = {
        8: 1.3, 9: 1.4, 10: 1.2,      # 출근 시간대
        18: 1.3, 19: 1.4, 20: 1.2      # 퇴근 시간대
    }

    if 0 <= hour <= 5:
        hour_weight = 0.4              # 새벽 시간대
    else:
        hour_weight = HOUR_WEIGHTS.get(hour, 1.0)

    # 날씨 가중치 보정
    weather_factor = 0.5 if rain > 0 else 1.0

    base_demand = predicted_demand / 5.0 if predicted_demand > 300 else predicted_demand
    
    # 모델 예측값에 시간/날씨 가중치 적용 
    calculated_demand = predicted_demand * hour_weight * weather_factor

    # 최종 수요 계산
    final_demand = int(round(calculated_demand))
    final_demand = max(5, min(final_demand, 500))

    # 등급 판정 기준
    if final_demand >= 20:
        demand_level = "높음"
        message = "해당 시간대 수요가 매우 높을 것으로 예상됩니다. 자전거 확보가 필요합니다."
    elif final_demand >= 10:
        demand_level = "보통"
        message = "해당 시간대 수요가 보통 수준입니다."
    else:
        demand_level = "낮음"
        message = "해당 시간대 수요가 비교적 한산합니다."

    return {
        "status": "success",
        "predicted_demand": final_demand,
        "demand_level": demand_level,
        "shortage_risk": final_demand > 25,
        "message": message
    }