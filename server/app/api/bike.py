from typing import Optional
from fastapi import APIRouter, Query
from app.services.seoul_api import (
    fetch_bike_routes,
    fetch_hourly_usage,
    fetch_stations,
)

router = APIRouter(prefix="/bike", tags=["Bike"])


@router.get("/stations")
def get_bike_stations():
    stations = fetch_stations()
    return {
        "status": "success",
        "stations": stations,
        "hourlyUsage": fetch_hourly_usage(),
    }


@router.get("/seoul/routes")
def get_bike_routes(
    region: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
):
    # 영문 탭 쿼리 전달 시 필터링 미스 예외 처리
    filter_type = (
        type if type and type not in ["personal", "all", "전체"] else None
    )

    return {
        "status": "success",
        "data": fetch_bike_routes(region, filter_type, difficulty),
    }


@router.get("/seoul/summary")
def get_bike_summary():
    stations = fetch_stations()
    real_station_count = len(stations)
    total_bikes_count = sum(s.get("available", 0) for s in stations)

    return {
        "status": "success",
        "data": {
            "today_rentals": total_bikes_count,
            "operating_stations": real_station_count,
            "total_bikes": total_bikes_count,
            "active_stations": real_station_count,
            "unit": "개",
        },
    }