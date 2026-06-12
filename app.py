import streamlit as st
import hashlib
import datetime
import pandas as pd
import random
import string

# --- 페이지 설정 ---
st.set_page_config(
    page_title="스마트 AI LMS", 
    layout="wide"
)

# --- 커스텀 스타일 (UI) ---
st.markdown("""
    <style>
        .main { background-color: #F8FAFC; }
        .login-box { max-width: 400px; margin: 100px auto; padding: 30px; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# --- 인증 데이터 (보안 해시 처리) ---
# 아이디: student / 비밀번호: 1234
# 아이디: teacher / 비밀번호: 1234
USER_DB = {
    "student": "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4",
    "teacher": "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"
}

def verify_pw(input_pw):
    return hashlib.sha256(input_pw.encode()).hexdigest()

# --- 세션 상태 초기화 ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = None
    
# [데이터베이스 대용 상태]
if "classes" not in st.session_state:
    st.session_state.classes = {"ENG-A": {"name": "초급 영어반", "boards": ["공지사항"]}}
    st.session_state.board_data = []

# --- 로그인 로직 ---
if not st.session_state.logged_in:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.title("🎓 로그인")
    user_id = st.text_input("아이디")
    user_pw = st.text_input("비밀번호", type="password")
    
    if st.button("로그인"):
        if user_id in USER_DB and verify_pw(user_pw) == USER_DB[user_id]:
            st.session_state.logged_in = True
            st.session_state.user_id = user_id
            st.session_state.role = "교사" if "teacher" in user_id else "학생"
            st.rerun()
        else:
            st.error("아이디나 비밀번호가 틀렸습니다.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 로그인 후 메인 대시보드 ---
st.sidebar.title(f"👤 {st.session_state.user_id} ({st.session_state.role})")
if st.sidebar.button("로그아웃"):
    st.session_state.logged_in = False
    st.rerun()

st.title(f"🚀 스마트 AI 영어 학습 시스템 [{st.session_state.role} 모드]")

if st.session_state.role == "학생":
    st.subheader("✍️ 학습 활동")
    sentence = st.text_input("영어 문장을 입력하세요:")
    if st.button("AI 피드백 받기"):
        st.info("💡 AI: 훌륭한 문장이에요! 문법적으로 완벽합니다.")
else:
    st.subheader("📊 관리자 대시보드")
    st.write("클래스 관리 및 학습 통계를 확인하세요.")
    if st.button("새 클래스 만들기"):
        new_code = "ENG-" + "".join(random.choices(string.ascii_uppercase, k=3))
        st.session_state.classes[new_code] = {"name": "신규반", "boards": []}
        st.success(f"새 클래스 {new_code} 생성 완료!")
