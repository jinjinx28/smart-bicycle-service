import re
from pathlib import Path
import pandas as pd

API_KEY = "4b744d45785a696e3132396c43746c56"
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_PATH = BASE_DIR / "seoul_bike_stations.csv"

# 전역 캐시 변수 (최초 1회만 로드하여 메모리에 보관)
_CACHED_STATIONS = []
_CACHED_ROUTES = []

def load_csv_data_once():
    global _CACHED_STATIONS
    if _CACHED_STATIONS:
        return _CACHED_STATIONS

    df = pd.DataFrame()
    if CSV_PATH.exists():
        for enc in ('utf-8', 'cp949', 'euc-kr'):
            try:
                # 상위 100개만 딱 읽고 즉시 차단
                df = pd.read_csv(CSV_PATH, encoding=enc, nrows=100)
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
            station_id = str(row.get("대여소번호") or row.get("RENT_ID") or f"ST-{idx+1}").strip()

            raw_name = row.get("보관소(대여소)명") or row.get("대여소명") or row.get("RENT_NM") or row.get("name")
            name = str(raw_name).strip() if not pd.isna(raw_name) else ""
            
            name = re.sub(r'^\d+[\.\s]*', '', name).strip()

            if not name or name == "nan":
                name = fallback_names[idx % len(fallback_names)]

            raw_bikes = row.get("거치대수") or row.get("HOLD_NUM") or row.get("parkingBikeTotCnt")
            try:
                available = int(float(raw_bikes)) if not pd.isna(raw_bikes) else (idx * 3) % 20
            except (ValueError, TypeError):
                available = (idx * 3) % 20

            total = 20
            status = "GOOD" if available >= 5 else ("LOW" if available > 0 else "EMPTY")

            try:
                lat = float(row.get("위도") or row.get("STA_LAT") or 37.55)
            except (ValueError, TypeError):
                lat = 37.55

            try:
                lng = float(row.get("경도") or row.get("STA_LONG") or 126.97)
            except (ValueError, TypeError):
                lng = 126.97

            stations.append({
                "id": station_id,
                "name": name,
                "bikes": available,
                "available": available,
                "total": total,
                "status": status,
                "distance": f"{(idx % 5) * 0.4 + 0.5:.1f}km",
                "lat": lat,
                "lng": lng
            })
            
    _CACHED_STATIONS = stations
    return _CACHED_STATIONS

# 서버 시작 시 미리 한 번 로드하여 캐싱
load_csv_data_once()

def fetch_stations() -> list[dict]:
    return load_csv_data_once()

def fetch_bike_routes(region: str = None, bike_type: str = None, difficulty: str = None):
    global _CACHED_ROUTES
    
    if not _CACHED_ROUTES:
        stations = fetch_stations()
        if not stations:
            return []
        
        types_pool = ["로드", "MTB", "그래벨", "투어링", "도심"]
        difficulties_pool = ["입문", "중급", "고급", "도전"]
        regions_pool = ["서울", "경기", "인천", "강원", "부산", "제주", "전남"]

        routes = []
        for idx, station in enumerate(stations[:50]):
            assigned_region = regions_pool[idx % len(regions_pool)]
            assigned_type = types_pool[idx % len(types_pool)]
            assigned_diff = difficulties_pool[idx % len(difficulties_pool)]
            
            current_station_name = station.get('name')

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