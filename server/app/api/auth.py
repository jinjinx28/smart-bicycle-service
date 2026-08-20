from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import create_mock_token
from app.db.database import get_db
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])


# --- Schemas ---
class AuthRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    riding_styles: Optional[str] = None
    marketing_agreed: Optional[bool] = None


# --- 1. 회원가입 (Create) ---
@router.post("/signup")
def signup(req: AuthRequest, db: Session = Depends(get_db)):
    if not req.email or not req.password:
        raise HTTPException(status_code=400, detail="이메일과 비밀번호를 입력해주세요.")

    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")

    user = User(
        email=req.email,
        username=req.username or "new_user",
        riding_styles=req.riding_styles,
        marketing_agreed=req.marketing_agreed or False,
    )
    user.set_password(req.password)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "status": "success",
        "message": "회원가입 완료",
        "user": {"id": user.id, "email": user.email, "username": user.username},
    }


# --- 2. 로그인 (Read) ---
@router.post("/login")
def login(req: AuthRequest, db: Session = Depends(get_db)):
    if not req.email or not req.password:
        raise HTTPException(status_code=400, detail="이메일과 비밀번호를 모두 입력해주세요.")

    user = db.query(User).filter(User.email == req.email).first()
    if not user or not user.verify_password(req.password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다.")

    return {
        "status": "success",
        "message": "로그인 성공",
        "token": create_mock_token(str(user.id)),
        "user": {"id": user.id, "email": user.email, "username": user.username},
    }


# --- 3. 회원 정보 수정 (Update) ---
@router.patch("/users/{user_id}")
def update_user(user_id: int, req: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 회원입니다.")

    if req.username is not None:
        user.username = req.username
    if req.riding_styles is not None:
        user.riding_styles = req.riding_styles
    if req.marketing_agreed is not None:
        user.marketing_agreed = req.marketing_agreed
    if req.password:
        user.set_password(req.password)

    db.commit()
    db.refresh(user)

    return {
        "status": "success",
        "message": "회원정보 수정 완료",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "riding_styles": user.riding_styles,
            "marketing_agreed": user.marketing_agreed,
        },
    }


# --- 4. 회원 탈퇴 (Delete) ---
@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 회원입니다.")

    db.delete(user)
    db.commit()

    return {"status": "success", "message": "회원 탈퇴 완료"}