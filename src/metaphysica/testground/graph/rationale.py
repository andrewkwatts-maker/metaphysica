"""Rationale: split a fork's or option's prose into its labelled sections.

Fork and option texts are written with upper-case section headings -- ``BUYS:``,
``COSTS:``, ``DEMOTED 2026-10-01 (D-015):``, ``RULED OUT 2026-09-06, ...`` -- at
the start of a line or of a sentence. This module finds them, never rewrites
them: the sections are slices of the original text, so joining them gives the
text back exactly (`split_rationale`) or modulo whitespace (`parse_rationale`).
Text before the first heading is the section ``text``.

`decision_refs` extracts the decisions a text cites: ``D-NNN`` ids and
``ruling:YYYY-MM-DD`` references.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Pattern, Sequence, Tuple

__all__ = [
    "HEADINGS",
    "TEXT",
    "Section",
    "split_rationale",
    "parse_rationale",
    "rationale_sections",
    "decision_refs",
    "normalise_whitespace",
]

#: (heading keyword, section key). Longer keywords first, so ``RULED OUT`` is
#: never read as ``RULED``. Matching is case-sensitive: the headings are
#: upper case by convention, prose is not.
HEADINGS: Tuple[Tuple[str, str], ...] = (
    ("WHAT THAT REVEALS", "what_that_reveals"),
    ("ALSO LIMITED", "also_limited"),
    ("NOT ADOPTED", "not_adopted"),
    ("NOT AFFECTED", "not_affected"),
    ("RULED OUT", "ruled_out"),
    ("WITHDRAWN", "withdrawn"),
    ("RE-OPENS", "re_opens"),
    ("ASSUMES", "assumes"),
    ("DEMOTED", "demoted"),
    ("RULED", "ruled"),
    ("COSTS", "costs"),
    ("BUYS", "buys"),
    ("OPEN", "open"),
)

#: Key of the text before the first heading (and of a text without any).
TEXT = "text"

#: A heading's qualifier runs to the first colon on its line, at most this
#: many characters on and never across a sentence end; otherwise the heading
#: is the keyword alone.
_QUALIFIER_LIMIT = 100

_REF = re.compile(r"\bD-\d{3}\b|\bruling:\d{4}-\d{2}-\d{2}\b")


@dataclass(frozen=True)
class Section:
    """One labelled slice of a rationale text."""

    key: str
    heading: str
    body: str

    @property
    def raw(self) -> str:
        """The exact slice of the original text."""
        return self.heading + self.body


def _heading_pattern(headings: Sequence[Tuple[str, str]]) -> Pattern[str]:
    """A regex matching a heading at a line start or a sentence start."""
    keywords = "|".join(re.escape(k) for k, _ in
                        sorted(headings, key=lambda h: -len(h[0])))
    start = r"(?:\A|(?<=\n)[ \t]*|(?<=[.!?] )|(?<=[.!?]  )|(?<=[.!?]\) ))"
    qualifier = r"(?P<qual>(?:(?!\.\s)[^:\n]){0,%d}:)?" % _QUALIFIER_LIMIT
    return re.compile(start + r"(?P<kw>" + keywords + r")(?![A-Za-z0-9_-])"
                      + qualifier)


_DEFAULT_PATTERN = _heading_pattern(HEADINGS)


def _key_of(keyword: str, headings: Sequence[Tuple[str, str]]) -> str:
    return dict(headings)[keyword]


def split_rationale(text: str,
                    headings: Optional[Sequence[Tuple[str, str]]] = None
                    ) -> List[Section]:
    """The text cut at every heading; ``"".join(s.raw) == text`` exactly."""
    table = HEADINGS if headings is None else tuple(headings)
    pattern = _DEFAULT_PATTERN if headings is None else _heading_pattern(table)
    matches = [m for m in pattern.finditer(text or "")]
    sections: List[Section] = []
    first = matches[0].start("kw") if matches else len(text or "")
    if first > 0:
        sections.append(Section(TEXT, "", text[:first]))
    for i, match in enumerate(matches):
        begin = match.start("kw")
        end = matches[i + 1].start("kw") if i + 1 < len(matches) else len(text)
        heading_end = match.end("qual") if match.group("qual") else match.end("kw")
        sections.append(Section(_key_of(match.group("kw"), table),
                                text[begin:heading_end],
                                text[heading_end:end]))
    return sections


def _unique_key(key: str, taken: Dict[str, str]) -> str:
    """``costs``, then ``costs_2``, ``costs_3`` ... for repeated headings."""
    if key not in taken:
        return key
    n = 2
    while "%s_%d" % (key, n) in taken:
        n += 1
    return "%s_%d" % (key, n)


def parse_rationale(text: str,
                    headings: Optional[Sequence[Tuple[str, str]]] = None
                    ) -> Dict[str, str]:
    """Section key -> that section's text (heading included), in text order.

    Unmatched text goes under ``"text"``; whitespace-only slices are dropped;
    a repeated heading gets a numbered key. The values joined with spaces equal
    the original text modulo whitespace.
    """
    out: Dict[str, str] = {}
    for section in split_rationale(text, headings):
        raw = section.raw.strip()
        if raw:
            out[_unique_key(section.key, out)] = raw
    return out


def rationale_sections(text: str,
                       headings: Optional[Sequence[Tuple[str, str]]] = None
                       ) -> List[Dict[str, object]]:
    """JSON-ready sections (key, heading, body, refs) that keep their order."""
    out: List[Dict[str, object]] = []
    for section in split_rationale(text, headings):
        if not section.raw.strip():
            continue
        out.append({
            "key": section.key,
            "heading": section.heading.strip(),
            "body": section.body.strip(),
            "refs": list(decision_refs(section.raw)),
        })
    return out


def decision_refs(text: str) -> Tuple[str, ...]:
    """``D-NNN`` and ``ruling:YYYY-MM-DD`` references, unique, in text order."""
    seen: Dict[str, None] = {}
    for match in _REF.finditer(text or ""):
        seen.setdefault(match.group(0), None)
    return tuple(seen)


def normalise_whitespace(text: str) -> str:
    """Collapse every run of whitespace to one space (for round-trip checks)."""
    return " ".join((text or "").split())
