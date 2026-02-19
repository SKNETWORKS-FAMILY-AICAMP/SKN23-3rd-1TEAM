"""
File: user.py
Author: 양창일
Created: 2026-02-15
Description: 사용자 정보를 저장하는 구조

Modification History:
- 2026-02-15: 초기 생성
"""

from sqlalchemy import String, Integer  # 컬럼 타입
from sqlalchemy.orm import Mapped, mapped_column  # 매핑
from app.db.base import Base  # 베이스

class User(Base):
    __tablename__ = "users"  # 테이블명

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  # PK
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)  # 유저명(내부 식별)
    password_hash: Mapped[str | None] = mapped_column(String(256), nullable=True)  # 로컬 로그인 비번 해시(소셜은 None)

    provider: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)  # kakao/google/naver
    provider_user_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)  # 제공자 고유 ID
    email: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)  # 이메일(있으면)