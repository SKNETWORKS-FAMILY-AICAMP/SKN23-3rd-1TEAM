import streamlit as st
from webcam_box import webcam_box

st.set_page_config(layout="wide")
st.title("Webcam (single fixed box, no layout jump)")

webcam_box(height=520)