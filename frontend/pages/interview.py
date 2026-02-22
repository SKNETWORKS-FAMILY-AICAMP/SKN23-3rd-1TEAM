import sys
import os
import time
import streamlit as st
from streamlit_webrtc import webrtc_streamer

# 1. 경로 해결
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_utils import api_ingest_resume, api_stt_whisper

st.set_page_config(page_title="DeepInterview | AI 면접", page_icon="🎤", layout="wide")

# --- CSS 스타일 (원래 상태 복구) ---
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; }
    .timer-box { background-color: #E9ECEF; border-radius: 12px; padding: 15px; text-align: center; font-size: 32px; font-weight: 800; color: #333; }
    
    /* 채팅 컨테이너 (카카오톡 느낌) */
    .chat-window { 
        background-color: #B2C7D9; 
        border-radius: 30px; 
        padding: 25px; 
        height: 65vh; 
        overflow-y: auto; 
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.1); 
        display: flex;
        flex-direction: column;
    }
    .bubble-ai { background: white; padding: 12px 16px; border-radius: 18px 18px 18px 2px; margin-bottom: 15px; color: black; max-width: 80%; font-size: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); align-self: flex-start; }
    .bubble-user { background: #FEE500; padding: 12px 16px; border-radius: 18px 18px 2px 18px; margin-bottom: 15px; color: black; margin-left: auto; max-width: 80%; font-size: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); align-self: flex-end; }
</style>
""", unsafe_allow_html=True)

# --- 세션 상태 관리 ---
if "messages" not in st.session_state: st.session_state.messages = []
if "running" not in st.session_state: st.session_state.running = False
if "current_q" not in st.session_state: st.session_state.current_q = 0
if "settings" not in st.session_state: st.session_state.settings = None
if "last_audio_hash" not in st.session_state: st.session_state.last_audio_hash = None
if "start_time" not in st.session_state: st.session_state.start_time = None

# 🔥 소요 시간 기록용 세션 변수 추가
if "q_start_time" not in st.session_state: st.session_state.q_start_time = time.time()
if "current_question_text" not in st.session_state: st.session_state.current_question_text = "반갑습니다. 자기소개 부탁드립니다."
if "processing" not in st.session_state: st.session_state.processing = False

# ==========================================
# ⚙️ 설정 모달
# ==========================================
@st.dialog("⚙️ 면접 설정")
def show_settings_modal():
    uploaded_file = st.file_uploader("📄 이력서 업로드 (PDF)", type=["pdf"])
    job_role = st.selectbox("💼 직무", ["Python 백엔드 개발자", "Java 백엔드", "데이터 엔지니어"])
    q_count = st.slider("🔢 문항 수", 3, 10, 5)
    difficulty = st.select_slider("🔥 난이도", options=["주니어", "미들", "시니어"], value="미들")
    
    if st.button("✅ 설정 완료", use_container_width=True):
        if uploaded_file:
            with st.spinner("이력서 분석 중..."):
                api_ingest_resume(uploaded_file)
        st.session_state.settings = {"job_role": job_role, "q_count": q_count, "difficulty": difficulty}
        st.rerun()

# ==========================================
# 🖥️ 레이아웃
# ==========================================
col_left, col_right = st.columns([4, 6], gap="large")

with col_left:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    if st.button("⚙️ Settings", use_container_width=True): show_settings_modal()
    
    webrtc_streamer(key="cam", media_stream_constraints={"video": True, "audio": False})
    
    # ⏱️ 실시간 타이머 (면접 중이면 계속 갱신)
    timer_placeholder = st.empty()
    if st.session_state.running:
        elapsed = int(time.time() - st.session_state.start_time)
        timer_placeholder.markdown(f'<div class="timer-box">{elapsed // 60:02}:{elapsed % 60:02}</div>', unsafe_allow_html=True)
    else:
        timer_placeholder.markdown('<div class="timer-box">00:00</div>', unsafe_allow_html=True)
    
    if not st.session_state.running:
        if st.button("▶️ Start Interview", type="primary", use_container_width=True):
            if not st.session_state.settings: st.error("설정을 먼저 완료하세요!"); st.stop()
            
            # 🚀 DB에 면접 세션 생성 후 session_id 발급받기
            with st.spinner("면접 세션을 준비 중입니다..."):
                from utils.api_utils import api_start_interview
                success, result = api_start_interview(st.session_state.settings["job_role"])
                if success and result and "session_id" in result:
                    st.session_state.session_id = result["session_id"]
                else:
                    st.error(f"세션 발급 실패: {result}")
                    st.stop()
                    
            st.session_state.running = True
            st.session_state.start_time = time.time()
            st.session_state.q_start_time = time.time()
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.current_question_text})
            
            # 첫 시작 시에도 인사말 TTS 오디오 자동 재생을 위한 처리 보강
            st.rerun()
    else:
        if st.button("⏹ Finish", type="secondary", use_container_width=True):
            from utils.api_utils import _handle_request
            if "session_id" in st.session_state:
                _handle_request("POST", "/infer/end", json={"session_id": st.session_state.session_id})
            st.session_state.running = False
            st.switch_page("pages/home.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("💬 Interview Chat")
    
    # ==========================================
    # 💬 1. 채팅 내역 표시 (기존 HTML/CSS 카카오톡 스타일 롤백)
    # ==========================================
    chat_html = '<div class="chat-window">'
    for msg in st.session_state.messages:
        div_class = "bubble-user" if msg["role"] == "user" else "bubble-ai"
        chat_html += f'<div class="{div_class}">{msg["content"]}</div>'
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # ==========================================
    # 🎙️ 2. 사용자 입력 (음성 또는 텍스트)
    # ==========================================
    audio_val = st.audio_input("🎙️ Voice Answer")
    text_val = st.chat_input("⌨️ Type message...")
    
    user_input = None
    if audio_val and not st.session_state.get("processing", False):
        current_hash = hash(audio_val.getvalue())
        if current_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = current_hash
            with st.spinner("음성을 텍스트로 변환 중... (STT)"):
                user_input = api_stt_whisper(audio_val)
    elif text_val:
        user_input = text_val

    # ==========================================
    # 🤖 3. 질문 제출 및 AI 응답 처리
    # ==========================================
    if user_input and st.session_state.running:
        st.session_state.processing = True
        
        # ⏱️ 답변 소요 시간 계산
        response_duration = time.time() - st.session_state.q_start_time
        
        # 3.1 사용자 메시지 즉시 세션에 추가
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun() # 사용자 메시지를 화면에 띄우기 위해 리런

    # ==========================================
    # 💡 4. AI 답변 필요 여부 확인 (채팅 맨 끝이 user일 때)
    # ==========================================
    if st.session_state.running and st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and st.session_state.processing:
        with st.spinner("*(면접관이 답변을 분석하고 다음 질문을 생각하는 중입니다...)* 🧐"):
            from utils.api_utils import api_get_next_question_v2
            
            payload = {
                **st.session_state.settings,
                "answer": st.session_state.messages[-1]["content"],
                "current_question": st.session_state.current_question_text,
                "session_id": st.session_state.get("session_id")
            }
            # 첫 번째 요소의 시간은 이미 지났으므로 근사치 소요시간 전달
            payload["response_time"] = int(time.time() - st.session_state.q_start_time)
            
            success, result = api_get_next_question_v2(payload)
            if success:
                ai_msg = result.get("answer", "알 수 없는 응답입니다.")
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                
                # 🔄 세션 갱신
                st.session_state.current_question_text = ai_msg
                st.session_state.q_start_time = time.time()
                st.session_state.current_q += 1

                # TTS 음성 생성 (백엔드 요청)
                from utils.api_utils import api_tts_service
                st.session_state.latest_audio = api_tts_service(ai_msg)
            else:
                st.error("AI 면접관 서버와 연결이 끊어졌습니다.")
                
        st.session_state.processing = False
        st.rerun()

    # 🔊 TTS 자동 재생 부 (렌더링 흐름 밖에서 보존)
    if st.session_state.get("latest_audio"):
        st.audio(st.session_state.latest_audio, format="audio/mp3", autoplay=True)
        # 한번 오디오를 띄우면 변수 해제 (중복재생 방지)
        st.session_state.latest_audio = None
    st.markdown('</div>', unsafe_allow_html=True)

# 타이머 실시간 갱신을 위한 루프
if st.session_state.running:
    time.sleep(1)
    st.rerun()