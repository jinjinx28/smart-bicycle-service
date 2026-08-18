from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/")
def get_dashboard():
    return {
        "status": "success",
        "data": {
            "totals": [
                {"label": "총 라이딩", "value": "214회", "sub": "누적 횟수"},
                {"label": "누적 거리", "value": "3,842km", "sub": "총 거리"},
                {"label": "총 라이딩 시간", "value": "186h", "sub": "시간"},
                {"label": "연속 라이딩", "value": "7일", "sub": "연속 기록"}
            ],
            "activity": {
                "badges": 12,
                "challenges": 5,
                "followers": 48,
                "savedRoutes": 19
            },
            "recommendedRoute": {
                "id": 1,
                "name": "여의나루-합정 한강 코스",
                "distance": "12.4 km",
                "duration": "약 45분",
                "image": "https://images.unsplash.com/photo-1541625602330-2277a4c46182?auto=format&fit=crop&w=800&q=80"
            },
            "quickMenu": [
                {"label": "따릉이 대여소", "path": "/bike/seoul", "icon": "MapPin"},
                {"label": "AI 코스추천", "path": "/ai", "icon": "Compass"},
                {"label": "커뮤니티", "path": "/community", "icon": "Users"},
                {"label": "장비 마켓", "path": "/market", "icon": "ShoppingBag"}
            ],
            "communityFeed": [
                {"title": "오늘 한강 라이딩 날씨 미쳤네요!", "author": "라이더A", "likes": 24},
                {"title": "반포대교 무지개 분수 구경 가실 분?", "author": "철원오빠", "likes": 15}
            ]
        }
    }