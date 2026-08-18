-- 1. 사용자 테이블 (Signup.jsx 입력 필드 및 동의 항목 반영)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,          
    password VARCHAR(255) NOT NULL,          
    riding_styles TEXT,                      
    marketing_agreed BOOLEAN DEFAULT 0,    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);