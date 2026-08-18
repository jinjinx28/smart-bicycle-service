from fastapi import APIRouter, Query
from typing import Optional
from app.services.seoul_api import fetch_stations, fetch_bike_routes

router = APIRouter(tags=["Bike Service"])

@router.get("/bike/seoul/routes")
def get_routes(type: Optional[str] = Query(None)):
    return {
        "status": "success",
        "type": type,
        "data": fetch_bike_routes(type)
    }

@router.get("/routes")
def get_routes_alias(type: Optional[str] = Query(None)):
    return {
        "status": "success",
        "type": type,
        "data": fetch_bike_routes(type)
    }

@router.get("/bike/stations")
def get_bike_stations():
    return {
        "status": "success",
        "stations": fetch_stations(),        
        "hourlyUsage": []        
    }