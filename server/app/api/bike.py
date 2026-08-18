from fastapi import APIRouter, Query
from typing import Optional
from app.services.seoul_api import fetch_stations, fetch_bike_routes, fetch_hourly_usage

router = APIRouter(prefix="/bike", tags=["Bike"])

@router.get("/stations")
def get_bike_stations():
    return {
        "status": "success",
        "stations": fetch_stations(),      
        "hourlyUsage": fetch_hourly_usage()        
    }

@router.get("/seoul/routes")
def get_bike_routes(
    region: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None)
):
    return {
        "status": "success",
        "data": fetch_bike_routes(region, type, difficulty)
    }

@router.get("/seoul/summary")
def get_bike_summary():
    stations = fetch_stations()
    real_station_count = len(stations)
    total_bikes_count = sum(s.get("available", 0) for s in stations)

    return {
        "status": "success",
        "data": {
            "total_bikes": total_bikes_count,
            "active_stations": real_station_count,  
            "unit": "개"
        }
    }