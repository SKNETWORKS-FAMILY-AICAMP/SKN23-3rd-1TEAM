import pathlib
import streamlit as st
import streamlit.components.v1 as components

_FRONTEND = pathlib.Path(__file__).parent / "frontend" / "index.html"

def webcam_box(height: int = 520):
    html = _FRONTEND.read_text(encoding="utf-8")
    # height 파라미터로 박스 높이만 바꾸고 싶으면 간단 치환
    html = html.replace("height: 520px;", f"height: {height}px;")
    components.html(html, height=height + 10)