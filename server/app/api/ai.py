import random
from typing import Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from app.services.seoul_api import fetch_hourly_usage, fetch_stations, load_csv_data_once

router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/bike/analysis")
def get_analysis_data():
    """자전거 사용량 분석 데이터 제공"""
    try:
        return {
            "status": "success",
            "total_stations": len(fetch_stations()),
            "hourly_data": fetch_hourly_usage(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ForecastRequest(BaseModel):
    station_id: Optional[Any] = "ST-1"
    hour: Optional[Any] = 12
    temperature: Optional[Any] = 20.0
    rainfall: Optional[Any] = 0.0

    @field_validator("station_id", mode="before")
    def parse_station(cls, v):
        return str(v) if v else "ST-1"

    class Config:
        extra = "allow"


@router.post("/bike/forecast")
def predict_bike_demand(payload: ForecastRequest):
    # 1. 대여소 정보 조회 (없으면 첫 번째 대여소 기본값)
    stations = load_csv_data_once()
    station = next((s for s in stations if str(s.get("id")) == str(payload.station_id)), stations[0] if stations else {"total": 15, "name": "기본 대여소"})
    scale = station.get("total", 15)

    # 2. 입력값 파싱 (안전한 기본값 적용)
    hour = int(payload.hour) if str(payload.hour).isdigit() else 12
    rain = float(payload.rainfall) if payload.rainfall not in (None, "") else 0.0

    # 3. 시간대별 가중치 및 날씨/랜덤 변동성 적용 (고정값 방지)
    weights = {0: 0.1, 1: 0.05, 2: 0.05, 3: 0.05, 4: 0.1, 5: 0.2, 8: 1.4, 9: 1.5, 18: 1.6, 19: 1.4}
    hour_weight = weights.get(hour, 1.0)
    weather_factor = 0.4 if rain > 0 else 1.0
    
    # 매번 다르게 나오도록 미세한 랜덤 계수 곱하기
    demand = int(scale * 0.8 * hour_weight * weather_factor * random.uniform(0.9, 1.1))

    # 4. 새벽 시간 및 최대/최소 범위 제한
    if 0 <= hour <= 4:
        demand = random.randint(0, 3)
    else:
        demand = max(2, min(demand, scale * 2))

    # 5. 등급 판정
    threshold = scale * 0.7
    level = "높음" if demand >= threshold else ("보통" if demand >= scale * 0.3 else "낮음")

    return {
        "status": "success",
        "station_name": station.get("name"),
        "predicted_demand": demand,
        "demand_level": level,
        "shortage_risk": demand >= threshold,
        "message": f"[{station.get('name')}] 해당 시간대 수요는 {level}입니다."
    }