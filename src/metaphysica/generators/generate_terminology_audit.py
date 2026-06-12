#!/usr/bin/env python3
"""Generate terminology_audit.json.

Audits consistency of physics terminology across formulas.json, sections.json,
and parameters.json. Flags entries that mention deprecated or inconsistent
notation for the M^{27}(24,1,2) dimensional architecture (e.g. legacy
``27D(26,1)`` references, old 26-spatial signatures, etc.).

Every flagged item ultimately traces back to the single seed b₃ = 24:
the 27-dim manifold is 24 (= b₃) bridge dimensions + 1 unified time +
2 sampler dimensions. Terminology drift = drift from that one seed.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from metaphysica.generators._common import autogen_dir

CANONICAL = {
    "manifold": "M^{27}(24,1,2)",
    "signature": "(26,1)",
    "decomposition": "24 (G2 core, = b3) + 1 (unified time T^1) + 2 (sampler S^{2,0})",
    "seed": "b3 = 24",
}

# Patterns that indicate stale / inconsistent notation.
DEPRECATED_PATTERNS = [
    (r"\b27D\(26,1\)\b", "Use M^{27}(24,1,2)"),
    (r"\b25D\b", "v23+ uses 27D = 24 + 1 + 2"),
    (r"\b26D\(25,1\)\b", "Pre-v24 notation; use M^{27}(24,1,2)"),
    (r"Consciousness Field", "Use S_EIS (Euclidean Information Sector)"),
    (r"\bn_gen\s*=\s*chi_eff\s*/\s*\(4\*b3\)", "Verify chi_eff=144, b3=24 -> 3"),
]

CANONICAL_KEYWORDS = [
    "M^{27}",
    "24+1+2",
    "b3 = 24",
    "G2 holonomy",
    "twisted connected sum",
    "S^{2,0}",
    "T^1",
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
        "audit_type": "27D Terminology Compliance",
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
