import time
import streamlit as st

# ---------------------------------------------------------
# 1. 페이지 및 CSS 커스텀
# ---------------------------------------------------------
st.set_page_config(
    page_title="휘명고등학교: 닫힌 교문",
    page_icon="🏫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* 전체 배경 검은색 */
    .stApp {
        background-color: #0b0c10;
        color: #c5c6c7;
    }
    header, footer { visibility: hidden; }

    /* 메인 타이틀 */
    .title-text {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        color: #66fcf1;
        letter-spacing: 5px;
        margin-top: 60px;
        margin-bottom: 40px;
        text-shadow: 0 0 20px rgba(102, 252, 241, 0.4);
    }

    /* 대사 상자 (비주얼 노블 스타일) */
    .dialogue-box {
        background: linear-gradient(180deg, rgba(20,24,33,0.95) 0%, rgba(11,12,16,0.98) 100%);
        border: 2px solid #45a29e;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 20px;
        min-height: 110px;
        box-shadow: 0 0 15px rgba(69, 162, 158, 0.2);
    }
    .speaker-name {
        color: #66fcf1;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 8px;
        border-bottom: 1px solid rgba(102, 252, 241, 0.2);
        padding-bottom: 4px;
    }
    .dialogue-text {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #e5e5e5;
    }

    /* 조사 카드 */
    .investigate-card {
        background-color: #1f2833;
        border-left: 4px solid #66fcf1;
        padding: 12px 16px;
        margin-bottom: 15px;
        border-radius: 4px;
    }

    /* 버튼 커스텀 */
    div.stButton > button {
        width: 100%;
        background-color: #1f2833;
        color: #c5c6c7;
        border: 1px solid #45a29e;
        padding: 14px 20px;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #45a29e;
        color: #0b0c10;
        box-shadow: 0 0 10px rgba(102, 252, 241, 0.5);
    }
    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. 게임 상태(Session State) 초기화
# ---------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "title"

if "state" not in st.session_state:
    st.session_state.state = {
        "scene": "intro",
        "inventory": set(),
        "clues": set(),
        "sanity": 100,
        "unlocked_lab": False,
        "endings": set(),
        "typewriter_seen": set()  # 타자 효과 중복 방지
    }

S = st.session_state.state


# ---------------------------------------------------------
# 3. 헬퍼 함수
# ---------------------------------------------------------
def render_dialogue(speaker, text, speed=0.02, scene_key=None):
    """타자 효과가 적용된 대사 상자"""
    # 이미 본 대사라면 타자 효과 없이 즉시 출력
    if scene_key and scene_key in S["typewriter_seen"]:
        html_code = f"""
        <div class="dialogue-box">
            <div class="speaker-name">[{speaker}]</div>
            <div class="dialogue-text">{text}</div>
        </div>
        """
        st.markdown(html_code, unsafe_allow_html=True)
        return

    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        html_code = f"""
        <div class="dialogue-box">
            <div class="speaker-name">[{speaker}]</div>
            <div class="dialogue-text">{displayed}</div>
        </div>
        """
        placeholder.markdown(html_code, unsafe_allow_html=True)
        time.sleep(speed)

    if scene_key:
        S["typewriter_seen"].add(scene_key)


def render_sidebar():
    """사이드바: 단서 및 상태창"""
    with st.sidebar:
        st.title("📂 조사 노트")
        st.metric(label="이성 수치 (Sanity)", value=f"{S['sanity']}%")
        st.divider()

        st.subheader("🔑 소지한 아이템")
        if S["inventory"]:
            for item in S["inventory"]:
                st.write(f"- {item}")
        else:
            st.caption("소지한 아이템이 없습니다.")

        st.divider()
        st.subheader("🧩 획득한 단서")
        if S["clues"]:
            for clue in S["clues"]:
                st.write(f"- {clue}")
        else:
            st.caption("수집된 단서가 없습니다.")

        st.divider()
        if st.button("🔴 메인 화면으로"):
            st.session_state.page = "title"
            st.rerun()


# ---------------------------------------------------------
# 4. 화면 로직
# ---------------------------------------------------------

# --- A. 타이틀 화면 ---
if st.session_state.page == "title":
    st.markdown('<div class="title-text">휘명고등학교<br><span style="font-size:1.5rem; color:#45a29e;">: 닫힌 교문</span></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("새로 시작하기"):
            # 세션 초기화
            S["scene"] = "intro"
            S["inventory"] = set()
            S["clues"] = set()
            S["sanity"] = 100
            S["unlocked_lab"] = False
            S["typewriter_seen"] = set()
            st.session_state.page = "game"
            st.rerun()

        if st.button("이어서하기"):
            if S["scene"] != "intro" or len(S["clues"]) > 0:
                st.session_state.page = "game"
                st.rerun()
            else:
                st.toast("저장된 데이터가 없습니다.", icon="⚠️")

        if len(S["endings"]) > 0:
            st.caption(f"🏆 수집한 엔딩: {len(S['endings'])}개")

# --- B. 게임 플레이 화면 ---
elif st.session_state.page == "game":
    render_sidebar()

    # [SCENE: 인트로]
    if S["scene"] == "intro":
        st.subheader("🏫 2026년 9월 30일, 방과 후 19:00")
        render_dialogue(
            "나",
            "정신을 차려보니 교실 안이었다. 창밖은 이미 칠흑 같은 어둠이 깔려있고, 학교 안에는 오직 적막만이 흐르고 있다. 분명 가방을 싸고 나가려 했었는데... 문이 밖에서 잠겨있다.",
            scene_key="intro_1"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 교실 안을 조사한다"):
                S["scene"] = "classroom"
                st.rerun()
        with col2:
            if st.button("🚪 뒷문을 강제로 열어본다"):
                S["sanity"] -= 10
                render_dialogue("시스템", "문은 덜컹거릴 뿐 열리지 않는다. 은근한 공포감이 밀려온다. (이성 -10)", scene_key="intro_door")

    # [SCENE: 교실 조사]
    elif S["scene"] == "classroom":
        st.subheader("📍 2학년 3반 교실")
        render_dialogue("나", "달빛만이 교실을 비추고 있다. 교탁 위와 선생님 책상이 눈에 띈다.", scene_key="classroom_main")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📂 교탁 위의 유기물 수첩 읽기"):
                S["clues"].add("암호 힌트: '탄소 6개로 이루어진 한 방향 유기구조'")
                render_dialogue("수첩", "'실험실 비밀번호는 가장 안정적인 6탄소 고리 구조의 이름을 영어로 입력할 것.'", scene_key="notebook")
        with col2:
            if st.button("🔑 선생님 책상 서랍 열기"):
                S["inventory"].add("동아리실 열쇠")
                render_dialogue("시스템", "서랍 안에서 [동아리실 열쇠]를 발견했다!", scene_key="drawer")

        st.divider()
        if st.button("🏃 복도로 나간다"):
            S["scene"] = "hallway"
            st.rerun()

    # [SCENE: 복도 - 거점 장소]
    elif S["scene"] == "hallway":
        st.subheader("📍 3층 중앙 복도")
        render_dialogue("나", "어두컴컴한 복도. 왼쪽에는 과학실이, 오른쪽에는 방송실이 있다.", scene_key="hallway_main")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧪 과학실로 이동"):
                S["scene"] = "science_lab"
                st.rerun()
        with col2:
            if st.button("🎙️ 동아리실로 이동"):
                if "동아리실 열쇠" in S["inventory"]:
                    S["scene"] = "club_room"
                    st.rerun()
                else:
                    render_dialogue("시스템", "문이 잠겨있다. 열쇠가 필요하다.", scene_key="club_locked")

        st.divider()
        if st.button("🏫 1층 중앙 현관으로 내려간다"):
            S["scene"] = "entrance"
            st.rerun()

    # [SCENE: 과학실 - 암호 퍼즐]
    elif S["scene"] == "science_lab":
        st.subheader("📍 3층 과학실")

        if not S["unlocked_lab"]:
            render_dialogue("전자 자물쇠", "비밀번호 입력 키패드가 반짝이고 있다.", scene_key="lab_pad")

            password = st.text_input("영어 단어를 입력하세요 (대소문자 무관):", key="lab_pwd_input")
            if st.button("확인"):
                if password.strip().lower() == "benzene":  # 벤젠
                    S["unlocked_lab"] = True
                    S["clues"].add("진실: 학교 지하실의 비인가 실험")
                    st.success("잠금장치가 해제되었습니다!")
                    st.rerun()
                else:
                    S["sanity"] -= 15
                    st.error("비밀번호가 틀렸습니다. 경고음이 복도에 울려 퍼집니다! (이성 -15)")

            if st.button("🔙 복도로 돌아가기"):
                S["scene"] = "hallway"
                st.rerun()
        else:
            render_dialogue("나", "과학실 문이 열렸다. 안쪽 책상 위에 비상탈출용 비상구 카드키가 놓여있다!", scene_key="lab_inside")
            S["inventory"].add("비상구 카드키")

            if st.button("🔙 복도로 돌아가기"):
                S["scene"] = "hallway"
                st.rerun()

    # [SCENE: 동아리실]
    elif S["scene"] == "club_room":
        st.subheader("📍 방송 동아리실")
        render_dialogue("나", "오래된 방송 장비들이 놓여있다. 벽면에 스크랩된 신문 기사가 붙어있다.", scene_key="club_main")

        S["clues"].add("신문 기사: '10년 전 방과 후 일어난 미스터리 한 전력 마비'")

        if st.button("🔙 복도로 돌아가기"):
            S["scene"] = "hallway"
            st.rerun()

    # [SCENE: 1층 현관 - 탈출 시도]
    elif S["scene"] == "entrance":
        st.subheader("📍 1층 중앙 현관")
        render_dialogue("나", "육중한 철문이 닫혀있다. 비상구 카드 태그 인식기와 일반 열쇠구멍이 함께 보인다.", scene_key="entrance_main")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💳 카드키 인식기에 태그"):
                if "비상구 카드키" in S["inventory"]:
                    S["scene"] = "ending_true"
                    st.rerun()
                else:
                    render_dialogue("시스템", "카드키가 없다.", scene_key="no_card")
        with col2:
            if st.button("🚪 강제로 틈새로 탈출 시도"):
                if S["sanity"] <= 30:
                    S["scene"] = "ending_bad"
                    st.rerun()
                else:
                    S["scene"] = "ending_normal"
                    st.rerun()

        if st.button("🔙 3층 복도로 돌아가기"):
            S["scene"] = "hallway"
            st.rerun()

    # --- C. 엔딩 연출 ---
    elif S["scene"] == "ending_true":
        S["endings"].add("True Ending")
        st.balloons()
        st.success("🎬 TRUE ENDING: 진실을 쥐고 탈출한 자")
        render_dialogue("시스템", "카드키가 작동하며 현관문이 열렸다. 당신은 학교의 비밀이 담긴 수첩과 단서를 가지고 무사히 밤의 학교를 빠져나왔습니다.", scene_key="end_t")
        if st.button("🔄 메인 화면으로"):
            st.session_state.page = "title"
            st.rerun()

    elif S["scene"] == "ending_normal":
        S["endings"].add("Normal Ending")
        st.warning("🎬 NORMAL ENDING: 찜찜한 평범한 귀가")
        render_dialogue("시스템", "경비 아저씨가 순찰을 돌다가 당신을 발견하고 문을 열어주었습니다. 하지만 오늘 밤 학교에서 무슨 일이 있었는지는 끝내 알 수 없었습니다.", scene_key="end_n")
        if st.button("🔄 메인 화면으로"):
            st.session_state.page = "title"
            st.rerun()

    elif S["scene"] == "ending_bad":
        S["endings"].add("Bad Ending")
        st.error("🎬 BAD ENDING: 어둠 속에 갇힌 공포")
        render_dialogue("시스템", "이성 수치를 잃고 패닉에 빠진 당신은 복도 구석에서 정신을 잃었습니다...", scene_key="end_b")
        if st.button("🔄 메인 화면으로"):
            st.session_state.page = "title"
            st.rerun()
