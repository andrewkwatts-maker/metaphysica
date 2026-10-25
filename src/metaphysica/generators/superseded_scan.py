"""Scan sections.json for prose presenting the retired b3 = 24 / TCS geometry.

Active geometry is seed_43_joyce (D-025). A block that still presents b3 = 24,
twisted connected sums or fano_tcs as active is a hit, unless it sits inside a
"superseded path" callout (marked by SUPERSEDED_MARK).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple

from metaphysica.generators._common import autogen_dir

#: Marker the shared callout puts in its text; hits inside it are fine.
SUPERSEDED_MARK = "Superseded path"

_B3_24 = re.compile(r"\bb\s*(?:_\s*\{?\s*3\s*\}?|₃|3)\s*(?:=|\?equiv|:)\s*24\b"
                    r"|\bb_?\{?3\}?\s*=\s*24\b|\bb₃\s*=\s*24\b"
                    r"|\bb3\s*=\s*24\b|\bbetti_?3\s*=\s*24\b", re.I)
_WORDS = re.compile(r"\bTCS\b|twisted[ -]connected[ -]sum|fano[_ -]?tcs", re.I)

#: A hit whose surrounding text carries one of these already says the geometry
#: is retired, so it is not presented as active.
_RETIRED = re.compile(
    r"off-path|retired|superseded|withdrawn|formerly|previously|earlier|"
    r"was false|falsified|abandoned|not among|seed_24|used to|no longer|"
    r"not a (?:twisted|TCS)|not (?:the )?TCS|excludes|stood at|"
    r"originally|old wording|\bwas (?:its|fitted|written)|artefact|"
    r"is not in it|suspended|record of|rejected|replaced|is OFF|now off|"
    r"published as|no published|not read off|not taken from|"
    r"relocated from|belonged to|read \"|typed", re.I)
_WINDOW = 220


def _strings(node: Any, path: str) -> Iterator[Tuple[str, str]]:
    """Yield (path, text) for every string under node."""
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            if k in ("html", "content_blocks"):
                continue  # html is derived; content_blocks duplicates contentBlocks
            yield from _strings(v, "%s.%s" % (path, k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _strings(v, "%s[%d]" % (path, i))


def is_hit(text: str) -> bool:
    """True when text presents the retired geometry."""
    return bool(_B3_24.search(text) or _WORDS.search(text))


def scan_sections(sections: Dict[str, Any]) -> List[Dict[str, str]]:
    """All hits as dicts: section, path, in_callout, snippet."""
    hits = []
    for sid, sec in sections.items():
        for path, text in _strings(sec, sid):
            if not is_hit(text):
                continue
            m = _B3_24.search(text) or _WORDS.search(text)
            lo = max(0, m.start() - 60)
            near = text[max(0, m.start() - _WINDOW):m.end() + _WINDOW]
            hits.append({"section": sid, "path": path,
                         "in_callout": (SUPERSEDED_MARK in text
                                        or bool(_RETIRED.search(near))),
                         "snippet": text[lo:m.end() + 60].replace("\n", " ")})
    return hits


def load_hits(path: Path = None) -> List[Dict[str, str]]:
    """Scan the published sections.json."""
    path = path or autogen_dir() / "sections.json"
    if not path.is_file():
        raise SystemExit("superseded_scan: %s missing" % path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return scan_sections(data["sections"])


def active_hits(hits: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Hits outside a superseded callout."""
    return [h for h in hits if not h["in_callout"]]


if __name__ == "__main__":
    hs = load_hits()
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    text = json.dumps(hs, indent=1, ensure_ascii=False)
    if out:
        out.write_text(text, encoding="utf-8")
    print(len(hs), len(active_hits(hs)))
