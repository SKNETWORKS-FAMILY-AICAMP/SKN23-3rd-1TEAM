"""
File: auth.py
Author: 양창일
Created: 2026-02-15
Description: 로그인, 회원가입 처리하는 API 주소

Modification History:
- 2026-02-15: 초기 생성
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response  # fastapi
from sqlalchemy.orm import Session  # 세션
from app.db.session import get_db  # DB
from app.schemas.auth_schema import SignupRequest, LoginRequest, TokenResponse, MeResponse  # 스키마
from app.services import auth_service  # 서비스
from app.core.config import settings  # 설정
from app.core.security import new_csrf_token  # CSRF
from app.models.user import User  # 타입힌트
from app.core.rate_limit import check_block, record_failure, reset_attempts

router = APIRouter(prefix="/api/auth", tags=["auth"])  # 라우터

def set_auth_cookies(res: Response, refresh_token: str, csrf_token: str) -> None:
    res.set_cookie(  # refresh 쿠키(HTTPOnly)
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/api/auth",
    )
    res.set_cookie(  # csrf 쿠키(JS가 읽어서 헤더로 보냄)
        key=settings.CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/api/auth",
    )

def clear_auth_cookies(res: Response) -> None:
    res.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/api/auth", domain=settings.COOKIE_DOMAIN)  # refresh 삭제
    res.delete_cookie(settings.CSRF_COOKIE_NAME, path="/api/auth", domain=settings.COOKIE_DOMAIN)  # csrf 삭제

def require_csrf(req: Request) -> None:
    cookie = req.cookies.get(settings.CSRF_COOKIE_NAME)  # 쿠키 csrf
    header = req.headers.get("X-CSRF-Token")  # 헤더 csrf
    if (not cookie) or (not header) or (cookie != header):
        raise HTTPException(status_code=403, detail="CSRF")  # 거부

@router.post("/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    try:
        auth_service.signup(db, req.username, req.password)  # 가입
        return {"ok": True}  # 응답
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid request")  # 정보 최소화

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, request: Request, res: Response, db: Session = Depends(get_db)):
    ip = request.client.host  # 접속 IP

    # 🔒 차단 확인
    try:
        check_block(ip)
    except Exception:
        raise HTTPException(status_code=429, detail="Too many attempts. Try later.")

    try:
        access, refresh, _ = auth_service.login(db, req.username, req.password)
        reset_attempts(ip)  # 성공하면 초기화
    except ValueError:
        record_failure(ip)  # 실패 기록
        raise HTTPException(status_code=401, detail="invalid credentials")

    csrf = new_csrf_token()
    set_auth_cookies(res, refresh, csrf)
    return {"access_token": access, "token_type": "bearer"}
@router.post("/refresh", response_model=TokenResponse)
def refresh(req: Request, res: Response, db: Session = Depends(get_db)):
    require_csrf(req)  # CSRF 체크
    refresh_token = req.cookies.get(settings.REFRESH_COOKIE_NAME)  # refresh 읽기
    if not refresh_token:
        raise HTTPException(status_code=401, detail="invalid token")  # 없음

    try:
        new_access, new_refresh = auth_service.rotate_refresh(db, refresh_token)  # 회전
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")  # 실패

    csrf = new_csrf_token()  # 새 csrf
    set_auth_cookies(res, refresh_token=new_refresh, csrf_token=csrf)  # 새 쿠키
    return {"access_token": new_access, "token_type": "bearer"}  # 새 access

@router.post("/logout")
def logout(req: Request, res: Response, db: Session = Depends(get_db)):
    require_csrf(req)  # CSRF 체크
    refresh_token = req.cookies.get(settings.REFRESH_COOKIE_NAME)  # refresh
    if refresh_token:
        auth_service.revoke_refresh(db, refresh_token)  # 폐기
    clear_auth_cookies(res)  # 쿠키 삭제
    return {"ok": True}  # 응답

def get_current_user(req: Request, db: Session) -> User:
    auth = req.headers.get("Authorization", "")  # 헤더
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="unauthorized")  # 없음
    token = auth.split(" ", 1)[1].strip()  # 토큰
    try:
        return auth_service.get_user_from_access(db, token)  # 유저
    except Exception:
        raise HTTPException(status_code=401, detail="unauthorized")  # 실패

@router.get("/me", response_model=MeResponse)
def me(req: Request, db: Session = Depends(get_db)):
    user = get_current_user(req, db)  # 유저
    return {"id": user.id, "username": user.username}  # 반환
