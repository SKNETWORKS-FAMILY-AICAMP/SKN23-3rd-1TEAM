"""
File: home.py
Author: 김지우
Created: 2026-02-20
Description: 메인 화면

Modification History:
- 2026-02-20 (김지우): 메인 화면 틀 생성
"""

import streamlit as st

# 1. 페이지 설정 (넓은 화면)
st.set_page_config(page_title="AIWORK", page_icon="🤖", layout="wide")

# (가정) 이전 로그인 페이지에서 인증을 거치고 넘어왔다고 전제합니다.
# 실제로는 로그인 로직에서 session_state에 user_name을 넣어주게 됩니다.
if "user_name" not in st.session_state:
    st.session_state.user_name = "000" 

# ==========================================
# 🛑 상단 대형 배너 
# ==========================================
st.image("https://via.placeholder.com/1200x120/1E1E1E/FFFFFF?text=DeepInterview+Grand+Open", use_container_width=True)
st.write("") # 약간의 여백

# ==========================================
# 🗂️ 메인 레이아웃 분할 (왼쪽 7 : 오른쪽 3)
# ==========================================
left_col, _,right_col = st.columns([7,0.1, 3])

# ------------------------------------------
# 👉 [오른쪽 단] 내 프로필 박스 & 퀵 메뉴
# ------------------------------------------
with right_col:
    # 1. 로그인 완료 유저 전용 프로필 컨테이너
    with st.container(border=True):
        profile_c1, profile_c2 = st.columns([2, 8])
        with profile_c1:
            # 유저 프로필 아바타
            st.image("https://api.dicebear.com/7.x/avataaars/svg?seed=Jiwu", width=50)
        with profile_c2:
            st.markdown(f"**{st.session_state.user_name} 님** (일반회원) 🔒 반갑습니다.")
            if st.button("로그아웃 ➔", key="logout_btn", help="클릭 시 로그인 페이지로 돌아갑니다"):
                st.warning("로그아웃 되었습니다. (로그인 페이지로 리다이렉트 로직 필요)")
                st.switch_page("app.py") # 나중에 진짜 연동할 때 주석 해제 (app.py 에서 streamlit 실행해야 잘됨.)
        
        st.divider()
        
        # 마이페이지 관련 퀵 메뉴 바
        nav_c1, nav_c2, nav_c3 = st.columns(3)
        nav_c1.button("이력서", use_container_width=True)
        nav_c2.button("내 기록", use_container_width=True)
        nav_c3.button("마이페이지", use_container_width=True)
            
    # 2. 🔥 핵심 CTA 배너 버튼 (면접장 이동)
    st.write("")
    if st.button("AI 모의 면접 시작", type="primary", use_container_width=True):
        st.success("면접 대기실로 이동합니다!")
        st.switch_page("pages/AI채팅부분.py") # 나중에 진짜 연동할 때 주석 해제
        
    # 3. 우측 하단 띠배너 광고 (깃허브 홍보 등)
    st.write("")
    with st.container(border=True):
        st.markdown("🔗 **Github Repository**")
        st.caption("깃허브 주소")

# ------------------------------------------
# 👈 [왼쪽 단] 맞춤형 채용 공고 & 기술 뉴스
# ------------------------------------------
with left_col:
    st.markdown(f"### ☺︎ **{st.session_state.user_name}** 님을 위한 맞춤 추천")
    
    # 탭 UI
    tab1, tab2, tab3 = st.tabs(["추천 공고", "백엔드 트렌드", "AI 면접 Tips"])
    
    with tab1:

        # ============== 이부분 공고 어떻게 가져올지 정해봐야되긴함 =====================
        # 공고 리스트 (테두리 있는 박스로 표현)
        with st.container(border=True):
            col1, col2 = st.columns([8, 2])
            with col1:
                st.markdown("#### 네이버 (NAVER) - Python 백엔드 신입/경력")
                st.write("FastAPI와 MSA 환경에서 대규모 트래픽을 처리할 개발자를 모십니다.")
            with col2:
                st.button("지원하기", key="apply_1", use_container_width=True)
                
        with st.container(border=True):
            col1, col2 = st.columns([8, 2])
            with col1:
                st.markdown("#### 토스 (Toss) - Server Developer")
                st.write("초당 수만 건의 결제 트랜잭션을 안정적으로 처리하는 경험을 해보세요.")
            with col2:
                st.button("지원하기", key="apply_2", use_container_width=True)
                
    with tab2:
        st.info("오늘의 백엔드 기술 블로그 및 아티클이 노출되는 영역입니다.")
        
    with tab3:
        st.info("최신 AI 면접 합격 후기 및 팁 게시판 영역입니다.")