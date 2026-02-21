"""
File: find_pw.py
Author: 김다빈, 김지우
Created: 2026-02-20
Description: 비밀번호 찾기 화면

Modification History:
- 2026-02-20 (김다빈): 초기 틀 생성
- 2026-02-21 (김지우): SMTP 이메일 인증 로직 및 세션 기반 단계별 비밀번호 재설정 UI 구현
"""

import streamlit as st
import re
import random
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# 페이지 기본 설정은 항상 최상단에 위치해야 합니다.
st.set_page_config(page_title="비밀번호 찾기", page_icon="🔍", layout="centered")

# .env 파일에서 환경 변수 불러오기 (override=True를 넣어서 수정된 비밀번호를 강제로 다시 읽어옵니다!)
load_dotenv(override=True)
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# --- 이메일 발송 함수 ---
def send_auth_email(receiver_email, auth_code):
    if not SENDER_EMAIL or not APP_PASSWORD:
        return False, "서버 설정 오류: .env 파일에서 이메일 정보를 불러오지 못했습니다."
        
    subject = "[보안] 비밀번호 재설정 인증 코드 안내"
    
    # 요청하신 이메일 내용으로 변경 (HTML 디자인 살짝 추가)
    body = f"""
    <html>
    <body style="font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; max-width: 500px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #222;">코드를 입력하고 로그인하세요</h2>
        
        <div style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; text-align: center; margin: 24px 0;">
            <h1 style="color: #bb38d0; letter-spacing: 8px; margin: 0; font-size: 32px;">{auth_code}</h1>
        </div>
        
        <p style="font-size: 14px; color: #555;">사이트에 로그인하려면 디바이스에 위 코드를 입력하세요. 코드는 15분 뒤 만료됩니다.</p>
        
        <p style="font-size: 13px; color: #888; margin-top: 30px;">
            회원님께서 전송한 요청이 아니라면 이 이메일은 무시하셔도 됩니다.<br>
            보안이 걱정되신다면 최근 디바이스 활동을 살펴보세요.
        </p>
        
        <p style="font-size: 13px; color: #888; font-weight: bold;">
            보안을 위해 회원님의 코드를 다른 사람들에게 공유하지 마세요.<br><br>
            - 관리자 드림 -
        </p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True, "성공"
    except smtplib.SMTPAuthenticationError:
        return False, "구글 로그인 실패: 앱 비밀번호가 틀렸거나 2단계 인증이 설정되지 않았습니다."
    except Exception as e:
        return False, f"알 수 없는 에러 발생: {str(e)}"

# --- CSS 스타일 ---
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

* {
    font-family: 'Noto Sans KR', sans-serif;
    box-sizing: border-box;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: #f5f5f5 !important;
    color: #000 !important;
}

[data-testid="stAppViewContainer"] > .main {
    background-color: #f5f5f5 !important;
}

[data-testid="stMarkdownContainer"], 
[data-testid="stMarkdownContainer"] p, 
[data-testid="stMarkdownContainer"] span,
label[data-testid="stWidgetLabel"] p,
label[data-testid="stWidgetLabel"] span {   
    color: #000 !important;
}

[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

.block-container {
    max-width: 460px !important;
    padding-top: 60px !important;
    padding-bottom: 60px !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

[data-testid="stTextInputRootElement"],
[data-testid="stTextInputRootElement"] > div {
    background-color: #e8e8e8 !important;
    border-color: transparent !important;
    transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

[data-testid="stTextInputRootElement"]:hover,
[data-testid="stTextInputRootElement"] > div:hover {
    background-color: #f0f0f0 !important;
}

[data-testid="stTextInput"],
[data-testid="stTextInput"] > div,
[data-testid="stTextInput"] > div > div,
[data-testid="stTextInput"] input {
    width: 100% !important;
    min-width: 0 !important;
}

.login-logo {
    font-size: 32px;
    font-weight: 700;
    color: #bb38d0;
    letter-spacing: -1px;
    text-align: center;
    margin-bottom: 28px;
}

label[data-testid="stWidgetLabel"] > div > p {
    font-size: 13px !important;
    color: #555 !important;
    font-weight: 500 !important;
    margin-bottom: 4px !important;
}

input[type="text"], input[type="password"] {
    border-color: transparent !important;
    border-radius: 6px !important;
    font-size: 15px !important;
    padding: 12px 14px !important;
    background: transparent !important;
    color: #4a4a4a !important; 
    -webkit-text-fill-color: #4a4a4a !important;
    transition: all 0.2s ease;
}

input[type="text"]:focus, input[type="password"]:focus {
    border-color: #bb38d0 !important;
    background: #fff !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(187,56,208,0.12) !important;
}

[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stButton"] > button {
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
div[data-testid="stButton"] > button:hover {
    background-color: #872a96 !important;
}

.helper-links {
    display: flex;
    justify-content: center;
    gap: 16px;
    font-size: 13px;
    color: #888;
    margin-top: 18px;
}
.helper-links a { color: #888; text-decoration: none; }
.helper-links a:hover { color: #bb38d0; }
.helper-sep { color: #ddd; }

.info-text {
    font-size: 14px;
    color: #666;
    text-align: center;
    margin-bottom: 20px;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- 세션 상태(Session State) 초기화 ---
if "reset_step" not in st.session_state:
    st.session_state.reset_step = 1
if "auth_code" not in st.session_state:
    st.session_state.auth_code = ""
if "target_email" not in st.session_state:
    st.session_state.target_email = ""

# 상단 로고
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="login-logo">비밀번호 찾기</div>', unsafe_allow_html=True)

# ==========================================
# [STEP 1] 이메일 입력 및 인증번호 발송
# ==========================================
if st.session_state.reset_step == 1:
    st.markdown(
        '<div class="info-text">가입하신 이메일 아이디를 입력해주세요.<br>비밀번호 재설정 인증번호를 보내드립니다.</div>',
        unsafe_allow_html=True,
    )
    
    email_input = st.text_input("아이디 (이메일)", placeholder="이메일을 입력하세요", key="email_input")
    
    if st.button("인증번호 발송", use_container_width=True):
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        
        if not email_input:
            st.warning("이메일을 입력해주세요.")
        elif not re.match(email_pattern, email_input):
            st.error("유효한 이메일 형식이 아닙니다. 다시 확인해주세요.")
        else:
            with st.spinner("이메일을 발송 중입니다. 잠시만 기다려주세요..."):
                # 6자리 랜덤 인증번호 생성
                generated_code = str(random.randint(100000, 999999))
                
                # 실제 이메일 발송 함수 호출 (결과와 에러 메시지를 같이 받음)
                is_sent, error_msg = send_auth_email(email_input, generated_code)
                
                if is_sent:
                    st.session_state.auth_code = generated_code
                    st.session_state.target_email = email_input
                    st.session_state.reset_step = 2
                    
                    st.success("인증번호가 발송되었습니다. 이메일함을 확인해주세요!")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    # 🔥 실패 시 화면에 바로 원인을 띄워줍니다.
                    st.error(f"이메일 발송 실패: {error_msg}")

# ==========================================
# [STEP 2] 인증번호 확인
# ==========================================
elif st.session_state.reset_step == 2:
    st.markdown(
        f'<div class="info-text"><b>{st.session_state.target_email}</b>(으)로<br>인증번호를 발송했습니다. 6자리 숫자를 입력해주세요.</div>',
        unsafe_allow_html=True,
    )
    
    code_input = st.text_input("인증번호", placeholder="6자리 숫자 입력")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("인증 확인", use_container_width=True):
            if code_input == st.session_state.auth_code:
                st.session_state.reset_step = 3
                st.rerun()
            else:
                st.error("인증번호가 일치하지 않습니다.")
    
    with col2:
        if st.button("처음으로 돌아가기", use_container_width=True):
            st.session_state.reset_step = 1
            st.rerun()

# ==========================================
# [STEP 3] 새 비밀번호 설정
# ==========================================
elif st.session_state.reset_step == 3:
    st.markdown(
        '<div class="info-text">이메일 인증이 완료되었습니다.<br>새로운 비밀번호를 설정해주세요.</div>',
        unsafe_allow_html=True,
    )
    
    new_password = st.text_input("새 비밀번호", type="password", placeholder="새로운 비밀번호 입력")
    new_password_check = st.text_input("새 비밀번호 확인", type="password", placeholder="비밀번호 다시 입력")
    
    if st.button("비밀번호 변경 완료", use_container_width=True):
        if not new_password or not new_password_check:
            st.warning("비밀번호를 모두 입력해주세요.")
        elif new_password != new_password_check:
            st.error("비밀번호가 일치하지 않습니다.")
        elif len(new_password) < 8:
            st.error("비밀번호는 8자리 이상이어야 합니다.")
        else:
            # TODO: DB 연동 - 여기에 데이터베이스의 비밀번호를 업데이트하는 로직을 추가하세요.
            
            st.success("비밀번호가 성공적으로 변경되었습니다! 로그인 페이지로 이동합니다.")
            time.sleep(2)
            
            # 상태 초기화 후 이동
            st.session_state.reset_step = 1
            st.session_state.auth_code = ""
            st.session_state.target_email = ""
            st.rerun()

# ==========================================
# 하단 링크 (URL 수정 완료)
# ==========================================
st.markdown(
    """
<div class="helper-links">
    <a href="/" target="_self">로그인으로 돌아가기</a>
    <span class="helper-sep">|</span>
    <a href="/sign_up" target="_self">회원가입</a>
</div>
""",
    unsafe_allow_html=True,
)