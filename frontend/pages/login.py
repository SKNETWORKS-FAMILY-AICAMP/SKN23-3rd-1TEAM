# 초기 화면 (로그인창)
import streamlit as st
from pathlib import Path
import os
from dotenv import load_dotenv
from authlib.integrations.requests_client import OAuth2Session
import requests
st.write("env loaded:", os.getenv("KAKAO_REDIRECT_URI"))
import sys
st.write("RUNTIME_PY:", sys.executable)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


st.set_page_config(page_title="로그인", page_icon="🔐", layout="centered")

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
    color: inherit !important;
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
.btn-naver {
    background: #03c75a;
    color: #fff;
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
.helper-links a:hover { color: #03c75a; }
.helper-sep { color: #ddd; }

/* Welcome screen */
.welcome-box {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.10);
    padding: 48px 44px;
    text-align: center;
}
.welcome-icon { font-size: 56px; margin-bottom: 16px; }
.welcome-name { font-size: 22px; font-weight: 700; color: #222; margin-bottom: 8px; }
.welcome-sub { font-size: 15px; color: #888; margin-bottom: 28px; }

/* Logout button */
[data-testid="stButton"] > button {
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None

# ── 로그인 완료 화면 ─────────────────────────────────────
if st.session_state.user:
    st.markdown(f"""
    <div class="welcome-box">
        <div class="welcome-icon">👋</div>
        <div class="welcome-name">{st.session_state.user['name']} 님, 환영합니다!</div>
        <div class="welcome-sub">로그인에 성공했습니다.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("로그아웃", use_container_width=True):
        st.session_state.user = None
        st.rerun()
    st.stop()

# ── 로그인 UI ─────────────────────────────────────────────
# st.markdown('<div class="login-card">', unsafe_allow_html=True)
st.markdown('<br>', unsafe_allow_html=True)
st.markdown('<div class="login-logo">AI<span>WORK</span></div>', unsafe_allow_html=True)

username = st.text_input("아이디", placeholder="이메일을 입력하세요")
password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")

if st.button("로그인", use_container_width=True):
    if username == "admin" and password == "1234":
        st.session_state.user = {"name": username}
        st.switch_page("pages/home.py")  # 로그인 성공시 home.py로 이동
    else:
        st.error("아이디 또는 비밀번호가 틀렸습니다.")

st.markdown("""
<div class="helper-links">
    <a href="#">아이디 찾기</a>
    <span class="helper-sep">|</span>
    <a href="#">비밀번호 찾기</a>
    <span class="helper-sep">|</span>
    <a href="#">회원가입</a>
</div>

<div class="divider-row">소셜 계정으로 로그인</div>

<div class="social-btns">
""", unsafe_allow_html=True)

# ── Google ────────────────────────────────────────────────
google_uri = "#"
try:
    if GOOGLE_CLIENT_ID:
        google = OAuth2Session(
            GOOGLE_CLIENT_ID,
            GOOGLE_CLIENT_SECRET,
            scope="openid email profile",
            redirect_uri=GOOGLE_REDIRECT_URI
        )
        google_uri, _ = google.create_authorization_url(
            "https://accounts.google.com/o/oauth2/auth"
        )
except Exception:
    pass

# ── Kakao ─────────────────────────────────────────────────
kakao_uri = "#"
try:
    if KAKAO_CLIENT_ID:
        kakao = OAuth2Session(
            KAKAO_CLIENT_ID,
            KAKAO_CLIENT_SECRET,
            redirect_uri=KAKAO_REDIRECT_URI,
            scope="profile_nickname account_email"
        )
        kakao_uri, _ = kakao.create_authorization_url(
            "https://kauth.kakao.com/oauth/authorize"
        )
except Exception:
    pass

# ── Naver URI (직접 구성) ──────────────────────────────────
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "YOUR_NAVER_CLIENT_ID")
# naver_uri = f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={NAVER_CLIENT_ID}&redirect_uri={REDIRECT_URI or ''}&state=naver"

# st.markdown(f"""
#     <a href="{google_uri}" class="social-btn btn-google" target="_self">
#         <svg width="20" height="20" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.31-8.16 2.31-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>
#         Google로 계속하기
#     </a>
#     <a href="{kakao_uri}" class="social-btn btn-kakao" target="_self">
#         <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#3c1e1e" d="M12 3C6.477 3 2 6.477 2 10.5c0 2.611 1.563 4.911 3.938 6.258L4.5 21l4.688-2.344A11.3 11.3 0 0012 18c5.523 0 10-3.477 10-7.5S17.523 3 12 3z"/></svg>
#         카카오로 계속하기
#     </a>
#     <a href="{naver_uri}" class="social-btn btn-naver" target="_self">
#         <svg width="20" height="20" viewBox="0 0 24 24"><path fill="white" d="M13.77 12.64L10.03 7H7v10h3.23v-5.64L14.02 17H17V7h-3.23v5.64z"/></svg>
#         네이버로 계속하기
#     </a>
# </div>
# """, unsafe_allow_html=True)

# st.markdown('</div>', unsafe_allow_html=True)
#naver_uri = f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={NAVER_CLIENT_ID}&redirect_uri={REDIRECT_URI or ''}&state=naver"

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

# ── OAuth Callback ─────────────────────────────────────────
query_params = st.query_params

if "code" in query_params:
    code = query_params["code"]
    state = query_params.get("state", "")

    # if state == "naver":
    #     # 네이버 토큰 처리
    #     try:
    #         NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
    #         token = requests.post(
    #             "https://nid.naver.com/oauth2.0/token",
    #             data={
    #                 "grant_type": "authorization_code",
    #                 "client_id": NAVER_CLIENT_ID,
    #                 "client_secret": NAVER_CLIENT_SECRET,
    #                 "code": code,
    #                 "state": state,
    #             }
    #         ).json()
    #         userinfo = requests.get(
    #             "https://openapi.naver.com/v1/nid/me",
    #             headers={"Authorization": f"Bearer {token['access_token']}"}
    #         ).json()
    #         st.session_state.user = {"name": userinfo["response"]["name"]}
    #         st.switch_page("pages/02_home.py") # 네이버 로그인 성공시 home.py로 이동
    #     except Exception:
    #         st.error("네이버 로그인 중 오류가 발생했습니다.")
    # el
    if state == "kakao":
        
        # 카카오 토큰 교환
        token = requests.get(
            "http://localhost:8000/api/auth/kakao/start",
            data={
                "grant_type": "authorization_code",
                "client_id": KAKAO_CLIENT_ID,
                "client_secret": KAKAO_CLIENT_SECRET,
                "redirect_uri": KAKAO_REDIRECT_URI,
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
        ).json()
        
        # 카카오 사용자 정보
        userinfo = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {token['access_token']}"},
        ).json()

        nickname = (userinfo.get("properties") or {}).get("nickname", "사용자")
        st.session_state.user = {"name": nickname}
        st.switch_page("pages/home.py")

    else:
        # Google 토큰 처리
        try:
            token = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                }
            ).json()
            userinfo = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={"Authorization": f"Bearer {token['access_token']}"}
            ).json()
            st.session_state.user = {"name": userinfo.get("name", "사용자")}
            st.switch_page("pages/home.py") # 구글 로그인 성공시 home.py로 이동
        except Exception:
            pass


