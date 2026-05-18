"""
Internet Archive Wayback Machine CDX search + snapshot fetch.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Any, List, Optional
from urllib.parse import urlparse

import httpx

DEFAULT_USER_AGENT = (
    "TraceNeuro/0.1 (+https://github.com/GamerNCoder/neurotracer; research corpus)"
)
CDX_API = "https://web.archive.org/cdx/search/cdx"

# Skip homepages and non-post URLs
_SKIP_PATH_SUFFIXES = (
    "/",
    "/index.html",
    "/index.htm",
    "/archive.html",
    "/search",
    "/feeds",
    "/atom.xml",
    "/rss.xml",
)
_MIN_PATH_SEGMENTS = 2


@dataclass(frozen=True)
class ArchiveCapture:
    original_url: str
    timestamp: str  # Wayback YYYYMMDDhhmmss
    archive_url: str
    mimetype: str = "text/html"


def _is_likely_blog_post(url: str) -> bool:
    parsed = urlparse(url)
    path = (parsed.path or "/").lower()
    if any(path.endswith(s) or path == s.rstrip("/") for s in _SKIP_PATH_SUFFIXES if s != "/"):
        if path in ("/", ""):
            return False
    for bad in ("/label/", "/search?", "/p/search", "/feeds/posts"):
        if bad in path:
            return False
    segments = [s for s in path.split("/") if s]
    if len(segments) < _MIN_PATH_SEGMENTS and not re.search(r"/\d{4}/", path):
        return False
    return True


def _build_archive_url(timestamp: str, original: str) -> str:
    return f"https://web.archive.org/web/{timestamp}/{original}"


class WaybackClient:
    def __init__(
        self,
        *,
        user_agent: str = DEFAULT_USER_AGENT,
        request_delay_sec: float = 1.25,
        timeout_sec: float = 60.0,
    ) -> None:
        self.request_delay_sec = request_delay_sec
        self._last_request_at = 0.0
        self._client = httpx.Client(
            timeout=timeout_sec,
            headers={"User-Agent": user_agent},
            follow_redirects=True,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "WaybackClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.request_delay_sec:
            time.sleep(self.request_delay_sec - elapsed)
        self._last_request_at = time.monotonic()

    def search_captures(
        self,
        url_pattern: str,
        *,
        limit: int = 50,
        to_date: str = "20111231",
        from_date: str = "20050101",
    ) -> List[ArchiveCapture]:
        """
        Query CDX for unique URLs matching pattern, archived before end of 2011.
        """
        self._throttle()
        params: dict[str, Any] = {
            "url": url_pattern,
            "output": "json",
            "from": from_date,
            "to": to_date,
            "filter": ["statuscode:200", "mimetype:text/html"],
            "collapse": "urlkey",
            "limit": str(max(limit, 10)),
        }
        r = self._client.get(CDX_API, params=params)
        r.raise_for_status()
        rows = r.json()
        if not rows or len(rows) < 2:
            return []

        # CDX columns: urlkey, timestamp, original, mimetype, statuscode, ...
        header = [c.lower() for c in rows[0]]
        try:
            ts_i = header.index("timestamp")
            orig_i = header.index("original")
            mime_i = header.index("mimetype") if "mimetype" in header else None
        except ValueError:
            return []

        out: List[ArchiveCapture] = []
        seen_urls: set[str] = set()
        for row in rows[1:]:
            if len(row) <= max(ts_i, orig_i):
                continue
            original = row[orig_i].strip()
            if not original or original in seen_urls:
                continue
            if not _is_likely_blog_post(original):
                continue
            seen_urls.add(original)
            timestamp = row[ts_i].strip()
            mime = row[mime_i] if mime_i is not None and mime_i < len(row) else "text/html"
            out.append(
                ArchiveCapture(
                    original_url=original,
                    timestamp=timestamp,
                    archive_url=_build_archive_url(timestamp, original),
                    mimetype=mime or "text/html",
                )
            )
            if len(out) >= limit:
                break
        return out

    def fetch_snapshot_html(self, capture: ArchiveCapture) -> bytes:
        self._throttle()
        r = self._client.get(capture.archive_url)
        r.raise_for_status()
        return r.content


def extract_title_from_html(raw: str) -> Optional[str]:
    m = re.search(r"<title[^>]*>([^<]+)</title>", raw, re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    title = re.sub(r"\s+", " ", m.group(1)).strip()
    if len(title) > 300:
        title = title[:297] + "..."
    return title or None


def archive_date_from_timestamp(ts: str) -> str:
    """Wayback timestamp YYYYMMDD... -> ISO date YYYY-MM-DD."""
    if len(ts) >= 8 and ts[:8].isdigit():
        y, m, d = ts[:4], ts[4:6], ts[6:8]
        return f"{y}-{m}-{d}"
    return ""
