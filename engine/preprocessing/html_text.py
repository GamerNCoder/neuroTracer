"""
Strip common blog/HTML exports to plain text for scoring.
Uses stdlib only (no BeautifulSoup dependency).
"""

from __future__ import annotations

import html as html_lib
import re
from typing import Final

_SCRIPT_STYLE: Final[re.Pattern[str]] = re.compile(
    r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL
)
_TAGS: Final[re.Pattern[str]] = re.compile(r"<[^>]+>")


def html_to_plaintext(raw: str) -> str:
    """Remove script/style/tags and collapse whitespace."""
    if not raw or not raw.strip():
        return ""
    text = _SCRIPT_STYLE.sub(" ", raw)
    text = _TAGS.sub(" ", text)
    text = html_lib.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_text_from_bytes(data: bytes, filename: str = "") -> str:
    """
    Decode bytes (utf-8 / latin-1 fallback) and strip HTML if extension suggests markup.
    """
    name = filename.lower()
    raw: str | None = None
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            raw = data.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if raw is None:
        raw = data.decode("utf-8", errors="replace")

    if name.endswith((".html", ".htm", ".xhtml")) or (
        raw.lstrip().startswith("<") and "<html" in raw[:2000].lower()
    ):
        return html_to_plaintext(raw)
    return raw.strip()
