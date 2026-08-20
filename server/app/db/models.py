from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from .database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    riding_styles = Column(Text, nullable=True)
    marketing_agreed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 비밀번호 암호화
    def set_password(self, raw_password: str):
        self.password = pwd_context.hash(raw_password[:72])

    # 비밀번호 검증
    def verify_password(self, raw_password: str) -> bool:
        return pwd_context.verify(raw_password, self.password)