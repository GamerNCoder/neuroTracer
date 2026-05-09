"""Batch scoring API tests."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_config_endpoint():
    r = client.get("/api/v1/config")
    assert r.status_code == 200
    data = r.json()
    assert "local_path_batch_enabled" in data
    assert isinstance(data["local_path_batch_enabled"], bool)


def test_batch_paths_disabled_by_default():
    r = client.post(
        "/api/v1/score/batch/paths",
        json={"paths": ["/etc/passwd"], "skip_history": True},
    )
    assert r.status_code == 403


def test_batch_files_two_html(tmp_path):
    f1 = tmp_path / "a.html"
    f1.write_bytes(
        b"<html><body><p>First old blog sentence here. Second sentence with maybe doubt.</p></body></html>"
    )
    f2 = tmp_path / "b.txt"
    f2.write_text(
        "Another post from 2012. It has enough words to pass the minimum length check easily.",
        encoding="utf-8",
    )
    with open(f1, "rb") as fa, open(f2, "rb") as fb:
        r = client.post(
            "/api/v1/score/batch/files",
            data={"skip_history": "true"},
            files=[
                ("files", ("a.html", fa, "text/html")),
                ("files", ("b.txt", fb, "text/plain")),
            ],
        )
    assert r.status_code == 200
    data = r.json()
    assert len(data["results"]) == 2
    assert all(x["ok"] for x in data["results"])
    assert all(0.0 <= x["humanscore"] <= 1.0 for x in data["results"])


def test_batch_paths_with_allowlist(monkeypatch, tmp_path):
    root = tmp_path / "blogs"
    root.mkdir()
    sample = root / "post.html"
    sample.write_text(
        "<p>Old blog content from 2012. It rambles a bit. Perhaps the weather was nicer then?</p>",
        encoding="utf-8",
    )
    monkeypatch.setenv("NEUROTRACER_ALLOW_LOCAL_PATHS", "1")
    monkeypatch.setenv("NEUROTRACER_LOCAL_PATH_ROOT", str(root))
    r = client.post(
        "/api/v1/score/batch/paths",
        json={"paths": [str(sample)], "skip_history": True},
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["ok"] is True
    assert data["results"][0]["path"] == str(sample)


def test_batch_directory_glob(monkeypatch, tmp_path):
    root = tmp_path / "export"
    root.mkdir()
    (root / "one.html").write_text(
        "<html><body>Sentence one here. Sentence two there. Third sentence for drift.</body></html>"
    )
    (root / "skip.bin").write_bytes(b"\x00\x01")
    monkeypatch.setenv("NEUROTRACER_ALLOW_LOCAL_PATHS", "1")
    monkeypatch.setenv("NEUROTRACER_LOCAL_PATH_ROOT", str(root))
    r = client.post(
        "/api/v1/score/batch/paths",
        json={
            "directory": str(root),
            "glob_pattern": "*.html",
            "skip_history": True,
        },
    )
    assert r.status_code == 200
    names = {Path(x["path"]).name for x in r.json()["results"]}
    assert names == {"one.html"}
    assert r.json()["results"][0]["ok"] is True
