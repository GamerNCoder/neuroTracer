"""Scraper unit tests (mocked Wayback; no network)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from engine.scraper.categories import CATEGORIES
from engine.scraper.runner import ScrapeRunner
from engine.scraper.storage import CorpusWriter
from engine.scraper.wayback import (
    ArchiveCapture,
    WaybackClient,
    _is_likely_blog_post,
    archive_date_from_timestamp,
    extract_title_from_html,
)


def test_categories_count():
    assert len(CATEGORIES) == 20


def test_is_likely_blog_post():
    assert _is_likely_blog_post("http://foo.blogspot.com/2010/03/my-trip.html")
    assert not _is_likely_blog_post("http://foo.blogspot.com/")
    assert not _is_likely_blog_post("http://foo.blogspot.com/search")


def test_archive_date_from_timestamp():
    assert archive_date_from_timestamp("20110615120000") == "2011-06-15"


def test_extract_title():
    html = "<html><head><title>My Old Post</title></head><body>x</body></html>"
    assert extract_title_from_html(html) == "My Old Post"


def test_corpus_writer_resume(tmp_path):
    out = tmp_path / "corpus"
    w = CorpusWriter(out)
    w.save_post(
        category_slug="travel",
        category_name="Travel",
        item_index=1,
        source_url="http://a.blogspot.com/2010/post.html",
        archive_url="https://web.archive.org/web/20100101/http://a.blogspot.com/2010/post.html",
        archive_timestamp="20100101120000",
        archive_date="2010-01-01",
        html_bytes=b"<html><body>" + b"word " * 80 + b"</body></html>",
        title="T",
    )
    assert w.already_have("travel", "http://a.blogspot.com/2010/post.html")
    assert not w.already_have("travel", "http://other.blogspot.com/x.html")
    assert w.manifest_path.exists()
    lines = w.manifest_path.read_text().strip().splitlines()
    row = json.loads(lines[0])
    assert row["status"] == "ok"
    assert row["category"] == "travel"
    assert row["archive_date"] == "2010-01-01"
    assert (out / "travel").exists()
    html_file = out / row["html_path"]
    assert html_file.is_file(), "HTML file must exist on disk when status=ok"
    assert html_file.stat().st_size > 0


@patch.object(WaybackClient, "search_captures")
@patch.object(WaybackClient, "fetch_snapshot_html")
def test_runner_loop(mock_fetch, mock_search, tmp_path):
    mock_search.return_value = [
        ArchiveCapture(
            original_url="http://x.blogspot.com/2009/01/hello-world.html",
            timestamp="20090101120000",
            archive_url="https://web.archive.org/web/20090101120000/http://x.blogspot.com/2009/01/hello-world.html",
        ),
        ArchiveCapture(
            original_url="http://y.blogspot.com/2008/02/another.html",
            timestamp="20080202120000",
            archive_url="https://web.archive.org/web/20080202120000/http://y.blogspot.com/2008/02/another.html",
        ),
    ]
    body = b"<html><head><title>Hi</title></head><body>" + b"content " * 60 + b"</body></html>"
    mock_fetch.return_value = body

    writer = CorpusWriter(tmp_path / "out")
    client = MagicMock(spec=WaybackClient)
    client.search_captures = mock_search
    client.fetch_snapshot_html = mock_fetch

    runner = ScrapeRunner(
        writer,
        client,
        per_category=2,
        max_categories=1,
        min_plaintext_chars=100,
    )
    stats = runner.run()
    assert stats.items_saved == 2
    assert stats.by_category[CATEGORIES[0].slug] == 2
    assert (tmp_path / "out" / "scrape_summary.json").exists()


def test_search_captures_parses_cdx():
    cdx_rows = [
        ["urlkey", "timestamp", "original", "mimetype", "statuscode"],
        [
            "com,blogspot)/2009/01/post",
            "20090101120000",
            "http://example.blogspot.com/2009/01/post.html",
            "text/html",
            "200",
        ],
    ]
    with patch("httpx.Client") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_resp = MagicMock()
        mock_resp.json.return_value = cdx_rows
        mock_resp.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_resp

        with WaybackClient(request_delay_sec=0) as wb:
            caps = wb.search_captures("*.blogspot.com/*", limit=5)
        assert len(caps) == 1
        assert "post.html" in caps[0].original_url
