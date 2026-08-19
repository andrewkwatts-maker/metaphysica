#!/usr/bin/env python3
"""Generate terminology_audit.json.

Audits consistency of physics terminology across formulas.json, sections.json,
and parameters.json. Flags entries that mention deprecated or inconsistent
notation for the M^{26}(24,2) dimensional architecture (e.g. legacy
``26D(26,1)`` references, old 26-spatial signatures, etc.).

Every flagged item ultimately traces back to the single seed b₃ = 24:
the 26D bulk is 24 (= b₃) spatial dimensions + 2 timelike directions,
one per 13D(12,1) shadow. Terminology drift = drift from that one seed.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from metaphysica.generators._common import autogen_dir

CANONICAL = {
    "manifold": "M^{26}(24,2)",
    "signature": "(24,2)",
    "decomposition": "24 (G2 core, = b3) + 2 (times, one per 13D shadow)",
    "seed": "b3 = 24",
}

# Context markers that exempt a string from the deprecated-pattern scan:
# self-labelled history, and the legitimate 27-dimensional exceptional
# Jordan algebra (dim J3(O) = 27 is real mathematics, not stale notation).
_CONTEXT_EXEMPT = (
    "superseded", "formerly", "historical", "retired", "legacy",
    "provenance", "two-time ruling", "jordan", "j3(o)", "j₃",
    "exceptional", "vintage", "attribution",
)

# Patterns that indicate stale / inconsistent notation.
DEPRECATED_PATTERNS = [
    (r"\b26D\(26,1\)\b", "Use M^{26}(24,2)"),
    (r"\b25D\b", "Two-time ruling: the bulk is 26D = 24 space + 2 times"),
    (r"\b26D\(25,1\)\b", "Pre-v24 notation; use M^{26}(24,2)"),
    (r"\b27D\b", "Two-time ruling: the bulk is 26D (24,2), not 27D"),
    (r"\bunified time\b", "Two-time ruling: one timelike direction per shadow"),
    (r"Consciousness Field", "Use S_EIS (Euclidean Information Sector)"),
    (r"\bn_gen\s*=\s*chi_eff\s*/\s*\(4\*b3\)", "Verify chi_eff=144, b3=24 -> 3"),
]

CANONICAL_KEYWORDS = [
    "M^{26}",
    "(24,2)",
    "24 + 2",
    "b3 = 24",
    "G2 holonomy",
    "twisted connected sum",
    "(12,1)",
    "Sp(2,R)",
]


def _scan_strings(obj: Any, path: str = "") -> List[Dict[str, Any]]:
    flags: List[Dict[str, Any]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            flags.extend(_scan_strings(v, f"{path}['{k}']"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            flags.extend(_scan_strings(v, f"{path}[{i}]"))
    elif isinstance(obj, str):
        # Text that labels itself as history, or that legitimately talks
        # about the 27-dimensional exceptional Jordan algebra, is not
        # terminology drift. Without this the 27D rule flags dim J3(O) = 27
        # and every provenance note the two-time migration deliberately left
        # in place.
        low = obj.lower()
        if any(k in low for k in _CONTEXT_EXEMPT):
            return flags
        for pat, suggestion in DEPRECATED_PATTERNS:
            if re.search(pat, obj):
                snippet = obj[:200] + ("..." if len(obj) > 200 else "")
                flags.append({
                    "path": path,
                    "pattern": pat,
                    "suggestion": suggestion,
                    "snippet": snippet,
                })
    return flags


def _scan_file(p: Path) -> List[Dict[str, Any]]:
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    return _scan_strings(data, f"{p.name}")


def main() -> int:
    ag = autogen_dir()
    inputs = ["formulas.json", "sections.json", "parameters.json", "theory_output.json"]

    all_flags: List[Dict[str, Any]] = []
    files_scanned: List[str] = []
    for name in inputs:
        p = ag / name
        if p.exists():
            files_scanned.append(name)
            for f in _scan_file(p):
                f["file"] = name
                all_flags.append(f)

    # Count canonical keyword presence as a positive indicator.
    keyword_hits: Dict[str, int] = {kw: 0 for kw in CANONICAL_KEYWORDS}
    for name in files_scanned:
        try:
            text = (ag / name).read_text(encoding="utf-8")
        except Exception:
            continue
        for kw in CANONICAL_KEYWORDS:
            keyword_hits[kw] += text.count(kw)

    status = "REVISION REQUIRED" if all_flags else "CONSISTENT"
    report = {
        "framework": "Principia Metaphysica",
        "audit_type": "26D Terminology Compliance",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total_files_scanned": len(files_scanned),
        "files_scanned": files_scanned,
        "total_flags": len(all_flags),
        "status": status,
        "canonical_terminology": CANONICAL,
        "deprecated_patterns": [
            {"pattern": p, "suggestion": s} for p, s in DEPRECATED_PATTERNS
        ],
        "canonical_keyword_hits": keyword_hits,
        "flagged_entries": all_flags,
        "seed_provenance": "All terminology terms trace back to seed b3 = 24 (G2 manifold third Betti number).",
    }

    out = ag / "terminology_audit.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"terminology_audit: {len(all_flags)} flag(s), status={status}")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
