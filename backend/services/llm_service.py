"""
File: llm_service.py
Author: 양창일 (초기 뼈대) / 1팀 (고도화)
Created: 2026-02-15
Description: LangChain 및 RAG 기반 AI 면접관 핵심 두뇌 로직 (꼬리 질문 생성)

Modification History:
- 2026-02-15 (양창일): 초기 생성 및 기본 텍스트 생성 뼈대 구축
- 2026-02-20 (김지우): 비동기(Async) ChatOpenAI 적용, 프롬프트 엔지니어링 및 RAG(ChromaDB) 연동으로 전면 개편
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.services.rag_service import rag_service  # 👈 사서(RAG) 호출


class LLMService:
    def __init__(self):
        """
        AI 면접관 초기화: 약간의 창의성(temperature)을 주어 뻔하지 않은 질문을 유도합니다.
        """
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

        # 🔥 압박 면접관 프롬프트 엔지니어링
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """당신은 {job_role} 직무의 10년 차 최고참 실무 면접관입니다.
            지원자의 답변을 평가하고, 아래 제공된 [참고 데이터(이력서 및 과거 답변)]를 바탕으로 
            지원자의 진짜 실력을 검증할 수 있는 '날카로운 꼬리 질문'을 딱 1개만 생성하세요.
            
            [참고 데이터]
            {context}
            
            [면접관 지침]
            1. 지원자의 답변이 훌륭하다면, 사용된 기술의 내부 동작 원리나 심화 트러블슈팅을 물어보세요.
            2. 지원자의 답변이 부족하거나 모순이 있다면, 그 부분을 예리하게 파고드세요.
            3. 인터넷에 널려있는 뻔한 질문(예: 장단점이 뭔가요?)은 절대 금지합니다.
            4. 대화하듯 자연스러운 구어체로 질문만 출력하세요.""",
                ),
                (
                    "human",
                    "지원자의 방금 답변: {user_answer}\n\n이 답변에 대한 평가를 속으로 진행하고, 다음 꼬리 질문을 던져주세요.",
                ),
            ]
        )

        self.chain = self.prompt | self.llm

    # ==========================================
    # 🎯 꼬리 질문 생성 메인 함수 (FastAPI 라우터에서 호출)
    # ==========================================
    async def generate_tail_question(
        self,
        session_id: str,
        job_role: str,
        current_question: str,
        user_answer: str,
        turn: int,
    ):
        """
        지원자의 답변을 바탕으로 맞춤형 꼬리 질문을 비동기(Async)로 생성합니다.
        """
        # 1. 동적 RAG: 방금 대답을 DB에 기억시킴
        rag_service.append_interview_log(
            session_id, current_question, user_answer, turn
        )

        # 2. RAG 검색: 이력서와 과거 대답에서 단서 찾기
        context = rag_service.retrieve_context(session_id, user_answer, k=3)

        # 3. LLM 추론: 프롬프트에 엮어서 발사!
        response = await self.chain.ainvoke(
            {"job_role": job_role, "context": context, "user_answer": user_answer}
        )

        return response.content


# FastAPI 라우터에서 쉽게 가져다 쓸 수 있도록 객체 생성
llm_service = LLMService()
