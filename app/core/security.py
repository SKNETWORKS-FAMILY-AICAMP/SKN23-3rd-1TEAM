"""
File: security.py
Author: 양창일
Created: 2026-02-15
Description: 암호 만들고 토큰 만들고 검사하는 보안 도구 모음

Modification History:
- 2026-02-15: 초기 생성
"""

import hashlib  # 해시
import secrets  # 랜덤
from datetime import datetime, timedelta, timezone  # 시간
from jose import jwt  # JWT
from passlib.context import CryptContext  # 비번 해시
from app.core.config import settings  # 설정

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")  # Argon2 사용

def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # 비번 해시

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)  # 비번 검증

def new_jti() -> str:
    return secrets.token_hex(16)  # 토큰 고유값

def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)  # CSRF 토큰

def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()  # SHA256

def create_access_token(sub: str) -> str:
    now = datetime.now(timezone.utc)  # 현재
    exp = now + timedelta(minutes=settings.ACCESS_TOKEN_MINUTES)  # 만료
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": exp}  # 최소 클레임
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)  # JWT 발급

def create_refresh_token(sub: str, jti: str) -> str:
    now = datetime.now(timezone.utc)  # 현재
    exp = now + timedelta(days=settings.REFRESH_TOKEN_DAYS)  # 만료
    payload = {"sub": sub, "jti": jti, "iat": int(now.timestamp()), "exp": exp}  # refresh 클레임
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)  # JWT 발급

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])  # JWT 검증/디코드
