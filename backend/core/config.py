"""
File: config.py
Author: 양창일
Created: 2026-02-15
Description: # 기본 설정

Modification History:
- 2026-02-15: 초기 생성
"""

import os
from pydantic import BaseModel
from dotenv import load_dotenv

class Settings(BaseModel):
<<<<<<< HEAD
    DATABASE_URL: str = os.getenv("DATABASE_URL", "").strip()
=======
    load_dotenv()

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
>>>>>>> 3266b1e9f74b438985b9c6640f00b53ce80b4111
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-super-long-random")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = 30
    REFRESH_TOKEN_DAYS: int = 14
    REFRESH_COOKIE_NAME: str = "refresh_token"
    CSRF_COOKIE_NAME: str = "csrf_token"
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "lax")
    COOKIE_DOMAIN: str | None = os.getenv("COOKIE_DOMAIN") or None

    BACKEND_BASE_URL: str = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")

    KAKAO_CLIENT_ID: str = os.getenv("KAKAO_CLIENT_ID", "")
    KAKAO_CLIENT_SECRET: str = os.getenv("KAKAO_CLIENT_SECRET", "")

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

    NAVER_CLIENT_ID: str = os.getenv("NAVER_CLIENT_ID", "")
    NAVER_CLIENT_SECRET: str = os.getenv("NAVER_CLIENT_SECRET", "")

    WORKNET_URL_BASE: str = os.getenv("WORKNET_URL_BASE")
    WORKNET_API_KEY: str = os.getenv("WORKNET_API_KEY")
    WORKNET_TIMEOUT_SEC: int = 10

    @property
    def FRONTEND_REDIRECT_URL(self) -> str:
        return f"{self.FRONTEND_BASE_URL}/social/callback"

    @property
    def KAKAO_REDIRECT_URI(self) -> str:
        return os.getenv(
            "KAKAO_REDIRECT_URI",
            f"{self.BACKEND_BASE_URL}/api/auth/kakao/callback",
        )

    @property
    def GOOGLE_REDIRECT_URI(self) -> str:
        return os.getenv(
            "GOOGLE_REDIRECT_URI",
            f"{self.BACKEND_BASE_URL}/api/auth/google/callback",
        )

    @property
    def NAVER_REDIRECT_URI(self) -> str:
        return f"{self.BACKEND_BASE_URL}/api/auth/naver/callback"

settings = Settings()
