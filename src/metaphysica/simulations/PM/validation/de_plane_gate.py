#!/usr/bin/env python3
"""Dark-energy verdict in the 2D (w0, wa) plane, with correlation sensitivity.

WHY THIS EXISTS
---------------
The outstanding-issues register reports the dark-energy tension as TWO
separate headlines: w0 = -23/24 at 3.62 sigma and wa = -1/sqrt(24) at 2.98
sigma against DESI DR2. But the DR2 (w0, wa) posterior is a strongly
anti-correlated ellipse, and two 1D sigmas computed from correlated marginals
DOUBLE-COUNT a single displacement. The honest statement is one number: the
Mahalanobis distance of the framework's point in the 2D plane.

The correlation coefficient rho is not published as a scalar, so this gate
does not invent one. It scans the plausible range and reports the verdict's
sensitivity. The conclusion is rho-robust: the framework point sits at
roughly 3.2-3.4 sigma equivalent for every rho in [-0.95, -0.60], which
neither of the 1D numbers correctly conveys (uncorrelated 2D would claim
4.3 sigma; the marginals suggest 3.6 + 3.0 as if independent).

This REPLACES anchor-shopping. An earlier advertised "0.027 sigma agreement"
rested on an anchor whose attribution could not be verified; the register
demands a decision between defending that anchor and accepting the honest
headline. This gate is the honest headline, computed rather than chosen.

KILL CONDITION (stated in advance, per the falsification-first posture):
if future BAO+CMB+SNe releases tighten to w0 < -0.99 or push the 2D distance
past 5 sigma under this same scan, w0 = -23/24 is dead -- there is no knob to
turn, which is precisely what makes it worth testing.

ALSO HERE: the neutrino-mass-sum conditional. The framework's mass sums
exceed the DESI LCDM bound but sit inside the relaxed bound that applies in
w0waCDM cosmologies -- which is exactly the cosmology this framework
predicts. Both rows are reported; neither is hidden inside the other.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = [
    "PlaneVerdict",
    "framework_point",
    "chi2_at_rho",
    "sigma_equivalent",
    "scan_rho",
    "mass_sum_rows",
    "write_report",
    "main",
]

# ── DESI DR2 anchors (inline with source attribution, per SSOT policy) ──────
#: w0waCDM best fit, DESI DR2 BAO + CMB + DESY5. Source: DESI DR2 (2025);
#: identical numbers quoted in docs/OUTSTANDING_ISSUES.md section 1.2.
_W0_OBS = -0.752
_W0_SIG = 0.057
#: wa best fit and symmetrised sigma (+0.23 / -0.20). Same source.
_WA_OBS = -0.86
_WA_SIG = 0.215

#: rho scan bounds. The DR2 (w0, wa) contour is strongly anti-correlated;
#: the exact coefficient needs the public chain, so the verdict is reported
#: across the plausible band rather than at an invented point value.
_RHO_SCAN = [-0.95, -0.90, -0.85, -0.80, -0.75, -0.70, -0.65, -0.60]

#: DESI 2024 LCDM neutrino-mass bound (eV). Source: DESI 2024 VI.
_SUM_MNU_LCDM_BOUND = 0.072
#: Relaxed bound in w0waCDM cosmologies (eV). Source: Elbers et al.
#: 2407.10965 (register 1.5 companion); Allali & Notari 2406.14554 concur.
_SUM_MNU_W0WA_BOUND = 0.16


@dataclass(frozen=True)
class PlaneVerdict:
    rho: float
    chi2: float
    p_value: float
    sigma_equivalent: float


def framework_point() -> Dict[str, float]:
    """The zero-parameter prediction, from the SSOT seed only."""
    from metaphysica.simulations.core.canonical_values import B3

    return {
        "w0": -(B3 - 1.0) / B3,          # -23/24
        "wa": -1.0 / math.sqrt(B3),      # -1/sqrt(24), leading order
    }


def chi2_at_rho(rho: float, point: Optional[Dict[str, float]] = None) -> float:
    """Mahalanobis chi-square (2 dof) of the framework point at given rho."""
    if not -1.0 < rho < 1.0:
        raise ValueError(f"correlation must be in (-1, 1), got {rho}")
    p = point or framework_point()
    u = (p["w0"] - _W0_OBS) / _W0_SIG
    v = (p["wa"] - _WA_OBS) / _WA_SIG
    return (u * u - 2.0 * rho * u * v + v * v) / (1.0 - rho * rho)


def sigma_equivalent(chi2: float) -> float:
    """Gaussian-equivalent sigma for a chi-square with 2 dof.

    For 2 dof the survival function is exact: p = exp(-chi2/2). The
    equivalent two-sided Gaussian significance solves p = erfc(n/sqrt(2)),
    inverted by bisection -- no scipy needed, no approximation beyond float.
    """
    p = math.exp(-chi2 / 2.0)
    lo, hi = 0.0, 40.0
    for _ in range(200):  # bounded; converges to ~1e-12 long before 200
        mid = (lo + hi) / 2.0
        if math.erfc(mid / math.sqrt(2.0)) > p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def scan_rho() -> List[PlaneVerdict]:
    out = []
    for rho in _RHO_SCAN:
        c = chi2_at_rho(rho)
        out.append(PlaneVerdict(
            rho=rho, chi2=c, p_value=math.exp(-c / 2.0),
            sigma_equivalent=sigma_equivalent(c),
        ))
    return out


def _registry_params() -> Optional[Dict[str, Any]]:
    raw = os.environ.get("METAPHYSICA_OUT")
    candidates = []
    if raw:
        candidates.append(Path(raw) / "AutoGenerated" / "parameters.json")
    candidates.append(
        Path(__file__).resolve().parents[5] / "AutoGenerated" / "parameters.json"
    )
    for path in candidates:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))["parameters"]
    return None


def mass_sum_rows() -> List[Dict[str, Any]]:
    """Every registered mass-sum prediction against BOTH bounds.

    The point is the conditional: the LCDM bound excludes the framework's
    values, and the framework's own dark-energy sector is what relaxes the
    bound that would kill it. Reporting both rows keeps the kill-switch
    honest -- if LCDM is reasserted, the FAIL column is already on record.
    """
    params = _registry_params()
    if params is None:
        return [{"parameter": None, "status": "SKIPPED",
                 "note": "parameters.json not available -- run the build"}]
    rows = []
    for name in ("neutrino.mass_sum", "geometry.sum_m_nu", "spectral.sum_m_nu"):
        entry = params.get(name)
        if not entry or not isinstance(entry.get("value"), (int, float)):
            continue
        value = float(entry["value"])
        rows.append({
            "parameter": name,
            "value_eV": value,
            "lcdm_bound_eV": _SUM_MNU_LCDM_BOUND,
            "under_lcdm": "PASS" if value < _SUM_MNU_LCDM_BOUND else "FAIL",
            "w0wa_bound_eV": _SUM_MNU_W0WA_BOUND,
            "under_own_cosmology": (
                "PASS" if value < _SUM_MNU_W0WA_BOUND else "FAIL"
            ),
        })
    return rows


def write_report(out_path: Optional[Path] = None) -> Path:
    if out_path is None:
        raw = os.environ.get("METAPHYSICA_OUT")
        base = Path(raw).resolve() if raw else Path(__file__).resolve().parents[5]
        out_path = base / "AutoGenerated" / "de_plane_gate.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    point = framework_point()
    scan = scan_rho()
    sigmas = [s.sigma_equivalent for s in scan]
    u = (point["w0"] - _W0_OBS) / _W0_SIG
    v = (point["wa"] - _WA_OBS) / _WA_SIG
    mass_rows = mass_sum_rows()
    mass_fails_lcdm = sum(
        1 for r in mass_rows if r.get("under_lcdm") == "FAIL"
    )

    payload: Dict[str, Any] = {
        "schema_version": 1,
        "framework_point": point,
        "anchors": {"w0": [_W0_OBS, _W0_SIG], "wa": [_WA_OBS, _WA_SIG],
                    "source": "DESI DR2 BAO+CMB+DESY5 (2025)"},
        "one_d_marginals_sigma": {"w0": abs(u), "wa": abs(v)},
        "uncorrelated_2d_sigma": sigma_equivalent(u * u + v * v),
        "rho_scan": [asdict(s) for s in scan],
        "sigma_range": [min(sigmas), max(sigmas)],
        "verdict": "TENSION_3SIGMA_ROBUST",
        "kill_condition": (
            "w0 < -0.99 in a future tightened fit, or 2D distance past "
            "5 sigma under this same scan, kills w0 = -23/24 outright"
        ),
        "mass_sum_conditional": mass_rows,
        "count": 1 + len(mass_rows),
        "n_pass": 0,
        "n_fail": mass_fails_lcdm,
        "note": (
            "One honest number instead of two correlated ones: the register's "
            "3.62-sigma (w0) and 2.98-sigma (wa) marginals double-count a "
            "single displacement. In the 2D plane the framework point sits at "
            f"{min(sigmas):.2f}-{max(sigmas):.2f} sigma equivalent across the "
            "plausible correlation band -- a genuine, rho-robust ~3-sigma "
            "tension. This neither rescues the prediction nor overstates it. "
            "The exact rho awaits the public DR2 chain; the conclusion does "
            "not depend on it."
        ),
    }
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return out_path


def main() -> int:
    point = framework_point()
    print("=" * 70)
    print(" DARK-ENERGY PLANE GATE -- (w0, wa) against DESI DR2, rho scan")
    print("=" * 70)
    print(f"  framework point : w0 = {point['w0']:+.6f}  wa = {point['wa']:+.6f}")
    print(f"  DR2 anchors     : w0 = {_W0_OBS} +/- {_W0_SIG}   "
          f"wa = {_WA_OBS} +/- {_WA_SIG}")
    u = (point["w0"] - _W0_OBS) / _W0_SIG
    v = (point["wa"] - _WA_OBS) / _WA_SIG
    print(f"  1D marginals    : |u| = {abs(u):.2f} sigma (w0)   "
          f"|v| = {abs(v):.2f} sigma (wa)   <- double-counted")
    print(f"  uncorrelated 2D : {sigma_equivalent(u*u + v*v):.2f} sigma "
          "<- ignores the ellipse")
    print()
    print("   rho     chi2    sigma-equivalent")
    for s in scan_rho():
        print(f"  {s.rho:+.2f}   {s.chi2:6.2f}    {s.sigma_equivalent:.2f}")
    sigmas = [s.sigma_equivalent for s in scan_rho()]
    print()
    print(f"  VERDICT: {min(sigmas):.2f}-{max(sigmas):.2f} sigma across the "
          "scan -- a rho-robust ~3-sigma tension")
    print()
    print("  Neutrino mass-sum conditional:")
    for r in mass_sum_rows():
        if r.get("parameter") is None:
            print(f"    {r['status']}: {r['note']}")
            continue
        print(f"    {r['parameter']:24} {r['value_eV']:.4f} eV   "
              f"LCDM(<{r['lcdm_bound_eV']}): {r['under_lcdm']:4}   "
              f"own w0waCDM(<{r['w0wa_bound_eV']}): {r['under_own_cosmology']}")
    out = write_report()
    print(f"\n  Report written to: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
