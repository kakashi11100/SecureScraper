import hashlib

def calculate_hash(text: str) -> str:
    """
    Generates a secure SHA-256 hash string from input text.
    Strips whitespace first so formatting tweaks don't trip false alerts.
    """
    if not text:
        return ""
    
    # Clean up whitespace and encode the string to bytes, then hash it
    cleaned_text = text.strip().encode('utf-8')
    return hashlib.sha256(cleaned_text).hexdigest()