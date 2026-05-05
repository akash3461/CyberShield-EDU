import re
import html

class Sanitizer:
    @staticmethod
    def clean_text(text: str) -> str:
        """Sanitizes text by removing HTML tags and stripping whitespace."""
        if not text:
            return ""
        # Remove HTML tags using regex
        clean = re.sub(r'<[^>]*?>', '', text)
        # Unescape HTML entities
        clean = html.unescape(clean)
        # Remove non-printable characters
        clean = ''.join(char for char in clean if char.isprintable())
        return clean.strip()

    @staticmethod
    def sanitize_url(url: str) -> str:
        """Basic sanitization for URLs to prevent simple injection/malformed input."""
        if not url:
            return ""
        # Remove any leading/trailing whitespace
        url = url.strip()
        # Remove any newline characters
        url = url.replace('\n', '').replace('\r', '')
        # Check for obvious javascript injection
        if url.lower().startswith('javascript:'):
            return "blocked:unsafe-protocol"
        return url

sanitizer = Sanitizer()
