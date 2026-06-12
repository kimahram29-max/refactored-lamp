import streamlit as st
import hashlib

# 기존 USER_DB를 세션 상태에 저장하여 앱이 재시작되어도 유지되게 합니다 (임시)
if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "student": "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"
    }

def verify_pw(input_pw):
    return hashlib.sha256(input_pw.encode()).hexdigest()

# 로그인/회원가입 탭 분리
tab1, tab2 = st.tabs(["로그인", "회원가입"])

with tab2:
    st.subheader("새 계정 만들기")
    new_id = st.text_input("사용할 아이디 입력", key="new_id")
    new_pw = st.text_input("사용할 비밀번호 입력", type="password", key="new_pw")
    
    if st.button("가입하기"):
        if new_id in st.session_state.user_db:
            st.error("이미 존재하는 아이디입니다.")
        elif new_id and new_pw:
            # 비밀번호 해시 저장
            st.session_state.user_db[new_id] = verify_pw(new_pw)
            st.success("회원가입 성공! '로그인' 탭에서 접속하세요.")
        else:
            st.warning("아이디와 비밀번호를 모두 입력해주세요.")

with tab1:
    # 기존 로그인 로직...
    user_id = st.text_input("아이디", key="login_id")
    user_pw = st.text_input("비밀번호", type="password", key="login_pw")
    if st.button("로그인"):
        if user_id in st.session_state.user_db and st.session_state.user_db[user_id] == verify_pw(user_pw):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("로그인 실패")
