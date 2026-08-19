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
    #   shadow with the canonical prediction s8_pm_predicted = 0.803. Excluded
    #   as a documented_alternative per T1.6 honest-accounting precedent.
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
