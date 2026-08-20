import math
import os
import re
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

SEOUL_API_KEY = os.getenv("SEOUL_API_KEY", os.getenv("API_KEY", ""))

CURRENT_DIR = Path(__file__).resolve().parent
possible_paths = [
    CURRENT_DIR.parent.parent / "seoul_bike_stations.csv",
    CURRENT_DIR.parent.parent.parent / "seoul_bike_stations.csv",
    Path.cwd() / "seoul_bike_stations.csv",
    Path.cwd() / "server" / "seoul_bike_stations.csv",
]
CSV_PATH = next((p for p in possible_paths if p.exists()), possible_paths[0])

_CACHED_STATIONS = []
_CACHED_ROUTES = []


def load_csv_data_once():
    global _CACHED_STATIONS
    if _CACHED_STATIONS:
        return _CACHED_STATIONS

    df = pd.DataFrame()
    if CSV_PATH.exists():
        for enc in ("utf-8", "cp949", "euc-kr", "utf-8-sig"):
            try:
                df = pd.read_csv(CSV_PATH, encoding=enc)
                break
            except Exception:
                continue

    stations = []
    if not df.empty:
        df.columns = [str(c).strip() for c in df.columns]

        id_col = next((c for c in df.columns if "번호" in c or "id" in c.lower()), None)
        name_col = next((c for c in df.columns if "명" in c or "이름" in c or "name" in c.lower()), None)
        usage_col = next((c for c in df.columns if "이용" in c or "건수" in c or "count" in c.lower()), None)

        grouped = df
        for idx, row in grouped.iterrows():
            station_id = str(row.get(id_col) if id_col else f"ST-{idx+1}").strip()
            raw_name = row.get(name_col) if name_col else f"따릉이 대여소 {idx+1}"
            name = str(raw_name).strip()
            name = re.sub(r"^\d+[\.\s]*", "", name).strip()

            usage_val = row.get(usage_col) if usage_col else 1
            try:
                usage_count = int(usage_val) if pd.notna(usage_val) else 1
            except (ValueError, TypeError):
                usage_count = 1

            available = max(2, (usage_count * 3) % 25)
            total = available + 5
            status = "GOOD" if available >= 5 else ("LOW" if available > 0 else "EMPTY")

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
                "lng": lng,
            })

    if not stations:
        sample_names = ["강남역 1번출구", "역삼역 3번출구", "논현역 2번출구", "삼성역 5번출구", "선릉역 1번출구"]
        for idx, s_name in enumerate(sample_names):
            stations.append({
                "id": f"ST-{idx+101}",
                "name": s_name,
                "bikes": 8,
                "available": 8,
                "total": 15,
                "status": "GOOD",
                "distance": "0.0km",
                "raw_distance": 0.0,
                "lat": 37.4979 + (idx * 0.002),
                "lng": 127.0276 + (idx * 0.002),
            })

    _CACHED_STATIONS = stations
    return _CACHED_STATIONS


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

    updated_stations.sort(key=lambda x: x["raw_distance"])
    return updated_stations


def fetch_bike_routes(region: str = None, bike_type: str = None, difficulty: str = None):
    global _CACHED_ROUTES
    if not _CACHED_ROUTES:
        stations = fetch_stations()
        types_pool = ["로드", "MTB", "그래벨", "투어링", "도심"]
        difficulties_pool = ["입문", "중급", "고급", "도전"]

        routes = []
        target_list = stations[:50] if stations else [{"name": f"따릉이 코스 {i+1}"} for i in range(10)]

        for idx, station in enumerate(target_list):
            routes.append({
                "id": idx + 1,
                "name": f"{station.get('name')} {types_pool[idx % len(types_pool)]} 코스",
                "region": "서울시",
                "bikeType": types_pool[idx % len(types_pool)],
                "difficulty": difficulties_pool[idx % len(difficulties_pool)],
                "distance": f"{((idx % 5) + 1) * 2.5:.1f}km",
                "stationName": station.get("name"),
                "image": None,
            })
        _CACHED_ROUTES = routes

    filtered_routes = _CACHED_ROUTES
    if region and region not in ["전체", "서울", "서울시"]:
        filtered_routes = [r for r in filtered_routes if r["region"] == region]
    if bike_type and bike_type not in ["전체", "personal", "all"]:
        filtered_routes = [r for r in filtered_routes if r["bikeType"] == bike_type]
    if difficulty and difficulty != "전체":
        filtered_routes = [r for r in filtered_routes if r["difficulty"] == difficulty]

    return filtered_routes


def fetch_hourly_usage() -> list[dict]:
    stations = fetch_stations()
    base_count = sum(s.get("available", 0) for s in stations) if stations else 50
    hourly_data = []
    for h in range(24):
        hourly_data.append({"hour": f"{h:02d}:00", "count": max(5, (base_count + h) % 40)})
    return hourly_data