"""
File: session.py
Author: 양창일
Created: 2026-02-15
Description: 데이터베이스랑 연결해주는 파일

Modification History:
- 2026-02-15: 초기 생성
"""

from sqlalchemy import create_engine  # 엔진
from sqlalchemy.orm import sessionmaker  # 세션팩토리
from backend.core.config import settings  # 설정

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}  # sqlite 옵션
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, future=True)  # DB 엔진
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)  # 세션

def get_db():  # DI용 DB 세션
    db = SessionLocal()  # 세션 생성
    try:
        yield db  # 세션 제공
    finally:
        db.close()  # 세션 종료
