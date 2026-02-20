import streamlit as st

if st.session_state.get("access_token"):
    st.switch_page("pages/02_home.py")
else:
    st.switch_page("pages/01_login.py")