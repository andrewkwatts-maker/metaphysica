"""Static checks for the Paths page and the site-wide path context (brief E2, D-021)."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "src" / "metaphysica" / "website"
PAGES = sorted((SITE / "Pages").glob("*.html")) + [SITE / "index.html"]
NODE = shutil.which("node")
JS_FILES = [SITE / "js" / "pm-path-context.js", SITE / "js" / "pm-paths-page.js"]


def _first_head_child(text: str) -> str:
    head = re.search(r"<head[^>]*>\s*(.*)", text, re.S | re.I)
    assert head, "no <head>"
    return head.group(1).lstrip()[:200]


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_path_context_script_first_in_head(page: Path):
    text = page.read_text(encoding="utf-8")
    prefix = "../js/" if page.parent.name == "Pages" else "js/"
    expected = f'<script src="{prefix}pm-path-context.js"></script>'
    assert _first_head_child(text).startswith(expected), page.name


def test_nav_has_paths_entry():
    header = (SITE / "js" / "pm-header.js").read_text(encoding="utf-8")
    assert re.search(r"href:\s*'paths\.html',\s*label:\s*'Paths',\s*id:\s*'paths'", header)


def test_paths_page_references_js_and_css():
    text = (SITE / "Pages" / "paths.html").read_text(encoding="utf-8")
    assert "../js/pm-paths-page.js" in text
    assert "../css/pm-paths.css" in text
    assert "<noscript>" in text


def test_paths_page_uses_no_innerhtml():
    for f in JS_FILES:
        assert "innerHTML" not in f.read_text(encoding="utf-8"), f.name


@pytest.mark.skipif(NODE is None, reason="node is not on PATH")
@pytest.mark.parametrize("js", JS_FILES, ids=lambda p: p.name)
def test_js_parses(js: Path):
    r = subprocess.run([NODE, "--check", str(js)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


@pytest.mark.skipif(NODE is None, reason="node is not on PATH")
def test_path_context_unit_tests():
    r = subprocess.run([NODE, "--test", str(REPO / "tests" / "js" / "path_context.test.mjs")],
                       capture_output=True, text=True, cwd=str(REPO))
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-1000:]
