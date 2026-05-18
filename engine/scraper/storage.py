"""
Write scraped blog corpus: HTML files + JSONL manifest with timestamps.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Set

from engine.preprocessing.html_text import extract_text_from_bytes


@dataclass
class ScrapeRecord:
    id: str
    category: str
    category_name: str
    item_index: int
    source_url: str
    archive_url: str
    archive_timestamp: str
    archive_date: str
    scraped_at: str
    title: Optional[str]
    char_count: int
    word_count: int
    html_path: str
    status: str  # ok | error
    error: Optional[str] = None

    def to_json(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScrapeStats:
    categories_total: int = 0
    categories_completed: int = 0
    items_saved: int = 0
    items_skipped: int = 0
    items_failed: int = 0
    by_category: Dict[str, int] = field(default_factory=dict)


class CorpusWriter:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir.expanduser().resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.output_dir / "manifest.jsonl"
        self._seen_keys: Set[str] = set()
        self._load_existing_keys()

    def _load_existing_keys(self) -> None:
        if not self.manifest_path.exists():
            return
        with self.manifest_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get("status") == "ok":
                    key = f"{row.get('category')}:{row.get('source_url')}"
                    self._seen_keys.add(key)

    def already_have(self, category: str, source_url: str) -> bool:
        return f"{category}:{source_url}" in self._seen_keys

    @staticmethod
    def make_id(category: str, source_url: str, archive_timestamp: str) -> str:
        raw = f"{category}|{source_url}|{archive_timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def category_dir(self, category_slug: str) -> Path:
        d = self.output_dir / category_slug
        d.mkdir(parents=True, exist_ok=True)
        return d

    def append_record(self, record: ScrapeRecord) -> None:
        with self.manifest_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_json(), ensure_ascii=False) + "\n")
        if record.status == "ok":
            self._seen_keys.add(f"{record.category}:{record.source_url}")

    def save_post(
        self,
        *,
        category_slug: str,
        category_name: str,
        item_index: int,
        source_url: str,
        archive_url: str,
        archive_timestamp: str,
        archive_date: str,
        html_bytes: bytes,
        title: Optional[str],
    ) -> ScrapeRecord:
        post_id = self.make_id(category_slug, source_url, archive_timestamp)
        html_rel = f"{category_slug}/{post_id}.html"
        html_path = self.category_dir(category_slug) / f"{post_id}.html"
        html_path.write_bytes(html_bytes)

        plain = extract_text_from_bytes(html_bytes, html_path.name)
        now = datetime.now(timezone.utc).isoformat()
        record = ScrapeRecord(
            id=post_id,
            category=category_slug,
            category_name=category_name,
            item_index=item_index,
            source_url=source_url,
            archive_url=archive_url,
            archive_timestamp=archive_timestamp,
            archive_date=archive_date,
            scraped_at=now,
            title=title,
            char_count=len(plain),
            word_count=len(plain.split()) if plain else 0,
            html_path=html_rel,
            status="ok",
        )
        self.append_record(record)
        return record

    def save_error(
        self,
        *,
        category_slug: str,
        category_name: str,
        item_index: int,
        source_url: str,
        archive_url: str,
        archive_timestamp: str,
        archive_date: str,
        error: str,
    ) -> ScrapeRecord:
        post_id = self.make_id(category_slug, source_url, archive_timestamp)
        now = datetime.now(timezone.utc).isoformat()
        record = ScrapeRecord(
            id=post_id,
            category=category_slug,
            category_name=category_name,
            item_index=item_index,
            source_url=source_url,
            archive_url=archive_url,
            archive_timestamp=archive_timestamp,
            archive_date=archive_date,
            scraped_at=now,
            title=None,
            char_count=0,
            word_count=0,
            html_path="",
            status="error",
            error=error,
        )
        self.append_record(record)
        return record

    def write_summary(self, stats: ScrapeStats, *, target_per_category: int) -> Path:
        summary = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "output_dir": str(self.output_dir),
            "target_categories": stats.categories_total,
            "target_per_category": target_per_category,
            "categories_completed": stats.categories_completed,
            "items_saved": stats.items_saved,
            "items_skipped": stats.items_skipped,
            "items_failed": stats.items_failed,
            "by_category": stats.by_category,
            "manifest": str(self.manifest_path.name),
        }
        path = self.output_dir / "scrape_summary.json"
        path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return path
