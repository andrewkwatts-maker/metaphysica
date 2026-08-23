#!/usr/bin/env python3
"""Evaluate proposed closed-form "parameter closures" and record honest verdicts.

WHY THIS EXISTS
---------------
A 2026-08 external review proposed a dozen closed-form expressions claimed to
eliminate the framework's remaining calibration inputs -- the VEV factor, the
GUT coupling, the Weinberg angle, PMNS angles, the cosmological constant, the
Hubble tension, the muon g-2 shift, a Majorana phase, a soft-SUSY scale, and a
baryogenesis prefactor. Each arrived with a claimed numerical result.

Checking the arithmetic BEFORE integration is the whole point of this gate:
most of the proposals fail their own numbers. The Weinberg formula evaluates
to 0.365, not the claimed 0.2312. The theta_13 formula gives 0.31 degrees, not
the claimed 8.618. The Golay cosmological-constant expression gives 1.17e-6
against a claimed 1.17e-120 -- one hundred and fourteen orders of magnitude of
difference between a formula and its own advertised output. Wiring any of
these in as "derivations" would manufacture exactly the fake-pass failure mode
this validation layer exists to eliminate.

The framework's standing rule is that falsified elegant candidates STAY ON THE
BOOKS, labelled FALSIFIED, so the same dead end is never explored twice. This
gate is that ledger for externally proposed closures: every candidate is
evaluated from SSOT inputs, compared against both its own claim and the
experimental anchor, and given a verdict that a build artifact records.

VERDICTS
--------
FALSIFIED            computed value contradicts experiment and/or the
                     proposal's own claimed output
ILL_FORMED           the expression is not mathematically evaluable as given
NEAR_MISS_NOTED      a numerical coincidence worth recording, with the
                     look-elsewhere caveat, but not adopted
PLAUSIBLE_UNTESTABLE arithmetic is self-consistent but no measurement exists
                     to test it against
ALREADY_INTEGRATED   the proposal restates something the codebase already has
OPEN_PROPOSAL        a structural idea with no numerical content to test;
                     adopting it is an author ruling, not an arithmetic check

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = [
    "CandidateVerdict",
    "evaluate_all_candidates",
    "write_report",
    "main",
]

# ── Experimental anchors (inline with source attribution, per SSOT policy) ──
#: sin^2(theta_W) in the MS-bar scheme at M_Z. Source: PDG 2024.
_SIN2_THETA_W_MZ = 0.23122
#: Solar mixing angle theta_12 in degrees. Source: NuFIT 6.0 (2024), IO/NO avg.
_THETA_12_DEG = 33.44
_THETA_12_SIGMA = 0.77
#: Reactor angle theta_13 in degrees. Source: NuFIT 6.0 (2024).
_THETA_13_DEG = 8.57
#: Baryon-to-photon ratio eta_B. Source: Planck 2018 + BBN.
_ETA_B = 6.12e-10
#: Jarlskog invariant, CKM. Source: PDG 2024.
_J_CP = 3.08e-5
#: Reduced Planck mass in GeV. Source: CODATA 2022 (M_Pl / sqrt(8 pi)).
_M_PL_REDUCED_GEV = 2.435e18
#: Canonical GUT scale in GeV. Source: standard SU(5)/SO(10) running.
_M_GUT_GEV = 2.0e16
#: Fine-structure constant. Source: CODATA 2022.
_ALPHA_EM = 7.2973525693e-3
#: Historical muon g-2 tension (BNL+FNAL vs 2020 theory WP), Delta a_mu.
#: Source: Muon g-2 collab. 2023. NOTE: 2024-2025 lattice-HVP results have
#: largely dissolved this tension; the anchor is kept for the claim check.
_DELTA_A_MU_HISTORICAL = 2.49e-9
#: Planck-inferred early-universe H0, km/s/Mpc. Source: Planck 2018.
_H0_PLANCK = 67.4
#: VEV calibration factor the proposal claims to reproduce (framework value).
_VEV_FACTOR_CLAIMED = 1.5859
#: GUT calibration coefficient the proposal claims to replace: 1/(10*pi).
_ALPHA_GUT_COEFF = 1.0 / (10.0 * math.pi)


@dataclass(frozen=True)
class CandidateVerdict:
    candidate_id: str
    expression: str
    computed: Optional[float]
    claimed: Optional[float]
    anchor: Optional[float]
    anchor_source: str
    verdict: str  # see module docstring
    note: str
    extras: Dict[str, Any] = field(default_factory=dict)


def _seeds():
    """SSOT inputs: b3 and chi_eff come from the canonical-values module."""
    from metaphysica.simulations.core.canonical_values import B3, CHI_EFF

    return float(B3), float(CHI_EFF)


def evaluate_all_candidates() -> List[CandidateVerdict]:
    b3, chi_eff = _seeds()
    pi = math.pi
    alpha_leak = 1.0 / math.sqrt(6.0)
    # k_beth as DEFINED BY THE PROPOSAL (b3^1.5 + 1/pi); not a registry value.
    k_beth = b3 ** 1.5 + 1.0 / pi
    out: List[CandidateVerdict] = []

    # 1. VEV factor = (26/10) * (1 - 1/b3^2)^(3/2), claimed ~ 1.5859
    from metaphysica.simulations.core.FormulasRegistry import get_registry

    reg = get_registry()
    d_bulk = float(reg.D_ancestral_total)  # 26 under the current ruling
    decad = float(reg.DECAD)               # 10
    vev = (d_bulk / decad) * (1.0 - 1.0 / b3 ** 2) ** 1.5
    out.append(CandidateVerdict(
        candidate_id="vev-factor-dimension-ratio",
        expression="(D_bulk/10) * (1 - 1/b3^2)^(3/2)",
        computed=vev, claimed=_VEV_FACTOR_CLAIMED, anchor=_VEV_FACTOR_CLAIMED,
        anchor_source="framework VEV calibration factor",
        verdict="FALSIFIED",
        note=(f"Evaluates to {vev:.4f}, not the claimed 1.5859 -- off by "
              f"{abs(vev - _VEV_FACTOR_CLAIMED) / _VEV_FACTOR_CLAIMED:.0%}. "
              "The proposal fails its own target before physics enters."),
    ))

    # 2. alpha_GUT coefficient from Vol(S^5) = pi^3 wrapping a D5 singularity
    computed_coeff = 1.0 / (pi ** 3 * (k_beth / chi_eff))
    vol_s5_ratio = pi ** 3 / (10.0 * pi)  # = pi^2/10
    out.append(CandidateVerdict(
        candidate_id="alpha-gut-s5-volume",
        expression="1 / (Vol(S^5) * k_beth / chi_eff)",
        computed=computed_coeff, claimed=0.032177, anchor=_ALPHA_GUT_COEFF,
        anchor_source="framework GUT calibration 1/(10*pi)",
        verdict="FALSIFIED",
        note=(f"Evaluates to {computed_coeff:.5f} vs the calibration "
              f"{_ALPHA_GUT_COEFF:.5f} -- {abs(computed_coeff/_ALPHA_GUT_COEFF-1):.0%} off. "
              "Separately noted: Vol(S^5)=pi^3 differs from 10*pi by exactly "
              f"pi^2/10 = {vol_s5_ratio:.4f} (1.3%), a coincidence recorded "
              "under NEAR_MISS below."),
        extras={"vol_s5_over_10pi": vol_s5_ratio},
    ))
    out.append(CandidateVerdict(
        candidate_id="vol-s5-ten-pi-coincidence",
        expression="Vol(S^5) = pi^3 vs 10*pi",
        computed=pi ** 3, claimed=None, anchor=10.0 * pi,
        anchor_source="framework GUT calibration denominator",
        verdict="NEAR_MISS_NOTED",
        note=("pi^3 = 31.006 vs 10*pi = 31.416: 1.3% apart because "
              "pi^2/10 = 0.98696. Recorded, not adopted -- a 1.3% miss among "
              "the space of small closed forms is well inside the "
              "look-elsewhere trap this framework already documented for "
              "theta_13."),
    ))

    # 3. Majorana phase eta = pi*sqrt(det/chi_eff) + 2pi/b3 with det = -25
    det_ratio = -25.0 / chi_eff
    out.append(CandidateVerdict(
        candidate_id="majorana-eta-picard",
        expression="pi*sqrt(-25/chi_eff) + 2*pi/b3, claimed = 5*pi/12",
        computed=None, claimed=math.degrees(5 * pi / 12), anchor=None,
        anchor_source="no measurement of eta exists",
        verdict="ILL_FORMED",
        note=(f"sqrt({det_ratio:.4f}) is imaginary, so the expression is not "
              "a real angle as written. Even taking |det|: pi*(5/12) + pi/12 "
              "= pi/2 = 90 deg, not the claimed 75 deg. Twice inconsistent. "
              "The det(N+ n N-) = -25 input is also not derived from any "
              "lattice data present in this codebase."),
    ))

    # 4. Baryogenesis prefactor J_CP / (Vol(G2)^2 * d^3) * (b3/chi_eff)
    golay_d = 8.0  # [[24,12,8]] code distance -- format-exception integer
    baryo = _J_CP / (6.0 * golay_d ** 3) * (b3 / chi_eff)
    out.append(CandidateVerdict(
        candidate_id="baryogenesis-golay-prefactor",
        expression="J_CP / (Vol(G2)^2 * d^3) * (b3/chi_eff)",
        computed=baryo, claimed=None, anchor=_ETA_B,
        anchor_source="Planck 2018 + BBN eta_B",
        verdict="FALSIFIED",
        note=(f"Gives {baryo:.2e} vs eta_B = {_ETA_B:.2e} -- a factor "
              f"{baryo / _ETA_B:.1f} off (and 19x off the baryon-to-entropy "
              "ratio). Order-of-magnitude proximity only; 'cleanly outputs a "
              "fixed coefficient' is not supported."),
    ))

    # 5. Lambda = (b3/chi_eff) * k_beth / 2^b3, claimed ~ 1.17e-120
    lam = (b3 / chi_eff) * (k_beth / 2.0 ** b3)
    out.append(CandidateVerdict(
        candidate_id="lambda-golay-capacity",
        expression="(b3/chi_eff) * k_beth / 2^b3",
        computed=lam, claimed=1.17e-120, anchor=1.1e-120,
        anchor_source="observed Lambda in Planck units (order)",
        verdict="FALSIFIED",
        note=(f"Evaluates to {lam:.3e} -- the claimed 1.17e-120 fabricates "
              "114 orders of magnitude. The mantissa happens to match, which "
              "makes the exponent error easy to miss on a skim; that is why "
              "this gate exists."),
    ))

    # 6. Hubble shift = H0 * (1 - (w0/-1)^alpha_leak), claimed 4.15
    from metaphysica.simulations.core.canonical_values import all_canonical

    h0_local = float(all_canonical()["H0_km_s_Mpc"]["value"])  # 71.55, FITTED
    w0 = -(b3 - 1.0) / b3
    shift = h0_local * (1.0 - (w0 / -1.0) ** alpha_leak)
    out.append(CandidateVerdict(
        candidate_id="hubble-shift-alpha-leak",
        expression="H0_local * (1 - (23/24)^(1/sqrt(6)))",
        computed=shift, claimed=4.15, anchor=h0_local - _H0_PLANCK,
        anchor_source="SH0ES-vs-Planck gap using framework H0_local",
        verdict="FALSIFIED",
        note=(f"Gives {shift:.2f} km/s/Mpc, not the claimed 4.15; "
              f"{h0_local:.2f} - {shift:.2f} = {h0_local - shift:.2f}, which "
              f"does not land on Planck's {_H0_PLANCK}. The reconciliation "
              "claim rests on wrong arithmetic."),
    ))

    # 7. Weinberg angle = (3/8) * (1 - 2/(b3*pi)), claimed ~ 0.2312
    weinberg = (3.0 / 8.0) * (1.0 - 2.0 / (b3 * pi))
    out.append(CandidateVerdict(
        candidate_id="weinberg-d5-running",
        expression="(3/8) * (1 - 2/(b3*pi))",
        computed=weinberg, claimed=0.2312, anchor=_SIN2_THETA_W_MZ,
        anchor_source="PDG 2024 sin^2(theta_W)(M_Z)",
        verdict="FALSIFIED",
        note=(f"Evaluates to {weinberg:.5f}, {weinberg / _SIN2_THETA_W_MZ:.2f}x "
              "the measured value. The claimed 'sub-sigma precision' is a "
              "58% miss. (3/8 at the GUT scale is standard group theory; the "
              "proposed one-step correction is not a running calculation.)"),
    ))

    # 8. m_soft = M_Pl * exp(-2*pi*chi_eff/(b3*d)), the one that self-checks
    m_soft = _M_PL_REDUCED_GEV * math.exp(-2.0 * pi * chi_eff / (b3 * golay_d))
    out.append(CandidateVerdict(
        candidate_id="soft-susy-golay-suppression",
        expression="M_Pl_reduced * exp(-2*pi*chi_eff/(b3*d))",
        computed=m_soft, claimed=2.18e16, anchor=_M_GUT_GEV,
        anchor_source="canonical GUT scale (no measured m_soft exists)",
        verdict="PLAUSIBLE_UNTESTABLE",
        note=(f"The only proposal whose arithmetic survives: exponent "
              f"-2pi*144/192 = -1.5*pi exactly, giving {m_soft:.2e} GeV, "
              f"{m_soft / _M_GUT_GEV:.2f}x the canonical GUT scale. But "
              "m_soft is unmeasured (SUSY unobserved), so this is a "
              "candidate, not a prediction that can currently be tested."),
    ))

    # 9. theta_13 = arcsin(alpha_leak/(b3*pi)), claimed 8.618 deg
    t13 = math.degrees(math.asin(alpha_leak / (b3 * pi)))
    out.append(CandidateVerdict(
        candidate_id="pmns-theta13-leak",
        expression="arcsin((1/sqrt(6)) / (b3*pi))",
        computed=t13, claimed=8.618, anchor=_THETA_13_DEG,
        anchor_source="NuFIT 6.0 theta_13",
        verdict="FALSIFIED",
        note=(f"Evaluates to {t13:.3f} deg -- the claim of 8.618 deg is a "
              f"{8.618 / t13:.0f}x arithmetic error in the proposal itself. "
              "The formula as written misses experiment by 27x."),
    ))

    # 10. theta_12 = arctan(1/sqrt(5)), claimed a victory at 24.09 deg
    t12 = math.degrees(math.atan(1.0 / math.sqrt(5.0)))
    t12_sigmas = abs(t12 - _THETA_12_DEG) / _THETA_12_SIGMA
    out.append(CandidateVerdict(
        candidate_id="pmns-theta12-golden",
        expression="arctan(1/sqrt(5))",
        computed=t12, claimed=24.094, anchor=_THETA_12_DEG,
        anchor_source="NuFIT 6.0 theta_12 (33.44 +/- 0.77 deg)",
        verdict="FALSIFIED",
        note=(f"Arithmetic is fine ({t12:.2f} deg) but experiment says "
              f"{_THETA_12_DEG} deg -- a {t12_sigmas:.0f}-sigma miss "
              "presented as a within-tolerance result."),
    ))

    # 11. Muon g-2: Delta a_mu = alpha_EM / (2*pi*b3*k_beth), claimed 24.9e-10
    damu = _ALPHA_EM / (2.0 * pi * b3 * k_beth)
    out.append(CandidateVerdict(
        candidate_id="muon-g2-torsion",
        expression="alpha_EM / (2*pi*b3*k_beth)",
        computed=damu, claimed=2.49e-9, anchor=_DELTA_A_MU_HISTORICAL,
        anchor_source="historical BNL+FNAL vs 2020 WP tension",
        verdict="FALSIFIED",
        note=(f"Evaluates to {damu:.2e}, {damu / 2.49e-9:.0f}x the claimed "
              "value. Also stale as a target: 2024-2025 lattice-HVP results "
              "have largely dissolved the g-2 tension, so 'resolving' it is "
              "no longer the win the proposal assumes."),
    ))

    # 12. Axion-mass b3 link / BabyIAXO window: already in the codebase
    out.append(CandidateVerdict(
        candidate_id="axion-babyiaxo-link",
        expression="m_a(b3=24) ~ 3.51 meV in the BabyIAXO window",
        computed=None, claimed=3.51e-3, anchor=None,
        anchor_source="BabyIAXO 2028 sensitivity window",
        verdict="ALREADY_INTEGRATED",
        note=("The b3-to-axion-mass link and its falsification window are "
              "already implemented and tested "
              "(tests/test_axion_photon_coupling.py asserts the BabyIAXO "
              "window). The proposal restates existing work."),
    ))

    # 13. Kahler-Ricci running Re(T) + instanton-corrected W(T)
    out.append(CandidateVerdict(
        candidate_id="running-ret-kahler-ricci",
        expression="dg/dln(mu) = -2*R + grad(Phi)^2/(b3*pi) + ... ; "
                   "W(T) += sum C_i exp(-2*pi*chi_i/(b3*T))",
        computed=None, claimed=None, anchor=None,
        anchor_source="Re(T) tension: 9.865 (Higgs) vs 7.086 (BBN)",
        verdict="OPEN_PROPOSAL",
        note=("Structural idea with no evaluable numbers: the C_i and chi_i "
              "per-cycle inputs do not exist in this codebase and would have "
              "to be invented to implement it. Whether to build a running-"
              "modulus sector is an author ruling; nothing here can be "
              "arithmetic-checked, so nothing is adopted or falsified."),
    ))

    return out


def write_report(
    verdicts: Optional[List[CandidateVerdict]] = None,
    out_path: Optional[Path] = None,
) -> Path:
    if verdicts is None:
        verdicts = evaluate_all_candidates()
    if out_path is None:
        raw = os.environ.get("METAPHYSICA_OUT")
        base = Path(raw).resolve() if raw else Path(__file__).resolve().parents[5]
        out_path = base / "AutoGenerated" / "candidate_closures.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    counts: Dict[str, int] = {}
    for v in verdicts:
        counts[v.verdict] = counts.get(v.verdict, 0) + 1

    payload: Dict[str, Any] = {
        "schema_version": 1,
        "count": len(verdicts),
        "n_pass": 0,
        "n_fail": counts.get("FALSIFIED", 0) + counts.get("ILL_FORMED", 0),
        "verdict_counts": counts,
        "candidates": [asdict(v) for v in verdicts],
        "note": (
            "Externally proposed closed-form parameter closures, evaluated "
            "from SSOT inputs before any integration. Most fail their own "
            "claimed numbers; per the framework's standing rule, falsified "
            "candidates stay on the books labelled FALSIFIED so the same "
            "dead end is never explored twice. n_pass is 0 by construction: "
            "this gate records verdicts on proposals, it does not certify "
            "framework predictions."
        ),
    }
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return out_path


def main() -> int:
    verdicts = evaluate_all_candidates()
    print("=" * 74)
    print(" CANDIDATE CLOSURE GATE -- externally proposed parameter closures")
    print("=" * 74)
    for v in verdicts:
        comp = f"{v.computed:.4g}" if v.computed is not None else "--"
        clm = f"{v.claimed:.4g}" if v.claimed is not None else "--"
        print(f"  [{v.verdict:20}] {v.candidate_id}")
        print(f"      {v.expression}")
        print(f"      computed={comp}  claimed={clm}  ({v.anchor_source})")
    out = write_report(verdicts)
    counts: Dict[str, int] = {}
    for v in verdicts:
        counts[v.verdict] = counts.get(v.verdict, 0) + 1
    print()
    print("  " + "  ".join(f"{k}={n}" for k, n in sorted(counts.items())))
    print(f"  Report written to: {out}")
    # Report-only: FALSIFIED verdicts are the honest OUTPUT of this gate,
    # not a build failure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
