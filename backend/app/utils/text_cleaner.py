import re
import unicodedata

def clean_text(text: str) -> str:
    """
    Performs basic text cleaning for scam detection.
    """
    if not text:
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKC', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Lowercase text for uniform processing
    text = text.lower()
    
    return text

def extract_metadata(text: str) -> dict:
    """
    Extracts basic metadata like presence of links or phone numbers.
    """
    has_link = bool(re.search(r'https?://\S+|www\.\S+', text))
    has_phone = bool(re.search(r'\+?\d{10,13}', text))
    
    return {
        "has_link": has_link,
        "has_phone": has_phone
    }
