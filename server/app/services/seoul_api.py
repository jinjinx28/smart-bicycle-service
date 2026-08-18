from pathlib import Path
import pandas as pd

API_KEY = "4b744d45785a696e3132396c43746c56"
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_PATH = BASE_DIR / "seoul_bike_stations.csv"

_CACHED_STATIONS = None
_CACHED_ROUTES = None

def fetch_stations() -> list[dict]:
    global _CACHED_STATIONS
    if _CACHED_STATIONS is not None:
        return _CACHED_STATIONS

    try:
        df = pd.DataFrame()
        if CSV_PATH.exists():
            for enc in ('utf-8', 'cp949'):
                try:
                    df = pd.read_csv(CSV_PATH, encoding=enc, nrows=200)
                    break
                except Exception:
                    continue

        stations = []
        if not df.empty:
            fallback_names = [
                "여의도 한강공원", "반포 한강공원", "뚝섬 유원지", "망원 한강공원", 
                "잠실철교 남단", "서울숲 공원", "광나루 한강공원", "상암 월드컵공원", 
                "양화 한강공원", "선유도 공원", "청계광장", "DDP 동대문디자인플라자"
            ]
            
            for idx, row in df.iterrows():
                raw_bikes = row.get("HOLD_NUM")
                if pd.isna(raw_bikes):
                    raw_bikes = row.get("bikes", 0)
                try:
                    available = int(raw_bikes)
                except (ValueError, TypeError):
                    available = 0

                raw_total = row.get("RACK_TOT_CNT")
                try:
                    total = int(raw_total)
                except (ValueError, TypeError):
                    total = 20

                status = "GOOD" if available >= 5 else ("LOW" if available > 0 else "EMPTY")

                raw_name = row.get("RENT_NM")
                if pd.isna(raw_name):
                    raw_name = row.get("name")
                if pd.isna(raw_name):
                    raw_name = row.get("stationName")
                
                name = str(raw_name).strip() if not pd.isna(raw_name) else ""
                if not name or name == "nan":
                    name = fallback_names[idx % len(fallback_names)]

                raw_lat = row.get("STA_LAT")
                if pd.isna(raw_lat):
                    raw_lat = row.get("lat", 0.0)
                try:
                    lat = float(raw_lat)
                except (ValueError, TypeError):
                    lat = 0.0

                raw_long = row.get("STA_LONG")
                if pd.isna(raw_long):
                    raw_long = row.get("lng", 0.0)
                try:
                    lng = float(raw_long)
                except (ValueError, TypeError):
                    lng = 0.0

                stations.append({
                    "id": str(row.get("RENT_ID", f"ST-{idx+1}")),
                    "name": name,
                    "bikes": available,
                    "available": available,
                    "total": total,
                    "status": status,
                    "distance": "1.2km",
                    "lat": lat,
                    "lng": lng
                })
        
        _CACHED_STATIONS = stations
        return _CACHED_STATIONS
    except Exception as e:
        print(f"CSV 읽기 에러: {e}")

    return []

def fetch_bike_routes(region: str = None, bike_type: str = None, difficulty: str = None):
    global _CACHED_ROUTES
    
    if _CACHED_ROUTES is None:
        stations = fetch_stations()
        if not stations:
            return []
        
        types_pool = ["로드", "MTB", "그래벨", "투어링", "도심"]
        difficulties_pool = ["입문", "중급", "고급", "도전"]
        regions_pool = ["서울", "경기", "인천", "강원", "부산", "제주", "전남"]
        fallback_names = [
            "여의도 한강공원", "반포 한강공원", "뚝섬 유원지", "망원 한강공원", 
            "잠실철교 남단", "서울숲 공원", "광나루 한강공원", "상암 월드컵공원"
        ]

        routes = []
        for idx, station in enumerate(stations[:50]):
            assigned_region = regions_pool[idx % len(regions_pool)]
            assigned_type = types_pool[idx % len(types_pool)]
            assigned_diff = difficulties_pool[idx % len(difficulties_pool)]
            
            current_station_name = station.get('name')
            if not current_station_name or current_station_name == "알 수 없는 대여소":
                current_station_name = fallback_names[idx % len(fallback_names)]

            routes.append({
                "id": idx + 1,
                "name": f"{current_station_name} {assigned_type} 코스",
                "region": assigned_region,
                "bikeType": assigned_type,
                "difficulty": assigned_diff,
                "distance": f"{((idx % 5) + 1) * 2.5:.1f}km",
                "stationName": current_station_name,
                "image": None
            })
        _CACHED_ROUTES = routes

    filtered_routes = _CACHED_ROUTES
    if region and region != "전체":
        filtered_routes = [r for r in filtered_routes if r["region"] == region]
    if bike_type and bike_type != "전체":
        filtered_routes = [r for r in filtered_routes if r["bikeType"] == bike_type]
    if difficulty and difficulty != "전체":
        filtered_routes = [r for r in filtered_routes if r["difficulty"] == difficulty]
        
    return filtered_routes

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