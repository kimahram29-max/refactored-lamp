import streamlit as st
import datetime
import pandas as pd

# --- 페이지 설정 (가장 먼저 실행되어야 함) ---
st.set_page_config(
    page_title="AI-Assisted LMS Prototype", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 커스텀 CSS 스타일링 (더 밝고 친근한 폰트 및 레이아웃) ---
st.markdown("""
    <style>
        /* 전체 배경 및 폰트 스타일 */
        .main {
            background-color: #FAFAFA;
        }
        h1 {
            color: #1E3A8A;
            font-family: 'Malgun Gothic', sans-serif;
            font-weight: 800;
        }
        h2, h3 {
            color: #2563EB;
            font-family: 'Malgun Gothic', sans-serif;
        }
        /* 카드 형태의 흰색 배경 박스 */
        .custom-card {
            background-color: #FFFFFF;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            margin-bottom: 20px;
            border-left: 5px solid #3B82F6;
        }
        /* 게시판 글 카드 스타일 */
        .board-card {
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #E5E7EB;
            margin-bottom: 15px;
        }
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

# --- 사이드바 디자인 (역할 분류) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 24px;'>🎈 서비스 모드</h1>", unsafe_allow_html=True)
    st.write("---")
    user_role = st.radio(
        "당신의 역할을 선택해 주세요:", 
        ["🌱 학생 (Learner) 모드", "💼 교사 (Instructor) 모드"],
        index=0
    )
    st.write("---")
    st.markdown("<small style='color:gray;'>EduTech LMS Prototype v1.2</small>", unsafe_allow_html=True)

# --- 메인 타이틀 ---
st.markdown("# 🚀 스마트 AI 영어 글쓰기 놀이터")
st.markdown("##### AI의 다정함 피드백을 받고, 친구들과 공유하며 데이터로 성장하는 우리들만의 대시보드 📝🌱")
st.markdown("---")

# ==================== [학생 모드] ====================
if "학생" in user_role:
    st.markdown("### ✍️ 학습자 전용 공간")
    
    tab1, tab2 = st.tabs(["✨ AI랑 문장 연습하기", "👭 친구들 생각 훔쳐보기 (게시판)"])
    
    with tab1:
        st.markdown("""
            <div class='custom-card'>
                <h4>📝 오늘 연습할 문장을 작성해 보아요!</h4>
                <p style='color: gray; font-size: 14px;'>문장을 작성하면 AI 튜터가 스스로 정답을 찾을 수 있도록 다정한 힌트(비계 설정)를 제공합니다.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # 이름과 입력창을 더 깔끔하게 배치
        col_name, col_input = st.columns([1, 3])
        with col_name:
            student_name = st.text_input("닉네임", value="영어꿈나무")
        with col_input:
            user_input = st.text_input("영어 문장 입력", placeholder="여기에 영어 문장을 적고 엔터를 누르거나 아래 버튼을 클릭하세요!")
        
        btn_col1, btn_col2 = st.columns([1, 2])
        with btn_col1:
            if st.button("🤖 AI 튜터에게 피드백 받기", use_container_width=True):
                if user_input.strip():
                    feedback, error_type = generate_educational_feedback(user_input)
                    st.session_state.current_feedback = feedback
                    st.session_state.current_error_type = error_type
                    
                    # 로그 기록
                    log_entry = {
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "student_id": student_name,
                        "sentence": user_input,
                        "error_type": error_type
                    }
                    st.session_state.user_logs.append(log_entry)
                else:
                    st.error("⚠️ 문장을 먼저 입력해야 AI 튜터가 도와줄 수 있어요!")
                    
        # 피드백이 있을 때 화사한 상자로 시각화
        if "current_feedback" in st.session_state and user_input:
            st.markdown("#### 🤖 AI 튜터의 다정한 힌트")
            # 정상 문장일 때는 초록색 상자, 오류 힌트일 때는 파란색 상자
            if "🎉" in st.session_state.current_feedback:
                st.success(st.session_state.current_feedback)
            else:
                st.info(st.session_state.current_feedback)
            
            with btn_col2:
                if st.button("🚀 이 문장과 피드백을 게시판에 공유하기", use_container_width=True):
                    post = {
                        "user": student_name,
                        "sentence": user_input,
                        "feedback": st.session_state.current_feedback,
                        "date": datetime.datetime.now().strftime("%m-%d %H:%M")
                    }
                    st.session_state.board_data.insert(0, post)
                    st.toast("게시판에 성공적으로 공유되었어요! 🎉")
                    del st.session_state.current_feedback
                    st.rerun()

    with tab2:
        st.markdown("### 📋 동료 학습 게시판")
        st.write("다른 친구들은 어떤 문장을 쓰고 어떤 힌트를 받았는지 살펴보며 함께 배워요! (Peer Learning)")
        st.markdown("---")
        
        if not st.session_state.board_data:
            st.write("아직 공유된 문장이 없어요. 첫 번째 주인공이 되어보세요! 🌟")
        else:
            for post in st.session_state.board_data:
                st.markdown(f"""
                    <div class='board-card'>
                        <span style='font-size: 18px; font-weight: bold;'>👤 {post['user']}</span> 
                        <span style='color: gray; font-size: 12px; float: right;'>{post['date']}</span>
                        <p style='margin-top: 10px; font-size: 16px; background-color: #F3F4F6; padding: 10px; border-radius: 6px;'>✍️ <b>작성 문장:</b> {post['sentence']}</p>
                        <p style='color: #1E40AF; font-size: 14px; margin-bottom: 0;'>💡 <b>받은 AI 피드백:</b> {post['feedback']}</p>
                    </div>
                """, unsafe_allow_html=True)

# ==================== [교사 모드] ====================
else:
    st.markdown("### 📊 선생님 전용 관리자 대시보드")
    st.write("학생들이 활동하며 남긴 학습 기록 데이터(LRS)를 실시간으로 분석하여 오프라인 수업 설계를 돕습니다.")
    st.markdown("---")
    
    if not st.session_state.user_logs:
        st.warning("아직 수집된 학생들의 학습 데이터가 존재하지 않습니다.")
    else:
        df = pd.DataFrame(st.session_state.user_logs)
        
        # 지표 카드를 더 예쁘고 눈에 띄게 배치
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown("""
                <div style='background-color: #EFF6FF; padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #BFDBFE;'>
                    <p style='color: #1D4ED8; margin: 0; font-size: 16px; font-weight: bold;'>📈 총 누적 학습 문장 수</p>
                    <h2 style='color: #1E40AF; margin: 10px 0 0 0;'>{}건</h2>
                </div>
            """.format(len(df)), unsafe_allow_html=True)
        with m_col2:
            most_common_error = df["error_type"].mode()[0] if not df.empty else "없음"
            st.markdown("""
                <div style='background-color: #FEF2F2; padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #FCA5A5;'>
                    <p style='color: #991B1B; margin: 0; font-size: 16px; font-weight: bold;'>🔍 가장 빈번한 오류 유형</p>
                    <h2 style='color: #7F1D1D; margin: 10px 0 0 0;'>{}</h2>
                </div>
            """.format(most_common_error), unsafe_allow_html=True)
            
        st.write("")
        st.write("")
        
        # 레이아웃을 쪼개서 왼쪽은 로그 표, 오른쪽은 시각화 그래프 배치
        g_col1, g_col2 = st.columns([3, 2])
        
        with g_col1:
            st.markdown("##### 🕒 실시간 학습 활동 로그 (LRS 데이터 수집)")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        with g_col2:
            st.markdown("##### 📊 주요 오류 유형 발생 분포")
            error_counts = df["error_type"].value_counts()
            st.bar_chart(error_counts, color="#3B82F6")
