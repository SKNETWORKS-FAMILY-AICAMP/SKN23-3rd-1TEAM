"""
File: rag_service.py
Author: 김지우
Created: 2026-02-21
Description: 이력서(PDF)를 텍스트로 쪼개서 ChromaDB에 넣고, 
             면접 중 실시간 대화를 DB에 추가(Append)하며, 
             필요할 때 관련된 내용을 검색해서 꺼내주는 데이터 관리 전담 파일

Modification History:
- 2026-02-21: 초기 생성
- 2026-02-22: Vector DB(Chroma) 관리 + 실시간 대화 기록(Append) + GPT-4.1-mini 면접 로직 통합
"""
import os
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.db import base # 질문 DB 참조를 위해 추가

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class InterviewAIService:
    def __init__(self, persist_dir="./chroma_db"):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.persist_dir = persist_dir
        # 요청하신 모델 명칭 유지
        self.llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.vector_db = Chroma(persist_directory=self.persist_dir, embedding_function=self.embeddings)

    def ingest_resume(self, file_path: str, session_id: str):
        loader = PyPDFLoader(file_path)
        docs = loader.load_and_split(self.text_splitter)
        for doc in docs:
            doc.metadata = {"source": "resume", "session_id": session_id}
        self.vector_db.add_documents(docs)
        print(f"✅ [{session_id}] 이력서 학습 완료")

    # ==========================================
    # 🔍 누락되었던 검색 함수 추가
    # ==========================================
    def retrieve_context(self, session_id: str, query: str, k: int = 3):
        """세션별 이력서 및 대화 기록 검색"""
        results = self.vector_db.similarity_search(
            query, k=k, filter={"session_id": session_id}
        )
        return "\n\n".join([f"({res.metadata.get('source')}) {res.page_content}" for res in results])

    # ==========================================
    # 🎯 500개 질문 DB와 이력서 매칭 로직 완성
    # ==========================================
    def get_relevant_question_from_db(self, session_id, db_session, job_role):
        """이력서 내용과 가장 유사한 기술 질문을 500개 풀에서 찾아 반환"""
        # 1. 이력서에서 기술 스택 컨텍스트 추출
        resume_context = self.retrieve_context(session_id, query="기술 스택 및 프로젝트 경험", k=2)
        
        # 2. DB에서 해당 직무의 질문들을 가져옴
        all_questions = db_session.query(base.QuestionPool).join(base.JobCategory).filter(
            base.JobCategory.target_role == job_role
        ).all()

        if not all_questions:
            return "관련 직무 질문을 찾을 수 없습니다."

        # 3. GPT를 사용하여 이력서와 가장 매칭되는 질문 1개 선정
        q_list = "\n".join([f"- {q.content}" for q in all_questions[:20]]) # 성능상 20개로 제한
        prompt = f"이력서 내용: {resume_context}\n\n질문 리스트:\n{q_list}\n\n위 질문 중 이력서와 가장 관련 깊은 질문 딱 하나만 골라서 질문 내용만 출력해."
        
        selected_q = self.llm.invoke(prompt)
        return selected_q.content

    def append_interview_log(self, session_id: str, question: str, user_answer: str):
        log_text = f"[면접관]: {question}\n[지원자]: {user_answer}"
        metadata = {"source": "live_interview", "session_id": session_id}
        self.vector_db.add_texts(texts=[log_text], metadatas=[metadata])

    def generate_interview_response(self, session_id, user_answer, settings):
        context = self.retrieve_context(session_id, user_answer, k=3)
        prompt = f"""
        당신은 {settings['job_role']} 전문 면접관입니다. (난이도: {settings['difficulty']})
        지원자의 답변: "{user_answer}"
        참고 컨텍스트: {context}
        
        지시사항:
        1. 답변이 이력서와 일치하는지 확인하고 날카로운 기술 검증 질문을 하세요.
        2. 형식: [점수] | [자신감] | [피드백] | [다음질문]
        """
        response = self.llm.invoke(prompt)
        return response.content

    def stt_whisper(self, audio_file):
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text

    def tts_voice(self, text: str):
        """텍스트를 OpenAI TTS를 사용하여 음성(바이너리)으로 변환"""
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy", # 기본 남성/여성 중립적 목소리
            input=text
        )
        return response.content

_instance = None
def get_ai_service():
    global _instance
    if _instance is None:
        _instance = InterviewAIService()
    return _instance