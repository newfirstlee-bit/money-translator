import os
import json
from groq import Groq
from dotenv import load_dotenv

try:
    import streamlit as st
except ImportError:
    st = None

load_dotenv()

def get_secret(key):
    """
    환경변수 또는 Streamlit Secrets에서 키를 가져옵니다.
    """
    value = os.getenv(key)
    if value:
        return value
    if st and hasattr(st, 'secrets') and key in st.secrets:
        return st.secrets[key]
    return None

GROQ_API_KEY = get_secret('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def generate_briefing(news_list):
    """
    10개 뉴스를 종합 분석하여 오늘의 시장 브리핑 생성
    Returns: dict with 'mood', 'summary', 'hot_keywords'
    """
    if not news_list or not client:
        return None
    
    news_content = ""
    for idx, item in enumerate(news_list):
        news_content += f"[{idx+1}] 제목: {item.get('title', '')}\n"

    system_prompt = "You are a Korean financial news analyst. Summarize market trends. Respond in Korean. Output valid JSON only."

    user_prompt = f"""아래 10개 경제 뉴스의 공통된 흐름을 분석해서 JSON으로 응답해줘.

[오늘의 뉴스 제목들]
{news_content}

[출력 형식]
{{
  "mood": "맑음 또는 흐림 또는 변동성",
  "mood_label": "호재 우세 또는 악재 우세 또는 혼조세",
  "summary": "오늘 시장의 전반적인 분위기를 3-4문장으로 설명. 어떤 이슈가 많이 나왔는지, 시장에 어떤 영향이 예상되는지.",
  "hot_keywords": ["키워드1", "키워드2", "키워드3"]
}}

중요:
- 이모지 사용 금지
- 모든 텍스트는 한국어로
- hot_keywords는 뉴스에서 자주 언급된 테마/종목/이슈 3-5개
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        response_text = completion.choices[0].message.content
        return json.loads(response_text)
    except Exception as e:
        print(f"Briefing generation error: {e}")
        return None


def analyze_news(news_list):
    """
    news_list: list of dicts from fetcher.py
    Returns list of dicts with added analysis fields
    """
    if not news_list:
        return []
    
    if not client:
        raise ValueError("GROQ_API_KEY not found in .env")

    # 프롬프트 구성
    news_content = ""
    for idx, item in enumerate(news_list):
        news_content += f"[{idx+1}] 제목: {item['title']}\n내용: {item['description']}\n\n"

    system_prompt = """You are a Korean stock market expert analyst. Analyze news and recommend SPECIFIC listed stocks. 
Always respond in Korean. Output valid JSON only."""

    user_prompt = f"""아래 뉴스들을 분석해서 JSON으로 응답해줘.

[뉴스 목록]
{news_content}

[투자 타겟 추출 규칙 - 엄격히 따라줘]
1. 모호한 표현 금지: '수출 관련주', '연구개발 기업' 같은 뜬구름 잡는 단어 쓰지 마.
2. 구체적 종목명 명시: 한국 주식 시장(KOSPI, KOSDAQ)에 상장된 실제 종목명을 2~3개 추천해.
3. 비상장 기업 처리: 뉴스에 나온 기업이 비상장(예: BBQ, LG CNS)이면, 상장된 경쟁사나 지분을 가진 모회사를 찾아서 추천해.

[출력 형식]
{{
  "news": [
    {{
      "index": 1,
      "summary": "한국어로 2-3줄 핵심 요약",
      "sentiment": "호재 또는 악재 또는 중립",
      "theme": "관련 테마/업종 (예: IT 서비스, 반도체, 2차전지)",
      "stocks": "주목할 종목 2-3개, 쉼표로 구분 (예: 삼성전자, SK하이닉스)",
      "comment": "왜 이 종목들이 관련 있는지 1-2줄로 쉽게 설명 (초등학생도 이해할 수 있게)"
    }}
  ]
}}

중요: 
- 모든 텍스트는 반드시 한국어로
- 이모지 사용 금지
- stocks에는 반드시 상장된 종목명만 넣어
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        response_text = completion.choices[0].message.content
        
        # JSON 파싱
        data = json.loads(response_text)
        analyzed_data = data.get('news', [])
        
        if not analyzed_data and isinstance(data, list):
            analyzed_data = data

        result = []
        for item in analyzed_data:
            idx = item.get('index', 0) - 1
            if 0 <= idx < len(news_list):
                original = news_list[idx]
                original['summary'] = item.get('summary', '요약 없음')
                original['sentiment'] = item.get('sentiment', '중립')
                # 새로운 필드들
                theme = item.get('theme', '')
                stocks = item.get('stocks', '')
                comment = item.get('comment', '')
                # keywords 필드에 구조화된 정보 저장 (JSON 형태)
                original['keywords'] = json.dumps({
                    'theme': theme,
                    'stocks': stocks,
                    'comment': comment
                }, ensure_ascii=False)
                result.append(original)
        return result

    except Exception as e:
        print(f"Groq API Error: {e}")
        raise e
