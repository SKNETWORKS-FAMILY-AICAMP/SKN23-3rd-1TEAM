"""
File: sign_up.py
Author: 김다빈, 김지우
Created: 2026-02-20
Description: 회원가입 화면

Modification History:
- 2026-02-20 (김다빈): 초기 틀 생성
- 2026-02-21 (김지우) : 이메일 인증 모달, 실시간 폼 검증, 약관 동의 및 가입 완료 프로세스 전체 구현
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

st.set_page_config(page_title="회원가입", page_icon="📝", layout="centered")

# .env 파일에서 환경 변수 불러오기
load_dotenv(override=True)
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# --- 이메일 발송 함수 ---
def send_auth_email(receiver_email, auth_code):
    if not SENDER_EMAIL or not APP_PASSWORD:
        return False, "서버 설정 오류: .env 파일에서 이메일 정보를 불러오지 못했습니다."
        
    subject = "[회원가입] 이메일 인증 번호 안내"
    body = f"""
    <html>
    <body style="font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; max-width: 500px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #222;">회원가입 이메일 인증</h2>
        <div style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; text-align: center; margin: 24px 0;">
            <h1 style="color: #bb38d0; letter-spacing: 8px; margin: 0; font-size: 32px;">{auth_code}</h1>
        </div>
        <p style="font-size: 14px; color: #555;">화면에 위 인증번호 6자리를 입력하여 가입을 완료해 주세요.</p>
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
    except Exception as e:
        return False, f"이메일 발송 실패: {str(e)}"


# --- 세션 상태(Session State) 초기화 ---
if "current_input_email" not in st.session_state: st.session_state.current_input_email = ""
if "id_checked" not in st.session_state: st.session_state.id_checked = False
if "id_check_result" not in st.session_state: st.session_state.id_check_result = None
if "verify_error_msg" not in st.session_state: st.session_state.verify_error_msg = ""
if "is_verified" not in st.session_state: st.session_state.is_verified = False
if "code_sent" not in st.session_state: st.session_state.code_sent = False
if "auth_code" not in st.session_state: st.session_state.auth_code = ""

# 약관 동의 세션 상태 관리
if "agree_all" not in st.session_state: st.session_state.agree_all = False
if "agree_terms" not in st.session_state: st.session_state.agree_terms = False
if "agree_privacy" not in st.session_state: st.session_state.agree_privacy = False

def toggle_all():
    st.session_state.agree_terms = st.session_state.agree_all
    st.session_state.agree_privacy = st.session_state.agree_all

def toggle_single():
    if st.session_state.agree_terms and st.session_state.agree_privacy:
        st.session_state.agree_all = True
    else:
        st.session_state.agree_all = False

# 이메일 입력칸 글자 변경 감지 (초기화 로직)
if "email_input" in st.session_state:
    if st.session_state.email_input != st.session_state.current_input_email:
        st.session_state.current_input_email = st.session_state.email_input
        st.session_state.id_checked = False
        st.session_state.id_check_result = None
        st.session_state.verify_error_msg = ""
        st.session_state.is_verified = False
        st.session_state.code_sent = False

# --- CSS 스타일 ---
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

* { font-family: 'Noto Sans KR', sans-serif; box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] { background-color: #f5f5f5 !important; color: #000 !important; }
[data-testid="stAppViewContainer"] > .main { background-color: #f5f5f5 !important; }
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span, label[data-testid="stWidgetLabel"] p, label[data-testid="stWidgetLabel"] span { color: #000 !important; }
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.block-container { max-width: 460px !important; padding-top: 60px !important; padding-bottom: 60px !important; padding-left: 1rem !important; padding-right: 1rem !important; }
[data-testid="stTextInputRootElement"], [data-testid="stTextInputRootElement"] > div { background-color: #e8e8e8 !important; border-color: transparent !important; transition: background-color 0.2s ease, box-shadow 0.2s ease; }
[data-testid="stTextInputRootElement"]:hover, [data-testid="stTextInputRootElement"] > div:hover { background-color: #f0f0f0 !important; }
[data-testid="stTextInput"], [data-testid="stTextInput"] > div, [data-testid="stTextInput"] > div > div, [data-testid="stTextInput"] input { width: 100% !important; min-width: 0 !important; }

.login-logo { font-size: 32px; font-weight: 700; color: #bb38d0; letter-spacing: -1px; text-align: center; margin-bottom: 28px; }
label[data-testid="stWidgetLabel"] > div > p { font-size: 13px !important; color: #555 !important; font-weight: 500 !important; margin-bottom: 4px !important; }

/* 텍스트 입력칸 사이즈 복구 */
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
input[type="text"]:focus, input[type="password"]:focus { border-color: #bb38d0 !important; background: #fff !important; outline: none !important; box-shadow: 0 0 0 2px rgba(187,56,208,0.12) !important; }

/* 🌟 메인 보라색 버튼 전용 스타일 */
[data-testid="stButton"] > button[kind="primary"] { 
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
    margin-top: 0px !important; 
}
[data-testid="stButton"] > button[kind="primary"]:hover { background-color: #872a96 !important; }

/* 🌟 '보기' 버튼을 텍스트 링크로 완벽 변신 */
[data-testid="stButton"] > button[kind="secondary"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    height: auto !important;
    min-height: 0 !important;
    display: inline-flex;
    justify-content: flex-end;
    width: 100%;
    margin-top: 6px !important; 
}
[data-testid="stButton"] > button[kind="secondary"]:hover,
[data-testid="stButton"] > button[kind="secondary"]:active,
[data-testid="stButton"] > button[kind="secondary"]:focus {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: transparent !important;
}
[data-testid="stButton"] > button[kind="secondary"] p {
    color: #888 !important; 
    font-size: 14px !important;
    text-decoration: underline !important;
    text-underline-offset: 3px; 
    margin: 0 !important;
    font-weight: 500 !important;
}
[data-testid="stButton"] > button[kind="secondary"]:hover p {
    color: #333 !important; 
}

.helper-links { display: flex; justify-content: center; gap: 16px; font-size: 13px; color: #888; margin-top: 18px; }
.helper-links a { color: #888; text-decoration: none; font-weight: 500; }
.helper-links a:hover { color: #bb38d0; text-decoration: underline; }

.status-msg { font-size: 13px; text-align: center; margin-top: 0px; margin-bottom: 12px; font-weight: 500; }
.field-msg { font-size: 12px; margin-top: -12px; margin-bottom: 12px; margin-left: 4px; font-weight: 500; }
.text-success { color: #2ecc71; }
.text-error { color: #e74c3c; }

div[data-testid="stDialog"] div[data-testid="stMarkdownContainer"] h3 { color: #bb38d0 !important; text-align: center; font-weight: 700; }
</style>
""",
    unsafe_allow_html=True,
)

email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
name_pattern = r'^[가-힣a-zA-Z\s]+$'
pw_pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[\W_]).{8,}$'

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="login-logo">회원가입</div>', unsafe_allow_html=True)


# ==========================================
# 💎 모달: 약관 보기
# ==========================================
@st.dialog("이용약관 및 동의서", width="large")
def show_terms_modal(title, content):
    st.markdown(f"### {title}")
    with st.container(height=350):
        st.markdown(content)
    if st.button("확인", type="primary", use_container_width=True):
        st.rerun()

terms_aiwork_text = """
**제 1 장 총칙**

**제 1 조 (목적)**
본 약관은 통계청이 운영하는 나라통계시스템 운영홈페이지(이하 "당 사이트")에서 제공하는 모든 서비스(이하 "서비스")의 이용조건 및 절차, 이용자와 당 사이트의 권리, 의무, 책임사항과 기타 필요한 사항을 규정함을 목적으로 합니다.

**제 2 조 (약관의 효력과 변경)**
① 당 사이트는 이용자가 본 약관 내용에 동의하는 것을 조건으로 이용자에게 서비스를 제공하며, 당 사이트의 서비스 제공 행위 및 이용자의 서비스 사용 행위에는 본 약관을 우선적으로 적용하겠습니다.
② 당 사이트는 본 약관을 사전 고지 없이 변경할 수 있으며, 변경된 약관은 당 사이트 내에 공지함으로써 이용자가 직접 확인하도록 할 것입니다. 이용자가 변경된 약관에 동의하지 아니하는 경우 본인의 회원등록을 취소(회원탈퇴)할 수 있으며, 계속 사용할 경우에는 약관 변경에 대한 암묵적 동의로 간주됩니다. 변경된 약관은 공지와 동시에 그 효력을 발휘합니다.
"""

terms_privacy_text = """
**1. 개인정보의 수집항목 및 수집방법**
통계청 나라통계사이트에서는 기본적인 회원 서비스 제공을 위한 필수정보로 실명인증정보와 가입정보로 구분하여 다음의 정보를 수집하고 있습니다. 필수정보를 입력해주셔야 회원 서비스 이용이 가능합니다.

가. 수집하는 개인정보의 항목 
* 수집하는 필수항목
  - 실명인증정보 : 이름, 휴대전화번호, 본인 인증 또는 I-PIN, GPKI
  - 가입정보 : 아이디, 비밀번호, 성명, 이메일, 휴대전화번호, 기관명

나. 개인정보 수집방법
  - 홈페이지 회원가입을 통한 수집 

**2. 개인정보의 수집/이용 목적 및 보유/이용 기간**
통계청 나라통계사이트에서는 정보주체의 회원 가입일로부터 서비스를 제공하는 기간 동안에 한하여 서비스를 이용하기 위한 최소한의 개인정보를 보유 및 이용하게 됩니다. 
* 개인정보의 보유 및 이용기간 : 2년 또는 회원탈퇴시
"""


# ==========================================
# 💎 모달: 이메일 인증
# ==========================================
@st.dialog("이메일 인증", width="small")
def email_verification_modal():
    st.markdown("### 본인 확인을 진행합니다 🚀")
    st.caption("가입하실 이메일 주소로 인증번호를 발송합니다.")
    
    st.text_input("인증받을 이메일 주소", value=st.session_state.current_input_email, disabled=True)
    
    btn_text = "인증번호 재발송" if st.session_state.code_sent else "인증번호 발송"
    
    if st.button(btn_text, type="primary", use_container_width=True):
        with st.spinner("이메일 발송 중..."):
            code = str(random.randint(100000, 999999))
            is_sent, msg = send_auth_email(st.session_state.current_input_email, code)
            
            if is_sent:
                st.session_state.code_sent = True
                st.session_state.auth_code = code
            else:
                st.markdown(f'<div class="status-msg text-error">{msg}</div>', unsafe_allow_html=True)
                
    if st.session_state.code_sent and not st.session_state.is_verified:
        st.markdown("---")
        auth_input = st.text_input("인증번호 6자리", placeholder="메일로 받은 인증번호를 입력하세요")
        
        msg_placeholder = st.empty()
        
        if st.button("인증 확인", type="primary", use_container_width=True):
            if auth_input == st.session_state.auth_code:
                st.session_state.is_verified = True
                msg_placeholder.markdown('<div class="status-msg text-success">인증이 완료되었습니다.</div>', unsafe_allow_html=True)
                time.sleep(1.5)
                st.rerun() 
            else:
                msg_placeholder.markdown('<div class="status-msg text-error">인증번호가 일치하지 않습니다. 다시 확인해주세요.</div>', unsafe_allow_html=True)


# ==========================================
# 💎 모달: 가입 완료 축하 창
# ==========================================
@st.dialog("가입 완료", width="small")
def signup_success_modal(user_name):
    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 50px; margin-bottom: 10px;">✨</div>
            <h2 style="color: #bb38d0; font-weight: 700; margin-bottom: 15px;">환영합니다!</h2>
            <p style="font-size: 16px; color: #333; line-height: 1.5;">
                <b>{user_name}</b>님,<br>회원가입이 성공적으로 완료되었습니다.
            </p>
            <p style="font-size: 13px; color: #888; margin-top: 25px;">
                3초 후 로그인 페이지로 자동 이동합니다... 🚀
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.03) 
        progress_bar.progress(i + 1)

    # 🔥 위젯(체크박스)에 연결된 키값들은 제외하고 일반 데이터만 깔끔하게 초기화합니다!
    for key in ["current_input_email", "id_checked", "id_check_result", "verify_error_msg", 
                "is_verified", "code_sent", "auth_code"]:
        if key in st.session_state:
            if type(st.session_state[key]) == bool:
                st.session_state[key] = False
            else:
                st.session_state[key] = ""
                
    st.switch_page("app.py")


# ==========================================
# 1. 아이디 입력 & 중복 확인 구역
# ==========================================
col1, col2 = st.columns([2.5, 1])

with col1:
    user_id = st.text_input("아이디 (이메일)", placeholder="이메일을 입력하세요", key="email_input")
with col2:
    st.markdown("<div style='margin-top: 29px;'></div>", unsafe_allow_html=True)
    if st.button("중복 확인", type="primary", use_container_width=True):
        st.session_state.verify_error_msg = ""
        
        if not user_id:
            st.session_state.id_check_result = "empty"
        elif not re.match(email_pattern, user_id):
            st.session_state.id_check_result = "invalid"
        else:
            with st.spinner("확인 중..."):
                time.sleep(0.5) 
                st.session_state.id_checked = True
                st.session_state.id_check_result = True 

# 결과 알림창
if st.session_state.id_check_result == "empty":
    st.markdown('<div class="status-msg text-error">이메일을 먼저 입력해주세요.</div>', unsafe_allow_html=True)
elif st.session_state.id_check_result == "invalid":
    st.markdown('<div class="status-msg text-error">유효한 이메일 형식이 아닙니다.</div>', unsafe_allow_html=True)
elif st.session_state.id_checked and st.session_state.id_check_result == True:
    st.markdown('<div class="status-msg text-success">사용가능한 아이디(이메일)입니다.</div>', unsafe_allow_html=True)
elif st.session_state.id_checked and st.session_state.id_check_result == False:
    st.markdown('<div class="status-msg text-error">다른 아이디(이메일)을 입력해주세요.</div>', unsafe_allow_html=True)


# ==========================================
# 2. 인증하기 버튼 & 인증 알림 위치
# ==========================================
if not st.session_state.is_verified:
    if st.button("인증하기", type="primary", use_container_width=True):
        if not st.session_state.id_checked or st.session_state.id_check_result != True:
            st.session_state.verify_error_msg = "먼저 사용 가능한 아이디(이메일)인지 중복 확인을 진행해주세요."
        else:
            st.session_state.verify_error_msg = ""
            email_verification_modal()
            
    auth_msg_ph = st.empty()
    if st.session_state.verify_error_msg:
        auth_msg_ph.markdown(f'<div class="status-msg text-error">{st.session_state.verify_error_msg}</div>', unsafe_allow_html=True)
else:
    st.button("인증 완료", type="primary", use_container_width=True, disabled=True)
    auth_msg_ph = st.empty()


# ==========================================
# 3. 추가 정보 입력 구역
# ==========================================
st.markdown("<hr style='margin:15px 0; border:none; border-top:1px solid #ddd;'>", unsafe_allow_html=True)

name = st.text_input("이름 (닉네임)", placeholder="한글 또는 영문만 입력하세요")
name_msg_ph = st.empty() 

if name:
    if re.match(name_pattern, name):
        name_msg_ph.markdown('<div class="field-msg text-success">올바른 이름 형식입니다.</div>', unsafe_allow_html=True)
    else:
        name_msg_ph.markdown('<div class="field-msg text-error">이름은 한글과 영어만 입력 가능합니다.</div>', unsafe_allow_html=True)

password = st.text_input("비밀번호", type="password", placeholder="영문, 숫자, 특수문자 포함 8자리 이상")
pw_msg_ph = st.empty() 

if password:
    if re.match(pw_pattern, password):
        pw_msg_ph.markdown('<div class="field-msg text-success">안전한 비밀번호입니다.</div>', unsafe_allow_html=True)
    else:
        pw_msg_ph.markdown('<div class="field-msg text-error">영문, 숫자, 특수문자를 모두 포함하여 8자리 이상이어야 합니다.</div>', unsafe_allow_html=True)

password_confirm = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호를 다시 입력하세요")
pw2_msg_ph = st.empty() 

if password_confirm:
    if password == password_confirm:
        pw2_msg_ph.markdown('<div class="field-msg text-success">비밀번호가 일치합니다.</div>', unsafe_allow_html=True)
    else:
        pw2_msg_ph.markdown('<div class="field-msg text-error">비밀번호가 일치하지 않습니다. 다시 입력해주세요.</div>', unsafe_allow_html=True)


# ==========================================
# 4. 약관 동의 구역
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
with st.container(border=True):
    st.checkbox("**전체 동의하기**", key="agree_all", on_change=toggle_all)
    st.caption("실명 인증된 아이디로 가입, 필수 이용약관 및 개인정보 수집/이용 동의를 포함합니다.")
    st.markdown("<hr style='margin: 5px 0 15px 0;'>", unsafe_allow_html=True)
    
    tcol1, tcol2 = st.columns([5, 1])
    with tcol1:
        st.checkbox("(필수) **AIWORK** 이용약관", key="agree_terms", on_change=toggle_single)
    with tcol2:
        if st.button("보기", key="btn_view_terms"):
            show_terms_modal("AIWORK 이용약관", terms_aiwork_text)
            
    pcol1, pcol2 = st.columns([5, 1])
    with pcol1:
        st.checkbox("(필수) 개인정보 수집/이용 동의", key="agree_privacy", on_change=toggle_single)
    with pcol2:
        if st.button("보기", key="btn_view_privacy"):
            show_terms_modal("개인정보 수집/이용 동의", terms_privacy_text)

terms_msg_ph = st.empty()


# ==========================================
# 5. 가입하기 버튼 검증
# ==========================================
if st.button("가입하기", type="primary", use_container_width=True):
    has_error = False
    
    if not st.session_state.is_verified:
        auth_msg_ph.markdown('<div class="status-msg text-error">이메일 인증을 먼저 진행해주세요.</div>', unsafe_allow_html=True)
        has_error = True
        
    if not name:
        name_msg_ph.markdown('<div class="field-msg text-error">이름을 입력해주세요.</div>', unsafe_allow_html=True)
        has_error = True
    elif not re.match(name_pattern, name):
        name_msg_ph.markdown('<div class="field-msg text-error">이름은 한글과 영어만 입력 가능합니다.</div>', unsafe_allow_html=True)
        has_error = True
        
    if not password:
        pw_msg_ph.markdown('<div class="field-msg text-error">비밀번호를 입력해주세요.</div>', unsafe_allow_html=True)
        has_error = True
    elif not re.match(pw_pattern, password):
        pw_msg_ph.markdown('<div class="field-msg text-error">영문, 숫자, 특수문자를 모두 포함하여 8자리 이상이어야 합니다.</div>', unsafe_allow_html=True)
        has_error = True
        
    if not password_confirm:
        pw2_msg_ph.markdown('<div class="field-msg text-error">비밀번호 확인을 입력해주세요.</div>', unsafe_allow_html=True)
        has_error = True
    elif password != password_confirm:
        pw2_msg_ph.markdown('<div class="field-msg text-error">비밀번호가 일치하지 않습니다. 다시 확인해주세요.</div>', unsafe_allow_html=True)
        has_error = True
        
    if not st.session_state.agree_terms or not st.session_state.agree_privacy:
        terms_msg_ph.markdown('<div class="field-msg text-error" style="text-align: center; margin-top: 5px;">필수 약관에 모두 동의해주세요.</div>', unsafe_allow_html=True)
        has_error = True

    # 에러가 없다면 축하 모달 띄우기!
    if not has_error:
        signup_success_modal(name)

st.markdown(
    """
<div class="helper-links">
    <a href="/" target="_self">이미 계정이 있으신가요? 로그인</a>
</div>
""",
    unsafe_allow_html=True,
)