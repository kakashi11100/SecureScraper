import pytest
import sqlite3
import os
import html
from scraper.storage import init_db, save_snapshot, get_stored_hash

DB_TEST_PATH = "test_secure_scraper.db"

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setting up a clean database before running the test, cleaning up after."""
    init_db(DB_TEST_PATH)
    yield
    if os.path.exists(DB_TEST_PATH):
        os.remove(DB_TEST_PATH)

def test_sqli_payload_is_neutralized():
    """Asserts that classic SQL Injection strings are treated strictly as data, not commands."""
    malicious_url = "https://example.com/page"
    # Injection payload attempting to close a string and bypass query boundaries
    sqli_payload = "'; DROP TABLE snapshots; --" 
    
    # Attempt to save the payload
    save_snapshot(malicious_url, "fakehash123", sqli_payload, db_path=DB_TEST_PATH)
    
    # If parameterization works, the table still exists and we can read the payload back safely
    stored_hash = get_stored_hash(malicious_url, db_path=DB_TEST_PATH)
    assert stored_hash == "fakehash123"

def test_xss_payload_is_escaped():
    """Asserts that dangerous HTML/JavaScript code is rendered harmless via escaping."""
    malicious_url = "https://example.com/hacked"
    xss_payload = "<script>alert('attacker-controlled-script')</script>"
    
    save_snapshot(malicious_url, "fakehash456", xss_payload, db_path=DB_TEST_PATH)
    
    # Query directly from database to check escaping status
    conn = sqlite3.connect(DB_TEST_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM snapshots WHERE url = ?", (malicious_url,))
    stored_content = cursor.fetchone()[0]
    conn.close()
    
    # It should be escaped safely, turning '<' into '&lt;'
    assert "&lt;script&gt;" in stored_content
    assert "<script>" not in stored_content