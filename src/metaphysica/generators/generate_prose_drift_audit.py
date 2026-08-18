# -*- coding: utf-8 -*-
"""Prose-drift audit: superseded values must not reappear in section text.

The canonical-value rulings (core/canonical_values.py) retired specific
numbers — the thermal-time w0 = -0.853, the x4 wa = -0.8165 presented as
canonical, V_us = 0.2257, m_h = 125.10/125.25, the ricci H0 = 76.34
presented as THE prediction, sin^2 = 0.23189-as-sin2_theta_w, and so on.
Prose that hand-copies numbers is exactly how they return.

This build step scans every content string in sections.json for the
superseded numerals of each ruling and reports hits with their section
id. Report-only (exit 0), but every hit is a WARN line in the build log.
Canonical values appearing in prose are fine; superseded ones are drift.

Values are matched as standalone numerals (with tolerance for trailing
digits) so e.g. "125.10" does not fire on "125.100 kg of…" false
positives across unit boundaries — matches require a non-digit on both
sides.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from metaphysica.generators._common import autogen_dir
from metaphysica.simulations.core.canonical_values import all_canonical

# Values that are too generic to scan for (fire everywhere).
_SKIP = {"45.0", "45.2", "5.0", "0.25", "42", "196", "24", "72", "144", "27", "25"}

# Extra retired numerals not carried in the table's superseded keys
# (prose-only spellings of the same retirements).
_EXTRA = {
    "0.2257": "stale V_us (canonical 0.22500)",
    "125.10": "stale m_H (canonical 125.20)",
    "125.25": "stale m_H (canonical 125.20)",
    "3.08e-5": "stale PDG J for comparisons (dataset 3.12e-5)",
    "33.44": "stale theta12 (canonical 33.59)",
    "8.33": "stale theta13 section text (canonical 8.65)",
    "0.23189": "geometric sin2 presented as sin2_theta_w (scheme ruling)",
}

# Two-time migration tokens (2026-08-19 bulk ruling): the 27D sampler-pair
# formulation is superseded — these string tokens flag any prose still on
# the old bulk. Matched as substrings (not numerals). "27" alone is NEVER
# matched: dim J3(O) = 27 is a legitimate Jordan-algebra 27.
_MIGRATION_TOKENS = {
    "27D": "superseded bulk (two-time ruling: 26D (24,2))",
    "M^27": "superseded bulk notation (canonical M^26(24,2))",
    "M²⁷": "superseded bulk notation (canonical M²⁶(24,2))",
    "(24,1,2)": "superseded sampler-pair signature (canonical (24,2))",
    "d²⁷X": "superseded measure (canonical d²⁶X)",
    "d^27": "superseded measure (canonical d^26)",
    "Cl(24,1)": "superseded spinor construction (canonical: Weyl of Cl(24,2))",
    "Cl(26,1)": "wrong Clifford algebra (canonical: Weyl of Cl(24,2))",
    "27-dimensional spacetime": "superseded bulk (26-dimensional (24,2))",
    "27-dimensional bulk": "superseded bulk (26-dimensional (24,2))",
    "27/10": "superseded alpha_T ratio (two-time: 26/10 = 2.6)",
}


def _superseded_index() -> Dict[str, str]:
    idx: Dict[str, str] = {}
    for symbol, entry in all_canonical().items():
        for sv, why in (entry.get("superseded") or {}).items():
            token = sv.split()[0]
            if token in _SKIP:
                continue
            try:
                float(token)
            except ValueError:
                continue
            idx[token] = f"{symbol}: {why}"
    idx.update(_EXTRA)
    return idx


def _collect_strings(node: Any, out: List[str]) -> None:
    if isinstance(node, str):
        out.append(node)
    elif isinstance(node, dict):
        for v in node.values():
            _collect_strings(v, out)
    elif isinstance(node, list):
        for v in node:
            _collect_strings(v, out)


def run_audit() -> Dict[str, Any]:
    sections_path = autogen_dir() / "sections.json"
    if not sections_path.exists():
        return {"schema_version": 1, "error": "sections.json not present", "hits": []}

    data = json.loads(sections_path.read_text(encoding="utf-8"))
    sections = data.get("sections", data)
    idx = _superseded_index()

    patterns = {
        token: re.compile(r"(?<![\d.])" + re.escape(token) + r"(?![\d])")
        for token in idx
    }
    # Migration tokens are plain substrings (notation, not numerals);
    # suppressed when the surrounding text already annotates the
    # supersession (same convention as the 0.2257 racetrack rule).
    for token, why in _MIGRATION_TOKENS.items():
        idx[token] = why
        patterns[token] = re.compile(re.escape(token))

    # Context-conditional tokens (encode the naming rulings precisely):
    # 0.57 is LEGITIMATE as alpha_sample — flag only when presented as
    # alpha_leak; 0.2257 is legitimate as the labelled racetrack variant —
    # flag only when unannotated (no canonical cross-reference nearby).
    # Prose that already labels a stale/variant value is not drift: the
    # auditor hunts UNlabelled quotes. Generic label vocabulary first, then
    # per-token context keys.
    _LABEL_KEYS = ("superseded", "retired", "falsified", "canonical",
                   "variant", "calibrated", "historical", "formerly")
    _TOKEN_KEYS = {
        "0.2257": ("0.22500", "e^{-3/2}", "0.22313"),
        "0.57": ("ansatz", "alpha_sample", "sample"),
        "8.33": ("%", "24/288", "ghost", "octonionic estimate"),
        "0.9996": ("8.3", "planck"),
        "0.967": ("0.9667",),
        "9.5941": ("nufit",),
        "76.34": ("sh0es",),
        "70.42": ("sh0es", "sterile", "combined"),
        "125.10": ("input", "pdg 2024"),
        "125.25": ("pdg 2024:",),
        "0.23189": ("0.23122", "tree-level", "scheme"),
        "-0.980": ("-23/24", "attractor"),
    }

    def _is_real_hit(token: str, context: str) -> bool:
        c = context.lower()
        if any(k in c for k in _LABEL_KEYS):
            return False
        for key in _TOKEN_KEYS.get(token, ()):
            if key.lower() in c:
                return False
        if token == "0.57":
            return "leak" in c
        if token in _MIGRATION_TOKENS:
            return not any(k in c for k in ("two-time", "sampler-pair formulation"))
        return True

    hits: List[Dict[str, Any]] = []
    for sec_id, sec in (sections.items() if isinstance(sections, dict) else enumerate(sections)):
        strings: List[str] = []
        _collect_strings(sec, strings)
        for s in strings:
            for token, rx in patterns.items():
                m = rx.search(s)
                if m:
                    start = max(0, m.start() - 60)
                    ctx = s[start:m.end() + 60].strip()
                    if not _is_real_hit(token, ctx):
                        continue
                    hits.append({
                        "section": str(sec_id),
                        "token": token,
                        "ruling": idx[token],
                        "context": ctx,
                    })

    # Deduplicate identical (section, token, context) triples
    seen = set()
    unique = []
    for h in hits:
        key = (h["section"], h["token"], h["context"][:60])
        if key not in seen:
            seen.add(key)
            unique.append(h)

    return {
        "schema_version": 1,
        "note": (
            "Prose-drift audit (S-1 guard): superseded numerals from the "
            "canonical-value rulings found in section content. Every hit "
            "is prose that must be rewritten to the canonical value or "
            "explicitly framed as a retired candidate."
        ),
        "summary": {"tokens_scanned": len(idx), "hits": len(unique)},
        "hits": unique,
    }


def main() -> int:
    report = run_audit()
    out = autogen_dir() / "prose_drift_audit.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("=" * 60)
    print("Prose-drift audit (superseded values in section text)")
    print("=" * 60)
    if "error" in report:
        print(f"  SKIPPED: {report['error']}")
        return 0
    s = report["summary"]
    print(f"  retired numerals scanned: {s['tokens_scanned']}   hits: {s['hits']}")
    for h in report["hits"][:20]:
        print(f"  WARN sec {h['section']:>6s} [{h['token']}] {h['ruling'][:48]}")
    print(f"\nReport written to: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
