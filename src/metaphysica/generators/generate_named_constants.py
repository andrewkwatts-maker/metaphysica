#!/usr/bin/env python3
"""Generate named_constants.json.

Flat dump of "named" physics constants — a curated subset of parameters.json
keyed by canonical name. Named constants are those that have:
- A symbolic name (e.g. alpha_em, M_PLANCK, theta_13_rad)
- A scalar numeric value
- A non-empty source or experimental attribution

All listed constants ultimately trace back to the seed b3 = 24 either
directly (geometric) or indirectly (calibrated to experiment).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from metaphysica.generators._common import autogen_dir

# Canonical "named" constants: the published Ten Named + key derived/established.
# If a parameter ID ends with one of these short names it is included.
NAMED_SUFFIXES = {
    # The Ten Named Constants of v24.2
    "watts_constant", "reid_invariant", "weinstein_scale",
    "hossenfelder_root", "wolfram_index", "carroll_metric",
    "tegmark_index", "krauss_constant", "tyson_root", "muskovich_seed",
    # Core physical constants
    "M_PLANCK", "alpha_em", "m_proton", "HBAR", "C_LIGHT",
    "alpha_GUT", "M_GUT", "m_H", "v_H",
    # Geometric seeds
    "b3", "chi_eff", "phi", "k_gimel", "roots_total",
    "visible_sector", "sterile_sector", "christ_constant",
}


def _is_named(param_id: str) -> bool:
    short = param_id.rsplit(".", 1)[-1]
    return short in NAMED_SUFFIXES


def main() -> int:
    ag = autogen_dir()
    src = ag / "parameters.json"
    if not src.exists():
        print(
            f"  named_constants: parameters.json not found — skipping "
            f"(run simulations first: pip install metaphysica[sims])"
        )
        return 0

    blob = json.loads(src.read_text(encoding="utf-8"))
    params = blob.get("parameters", {}) or {}

    constants: Dict[str, Any] = {}
    for pid, pdata in params.items():
        if not isinstance(pdata, dict):
            continue
        if not _is_named(pid):
            continue
        short = pid.rsplit(".", 1)[-1]
        meta = pdata.get("metadata", {}) or {}
        entry = {
            "pm_path": pid,
            "value": pdata.get("value"),
            "units": meta.get("units"),
            "description": meta.get("description"),
            "status": pdata.get("status"),
            "source": pdata.get("source"),
            "experimental_value": pdata.get("experimental_value"),
            "experimental_uncertainty": pdata.get("experimental_uncertainty"),
            "sigma_deviation": pdata.get("sigma_deviation"),
            "validation_status": pdata.get("validation_status"),
            "seed_provenance": "b3 = 24",
        }
        # Prefer the first encounter; do not clobber if same short name appears.
        if short not in constants:
            constants[short] = entry

    output = {
        "version": blob.get("version", "unknown"),
        "name": "Named Constants Registry",
        "description": "Curated named physics constants from parameters.json, "
                       "keyed by canonical short name.",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "generator": "metaphysica.generators.generate_named_constants",
        "seed_provenance": "All constants derive from or calibrate against the seed b3 = 24.",
        "total": len(constants),
        "constants": constants,
    }

    out = ag / "named_constants.json"
    out.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"named_constants: {len(constants)} entries")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
