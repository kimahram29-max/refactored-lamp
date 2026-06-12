import streamlit as st
import datetime
import pandas as pd
import random
import string
from streamlit_google_auth import Authenticate

# --- 페이지 설정 ---
st.set_page_config(
    page_title="AI-Assisted LMS Prototype (Secure Auth)", 
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
        .login-container { max-width: 450px; margin: 60px auto; padding: 35px; background-color: #FFFFFF !important; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border: 1px solid #E2E8F0; text-align: center; }
        .login-container h2 { color: #1E3A8A !important; margin-top:0; }
        .login-container p { color: #64748B !important; font-size:14px; margin-bottom: 25px; }
        .class-box { background-color: #EFF6FF !important; padding: 15px; border-radius: 8px; border: 1px solid #BFDBFE; margin-bottom: 10px; }
        .board-tag { background-color: #E0F2FE !important; color: #0369A1 !important; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .user-profile { font-size: 13px; color: #64748B; }
    </style>
""", unsafe_allow_html=True)

# --- 데이터베이스 대용 세션 상태 초기화 ---
if "classes" not in st.session_state:
    st.session_state.classes = {
        "ENG-A반": {
            "name": "초급 영어 회화반", 
            "teacher_email": "teacher@gmail.com", 
            "teacher_name": "선생님",
            "students": ["student1@gmail.com"],
            "boards": ["📢 공지사항 및 자유게시판", "📝 1주차 시제 연습 동네"]
        }
    }

if "board_data" not in st.session_state:
    st.session_state.board_data = [
        {
            "class": "ENG-A반", 
            "board_name": "📝 1주차 시제 연습 동네",
            "user_email": "student1@gmail.com",
            "user_name": "홍길동", 
            "sentence": "I active study English yesterday.", 
            "feedback": "⚠️ 시제 오류 발견! 'yesterday'가 있으니 과거형 동사를 사용해 보세요.", 
            "date": "2026-06-12 14:20"
        }
    ]

if "user_logs" not in st.session_state:
    st.session_state.user_logs = [
        {"timestamp": "2026-06-12 14:19", "class_code": "ENG-A반", "board_name": "📝 1주차 시제 연습 동네", "student_email": "student1@gmail.com", "sentence": "I active study English yesterday.", "error_type": "동사 시제 오류"}
    ]

if "my_classes" not in st.session_state:
    st.session_state.my_classes = ["ENG-A반"]

if "user_role_dict" not in st.session_state:
    st.session_state.user_role_dict = {}

def generate_educational_feedback(sentence):
    sentence_lower = sentence.lower().strip()
    if len(sentence.split()) < 3:
        return "⚠️ 문장 구조가 너무 간단해요! 주어, 동사, 목적어를 갖춘 완전한 문장으로 조금 더 길게 써볼까요? 💭", "문장 구조 미달"
    if "yesterday" in sentence_lower and "study" in sentence_lower and "studied" not in sentence_lower:
        return "💡 과거의 특별한 순간('yesterday')을 이야기하고 있네요! 동사의 형태도 과거형으로 맞춰주면 어떨까요? 바꾸어 다시 입력해 보세요! ✨", "동사 시제 오류"
    if "i think" in sentence_lower:
        return "✍️ 'I think'는 훌륭한 표현이에요! 만약 조금 더 격식 있고 명확한 주장을 펼치고 싶다면 'I believe'나 'I contend' 같은 멋진 어휘로 업그레이드해 보는 걸 추천해요! 🚀", "어휘 확장 제안"
    return "🎉 와우! 문법과 표현이 아주 매끄럽고 훌륭한 문장이에요. 작성한 문장을 소리 내어 크게 3번 읽어보며 귀로 직접 확인해 보세요! 🗣️⭐", "정상 문장"

# ==========================================
# 🔒 [구글 계정 연동] 인자 오류 완전 수정 구역
# ==========================================
# 라이브러리가 요구하는 표준 방식(
