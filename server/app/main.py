from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ai, auth, bike, chat, dashboard, route
from app.db.database import init_db

app = FastAPI(title="따릉이 스마트 서비스 API")

# DB 테이블 생성
@app.on_event("startup")
def on_startup():
    init_db()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 일괄 등록
routers = (auth.router, bike.router, ai.router, dashboard.router, route.router, chat.router)
for r in routers:
    app.include_router(r, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "따릉이 서버 정상 가동 중"}