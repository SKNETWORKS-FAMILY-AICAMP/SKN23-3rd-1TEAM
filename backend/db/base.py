"""
File: base.py
Author: 양창일
Created: 2026-02-15
Description: DB 모델들의 기본 뼈대

Modification History:
- 2026-02-15: 초기 생성
- 2026-02-22 (김지우) : 벡엔드 DB 모델 정의 - 기존 User 모델 외에 직무 분류, 질문 풀, 면접 기록 테이블 추가
"""

from sqlalchemy.orm import DeclarativeBase  # 베이스 클래스

class Base(DeclarativeBase):  # ORM 베이스
    pass  # 확장용


from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from backend.db.session import Base
from datetime import datetime

# 1. 직무 분류 테이블 (Python, Java, 네트워크 등 확장용)
class JobCategory(Base):
    __tablename__ = "job_categories"
    id = Column(Integer, primary_key=True, index=True)
    main_category = Column(String(50))  # 예: 개발, 인프라
    sub_category = Column(String(50))   # 예: 백엔드, 프론트엔드
    target_role = Column(String(50))    # 예: Java 개발자, Python 개발자

# 2. 질문 저장소 테이블 (CSV 마이그레이션 및 GPT 증폭용)
class QuestionPool(Base):
    __tablename__ = "question_pool"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("job_categories.id"))
    question_type = Column(String(30))  # 인성, 기술, 상황
    skill_tag = Column(String(100))     # Java, Spring, Docker 등
    difficulty = Column(String(20))     # 주니어, 미들, 시니어
    content = Column(Text)              # 질문 내용
    reference_answer = Column(Text)     # 모범 답안 (AI 채점 기준)
    keywords = Column(String(255))      # 반드시 포함되어야 할 키워드 (쉼표 구분)

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime, func

# 3. 면접 세션 요약 테이블
class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    job_role = Column(String(50))
    total_score = Column(Float, default=0.0)
    status = Column(String(20), default="START")
    created_at = Column(DateTime, default=func.now())

# 4. 개별 문항 상세 기록 테이블 (STT 답변 및 채점 결과)
class InterviewDetail(Base):
    __tablename__ = "interview_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"))
    question_text = Column(Text)
    answer_text = Column(Text)          # STT로 변환된 답변
    response_time = Column(Integer)     # 답변 소요 시간 (초)
    score = Column(Float)               # 해당 문항 점수
    feedback = Column(Text)             # AI 개별 피드백
    sentiment_score = Column(Float)     # 자신감 수치