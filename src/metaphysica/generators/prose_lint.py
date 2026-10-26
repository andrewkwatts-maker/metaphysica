"""Prose lints for the published paper text: long sentences, filler, version tags.

Pure functions over ``(where, text)``; each returns a list of ``Finding``.
``section_items`` and ``page_items`` adapt the published surfaces (sections.json,
Pages html and the website source pages) to ``(where, kind, text)`` triples so
the lints never touch the filesystem.

Checks
- ``long_sentence``: a sentence over ``MAX_WORDS`` words (markup and maths removed).
- ``filler``: stock padding phrases that add no content.
- ``version_tag``: an internal version tag (v22, v23.1, _v19) in a reader-facing
  title or heading.
- ``duplicate_paragraph``: the same paragraph published in more than one section.
"""
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Tuple

MAX_WORDS = 40
#: Shortest paragraph (in words) that counts as a duplicate; shorter ones are
#: captions and labels that legitimately repeat.
MIN_DUPLICATE_WORDS = 12

FILLER = ("it is important to note", "it should be noted", "in order to",
          "clearly", "obviously", "essentially", "very", "basically", "note that")
_FILLER_RX = re.compile(r"\b(?:%s)\b" % "|".join(re.escape(p) for p in FILLER), re.I)
_VERSION_RX = re.compile(r"(?<![A-Za-z0-9])v\d+(?:\.\d+)*(?!\w)|_v\d+(?!\w)", re.I)

_TAG = re.compile(r"<[^>]+>")
_MATH = re.compile(r"\$\$.+?\$\$|\$[^$\n]+\$|\\\(.+?\\\)|\\\[.+?\\\]", re.S)
_DROP_BLOCK = re.compile(r"<(script|style|svg|pre|code)\b.*?</\1>", re.S | re.I)
_PARA = re.compile(r"</?(?:p|div|li|ul|ol|h[1-6]|br|tr|table|section|blockquote)\b[^>]*>",
                   re.I)
_HEADING = re.compile(r"<h[1-6]\b[^>]*>(.*?)</h[1-6]>", re.S | re.I)
#: Full stops that do not end a sentence.
_ABBREV = re.compile(r"\b(?:e\.g|i\.e|etc|cf|vs|et al|Fig|Figs|Eq|Eqs|Sec|Ref|Refs"
                     r"|approx|resp|No|Vol|pp|Dr|Prof)\.", re.I)
_DOT = "\u0001"
_SENT_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(\[\"'])")


@dataclass(frozen=True)
class Finding:
    """One lint result: which check, where, and the offending text."""
    check: str
    where: str
    text: str


def plain(text: str) -> str:
    """Reader text of an HTML fragment: no scripts, tags or maths; entities decoded."""
    text = _DROP_BLOCK.sub(" ", text)
    text = _MATH.sub(" X ", html.unescape(text)) if "<" not in text else \
        html.unescape(_MATH.sub(" X ", _TAG.sub(" ", text)))
    return re.sub(r"\s+", " ", text).strip()


def paragraphs(text: str) -> List[str]:
    """Paragraph-level plain texts of an HTML fragment (block tags split)."""
    text = _DROP_BLOCK.sub(" ", text)
    parts = _PARA.split(text) if "<" in text else re.split(r"\n\s*\n", text)
    return [p for p in (plain(x) for x in parts) if p]


def sentences(text: str) -> List[str]:
    """Split plain text into sentences, keeping abbreviations and decimals whole."""
    safe = _ABBREV.sub(lambda m: m.group(0).replace(".", _DOT), text)
    safe = re.sub(r"(?<=\d)\.(?=\d)", _DOT, safe)
    return [s.replace(_DOT, ".").strip() for s in _SENT_END.split(safe) if s.strip()]


def _words(sentence: str) -> int:
    return len(sentence.split())


def long_sentences(where: str, text: str, limit: int = MAX_WORDS) -> List[Finding]:
    """Sentences of more than ``limit`` words."""
    return [Finding("long_sentence", where, s)
            for p in paragraphs(text) for s in sentences(p) if _words(s) > limit]


def filler(where: str, text: str) -> List[Finding]:
    """One finding per filler phrase occurrence."""
    return [Finding("filler", where, m.group(0).lower())
            for p in paragraphs(text) for m in _FILLER_RX.finditer(_MATH.sub(" X ", p))]


def version_tags(where: str, title: str) -> List[Finding]:
    """Internal version tags in a reader-facing title or heading."""
    return [Finding("version_tag", where, m.group(0))
            for m in _VERSION_RX.finditer(plain(title))]


def headings(text: str) -> List[str]:
    """Inner texts of the h1..h6 elements of an HTML fragment."""
    return [m.group(1) for m in _HEADING.finditer(text)]


def duplicate_paragraphs(items: Iterable[Tuple[str, str]]) -> List[Finding]:
    """Paragraphs published under more than one distinct ``where`` (one finding each).

    ``items`` is ``(where, html-or-text)``; ``where`` is the section id, so a
    paragraph repeated inside one section is not a duplicate.
    """
    seen: Dict[str, set] = {}
    for where, text in items:
        for p in paragraphs(text):
            if _words(p) >= MIN_DUPLICATE_WORDS:
                seen.setdefault(p, set()).add(where)
    return [Finding("duplicate_paragraph", ",".join(sorted(w)[:3]), p)
            for p, w in seen.items() if len(w) > 1]


# --- surfaces ---------------------------------------------------------------

Item = Tuple[str, str, str]   # (where, kind, text); kind is "title" or "body"


def section_items(sections: Dict[str, dict]) -> Iterator[Item]:
    """(where, kind, text) for every title and block of a sections.json dict."""
    for sid, sec in sections.items():
        sid = str(sec.get("id", sid))
        for key in ("title", "shortTitle"):
            if sec.get(key):
                yield "%s.%s" % (sid, key), "title", sec[key]
        if sec.get("abstract"):
            yield "%s.abstract" % sid, "body", sec["abstract"]
        for i, blk in enumerate(sec.get("contentBlocks") or []):
            at = "%s[%d]" % (sid, i)
            if blk.get("title"):
                yield at + ".title", "title", blk["title"]
            if isinstance(blk.get("content"), str):
                yield at, "body", blk["content"]
                for h in headings(blk["content"]):
                    yield at + ".heading", "title", h


def page_items(root: Path, patterns: Tuple[str, ...] = ("*.html",)) -> Iterator[Item]:
    """(where, kind, text) for each html page: its headings and its body text."""
    for pat in patterns:
        for f in sorted(root.glob(pat)):
            text = f.read_text(encoding="utf-8", errors="replace")
            for h in headings(text):
                yield f.name, "title", h
            yield f.name, "body", text


def lint_items(items: Iterable[Item]) -> List[Finding]:
    """Run every lint over the items."""
    out: List[Finding] = []
    bodies: List[Tuple[str, str]] = []
    for where, kind, text in items:
        if kind == "title":
            out += version_tags(where, text)
        else:
            out += long_sentences(where, text) + filler(where, text)
            bodies.append((where.split("[")[0].split(".")[0], text))
    return out + duplicate_paragraphs(bodies)


def counts(findings: Iterable[Finding]) -> Dict[str, int]:
    """Findings per check; every check is present, zero when clean."""
    out = {"long_sentence": 0, "filler": 0, "version_tag": 0, "duplicate_paragraph": 0}
    for f in findings:
        out[f.check] += 1
    return out


def load_sections(root: Path) -> Dict[str, dict]:
    """sections.json of a published tree; fails early when it is missing."""
    path = root / "AutoGenerated" / "sections.json"
    if not path.is_file():
        raise SystemExit("prose_lint: %s missing" % path)
    return json.loads(path.read_text(encoding="utf-8"))["sections"]


if __name__ == "__main__":
    import sys
    base = Path(sys.argv[1])
    found = lint_items(list(section_items(load_sections(base)))
                       + list(page_items(base / "Pages")))
    print(counts(found))
    for fd in found[:int(sys.argv[2]) if len(sys.argv) > 2 else 0]:
        print(fd.check, fd.where, "|", fd.text[:160].encode("ascii", "replace").decode())
