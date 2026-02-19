"""
File: infer.py
Author: 양창일
Created: 2026-02-15
Description: AI 실행해주는 API 주소

Modification History:
- 2026-02-15: 초기 생성
"""

from fastapi import APIRouter, Depends, Request, HTTPException  # fastapi
from sqlalchemy.orm import Session  # 세션
from app.db.session import get_db  # db
from app.schemas.infer_schema import InferRequest, InferResponse  # 스키마
from app.services.llm_service import generate_text  # 모델 호출
from app.services import auth_service  # 인증
from app.models.user import User  # 타입

router = APIRouter(prefix="/api", tags=["infer"])  # 라우터

def require_user(req: Request, db: Session) -> User:
    auth = req.headers.get("Authorization", "")  # 헤더
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="unauthorized")  # 거부
    token = auth.split(" ", 1)[1].strip()  # 토큰
    return auth_service.get_user_from_access(db, token)  # 유저

@router.post("/infer", response_model=InferResponse)
def infer(req: Request, body: InferRequest, db: Session = Depends(get_db)):
    _user = require_user(req, db)  # 인증
    result = generate_text(body.prompt)  # 추론
    return {"result": result}  # 반환
