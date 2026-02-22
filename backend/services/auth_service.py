"""
File: auth_service.py
Author: 양창일
Created: 2026-02-15
Description: 로그인과 토큰을 실제로 처리하는 코드

Modification History:
- 2026-02-15: 초기 생성
"""

from sqlalchemy.orm import Session  # 세션
from datetime import datetime, timezone, timedelta  # 시간
from backend.models.user import User  # 유저
from backend.models.refresh_token import RefreshToken  # 리프레시 저장
from backend.core.security import (
    hash_password, verify_password, new_jti, sha256_hex,
    create_access_token, create_refresh_token, decode_token
)  # 보안 유틸
from backend.core.config import settings  # 설정

def signup(db: Session, username: str, password: str) -> None:
    exists = db.query(User).filter(User.username == username).first()  # 중복 확인
    if exists:
        raise ValueError("invalid credentials")  # 계정열거 방지용 동일 메세지
    user = User(username=username, password_hash=hash_password(password))  # 유저 생성
    db.add(user)  # 추가
    db.commit()  # 커밋

def login(db: Session, username: str, password: str) -> tuple[str, str, str]:
    user = db.query(User).filter(User.username == username).first()  # 유저 조회

    # 소셜 유저(password_hash=None)는 로컬 로그인 불가
    if (not user) or (not user.password_hash) or (not verify_password(password, user.password_hash)):  # 검증
        raise ValueError("invalid credentials")  # 동일 응답(계정열거 방지)

    access = create_access_token(sub=str(user.id))  # access 발급
    jti = new_jti()  # refresh id
    refresh = create_refresh_token(sub=str(user.id), jti=jti)  # refresh 발급

    exp = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_DAYS)  # 만료
    row = RefreshToken(user_id=user.id, jti=jti, token_hash=sha256_hex(refresh), expires_at=exp)  # DB 저장(해시)
    db.add(row)  # 추가
    db.commit()  # 커밋

    return access, refresh, str(user.id)  # 반환


def rotate_refresh(db: Session, refresh_token: str) -> tuple[str, str]:
    payload = decode_token(refresh_token)  # 검증
    user_id = int(payload.get("sub"))  # 소유자
    jti = payload.get("jti")  # 토큰 ID
    if not jti:
        raise ValueError("invalid token")  # 실패

    row = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()  # DB 조회
    if (not row) or (row.revoked_at is not None):  # 없거나 폐기됨
        raise ValueError("invalid token")  # 실패
    if row.token_hash != sha256_hex(refresh_token):  # 토큰 불일치(탈취/재사용)
        raise ValueError("invalid token")  # 실패
    if row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):  # 만료
        raise ValueError("invalid token")  # 실패

    row.revoked_at = datetime.now(timezone.utc)  # 기존 refresh 폐기(회전)
    db.add(row)  # 반영

    new_access = create_access_token(sub=str(user_id))  # 새 access
    new_jti = new_jti()  # 새 jti
    new_refresh = create_refresh_token(sub=str(user_id), jti=new_jti)  # 새 refresh

    exp = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_DAYS)  # 만료
    db.add(RefreshToken(user_id=user_id, jti=new_jti, token_hash=sha256_hex(new_refresh), expires_at=exp))  # 저장
    db.commit()  # 커밋

    return new_access, new_refresh  # 반환

def revoke_refresh(db: Session, refresh_token: str) -> None:
    try:
        payload = decode_token(refresh_token)  # 디코드
        jti = payload.get("jti")  # jti
    except Exception:
        return  # 토큰이 이미 이상하면 그냥 무시(정보노출 방지)

    if not jti:
        return  # 없음

    row = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()  # 조회
    if row and row.revoked_at is None:
        row.revoked_at = datetime.now(timezone.utc)  # 폐기
        db.add(row)  # 반영
        db.commit()  # 커밋

def get_user_from_access(db: Session, access_token: str) -> User:
    payload = decode_token(access_token)  # 검증
    sub = payload.get("sub")  # user id
    if not sub:
        raise ValueError("invalid token")  # 실패
    user = db.query(User).filter(User.id == int(sub)).first()  # 유저 조회
    if not user:
        raise ValueError("invalid token")  # 실패
    return user  # 반환

def issue_tokens_for_user_id(db: Session, user_id: int) -> tuple[str, str]:
    access = create_access_token(sub=str(user_id))  # access 발급
    jti = new_jti()  # refresh jti
    refresh = create_refresh_token(sub=str(user_id), jti=jti)  # refresh 발급

    exp = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_DAYS)  # 만료
    row = RefreshToken(user_id=user_id, jti=jti, token_hash=sha256_hex(refresh), expires_at=exp)  # DB 저장
    db.add(row)  # 추가
    db.commit()  # 커밋

    return access, refresh  # 반환