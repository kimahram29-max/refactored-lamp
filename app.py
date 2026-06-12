import streamlit as st
import datetime
import pandas as pd

# --- 페이지 설정 ---
st.set_page_config(
    page_title="AI-Assisted LMS Prototype", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 다크/라이트 모드 통합 방어 커스텀 CSS ---
st.markdown("""
    <style>
        .main { background-color: #F8FAFC; }
        .main-title { color: #1E3A8A !important; font-family: 'Malgun Gothic', sans-serif; font-weight: 800; margin-bottom: 5px; }
        .sub-title { color: #475569 !important; font-size: 16px; margin-bottom: 25px; }
        .custom-card {
            background-color: #FFFFFF !important; padding: 25px; border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 25px; border-left: 6px solid #3B82F6;
        }
        .custom-card h4 { color: #1E293B !important; font-weight: bold; margin-top: 0; margin-bottom: 10px; }
        .custom-card p { color: #64748B !important; font-size: 14px; margin-bottom: 0; }
        .board-card { background-color: #FFFFFF !important; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
        .board-user { color: #1E293B !important; font-size: 16px; font-weight: bold; }
        .board-sentence { margin-top: 10px; font-size: 15px; background-color: #F8FAFC !important; color: #334155 !important; padding: 12px; border-radius: 8px; border-left: 3px solid #CBD5E1; }
        .board-feedback { color: #2563EB !important; font-size: 14px; margin-bottom: 0; font-weight: 500; }
        .login-container { max-width: 450px; margin: 60px auto; padding: 35px; background-color: #FFFFFF !important; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border: 1px solid #E2E8F0; }
        .login-container h2 { color: #1E3A8A !important; }
        .login-container p { color: #64748B !important; }
    </style>
""", unsafe_allow_html=True)

# --- 데이터베이스 대용 세션 상태 초기화 ---
if "board_data" not in st.session_state:
    st.session_state.board_data = [
        {"user": "학생_홍길동", "sentence": "I active study English yesterday.", "feedback": "⚠️ 시제 오류 발견! 'yesterday'가 있으니 과거형 동사를 사용해 보세요.", "date": "2026-06-12 14:20"}
    ]
if "user_logs" not in st.session_state:
    st.session_state.user_logs = [
        {"timestamp": "2026-06-12 14:19", "student_id": "학생_홍길동", "sentence": "I active study English yesterday.", "error_type": "동사 시제 및 형태 오류"}
    ]
if "login_success" not in st.session_state:
    st.session_state.login_success = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""

# 교육공학적 AI 피드백 규칙 함수
def generate_educational_feedback(sentence):
    sentence_lower = sentence.lower().strip()
    if len(sentence.split()) < 3:
        return "⚠️ 문장 구조가 너무 간단해요! 주어, 동사, 목적어를 갖춘 완전한 문장으로 조금 더 길게 써볼까요? 💭", "문장 구조 미달"
    if "yesterday" in sentence_lower and "study" in sentence_lower and "studied" not in sentence_lower:
        return "💡 과거의 특별한 순간('yesterday')을 이야기하고 있네요! 동사의 형태도 과거형으로 맞춰주면 어떨까요? 바꾸어 다시 입력해 보세요! ✨", "동사 시제 오류"
    if "i think" in sentence_lower:
        return "✍️ 'I think'는 훌륭한 표현이에요! 만약 조금 더 격식 있고 명확한 주장을 펼치고 싶다면 'I believe'나 'I contend' 같은 멋진 어휘로 업그레이드해 보는 걸 추천해요! 🚀", "어휘 확장 제안"
    return "🎉 와우! 문법과 표현이 아주 매끄럽고 훌륭한 문장이에요. 작성한 문장을 소리 내어 크게 3번 읽어보며 귀로 직접 확인해 보세요! 🗣️⭐", "정상 문장"

# --- [로그인 화면 로직] ---
if not
