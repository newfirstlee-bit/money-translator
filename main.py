import streamlit as st
import datetime
import time
import json
from database import init_db, get_news_by_date, save_news, get_briefing_by_date, save_briefing, get_last_update_time
from fetcher import fetch_naver_news
from analyzer import analyze_news, generate_briefing

# --- Page Config ---
st.set_page_config(
    page_title="매일 경제 브리핑",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif !important;
        color: #1a1a1a !important;
    }
    
    /* 사이트 배경 흰색 */
    .stApp, 
    .stApp > header,
    .stApp > div,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    .main,
    .block-container {
        background-color: #ffffff !important;
        background: #ffffff !important;
    }
    
    /* 모든 텍스트 요소 어두운 색상 */
    h1, h2, h3, h4, h5, h6, p, span, div, label, a {
        color: #1a1a1a !important;
    }
    
    .stMarkdown, .stText, .stCaption {
        color: #1a1a1a !important;
    }
    
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p {
        color: #1a1a1a !important;
    }
    
    .stCaption {
        color: #666666 !important;
    }
    
    /* 버튼 스타일 */
    .stButton > button,
    .stButton > button > div,
    .stButton > button > div > p,
    .stButton > button span,
    .stButton button * {
        color: #ffffff !important;
        background-color: transparent !important;
    }
    
    .stButton > button {
        background-color: #1a1a1a !important;
    }
    
    .stButton > button:hover {
        background-color: #333333 !important;
    }
    
    .stLinkButton > a,
    .stLinkButton > a > div,
    .stLinkButton > a > div > p,
    .stLinkButton a * {
        color: #ffffff !important;
    }
    
    .stLinkButton > a {
        background-color: #1a1a1a !important;
    }
    
    /* 사이드바 */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
        padding-bottom: 0 !important;
    }
    
    [data-testid="stSidebar"] > div {
        padding-bottom: 0 !important;
    }
    
    /* 앵커 링크 아이콘 숨기기 */
    /* 앵커 링크 아이콘 숨기기 (강력 적용) */
    .stMarkdown h1 a,
    .stMarkdown h2 a,
    .stMarkdown h3 a,
    .stMarkdown h4 a,
    .stMarkdown h5 a,
    .stMarkdown h6 a,
    a.header-link,
    a[data-testid="StyledLinkIconContainer"],
    [data-testid="StyledLinkIconContainer"],
    .css-zt5igj,
    .st-emotion-cache-1h9usn1 {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
    }
    
    /* 전체 페이지 하단 여백 제거 */
    .main .block-container {
        padding-bottom: 0 !important;
    }
    
    footer {
        display: none !important;
    }
    
    /* 인사이트 박스 */
    .insight-box {
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
    }
    
    .insight-bullish {
        background-color: #ffebee !important;
        border-left: 4px solid #d32f2f;
    }
    
    .insight-bearish {
        background-color: #e3f2fd !important;
        border-left: 4px solid #1976d2;
    }
    
    .insight-neutral {
        background-color: #f5f5f5 !important;
        border-left: 4px solid #9e9e9e;
    }
    
    .sentiment-bullish {
        color: #d32f2f !important;
        font-weight: 700 !important;
    }
    
    .sentiment-bearish {
        color: #1976d2 !important;
        font-weight: 700 !important;
    }
    
    .sentiment-neutral {
        color: #757575 !important;
        font-weight: 700 !important;
    }
    
    /* 브리핑 박스 */
    .briefing-box {
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 24px;
    }
    
    .mood-sunny {
        color: #ff6b35 !important;
    }
    
    .mood-cloudy {
        color: #5c6bc0 !important;
    }
    
    .mood-volatile {
        color: #78909c !important;
    }
    
    .hot-keyword {
        display: inline-block;
        background-color: #e8f4f8;
        color: #0277bd !important;
        padding: 4px 12px;
        border-radius: 16px;
        margin: 4px;
        font-weight: 500;
    }
    
    .update-info {
        background-color: #f5f5f5;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 0.9rem;
        color: #666 !important;
        margin-bottom: 16px;
    }
    
    /* 프로그레스 바 배경 제거 */
    [data-testid="stStatusWidget"],
    [data-testid="stStatus"],
    .stProgress,
    .stProgress > div {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* 뉴스 카드 박스 */
    .news-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* ===== 모든 팝업/다이얼로그/메뉴 흰색 배경 강제 적용 ===== */
    
    /* 토스트 메시지 */
    [data-testid="stToast"],
    [data-testid="stToast"] > div,
    [data-testid="stToast"] p {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* 연결 에러 팝업 */
    [data-testid="stConnectionStatus"],
    [data-testid="stConnectionStatus"] > div,
    .stConnectionStatus,
    .stConnectionStatus > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* 모달/다이얼로그 */
    [data-testid="stModal"],
    [data-testid="stDialog"],
    [role="dialog"],
    [role="alertdialog"],
    .stModal,
    .stDialog {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    [data-testid="stModal"] *,
    [data-testid="stDialog"] *,
    [role="dialog"] *,
    [role="alertdialog"] * {
        color: #1a1a1a !important;
    }
    
    /* 드롭다운 메뉴 */
    [data-testid="stSelectbox"] > div,
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [data-baseweb="select"] [role="listbox"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    [data-baseweb="popover"] *,
    [data-baseweb="menu"] * {
        color: #1a1a1a !important;
    }
    
    /* 우상단 햄버거 메뉴 */
    [data-testid="stMainMenu"],
    [data-testid="stMainMenu"] > div,
    [data-testid="stMainMenuPopover"],
    #MainMenu,
    #MainMenu > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    [data-testid="stMainMenu"] *,
    [data-testid="stMainMenuPopover"] *,
    #MainMenu * {
        color: #1a1a1a !important;
    }
    
    /* 툴팁 */
    [data-testid="stTooltipContent"],
    [role="tooltip"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* 경고/에러/알림 박스 */
    [data-testid="stAlert"],
    .stAlert {
        background-color: #ffffff !important;
    }
    
    [data-testid="stAlert"] *,
    .stAlert * {
        color: #1a1a1a !important;
    }
    
    /* 버튼 호버 상태 */
    button:hover {
        background-color: #333333 !important;
        color: #ffffff !important;
    }
    
    /* 모달 너비 확장 및 스타일 */
    div[data-testid="stDialog"] div[role="dialog"] {
        width: 80vw !important;
        max-width: 900px !important;
    }
    
    .portfolio-header {
        background: transparent;
        color: #1a1a1a !important;
        padding: 0 0 24px 0;
        margin-bottom: 24px;
        text-align: left;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .portfolio-header h2 {
        color: #1a1a1a !important;
        margin: 0;
        font-size: 2.0rem;
        font-weight: 700;
    }
    
    .portfolio-header p {
        color: #666 !important;
        margin: 8px 0 0 0;
        font-size: 1.0rem;
    }
    
    .portfolio-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #eee;
        margin-bottom: 20px;
    }
    
    .portfolio-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        height: auto;
    }
    
    .portfolio-card h4 {
        color: #1a1a1a !important;
        margin-top: 0;
        border-bottom: 2px solid #333;
        padding-bottom: 8px;
        margin-bottom: 16px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialization ---
init_db()

# --- Constants ---
DAILY_REFRESH_LIMIT = 20  # 하루 새로고침 횟수 제한
BUSINESS_HOUR_START = 7  # 운영 시작 시간
BUSINESS_HOUR_END = 22  # 운영 종료 시간

# KST Timezone Definition
KST = datetime.timezone(datetime.timedelta(hours=9))

# --- Logic ---
def get_batch_date():
    now = datetime.datetime.now(KST)
    if now.hour < 7:
        batch_date = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        batch_date = now.strftime("%Y-%m-%d")
    return batch_date

def is_business_hours():
    """운영 시간인지 확인 (07:00 ~ 22:00)"""
    current_hour = datetime.datetime.now(KST).hour
    return BUSINESS_HOUR_START <= current_hour <= BUSINESS_HOUR_END

def get_refresh_count(batch_date):
    """오늘 새로고침 횟수 반환 (세션 스테이트 기반)"""
    if 'refresh_counts' not in st.session_state:
        st.session_state.refresh_counts = {}
    return st.session_state.refresh_counts.get(batch_date, 0)

def increment_refresh_count(batch_date):
    """새로고침 횟수 증가"""
    if 'refresh_counts' not in st.session_state:
        st.session_state.refresh_counts = {}
    current = st.session_state.refresh_counts.get(batch_date, 0)
    st.session_state.refresh_counts[batch_date] = current + 1
    return DAILY_REFRESH_LIMIT - (current + 1)

def can_refresh(batch_date):
    """새로고침 가능 여부 확인"""
    return get_refresh_count(batch_date) < DAILY_REFRESH_LIMIT and is_business_hours()

def format_last_update_time(last_update):
    """마지막 업데이트 시간을 사람이 읽기 쉬운 형식으로 변환"""
    if not last_update:
        return "정보 없음"
    
    # Ensure last_update is aware or naive consistently. Best to convert to KST if naive
    # Assuming DB returns naive time, usually UTC or local. 
    # For simplicity, treating last_update as naive and comparing with naive if need be, 
    # BUT better to compare with KST now.
    
    now = datetime.datetime.now(KST)
    
    # If last_update is close to now, we should handle it.
    # However, 'last_update' comes from DB (database.py). 
    # Let's assume database stores text or naive datetime. 
    # We will just focus on the 'now' part being KST for "Today" calculation.
    
    # NOTE: database.py likely returns datetime object.
    
    # To compare dates safely:
    last_update_date = last_update.date()
    now_date = now.date()
    
    if last_update_date == now_date:
        # 오늘이면 "오늘 오후 2:30" 형식
        hour = last_update.hour
        minute = last_update.minute
        if hour < 12:
            period = "오전"
            display_hour = hour if hour > 0 else 12
        else:
            period = "오후"
            display_hour = hour - 12 if hour > 12 else 12
        return f"오늘 {period} {display_hour}:{minute:02d}"
    else:
        return last_update.strftime("%m/%d %H:%M")

def format_time_hhmm(date_str):
    if not date_str:
        return ""
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        return dt.strftime("%H:%M")
    except:
        return ""

def render_briefing(briefing):
    """상단 브리핑 대시보드 렌더링"""
    if not briefing:
        return
    
    mood = briefing.get('mood', '')
    mood_label = briefing.get('mood_label', '')
    summary = briefing.get('summary', '')
    hot_keywords = briefing.get('hot_keywords', [])
    
    # 무드별 스타일
    if '맑음' in mood:
        mood_class = 'mood-sunny'
        mood_icon = '☀️'
    elif '흐림' in mood:
        mood_class = 'mood-cloudy'
        mood_icon = '☁️'
    else:
        mood_class = 'mood-volatile'
        mood_icon = '🌤️'
    
    # 키워드 HTML
    keywords_html = ""
    if hot_keywords:
        for kw in hot_keywords:
            keywords_html += f'<span class="hot-keyword">#{kw}</span>'
    
    briefing_html = f"""
<div class="briefing-box">
    <h4>오늘의 경제 날씨: <span class="{mood_class}">{mood} ({mood_label})</span></h4>
    <p style="line-height: 1.8; margin: 16px 0;">{summary}</p>
    <div style="margin-top: 16px;">
        <b>오늘의 핫 키워드:</b><br>
        {keywords_html}
    </div>
</div>
"""
    st.markdown(briefing_html, unsafe_allow_html=True)

def render_news_card(item, index):
    """뉴스 카드 렌더링 (번호 포함)"""
    sentiment = item.get('sentiment', '중립')
    
    # 감성별 스타일
    if "호재" in sentiment:
        sentiment_class = "sentiment-bullish"
        insight_class = "insight-bullish"
        sentiment_label = "호재"
    elif "악재" in sentiment:
        sentiment_class = "sentiment-bearish"
        insight_class = "insight-bearish"
        sentiment_label = "악재"
    else:
        sentiment_class = "sentiment-neutral"
        insight_class = "insight-neutral"
        sentiment_label = "중립"
    
    # keywords 파싱
    keywords_raw = item.get('keywords') or '{}'
    try:
        insight_data = json.loads(keywords_raw)
        theme = insight_data.get('theme', '')
        stocks = insight_data.get('stocks', '')
        comment = insight_data.get('comment', '')
    except:
        theme = ''
        stocks = ''
        comment = keywords_raw
    
    # 번호 + 발행시간
    formatted_time = format_time_hhmm(item.get('pub_date'))
    time_str = f" | 발행시간: {formatted_time}" if formatted_time else ""
    
    # 원본 링크 HTML (텍스트 하이퍼링크)
    link_url = item.get('url')
    link_html = ""
    if link_url and link_url.startswith('http'):
        link_html = f'<a href="{link_url}" target="_blank" style="color: #666 !important; text-decoration: underline; font-size: 0.85rem;">원본 기사 →</a>'
    
    # 인사이트 HTML
    insight_html = ""
    if theme:
        insight_html += f"<b>관련 테마:</b> {theme}<br>"
    if stocks:
        insight_html += f"<b>주목할 종목:</b> {stocks}<br>"
    if comment:
        insight_html += f"<br><b>AI 코멘트:</b> {comment}"
    
    # 카드 전체를 HTML로 렌더링
    card_html = f'''
<div class="news-card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="color: #666; font-size: 0.85rem;">#{index}{time_str}</span>
        {link_html}
    </div>
    <h3 style="margin: 0 0 12px 0; font-size: 1.1rem; line-height: 1.4;">{item.get('title', '제목 없음')}</h3>
    <div class="insight-box {insight_class}">
        <span class="{sentiment_class}">[{sentiment_label}]</span><br><br>
        {insight_html}
    </div>
    <p style="line-height: 1.7; margin: 12px 0 0 0;">{item.get('summary', '요약 없음')}</p>
</div>
'''
    st.markdown(card_html, unsafe_allow_html=True)

def run_update(batch_date):
    """뉴스 수집 및 분석 실행 (전체 화면 로딩)"""
    # 로딩 상태 표시
    loading_container = st.empty()
    
    with loading_container.container():
        st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 400px; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 24px;">🔄</div>
            <h2 style="margin: 0 0 16px 0;">AI가 뉴스를 분석하고 있습니다</h2>
            <p id="loading-status" style="color: #666;">잠시만 기다려주세요...</p>
        </div>
        """, unsafe_allow_html=True)
        
        progress = st.progress(0, text="뉴스 수집 중...")
        
        raw_news = []
        try:
            raw_news = fetch_naver_news(query="경제", display=10)
            progress.progress(30, text=f"뉴스 {len(raw_news)}개 확보 완료")
        except Exception as e:
            st.error(f"뉴스 수집 실패: {e}")
            return
        
        analyzed_news = []
        briefing = None
        if raw_news:
            progress.progress(50, text="AI가 시장 영향을 분석 중...")
            try:
                analyzed_news = analyze_news(raw_news)
                progress.progress(70, text="분석 완료, 브리핑 작성 중...")
            except Exception as e:
                st.error(f"분석 실패: {e}")
                return
            
            try:
                briefing = generate_briefing(raw_news)
                progress.progress(90, text="브리핑 완료, 저장 중...")
            except Exception as e:
                st.error(f"브리핑 생성 실패: {e}")
        
        if analyzed_news:
            # 기존 데이터 삭제 후 새로 저장
            from database import delete_news_by_date
            delete_news_by_date(batch_date)
            
            save_news(analyzed_news, batch_date)
            if briefing:
                save_briefing(briefing, batch_date)
            progress.progress(100, text="완료!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("분석 과정에서 문제가 발생했습니다.")

@st.dialog("프로젝트 소개")
def show_project_info():
    # 헤더 섹션
    st.markdown("""
        <div class="portfolio-header">
            <h2>매일 경제 브리핑</h2>
            <p>AI 기반 경제 뉴스 통역기 & 투자 인사이트 제공 서비스</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. 개요 및 시나리오 (상하 배치 - Full Width)
    st.markdown("""
        <div class="portfolio-section">
            <h3 style="margin-top:0;">🎯 프로젝트 목표</h3>
            <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 0;">
                경제 뉴스를 봐도 어느 주식에 영향을 끼치는지 파악하기 어려운 사람에게 
                <strong>주식 호재/악재 인사이트를 제공</strong>합니다.
            </p>
        </div>
        
        <div class="portfolio-section">
            <h3 style="margin-top:0;">👤 유저 시나리오</h3>
            <p style="line-height: 1.6; margin-bottom: 0;">
                <strong>상황</strong>: 투자 정보를 얻고 싶은데 시간이 없는 직장인<br>
                <strong>행동</strong>: 출근길에 앱 접속 > [오늘 뉴스 보기] 클릭<br>
                <strong>경험</strong>: 3줄 요약과 호재/악재 라벨 확인 > 관련 수혜주 정보 획득
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💡 기술적 의사결정 (Technical Decisions)")
    
    # 2. 고려사항 (상하 배치 - Full Width)
    st.markdown("""
        <div class="portfolio-card">
            <h4>1. 비용 효율성 및 모델 선정</h4>
            <p style="color: #666; font-size: 0.9rem; margin-bottom: 12px;">"성능은 유지하되 운영 비용 Zero 달성"</p>
            <div style="background: #f5f5f5; padding: 12px; border-radius: 6px;">
                <strong>의사결정 포인트</strong><br>
                챗GPT API key 발급 비용 부담이 MVP 기능 단계에서는 불필요하다고 판단했습니다. 
                <strong>Groq(Llama 3.3)</strong>을 도입하여 비용을 절감할 수 있었습니다.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="portfolio-card" style="margin-top: 20px;">
            <h4>2. 데이터 전처리 및 품질관리</h4>
            <p style="color: #666; font-size: 0.9rem; margin-bottom: 12px;">"필요한 데이터만 사용할 수 있도록 필터링 규칙 적용"</p>
            <div style="background: #f5f5f5; padding: 12px; border-radius: 6px;">
                <strong>의사결정 포인트</strong><br>
                무작정 뉴스 요약을 시키면 효용성이 떨어지는 뉴스 기사도 함께 요약되기 때문에 
                <strong>Rule-base 데이터 필터링</strong>을 먼저 적용하여 경제 뉴스와 무관한 키워드를 제거하는 작업을 진행했습니다.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🚧 한계점 (Limitations)")
    
    # 3. 한계점 (Full Width)
    st.markdown("""
        <div class="portfolio-card">
            <h4>트렌드 분석 기능에 제한이 존재함</h4>
            <div style="background: #f5f5f5; padding: 12px; border-radius: 6px; margin-top: 16px;">
                <p style="margin: 0 0 8px 0;">
                    <strong>원인</strong><br>
                    네이버 검색 API는 조회수 데이터를 제공하지 않아 별도로 조회수와 언급량을 분석해야 하는데, 이를 파악하려면 수천 건의 기사 본문을 크롤링하여 LLM에 입력해야 합니다. 과도한 토큰 비용 발생으로 인하여 뉴스기사 데이터 자체를 분석하는 기능까지는 개발하지 못했습니다.
                </p>
                <p style="margin: 0;">
                    <strong>해결방법</strong><br>
                    특정 키워드 가중치 필터링을 대안으로 적용하여 효율을 높였습니다.<br>
                    <span style="color: #666; font-size: 0.9rem;">(사용된 키워드: 단독, 체결, 수주, 인수, 합병, 공시, 특징주, 급등, 어닝 서프라이즈, 흑자 전환 등)</span>
                </p>
            </div>
        </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 닫기 버튼 및 다시보지 않기
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1, 1])
    with col_l:
        dont_show = st.checkbox("오늘 하루 열지 않기")
    with col_r:
        if st.button("프로젝트 구경하기 (닫기)", type="primary", use_container_width=True):
            if dont_show:
                st.session_state.dont_show_today = True
            st.rerun()

def main():
    batch_date = get_batch_date()
    
    # --- Auto-Show Logic ---
    if 'has_seen_intro' not in st.session_state:
        # 세션에서 처음 방문인지 체크
        should_show = True
        
        # 오늘 하루 보지 않기 체크 여부 확인
        if 'dont_show_today' in st.session_state and st.session_state.dont_show_today:
            should_show = False
            
        if should_show:
            show_project_info()
            st.session_state.has_seen_intro = True
            
    # DB 조회
    news_data = get_news_by_date(batch_date)

    # 프로젝트 소개 버튼 (좌측 상단)
    if st.button("📋 프로젝트 소개", type="primary"):
        show_project_info()
    
    st.title("매일 경제 브리핑")
    st.caption("AI가 떠먹여주는 오늘의 경제 뉴스 & 투자 인사이트")
    
    batch_date = get_batch_date()
    
    # 새로고침 트리거 확인
    if 'trigger_refresh' not in st.session_state:
        st.session_state.trigger_refresh = False
    
    # 토스트 메시지 표시 (남은 횟수)
    if 'show_remaining_toast' in st.session_state and st.session_state.show_remaining_toast is not None:
        remaining = st.session_state.show_remaining_toast
        st.toast(f"남은횟수 {remaining}/{DAILY_REFRESH_LIMIT}")
        st.session_state.show_remaining_toast = None
    
    # DB 조회
    news_data = get_news_by_date(batch_date)
    briefing_data = get_briefing_by_date(batch_date)
    last_update = get_last_update_time(batch_date)
    
    # 새로고침 트리거가 활성화되면 로딩 실행
    if st.session_state.trigger_refresh:
        st.session_state.trigger_refresh = False
        run_update(batch_date)
        return  # run_update에서 st.rerun() 호출

    
    if news_data:
        # Case B: 데이터가 있을 때
        st.markdown(f"### {batch_date}")
        
        # 마지막 업데이트 시간 표시
        update_time_str = format_last_update_time(last_update)
        remaining = DAILY_REFRESH_LIMIT - get_refresh_count(batch_date)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'<div class="update-info">마지막 업데이트: {update_time_str}</div>', unsafe_allow_html=True)
        with col2:
            refresh_possible = can_refresh(batch_date)
            if st.button("새로고침", use_container_width=True, disabled=not refresh_possible):
                if refresh_possible:
                    remaining_after = increment_refresh_count(batch_date)
                    st.session_state.trigger_refresh = True
                    st.session_state.show_remaining_toast = remaining_after
                    st.rerun()
        
        # 상단 브리핑 대시보드
        render_briefing(briefing_data)
        
        # 뉴스 카드 (번호 포함)
        for idx, item in enumerate(news_data, 1):
            render_news_card(item, idx)
            
    else:
        # Case A: 데이터가 없을 때
        st.info(f"{batch_date} 기준 데이터가 아직 없습니다.")
        st.write("")
        
        if is_business_hours():

            if st.button("오늘 뉴스 분석 시작하기", type="primary", use_container_width=True):
                run_update(batch_date)
        else:
            st.warning("현재 운영시간(07:00~22:00) 외입니다. 운영시간에 다시 방문해 주세요.")

    # --- Sidebar ---
    with st.sidebar:
        # if st.button("📋 프로젝트 소개", type="primary", use_container_width=True):
        #     show_project_info()
            
        # st.divider()
        st.header("관리자 메뉴")
        st.caption(f"운영시간: {BUSINESS_HOUR_START}:00 ~ {BUSINESS_HOUR_END}:00")
        st.caption(f"하루 새로고침 횟수: {DAILY_REFRESH_LIMIT}회")
        st.divider()
        if st.button("데이터 초기화"):
            from database import delete_news_by_date
            delete_news_by_date(batch_date)
            st.toast("데이터가 초기화되었습니다.")
            time.sleep(1)
            st.rerun()

if __name__ == "__main__":
    main()

