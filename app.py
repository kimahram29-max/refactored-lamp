import streamlit as st
import hashlib
import datetime
import pandas as pd
import random
import string

# --- 페이지 설정 ---
st.set_page_config(page_title="스마트 AI LMS", layout="wide")

# --- 인증 관리 ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = None
    # 아이디: student / 비밀번호: 1234
    st.session_state.user_db = {"student": "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"}

def verify_pw(input_pw):
    return hashlib.sha256(input_pw.encode()).hexdigest()

# --- 데이터 상태 초기화 (기존 기능 복구) ---
if "classes" not in st.session_state:
    st.session_state.classes = {"ENG-A": {"name": "초급 영어 회화반", "boards": ["공지사항", "1주차 연습"]}}
    st.session_state.board_data = []
    st.session_state.user_logs = []
    st.session_state.my_classes = ["ENG-A"]

# ==========================================
# 🔒 로그인/회원가입 화면
# ==========================================
if not st.session_state.logged_in:
    st.title("🎓 스마트 AI LMS 로그인")
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        u_id = st.text_input("아이디", key="l_id")
        u_pw = st.text_input("비밀번호", type="password", key="l_pw")
        if st.button("로그인"):
            if u_id in st.session_state.user_db and st.session_state.user_db[u_id] == verify_pw(u_pw):
                st.session_state.logged_in = True
                st.session_state.user_id = u_id
                st.session_state.role = "교사" if "teacher" in u_id else "학생"
                st.rerun()
            else:
                st.error("정보가 일치하지 않습니다.")

    with tab2:
        n_id = st.text_input("새 아이디", key="n_id")
        n_pw = st.text_input("새 비밀번호", type="password", key="n_pw")
        if st.button("가입하기"):
            if n_id in st.session_state.user_db: st.error("이미 있는 아이디입니다.")
            else:
                st.session_state.user_db[n_id] = verify_pw(n_pw)
                st.success("가입 완료! 로그인하세요.")
    st.stop()

# ==========================================
# 🔓 메인 대시보드 (기존 기능들 다 복구됨)
# ==========================================
st.sidebar.title(f"👤 {st.session_state.user_id} ({st.session_state.role})")
if st.sidebar.button("로그아웃"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🚀 스마트 AI 영어 글쓰기 놀이터")

if st.session_state.role == "학생":
    # [기존 학생 기능]
    selected_class = st.selectbox("클래스 선택", st.session_state.my_classes)
    user_input = st.text_input("영어 문장 입력:")
    if st.button("AI 피드백 받기"):
        st.success("🤖 AI: 문장이 아주 훌륭해요!")
        st.session_state.board_data.append({"user": st.session_state.user_id, "text": user_input})

    st.write("---")
    st.subheader("📋 게시판")
    for post in st.session_state.board_data:
        st.write(f"**{post['user']}**: {post['text']}")

else:
    # [기존 교사 기능]
    st.subheader("📊 관리자 대시보드")
    if st.button("새 클래스 생성"):
        new_c = "ENG-" + "".join(random.choices(string.ascii_uppercase, k=3))
        st.session_state.classes[new_c] = {"name": "신규반", "boards": []}
        st.rerun()
    st.write(f"현재 클래스 목록: {list(st.session_state.classes.keys())}")
