"""
Loop scraper: 20 categories × N items via Wayback Machine.
"""

from __future__ import annotations

import logging
from typing import Callable, Optional

from engine.preprocessing.html_text import extract_text_from_bytes
from engine.scraper.categories import Category, categories_slice
from engine.scraper.storage import CorpusWriter, ScrapeStats
from engine.scraper.wayback import (
    WaybackClient,
    archive_date_from_timestamp,
    extract_title_from_html,
)

logger = logging.getLogger(__name__)


class ScrapeRunner:
    def __init__(
        self,
        writer: CorpusWriter,
        client: WaybackClient,
        *,
        per_category: int = 25,
        max_categories: int = 20,
        min_plaintext_chars: int = 200,
        to_date: str = "20111231",
        search_multiplier: int = 4,
    ) -> None:
        self.writer = writer
        self.client = client
        self.per_category = per_category
        self.max_categories = max_categories
        self.min_plaintext_chars = min_plaintext_chars
        self.to_date = to_date
        self.search_multiplier = search_multiplier

    def run(
        self,
        *,
        on_category_start: Optional[Callable[[Category, int], None]] = None,
        on_item_saved: Optional[Callable[[Category, int, int], None]] = None,
    ) -> ScrapeStats:
        categories = categories_slice(self.max_categories)
        stats = ScrapeStats(categories_total=len(categories))

        for cat_idx, category in enumerate(categories):
            if on_category_start:
                on_category_start(category, cat_idx)
            saved = self._scrape_category(category, stats, on_item_saved)
            stats.by_category[category.slug] = saved
            if saved >= self.per_category:
                stats.categories_completed += 1
            logger.info(
                "Category %s: saved %d/%d",
                category.slug,
                saved,
                self.per_category,
            )

        self.writer.write_summary(stats, target_per_category=self.per_category)
        return stats

    def _scrape_category(
        self,
        category: Category,
        stats: ScrapeStats,
        on_item_saved: Optional[Callable[[Category, int, int], None]],
    ) -> int:
        search_limit = self.per_category * self.search_multiplier
        try:
            captures = self.client.search_captures(
                category.cdx_url_pattern,
                limit=search_limit,
                to_date=self.to_date,
            )
        except Exception as e:
            logger.error("CDX search failed for %s: %s", category.slug, e)
            return 0

        saved = 0
        item_index = 0
        for cap in captures:
            if saved >= self.per_category:
                break
            if self.writer.already_have(category.slug, cap.original_url):
                stats.items_skipped += 1
                continue

            item_index += 1
            archive_date = archive_date_from_timestamp(cap.timestamp)

            try:
                html_bytes = self.client.fetch_snapshot_html(cap)
                plain = extract_text_from_bytes(html_bytes, "page.html")
                if len(plain) < self.min_plaintext_chars:
                    stats.items_skipped += 1
                    logger.debug(
                        "Skip short text (%d chars): %s",
                        len(plain),
                        cap.original_url,
                    )
                    continue

                raw_html = html_bytes.decode("utf-8", errors="replace")
                title = extract_title_from_html(raw_html)

                self.writer.save_post(
                    category_slug=category.slug,
                    category_name=category.name,
                    item_index=saved + 1,
                    source_url=cap.original_url,
                    archive_url=cap.archive_url,
                    archive_timestamp=cap.timestamp,
                    archive_date=archive_date,
                    html_bytes=html_bytes,
                    title=title,
                )
                saved += 1
                stats.items_saved += 1
                if on_item_saved:
                    on_item_saved(category, saved, self.per_category)

            except Exception as e:
                stats.items_failed += 1
                self.writer.save_error(
                    category_slug=category.slug,
                    category_name=category.name,
                    item_index=item_index,
                    source_url=cap.original_url,
                    archive_url=cap.archive_url,
                    archive_timestamp=cap.timestamp,
                    archive_date=archive_date,
                    error=str(e),
                )
                logger.warning("Fetch failed %s: %s", cap.original_url, e)

        return saved
