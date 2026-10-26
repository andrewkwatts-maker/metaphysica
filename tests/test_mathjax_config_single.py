"""The site has one MathJax configuration and one pinned MathJax version."""
from __future__ import annotations

import re
from pathlib import Path

WEBSITE = Path(__file__).resolve().parents[1] / "src" / "metaphysica" / "website"
PINNED = "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"
CONFIG_TAG = re.compile(r'<script\s+src="[^"]*js/mathjax-config\.js"')
MATHJAX_TAG = re.compile(r'<script[^>]*src="([^"]*mathjax[^"]*)"[^>]*>', re.I)
INLINE = re.compile(r"\bMathJax\s*=\s*\{")


def _pages():
    return sorted(p for p in WEBSITE.rglob("*.html"))


def test_no_page_carries_an_inline_mathjax_config():
    bad = [p.name for p in _pages() if INLINE.search(p.read_text(encoding="utf-8"))]
    assert bad == []


def test_every_mathjax_script_is_the_pinned_url():
    bad = []
    for page in _pages():
        for src in MATHJAX_TAG.findall(page.read_text(encoding="utf-8")):
            if src != PINNED and not src.endswith("mathjax-config.js"):
                bad.append((page.name, src))
    assert bad == []


def test_pages_with_mathjax_load_the_shared_config_first():
    bad = []
    for page in _pages():
        text = page.read_text(encoding="utf-8")
        cdn = text.find(PINNED)
        if cdn < 0:
            continue
        cfg = CONFIG_TAG.search(text)
        if cfg is None or cfg.start() > cdn:
            bad.append(page.name)
    assert bad == []


def test_shared_config_defines_slashed_and_the_delimiters():
    text = (WEBSITE / "js" / "mathjax-config.js").read_text(encoding="utf-8")
    assert "slashed" in text and "processEscapes: true" in text
    assert "window.MathJax" in text
