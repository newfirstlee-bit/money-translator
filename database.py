import sqlite3
import os
import json
from datetime import datetime

DB_PATH = 'daily_news.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 뉴스 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_date TEXT NOT NULL,
            title TEXT,
            url TEXT,
            pub_date TEXT,
            summary TEXT,
            sentiment TEXT,
            keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 브리핑 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_briefing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_date TEXT NOT NULL UNIQUE,
            mood TEXT,
            mood_label TEXT,
            summary TEXT,
            hot_keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_news_by_date(batch_date):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM daily_news WHERE batch_date = ?', (batch_date,))
    rows = c.fetchall()
    news_list = [dict(row) for row in rows]
    conn.close()
    return news_list

def get_briefing_by_date(batch_date):
    """해당 날짜의 브리핑 조회"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM daily_briefing WHERE batch_date = ?', (batch_date,))
    row = c.fetchone()
    conn.close()
    if row:
        briefing = dict(row)
        # hot_keywords JSON 파싱
        try:
            briefing['hot_keywords'] = json.loads(briefing.get('hot_keywords', '[]'))
        except:
            briefing['hot_keywords'] = []
        return briefing
    return None

def save_briefing(briefing_data, batch_date):
    """브리핑 저장"""
    if not briefing_data:
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    hot_keywords = briefing_data.get('hot_keywords', [])
    if isinstance(hot_keywords, list):
        hot_keywords = json.dumps(hot_keywords, ensure_ascii=False)
    
    c.execute('''
        INSERT OR REPLACE INTO daily_briefing (batch_date, mood, mood_label, summary, hot_keywords)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        batch_date,
        briefing_data.get('mood', ''),
        briefing_data.get('mood_label', ''),
        briefing_data.get('summary', ''),
        hot_keywords
    ))
    
    conn.commit()
    conn.close()

def save_news(news_items, batch_date):
    """뉴스 저장"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    for item in news_items:
        c.execute('''
            INSERT INTO daily_news (batch_date, title, url, pub_date, summary, sentiment, keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            batch_date,
            item.get('title'),
            item.get('originallink') or item.get('url') or item.get('link'),
            item.get('pub_date'),
            item.get('summary'),
            item.get('sentiment'),
            item.get('keywords')
        ))
    
    conn.commit()
    conn.close()

def delete_news_by_date(batch_date):
    """해당 날짜의 뉴스와 브리핑 삭제"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM daily_news WHERE batch_date = ?", (batch_date,))
    c.execute("DELETE FROM daily_briefing WHERE batch_date = ?", (batch_date,))
    conn.commit()
    conn.close()

def get_last_update_time(batch_date):
    """해당 날짜의 가장 최신 created_at 시간 반환 (뉴스 또는 브리핑 중 최신, KST 변환)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 뉴스 테이블에서 최신 시간
    c.execute('''
        SELECT MAX(created_at) as last_update 
        FROM daily_news 
        WHERE batch_date = ?
    ''', (batch_date,))
    news_row = c.fetchone()
    
    # 브리핑 테이블에서 최신 시간
    c.execute('''
        SELECT MAX(created_at) as last_update 
        FROM daily_briefing 
        WHERE batch_date = ?
    ''', (batch_date,))
    briefing_row = c.fetchone()
    
    conn.close()
    
    from datetime import timedelta
    KST_OFFSET = timedelta(hours=9)  # UTC+9
    
    def parse_datetime(dt_str):
        if not dt_str:
            return None
        try:
            utc_time = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            return utc_time + KST_OFFSET  # UTC → KST 변환
        except:
            try:
                # 밀리초 포함 형식도 시도
                utc_time = datetime.strptime(dt_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
                return utc_time + KST_OFFSET
            except:
                return None
    
    news_time = parse_datetime(news_row[0]) if news_row else None
    briefing_time = parse_datetime(briefing_row[0]) if briefing_row else None
    
    # 둘 중 더 최신 시간 반환
    if news_time and briefing_time:
        return max(news_time, briefing_time)
    return news_time or briefing_time
