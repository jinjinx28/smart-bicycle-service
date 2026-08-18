from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3
from app.core.security import create_mock_token
from app.db.database import insert_user, find_user_by_email

router = APIRouter(prefix="/auth", tags=["Auth"])

# 1. 로그인/회원가입에 공통으로 사용할 유연한 데이터 모델 
class AuthRequest(BaseModel):
    email: str | None = None
    username: str | None = None
    id: str | None = None
    password: str | None = None

# 2. 로그인 API
@router.post("/login")
def login(req: AuthRequest):
    # 로그인 시 필수 값 누락 방어 코드
    if not req.email or not req.password:
        raise HTTPException(status_code=400, detail="이메일과 비밀번호를 모두 입력해주세요.")

    # 입력된 이메일로 DB 조회 함수 호출
    db_user = find_user_by_email(req.email)
    
    # 유저가 없거나 비밀번호가 틀리면 에러 반환
    if not db_user or db_user[2] != req.password:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다.")

    return {
        "status": "success",
        "message": "로그인 성공",
        "token": create_mock_token(str(db_user[0])),
        "user": {
            "email": db_user[0],
            "username": db_user[1]
        }
    }

# 3. 회원가입 API
@router.post("/signup")
def signup(req: AuthRequest):
    user_username = req.username or "new_user"
    user_email = req.email
    
    if not user_email or not req.password:
        raise HTTPException(status_code=400, detail="이메일과 비밀번호를 입력해주세요.")

    if find_user_by_email(user_email):
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")

    insert_user(user_email, user_username, req.password)
    
    return {
        "status": "success",
        "message": "회원가입 완료",
        "user": {
            "email": user_email,
            "username": user_username
        }
    }