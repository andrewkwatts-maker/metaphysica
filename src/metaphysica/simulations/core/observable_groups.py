"""
observable_groups.py — shared observable-group mapping (Sprint T2 #6).
=====================================================================

Single source of truth for the "same physical observable, multiple
registered parameters" mapping used by:

* ``scripts/audit_shadow_derivations.py`` — the CI shadow-derivation
  detector that flags pairwise numeric disagreement between members of
  the same group.
* ``metaphysica.simulations.PM.analysis.proof_completeness`` — the
  proof-completeness ledger, which exposes a ``Duplicate_Derivations``
  column listing the other registered parameter IDs that compute the
  same observable.

Keeping a single ``OBSERVABLE_GROUPS`` dict here keeps the shadow detector
and the ledger's cross-link surface in lock-step: adding a new alternate
derivation in one place automatically lights up the duplication marker in
both reports.

Each key is the human-readable observable name; each value is the list of
canonical parameter IDs the registry uses to surface different chains for
that observable. Group members that don't appear in the live registry are
silently skipped by both consumers, so the map can over-specify safely as
the registry evolves.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from typing import Dict, List, Mapping, Tuple


#: Explicit observable -> registered parameter IDs mapping. Human-curated
#: rather than heuristic-on-name: it makes the duplication surface
#: reproducible and audit-friendly. To extend, add a new key + list of
#: canonical parameter IDs that all derive the same physical observable.
OBSERVABLE_GROUPS: Dict[str, List[str]] = {
    "theta_13": [
        "nufit.theta_13",
        "geometry.theta_13",
        "neutrino.theta_13_pred",
        "pmns.theta_13_triality",
        "particle.theta_13_deg",
    ],
    "eta_B": [
        "cosmology.eta_baryon_pred",
        "cosmology.eta_baryon_geometric",
        "cosmology.eta_B",
        "geometry.eta_baryon",
    ],
    "n_s": [
        "cosmology.n_s_pred",
        "cosmology.n_s",
        "geometry.n_s",
    ],
    "H0_local": [
        # Canonical SH0ES anchor (v16.2 geometric anchor; observational input,
        # not a derivation). Sprint T3 #5 disposition: this is the single
        # canonical late-time H0 value for the framework.
        "geometry.H0_local",
        # v26.x mirror-DM linear-response resolver. Returns 73.04 baseline
        # plus a Δw_mirror ~ 1e-13 shift -- documented in cosmological_tensions
        # as DOCUMENTED_TENSION (magnitude 10^13x too small to actually
        # resolve). Kept in the cross-check because the *value* matches the
        # 73.04 anchor (delta is sub-pico-km/s/Mpc); the disagreement is
        # honestly flagged in the module status string, not the number.
        "cosmology.H0_resolved_km_s_Mpc",
        # bridge_axion_ede.H0_predicted -- KNP early dark energy attempt.
        # Returns 67.4 (Planck baseline) when the EDE shift is negligible
        # (f_EDE ~ 7e-9 in current implementation), and only deviates when
        # the modified sound horizon r_s shifts. When present in the
        # registry it is the EARLY-universe-anchored prediction, so it is
        # not directly comparable to the late-time SH0ES anchor and is
        # intentionally omitted from the cross-check below.
        # Intentionally omitted from the cross-check:
        #   cosmology.H0_local
        #       ricci_flow_h0.py's late-time H(z=0) = H0_planck * (1 + sin^2(31°)/2)
        #       ≈ 76.34 km/s/Mpc. The 31° "13D/26D volume mixing angle" is
        #       documented in hubble_tension.py (lines 39-43) as a fitted
        #       phenomenological parameter, not a derivation from G2 topology.
        #       Treated as a documented_alternative path (an attempted but
        #       quantitatively non-canonical late-time evolution model) per
        #       the same pattern as higgs.m_higgs_geometric (failed pure-
        #       geometry leg) and higgs.m_higgs_bulk (raw 26D pre-projection).
        #   cosmology.H0_predicted
        #       bridge_axion_ede.py BAO-anchored prediction; not consistently
        #       registered, and when present is the early-universe anchored
        #       value (~67.4) not the late-time SH0ES anchor.
    ],
    # S8 — canonical framework prediction only.
    #   s8_pm_baseline is the Planck observational anchor (~0.83); excluded.
    #   S8_resolved is Sprint 5.5's "tensions resolved" output but the magnitude
    #   gap (delta_w_mirror 10^13 too small to actually shift S8) is honestly
    #   documented in cosmological_tensions.py — the returned value collapses
    #   to the baseline anchor, so surfacing it here generates a spurious
    #   shadow with the canonical prediction s8_pm_predicted (~0.815 after
    #   the R2 growth-ODE ruling replaced the retired 5.1% exponential).
    #   Excluded as a documented_alternative per T1.6 honest-accounting
    #   precedent.
    "S8": [
        "cosmology.s8_pm_predicted",
    ],
    "m_higgs": [
        "pdg.m_higgs",
        "particle.m_h_GeV",
        "higgs.m_h",
        "higgs.m_higgs_local",
        # Intentionally omitted from the cross-check:
        #   higgs.m_higgs_geometric (documented failed pure-geometry leg)
        #   higgs.m_higgs_bulk      (raw 26D bulk tension, pre-projection)
        #   higgs.m_higgs_pred      (Sprint T3 #4 disposition: legacy v24.2
        #       racetrack-inversion ansatz with hand-tuned Re(T) = 9.865 in
        #       higgs_mass.py. The Re(T) value was inverted to give m_h =
        #       125.10 GeV under v24.2 constants (y_top = 0.99, v_Y = 174.0
        #       GeV); when later sprints refined y_top → 0.9919 and
        #       v_Y → 174.10 the calibration drifted, yielding m_h ≈ 120.62
        #       GeV (3.58% low). v25.0 supersedes this with the MSSM CP-even
        #       diagonalisation path in higgs_sector.py
        #       (particle.m_h_GeV = 125.08), which is the canonical late-
        #       sprint derivation already in the cross-check above. The
        #       legacy parameter is kept in the registry for backwards
        #       compat / paper reproducibility and treated as a documented
        #       alternative path (same pattern as m_higgs_geometric and
        #       m_higgs_bulk above).
    ],
    "g_a_gamma": [
        # Sprint T5 #8: both registry slots store the ALP-photon coupling as
        # UTF-8 superscript strings (``"10⁻¹¹"``, ``"2.9×10⁻¹¹"``); the
        # auditor's ``_coerce_string_value`` helper parses them into floats so
        # the order-of-magnitude cross-check actually fires. ``…_value`` is
        # the explicit numerical anchor (2.9e-11 GeV^-1, IAXO discovery
        # window mid-point); ``alp.coupling_GeV_inv`` is the bare order-of-
        # magnitude (1e-11 GeV^-1). With the 50% per-observable tolerance
        # override they agree as "same order of magnitude" which is the only
        # claim the framework makes here.
        "alp.coupling_GeV_inv",
        "alp.coupling_GeV_inv_value",
    ],
    "sigma_m_nu": [
        # Sprint T5 #8: the originally-listed ``cosmology.sigma_m_refined_eV``
        # / ``neutrino.sigma_m_nu`` slots are not registered in the live
        # registry, leaving the group with zero numeric members. The two
        # parameters that actually surface the predicted neutrino-mass sum
        # are ``geometry.sum_m_nu`` (pure-topology prediction from the b3=24
        # spectrum) and ``spectral.sum_m_nu`` (m_1+m_2+m_3 from the Dirac
        # spectral chain). Both are floats in eV; the 10% per-observable
        # tolerance override accommodates the legitimate cosmology-bound vs
        # spectral-chain spread.
        "geometry.sum_m_nu",
        "spectral.sum_m_nu",
    ],
}


def build_param_to_group_index(
    groups: Mapping[str, List[str]] = OBSERVABLE_GROUPS,
) -> Dict[str, Tuple[str, Tuple[str, ...]]]:
    """Invert ``groups`` into a ``param_id -> (observable, siblings)`` map.

    For each parameter ID that appears in any group, return the observable
    name plus the *other* parameter IDs in the same group (i.e. the cross-
    link targets). Parameters that do not appear in any group are absent
    from the result.

    Parameters
    ----------
    groups
        The observable->members map. Defaults to the module-level
        :data:`OBSERVABLE_GROUPS`. Accepts any mapping so tests can pass a
        scoped subset without monkey-patching.

    Returns
    -------
    dict
        ``{param_id: (observable_name, tuple_of_other_member_ids)}``.
        ``tuple_of_other_member_ids`` is in the deterministic order the
        group was declared, minus the lookup ID itself.
    """
    index: Dict[str, Tuple[str, Tuple[str, ...]]] = {}
    for observable, members in groups.items():
        # Deduplicate while preserving the declaration order — JSON+MD
        # output is deterministic across runs.
        seen: List[str] = []
        for m in members:
            if m not in seen:
                seen.append(m)
        for m in seen:
            others = tuple(other for other in seen if other != m)
            index[m] = (observable, others)
    return index


__all__ = [
    "OBSERVABLE_GROUPS",
    "build_param_to_group_index",
]

# ══════════════════════════════════════════════════════════════════════════
# Disposition ledger (2026-08-24)
# ══════════════════════════════════════════════════════════════════════════
#
# WHY THIS EXISTS
# ---------------
# OBSERVABLE_GROUPS above is human-curated, and its own docstring defends
# that as "reproducible and audit-friendly". It is also how the shadow
# detector went blind. A curated allowlist records what someone REMEMBERED
# to check, and it drifts toward what already agrees:
#
#   * the H0_local group held two entries, both 73.04, and reported
#     CONSISTENT -- while the registry also shipped H0_local = 71.55 (the
#     canonical value) and H0_ricci_variant = 76.34 (a 3.17-sigma FAIL)
#   * the S8 group held ONE entry, so the detector reported "insufficient
#     data" while four distinct S8 values were registered
#   * theta_13's group omitted theta13_derived = 9.594 deg, the framework's
#     own 9.31-sigma failure, so it was never compared against the 8.669 deg
#     carried by particle.theta_13_rad
#
# The detector reported 0 conflicts throughout.
#
# WHY NOT SIMPLY AUTO-DISCOVER
# ----------------------------
# Naive name matching swings to the opposite error. Grouping H0_early (67.4,
# Planck) with H0_late_evolved (73.04, SH0ES) would report the HUBBLE
# TENSION ITSELF as a code defect. It is physical, not a bug. False
# conflicts corrode a report just as fast as false silence -- both teach the
# reader to stop looking.
#
# THE FIX
# -------
# Discovery finds candidates; a DISPOSITION must exist for every one.
# Omission becomes structurally impossible, because an unclassified
# parameter surfaces as UNTRIAGED instead of vanishing. Distinctness stays
# declarable, so genuine physics does not read as a defect -- but it must be
# DECLARED, with a reason, rather than assumed by omission.

#: Substrings identifying candidate parameters per observable. Cast WIDE on
#: purpose: over-collection costs one disposition line, under-collection
#: costs a contradiction that never surfaces.
OBSERVABLE_TOKENS: Dict[str, Tuple[str, ...]] = {
    "theta_13": ("theta_13", "theta13"),
    "eta_B": ("eta_b", "eta_baryon"),
    "n_s": ("n_s_", ".n_s"),
    "H0_local": ("h0",),
    "S8": ("s8",),
    "m_higgs": ("m_higgs", "m_h_", ".m_h"),
    "g_a_gamma": ("g_a_gamma", "coupling_gev"),
    # "mass_sum" added 2026-08-24: neutrino.mass_sum = 0.1012 eV was
    # escaping discovery entirely -- the name contains neither m_nu nor
    # sum_m_nu. Found when the DE plane gate listed it beside the two
    # discovered sums (0.0598, 0.0817) and the trio visibly disagreed.
    "sigma_m_nu": ("m_nu", "sum_m_nu", "mass_sum"),
}

#: Disposition kinds.
MEMBER = "MEMBER"              # competing derivation -- compare it
DISTINCT = "DISTINCT"          # different physical quantity -- do not compare
INTERMEDIATE = "INTERMEDIATE"  # coefficient/sigma/ratio, not a prediction
UNTRIAGED = "UNTRIAGED"        # nobody has classified it -- a finding

#: Every candidate must appear here. The reason string is the point: it is
#: what stops a future reader from quietly re-curating the report back into
#: agreement.
DISPOSITIONS: Dict[str, Tuple[str, str]] = {
    # -- H0: the tension is physical; the rival derivations are not --------
    "cosmology.H0_early": (DISTINCT, "early-universe (Planck) H0 -- the "
                                     "early/late split IS the Hubble tension"),
    "cosmology.H0_early_normalized": (DISTINCT, "early-universe, normalised"),
    "geometry.H0_early": (DISTINCT, "early-universe duplicate"),
    "desi.H0": (DISTINCT, "DESI early-universe anchor"),
    "cosmology.H0_late_evolved": (MEMBER, "late-time H0"),
    "cosmology.H0_baseline_km_s_Mpc": (DISTINCT,
        "R4 ruling (2026-08-25): this is the SH0ES anchor (73.04) restated "
        "under a cosmology.* name, not a rival derivation. An anchor is data "
        "-- same ground as desi.S8 / planck.S8 / bounds.sum_m_nu_upper. "
        "Keeping it in the group manufactured self-agreement rows "
        "(73.04-vs-73.04) and a phantom conflict against the honest 71.55."),
    "cosmology.H0_local": (MEMBER, "canonical framework late-time prediction, "
                                   "71.55 -- absent from the curated group"),
    "cosmology.H0_ricci_variant": (DISTINCT,
        "documented alternative, per the pre-existing comment in this file's "
        "H0 group -- which describes exactly this 76.34 value (fitted 31-deg "
        "volume-mixing angle, 'not a derivation from G2 topology') but under "
        "the STALE name cosmology.H0_local; the parameter was later renamed "
        "and the canonical name now carries 71.55. The prior ruling stands; "
        "its 3.17-sigma FAIL is tracked by the validation layer."),
    "cosmology.H0_physical": (DISTINCT,
        "Appendix Z's terminal-ledger H0: (125/288)/24 * 400 * 10.1 = 73.06. "
        "DISTINCT on the same R4 grounds as H0_baseline_km_s_Mpc. Only the "
        "PRODUCT 400 * 10.1 = 4040 enters the arithmetic, neither factor has "
        "a source in the framework, and the product is what places the result "
        "on 73. A free constant that absorbs the answer is not an independent "
        "late-time derivation, and scoring it inside the comparison group "
        "would manufacture another self-agreement row. It IS still scored "
        "against SH0ES on its own parameter, so the claim stays visible. "
        "Whether either factor can be sourced is an author ruling; if one can "
        "be, this should be revisited as a MEMBER."),
    "cosmology.H0_tension_sigma": (INTERMEDIATE, "sigma, not an H0 value"),
    "cosmology.H0_tension_remaining_sigma": (INTERMEDIATE,
        "residual tension in sigmas, not a value of H0"),
    "geometry.H0_tension_ratio": (INTERMEDIATE,
        "late/early H0 ratio, dimensionless"),
    "cosmology.h0_unwinding_scale": (INTERMEDIATE, "model scale, not H0"),

    # -- S8: four registered values, one curated group member -------------
    "cosmology.s8_pm_predicted": (MEMBER, "friction-suppressed prediction"),
    "cosmology.S8_pred": (MEMBER, "alternate S8 prediction (0.8333)"),
    "geometry.S8": (MEMBER, "geometry-sector S8 (0.8333)"),
    "cosmology.S8_resolved": (MEMBER, "post-resolution S8 -- lands on the "
                                      "anchor almost exactly, which deserves "
                                      "scrutiny of its own"),
    "cosmology.s8_pm_baseline": (DISTINCT, "unsuppressed baseline, not a "
                                           "prediction of observed S8"),
    "cosmology.S8_baseline": (DISTINCT,
        "pre-suppression baseline, not a prediction of observed S8"),
    "desi.S8": (DISTINCT, "experimental anchor"),
    "planck.S8": (DISTINCT, "experimental anchor"),
    # Weak-lensing anchors. Same ground as desi.S8 / planck.S8: data, not
    # rival derivations. They exist as registry rows because the S8 tension
    # was being scored against the CMB anchor only -- s8_pm_predicted passes
    # Planck at 0.7 sigma while the framework's own text puts the KiDS
    # tension at ~2.7 sigma, and that number appeared in no scored row.
    "lensing.S8_kids1000": (DISTINCT,
        "KiDS-1000 experimental anchor (Heymans et al. 2021)"),
    "lensing.S8_des_y3": (DISTINCT,
        "DES Y3 experimental anchor (DES Collaboration 2022)"),
    "lensing.S8_hsc_y3": (DISTINCT,
        "HSC Y3 experimental anchor (Li et al. 2023)"),
    "cosmology.s8_pm_vs_lensing": (DISTINCT,
        "NOT a rival derivation -- it is numerically identical to "
        "cosmology.s8_pm_predicted, the same prediction scored against the "
        "weak-lensing anchor instead of the CMB one. Comparing the two "
        "inside the group would manufacture a 0-sigma self-agreement row of "
        "exactly the kind the R4 ruling struck out for "
        "cosmology.H0_baseline_km_s_Mpc. Its disagreement with the anchor "
        "is the S8 tension and is tracked by the validation layer "
        "(2.73 sigma TENSION)."),
    "cosmology.S8_tension_remaining_sigma": (INTERMEDIATE,
        "residual tension in sigmas, not a value of S8"),
    "cosmology.s8_tension_des": (INTERMEDIATE,
        "tension against the DES survey, in sigmas"),
    "cosmology.s8_tension_des_baseline": (INTERMEDIATE,
        "baseline DES tension, in sigmas"),
    "cosmology.s8_tension_kids": (INTERMEDIATE,
        "tension against the KiDS survey, in sigmas"),
    "cosmology.s8_tension_kids_baseline": (INTERMEDIATE,
        "baseline KiDS tension, in sigmas"),
    "cosmology.s8_tension_planck": (INTERMEDIATE,
        "tension against Planck, in sigmas"),
    "cosmology.s8_friction_beta_eff": (INTERMEDIATE, "friction coefficient"),
    "cosmology.s8_friction_kernel": (INTERMEDIATE, "friction kernel"),
    "cosmology.s8_friction_suppression_pct": (INTERMEDIATE, "percentage -- "
                                              "5.13 here against the 4.31 "
                                              "the growth-ODE branch uses"),
    "cosmology.s8_suppression_factor": (INTERMEDIATE,
        "multiplicative suppression factor, dimensionless"),
    "cosmology.s8_improvement_factor": (INTERMEDIATE,
        "how much the mechanism improves the tension, dimensionless"),
    "geometry.s8_viscosity_scale": (INTERMEDIATE, "model scale"),

    # -- theta_13: the framework's own failing derivation was omitted ------
    "neutrino.theta13_derived": (MEMBER,
        "9.594 deg, still registered as DERIVED with the stale 0.25-deg "
        "error band in its module docstring; the register corrects the "
        "band to 0.11 deg making this 9.31 sigma. A LIVE rival to the "
        "8.647 canonical branch until an author ruling retires it."),
    "particle.theta_13_rad": (DISTINCT,
        "same angle in RADIANS (0.1513 = 8.669 deg). The auditor compares "
        "raw numerics with no unit conversion, so grouping this with the "
        "degree-valued members manufactured a fake 98% conflict that masked "
        "the real 10.9% one. The degree entries carry the comparison; unit "
        "consistency between deg and rad forms belongs to the triple-track "
        "layer, not the shadow auditor."),
    "particle.eml_theta_13_rad": (DISTINCT,
        "EML cross-check of theta_13_rad -- radians, same reasoning"),
    "neutrino.sin_theta13_derived": (DISTINCT, "sine, not the angle"),
    "neutrino.theta13_sigma": (INTERMEDIATE,
        "deviation in sigmas, not the angle itself"),

    # -- remaining observables --------------------------------------------
    "cosmology.n_s_slow_roll": (MEMBER, "slow-roll n_s variant"),
    "higgs.m_higgs_pred": (DISTINCT,
        "documented stale-calibration artifact, NOT a rival: the Sprint "
        "T3 #4 block in higgs_mass.py records that Re(T)=9.865 was "
        "hand-inverted to hit 125.10 under v24.2 inputs, later input "
        "refinements detuned it to 120.62, and it is kept only for "
        "paper reproducibility. The canonical path is particle.m_h_GeV "
        "= 125.08 (0.9 sigma). An earlier draft here guessed a "
        "tree-level-vs-loops story; the documentation says otherwise."),
    "higgs.m_higgs_geometric": (DISTINCT,
        "documented failed pure-geometry leg (Re(T)=1.833 -> 504 GeV), "
        "per the Sprint T3 #4 disposition block in higgs_mass.py -- kept "
        "on the books per the falsified-candidates rule, not competing"),
    "higgs.m_higgs_bulk": (DISTINCT,
        "documented raw 26D pre-projection value (414 GeV), same Sprint "
        "T3 #4 block -- an intermediate of the chain, not a prediction"),
    "cosmology.planck_omega_dm_h2": (DISTINCT, "relic density, matched only "
                                               "by the crude m_h token"),
    "portals.alp_photon_coupling_gev_inv": (MEMBER, "ALP photon coupling"),
    "portals.alp_nucleon_coupling_gev_inv": (DISTINCT, "nucleon, not photon"),
    "bounds.sum_m_nu_upper": (DISTINCT, "experimental upper bound"),
    "spectral.m_nu_1": (DISTINCT, "individual mass eigenvalue, not the sum"),
    "spectral.m_nu_2": (DISTINCT, "individual mass eigenvalue"),
    "spectral.m_nu_3": (DISTINCT, "individual mass eigenvalue"),
    "neutrino.mass_sum": (MEMBER,
        "0.1012 eV -- the register 1.5 headline value, which had escaped "
        "token discovery (its name contains neither m_nu nor sum_m_nu). "
        "Disagrees with the discovered sums geometry.sum_m_nu = 0.0817 "
        "(the R5 canonical headline) and spectral.sum_m_nu = 0.0625 (the "
        "spectral cross-check, self-consistent after the R5 chain audit "
        "replaced a hardcoded m1 with the formula's own output) -- three "
        "registered values for one observable, the exact defect this "
        "ledger exists to surface."),
}


def discover_candidates(params):
    """Every registry parameter whose name matches an observable token.

    Deliberately over-collects: a candidate costs one disposition line, a
    missed candidate costs a contradiction nobody sees.
    """
    out = {}
    for observable, tokens in OBSERVABLE_TOKENS.items():
        hits = []
        for name, entry in params.items():
            value = entry.get("value") if isinstance(entry, dict) else entry
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                continue
            if any(tok in name.lower() for tok in tokens):
                hits.append(name)
        out[observable] = sorted(hits)
    return out


def audit_dispositions(params):
    """Candidates with no disposition, plus those explicitly UNTRIAGED.

    A non-empty result means the ledger has fallen behind the registry --
    exactly the drift that let the H0 and S8 contradictions hide.
    """
    declared = {m for members in OBSERVABLE_GROUPS.values() for m in members}
    undisposed = []
    untriaged = []
    for _observable, names in discover_candidates(params).items():
        for name in names:
            if name in declared:
                continue
            disposition = DISPOSITIONS.get(name)
            if disposition is None:
                undisposed.append(name)
            elif disposition[0] == UNTRIAGED:
                untriaged.append(name)
    return {"undisposed": sorted(set(undisposed)),
            "untriaged": sorted(set(untriaged))}


def effective_groups(params):
    """OBSERVABLE_GROUPS plus every candidate dispositioned MEMBER.

    This is what a conflict detector should actually check: the curated
    lists remain the declared core, and the ledger supplies what curation
    forgot.
    """
    groups = {k: list(v) for k, v in OBSERVABLE_GROUPS.items()}
    for observable, names in discover_candidates(params).items():
        bucket = groups.setdefault(observable, [])
        for name in names:
            disposition = DISPOSITIONS.get(name)
            if disposition and disposition[0] == MEMBER and name not in bucket:
                bucket.append(name)
    return groups

