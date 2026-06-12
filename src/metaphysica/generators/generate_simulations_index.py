#!/usr/bin/env python3
"""Generate simulations-index.json.

Top-level index of all simulation modules under
``metaphysica/simulations/`` along with their gate / formula contributions.

Cross-references:
- ``GATES_CERTIFICATES.json`` for gate -> source-simulation mapping
- ``parameters.json`` for parameter -> source_simulation mapping
- ``formulas.json`` for formula -> source simulation (best-effort)

All listed simulations contribute to derivations anchored on the
seed b3 = 24.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from metaphysica.generators._common import autogen_dir

# Where the simulation package lives inside the installed lib.
_HERE = Path(__file__).resolve().parent
SIM_ROOT = _HERE.parent / "simulations"


def _extract_docstring(file_path: Path) -> Dict[str, Optional[str]]:
    info: Dict[str, Optional[str]] = {"description": None, "title": None, "status": None}
    try:
        head = file_path.read_text(encoding="utf-8", errors="ignore")[:2500]
    except Exception:
        return info
    m = re.search(r'"""(.+?)"""', head, re.DOTALL) or re.search(r"'''(.+?)'''", head, re.DOTALL)
    if not m:
        return info
    doc = m.group(1).strip()
    lines = [ln.strip() for ln in doc.split("\n") if ln.strip()]
    for ln in lines:
        if ln.startswith("=") or ln.startswith("-"):
            continue
        if ln.lower().startswith(("copyright", "version")):
            continue
        if " - " in ln and ln.startswith("PRINCIPIA"):
            info["title"] = ln.split(" - ", 1)[1].strip()
            continue
        if info["description"] is None and len(ln) > 15:
            info["description"] = ln
            break
    doc_upper = doc.upper()
    for tag in ("CORE", "PREDICTION", "VALIDATED", "GEOMETRIC"):
        if f"STATUS: {tag}" in doc_upper:
            info["status"] = tag
            break
    return info


def _category_from_path(rel: Path) -> str:
    parts = [p.lower() for p in rel.parts]
    if "pm" in parts:
        i = parts.index("pm")
        if i + 1 < len(parts):
            sub = parts[i + 1]
            return f"PM/{sub}"
    if parts:
        return parts[0]
    return "uncategorized"


def _scan_sims() -> List[Dict[str, Any]]:
    if not SIM_ROOT.exists():
        return []
    out: List[Dict[str, Any]] = []
    for py in SIM_ROOT.rglob("*.py"):
        if py.name.startswith("__"):
            continue
        rel = py.relative_to(SIM_ROOT)
        info = _extract_docstring(py)
        out.append({
            "file": py.name,
            "path": f"simulations/{rel.as_posix()}",
            "category": _category_from_path(rel),
            "title": info["title"],
            "description": info["description"],
            "status": info["status"],
        })
    return out


def _attribution_from_certificates(certs_blob: Dict[str, Any]) -> Dict[str, List[str]]:
    """Map simulation path -> list of gate IDs it contributes to."""
    attribution: Dict[str, List[str]] = {}
    for c in certs_blob.get("certificates", []) or []:
        gate_id = c.get("gate_id") or c.get("id") or ""
        src = c.get("source_simulation") or c.get("source") or ""
        if src and gate_id:
            attribution.setdefault(str(src), []).append(str(gate_id))
    return attribution


def _attribution_from_params(params_blob: Dict[str, Any]) -> Dict[str, List[str]]:
    """Map simulation source -> list of parameters it produces."""
    attribution: Dict[str, List[str]] = {}
    for pid, pdata in (params_blob.get("parameters") or {}).items():
        if not isinstance(pdata, dict):
            continue
        src = pdata.get("source_simulation") or pdata.get("source") or ""
        if src:
            attribution.setdefault(str(src), []).append(pid)
    return attribution


def main() -> int:
    ag = autogen_dir()
    sims = _scan_sims()

    certs_blob: Dict[str, Any] = {}
    params_blob: Dict[str, Any] = {}
    try:
        certs_blob = json.loads((ag / "GATES_CERTIFICATES.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    try:
        params_blob = json.loads((ag / "parameters.json").read_text(encoding="utf-8"))
    except Exception:
        pass

    gate_attr = _attribution_from_certificates(certs_blob)
    param_attr = _attribution_from_params(params_blob)

    # Bucket by category
    by_category: Dict[str, List[Dict[str, Any]]] = {}
    for s in sims:
        # Heuristic: try matching by filename stem or path segment
        stem = Path(s["path"]).stem
        s["gates_contributed"] = sorted({
            g for key, gs in gate_attr.items() if stem in key for g in gs
        })
        s["parameters_contributed"] = sorted({
            p for key, ps in param_attr.items() if stem in key for p in ps
        })
        by_category.setdefault(s["category"], []).append(s)

    index = {
        "version": (params_blob.get("version") or "unknown"),
        "name": "Simulations Index",
        "description": "Top-level index of simulation modules with gate/parameter contributions.",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "generator": "metaphysica.generators.generate_simulations_index",
        "seed_provenance": "All simulations descend from the seed b3 = 24.",
        "total_scripts": len(sims),
        "total_categories": len(by_category),
        "categories": {
            cat: {
                "title": cat,
                "count": len(items),
                "scripts": sorted(items, key=lambda x: x["file"]),
            }
            for cat, items in sorted(by_category.items())
        },
    }

    out = ag / "simulations-index.json"
    out.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"simulations-index: {len(sims)} scripts across {len(by_category)} categories")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
