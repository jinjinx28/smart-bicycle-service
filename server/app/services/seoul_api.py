import re
from pathlib import Path
import pandas as pd
import math

API_KEY = "4b744d45785a696e3132396c43746c56"
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_PATH = BASE_DIR / "seoul_bike_stations.csv"

# 전역 캐시 변수
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
                df = pd.read_csv(CSV_PATH, encoding=enc, nrows=500)
                break
            except Exception:
                continue

    stations = []
    if not df.empty:
        # 컬럼명 공백 제거 및 안전한 집계 처리
        df.columns = [str(c).strip() for c in df.columns]

        if '대여소번호' in df.columns and '대여소명' in df.columns:
            agg_dict = {}
            if '이용건수' in df.columns:
                agg_dict['이용건수'] = 'sum'
            
            try:
                grouped = df.groupby(['대여소번호', '대여소명'], as_index=False).agg(agg_dict) if agg_dict else df
            except Exception:
                grouped = df
        else:
            grouped = df

        for idx, row in grouped.iterrows():
            station_id = str(row.get("대여소번호") or f"ST-{idx+1}").strip()
            raw_name = row.get("대여소명") or "따릉이 대여소"
            name = str(raw_name).strip()
            name = re.sub(r'^\d+[\.\s]*', '', name).strip()

            usage_count = int(row.get("이용건수", 1)) if '이용건수' in row else 1
            available = max(2, (usage_count * 3) % 25)
            total = available + 5

            status = "GOOD" if available >= 5 else ("LOW" if available > 0 else "EMPTY")

            # 강남역(37.4979, 127.0276) 주변에 배치되도록 좌표 부여
            lat = 37.4979 + ((idx * 0.003) % 0.05)
            lng = 127.0276 + ((idx * 0.003) % 0.05)

            stations.append({
                "id": station_id,
                "name": name,
                "bikes": available,
                "available": available,
                "total": total,
                "status": status,
                "distance": "0.0km",
                "raw_distance": 0.0,
                "lat": lat,
                "lng": lng
            })
            
    _CACHED_STATIONS = stations
    return _CACHED_STATIONS

# 서버 시작 시 로드
load_csv_data_once()

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def fetch_stations(user_lat: float = None, user_lng: float = None) -> list[dict]:
    stations = load_csv_data_once()
    
    target_lat = user_lat if user_lat is not None else 37.4979
    target_lng = user_lng if user_lng is not None else 127.0276

    updated_stations = []
    for station in stations:
        s_copy = station.copy()
        dist = calculate_distance(target_lat, target_lng, s_copy["lat"], s_copy["lng"])
        s_copy["raw_distance"] = dist
        s_copy["distance"] = f"{dist:.1f}km"
        updated_stations.append(s_copy)
    
    # 거리순 엄격 정렬
    updated_stations.sort(key=lambda x: x["raw_distance"])
    return updated_stations

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
            routes.append({
                "id": idx + 1,
                "name": f"{station.get('name')} {types_pool[idx % len(types_pool)]} 코스",
                "region": regions_pool[idx % len(regions_pool)],
                "bikeType": types_pool[idx % len(types_pool)],
                "difficulty": difficulties_pool[idx % len(difficulties_pool)],
                "distance": f"{((idx % 5) + 1) * 2.5:.1f}km",
                "stationName": station.get('name'),
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

