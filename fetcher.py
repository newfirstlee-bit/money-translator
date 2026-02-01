import os
import requests
import re
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
    # 1. 환경변수 확인 (로컬 우선)
    value = os.getenv(key)
    if value:
        return value
    
    # 2. Streamlit Secrets 확인 (배포 환경)
    if st and hasattr(st, 'secrets') and key in st.secrets:
        return st.secrets[key]
    
    return None

NAVER_CLIENT_ID = get_secret('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = get_secret('NAVER_CLIENT_SECRET')

# 검색할 때 쓸 알짜 키워드 (우선순위 높은 뉴스)
TARGET_KEYWORDS = [
    "단독", "체결", "수주", "인수", "합병", "공시", 
    "특징주", "급등", "어닝 서프라이즈", "흑자 전환", 
    "세계 최초", "FDA 승인", "개발 성공", "정부 발표"
]

# 결과에서 걸러낼 쓰레기 키워드 (제외할 뉴스)
EXCLUDE_KEYWORDS = [
    "마감", "시황", "코스피", "코스닥", "환율", "유가", 
    "인사", "부고", "동정", "게시판", "캠페인", 
    "모집", "개최", "이벤트", "할인", "포토", "영상", 
    "오늘의 운세", "날씨", "기자수첩"
]

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

def should_exclude(title, description):
    """제외 키워드가 포함된 뉴스인지 확인"""
    text = (title + " " + description).lower()
    for keyword in EXCLUDE_KEYWORDS:
        if keyword.lower() in text:
            return True
    return False

def has_target_keyword(title, description):
    """타겟 키워드가 포함된 뉴스인지 확인"""
    text = (title + " " + description).lower()
    for keyword in TARGET_KEYWORDS:
        if keyword.lower() in text:
            return True
    return False

def fetch_naver_news(query="경제", display=10):
    """
    네이버 뉴스 API에서 뉴스를 가져오고 필터링
    - 제외 키워드가 포함된 뉴스는 제거
    - 타겟 키워드가 포함된 뉴스를 우선 정렬
    """
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    # 더 많이 가져와서 필터링 후 원하는 개수만 반환
    params = {
        "query": query,
        "display": min(display * 3, 100),  # 필터링 여유분 확보
        "sort": "date"  # 최신순
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    
    items = []
    target_items = []  # 타겟 키워드 포함 뉴스
    normal_items = []  # 일반 뉴스
    
    for item in data.get('items', []):
        title = clean_html(item['title'])
        description = clean_html(item['description'])
        
        # 제외 키워드 필터링
        if should_exclude(title, description):
            continue
        
        news_item = {
            'title': title,
            'originallink': item.get('originallink') or item.get('link'),
            'link': item.get('link'),
            'pub_date': item['pubDate'],
            'description': description
        }
        
        # 타겟 키워드 포함 여부에 따라 분류
        if has_target_keyword(title, description):
            target_items.append(news_item)
        else:
            normal_items.append(news_item)
    
    # 타겟 키워드 뉴스 우선, 나머지는 일반 뉴스
    items = target_items + normal_items
    
    # 요청한 개수만큼만 반환
    return items[:display]
