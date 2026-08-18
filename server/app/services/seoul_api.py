import requests
from pathlib import Path
import pandas as pd

API_KEY = "4b744d45785a696e3132396c43746c56"
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_PATH = BASE_DIR / "seoul_bike_stations.csv"

_CACHED_STATIONS = None

def fetch_stations() -> list[dict]:
    global _CACHED_STATIONS
    if _CACHED_STATIONS is not None:
        return _CACHED_STATIONS

    try:
        if CSV_PATH.exists():
            try:
                df = pd.read_csv(CSV_PATH, encoding='utf-8')
            except Exception:
                try:
                    df = pd.read_csv(CSV_PATH, encoding='cp949')
                except Exception:
                    with open(CSV_PATH, mode='r', encoding='cp949', errors='ignore') as f:
                        df = pd.read_csv(f)
        else:
            df = pd.DataFrame()

        if not df.empty:
            stations = []
            for _, row in df.iterrows():
                available = int(row.get("HOLD_NUM") or row.get("bikes") or 0)
                total = int(row.get("RACK_TOT_CNT") or 20)
                status = "GOOD" if available >= 5 else ("LOW" if available > 0 else "EMPTY")

                stations.append({
                    "id": str(row.get("RENT_ID") or row.get("id") or ""),
                    "name": str(row.get("RENT_NM") or row.get("name") or "알 수 없는 대여소"),
                    "bikes": available,
                    "available": available,
                    "total": total,
                    "status": status,
                    "distance": "1.2km",
                    "lat": float(row.get("STA_LAT") or row.get("lat") or 0.0),
                    "lng": float(row.get("STA_LONG") or row.get("lng") or 0.0)
                })
            _CACHED_STATIONS = stations
            return _CACHED_STATIONS
    except Exception as e:
        print(f"CSV 읽기 에러: {e}")

    return []

def fetch_bike_routes(region: str = None, bike_type: str = None, difficulty: str = None):
    stations = fetch_stations()
    if not stations:
        return []
    
    types_pool = ["로드", "MTB", "그래벨", "투어링", "도심"]
    difficulties_pool = ["입문", "중급", "고급", "도전"]
    regions_pool = ["서울", "경기", "인천", "강원", "부산", "제주", "전남"]

    routes = []
    for idx, station in enumerate(stations):
        assigned_region = regions_pool[idx % len(regions_pool)]
        assigned_type = types_pool[idx % len(types_pool)]
        assigned_diff = difficulties_pool[idx % len(difficulties_pool)]

        routes.append({
            "id": idx + 1,
            "name": f"{station.get('name')} {assigned_type} 코스",
            "region": assigned_region,
            "bikeType": assigned_type,
            "difficulty": assigned_diff,
            "distance": f"{((idx % 5) + 1) * 2.5:.1f}km",
            "stationName": station.get('name'),
            "image": None
        })
    
    if region and region != "전체":
        routes = [r for r in routes if r["region"] == region]
        
    if bike_type and bike_type != "전체":
        routes = [r for r in routes if r["bikeType"] == bike_type]
        
    if difficulty and difficulty != "전체":
        routes = [r for r in routes if r["difficulty"] == difficulty]
        
    return routes

def fetch_hourly_usage() -> list[dict]:
    stations = fetch_stations()
    base_count = sum(s.get("available", 0) for s in stations) if stations else 50

    hourly_data = []
    for h in range(24):
        hourly_data.append({
            "hour": f"{h:02d}:00",
            "count": max(5, (base_count + h) % 40)
        })
    return hourly_data