import math
import os
import re
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

_CACHED_STATIONS: list[dict] = []
_CACHED_ROUTES: list[dict] = []
_CACHED_WEATHER: list[dict] = []

# 서울 중심부 기본값 (서울시청 기준)
DEFAULT_LAT = 37.5665
DEFAULT_LNG = 126.9780

def find_data_file(keyword: str) -> Path:
    current_file = Path(__file__).resolve()
    search_dirs = [current_file.parent, Path.cwd()] + list(current_file.parents)

    for d in search_dirs:
        if not d.exists():
            continue
        for f in d.iterdir():
            if f.is_file():
                fn = f.name.lower()
                if keyword in fn and (fn.endswith(".csv") or fn.endswith(".xlsx") or fn.endswith(".xls")):
                    return f

    raise FileNotFoundError(f"'{keyword}' 파일을 찾을 수 없습니다.")

def clean_station_name(raw_name: str, fallback_idx: int = 1) -> str:
    if not raw_name or pd.isna(raw_name):
        return f"대여소 #{fallback_idx}"

    s = str(raw_name).strip()

    if s.lower() in ["nan", "none", "null", "", "보관소(대여소)명", "대여소명"]:
        return f"대여소 #{fallback_idx}"

    if re.search(r"\d{4}[-\.\/]\d{1,2}", s):
        return f"대여소 #{fallback_idx}"

    s = re.sub(r"^(서울특별시|서울시|서울)\s*", "", s).strip()
    s = re.sub(
        r"^(강남구|강동구|강북구|강서구|관악구|광진구|구로구|금천구|노원구|도봉구|동대문구|동작구|마포구|서대문구|서초구|성동구|성북구|송파구|양천구|영등포구|용산구|은평구|종로구|중구|중랑구)\s*",
        "",
        s,
    ).strip()

    cleaned = re.sub(r"^\d+[\.\s_\-]+", "", s).strip()
    cleaned = re.sub(r"^ST-\d+[\.\s_\-]+", "", cleaned, flags=re.IGNORECASE).strip()

    return cleaned if cleaned and cleaned.lower() != "nan" else f"대여소 #{fallback_idx}"

def load_csv_data_once() -> list[dict]:
    global _CACHED_STATIONS
    if _CACHED_STATIONS:
        return _CACHED_STATIONS

    target_file = find_data_file("station")
    try:
        if target_file.name.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(target_file, header=None)
        else:
            for enc in ("utf-8-sig", "cp949", "euc-kr", "utf-8"):
                try:
                    df = pd.read_csv(target_file, encoding=enc, header=None)
                    if not df.empty: break
                except Exception: continue
    except Exception as e:
        raise ValueError(e)

    stations = []
    for idx, row in df.iterrows():
        row_values = row.fillna("").values
        
        raw_name = str(row_values[1]).strip() if len(row_values) > 1 else ""
        if not raw_name or raw_name in ["보관소(대여소)명", "대여소명"]:
            continue

        lat, lng, total_racks = DEFAULT_LAT, DEFAULT_LNG, 15
        for val in row_values:
            try:
                f_val = float(val)
                if 37.0 <= f_val <= 38.0: lat = f_val
                elif 126.0 <= f_val <= 128.0: lng = f_val
                elif f_val.is_integer() and 5 <= int(f_val) <= 100: total_racks = int(f_val)
            except (ValueError, TypeError):
                continue

        s_name = clean_station_name(raw_name, fallback_idx=len(stations) + 1)
        available = int(max(1, ((len(stations) * 7) + 3) % total_racks))

        stations.append({
            "id": f"ST-{len(stations) + 1}",
            "name": str(s_name),
            "bikes": available,
            "available": available,
            "total": total_racks,
            "status": "GOOD" if available >= 5 else "LOW",
            "distance": "0.0km",
            "raw_distance": 0.0,
            "lat": float(lat),
            "lng": float(lng),
        })

    _CACHED_STATIONS = stations
    return _CACHED_STATIONS

def fetch_weather_data() -> list[dict]:
    global _CACHED_WEATHER
    if _CACHED_WEATHER:
        return _CACHED_WEATHER

    try:
        target_file = find_data_file("weather")
        df = pd.read_csv(target_file, encoding='cp949')
        df = df.where(pd.notnull(df), None)
        _CACHED_WEATHER = df.to_dict(orient="records")
    except Exception:
        _CACHED_WEATHER = []

    return _CACHED_WEATHER

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(float(lat2) - float(lat1))
    dlon = math.radians(float(lon2) - float(lon1))
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(float(lat1)))
        * math.cos(math.radians(float(lat2)))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return float(R * c)

def fetch_stations(user_lat=None, user_lng=None, limit: int = 10) -> list[dict]:
    stations = load_csv_data_once()
    try:
        target_lat = float(user_lat) if user_lat is not None and not math.isnan(float(user_lat)) else DEFAULT_LAT
        target_lng = float(user_lng) if user_lng is not None and not math.isnan(float(user_lng)) else DEFAULT_LNG
    except (ValueError, TypeError):
        target_lat, target_lng = DEFAULT_LAT, DEFAULT_LNG

    updated_stations = []
    for station in stations:
        s_copy = station.copy()
        dist = calculate_distance(target_lat, target_lng, s_copy["lat"], s_copy["lng"])
        if math.isnan(dist): dist = 0.0
        s_copy["raw_distance"] = float(dist)
        s_copy["distance"] = f"{dist:.1f}km"
        updated_stations.append(s_copy)

    updated_stations.sort(key=lambda x: x["raw_distance"])
    return updated_stations[:limit]

def fetch_bike_routes(region: str = None, bike_type: str = None, difficulty: str = None) -> list[dict]:
    global _CACHED_ROUTES
    if not _CACHED_ROUTES:
        stations = fetch_stations(limit=50)
        types = ["로드", "MTB", "그래벨", "투어링", "도심"]
        diffs = ["입문", "중급", "고급", "도전"]
        
        base_route_names = [
            "북한산 순환 코스", "한강 자전거 도로 코스", "남산 북악산 업힐 코스", 
            "여의도 한강공원 코스", "반포 잠수교 라이딩", "청계천 도심 산책 코스", 
            "올림픽공원 순환 코스", "양재천 자전거 길", "불광천 코스", "탄천 합수부 코스"
        ]
        
        routes = []
        for idx, s in enumerate(stations):
            route_name = base_route_names[idx % len(base_route_names)]
            elevation_val = f"{(idx * 45 + 120)}m"
            time_val = f"{(idx % 2) + 1}시간 {(idx * 15) % 60}분"
            
            routes.append({
                "id": idx + 1,
                "name": f"{s.get('name')} {types[idx % len(types)]} 코스",
                "region": "서울시",
                "bikeType": types[idx % len(types)],
                "difficulty": diffs[idx % len(diffs)],
                "distance": f"{((idx % 5) + 1) * 3.5:.1f}km",
                "elevation": elevation_val,
                "cumulativeElevation": elevation_val,
                "elevationGain": elevation_val,
                "time": time_val,
                "estimatedTime": time_val,
                "duration": time_val,
                "rating": round(4.5 + (idx % 5) * 0.1, 1),
                "stationName": str(s.get("name")),
                "image": None,
            })
        _CACHED_ROUTES = routes
    
    res = _CACHED_ROUTES
    if region and region not in ["전체", "서울", "서울시"]: res = [r for r in res if r["region"] == region]
    if bike_type and bike_type not in ["전체", "personal", "all"]: res = [r for r in res if r["bikeType"] == bike_type]
    if difficulty and difficulty != "전체": res = [r for r in res if r["difficulty"] == difficulty]
    return res

def fetch_hourly_usage() -> list[dict]:
    """
    대여소 총 수용량을 바탕으로, 실제 출퇴근 시간대(오전 8~9시, 오후 6~7시)에 
    이용량이 급증하는 현실적인 시간대별 이용량 패턴을 계산합니다.
    """
    stations = fetch_stations(limit=10)
    total_capacity = sum(s.get("total", 15) for s in stations)
    base_weight = max(10, total_capacity // 5)
    
    hourly_data = []
    for h in range(24):
        morning_peak = math.exp(-((h - 8) ** 2) / 4.0) * 1.5
        
        evening_peak = math.exp(-((h - 18) ** 2) / 6.0) * 2.0
        
        multiplier = 0.6 + morning_peak + evening_peak
        count = int(base_weight * multiplier + (h % 2))
        
        hourly_data.append({
            "hour": f"{h:02d}:00", 
            "count": int(max(3, count))
        })
        
    return hourly_data

async def update_weather_cache() -> list[dict]:
    global _CACHED_WEATHER
    _CACHED_WEATHER = []
    return fetch_weather_data()