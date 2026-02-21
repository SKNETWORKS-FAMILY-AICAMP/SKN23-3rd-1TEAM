"""
File: rag_service.py
Author: 김지우
Created: 2026-02-21
Description: 이력서(PDF)를 텍스트로 쪼개서 ChromaDB에 넣고, 
             면접 중 실시간 대화를 DB에 추가(Append)하며, 
             필요할 때 관련된 내용을 검색해서 꺼내주는 데이터 관리 전담 파일

Modification History:
- 2026-02-21: 초기 생성
"""
# 터미널 설치 필수: pip install langchain langchain-community langchain-openai chromadb pdfplumber
import os
import pdfplumber
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

class RAGService:
    def __init__(self, persist_dir="./chroma_db"):
        """
        RAG 서비스 초기화: 임베딩 모델과 벡터 DB(Chroma) 세팅
        """
        # OpenAI API 키가 환경변수(.env)에 있어야 합니다.
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.persist_dir = persist_dir
        
        # ChromaDB 연결
        self.vector_db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings
        )
        
        # 텍스트 청킹(쪼개기) 설정
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, 
            chunk_overlap=50
        )

    # ==========================================
    # 📄 1. 이력서 PDF 전처리 및 DB 주입 (Init)
    # ==========================================
    def process_resume(self, pdf_file_path: str, session_id: str):
        """
        지원자의 이력서를 파싱하여 벡터 DB에 저장합니다.
        session_id를 메타데이터로 달아 다른 지원자 데이터와 섞이지 않게 합니다.
        """
        raw_text = ""
        try:
            with pdfplumber.open(pdf_file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        raw_text += extracted + "\n"
        except Exception as e:
            print(f"❌ PDF 파싱 에러: {e}")
            return False

        if not raw_text.strip():
            return False

        chunks = self.text_splitter.split_text(raw_text)
        
        # 메타데이터에 session_id를 넣어서 '누구의 이력서인지' 식별
        metadatas = [{"source": "resume", "session_id": session_id} for _ in chunks]
        
        self.vector_db.add_texts(texts=chunks, metadatas=metadatas)
        print(f"✅ [{session_id}] 이력서 데이터 {len(chunks)}개 청크 저장 완료!")
        return True

    # ==========================================
    # 🔄 2. 동적 RAG: 실시간 면접 답변 DB 추가
    # ==========================================
    def append_interview_log(self, session_id: str, question: str, user_answer: str, turn: int):
        """
        면접 중에 지원자가 한 대답을 실시간으로 DB에 꽂아 넣습니다. (100점짜리 치트키 🔥)
        """
        log_text = f"[면접관]: {question}\n[지원자]: {user_answer}"
        metadata = {
            "source": "live_interview", 
            "session_id": session_id,
            "turn": turn
        }
        
        self.vector_db.add_texts(texts=[log_text], metadatas=[metadata])
        print(f"🔄 [{session_id}] {turn}턴 째 대화 기록 실시간 임베딩 완료!")

    # ==========================================
    # 🔍 3. RAG 검색 (LLM이 꼬리 질문을 만들기 전 호출)
    # ==========================================
    def retrieve_context(self, session_id: str, query: str, k: int = 3):
        """
        현재 세션(지원자)의 이력서와 과거 면접 답변 중, 현재 질문(query)과 가장 관련된 데이터를 찾습니다.
        """
        # DB가 비어있으면 에러 방지
        if self.vector_db._collection.count() == 0:
            return ""

        # 해당 session_id를 가진 데이터만 검색 (다른 사람 이력서 섞임 방지)
        results = self.vector_db.similarity_search(
            query, 
            k=k,
            filter={"session_id": session_id} # 🔥 보안의 핵심: 내 데이터만 검색!
        )
        
        # 찾은 결과들을 하나의 문자열로 엮어서 반환
        context_str = "\n\n".join([f"({res.metadata.get('source')} 참고) {res.page_content}" for res in results])
        return context_str

# FastAPI에서 언제든 불러다 쓸 수 있도록 싱글톤(Singleton) 객체로 하나 만들어 둡니다.
rag_service = RAGService()