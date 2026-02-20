"""
File: base.py
Author: 양창일
Created: 2026-02-15
Description: DB 모델들의 기본 뼈대

Modification History:
- 2026-02-15: 초기 생성
"""

from sqlalchemy.orm import DeclarativeBase  # 베이스 클래스

class Base(DeclarativeBase):  # ORM 베이스
    pass  # 확장용
