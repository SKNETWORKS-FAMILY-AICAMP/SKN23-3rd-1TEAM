"""
File: social_service.py
Author: 양창일
Created: 2026-02-15
Description: 소셜 로그인

Modification History:
- 2026-02-16: 초기 생성
"""


import requests  # HTTP 호출
from sqlalchemy.orm import Session  # DB 세션
from app.core.config import settings  # 설정
from app.models.user import User  # 유저 모델

def _require(value: str, name: str) -> str:
    if not value:
        raise ValueError(f"missing {name}")
    return value

def get_or_create_social_user(db: Session, provider: str, provider_user_id: str, email: str | None) -> User:
    user = (
        db.query(User)
        .filter(User.provider == provider, User.provider_user_id == provider_user_id)
        .first()
    )
    if user:
        if (not user.email) and email:
            user.email = email
            db.add(user)
            db.commit()
        return user

    # 내부 username은 중복 피하려고 provider 기반으로 만든다
    base_username = f"{provider}_{provider_user_id}"
    username = base_username[:64]

    # 없으면 새로 생성
    user = User(
        username=username,
        password_hash=None,
        provider=provider,
        provider_user_id=provider_user_id,
        email=email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Kakao
def kakao_exchange_code_for_token(code: str) -> str:
    _require(settings.KAKAO_CLIENT_ID, "KAKAO_CLIENT_ID")
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_CLIENT_ID,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "code": code,
    }
    if settings.KAKAO_CLIENT_SECRET:
        data["client_secret"] = settings.KAKAO_CLIENT_SECRET

    resp = requests.post(url, data=data, timeout=10)
    resp.raise_for_status()
    j = resp.json()
    return j["access_token"]

def kakao_fetch_profile(access_token: str) -> tuple[str, str | None]:
    url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    j = resp.json()
    provider_user_id = str(j["id"])
    email = None
    kakao_account = j.get("kakao_account") or {}
    email = kakao_account.get("email")
    return provider_user_id, email

# Google
def google_exchange_code_for_token(code: str) -> str:
    _require(settings.GOOGLE_CLIENT_ID, "GOOGLE_CLIENT_ID")
    _require(settings.GOOGLE_CLIENT_SECRET, "GOOGLE_CLIENT_SECRET")
    url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    resp = requests.post(url, data=data, timeout=10)
    resp.raise_for_status()
    j = resp.json()
    return j["access_token"]

def google_fetch_profile(access_token: str) -> tuple[str, str | None]:
    # 실서비스에서는 id_token 검증(서명/iss/aud)까지 하는 게 더 안전함
    url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    j = resp.json()
    provider_user_id = str(j.get("id"))
    email = j.get("email")
    return provider_user_id, email

# Naver
def naver_exchange_code_for_token(code: str, state: str) -> str:
    _require(settings.NAVER_CLIENT_ID, "NAVER_CLIENT_ID")
    _require(settings.NAVER_CLIENT_SECRET, "NAVER_CLIENT_SECRET")
    url = "https://nid.naver.com/oauth2.0/token"
    params = {
        "grant_type": "authorization_code",
        "client_id": settings.NAVER_CLIENT_ID,
        "client_secret": settings.NAVER_CLIENT_SECRET,
        "code": code,
        "state": state,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    j = resp.json()
    return j["access_token"]

def naver_fetch_profile(access_token: str) -> tuple[str, str | None]:
    url = "https://openapi.naver.com/v1/nid/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    j = resp.json()
    res = j.get("response") or {}
    provider_user_id = str(res.get("id"))
    email = res.get("email")
    return provider_user_id, email
