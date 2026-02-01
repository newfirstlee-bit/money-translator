import sqlite3
import datetime

DB_PATH = 'daily_news.db'

def get_batch_date():
    # main.py와 동일한 로직
    now = datetime.datetime.now()
    if now.hour < 7:
        batch_date = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        batch_date = now.strftime("%Y-%m-%d")
    return batch_date

def clear_today():
    batch_date = get_batch_date()
    print(f"Clearing data for batch_date: {batch_date}")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM daily_news WHERE batch_date = ?", (batch_date,))
    deleted_count = c.rowcount
    conn.commit()
    conn.close()
    
    print(f"Deleted {deleted_count} records.")

if __name__ == "__main__":
    clear_today()
