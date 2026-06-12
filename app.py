import streamlit as st
import hashlib
import datetime
import pandas as pd
import random
import string

# --- 페이지 설정 ---
st.set_page_config(page_title="AI-Assisted LMS Prototype", layout="wide", initial_sidebar_state="expanded")

# --- 커스텀 CSS ---
st.markdown("""
    <style>
        .main { background-color: #F8FAFC; }
        .main-title { color: #1E3A8A; font-weight: 800; }
        .custom-card { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border-left: 5px solid #3B82F6; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 세션 상태 초기화 (기존 데이터 구조 완벽 복구) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_db = {"student": "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"} # 1234 해시값
    st.session_state.user_role_dict = {}
    st.session_state.classes = {"ENG-A": {"name": "초급 영어 회화반", "boards": ["공지사항", "1주차 연습"]}}
    st.session_state.board_data = [] # 게시판 데이터
    st.session_state.user_logs = [] # AI 로그 데이터

def verify_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

# --- 로그인 / 회원가입 ---
if not st.session_state.logged_in:
    st.title("🎓 스마트 AI LMS 시스템")
    c1, c2 = st.tabs(["로그인", "회원가입"])
    with c1:
        u_id = st.text_input("아이디", key="l_id")
        u_pw = st.text_input("비밀번호", type="password", key="l_pw")
        if st.button("로그인"):
            if u_id in st.session_state.user_db and st.session_state.user_db[u_id] == verify_pw(u_pw):
                st.session_state.logged_in = True
                st.session_state.user_id = u_id
                st.session_state.role = "교사" if "teacher" in u_id else "학생"
                st.rerun()
    with c2:
        n_id = st.text_input("새 아이디", key="n_id")
        n_pw = st.text_input("새 비밀번호", type="password", key="n_pw")
        if st.button("가입하기"):
            st.session_state.user_db[n_id] = verify_pw(n_pw)
            st.success("가입 완료!")
    st.stop()

# --- 메인 대시보드 ---
st.sidebar.write(f"### 👤 {st.session_state.user_id}님 환영합니다.")
if st.sidebar.button("로그아웃"): st.session_state.logged_in = False; st.rerun()

st.markdown("<h1 class='main-title'>🚀 스마트 AI 영어 학습 시스템</h1>", unsafe_allow_html=True)

if st.session_state.role == "학생":
    st.subheader("✍️ 학습 활동소")
    selected_class = st.selectbox("클래스 선택", list(st.session_state.classes.keys()))
    sent = st.text_input("영어 문장을 작성하세요")
    if st.button("AI 피드백 요청"):
        feedback = "💡 문법이 아주 좋습니다!"
        st.session_state.board_data.append({"user": st.session_state.user_id, "text": sent, "feedback": feedback})
        st.success(feedback)
    
    st.write("### 📋 게시판")
    for b in st.session_state.board_data:
        st.markdown(f"<div class='custom-card'><b>{b['user']}</b>: {b['text']}<br><i>AI: {b['feedback']}</i></div>", unsafe_allow_html=True)

else:
    st.subheader("📊 교사 관리자 대시보드")
    if st.button("새 클래스 개설"):
        code = "ENG-" + "".join(random.choices(string.ascii_uppercase, k=3))
        st.session_state.classes[code] = {"name": "신규 분반", "boards": []}
        st.rerun()
    st.write("클래스 목록:", st.session_state.classes)
