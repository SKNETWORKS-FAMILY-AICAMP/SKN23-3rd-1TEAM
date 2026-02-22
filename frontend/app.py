import streamlit as st
st.set_page_config(page_title="AIWORK", page_icon="🔐", layout="centered")  # 기본 설정

if st.session_state.get("access_token"):
    st.switch_page("pages/home.py")
else:
    st.switch_page("pages/login.py")