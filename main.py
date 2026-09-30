import time
import streamlit as st

# Page Configuration
st.set_page_config(page_title="방과 후의 학교", page_icon="🏫", layout="centered")

# ---------------------------------------------------------
# 1. Custom CSS (게임 UI 스타일링)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* 배경 및 전체 컨테이너 느낌 수정 */
    .stApp {
        background-color: #1a1a24;
        color: #e0e0e0;
    }
    /* 대사 상자 스타일링 */
    .dialogue-box {
        background-color: rgba(20, 20, 30, 0.85);
        border: 2px solid #5a5a7a;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 20px;
        min-height: 120px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .speaker-name {
        color: #ffaa00;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 8px;
    }
    /* 버튼 커스텀 */
    div.stButton > button {
        width: 100%;
        background-color: #2b2b3d;
        color: #ffffff;
        border: 1px solid #4a4a6a;
        padding: 12px;
        border-radius: 8px;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #4a4a6a;
        border-color: #ffaa00;
        color: #ffaa00;
    }
    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. 게임 상태(Session State) 초기화
# ---------------------------------------------------------
if "scene" not in st.session_state:
    st.session_state.scene = "start"
if "courage" not in st.session_state:
    st.session_state.courage = 0
if "has_key" not in st.session_state:
    st.session_state.has_key = False
if "endings_found" not in st.session_state:
    st.session_state.endings_found = set()


# ---------------------------------------------------------
# 3. 헬퍼 함수: 한 글자씩 텍스트 출력
# ---------------------------------------------------------
def type_text(speaker, text, speed=0.03):
    """대사창 형태의 타자 효과 출력 함수"""
    placeholder = st.empty()
    displayed_text = ""
    
    for char in text:
        displayed_text += char
        html_content = f"""
        <div class="dialogue-box">
            <div class="speaker-name">[{speaker}]</div>
            <div>{displayed_text}</div>
        </div>
        """
        placeholder.markdown(html_content, unsafe_allow_html=True)
        time.sleep(speed)


# ---------------------------------------------------------
# 4. 장면(Scene) 컨트롤러
# ---------------------------------------------------------
st.title("🏫 방과 후의 비밀")
st.caption(f"수집한 엔딩: {len(st.session_state.endings_found)}/2 | 용기: {st.session_state.courage}")
st.divider()

# --- [장면 0: 시작 화면] ---
if st.session_state.scene == "start":
    st.write("노을빛이 진하게 물든 방과 후 5시. 교실에 혼자 남아있다.")
    type_text("나", "벌써 시간이 이렇게 됐네... 빨리 가방 싸서 집에 가야겠다.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚪 복도로 나간다"):
            st.session_state.scene = "hallway"
            st.rerun()
    with col2:
        if st.button("🔍 서랍 속을 둘러본다"):
            st.session_state.scene = "desk_search"
            st.rerun()

# --- [장면 1: 서랍 수색] ---
elif st.session_state.scene == "desk_search":
    type_text("나", "선생님 책상 옆에 녹슨 열쇠 하나가 떨어져 있다. 어디 열쇠지?")
    st.session_state.has_key = True
    
    if st.button("🔑 열쇠를 챙기고 복도로 나간다"):
        st.session_state.scene = "hallway"
        st.rerun()

# --- [장면 2: 복도] ---
elif st.session_state.scene == "hallway":
    type_text("시스템", "어두컴컴한 복도 끝, 닫혀있어야 할 과학실 문이 미세하게 열려있다.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧪 과학실로 들어간다"):
            st.session_state.courage += 1
            st.session_state.scene = "science_lab"
            st.rerun()
    with col2:
        if st.button("🏃 무시하고 정문으로 달린다"):
            st.session_state.scene = "ending_1"
            st.rerun()

# --- [장면 3: 과학실] ---
elif st.session_state.scene == "science_lab":
    if st.session_state.has_key:
        type_text("나", "가지고 있던 열쇠로 과학실 안쪽 보관함을 열었다! 안에서 비밀 수첩을 발견했다.")
        if st.button("📖 수첩을 열어본다"):
            st.session_state.scene = "ending_2"
            st.rerun()
    else:
        type_text("나", "과학실 안쪽 보관함이 잠겨있다. 열쇠가 있으면 열 수 있을 것 같은데...")
        if st.button("🔙 다시 복도로 나간다"):
            st.session_state.scene = "hallway"
            st.rerun()

# --- [엔딩 1] ---
elif st.session_state.scene == "ending_1":
    st.session_state.endings_found.add("Ending 1")
    st.error("🎬 BAD ENDING: 평범한 일상")
    type_text("시스템", "당신은 아무것도 확인하지 않은 채 학교를 빠져나왔습니다. 이상한 소문의 진실은 영원히 알 수 없습니다.")
    
    if st.button("🔄 처음부터 다시 하기"):
        st.session_state.scene = "start"
        st.session_state.courage = 0
        st.session_state.has_key = False
        st.rerun()

# --- [엔딩 2] ---
elif st.session_state.scene == "ending_2":
    st.session_state.endings_found.add("Ending 2")
    st.success("🎬 TRUE ENDING: 학교의 비밀 밝혀냄")
    type_text("시스템", "수첩 안에는 방과 후 학교에서 벌어지던 비밀 연구 기록이 적혀있었습니다!")
    
    if st.button("🔄 처음부터 다시 하기"):
        st.session_state.scene = "start"
        st.session_state.courage = 0
        st.session_state.has_key = False
        st.rerun()
