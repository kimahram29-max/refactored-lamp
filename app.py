import streamlit as st
import datetime
import pandas as pd
import random
import string
import hashlib
import json
import os

# --- 데이터 영구 저장을 위한 파일 경로 ---
DATA_FILE = "lms_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # 초기 데이터 구조
    return {
        "classes": {
            "ENG-A班": {
                "name": "초급 영어 회화반", 
                "teacher": "선생님", 
                "students": ["학생_홍길동", "영어꿈나무"],
                "boards": ["📢 공지사항 및 자유게시판", "📝 1주차 시제 연습 동네"]
            }
        },
        "board_data": [
            {
                "class": "ENG-A班", 
                "board_name": "📝 1주차 시제 연습 동네",
                "user": "학생_홍길동", 
                "sentence": "I active study English yesterday.", 
                "feedback": "⚠️ 시제 오류 발견! 'yesterday'가 있으니 과거형 동사를 사용해 보세요.", 
                "date": "2026-06-12 14:20"
            }
        ],
        "user_logs": [
            {"timestamp": "2026-06-12 14:19", "class_code": "ENG-A班", "board_name": "📝 1주차 시제 연습 동네", "student_id": "학생_홍길동", "sentence": "I active study English yesterday.", "error_type": "동사 시제 오류"}
        ],
        "user_db": {"admin": hashlib.sha256("1234".encode()).hexdigest()} # 초기 관리자 계정 1234
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 세션 상태 초기화 (파일에서 로드) ---
data_store = load_data()
if "data" not in st.session_state:
    st.session_state.data = data_store
if "login_success" not in st.session_state:
    st.session_state.login_success = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""
if "my_classes" not in st.session_state:
    st.session_state.my_classes = ["ENG-A班"]

# --- 페이지 설정 ---
st.set_page_config(page_title="AI-Assisted LMS Prototype", layout="wide", initial_sidebar_state="expanded")

# --- CSS (복구됨) ---
st.markdown("""
    <style>
        .main { background-color: #F8FAFC; }
        .main-title { color: #1E3A8A !important; font-family: 'Malgun Gothic', sans-serif; font-weight: 800; margin-bottom: 5px; }
        .sub-title { color: #475569 !important; font-size: 16px; margin-bottom: 25px; }
        .custom-card { background-color: #FFFFFF !important; padding: 25px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 25px; border-left: 6px solid #3B82F6; }
        .board-card { background-color: #FFFFFF !important; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
        .board-user { color: #1E293B !important; font-size: 16px; font-weight: bold; }
        .board-sentence { margin-top: 10px; font-size: 15px; background-color: #F8FAFC !important; color: #334155 !important; padding: 12px; border-radius: 8px; border-left: 3px solid #CBD5E1; }
        .board-feedback { color: #2563EB !important; font-size: 14px; margin-bottom: 0; font-weight: 500; }
        .login-container { max-width: 450px; margin: 60px auto; padding: 35px; background-color: #FFFFFF !important; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border: 1px solid #E2E8F0; }
        .class-box { background-color: #EFF6FF !important; padding: 15px; border-radius: 8px; border: 1px solid #BFDBFE; margin-bottom: 10px; }
        .board-tag { background-color: #E0F2FE !important; color: #0369A1 !important; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def generate_educational_feedback(sentence):
    sentence_lower = sentence.lower().strip()
    if len(sentence.split()) < 3:
        return "⚠️ 문장 구조가 너무 간단해요! 주어, 동사, 목적어를 갖춘 완전한 문장으로 조금 더 길게 써볼까요? 💭", "문장 구조 미달"
    if "yesterday" in sentence_lower and "study" in sentence_lower and "studied" not in sentence_lower:
        return "💡 과거의 특별한 순간('yesterday')을 이야기하고 있네요! 동사의 형태도 과거형으로 맞춰주면 어떨까요? 바꾸어 다시 입력해 보세요! ✨", "동사 시제 오류"
    return "🎉 와우! 문법과 표현이 아주 매끄럽고 훌륭한 문장이에요. 🗣️⭐", "정상 문장"

# --- 로그인 로직 (파일 저장 데이터와 연동) ---
if not st.session_state.login_success:
    st.markdown("<div class='login-container'><h2>🎓 스마트 AI LMS 시스템</h2></div>", unsafe_allow_html=True)
    input_name = st.text_input("이름:", key="login_name_input")
    input_role = st.selectbox("역할:", ["🌱 학생 (Learner) 모드", "💼 교사 (Instructor) 모드"], key="login_role_select")
    if st.button("안전 로그인"):
        st.session_state.login_success = True
        st.session_state.user_name = input_name
        st.session_state.user_role = input_role
        st.rerun()
    st.stop()

# --- 메인 본문 ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_name}")
    if st.button("🚪 로그아웃"):
        st.session_state.login_success = False; st.rerun()

st.markdown("<h1 class='main-title'>🚀 스마트 AI 영어 글쓰기 놀이터</h1>", unsafe_allow_html=True)

if "학생" in st.session_state.user_role:
    selected_class = st.selectbox("클래스 선택:", st.session_state.my_classes)
    class_info = st.session_state.data["classes"][selected_class]
    selected_board = st.selectbox("게시판 선택:", class_info["boards"])
    
    user_input = st.text_input("영어 문장 입력:")
    if st.button("AI 피드백"):
        feedback, error_type = generate_educational_feedback(user_input)
        post = {
            "class": selected_class,
            "board_name": selected_board,
            "user": st.session_state.user_name,
            "sentence": user_input,
            "feedback": feedback,
            "date": datetime.datetime.now().strftime("%m-%d %H:%M")
        }
        st.session_state.data["board_data"].insert(0, post)
        st.session_state.data["user_logs"].append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "class_code": selected_class, "board_name": selected_board,
            "student_id": st.session_state.user_name, "sentence": user_input, "error_type": error_type
        })
        save_data(st.session_state.data) # 변경 시 자동 저장
        st.success(feedback)

    for post in [p for p in st.session_state.data["board_data"] if p["class"] == selected_class]:
        st.markdown(f"<div class='board-card'><div class='board-user'>{post['user']}</div><div class='board-sentence'>{post['sentence']}</div><div class='board-feedback'>{post['feedback']}</div></div>", unsafe_allow_html=True)

else:
    st.subheader("📊 교사 관리 대시보드")
    # 교사 대시보드 로직...
    st.write("클래스 목록:", st.session_state.data["classes"])
    if st.button("클래스 생성"):
        code = "ENG-" + "".join(random.choices(string.ascii_uppercase, k=3))
        st.session_state.data["classes"][code] = {"name": "신규반", "boards": ["공지사항"]}
        save_data(st.session_state.data)
        st.rerun()
