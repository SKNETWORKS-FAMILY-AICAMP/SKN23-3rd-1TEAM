"""
File: app.py
Author: 김지우
Created: 2026-02-26
Description: 메인 화면

Modification History:
- 2026-02-26 (김지우): 초기 생성 및 login.py로 바로 이동 세팅 
"""

import streamlit as st
st.set_page_config(page_title="AIWORK", page_icon="👾", layout="centered")

# 소셜 로그인 콜백 토큰은 루트에서 먼저 세션으로 넘겨서 페이지 전환 중 유실되지 않게 한다.
social_token = st.query_params.get("access_token")
social_provider = st.query_params.get("social")
if social_token:
    st.session_state.social_login_token = social_token
if social_provider:
    st.session_state.social_login_provider = social_provider

# login.py로 바로 이동
st.switch_page("pages/login.py")
