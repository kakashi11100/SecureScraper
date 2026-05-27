import re
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """
    Validates that a URL is well-formed and uses HTTP/HTTPS.
    Prevents SSRF (Server-Side Request Forgery) by blocking file:// or internal protocols.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False
        return bool(parsed.netloc)
    except Exception:
        return False

def sanitize_selector(selector: str) -> str:
    """
    Strips dangerous characters out of CSS selectors to prevent 
    any malicious injection into the parsing engine.
    """
    # Allow only standard CSS selector characters (alphanumeric, spaces, dots, hashes, dashes)
    return re.sub(r'[^a-zA-Z0-9_\-\.\#\s\>\:\(\)]', '', selector)