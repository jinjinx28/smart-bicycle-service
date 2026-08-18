from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, bike, ai, dashboard, route, chat
app = FastAPI(title="따릉이 스마트 서비스 API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 일괄 등록 
for api_router in (auth.router, bike.router, ai.router, dashboard.router, route.router, chat.router):
    app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "따릉이 서버 정상 가동 중"}