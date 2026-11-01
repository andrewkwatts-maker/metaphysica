"""One source for the site's headline statistics.

Reads ``statistical_rigor_report.json`` and ``GATES_CERTIFICATES.json`` and
returns chi2, rows, dof, p, verdict and the gate tally. Every page binding
(index, certificates, sections, parameters, falsification, appendix F) reads
the values this emits; none may carry a fallback literal.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from metaphysica.generators.generate_improvement_scorecard import (
    AXIOM, _bucket_certificate)

#: Shown when an artifact lacks a value; the build log carries the reason.
NOT_AVAILABLE = "not available in this build"
NOT_APPLICABLE_STATUS = "NOT_APPLICABLE"


def _read(path: Path) -> Dict[str, Any]:
    """Load a JSON artifact, failing early with the missing path."""
    if not path.exists():
        raise FileNotFoundError(f"headline_stats: missing artifact {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def tally_gates(certs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Count gates by evaluated bucket, skipping gates marked not applicable."""
    ids: Dict[str, List[str]] = {"locked": [], "open": [], "axiom": [], "other": []}
    n_decl = n_pass = n_fail = 0
    for cert in certs:
        ev = str(cert.get("evaluation_status") or "").upper()
        if ev == NOT_APPLICABLE_STATUS:
            continue
        ids[_bucket_certificate(cert)].append(str(cert.get("gate_id")))
        n_pass += ev == "COMPUTED_PASS"
        n_fail += ev == "COMPUTED_FAIL"
        n_decl += not ev.startswith("COMPUTED")
    total = sum(len(v) for v in ids.values())
    return {
        "total": total, "locked": len(ids["locked"]), "open": len(ids["open"]),
        "axiom": len(ids["axiom"]), "testable": total - len(ids["axiom"]),
        "locked_ids": ids["locked"], "open_ids": ids["open"],
        "declarative": n_decl, "computed_pass": n_pass, "computed_fail": n_fail,
    }


def _fit(rigor: Dict[str, Any]) -> Dict[str, Any]:
    """Pull the global-fit numbers from the rigor report, None when absent."""
    rows = (rigor.get("chi_squared_from_rows") or {}).get("all_scoring_rows") or {}
    edof = rigor.get("edof_analysis") or {}
    return {
        "chi_squared": rows.get("chi_squared"), "rows": rows.get("n"),
        "dof": edof.get("effective_dof"), "p_value": edof.get("p_value"),
        "verdict": edof.get("status") or (rigor.get("summary") or {}).get("status"),
    }


def _formulas_ok(certs_doc: Dict[str, Any]) -> Optional[int]:
    """Formulas-checked-OK count, only if a build artifact records it."""
    value = (certs_doc.get("summary") or {}).get("formulas_checked_ok")
    return int(value) if value is not None else None


def headline_statistics(rigor_path: Path, certs_path: Path) -> Dict[str, Any]:
    """Return the single dict every headline binding reads."""
    rigor, certs_doc = _read(Path(rigor_path)), _read(Path(certs_path))
    gates = tally_gates(certs_doc.get("certificates") or [])
    fit = _fit(rigor)
    ok = _formulas_ok(certs_doc)
    out = {**fit, **{f"gates_{k}": v for k, v in gates.items()
                     if not k.endswith("_ids")},
           "gates_locked_ids": gates["locked_ids"],
           "gates_open_ids": gates["open_ids"],
           "formulas_checked_ok": ok}
    out["missing"] = sorted(k for k, v in out.items() if v is None)
    return out


def display_value(value: Any) -> Any:
    """Return the value, or the standard 'not available' text when None."""
    return NOT_AVAILABLE if value is None else value


def find_headline() -> Optional[Dict[str, Any]]:
    """Headline dict from the newest artifact dir holding both sources, or None."""
    from metaphysica.simulations.core.parameter_artifact import candidate_paths
    pairs = [(p.parent / "statistical_rigor_report.json",
              p.parent / "GATES_CERTIFICATES.json") for p in candidate_paths()]
    found = [(r, c) for r, c in pairs if r.is_file() and c.is_file()]
    if not found:
        return None
    rigor, certs = max(found, key=lambda rc: rc[0].stat().st_mtime)
    return headline_statistics(rigor, certs)


def fmt(value: Any, spec: str = "{}") -> str:
    """Format a headline value, or the standard unavailable text for None."""
    return NOT_AVAILABLE if value is None else spec.format(value)
