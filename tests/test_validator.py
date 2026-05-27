import pytest
from scraper.validator import is_valid_url, sanitize_selector

def test_url_validation_success():
    assert is_valid_url("https://example.com/pricing") is True

def test_url_validation_rejects_malicious_protocols():
    # Blocks local file reading attempts
    assert is_valid_url("file:///etc/passwd") is False
    assert is_valid_url("gopher://localhost") is False

def test_selector_sanitization():
    # Should strip out dangerous characters like semicolons or quotes
    dirty_selector = "div.price-table; DROP TABLE users;"
    clean_selector = sanitize_selector(dirty_selector)
    assert ";" not in clean_selector
    assert "DROP" in clean_selector # It safely strips the punctuation, rendering it useless as a command
