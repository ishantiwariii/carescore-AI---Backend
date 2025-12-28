from utils.constants import FORBIDDEN_KEYWORDS
import re

def sanitize_text(text):
    """Removes diagnostic claims and disease names"""
    cleaned_text = text
    for word in FORBIDDEN_KEYWORDS:
        # Case insensitive replacement
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        cleaned_text = pattern.sub("[REDACTED FOR SAFETY]", cleaned_text)
    
    return cleaned_text