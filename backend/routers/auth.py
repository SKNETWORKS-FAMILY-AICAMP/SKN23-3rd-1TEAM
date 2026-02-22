"""
File: auth.py
Author: 양창일, 김지우
Created: 2026-02-15
Description: 로그인, 회원가입 처리하는 API 주소

Modification History:
- 2026-02-15 (양창일): 초기 생성 (로그인, 회원가입, CSRF 방어, Rate Limit 등)
- 2026-02-21 (김지우): 로그인 API 로직 보완
- 2026-02-22 (김지우): 토큰 검증(/verify) API 및 비밀번호 찾기(/send-reset-email, /reset-password) API 통합 추가
"""

import os
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Header
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# --- 백엔드 모듈 임포트 ---
from backend.db.session import get_db
from backend.schemas.auth_schema import (
    SignupRequest, LoginRequest, TokenResponse, MeResponse,
    ResetEmailRequest, ResetPasswordRequest
)
from backend.services import auth_service
from backend.core.config import settings
from backend.core.security import new_csrf_token
from backend.models.user import User
from backend.core.rate_limit import check_block, record_failure, reset_attempts

load_dotenv(override=True)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-aiwork-key-2026")

# 🔥 라우터는 파일 전체에서 딱 한 번만 선언합니다!
router = APIRouter(prefix="/api/auth", tags=["auth"])


# ==========================================
# 🛠️ 쿠키 및 CSRF 보조 함수 (기존 로직 유지)
# ==========================================
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
    res.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/api/auth", domain=settings.COOKIE_DOMAIN)
    res.delete_cookie(settings.CSRF_COOKIE_NAME, path="/api/auth", domain=settings.COOKIE_DOMAIN)

def require_csrf(req: Request) -> None:
    cookie = req.cookies.get(settings.CSRF_COOKIE_NAME)
    header = req.headers.get("X-CSRF-Token")
    if (not cookie) or (not header) or (cookie != header):
        raise HTTPException(status_code=403, detail="CSRF 에러: 올바르지 않은 접근입니다.")

def get_current_user(req: Request, db: Session) -> User:
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="unauthorized")
    token = auth.split(" ", 1)[1].strip()
    try:
        return auth_service.get_user_from_access(db, token)
    except Exception:
        raise HTTPException(status_code=401, detail="unauthorized")


# ==========================================
# 🛑 기본 계정 API: 회원가입, 로그인, 로그아웃
# ==========================================
@router.post("/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    try:
        auth_service.signup(db, req.username, req.password)
        return {"ok": True}
    except ValueError:
        raise HTTPException(status_code=400, detail="유효하지 않은 요청입니다.")

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, request: Request, res: Response, db: Session = Depends(get_db)):
    ip = request.client.host  

    # 🔒 차단 확인
    try:
        check_block(ip)
    except Exception:
        raise HTTPException(status_code=429, detail="시도 횟수가 너무 많습니다. 잠시 후 다시 시도해주세요.")

    try:
        # 로그인 검증 후 access 토큰 등 발급
        access, refresh, user_id = auth_service.login(db, req.email, req.password)  # req.username -> req.email (Pydantic 맞춰 변경)
        reset_attempts(ip)
    except ValueError:
        record_failure(ip)
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 일치하지 않습니다.")

    csrf = new_csrf_token()
    set_auth_cookies(res, refresh, csrf)

    # 🔥 DB의 실제 이름(name) 컬럼 사용
    user_obj = db.query(User).filter(User.id == int(user_id)).first()
    user_name = (user_obj.name or req.email.split("@")[0]) if user_obj else req.email.split("@")[0]

    return {
        "access_token": access,
        "token_type": "bearer",
        "name": user_name,
        "role": "user"
    }

@router.post("/logout")
def logout(req: Request, res: Response, db: Session = Depends(get_db)):
    require_csrf(req)
    refresh_token = req.cookies.get(settings.REFRESH_COOKIE_NAME)
    if refresh_token:
        auth_service.revoke_refresh(db, refresh_token)
    clear_auth_cookies(res)
    return {"ok": True}

@router.post("/refresh", response_model=TokenResponse)
def refresh(req: Request, res: Response, db: Session = Depends(get_db)):
    require_csrf(req)
    refresh_token = req.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    try:
        new_access, new_refresh = auth_service.rotate_refresh(db, refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    csrf = new_csrf_token()
    set_auth_cookies(res, refresh_token=new_refresh, csrf_token=csrf)
    return {"access_token": new_access, "token_type": "bearer"}

@router.get("/me", response_model=MeResponse)
def me(req: Request, db: Session = Depends(get_db)):
    user = get_current_user(req, db)
    return {"id": user.id, "username": user.username}


# ==========================================
# 🛑 프론트엔드용 API: 토큰 검증, 비밀번호 찾기
# ==========================================

@router.get("/verify")
def verify_token(authorization: str = Header(None), db: Session = Depends(get_db)):
    """프론트엔드(home.py)가 화면 이동 시 토큰의 만료 여부를 묻는 API"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="토큰이 없습니다.")

    token = authorization.split(" ")[1]
    try:
        # ✅ 토큰 생성에 사용한 것과 동일한 키(settings.SECRET_KEY)로 검증
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")

        # DB에서 실제 이름 조회
        user_obj = db.query(User).filter(User.id == int(user_id)).first() if user_id else None
        if not user_obj:
            raise HTTPException(status_code=401, detail="유효하지 않은 인증 정보입니다.")

        user_name = user_obj.name or user_obj.email.split("@")[0]
        return {"name": user_name, "role": "user"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="30분 동안 활동이 없어 자동 로그아웃 되었습니다.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 인증 정보입니다.")


@router.post("/send-reset-email")
def api_send_reset_email(req: ResetEmailRequest, db: Session = Depends(get_db)):
    """이메일 발송 API"""
    # 1. DB에 가입된 이메일인지 검증 (username 컬럼 활용)
    if not auth_service.check_user_exists(db, req.email):
        raise HTTPException(status_code=404, detail="가입되지 않은 이메일입니다. 아이디를 다시 확인해주세요.")
    
    # 2. 이메일 발송 진행
    is_sent, error_msg = auth_service.send_auth_email(req.email, req.auth_code)
    
    if not is_sent:
        raise HTTPException(status_code=500, detail=error_msg)
        
    return {"message": "인증번호 발송 성공"}


@router.post("/reset-password")
def api_reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """비밀번호 재설정 API"""
    success, error_msg = auth_service.update_password(db, req.email, req.new_password)
    
    if not success:
        raise HTTPException(status_code=500, detail=error_msg)
        
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}