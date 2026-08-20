import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ai, auth, bike, chat, dashboard, route
from app.db.database import init_db
from app.services.seoul_api import update_weather_cache

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    init_db()
    
    # 서버 기동 시 날씨 데이터 자동 갱신 루프 시작
    async def scheduler():
        while True:
            try:
                await update_weather_cache()
            except Exception as e:
                print(f"날씨 데이터 갱신 중 오류 발생: {e}")
            await asyncio.sleep(3600)  # 1시간 간격
            
    asyncio.create_task(scheduler())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = (auth.router, bike.router, ai.router, dashboard.router, route.router, chat.router)
for r in routers:
    app.include_router(r, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "따릉이 서버 정상 가동 중"}