"""
File: auth_schema.py
Author: 양창일
Created: 2026-02-15
Description: 로그인 관련 데이터 모양 정의

Modification History:
- 2026-02-15: 초기 생성
"""

from pydantic import BaseModel, Field  # 스키마

class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)  # 유저명
    password: str = Field(min_length=8, max_length=128)  # 비번

class LoginRequest(BaseModel):
    username: str  # 유저명
    password: str  # 비번

class TokenResponse(BaseModel):
    access_token: str  # 액세스 토큰
    token_type: str = "bearer"  # 타입

class MeResponse(BaseModel):
    id: int  # 유저 ID
    username: str  # 유저명
