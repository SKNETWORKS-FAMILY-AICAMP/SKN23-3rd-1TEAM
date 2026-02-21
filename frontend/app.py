"""
File: app.py
Author: 김지우
Created: 2026-02-20
Description: 로그인 화면

Modification History:
- 2026-02-20: 초기 생성
"""
# pip install streamlit python-dotenv authlib requests

# 초기 화면 (로그인창)
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")

st.set_page_config(page_title="로그인", page_icon="🔐", layout="centered")

if "access_token" not in st.session_state:
    st.session_state.access_token = None

social_token = st.query_params.get("access_token")
if social_token:
    st.session_state.access_token = social_token
    st.query_params.clear()
    st.switch_page("pages/home.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

* {
    font-family: 'Noto Sans KR', sans-serif;
    box-sizing: border-box;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: #f5f5f5 !important;
}

[data-testid="stAppViewContainer"] > .main {
    background-color: #f5f5f5;
}

[data-testid="stHeader"] {
    background: transparent;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* 전체 컨테이너 너비 고정 */
.block-container {
    max-width: 460px !important;
    padding-top: 60px !important;
    padding-bottom: 60px !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

[data-testid="stTextInputRootElement"],
[data-testid="stTextInputRootElement"] > div {
    background-color: #FAFAFA !important;
    /* border: 1.5px solid #ddd !important;  */
    border-color: transparent !important;
}

/* ✅ 입력 칸 너비 완전 통일 */
[data-testid="stTextInput"],
[data-testid="stTextInput"] > div,
[data-testid="stTextInput"] > div > div,
[data-testid="stTextInput"] input {
    width: 100% !important;
    min-width: 0 !important;
}

/* Login card */
.login-card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.10);
    padding: 48px 44px 36px 44px;
    margin: 0 auto;
}

.login-logo {
    font-size: 32px;
    font-weight: 700;
    color: #bb38d0;
    letter-spacing: -1px;
    text-align: center;
    margin-bottom: 28px;
}

.login-logo span {
    color: #222;
}

/* Input labels */
label[data-testid="stWidgetLabel"] > div > p {
    font-size: 13px !important;
    color: #555 !important;
    font-weight: 500 !important;
    margin-bottom: 4px !important;
}

/* Input boxes */
input[type="text"], input[type="password"] {
    /* border: 1.5px solid #ddd !important; */
    border-color: transparent !important;
    border-radius: 6px !important;
    font-size: 15px !important;
    padding: 12px 14px !important;
    /* transition: border-color 0.2s; */
    background: #fafafa !important;
}

/* 🔥 Placeholder(안내 문구) 색상 지정 추가 */
input[type="text"]::placeholder, 
input[type="password"]::placeholder {
    color: rgb(130, 131, 137) !important;
    opacity: 1 !important; /* 브라우저 기본 투명도 덮어쓰기 */
}

/* 로그인 버튼 색 */
input[type="text"]:focus, input[type="password"]:focus {
    border-color: #bb38d0 !important;
    background: #fff !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(3,199,90,0.12) !important;
}

/* Primary login button */
[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stButton"]:first-of-type > button {
    background-color: #bb38d0 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    height: 50px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    width: 100% !important;
    letter-spacing: 0.5px;
    transition: background 0.15s;
    margin-top: 6px;
}
div[data-testid="stButton"]:first-of-type > button:hover {
    background-color: #872a96 !important;
}

/* Divider text */
.divider-row {
    display: flex;
    align-items: center;
    margin: 24px 0 20px;
    color: #bbb;
    font-size: 13px;
    gap: 10px;
}
.divider-row::before, .divider-row::after {
    content: '';
    flex: 1;
    border-top: 1px solid #eee;
}

/* Social buttons container */
.social-btns {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 20px;
}

.social-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    border: none;
    border-radius: 6px;
    height: 48px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none !important;   /* ← 추가 */
    color: inherit !important;          /* ← 추가 */
    transition: filter 0.15s, box-shadow 0.15s;
    width: 100%;
}
a.social-btn {
    color: #000 !important;
    text-decoration: none !important;
}

.social-btn:hover {
    filter: brightness(0.96);
    box-shadow: 0 2px 8px rgba(0,0,0,0.10);
}

.btn-google {
    background: #fff;
    color: #3c4043;
    border: 1.5px solid #ddd !important;
}
.btn-kakao {
    background: #FEE500;
    color: #3c1e1e;
}

/* Helper links */
.helper-links {
    display: flex;
    justify-content: center;
    gap: 16px;
    font-size: 13px;
    color: #888;
    margin-top: 18px;
}


.helper-links a {
    color: #888;
    text-decoration: none;
}

.helper-links a:hover{ color: #bb38d0 !important; transition: all 500ms; }
.helper-sep { color: #ddd; }

/* Logout button */
[data-testid="stButton"] > button {
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None

# ── 로그인 UI ─────────────────────────────────────────────
st.markdown('<br>', unsafe_allow_html=True)
st.markdown('<div class="login-logo">AI<span>WORK</span></div>', unsafe_allow_html=True)

username = st.text_input("아이디", placeholder="이메일을 입력하세요")
password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")

# 🔥 수정된 부분: 관리자 분기 및 일반 DB 연동 자리 추가
if st.button("로그인", use_container_width=True):
    # 1. 관리자 계정 하드코딩 확인
    if username == "admin" and password == "1234":
        st.session_state.user = {"name": username, "role": "admin"}
        st.session_state.show_admin_choice = True # 관리자용 선택 화면 띄우기
        st.rerun() # 화면 새로고침하여 분기 화면 표시
        
    # 2. [TODO] 나중에 여기에 일반 사용자 DB 검증 로직 추가
    # elif check_user_in_database(username, password):
    #     st.session_state.user = {"name": username, "role": "user"}
    #     st.switch_page("pages/home.py") # 일반 사용자는 바로 홈으로 이동
        
    # 3. 로그인 실패
    else:
        st.error("아이디 또는 비밀번호가 틀렸습니다.")

# 관리자 로그인 성공 시 선택 화면 (Streamlit 중첩 버튼 에러 방지용 분리)
if st.session_state.get("show_admin_choice"):
    st.success("✅ 관리자 권한으로 인증되었습니다. 이동할 페이지를 선택하세요.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 기존 홈 화면", use_container_width=True):
            st.session_state.show_admin_choice = False
            st.switch_page("pages/home.py")
    with col2:
        if st.button("⚙️ 관리자 페이지", use_container_width=True, type="primary"):
            st.session_state.show_admin_choice = False
            st.switch_page("pages/admin.py")
    
    st.stop() # 관리자 선택 화면이 떴을 때는 아래쪽 소셜 로그인 UI를 그리지 않음

st.markdown("""
<div class="helper-links">
    <a href="find_pw" target="_self">비밀번호 찾기</a>
    <span class="helper-sep">|</span>
    <a href="sign_up" target="_self">회원가입</a>
</div>

<div class="divider-row">소셜 계정으로 로그인</div>

<div class="social-btns">
""", unsafe_allow_html=True)

# ── Google ────────────────────────────────────────────────
google_uri = "http://localhost:8000/api/auth/google/start"

# ── Kakao ─────────────────────────────────────────────────
kakao_uri = "http://localhost:8000/api/auth/kakao/start"

st.markdown(f"""
    <a href="{google_uri}" class="social-btn btn-google" target="_self">
        <svg width="20" height="20" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.31-8.16 2.31-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>
        Google로 계속하기
    </a>
    <br>
    <a href="{kakao_uri}" class="social-btn btn-kakao" target="_self">
        <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#3c1e1e" d="M12 3C6.477 3 2 6.477 2 10.5c0 2.611 1.563 4.911 3.938 6.258L4.5 21l4.688-2.344A11.3 11.3 0 0012 18c5.523 0 10-3.477 10-7.5S17.523 3 12 3z"/></svg>
        카카오로 계속하기
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)