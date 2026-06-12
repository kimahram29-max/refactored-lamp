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
# 🔒 [구글 계정 연동] 인자 오류 수정한 보안 구역
# ==========================================
# 에러가 발생하던 인자 생성을 생략하고, Secrets에서 값을 직접 대입하는 방식으로 우회
authenticator = Authenticate(
    cookie_name="lms_oauth_cookie",
    cookie_key=st.secrets["google_auth"]["cookie_secret"],
    cookie_expiry_days=1
)

# Secrets 매핑 데이터를 안전하게 세팅
authenticator.client_id = st.secrets["google_auth"]["client_id"]
authenticator.client_secret = st.secrets["google_auth"]["client_secret"]
authenticator.redirect_uri = st.secrets["google_auth"]["redirect_uri"]

# 로그인 상태 확인 구동
authenticator.check_authentification()

if not st.session_state.get("connected", False):
    st.markdown("""
        <div class='login-container'>
            <h2>🎓 스마트 AI LMS 로그인</h2>
            <p>안전한 데이터 보호를 위해 구글 계정 연동이 필요합니다.<br>아래 버튼을 눌러 본인 인증을 진행해 주세요.</p>
        </div>
    """, unsafe_allow_html=True)
    
    authenticator.login()
    st.stop()

else:
    # 로그인 성공 시 유저 정보 할당
    user_email = st.session_state.get("user_info", {}).get("email", "unknown@gmail.com")
    user_name = st.session_state.get("user_info", {}).get("name", "사용자")
    
    # 역할 부여 로직
    if user_email not in st.session_state.user_role_dict:
        st.markdown(f"""
            <div class='login-container'>
                <h2>🌱 역할 등록 안내</h2>
                <p><b>{user_name} ({user_email})</b>님, 반갑습니다!<br>이 계정으로 사용할 시스템 역할을 선택해 주세요.</p>
            </div>
        """, unsafe_allow_html=True)
        
        selected_role = st.selectbox("시스템 권한을 선택하세요:", ["선택하세요", "🌱 학생 (Learner) 모드", "💼 교사 (Instructor) 모드"], key="first_role_select")
        if st.button("역할 등록 완료", use_container_width=True):
            if selected_role != "선택하세요":
                st.session_state.user_role_dict[user_email] = selected_role
                st.rerun()
            else:
                st.error("⚠️ 역할을 반드시 선택해야 진입할 수 있습니다.")
        st.stop()

    current_role = st.session_state.user_role_dict[user_email]

    # ==========================================
    # 🔓 메인 대시보드 애플리케이션 진입
    # ==========================================
    with st.sidebar:
        st.markdown(f"<h3 style='text-align: center; color:#F1F5F9;'>👤 {user_name}님</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;' class='user-profile'>{user_email}</p>", unsafe_allow_html=True)
        st.info(f"현재 권한: {current_role}")
        st.write("---")
        
        if "학생" in current_role:
            st.markdown("### 🔑 클래스 코드 등록")
            join_code = st.text_input("선생님께 받은 코드 입력:", placeholder="예: ENG-W72B", key="join_class_input").strip()
            if st.button("클래스 등록하기", use_container_width=True):
                if join_code in st.session_state.classes:
                    if user_email not in st.session_state.classes[join_code]["students"]:
                        st.session_state.classes[join_code]["students"].append(user_email)
                    if join_code not in st.session_state.my_classes:
                        st.session_state.my_classes.append(join_code)
                    st.success(f"🎉 '{st.session_state.classes[join_code]['name']}' 등록 완료!")
                    st.rerun()
                else:
                    st.error("⚠️ 존재하지 않는 클래스 코드입니다.")
            st.write("---")
            
        if st.button("🚪 로그아웃", use_container_width=True):
            authenticator.logout()
            st.rerun()
            
        st.write("---")
        st.markdown("<small style='color:#94A3B8;'>EduTech LMS v2.2</small>", unsafe_allow_html=True)

    st.markdown("<h1 class='main-title'>🚀 스마트 AI 영어 글쓰기 놀이터</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>구글 인증을 통해 동명이인 걱정 없이 안전하게 빌드업하는 포트폴리오 대시보드 📝🌱</p>", unsafe_allow_html=True)
    st.markdown("---")

    # ==================== [학생 화면 분기] ====================
    if "학생" in current_role:
        st.markdown("### ✍️ 학습자 전용 공간")
        
        if not st.session_state.my_classes:
            st.warning("⚠️ 먼저 사이드바에서 선생님이 생성하신 클래스 코드를 등록해 주세요!")
        else:
            sc_col1, sc_col2 = st.columns(2)
            with sc_col1:
                selected_class = st.selectbox("현재 가입된 클래스 선택:", st.session_state.my_classes)
                class_info = st.session_state.classes[selected_class]
            with sc_col2:
                selected_board = st.selectbox("제출 및 조회할 게시판 선택:", class_info["boards"])
                
            st.caption(f"📍 소속: {class_info['name']} ({selected_class})  >  구역: {selected_board}")
            
            tab1, tab2 = st.tabs(["✨ AI랑 문장 연습하기", "👭 친구들 생각 훔쳐보기 (게시판)"])
            
            with tab1:
                st.markdown(f"""
                    <div class='custom-card'>
                        <h4>📝 [{selected_board}] 문장 제출소</h4>
                        <p>선택한 게시판의 목적에 맞는 영어 문장을 적어보세요. AI 튜터가 피드백을 제공합니다.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                user_input = st.text_input("영어 문장 입력", placeholder="여기에 영어 문장을 적으세요!", key="main_english_input")
                
                btn_col1, btn_col2 = st.columns([1, 2])
                with btn_col1:
                    if st.button("🤖 AI 튜터에게 피드백 받기", use_container_width=True, key="get_feedback_btn"):
                        if user_input.strip():
                            feedback, error_type = generate_educational_feedback(user_input)
                            st.session_state.current_feedback = feedback
                            st.session_state.current_error_type = error_type
                            
                            log_entry = {
                                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "class_code": selected_class,
                                "board_name": selected_board,
                                "student_email": user_email,
                                "sentence": user_input,
                                "error_type": error_type
                            }
                            st.session_state.user_logs.append(log_entry)
                        else:
                            st.error("⚠️ 문장을 먼저 입력해야 AI 튜터가 도와줄 수 있어요!")
                            
                if "current_feedback" in st.session_state and user_input:
                    st.markdown("#### 🤖 AI 튜터의 다정한 힌트")
                    if "🎉" in st.session_state.current_feedback:
                        st.success(st.session_state.current_feedback)
                    else:
                        st.info(st.session_state.current_feedback)
                    
                    with btn_col2:
                        if st.button("🚀 이 문장과 피드백을 게시판에 공유하기", use_container_width=True, key="share_board_btn"):
                            post = {
                                "class": selected_class,
                                "board_name": selected_board,
                                "user_email": user_email,
                                "user_name": user_name,
                                "sentence": user_input,
                                "feedback": st.session_state.current_feedback,
                                "date": datetime.datetime.now().strftime("%m-%d %H:%M")
                            }
                            st.session_state.board_data.insert(0, post)
                            st.toast(f"'{selected_board}' 게시판에 성공적으로 공유되었어요! 🎉")
                            del st.session_state.current_feedback
                            st.rerun()

            with tab2:
                st.markdown(f"### 📋 동료 학습 게시판 [{selected_board}]")
                st.write("현재 선택한 특정 게시판 구역에 공유된 문장들만 모아 읽어봅니다.")
                st.markdown("---")
                
                filtered_board = [p for p in st.session_state.board_data if p["class"] == selected_class and p["board_name"] == selected_board]
                
                if not filtered_board:
                    st.write("이 게시판 구역에 아직 등록된 문장이 없어요. 첫 번째 주인공이 되어보세요!")
                else:
                    for post in filtered_board:
                        st.markdown(f"""
                            <div class='board-card'>
                                <div class='board-user'>👤 {post['user_name']} <span style='font-size:11px; color:#94A3B8;'>({post['user_email']})</span> <span class='board-tag'>{post['board_name']}</span> <span style='color: #94A3B8; font-size: 12px; font-weight: normal; float: right;'>{post['date']}</span></div>
                                <div class='board-sentence'><b>✍️ 작성 문장:</b> {post['sentence']}</div>
                                <div class='board-feedback'><b>💡 받은 AI 피드백:</b> {post['feedback']}</div>
                            </div>
                        """, unsafe_allow_html=True)

    # ==================== [교사 화면 분기] ====================
    else:
        st.markdown("### 📊 선생님 전용 관리자 대시보드")
        
        c_tab1, c_tab2, c_tab3 = st.tabs(["🏫 클래스 개설 및 코드", "📋 클래스별 세부 게시판 관리", "📈 데이터 분석 대시보드"])
        
        with c_tab1:
            st.markdown("#### 🆕 새로운 클래스 개설하기")
            new_class_name = st.text_input("클래스 이름 입력 (예: 멀티미디어와 영어교육 A분반):", placeholder="개설할 분반 명칭을 적어주세요.")
            
            if st.button("🛠️ 클래스 생성 및 코드 발급"):
                if new_class_name.strip():
                    random_code = "ENG-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
                    st.session_state.classes[random_code] = {
                        "name": new_class_name, 
                        "teacher_email": user_email, 
                        "teacher_name": user_name,
                        "students": [],
                        "boards": ["📢 공지사항 및 자유게시판"]
                    }
                    st.success(f"🎉 클래스가 개설되었습니다! **코드: {random_code}**")
                else:
                    st.error("⚠️ 클래스 이름을 입력해 주세요!")
            
            st.write("---")
            st.markdown("#### 📋 현재 운영 중인 클래스 목록")
            for code, info in st.session_state.classes.items():
                st.markdown(f"""
                    <div class='class-box'>
                        <b>🏫 클래스명:</b> {info['name']} | <b>🔑 가입 코드: <span style='color:#1D4ED8;'>{code}</span></b><br>
                        👥 <b>참여 학생 수:</b> {len(info['students'])}명 ({', '.join(info['students']) if info['students'] else '등록된 학생 없음'})<br>
                        🗂️ <b>개설된 게시판 개수:</b> {len(info['boards'])}개
                    </div>
                """, unsafe_allow_html=True)
                
        with c_tab2:
            st.markdown("#### 🛠️ 클래스별 게시판 생성 및 삭제 관리")
            all_codes = list(st.session_state.classes.keys())
            
            if not all_codes:
                st.warning("개설된 클래스가 없습니다. 첫 번째 탭에서 클래스를 먼저 만들어주세요.")
            else:
                target_class_for_board = st.selectbox("게시판을 관리할 대상 클래스를 지정하세요:", all_codes, format_func=lambda x: f"{st.session_state.classes[x]['name']} ({x})", key="mg_board_select")
                
                st.write("")
                st.markdown(f"##### 🆕 [{st.session_state.classes[target_class_for_board]['name']}] 내부에 새 게시판 만들기")
                
                new_board_title = st.text_input("새 게시판 이름 (예: 📝 중간고사 대체 에세이 제출방):", placeholder="생성할 게시판 명칭을 작성해 주세요.")
                
                if st.button("➕ 게시판 개설하기"):
                    if new_board_title.strip():
                        if new_board_title in st.session_state.classes[target_class_for_board]["boards"]:
                            st.error("⚠️ 이미 동일한 이름을 가진 게시판이 존재합니다.")
                        else:
                            st.session_state.classes[target_class_for_board]["boards"].append(new_board_title.strip())
                            st.success(f"🎉 '{new_board_title}' 게시판이 성공적으로 개설되었습니다!")
                            st.rerun()
                    else:
                        st.error("⚠️ 게시판 이름을 작성해 주세요!")
                        
                st.write("---")
                st.markdown("##### 📁 현재 개설된 게시판 현황")
                for b_name in st.session_state.classes[target_class_for_board]["boards"]:
                    st.text(f"• {b_name}")

        with c_tab3:
            st.markdown("#### 🔍 클래스별 학습 분석")
            all_class_codes = list(st.session_state.classes.keys())
            
            if not all_class_codes:
                st.warning("먼저 클래스를 생성해 주세요.")
            else:
                target_class = st.selectbox("데이터를 조회할 클래스를 선택하세요:", all_class_codes, format_func=lambda x: f"{st.session_state.classes[x]['name']} ({x})", key="analysis_class_select")
                
                df_all = pd.DataFrame(st.session_state.user_logs)
                df = df_all[df_all["class_code"] == target_class] if not df_all.empty else pd.DataFrame()
                
                if df.empty:
                    st.info(f"💡 해당 클래스({st.session_state.classes[target_class]['name']})에 아직 수집된 학습 데이터가 없습니다.")
                else:
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        st.markdown(f"""
                            <div style='background-color: #EFF6FF; padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #BFDBFE;'>
                                <p style='color: #1D4ED8; margin: 0; font-size: 16px; font-weight: bold;'>📈 반 누적 연습 문장 수</p>
                                <h2 style='color: #1E40AF; margin: 10px 0 0 0;'>{len(df)}건</h2>
                            </div>
                        """, unsafe_allow_html=True)
                    with m_col2:
                        most_common_error = df["error_type"].mode()[0] if not df["error_type"].empty else "없음"
                        st.markdown(f"""
                            <div style='background-color: #FEF2F2; padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #FCA5A5;'>
                                <p style='color: #991B1B; margin: 0; font-size: 16px; font-weight: bold;'>🔍 반내 최다 발생 오류</p>
                                <h2 style='color: #7F1D1D; margin: 10px 0 0 0;'>{most_common_error}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    st.write("")
                    
                    g_col1, g_col2 = st.columns([3, 2])
                    with g_col1:
                        st.markdown(f"##### 🕒 {st.session_state.classes[target_class]['name']} 실시간 활동 기록")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                    with g_col2:
                        st.markdown("##### 📊 오류 분포 시각화")
                        error_counts = df["error_type"].value_counts()
                        st.bar_chart(error_counts, color="#3B82F6")
