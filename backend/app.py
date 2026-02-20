"""
File: app.py
Author: 양창일
Created: 2026-02-15
Description:  # 서버 시작 파일 (전체를 연결하는 중심 파일)

Modification History:
- 2026-02-15: 초기 생성
"""

from fastapi import FastAPI  # fastapi
from fastapi.middleware.cors import CORSMiddleware  # cors
from backend.db.session import engine  # engine
from backend.db.base import Base  # base
from backend.models import user, refresh_token  # 모델 등록용(임포트)
from backend.routers import infer, auth, social_auth 

app = FastAPI()  # 앱

app.add_middleware(  # CORS는 반드시 특정 origin만
    CORSMiddleware,
    allow_origins=["http://localhost:8501","http://localhost:5173"],  # Vue 개발 서버 예시
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)  # 테이블 생성(초기용)

app.include_router(auth.router)
app.include_router(social_auth.router)
app.include_router(infer.router)
