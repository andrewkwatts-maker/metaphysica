"""Decision log: parse a Markdown log of ``## D-NNN · ...`` entries (read-only).

A decision log records every change to the active path BEFORE it is computed,
with results appended as later entries under the same id. Headings look like::

    ## D-001 · 2026-09-30 · G0 · PRE-REGISTERED
    ## D-001 · RESULT · 2026-09-30 · CONFIRMED (lead run)
    ## D-001 / D-002 · INDEPENDENT VERIFICATION · 2026-09-30
    ## D-003 · ADDENDUM · the split form does not support the resolution
    ## D-015 · 2026-10-01 · RULINGS — the author's, on the four held decisions
    ## D-021 · 2026-10-02 · PATH ACCEPT · <configuration name>

so a heading is: ids, then `` · ``-separated segments (a date, an optional
follow-up label such as RESULT / ADDENDUM / VERIFICATION, a gate, a status),
with an optional `` — title``. Every entry keeps its body (the text up to the
next ``## `` heading), and the merged view of one id (`Decision`) gives the
date, title, latest status and summary (first paragraph) the path graph draws.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

__all__ = [
    "ENTRY",
    "RESULT",
    "ADDENDUM",
    "VERIFICATION",
    "ACCEPT",
    "RETIRE",
    "REINSTATE",
    "PATH_KINDS",
    "DecisionEntry",
    "Decision",
    "DecisionLog",
    "is_decision_id",
    "parse_heading",
    "parse_log",
    "load_log",
    "next_id",
    "exists",
]

# entry kinds
ENTRY = "ENTRY"                  # an original entry (pre-registration, ruling)
RESULT = "RESULT"
ADDENDUM = "ADDENDUM"
VERIFICATION = "VERIFICATION"
ACCEPT = "PATH ACCEPT"           # written by the test ground's accept()
RETIRE = "PATH RETIRE"           # written by retire()
REINSTATE = "PATH REINSTATE"     # written by reinstate()

#: The test ground's own entry kinds and the status each one records.
PATH_KINDS: Dict[str, str] = {
    ACCEPT: "ACCEPTED",
    RETIRE: "RETIRED",
    REINSTATE: "REINSTATED",
}

_SEPARATOR = re.compile(r"\s+·\s+")
_TITLE_DASH = " — "
_IDS = re.compile(r"^D-\d{3}(?:\s*/\s*D-\d{3})*$")
_ID = re.compile(r"D-\d{3}")
_ONE_ID = re.compile(r"^D-\d{3}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_FOLLOW_UP = re.compile(
    r"^(?P<kind>RESULT|ADDENDUM|VERIFICATION)(?:\s+\d+)?$"
    r"|^(?:INDEPENDENT|BLIND)\s+(?P<verif>VERIFICATION)$")
_TARGET_DIGEST = re.compile(r"digest `(?P<digest>[0-9a-f]{16})`")
_BOLD_LABEL = re.compile(r"^\*\*[^*]{1,40}\*\*\s*")
_TITLE_LIMIT = 120


def is_decision_id(text: str) -> bool:
    """True for a well-formed decision id such as ``D-019``."""
    return bool(_ONE_ID.match(text or ""))


def _segments(text: str) -> List[str]:
    return [s.strip() for s in _SEPARATOR.split(text) if s.strip()]


def _follow_up_kind(segment: str) -> Optional[str]:
    match = _FOLLOW_UP.match(segment)
    if not match:
        return None
    return match.group("kind") or match.group("verif")


def parse_heading(heading: str) -> Optional[Dict[str, Any]]:
    """The parts of a decision heading (without ``## ``), or None.

    Returns ``ids, date, kind, label, gate, status, title``; None when the
    heading does not start with decision ids (e.g. ``How decisions are made``).
    """
    parts = _SEPARATOR.split(heading.strip(), maxsplit=1)
    if not _IDS.match(parts[0].strip()):
        return None
    rest = parts[1] if len(parts) > 1 else ""
    title = ""
    if _TITLE_DASH in rest:
        rest, title = rest.split(_TITLE_DASH, 1)
    date: Optional[str] = None
    others: List[str] = []
    for segment in _segments(rest):
        if date is None and _DATE.match(segment):
            date = segment
        else:
            others.append(segment)
    out: Dict[str, Any] = {"ids": tuple(_ID.findall(parts[0])), "date": date,
                           "kind": ENTRY, "label": "", "gate": "",
                           "status": "", "title": title.strip()}
    if others and others[0] in PATH_KINDS:
        out.update(kind=others[0], label=others[0], status=PATH_KINDS[others[0]],
                   title=out["title"] or " · ".join(others[1:]))
        return out
    if others and _follow_up_kind(others[0]):
        out["kind"] = _follow_up_kind(others[0])
        out["label"] = others.pop(0)
    if not out["title"] and others and others[-1][:1].islower():
        out["title"] = others.pop()
    out["status"] = others[-1] if others else out["label"]
    out["gate"] = " · ".join(others[:-1])
    return out


def _first_paragraph(body: str) -> str:
    """The first non-empty paragraph of a body, whitespace collapsed."""
    for block in re.split(r"\n\s*\n", body):
        text = " ".join(block.split())
        if text and text != "---":
            return text
    return ""


@dataclass(frozen=True)
class DecisionEntry:
    """One ``## D-NNN`` section of the log."""

    ids: Tuple[str, ...]
    heading: str
    line: int
    date: Optional[str]
    kind: str
    label: str
    gate: str
    status: str
    title: str
    body: str

    @property
    def id(self) -> str:
        return self.ids[0]

    @property
    def summary(self) -> str:
        return _first_paragraph(self.body)

    @property
    def target_name(self) -> str:
        """For a PATH entry: the configuration or option it acted on."""
        return self.title if self.kind in PATH_KINDS else ""

    @property
    def target_digest(self) -> Optional[str]:
        """For a PATH ACCEPT entry: the first digest named in its body."""
        if self.kind != ACCEPT:
            return None
        match = _TARGET_DIGEST.search(self.body)
        return match.group("digest") if match else None

    def as_dict(self) -> Dict[str, Any]:
        return {"heading": self.heading, "line": self.line, "date": self.date,
                "kind": self.kind, "gate": self.gate, "status": self.status,
                "title": self.title}


def _derived_title(summary: str) -> str:
    """A title from a summary's first sentence, when no heading gives one."""
    text = _BOLD_LABEL.sub("", summary)
    sentence = re.split(r"(?<=[.?!])\s", text, maxsplit=1)[0]
    if len(sentence) > _TITLE_LIMIT:
        sentence = sentence[:_TITLE_LIMIT - 1].rstrip() + "…"
    return sentence


@dataclass(frozen=True)
class Decision:
    """All entries of one decision id, merged for display."""

    id: str
    entries: Tuple[DecisionEntry, ...]

    @property
    def date(self) -> Optional[str]:
        return next((e.date for e in self.entries if e.date), None)

    @property
    def title(self) -> str:
        titled = next((e.title for e in self.entries if e.title), "")
        return titled or _derived_title(self.summary)

    @property
    def status(self) -> str:
        """The latest entry's status: where the decision stands now."""
        return self.entries[-1].status if self.entries else ""

    @property
    def summary(self) -> str:
        return self.entries[0].summary if self.entries else ""

    def as_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "date": self.date, "title": self.title,
                "status": self.status, "summary": self.summary,
                "entries": [e.as_dict() for e in self.entries]}


def _iter_sections(text: str):
    """(line number, heading, body) for every ``## `` heading outside fences."""
    current: Optional[Tuple[int, str]] = None
    body: List[str] = []
    fenced = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        if not fenced and line.startswith("## "):
            if current is not None:
                yield current[0], current[1], "\n".join(body)
            current, body = (number, line[3:].strip()), []
        elif current is not None:
            body.append(line)
    if current is not None:
        yield current[0], current[1], "\n".join(body)


def _clean_body(body: str) -> str:
    lines = body.strip("\n").splitlines()
    while lines and lines[-1].strip() in ("", "---"):
        lines.pop()
    return "\n".join(lines).strip("\n")


def parse_log(text: str) -> List[DecisionEntry]:
    """Every decision entry of a log, in file order."""
    entries: List[DecisionEntry] = []
    for line, heading, body in _iter_sections(text):
        parts = parse_heading(heading)
        if parts is None:
            continue
        entries.append(DecisionEntry(heading=heading, line=line,
                                     body=_clean_body(body), **parts))
    return entries


class DecisionLog:
    """A parsed decision log: lookups by id, the next free id."""

    def __init__(self, entries: Sequence[DecisionEntry],
                 path: Optional[Path] = None) -> None:
        self.entries: Tuple[DecisionEntry, ...] = tuple(entries)
        self.path = path

    @classmethod
    def parse(cls, text: str, path: Optional[Path] = None) -> "DecisionLog":
        return cls(parse_log(text), path)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "DecisionLog":
        """Parse the log at ``path``; a missing file is an empty log."""
        path = Path(path)
        if not path.is_file():
            return cls((), path)
        return cls.parse(path.read_text(encoding="utf-8"), path)

    def ids(self) -> List[str]:
        return sorted({i for e in self.entries for i in e.ids})

    def exists(self, decision_id: str) -> bool:
        return any(decision_id in e.ids for e in self.entries)

    def next_id(self) -> str:
        numbers = [int(i[2:]) for i in self.ids()]
        return "D-%03d" % (max(numbers, default=0) + 1)

    def entries_for(self, decision_id: str) -> List[DecisionEntry]:
        return [e for e in self.entries if decision_id in e.ids]

    def decision(self, decision_id: str) -> Optional[Decision]:
        entries = self.entries_for(decision_id)
        return Decision(decision_id, tuple(entries)) if entries else None

    def decisions(self) -> List[Decision]:
        return [Decision(i, tuple(self.entries_for(i))) for i in self.ids()]

    def of_kind(self, kind: str) -> List[DecisionEntry]:
        return [e for e in self.entries if e.kind == kind]


LogSource = Union[DecisionLog, str, Path]


def load_log(path: Union[str, Path]) -> DecisionLog:
    return DecisionLog.load(path)


def _as_log(source: LogSource) -> DecisionLog:
    return source if isinstance(source, DecisionLog) else load_log(source)


def next_id(source: LogSource) -> str:
    """The next free ``D-NNN`` after the highest id in the log."""
    return _as_log(source).next_id()


def exists(source: LogSource, decision_id: str) -> bool:
    """True when the log has at least one entry for ``decision_id``."""
    return _as_log(source).exists(decision_id)
