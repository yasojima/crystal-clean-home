"""Strip retired importer metadata without changing home presentation."""
import re


def clean_home(text):
    text = re.sub(r'<script\b[^>]*(?:application/ld\+json|wp-emoji-settings)[^>]*>.*?</script>', '', text, flags=re.S | re.I)
    text = re.sub(r'<script\b[^>]*type="module"[^>]*>.*?wp-emoji.*?</script>', '', text, flags=re.S | re.I)
    text = re.sub(r'<link\b[^>]*(?:rel=["\'](?:next|EditURI|https://api.w.org/)["\'])[^>]*>', '', text, flags=re.I)
    text = re.sub(r'<meta\b[^>]*(?:og:image|twitter:image)[^>]*>', '', text, flags=re.I)
    text = re.sub(r'<!--(?!\s*cch-).*?-->', '', text, flags=re.S)
    return text
