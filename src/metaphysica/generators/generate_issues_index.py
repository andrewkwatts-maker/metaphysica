"""Turn the outstanding-issues register into a measured set.

WHY THIS EXISTS
===============
``docs/OUTSTANDING_ISSUES.md`` is the project's authority -- "Where a companion
and this file disagree, this file wins" -- but it is prose, and it is two
documents in one:

  * a NUMBERED REGISTER (Tier 1/2/3, entries like ``### 1.1 ...``), and
  * a CHRONOLOGICAL PASS LOG of dated sections that amend, supersede and
    sometimes withdraw those numbered entries.

The pass log is the later authority, and nothing enforced that ordering. A
numbered entry can therefore read as live when a later pass has already
withdrawn it -- which has happened: b_3 = 24 was refuted in the fifteenth pass,
the refutation withdrawn in the sixteenth, and re-established on different
grounds in the nineteenth.

This module derives an index so "all known issues" becomes a count rather than
a reading. It PARSES; it never edits the register, and it never invents a
status -- every status word it reports is vocabulary the register itself uses.

WHAT IT DOES NOT DO
===================
It does not decide anything. Where a numbered entry and a later pass disagree,
the disagreement is RECORDED as a contradiction, not resolved by preference.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = ["parse_register", "build_index", "register_path", "main"]

#: Status markers in priority order. Every pattern is vocabulary the register
#: already uses; none is introduced here.
_MARKERS = [
    ("CLOSED", re.compile(r"✅\s*\*{0,2}CLOSED", re.I)),
    ("WITHDRAWN", re.compile(r"\bWITHDRAWN\b|\bRETRACTED\b", re.I)),
    ("FALSIFIED", re.compile(r"\bFALSIFIED\b|\bREFUTED\b", re.I)),
    ("RETIRED", re.compile(r"\bRETIRED\b|\bSUPERSEDED\b", re.I)),
    ("USER_GATED", re.compile(r"USER-GATED", re.I)),
    ("AUTHOR_RULING", re.compile(
        r"OPEN RULING|Decision needed|needs a ruling|needs a decision"
        r"|is a physics ruling|Action for the author", re.I)),
    ("BLOCKED", re.compile(r"\bBLOCKER\b|BLOCKED_ON|CONDITIONAL_ON", re.I)),
    ("UNDETERMINED", re.compile(r"\bUNDETERMINED\b", re.I)),
    ("STRUCTURAL", re.compile(r"STRUCTURAL_CHALLENGED|\bSTRUCTURAL\b", re.I)),
    ("UNBOUNDED", re.compile(r"\bUNBOUNDED\b", re.I)),
    ("RESOLVED", re.compile(r"\bRESOLVED\b|\bDISSOLVED\b", re.I)),
    ("OPEN", re.compile(r"Still open|Open problem|\bOPEN\b", re.I)),
]

_ENTRY_RE = re.compile(r"^###\s+(\d+\.\d+[a-z]?)\s+(.*)$")
_PASS_RE = re.compile(r"^#{1,2}\s+(20\d\d-\d\d-\d\d)(.*)$")
_TIER_RE = re.compile(r"^##\s+Tier\s+(\d)")

#: A status the numbered entry reads as settled.
_SETTLED = frozenset({"CLOSED", "RESOLVED"})
#: A status a later pass reads as undone.
_UNDONE = frozenset({"WITHDRAWN", "FALSIFIED", "RETIRED"})


def _classify(text: str) -> List[str]:
    """Every status marker present, in priority order. Never invents one."""
    return [name for name, rx in _MARKERS if rx.search(text)]


def _paragraphs_mentioning(body: str, entry_id: str) -> List[str]:
    """Paragraphs of ``body`` that reference ``entry_id`` as an issue number.

    Scoped to the paragraph, so a status word three screens away is not
    attributed to this entry. That scoping is the whole reason this is not a
    bare substring count.
    """
    eid = re.escape(entry_id)
    pattern = re.compile(
        r"(?:§|\bsee\s+|\bcloses?\s+|\bin\s+|\()" + eid + r"\b"
        r"|^" + eid + r"\b", re.M)
    return [p for p in re.split(r"\n\s*\n", body) if pattern.search(p)]


# A keyword-overlap heuristic was tried here to guess the missing link between
# numbered entries and the passes that amend them. It matched 6-9 of the 25
# passes for EVERY entry, so it carried no information at all -- a signal that
# fires on everything is the same defect as a check that cannot fail, and
# shipping it as a "lead to check" would have dressed noise as evidence. It is
# removed rather than tuned. The honest report is the structural finding: the
# link does not exist in machine-readable form.


def parse_register(text: str) -> Dict[str, Any]:
    """Split the register into numbered entries and dated passes."""
    lines = text.splitlines()
    entries: List[Dict[str, Any]] = []
    passes: List[Dict[str, Any]] = []

    tier: Optional[int] = None
    cur_entry: Optional[Dict[str, Any]] = None
    cur_pass: Optional[Dict[str, Any]] = None
    in_pass_log = False

    for i, line in enumerate(lines):
        m_tier = _TIER_RE.match(line)
        if m_tier and not in_pass_log:
            tier = int(m_tier.group(1))

        m_pass = _PASS_RE.match(line)
        if m_pass:
            in_pass_log = True
            cur_entry = None
            cur_pass = {
                "date": m_pass.group(1),
                "title": m_pass.group(2).strip(" —-"),
                "line": i + 1,
                "body": [],
            }
            passes.append(cur_pass)
            continue

        if not in_pass_log:
            m_entry = _ENTRY_RE.match(line)
            if m_entry:
                cur_entry = {
                    "id": m_entry.group(1),
                    "tier": tier,
                    "heading": m_entry.group(2).strip(),
                    "line": i + 1,
                    "body": [],
                }
                entries.append(cur_entry)
                continue
            if cur_entry is not None:
                cur_entry["body"].append(line)
        elif cur_pass is not None:
            cur_pass["body"].append(line)

    for e in entries:
        e["body"] = "\n".join(e["body"]).strip()
    for p in passes:
        p["body"] = "\n".join(p["body"]).strip()
    return {"entries": entries, "passes": passes}


def build_index(text: str) -> Dict[str, Any]:
    """One row per numbered entry, with the pass log as the later authority."""
    parsed = parse_register(text)
    rows: List[Dict[str, Any]] = []

    for entry in parsed["entries"]:
        # The heading is the entry's own declared status and outranks its body:
        # 1.11's heading reads RESOLVED while its body mentions a retired kill
        # condition, and body-first classification reported it as RETIRED.
        from_heading = _classify(entry["heading"])
        from_body = _classify(entry["body"])
        own = from_heading or from_body

        touches: List[Dict[str, Any]] = []
        for p in parsed["passes"]:
            paras = _paragraphs_mentioning(p["body"], entry["id"])
            if not paras:
                continue
            touches.append({
                "date": p["date"],
                "title": p["title"],
                "line": p["line"],
                "markers": _classify("\n\n".join(paras)),
            })

        later = touches[-1] if touches else None
        contradiction = None
        if later:
            own_set, late_set = set(own), set(later["markers"])
            if _SETTLED & own_set and _UNDONE & late_set:
                contradiction = (
                    "entry reads %s; the %s pass that touches it reads %s"
                    % (sorted(_SETTLED & own_set), later["date"],
                       sorted(_UNDONE & late_set)))
            elif _UNDONE & own_set and _SETTLED & late_set:
                contradiction = (
                    "entry reads %s; the %s pass that touches it reads %s"
                    % (sorted(_UNDONE & own_set), later["date"],
                       sorted(_SETTLED & late_set)))

        rows.append({
            "id": entry["id"],
            "tier": entry["tier"],
            "heading": entry["heading"],
            "line": entry["line"],
            "status": own[0] if own else "UNLABELLED",
            "status_source": "heading" if from_heading else (
                "body" if from_body else "none"),
            "all_markers_in_entry": own,
            "n_passes_citing_by_id": len(touches),
            "last_cited": later["date"] if later else None,
            "last_cited_markers": later["markers"] if later else [],
            "contradiction": contradiction,
        })

    rows.sort(key=lambda r: (r["tier"] or 99, r["id"]))

    counts: Dict[str, int] = {}
    for row in rows:
        key = row["status"]
        counts[key] = counts.get(key, 0) + 1

    never_cited = [r["id"] for r in rows if r["n_passes_citing_by_id"] == 0]

    return {
        "_schema": 1,
        "_note": (
            "Derived from docs/OUTSTANDING_ISSUES.md. The pass log is the "
            "later authority; where a numbered entry disagrees with a pass "
            "that cites it, the disagreement is recorded in `contradiction`, "
            "never resolved here. Every status word is one the register "
            "itself uses."
        ),
        "_the_structural_finding": (
            "The register's two halves are joined by nothing a machine can "
            "check. Across %d passes there are only %d id-citations of "
            "numbered entries, so %d of %d entries are never cited by number "
            "at all. Amendment happens by topic, in prose. That is exactly how "
            "a numbered entry goes stale while a later pass has already moved "
            "it. A keyword-overlap heuristic was tried as a substitute link "
            "and removed: it matched 6-9 of the 25 passes for EVERY entry, so "
            "it carried no information. Restoring the link means citing entry "
            "ids in the passes, not guessing."
            % (len(parsed["passes"]),
               sum(r["n_passes_citing_by_id"] for r in rows),
               len(never_cited), len(rows))
        ),
        "n_entries": len(rows),
        "n_passes": len(parsed["passes"]),
        "n_id_citations": sum(r["n_passes_citing_by_id"] for r in rows),
        "n_entries_never_cited_by_id": len(never_cited),
        "entries_never_cited_by_id": never_cited,
        "n_contradictions": sum(1 for r in rows if r["contradiction"]),
        "status_counts": dict(sorted(counts.items())),
        "passes": [
            {"date": p["date"], "title": p["title"], "line": p["line"]}
            for p in parsed["passes"]
        ],
        "entries": rows,
    }


def register_path() -> Path:
    """The register, in the build target (the PM repo)."""
    from metaphysica.generators._common import out_dir

    return out_dir() / "docs" / "OUTSTANDING_ISSUES.md"


def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Index the issues register.")
    ap.add_argument("--register", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    reg = args.register or register_path()
    if not reg.is_file():
        print("  issues_index: %s not found - skipping" % reg)
        return 0

    index = build_index(reg.read_text(encoding="utf-8"))
    out = args.out or (reg.parent / "issues_index.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("  issues_index: %d entries, %d passes, %d contradictions -> %s"
          % (index["n_entries"], index["n_passes"],
             index["n_contradictions"], out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
