import streamlit as st
import os
import time
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI
import io

# --- 기본 페이지 설정 ---
st.set_page_config(page_title="AI 면접관", page_icon="🤖", layout="centered")

# --- CSS 스타일 적용 (카카오톡 스타일) ---
st.markdown(
    """
<style>
/* 전체 배경색 */
.stApp {
    background-color: #b2c7d9;
}

/* 채팅 컨테이너 */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 10px;
}

/* AI(면접관) 말풍선 스타일 */
.ai-message {
    align-self: flex-start;
    background-color: #ffffff;
    color: #000000;
    padding: 10px 15px;
    border-radius: 15px;
    border-top-left-radius: 0;
    max-width: 70%;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    margin-bottom: 10px;
    position: relative;
    font-size: 15px;
}

/* 사용자 말풍선 스타일 */
.user-message {
    align-self: flex-end;
    background-color: #fef01b;
    color: #000000;
    padding: 10px 15px;
    border-radius: 15px;
    border-top-right-radius: 0;
    max-width: 70%;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    margin-bottom: 10px;
    position: relative;
    font-size: 15px;
}

/* 화자 이름 */
.sender-name {
    font-size: 12px;
    color: #4a4a4a;
    margin-bottom: 4px;
}

/* 헤더 및 텍스트 색상 강제 지정 (다크모드 방지용) */
h1, h2, h3, p, div {
    color: #333333;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- 인증 확인 ---
if "user" not in st.session_state or st.session_state.user is None:
    st.warning("로그인이 필요합니다.")
    st.stop()

# --- OpenAI 클라이언트 연동 ---
# .env 또는 시스템 환경변수에 OPENAI_API_KEY가 설정되어 있어야 합니다.
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
except Exception as e:
    client = None
    st.error("OpenAI API 키가 설정되지 않았습니다.")

# --- Session State 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 초기 인사말
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "안녕하세요! 저는 AI 면접관입니다. 면접을 시작하기 전, 가볍게 자기소개를 부탁드립니다. (음성으로 답변해주시거나 텍스트를 입력해주세요.)",
        }
    )

if "interview_ended" not in st.session_state:
    st.session_state.interview_ended = False

# --- UI 레이아웃 ---
st.title("🤖 AI 화상 면접")

# 상단: 토킹헤드 자리 (Placeholder)
with st.container():
    st.markdown("### 🎥 AI Interviewer Video")
    st.video(
        "https://www.w3schools.com/html/mov_bbb.mp4", format="video/mp4", start_time=0
    )
    st.caption(
        "※ 실시간 AI 토킹헤드 및 립싱크(LivePortrait, MuseTalk) 모델 연동 대기 중입니다."
    )
st.divider()

# 채팅창 영역 시작 (CSS 설정을 위한 컨테이너)
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# 저장된 채팅 메시지 렌더링
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f'<div style="display:flex; justify-content:flex-end;"><div class="user-message">{message["content"]}</div></div>',
            unsafe_allow_html=True,
        )
    elif message["role"] == "assistant":
        st.markdown(
            f'<div style="display:flex; justify-content:flex-start;"><div style="display:flex; flex-direction:column;"><div class="sender-name">면접관</div><div class="ai-message">{message["content"]}</div></div></div>',
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)

# --- 하단 입력 영역 (마이크 & 텍스트) ---
if not st.session_state.interview_ended:
    st.divider()

    # 텍스트 채팅 입력
    prompt = st.chat_input("텍스트로 메시지를 입력하세요.")

    # 음성 입력 (Streamlit 1.36+ 기본 제공)
    with st.expander("🎙️ 마이크로 음성 답변하기", expanded=False):
        audio_val = st.audio_input(
            "녹음 버튼을 눌러 말씀하신 후 V(완료) 버튼을 눌러주세요."
        )

    # --- TTS 재생 처리 ---
    # 방금 생성된 답변이 있다면 오디오를 재생합니다.
    if "latest_audio_content" in st.session_state:
        st.audio(
            st.session_state.latest_audio_content, format="audio/mp3", autoplay=True
        )
        # 재생 후에는 상태에서 삭제하여 리렌더링 시 반복 재생 방지
        del st.session_state.latest_audio_content

    # 사용자 입력 처리 로직 (STT 우선, 없으면 Text)
    user_input_text = ""

    # 1. 오디오 입력 처리
    if audio_val is not None:
        audio_bytes = audio_val.getvalue()
        audio_hash = hash(audio_bytes)
        # 중복 처리 방지
        if st.session_state.get("last_processed_audio") != audio_hash:
            st.session_state.last_processed_audio = audio_hash

            # --- STT 처리 ---
            with st.spinner("음성을 텍스트로 변환하는 중입니다..."):
                try:
                    if client:
                        audio_file = io.BytesIO(audio_bytes)
                        audio_file.name = "audio.wav"
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1", file=audio_file, language="ko"
                        )
                        user_input_text = transcript.text
                    else:
                        user_input_text = (
                            "[STT 변환 임시 텍스트: 사용자가 음성을 입력했습니다.]"
                        )
                except Exception as e:
                    st.error(f"STT 에러 발생: {e}")
                    user_input_text = "[음성 인식 실패]"

    # 2. 텍스트 직접 입력 처리
    elif prompt:
        user_input_text = prompt

    # 입력값이 있을 경우 화면에 추가 및 AI 응답 요청
    if user_input_text:
        # User 메시지 추가
        st.session_state.messages.append({"role": "user", "content": user_input_text})
        st.markdown(
            f'<div style="display:flex; justify-content:flex-end;"><div class="user-message">{user_input_text}</div></div>',
            unsafe_allow_html=True,
        )

        # AI(LLM) 응답 생성
        with st.spinner("AI 면접관이 답변을 생성 중입니다..."):
            system_prompt = {
                "role": "system",
                "content": "당신은 IT 분야의 전문적이고 날카로운 면접관입니다. 사용자의 답변에 꼬리질문을 1~2개 정도 던집니다. 면접이 충분히 진행되었다고 판단되면 (대략 3~4턴 이상) 대화 마지막에 [INTERVIEW_END] 태그를 붙여주세요.",
            }
            api_messages = [system_prompt] + st.session_state.messages

            try:
                if client:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini", messages=api_messages, max_tokens=500
                    )
                    ai_reply = response.choices[0].message.content
                else:
                    ai_reply = (
                        "연결된 LLM 모듈이 없습니다. (.env의 OPENAI_API_KEY 확인 필요)"
                    )
            except Exception as e:
                ai_reply = f"응답 생성 중 오류가 발생했습니다: {e}"

            # 면접 종료 태그 감지
            if "[INTERVIEW_END]" in ai_reply:
                st.session_state.interview_ended = True
                ai_reply = ai_reply.replace("[INTERVIEW_END]", "").strip()

            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.markdown(
                f'<div style="display:flex; justify-content:flex-start;"><div style="display:flex; flex-direction:column;"><div class="sender-name">면접관</div><div class="ai-message">{ai_reply}</div></div></div>',
                unsafe_allow_html=True,
            )

            # --- TTS 오디오 생성 및 저장 ---
            # 여기서 st.audio를 바로 렌더링하고 st.rerun()을 해버리면 렌더링된 요소가 즉시 날아가버려서 소리가 나지 않습니다.
            # 따라서 session_state에 저장해두고 다음 리렌더링 사이클 상단에서 재생하도록 합니다.
            if client:
                try:
                    tts_response = client.audio.speech.create(
                        model="tts-1",
                        voice="onyx",  # 면접관 느낌의 낮은 목소리
                        input=ai_reply,
                    )
                    st.session_state.latest_audio_content = tts_response.content
                except Exception as e:
                    st.error(f"TTS 재생 중 오류 발생: {e}")

            st.rerun()

    # 면접 수동 종료 버튼
    if st.button("면접 수동 종료"):
        st.session_state.interview_ended = True
        st.rerun()

else:
    # --- 면접 종료 후 결과 화면 ---
    st.divider()
    st.success("🎉 면접이 종료되었습니다. 수고하셨습니다.")

    st.subheader("💡 면접 결과 및 피드백")

    with st.spinner("결과를 분석 중입니다..."):
        # 전체 대화 내용을 바탕으로 피드백을 요청하는 LLM 호출
        eval_prompt = "다음은 사용자와 AI 면접관의 대화 내역입니다. 이를 바탕으로 사용자의 프레젠테이션/답변 능력에 대해 합격/불합격 여부(임의 판단 가능), 총점(100점 만점), 강점 2가지, 약점 및 개선점 2가지를 마크다운 형식으로 간단히 정리해주세요.\n\n"
        for m in st.session_state.messages[1:]:  # 첫 인사말 제외
            role_str = "면접관" if m["role"] == "assistant" else "지원자"
            eval_prompt += f"{role_str}: {m['content']}\n"

        try:
            if client:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": eval_prompt}],
                    max_tokens=1000,
                )
                evaluation = response.choices[0].message.content
            else:
                evaluation = "평가 결과 (임시): 잘 하셨습니다. [API 연동 안됨]"
        except Exception as e:
            evaluation = "평가 생성 중 오류 표시"

    st.markdown(evaluation)

    # 텍스트 다운로드 (대화 스크립트)
    script_text = ""
    for m in st.session_state.messages:
        role_str = "AI 면접관" if m["role"] == "assistant" else "본인"
        script_text += f"[{role_str}] {m['content']}\n"

    st.download_button(
        label="📄 대화 스크립트 다운로드 (.txt)",
        data=script_text.encode("utf-8"),
        file_name="interview_script.txt",
        mime="text/plain",
    )

    # 처음으로 돌아가기
    if st.button("다시 시작하기"):
        st.session_state.messages = []
        st.session_state.interview_ended = False
        st.rerun()
