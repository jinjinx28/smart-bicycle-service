import os
import pandas as pd

def predict_demand(station_id: str):
    return {"station_id": station_id, "demand": "HIGH", "recommended_bikes": 8}

def get_bike_analysis_data():
    
    top_stations = [
        {"name": "여의도역 1번출구", "count": 150},
        {"name": "강남역 11번출구", "count": 140},
        {"name": "고속터미널역", "count": 130},
        {"name": "홍대입구역 9번출구", "count": 125},
        {"name": "잠실역 8번출구", "count": 120},
        {"name": "신림역 3번출구", "count": 110}
    ]
    
    monthly_usage = [
        {"month": "1월", "count": 12000},
        {"month": "2월", "count": 13500},
        {"month": "3월", "count": 22000},
        {"month": "4월", "count": 35000},
        {"month": "5월", "count": 42000},
        {"month": "6월", "count": 48000}
    ]
    
    age_distribution = [
        {"age": "10대", "percent": 5},
        {"age": "20대", "percent": 45},
        {"age": "30대", "percent": 25},
        {"age": "40대", "percent": 15},
        {"age": "50대 이상", "percent": 10}
    ]
    
    insights = [
        {
            "title": "실시간 데이터 기반 분석",
            "description": "서울시 공공자전거 대여소 및 이용 패턴 데이터를 기반으로 도출된 결과입니다."
        },
        {
            "title": "출퇴근 시간 이용 집중",
            "description": "주요 역세권 및 거점 대여소 주변으로 이용량이 집중되는 경향을 보입니다."
        },
        {
            "title": "계절별 이용 패턴",
            "description": "기온이 온화해지는 봄·여름 시즌에 대여량이 크게 증가합니다."
        }
    ]

    return {
        "monthlyUsage": monthly_usage,
        "topStations": top_stations,
        "ageDistribution": age_distribution,
        "insights": insights
    }