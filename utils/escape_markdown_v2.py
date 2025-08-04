import re

def escape_markdown_v2(text):
    """Escape special characters for MarkdownV2."""
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)
