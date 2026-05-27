import sqlite3
import html

def init_db(db_path: str = "scraper.db"):
    """Initializes the SQLite database and creates the schema if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            url TEXT PRIMARY KEY,
            hash TEXT NOT NULL,
            content TEXT,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_snapshot(url: str, content_hash: str, raw_text: str, db_path: str = "scraper.db"):
    """Persists scraper state securely using parameterized queries and output escaping."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Mitigation against Stored XSS: Escape HTML strings
    safe_text = html.escape(raw_text)
    
    # 2. Mitigation against SQL Injection: Use '?' placeholders
    cursor.execute("""
        INSERT OR REPLACE INTO snapshots (url, hash, content, last_checked) 
        VALUES (?, ?, ?, datetime('now'))
    """, (url, content_hash, safe_text))
    
    conn.commit()
    conn.close()

def get_stored_hash(url: str, db_path: str = "scraper.db") -> str:
    """Retrieves the last known hash for a given URL. Returns None if new."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Secure parameterized selection
    cursor.execute("SELECT hash FROM snapshots WHERE url = ?", (url,))
    row = cursor.fetchone()
    
    conn.close()
    return row[0] if row else None