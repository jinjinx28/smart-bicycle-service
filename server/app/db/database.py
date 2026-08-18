import sqlite3

DB_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(100) NOT NULL,          
            password VARCHAR(255) NOT NULL,          
            riding_styles TEXT,                      
            marketing_agreed BOOLEAN DEFAULT 0,    
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# 서버 켜질 때 테이블 생성 함수 실행
init_db()

# 회원가입 정보 DB 저장 함수
def insert_user(email, username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (email, username, password)
        VALUES (?, ?, ?)
    """, (email, username, password))
    conn.commit()
    conn.close()

# 로그인용 이메일 조회 함수
def find_user_by_email(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT email, username, password FROM users WHERE email = ?", (email,))
    db_user = cursor.fetchone()
    conn.close()
    return db_user