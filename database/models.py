import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Foydalanuvchilar jadvali
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        balance INTEGER DEFAULT 0,
        role TEXT DEFAULT 'user',
        is_banned INTEGER DEFAULT 0,
        referrer_id INTEGER DEFAULT NULL,
        joined_date TEXT NOT NULL
    )
    """)

    # Tizim sozlamalari jadvali (Karta, API)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)

    # Boshlang'ich API va Karta sozlamalarini joylash
    default_settings = [
        ('card_number', '8600 0000 0000 0000'),
        ('card_owner', 'Admin Name'),
        ('smm_api_url', 'https://foydaliksmm.uz/api/v2'),
        ('smm_api_key', '8a6a494c3e3f2f292380188f337d14b8')
    ]
    cursor.executemany("INSERT OR IGNORE INTO system_settings (key, value) VALUES (?, ?)", default_settings)

    conn.commit()
    conn.close()