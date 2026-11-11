#!/usr/bin/env python3
"""Dark-energy verdict in the 2D (w0, wa) plane, with correlation sensitivity.

WHY THIS EXISTS
---------------
The registered point is (w0, wa) from CANON: w0 = -(n-1)/n with n set by the
dark_energy_betti fork, wa = -1/sqrt(b3) at the adopted b3. Scored one at a
time against DESI DR2 it gives two 1D sigmas. But the DR2 (w0, wa) posterior
is a strongly anti-correlated ellipse, and two 1D sigmas computed from
correlated marginals DOUBLE-COUNT a single displacement. The honest statement
is one number: the Mahalanobis distance of the point in the 2D plane.

The anchors are read from the experimental loader (desi_2025_constraints.json).
DESI gives asymmetric errors on wa; each coordinate is scaled by the error on
the side of the central value the point lies on, as the scored
cosmology.wa_derived row does, so the gate and the row report one wa tension.

The correlation coefficient rho is not published as a scalar, so this gate
does not invent one. It scans the plausible range and reports the verdict's
sensitivity; every sigma it quotes (the marginals, the scan band, the
uncorrelated 2D value) is computed in write_report, never typed here.

STATUS: only predictions are scored. CANON gives w0 the status INPUT under a
frozen dark_energy_betti option (n is a typed integer, not the live b3) and
PREDICTED under b3_live. With an INPUT w0 the plane distance is reported as
INPUT_CONDITIONED and only the 1D wa marginal is the scored prediction.

This REPLACES anchor-shopping. An earlier advertised "0.027 sigma agreement"
rested on an anchor whose attribution could not be verified; the register
demands a decision between defending that anchor and accepting the honest
headline. This gate is the honest headline, computed rather than chosen.

KILL CONDITION (stated in advance, per the falsification-first posture):
if future BAO+CMB+SNe releases tighten to w0 below _KILL_W0 or push the 2D
distance past _KILL_SIGMA under this same scan, the registered point is dead
-- there is no knob to turn, which is precisely what makes it worth testing.

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
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "PlaneVerdict",
    "framework_point",
    "framework_status",
    "anchors",
    "standardized",
    "mahalanobis",
    "chi2_at_rho",
    "sigma_equivalent",
    "scan_rho",
    "plane_verdict",
    "mass_sum_rows",
    "build_payload",
    "write_report",
    "main",
]

#: rho scan bounds. The DR2 (w0, wa) contour is strongly anti-correlated;
#: the exact coefficient needs the public chain, so the verdict is reported
#: across the plausible band rather than at an invented point value.
_RHO_SCAN = [-0.95, -0.90, -0.85, -0.80, -0.75, -0.70, -0.65, -0.60]
#: A scan band narrower than this (in sigma) is called rho-robust.
_RHO_ROBUST_SPREAD = 0.5
#: Kill thresholds stated in advance (not fitted): a tightened w0 below
#: this value, or a 2D distance past this many sigma, kills the point.
_KILL_W0 = -0.99
_KILL_SIGMA = 5.0

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
    """The registered (w0, wa) point on the active path, read from CANON.

    w0 is CANON["w0"]: -(n-1)/n with n set by the dark_energy_betti fork
    (frozen n is an input constant, b3_live uses the live b3). wa is
    CANON["wa"]: -1/sqrt(b3) at the live b3, leading order. Neither is
    recomputed here, so the gate scores exactly the registered values.
    """
    from metaphysica.simulations.core.canonical_values import CANON

    return {
        "w0": float(CANON["w0"]["value"]),
        "wa": float(CANON["wa"]["value"]),
    }


def framework_status() -> Dict[str, Dict[str, str]]:
    """CANON status and form of each coordinate (INPUT or PREDICTED for w0)."""
    from metaphysica.simulations.core.canonical_values import CANON

    return {key: {"status": CANON[key]["status"], "form": CANON[key]["form"]}
            for key in ("w0", "wa")}


def anchors(point: Optional[Dict[str, float]] = None
            ) -> Dict[str, Tuple[float, float]]:
    """(central value, sigma) of DESI DR2 w0 and wa from the loader.

    sigma is the error on the side of the central value the point lies on
    (ExperimentalValue.uncertainty_toward), the convention of the scored
    cosmology.wa_derived row.
    """
    from metaphysica.simulations.data.experimental_data_loader import get_loader

    p = point or framework_point()
    loader = get_loader()
    out = {}
    for key in ("w0", "wa"):
        ev = loader.get_desi(key)
        out[key] = (float(ev.value), float(ev.uncertainty_toward(p[key])))
    return out


def standardized(point: Optional[Dict[str, float]] = None) -> Tuple[float, float]:
    """(u, v): the point's offsets from the anchors in units of their sigma."""
    p = point or framework_point()
    a = anchors(p)
    return ((p["w0"] - a["w0"][0]) / a["w0"][1],
            (p["wa"] - a["wa"][0]) / a["wa"][1])


def mahalanobis(u: float, v: float, rho: float) -> float:
    """Chi-square (2 dof) of standardized offsets (u, v) at correlation rho."""
    if not -1.0 < rho < 1.0:
        raise ValueError(f"correlation must be in (-1, 1), got {rho}")
    return (u * u - 2.0 * rho * u * v + v * v) / (1.0 - rho * rho)


def chi2_at_rho(rho: float, point: Optional[Dict[str, float]] = None) -> float:
    """Mahalanobis chi-square (2 dof) of the framework point at given rho."""
    if not -1.0 < rho < 1.0:
        raise ValueError(f"correlation must be in (-1, 1), got {rho}")
    u, v = standardized(point)
    return mahalanobis(u, v, rho)


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


def scan_rho(point: Optional[Dict[str, float]] = None) -> List[PlaneVerdict]:
    u, v = standardized(point)
    out = []
    for rho in _RHO_SCAN:
        c = mahalanobis(u, v, rho)
        out.append(PlaneVerdict(
            rho=rho, chi2=c, p_value=math.exp(-c / 2.0),
            sigma_equivalent=sigma_equivalent(c),
        ))
    return out


def plane_verdict(w0_status: str, sigmas: List[float]) -> str:
    """The plane verdict, computed from the w0 status and the scan band.

    An INPUT w0 is not a prediction, so the plane distance is only
    INPUT_CONDITIONED. With a PREDICTED w0 the verdict names the floor of the
    smallest scanned sigma and whether the band is narrower than
    _RHO_ROBUST_SPREAD (ROBUST) or not (RHO_DEPENDENT).
    """
    if w0_status != "PREDICTED":
        return "INPUT_CONDITIONED"
    lo, hi = min(sigmas), max(sigmas)
    robust = hi - lo < _RHO_ROBUST_SPREAD
    return "TENSION_%dSIGMA_%s" % (int(lo), "ROBUST" if robust else "RHO_DEPENDENT")


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


def _kill_condition(status: Dict[str, Dict[str, str]]) -> str:
    return (
        f"w0 < {_KILL_W0} in a future tightened fit, or 2D distance past "
        f"{_KILL_SIGMA:g} sigma under this same scan, kills the registered point "
        f"(w0 = {status['w0']['form']}, status {status['w0']['status']}; "
        f"wa = {status['wa']['form']}, status {status['wa']['status']}) outright"
    )


def _note(u: float, v: float, sigmas: List[float], uncorrelated: float,
          status: Dict[str, Dict[str, str]]) -> str:
    lo, hi = min(sigmas), max(sigmas)
    band = ("rho-robust" if hi - lo < _RHO_ROBUST_SPREAD else "rho-dependent")
    text = (
        f"One number instead of two correlated ones: the 1D marginals "
        f"{abs(u):.2f}-sigma (w0) and {abs(v):.2f}-sigma (wa) double-count a "
        f"single displacement. In the 2D plane the point sits at "
        f"{lo:.2f}-{hi:.2f} sigma equivalent across the scanned correlation "
        f"band ({band}, spread {hi - lo:.2f} sigma; uncorrelated 2D would "
        f"read {uncorrelated:.2f}). The exact rho awaits the public DR2 chain. "
    )
    w0 = status["w0"]
    if w0["status"] != "PREDICTED":
        return text + (
            f"w0 = {w0['form']} has CANON status {w0['status']} on this path: "
            f"it is not scored as a prediction, so the plane distance is "
            f"INPUT_CONDITIONED and only wa ({abs(v):.2f}-sigma) is scored.")
    return text + "Both coordinates are PREDICTED on this path."


def build_payload() -> Dict[str, Any]:
    """The report payload; every sigma and text number is computed here."""
    point = framework_point()
    status = framework_status()
    a = anchors(point)
    u, v = standardized(point)
    scan = scan_rho(point)
    sigmas = [s.sigma_equivalent for s in scan]
    uncorrelated = sigma_equivalent(u * u + v * v)
    mass_rows = mass_sum_rows()
    w0_scored = status["w0"]["status"] == "PREDICTED"
    return {
        "schema_version": 1,
        "framework_point": point,
        "framework_status": status,
        "anchors": {"w0": list(a["w0"]), "wa": list(a["wa"]),
                    "source": "DESI DR2 BAO+CMB+DESY5 (2025), "
                              "desi_2025_constraints.json; sigma on the "
                              "side of the point"},
        "one_d_marginals_sigma": {"w0": abs(u), "wa": abs(v)},
        "uncorrelated_2d_sigma": uncorrelated,
        "rho_scan": [asdict(s) for s in scan],
        "sigma_range": [min(sigmas), max(sigmas)],
        "verdict": plane_verdict(status["w0"]["status"], sigmas),
        "scored": "plane" if w0_scored else "wa",
        "scored_sigma": min(sigmas) if w0_scored else abs(v),
        "kill_condition": _kill_condition(status),
        "mass_sum_conditional": mass_rows,
        "count": 1 + len(mass_rows),
        "n_pass": 0,
        "n_fail": sum(1 for r in mass_rows if r.get("under_lcdm") == "FAIL"),
        "note": _note(u, v, sigmas, uncorrelated, status),
    }


def write_report(out_path: Optional[Path] = None) -> Path:
    if out_path is None:
        raw = os.environ.get("METAPHYSICA_OUT")
        base = Path(raw).resolve() if raw else Path(__file__).resolve().parents[5]
        out_path = base / "AutoGenerated" / "de_plane_gate.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(build_payload(), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return out_path


def main() -> int:
    payload = build_payload()
    point, a = payload["framework_point"], payload["anchors"]
    marg = payload["one_d_marginals_sigma"]
    print("=" * 70)
    print(" DARK-ENERGY PLANE GATE -- (w0, wa) against DESI DR2, rho scan")
    print("=" * 70)
    print(f"  framework point : w0 = {point['w0']:+.6f}  wa = {point['wa']:+.6f}")
    print(f"  CANON status    : w0 {payload['framework_status']['w0']['status']}"
          f"   wa {payload['framework_status']['wa']['status']}")
    print(f"  DR2 anchors     : w0 = {a['w0'][0]} +/- {a['w0'][1]}   "
          f"wa = {a['wa'][0]} +/- {a['wa'][1]} (side of the point)")
    print(f"  1D marginals    : |u| = {marg['w0']:.2f} sigma (w0)   "
          f"|v| = {marg['wa']:.2f} sigma (wa)   <- double-counted")
    print(f"  uncorrelated 2D : {payload['uncorrelated_2d_sigma']:.2f} sigma "
          "<- ignores the ellipse")
    print()
    print("   rho     chi2    sigma-equivalent")
    for s in payload["rho_scan"]:
        print(f"  {s['rho']:+.2f}   {s['chi2']:6.2f}    {s['sigma_equivalent']:.2f}")
    lo, hi = payload["sigma_range"]
    print()
    print(f"  VERDICT: {payload['verdict']} ({lo:.2f}-{hi:.2f} sigma across "
          f"the scan; scored: {payload['scored']})")
    print()
    print("  Neutrino mass-sum conditional:")
    for r in payload["mass_sum_conditional"]:
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
