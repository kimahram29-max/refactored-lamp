import streamlit as st
import datetime

# 1. 시스템 기본 설정 및 데이터베이스 대용 (세션 상태 초기화)
if "board_data" not in st.session_state:
    st.session_state.board_data = []  # 공유 게시판 데이터

if "user_logs" not in st.session_state:
    st.session_state.user_logs = []  # 개인 학습 데이터 로그

# 가상의 AI 피드백 함수 (실제 구현 시 OpenAI API 등으로 대체 가능)
def get_ai_feedback(sentence):
    if len(sentence.split()) < 3:
        return "문장이 조금 짧아요! 주어와 동사를 갖춘 완전한 문장으로 작성해 볼까요?"
    # 간단한 가상 피드백 규칙
    if "think" in sentence.lower():
        return "💡 'think' 대신 'believe'나 'assert'를 사용하면 더 학술적인 문장이 됩니다."
    return "✅ 문법적으로 훌륭한 문장입니다! 시제와 수 일치가 잘 맞네요."

# --- UI 레이아웃 시작 ---
st.title("🎓 에듀테크 101: AI 영어 글쓰기 학습 LMS")
st.write("영어 문장을 쓰고 AI의 피드백을 받은 뒤, 동료들과 공유해 보세요.")

# 탭 구성: 학습하기 / 공유 게시판 / 대시보드(데이터 기록)
tab1, tab2, tab3 = st.tabs(["📝 문장 학습하기", "📋 공유 게시판", "📊 학습 대시보드"])

# [Tab 1] 문장 학습하기
with tab1:
    st.header("오늘의 영어 한 줄 쓰기")
    user_input = st.text_input("영어 문장을 입력하세요:", placeholder="I think studying English is fun.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🤖 AI 피드백 받기"):
            if user_input.strip():
                # AI 피드백 생성 및 로그 기록
                feedback = get_ai_feedback(user_input)
                st.session_state.current_feedback = feedback
                
                # 로그 저장
                log_entry = {
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "sentence": user_input,
                    "feedback": feedback
                }
                st.session_state.user_logs.append(log_entry)
            else:
                st.warning("문장을 먼저 입력해 주세요!")

    # 피드백이 생성되었을 때만 화면에 표시 및 공유 버튼 활성화
    if "current_feedback" in st.session_state and user_input:
        st.info(f"**AI Feedback:** {st.session_state.current_feedback}")
        
        with col2:
            if st.button("🚀 게시판에 공유하기"):
                # 게시판 데이터 추가
                post = {
                    "user": "새내기_학생A",
                    "sentence": user_input,
                    "feedback": st.session_state.current_feedback,
                    "date": datetime.datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.board_data.insert(0, post) # 최신 글이 위로 오도록
                st.success("게시판에 성공적으로 공유되었습니다!")
                # 피드백 초기화
                del st.session_state.current_feedback

# [Tab 2] 공유 게시판
with tab2:
    st.header("동료들의 학습 게시판")
    if not st.session_state.board_data:
        st.write("아직 공유된 문장이 없습니다. 첫 번째 주인공이 되어보세요!")
    else:
        for idx, post in enumerate(st.session_state.board_data):
            with st.container():
                st.markdown(f"### 👤 {post['user']} <small style='color:gray;'>({post['date']})</small>", unsafe_allow_html=True)
                st.write(f"**작성 문장:** {post['sentence']}")
                st.caption(f"🤖 **받은 피드백:** {post['feedback']}")
                st.markdown("---")

# [Tab 3] 학습 대시보드 (데이터 기록)
with tab3:
    st.header("📊 나의 학습 데이터 기록")
    if not st.session_state.user_logs:
        st.write("아직 누적된 데이터가 없습니다. 문장을 작성하고 피드백을 받아보세요.")
    else:
        st.write(f"총 **{len(st.session_state.user_logs)}개**의 문장을 연습하셨습니다.")
        # 테이블 형태로 로그 시각화
        st.table(st.session_state.user_logs)
