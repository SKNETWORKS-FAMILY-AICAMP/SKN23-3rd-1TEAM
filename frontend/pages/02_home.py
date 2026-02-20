import streamlit as st
from datetime import datetime
import time
from streamlit_webrtc import webrtc_streamer

# --- 페이지 설정 ---
st.set_page_config(page_title="DeepInterview", page_icon="🎤", layout="wide")

st.markdown("""
<style>
/* 전체 앱 여백 및 불필요한 UI 제거 */
.stApp { background-color: #F8F9FA; }
.block-container { padding: 2rem 3rem !important; max-width: 1400px !important; }
#MainMenu, footer, header {visibility: hidden;}
[data-testid="stToolbar"] {display: none;}

/* 타이머 디자인 */
.timer-box {
    background-color: #E9ECEF;
    border-radius: 10px;
    padding: 15px;
    text-align: center;
    font-size: 35px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #333;
}

/* 요약 대시보드 카드 디자인 */
.summary-card {
    background-color: white;
    border-left: 5px solid #8B5CF6;
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 상태 관리 (Session State)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "running" not in st.session_state:
    st.session_state.running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "current_q" not in st.session_state:
    st.session_state.current_q = 1
if "settings" not in st.session_state:
    st.session_state.settings = None
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None

# 🔥 시작 버튼을 눌렀을 때 발동하는 함수
def toggle_timer():
    if not st.session_state.settings:
        st.warning("먼저 ⚙️ 면접 설정을 완료해주세요!")
        return
        
    if not st.session_state.running:
        st.session_state.start_time = time.time()
        st.session_state.running = True
        
        # 시작과 동시에 AI가 첫 질문 던지기!
        if len(st.session_state.messages) == 0:
            job = st.session_state.settings['job_role']
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"반갑습니다. {job} 포지션에 지원해 주셔서 감사합니다. 먼저 간단한 자기소개 부탁드립니다.", 
                "time": datetime.now().strftime("%H:%M")
            })

# ==========================================
# ⚙️ 모달 1: 면접 설정 및 준비
# ==========================================
@st.dialog("⚙️ 면접 설정 및 준비")
def show_settings_modal():
    st.write("면접에 필요한 기본 정보를 설정합니다.")
    st.divider()
    
    uploaded_file = st.file_uploader("📄 이력서 업로드 (PDF)", type=["pdf"])
    q_count = st.slider("🔢 문제 개수", min_value=3, max_value=10, value=5)
    difficulty = st.pills("🔥 문제 난이도", options=["상 (시니어)", "중 (미들)", "하 (주니어)"], default="중 (미들)")
    job_role = st.selectbox("💼 지원 직무", ["Python 백엔드 개발자", "Java 백엔드", "데이터 엔지니어", "AI 리서처"])
    
    st.divider()
    if st.button("✅ 적용하기", use_container_width=True, type="primary"):
        st.session_state.settings = {
            "has_resume": uploaded_file is not None,
            "resume_name": uploaded_file.name if uploaded_file else "미제출",
            "q_count": q_count,
            "difficulty": difficulty,
            "job_role": job_role
        }
        st.rerun()

# ==========================================
# 🛑 모달 2: 면접 종료 및 저장 동의 (새로 추가됨!)
# ==========================================
@st.dialog("🛑 면접 종료 및 결과 확인")
def show_end_modal():
    st.markdown("### 면접이 모두 종료되었습니다.")
    st.write("고생하셨습니다. AI 면접관이 결과를 분석할 준비를 마쳤습니다.")
    
    st.divider()
    
    # 디테일 끝판왕: 저장 동의 체크박스
    st.markdown("<span style='font-size: 13px; color: gray;'>마이페이지 복습 및 AI 학습을 위해 녹음된 음성 및 텍스트 데이터를 서버에 저장하시겠습니까?</span>", unsafe_allow_html=True)
    save_agree = st.checkbox("✅ 녹음 내용 및 면접 데이터 저장에 동의합니다.")
    
    if st.button("확인 (결과 보기)", type="primary", use_container_width=True):
        if save_agree:
            st.success("데이터가 안전하게 저장되었습니다. 결과 페이지로 이동합니다...")
        else:
            st.info("데이터를 저장하지 않고 결과 페이지로 이동합니다...")
        
        time.sleep(1.5)
        st.switch_page("./page2.py") # 🚀 페이지 이동

# ==========================================
# 🖥️ 화면 레이아웃 분할 (좌측 4 : 우측 6)
# ==========================================
col_left, col_right = st.columns([4, 6], gap="large")

# ---------------------------------------------------------
# ⬅️ 좌측 영역
# ---------------------------------------------------------
with col_left:
    st.markdown("### 📋 면접 대기실")
    
    if st.button("⚙️ 면접 설정 열기", use_container_width=True):
        show_settings_modal()
        
    if st.session_state.settings:
        s = st.session_state.settings
        st.markdown(f"""
        <div class="summary-card">
            <h4 style="margin-top:0;">✅ 설정 완료</h4>
            <b>💼 직무:</b> {s['job_role']}<br>
            <b>🔥 난이도:</b> {s['difficulty']}<br>
            <b>🔢 문항 수:</b> 총 {s['q_count']}개<br>
            <b>📄 이력서:</b> {s['resume_name']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("👆 위 버튼을 눌러 면접 설정을 완료해주세요.")

    st.markdown("#### 📸 지원자 웹캠 화면")
    webrtc_streamer(
        key="candidate_cam", 
        media_stream_constraints={"video": True, "audio": False} 
    )
    
    st.write("") 

    t_col1, t_col2 = st.columns([1, 1])
    
    with t_col1:
        elapsed = int(time.time() - st.session_state.start_time) if st.session_state.running else 0
        minutes, seconds = elapsed // 60, elapsed % 60
        st.markdown(f'<div class="timer-box">{minutes:02}:{seconds:02}</div>', unsafe_allow_html=True)
        
    with t_col2:
        st.write("")
        # 🔥 버튼 로직 분기: 실행 중일 땐 종료 모달, 대기 중일 땐 타이머 시작
        if st.session_state.running:
            if st.button("⏹ 끝내기 (정지)", use_container_width=True, type="secondary"):
                show_end_modal()
        else:
            st.button("▶️ 시작하기", on_click=toggle_timer, use_container_width=True, type="primary")

    if st.session_state.running:
        time.sleep(1)
        st.rerun()

# ---------------------------------------------------------
# ➡️ 우측 영역: AI 면접관 실시간 채팅
# ---------------------------------------------------------
with col_right:
    total_q = st.session_state.settings["q_count"] if st.session_state.settings else 5
    job_role_display = st.session_state.settings["job_role"] if st.session_state.settings else "Python 백엔드 개발자"
    
    st.markdown(f"**현재 진행률: 질문 {st.session_state.current_q} / {total_q}**")
    st.progress(st.session_state.current_q / total_q)
    
    st.markdown("""
    <style>
    [data-testid="column"]:nth-of-type(2) {
        background-color: #B2C7D9 !important;
        border-radius: 20px;
        padding: 20px !important;
        height: 85vh;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        position: relative;
    }
    .chat-container { height: 55vh; overflow-y: auto; padding-right: 10px; margin-bottom: 10px; }
    .chat-container::-webkit-scrollbar { width: 6px; }
    .chat-container::-webkit-scrollbar-thumb { background-color: rgba(0,0,0,0.2); border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        st.markdown(f"""
            <div style="margin:10px 0; text-align:left">
                <div style="font-size:12px; margin-bottom:4px; color:#333;">🤖 AI 면접관 ({job_role_display})</div>
                <div style="display:inline-block; background:white; padding:12px 18px; border-radius:20px; max-width:80%;">
                    안녕하세요! 설정을 마치셨다면 하단의 <b>[시작하기]</b>를 누른 뒤, 마이크나 텍스트로 답변해주세요.
                </div>
            </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        role, time_str = msg["role"], msg.get("time", datetime.now().strftime("%H:%M"))
        if role == 'user':
            st.markdown(f"""
                <div style="margin:15px 0; text-align:right">
                    <div style="display:inline-block; background:#FEE500; padding:12px 18px; border-radius:20px; max-width:80%; font-size:15px; color:#111; text-align:left;">
                        {msg["content"]}
                    </div>
                    <div style="font-size:11px; color:#555; margin-top:5px;">{time_str}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="margin:15px 0; text-align:left">
                    <div style="font-size:12px; margin-bottom:4px; color:#333;">🤖 AI 면접관</div>
                    <div style="display:inline-block; background:white; padding:12px 18px; border-radius:20px; max-width:80%; font-size:15px; color:#111; text-align:left;">
                        {msg["content"]}
                    </div>
                    <div style="font-size:11px; color:#555; margin-top:5px;">{time_str}</div>
                </div>
            """, unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================
    # 🎙️ STT 마이크 및 텍스트 혼합 입력부
    # =========================================================
    final_prompt = None
    
    audio_value = st.audio_input("🎙️ 마이크로 답변하기")
    
    if audio_value is not None:
        audio_id = hash(audio_value.getvalue())
        if audio_id != st.session_state.last_audio_id:
            st.session_state.last_audio_id = audio_id
            final_prompt = "🎤 (음성 인식됨) 제가 그 프로젝트에서 주로 담당했던 부분은 데이터베이스 아키텍처 설계와 쿼리 최적화였습니다."

    text_prompt = st.chat_input("⌨️ 텍스트로 답변하기...")
    if text_prompt:
        final_prompt = text_prompt

    if final_prompt:
        if not st.session_state.running:
            st.warning("타이머 [시작하기] 버튼을 먼저 눌러주세요!")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": final_prompt, "time": datetime.now().strftime("%H:%M")})
        
        if st.session_state.current_q < total_q:
            st.session_state.current_q += 1
            
        with st.spinner("AI 면접관이 답변을 분석 중입니다..."):
            time.sleep(1.5)
            ai_response = f"'{final_prompt}'라는 답변 잘 들었습니다. 데이터베이스 아키텍처 설계 시 가장 중요하게 고려한 점은 무엇인가요?"
            st.session_state.messages.append({"role": "assistant", "content": ai_response, "time": datetime.now().strftime("%H:%M")})
        
        st.rerun()