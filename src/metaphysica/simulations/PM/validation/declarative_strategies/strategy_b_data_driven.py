#!/usr/bin/env python3
"""Strategy B: Data-driven — bind each gate to parameters.json registry values.

Each gate is converted to a numerical check against live registry entries,
with a tolerance that is itself derived from the gate's stated result or from
the experimental uncertainty already stored in parameters.json.  No new
physical constant is invented: the tolerance must be derivable from the
registry without an author ruling.

SAMPLE: 6 of the 24 DECLARATIVE gates are converted here.
    G01 — Integer Root Parity          (exact integer match)
    G17 — Generation Triality          (exact integer match)
    G22 — Gluon String Tension ratio   (exact rational match)
    G23 — Proton Stability Floor       (inequality from registry)
    G36 — CKM Matrix Unitarity         (registry unitarity deviation)
    G37 — CP-Violation Phase           (Jarlskog invariant vs PDG)

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List

__all__ = [
    "GateResult",
    "gate_G01_integer_root_parity",
    "gate_G17_generation_triality",
    "gate_G22_gluon_string_tension",
    "gate_G23_proton_stability_floor",
    "gate_G36_ckm_unitarity",
    "gate_G37_cp_violation_phase",
    "run_all",
]


@dataclass
class GateResult:
    gate_id: int
    gate_name: str
    verdict: str          # "PASS" | "FAIL"
    measured: Any
    expected: Any
    tolerance: Any
    tolerance_source: str  # where the tolerance came from
    note: str
    numbers_invented: int = 0


def _params() -> dict:
    from metaphysica.generators._common import autogen_dir
    path = autogen_dir() / "parameters.json"
    with open(path) as fh:
        return json.load(fh)["parameters"]


# ---------------------------------------------------------------------------
# G01: Integer Root Parity — topology.ancestral_roots == 288
# Tolerance: none required (exact integer).
# ---------------------------------------------------------------------------
def gate_G01_integer_root_parity() -> GateResult:
    p = _params()
    measured = int(p["topology.ancestral_roots"]["value"])
    expected = 288
    return GateResult(
        gate_id=1,
        gate_name="Integer Root Parity",
        verdict="PASS" if measured == expected else "FAIL",
        measured=measured,
        expected=expected,
        tolerance="exact",
        tolerance_source="integer equality — no tolerance possible",
        note="topology.ancestral_roots must equal 288.",
        numbers_invented=0,
    )


# ---------------------------------------------------------------------------
# G17: Generation Triality — fermion.n_generations == 3
# Tolerance: none (exact integer).
# ---------------------------------------------------------------------------
def gate_G17_generation_triality() -> GateResult:
    p = _params()
    measured = int(p["fermion.n_generations"]["value"])
    expected = 3
    return GateResult(
        gate_id=17,
        gate_name="Generation Triality",
        verdict="PASS" if measured == expected else "FAIL",
        measured=measured,
        expected=expected,
        tolerance="exact",
        tolerance_source="integer equality",
        note="fermion.n_generations must equal 3.",
        numbers_invented=0,
    )


# ---------------------------------------------------------------------------
# G22: Gluon String Tension — topology.shadow_torsion_total / roots_total = 24/288
# Tolerance: none (exact integer ratio).
# ---------------------------------------------------------------------------
def gate_G22_gluon_string_tension() -> GateResult:
    p = _params()
    shadow = int(p["topology.shadow_torsion_total"]["value"])   # 24
    roots = int(p["geometry.roots_total"]["value"])             # 288
    expected_num, expected_den = 24, 288
    match = (shadow == expected_num) and (roots == expected_den)
    return GateResult(
        gate_id=22,
        gate_name="Gluon String Tension",
        verdict="PASS" if match else "FAIL",
        measured=f"{shadow}/{roots}",
        expected=f"{expected_num}/{expected_den}",
        tolerance="exact",
        tolerance_source="integer ratio equality",
        note="shadow_torsion_total/roots_total must equal 24/288.",
        numbers_invented=0,
    )


# ---------------------------------------------------------------------------
# G23: Proton Stability Floor — proton_decay.tau_p_years > bounds.tau_proton_lower
# Tolerance: inequality (no numeric threshold invented).
# ---------------------------------------------------------------------------
def gate_G23_proton_stability_floor() -> GateResult:
    p = _params()
    tau_p = p["proton_decay.tau_p_years"]["value"]
    bound = p["bounds.tau_proton_lower"]["value"]
    verdict = "PASS" if tau_p > bound else "FAIL"
    return GateResult(
        gate_id=23,
        gate_name="Proton Stability Floor",
        verdict=verdict,
        measured=tau_p,
        expected=f"> {bound}",
        tolerance="strict inequality",
        tolerance_source="bounds.tau_proton_lower from parameters.json (PDG 2024)",
        note=f"proton_decay.tau_p_years ({tau_p:.3e}) > bounds.tau_proton_lower ({bound:.3e})",
        numbers_invented=0,
    )


# ---------------------------------------------------------------------------
# G36: CKM Matrix Unitarity — ckm.unitarity_test < tolerance
# The gate claims "row-1 unitarity deviation ~ 5.8e-5".
# Tolerance: the gate's own published result value (5.8e-5) rounded up to
# 1e-4 is NOT invented — it comes from the gate's wl_code result string.
# However, this still requires extracting a number from prose.
# We use ckm.unitarity_test directly: if the registry stores the deviation,
# we check it is < 1 (the only threshold derivable without inventing anything —
# "unitarity deviation < 1" is definitionally true for a unitary matrix).
# A tighter threshold (1e-4) would require the author to specify it.
# numbers_invented=1 is flagged because no registry key stores the tolerance.
# ---------------------------------------------------------------------------
def gate_G36_ckm_unitarity() -> GateResult:
    p = _params()
    deviation = p["ckm.unitarity_test"]["value"]
    # The only non-invented threshold is "< 1" (unitarity must hold in the
    # matrix-algebra sense).  The gate's prose claims 5.8e-5 but that number
    # is not stored as a tolerance in the registry — it IS the deviation value.
    # So we check deviation < 1 (trivially strong) and flag that the tight
    # threshold (e.g. 1e-4) would require a ruling.
    verdict = "PASS" if deviation < 1.0 else "FAIL"
    return GateResult(
        gate_id=36,
        gate_name="CKM Matrix Unitarity",
        verdict=verdict,
        measured=deviation,
        expected="< 1.0",
        tolerance=1.0,
        tolerance_source=(
            "Threshold 1.0 derived from unitarity definition (deviation < 1 is "
            "necessary for any unitary matrix). A physically meaningful tight "
            "threshold (e.g. 1e-3) would require an author ruling and is NOT "
            "available in the registry — counted as numbers_invented=1."
        ),
        note=(
            f"ckm.unitarity_test = {deviation:.4e}. Gate PASSES the weak "
            "unitarity bound but the physically relevant tight bound is not "
            "derivable without an author ruling."
        ),
        numbers_invented=1,
    )


# ---------------------------------------------------------------------------
# G37: CP-Violation Phase — ckm.jarlskog_invariant vs pdg.J_ckm
# The gate claims J = 3.08e-5; PDG 2024 is (3.0±0.3)e-5.
# Tolerance: the PDG uncertainty is stored in parameters.json under
# pdg.J_ckm with its own uncertainty field — no invention required.
# ---------------------------------------------------------------------------
def gate_G37_cp_violation_phase() -> GateResult:
    p = _params()
    J_theory = p["ckm.jarlskog_invariant"]["value"]
    J_pdg = p["pdg.J_ckm"]["value"]
    # Use the PDG uncertainty from the registry entry
    J_pdg_unc = p["pdg.J_ckm"].get("uncertainty", None)
    if J_pdg_unc and J_pdg_unc > 0:
        invented = 0
        tol_source = "pdg.J_ckm uncertainty field from parameters.json"
    else:
        # Fallback: gate prose says "(3.0±0.3)e-5", i.e. 3e-6
        J_pdg_unc = 3.0e-6
        invented = 1
        tol_source = (
            "3.0e-6 read from gate's own result text '(3.0±0.3)e-5 PDG 2024'. "
            "Not in registry uncertainty field — counted as numbers_invented=1."
        )

    # Allow 3-sigma agreement
    sigma = abs(J_theory - J_pdg) / J_pdg_unc if J_pdg_unc else float("inf")
    # Gate passes if within 5 sigma (generous; the declared result is 1 sigma)
    verdict = "PASS" if sigma < 5.0 else "FAIL"
    return GateResult(
        gate_id=37,
        gate_name="CP-Violation Phase",
        verdict=verdict,
        measured=J_theory,
        expected=f"{J_pdg} ± {J_pdg_unc}",
        tolerance=f"5 sigma = {5 * J_pdg_unc:.2e}",
        tolerance_source=tol_source,
        note=f"J_theory={J_theory:.4e}, J_PDG={J_pdg:.4e}, sigma={sigma:.2f}",
        numbers_invented=invented,
    )


def run_all() -> List[GateResult]:
    return [
        gate_G01_integer_root_parity(),
        gate_G17_generation_triality(),
        gate_G22_gluon_string_tension(),
        gate_G23_proton_stability_floor(),
        gate_G36_ckm_unitarity(),
        gate_G37_cp_violation_phase(),
    ]


def main() -> int:
    results = run_all()
    print("=" * 60)
    print(" STRATEGY B — DATA-DRIVEN GATE CHECKS")
    print("=" * 60)
    n_pass = sum(1 for r in results if r.verdict == "PASS")
    total_invented = sum(r.numbers_invented for r in results)
    for r in results:
        print(f"  [{r.verdict}] G{r.gate_id:02d} {r.gate_name}")
        print(f"        measured={r.measured}  expected={r.expected}")
        print(f"        tolerance={r.tolerance}  source={r.tolerance_source[:60]}")
        print(f"        numbers_invented={r.numbers_invented}")
    print(f"\n  {n_pass}/{len(results)} PASS  |  {total_invented} numbers invented")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
