# PRD: Money Translator (MVP) - AI Morning Briefing

## 1. 프로젝트 개요
**프로젝트명**: Money Translator (매일 경제 브리핑)

**목표**: 경제 뉴스를 AI가 분석하여 '쉬운 요약'과 '부정/긍정(호재/악재) 라벨링', '관련 수혜주' 인사이트를 제공한다.

**핵심 가치**:
- **Speed**: 뉴스를 읽는 시간을 단축한다 (3줄 요약).
- **Context**: 뉴스가 내 주식에 미칠 영향을 즉시 파악한다 (호재/악재 라벨).
- **Zero Cost**: 무료 LLM(Groq)과 오픈 API를 활용하여 운영 비용을 최적화한다.

## 2. 유저 시나리오 (User Flow)

### 2.1. 첫 방문 (07:00 AM 이후, 당일 데이터 없음)
1. **접속**: 유저가 사이트에 접속한다.
2. **소개 및 백그라운드 분석**: 
   - 화면에 "프로젝트 소개" 팝업(Modal)이 자동으로 뜬다.
   - 유저가 팝업의 내용을 읽는 동안, **백그라운드에서 AI 뉴스 분석**이 시작된다. (Lazy Auto-Run)
3. **대기 (Optional)**: 유저가 팝업을 닫았는데 아직 분석이 안 끝났다면, 메인 화면에 "AI가 시장 데이터를 분석 중입니다... (약 30초)" 로딩 화면이 표시된다.
4. **결과 노출**: 분석이 완료되면 페이지가 자동으로 새로고침되며 "오늘의 브리핑"과 "뉴스 리스트"가 나타난다.

### 2.2. 재방문 (데이터 존재)
1. **즉시 확인**: 대기 시간 없이 저장된 뉴스 리스트와 브리핑 대시보드를 확인한다.
2. **새로고침**: 필요 시 [새로고침] 버튼을 눌러 최신 뉴스로 업데이트한다. (일일 20회 제한)

## 3. 상세 기능 명세 (Specifications)

### 3.1. 시간 및 데이터 관리 규칙 (Business Logic)
- **기준 시간**: 한국 표준시 (KST, UTC+9)
- **운영 시간**: 07:00 ~ 22:00 (KST)
- **데이터 배치(Batch)**:
  - 매일 07:00를 기준으로 '새로운 하루'로 인식한다.
  - 다음 날 06:59까지는 같은 '오늘' 데이터로 취급한다.
- **데이터 보존 전략**: Streamlit Cloud의 휘발성(Ephemeral) 특성을 고려하여, SQLite를 사용하되 "오늘 하루의 데이터"를 캐싱하는 용도로만 정의한다. (영구 보존 보장 X)

### 3.2. 데이터 수집 (Input)
- **소스**: 네이버 뉴스 검색 API
- **필터링 로직 (Rule-based)**:
  - LLM 비용/속도 최적화를 위해 **키워드 기반 사전 필터링** 수행.
  - **포함(Include)**: 단독, 체결, 수주, M&A, FDA, 승인, 개발, 흑자 등
  - **제외(Exclude)**: 부고, 인사, 포토, 날씨, 운세, 마감시황 등

### 3.3. AI 분석 파이프라인 (Processing)
- **Engine**: Groq API (Llama-3.3-70b-versatile)
- **Concurrency**: `concurrent.futures.ThreadPoolExecutor`를 사용하여 UI 블로킹 방지.
- **Prompt Engineering**:
  - `Output JSON`: 구조화된 데이터 강제 (호재/악재, 테마, 종목명).
  - `Hallucination Control`: 기사 본문에 없는 내용은 추론하지 않도록 제약.

### 3.4. 사용자 인터페이스 (UI/UX)
- **톤앤매너**: 신뢰감을 주는 금융 대시보드 스타일. 깔끔한 화이트/그레이 톤에 포인트 컬러 사용.
- **가시성**:
  - **호재**: 붉은 계열 (Red/Orange)
  - **악재**: 푸른 계열 (Blue) - *한국 주식 시장 관행 따름*
  - **중립**: 그레이 (Gray)
- **Project Info Modal**:
  - 앱의 목적(Vision)과 기술적 의사결정(Technical Decisions)을 설명하는 포트폴리오 성격의 모달.
  - **하루 열지 않기** 기능 제공 (Cookie/Session State 활용).

## 4. 데이터베이스 (SQLite)
- **테이블**:
  - `daily_news`: 개별 기사 분석 데이터 (제목, 링크, 발행시간, 요약, 감성, 키워드).
  - `daily_briefing`: 전체 시장 요약 데이터 (무드, 요약, 핫키워드).
- **보안**: `.env` 및 `st.secrets`를 통해 API Key 관리. DB 파일은 `.gitignore` 처리.

## 5. 기술 스택 (Tech Stack)
- **Frontend/Backend**: Streamlit (Python 3.12)
- **AI Model**: Groq (Llama 3.3)
- **Data**: Naver Search API
- **Infra**: Streamlit Cloud (Community Tier)

## 6. 개발 히스토리 & 의사결정 (Decision Log)
*(상세 내용은 `PORTFOLIO_CASE_STUDY.md` 참조)*
1. **Groq 도입**: GPT-4 대비 비용 절감 및 속도 향상.
2. **Backgound Threading**: 긴 분석 시간(30초)동안 유저 이탈을 막기 위해 팝업 + 백그라운드 처리 도입.
3. **KST Timezone**: AWS/Cloud 서버의 UTC 환경에서도 한국 시간 기준으로 작동하도록 강제.

