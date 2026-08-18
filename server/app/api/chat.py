from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 로드
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI()

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    station_id: Optional[str] = None

@router.post("")
def chat_with_ai(payload: ChatRequest):
    user_msg = payload.message.strip()

    try:
        # 진짜 GPT-4o-mini 모델 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 스마트 자전거 서비스 'PEDALUP'의 친절한 AI 어시스턴트입니다. 자전거 대여소, 혼잡도, 수요 예측 등에 대해 친절하고 정확하게 답변해주세요."},
                {"role": "user", "content": user_msg},
            ],
        )

        ai_reply = response.choices[0].message.content

        return {
            "status": "success",
            "reply": ai_reply
        }
    except Exception as e:
        print(f"⚠️ OpenAI API 호출 에러: {e}")
        return {
            "status": "success",
            "reply": f"죄송합니다. 현재 AI 응답을 불러오는 중에 문제가 발생했습니다. (에러: {str(e)})"
        }