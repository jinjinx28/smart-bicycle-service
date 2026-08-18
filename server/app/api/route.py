from fastapi import APIRouter, Query
from typing import Optional
from app.services.seoul_api import fetch_stations, fetch_bike_routes

router = APIRouter(prefix="/routes", tags=["Route"])

@router.get("")
def get_routes(type: Optional[str] = Query(None)):
    return {
        "status": "success",
        "type": type,
        "data": fetch_bike_routes(type)
    }

@router.get("/stations")
def get_bike_stations():
    return {
        "status": "success",
        "stations": fetch_stations(),       
        "hourlyUsage": []         
    }
