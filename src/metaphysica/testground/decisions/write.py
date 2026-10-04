"""Decision entries the test ground writes: templates and an append-only writer.

Three templates -- PATH ACCEPT (a configuration becomes the active path), PATH
RETIRE (an option is demoted to DISABLED) and PATH REINSTATE (a DISABLED option
is put back on the table) -- each rendered as a Markdown entry whose heading the
log parser reads back (``## D-NNN · <date> · PATH ACCEPT · <name>``).

`append_entry` adds an entry at the end of the log through a temporary file and
``os.replace``: the existing bytes are kept exactly, so nothing already in the
log is ever rewritten or removed.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Mapping, Optional, Sequence, Tuple

from metaphysica.testground.decisions.log import ACCEPT, REINSTATE, RETIRE

__all__ = [
    "RULE_CITATION",
    "AcceptEntry",
    "RetireEntry",
    "ReinstateEntry",
    "render_accept",
    "render_retire",
    "render_reinstate",
    "append_entry",
]

#: The governance every entry written here cites.
RULE_CITATION = (
    "Under the decision rule of D-019 (lexicographic: validity > closure > "
    "consistency > elegance, with data only as a disclosed tie-break); the "
    "assessment proposes, one explicit act accepts, nothing is adopted "
    "automatically.")

_SEPARATOR = "---"


def _heading(decision_id: str, date: str, kind: str, name: str) -> str:
    return "## %s · %s · %s · %s" % (decision_id, date, kind, name)


def _code(value: object) -> str:
    return "`%s`" % ("—" if value is None else value)


def _table(header: Sequence[str], rows: Sequence[Sequence[str]]) -> List[str]:
    lines = ["| " + " | ".join(header) + " |",
             "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return lines


@dataclass(frozen=True)
class AcceptEntry:
    """Everything a PATH ACCEPT entry states."""

    decision_id: str
    date: str
    theory: str
    name: str
    digest: str
    previous_name: str
    previous_digest: str
    kept_as: str
    diff: Mapping[str, Tuple[Optional[str], Optional[str]]]
    reason: str = ""
    assessment_verdict: Optional[str] = None
    target_verdict: Optional[str] = None
    deciding_criterion: Optional[str] = None
    #: (criterion, previous cell, target cell), in the D-019 order.
    scores: Sequence[Tuple[str, str, str]] = ()
    data_tiebreak: bool = False
    trials_factor: Optional[int] = None
    override_reason: str = ""
    stale_reasons: Sequence[str] = ()
    notes: Sequence[str] = field(default_factory=tuple)


def _diff_lines(diff: Mapping[str, Tuple[Optional[str], Optional[str]]]
                ) -> List[str]:
    if not diff:
        return ["No fork changes option: the selection is identical."]
    rows = [(_code(fork), _code(old), _code(new))
            for fork, (old, new) in sorted(diff.items())]
    return _table(("fork", "was", "now"), rows)


def _assessment_lines(entry: AcceptEntry) -> List[str]:
    if entry.assessment_verdict is None:
        return ["**Assessment.** None supplied: this accept rests on the "
                "reason stated here, not on a comparator run."]
    lines = ["**Assessment.** Verdict %s; the accepted configuration's own "
             "verdict %s; deciding criterion %s."
             % (_code(entry.assessment_verdict), _code(entry.target_verdict),
                _code(entry.deciding_criterion))]
    if entry.scores:
        lines += ["", "**Score breakdown** (criteria in the D-019 order; each "
                      "key a tuple of integers, lower is better).", ""]
        lines += _table(("criterion", "was (%s)" % _code(entry.previous_digest),
                         "now (%s)" % _code(entry.digest)),
                        [(c, a, b) for c, a, b in entry.scores])
    return lines


def _tiebreak_lines(entry: AcceptEntry) -> List[str]:
    if not entry.data_tiebreak:
        return []
    k = "unknown" if entry.trials_factor is None else str(entry.trials_factor)
    return ["**Data tie-break.** The configurations tie on criteria 1–4 and "
            "agreement with data decided, with trials factor k = %s. Accepting "
            "on it counts one fitted degree of freedom (data_tiebreak_dof "
            "+1)." % k]


def _override_lines(entry: AcceptEntry) -> List[str]:
    if not entry.override_reason:
        return []
    lines = ["**Override.** %s" % entry.override_reason]
    lines += ["- overridden: %s" % s for s in entry.stale_reasons]
    return lines


def render_accept(entry: AcceptEntry) -> str:
    """The Markdown text of a PATH ACCEPT entry (ends with a newline)."""
    blocks: List[List[str]] = [
        [_heading(entry.decision_id, entry.date, ACCEPT, entry.name)],
        ["**Target.** Configuration %s, digest %s, of theory %s, accepted as "
         "the active path." % (_code(entry.name), _code(entry.digest),
                               _code(entry.theory))],
        ["**Replaces.** %s, digest %s, kept switchable as the named "
         "configuration %s. Nothing is deleted."
         % (_code(entry.previous_name), _code(entry.previous_digest),
            _code(entry.kept_as))],
        ["**Selection diff.**", ""] + _diff_lines(entry.diff),
        _assessment_lines(entry),
        _tiebreak_lines(entry),
        ["**Reason.** %s" % entry.reason] if entry.reason else [],
        _override_lines(entry),
        ["**Notes.**", ""] + ["- %s" % n for n in entry.notes]
        if entry.notes else [],
        ["**Rule.** " + RULE_CITATION],
    ]
    return "\n\n".join("\n".join(b) for b in blocks if b) + "\n"


@dataclass(frozen=True)
class RetireEntry:
    """Everything a PATH RETIRE entry states."""

    decision_id: str
    date: str
    theory: str
    fork: str
    option: str
    certainty: str
    reason: str
    previous_status: str
    evidence: str = ""
    kill_condition: str = ""


def _target(fork: str, option: str) -> str:
    return "%s.%s" % (fork, option)


def render_retire(entry: RetireEntry) -> str:
    """The Markdown text of a PATH RETIRE entry (ends with a newline)."""
    where = ("mode `archaeology` still runs it" if entry.certainty == "certain"
             else "mode `reassess` still sweeps it")
    blocks = [
        _heading(entry.decision_id, entry.date, RETIRE,
                 _target(entry.fork, entry.option)),
        "**Target.** Option %s of fork %s (theory %s), retired: status "
        "DISABLED (was %s), certainty %s." % (
            _code(entry.option), _code(entry.fork), _code(entry.theory),
            entry.previous_status.upper(), _code(entry.certainty)),
        "**Reason.** %s" % entry.reason,
        "**Evidence.** %s" % entry.evidence if entry.evidence else "",
        "**Kill condition.** %s" % entry.kill_condition
        if entry.kill_condition else "",
        "**Kept.** The option stays declared and runnable; it leaves the "
        "default assessment and %s. Dead ends are demoted and labelled, never "
        "deleted." % where,
        "**Rule.** " + RULE_CITATION,
    ]
    return "\n\n".join(b for b in blocks if b) + "\n"


@dataclass(frozen=True)
class ReinstateEntry:
    """Everything a PATH REINSTATE entry states."""

    decision_id: str
    date: str
    theory: str
    fork: str
    option: str
    reason: str
    previous_certainty: Optional[str] = None


def render_reinstate(entry: ReinstateEntry) -> str:
    """The Markdown text of a PATH REINSTATE entry (ends with a newline)."""
    blocks = [
        _heading(entry.decision_id, entry.date, REINSTATE,
                 _target(entry.fork, entry.option)),
        "**Target.** Option %s of fork %s (theory %s), reinstated: status "
        "CONSIDERED (was DISABLED, certainty %s)." % (
            _code(entry.option), _code(entry.fork), _code(entry.theory),
            _code(entry.previous_certainty or "reassessable")),
        "**Reason.** %s" % entry.reason,
        "**Rule.** " + RULE_CITATION,
    ]
    return "\n\n".join(blocks) + "\n"


def _newline_of(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def _joined(existing: str, entry: str) -> str:
    """``existing`` + separator + ``entry`` in the existing newline style."""
    nl = _newline_of(existing)
    body = entry.replace("\r\n", "\n").rstrip("\n").replace("\n", nl) + nl
    if not existing.strip():
        return existing + body
    head = existing if existing.endswith(nl) else existing + nl
    last = [line for line in head.splitlines() if line.strip()][-1]
    separator = nl if last.strip() == _SEPARATOR else nl + _SEPARATOR + nl + nl
    return head + separator + body


def _atomic_write(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".tmp",
                               dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _continued(existing: str, note: str) -> str:
    """``existing`` + a blank line + ``note`` (no separator: same entry)."""
    nl = _newline_of(existing)
    head = existing if existing.endswith(nl) or not existing else existing + nl
    body = note.replace("\r\n", "\n").strip("\n").replace("\n", nl) + nl
    return head + (nl if head else "") + body


def append_entry(path: Path, entry: str, separate: bool = True) -> str:
    """Append ``entry`` to the log at ``path``; return the new full text.

    The existing content is preserved byte for byte. With ``separate`` a
    ``---`` separator is added first (unless the log already ends with one);
    without it the text continues the last entry (used for a follow-up note).
    """
    path = Path(path)
    existing = ""
    if path.is_file():
        with open(path, encoding="utf-8", newline="") as handle:
            existing = handle.read()
    text = _joined(existing, entry) if separate else _continued(existing, entry)
    _atomic_write(path, text)
    return text
