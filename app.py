import streamlit as st
import datetime
import pandas as pd

# 1. 데이터베이스 대용 세션 상태 초기화
if "board_data" not in st.session_state:
    st.session_state.board_data = [
        {"user": "학생_홍길동", "sentence": "I active study English yesterday.", "feedback": "⚠️ 시제 오류 발견! 'yesterday'가 있으니 과거형 동사를 사용해 보세요.", "date": "2026-06-12 14:20:10"}
    ]

if "user_logs" not in st.session_state:
    st.session_state.user_logs = [
        {"timestamp": "2026-06-12 14:19:55", "student_id": "학생_홍길동", "sentence": "I active study English yesterday.", "error_type": "동사 시제 및 형태 오류"}
    ]

# 교육공학적 AI 피드백 규칙 함수 (Scaffolding 모델 적용)
def generate_educational_feedback(sentence):
    sentence_lower = sentence.lower().strip()
    
    # 1. 너무 짧은 문장
    if len(sentence.split()) < 3:
        return "⚠️ 문장 구조가 너무 단순해요. 주어, 동사, 목적어/보어를 갖춘 완전한 문장으로 확장해 볼까요?", "문장 구조 미달"
    
    # 2. 흔한 시제/부사 오류 예시 (과거 부사인데 현재형 동사)
    if "yesterday" in sentence_lower and "study" in sentence_lower and "studied" not in sentence_lower:
        return "💡 과거의 일을 말할 때는 동사도 과거형태여야 해요. 'yesterday'와 어울리는 동사 형태를 생각해 보세요!", "동사 시제 오류"
    
    # 3. 학술적 표현 추천 (think 과도하게 사용 시)
    if "i think" in sentence_lower:
        return "✍️ 'I think'는 훌륭한 표현이지만, 조금 더 학술적이거나 주장을 명확히 하고 싶다면 'I believe'나 'I contend' 같은 표현을 추천해요.", "어휘 확장 제안"
        
    # 기본 격려 피드백
    return "✅ 훌륭한 문장입니다! 주어와 동사의 수 일치 및 시제가 매끄럽게 연결되었습니다. 낭독하며 자신감을 귀로 확인해 보세요.", "정상 문장"

# --- UI 레이아웃 시작 ---
st.set_page_config(page_title="AI-Assisted LMS Prototype", layout="wide")

st.title("🎓 에듀테크 기반 영어 글쓰기 유사 LMS")
st.write("교육공학적 설계가 반영된 AI 피드백 및 교사/학생 다중 역할 대시보드 프로토타입입니다.")

# 사이드바에서 역할 분류 (교사와 학생)
st.sidebar.header("👤 시스템 역할 선택")
user_role = st.sidebar.radio("당신의 역할은 무엇입니까?", ["학생 (Learner)", "교사 (Instructor)"])

# ==================== [학생 모드] ====================
if user_role == "학생 (Learner)":
    st.subheader("📝 학생 전용 학습 공간")
    
    tab1, tab2 = st.tabs(["✍️ 문장 작성 및 피드백", "📋 동료 공유 게시판"])
    
    with tab1:
        st.markdown("### 오늘의 영어 문장 연습")
        student_name = st.text_input("본인의 이름을 입력하세요:", value="새내기_학습자")
        user_input = st.text_input("연습할 영어 문장을 입력하세요:", placeholder="예: I think studying English is dynamic.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🤖 AI 교육적 피드백 받기"):
                if user_input.strip():
                    feedback, error_type = generate_educational_feedback(user_input)
                    st.session_state.current_feedback = feedback
                    st.session_state.current_error_type = error_type
                    
                    # 교사가 볼 수 있도록 전체 데이터 로그에 기록
                    log_entry = {
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "student_id": student_name,
                        "sentence": user_input,
                        "error_type": error_type
                    }
                    st.session_state.user_logs.append(log_entry)
                else:
                    st.warning("문장을 입력해 주세요.")
                    
        if "current_feedback" in st.session_state and user_input:
            st.info(f"**AI 교수학습 피드백:**\n\n{st.session_state.current_feedback}")
            
            with col2:
                if st.button("🚀 동료 게시판에 이 문장 공유하기"):
                    post = {
                        "user": student_name,
                        "sentence": user_input,
                        "feedback": st.session_state.current_feedback,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.board_data.insert(0, post)
                    st.success("게시판에 성공적으로 공유되었습니다! 다른 친구들의 문장도 확인해 보세요.")
                    del st.session_state.current_feedback

    with tab2:
        st.markdown("### 📋 동료 학습 게시판")
        st.caption("다른 학생들의 문장과 AI 피드백을 보며 함께 학습(Peer Learning)하는 공간입니다.")
        st.markdown("---")
        
        if not st.session_state.board_data:
            st.write("아직 공유된 문장이 없습니다.")
        else:
            for post in st.session_state.board_data:
                st.markdown(f"**👤 {post['user']}** <small style='color:gray;'>({post['date']})</small>", unsafe_allow_html=True)
                st.write(f"✍️ **제출 문장:** {post['sentence']}")
                st.caption(f"🤖 **AI 피드백:** {post['feedback']}")
                st.markdown("---")

# ==================== [교사 모드] ====================
else:
    st.subheader("📊 교사 전용 관리자 대시보드")
    st.write("학생들의 학습 데이터와 오류 유형 통계를 실시간으로 모니터링하여 맞춤형 오프라인 지도를 설계할 수 있습니다.")
    
    if not st.session_state.user_logs:
        st.write("아직 누적된 학생들의 학습 데이터가 없습니다.")
    else:
        # 데이터프레임 변환
        df = pd.DataFrame(st.session_state.user_logs)
        
        # 상단 핵심 지표 요약
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="총 누적 학습 문장 수", value=f"{len(df)}건")
        with col2:
            most_common_error = df["error_type"].mode()[0] if not df.empty else "없음"
            st.metric(label="가장 많이 발생한 오류 유형", value=most_common_error)
            
        st.markdown("### 📈 실시간 학생 활동 로그 (LRS 데이터)")
        st.dataframe(df, use_container_width=True)
        
        st.markdown("### 🔍 주요 오류 유형 분포")
        error_counts = df["error_type"].value_counts()
        st.bar_chart(error_counts)
