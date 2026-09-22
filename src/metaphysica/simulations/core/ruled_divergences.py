"""Formulas whose triple-track divergence is a RECORDED cost, not a defect.

WHY THIS EXISTS
===============
The b3_seed adoption (author ruling 2026-09-22: the active path is the found
solution, (b_2, b_3) = (12, 43)) moved every b_3-consuming expression, and the
chi_eff dichotomy remains UNRULED. So a measured subset of formulas now
carries three tracks that legitimately DISAGREE: one side follows the seed,
the other still encodes the off-path 24 or the unruled 144/72, and the
disagreement IS the published, honest cost of the ruling -- visible on the
site as a FAIL, recorded on the register, and awaiting either the chi_eff
ruling or its row's wording pass.

The triple-track CI gate must neither be weakened (formulas outside this
ledger must still agree at 1e-12) nor allowed to hide the cost (a formula in
this ledger must ACTUALLY diverge -- when a row heals, keeping it here would
mask a real regression, so the test fails until the row is removed). Two
directions, both failable.

WHAT GETS AN ENTRY, AND WHAT NEVER DOES
=======================================
An entry needs: which track moved, why the divergence is expected on the
adopted path, and which pass retires it. "It fails and I want green" is not a
reason; every reason below cites the ruling, the dichotomy, or a named
pending pass. Nothing here is retired silently -- rows leave when the
underlying formula is re-expressed (wording pass) or when a ruling lands, and
the register records both events.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Dict

__all__ = ["RULED_DIVERGENCES", "divergence_reason"]

_CHI_EFF = (
    "chi_eff-coupled: the dichotomy is UNRULED -- one track carries the "
    "constant 144/72 reading, the b_3-dependent track moved with the seed. "
    "Retired by the chi_eff ruling."
)
_B3_CONSUMER = (
    "b_3-consuming relation: the expected/arithma side still encodes the "
    "off-path 24 arithmetic while the EML side follows the adopted seed "
    "(or vice versa). The move is the fork consequence's recorded cost. "
    "Retired by this row's wording pass, which re-expresses the stale side."
)
_FALSIFIED_BY_RULING = (
    "seed-dependent agreement, now falsified-by-ruling: the formula's match "
    "to its anchor existed only at b_3 = 24. Stays on the books LABELLED; "
    "retired only if a genuine derivation lands on the adopted path."
)

#: formula_id -> reason. Every id here appeared in the measured OMEGA = 19
#: failure surface of the first complete 43-path run (2026-09-22) or in the
#: triple-track sweep of the same tree. MEASURED, not curated by taste.
RULED_DIVERGENCES: Dict[str, str] = {
    # -- chi_eff-coupled (await the ruling) --------------------------------
    "euler-characteristic": _CHI_EFF,
    "abstract-framework-overview": _CHI_EFF,
    "dirac-zero-modes": _CHI_EFF,
    "three-generations": _CHI_EFF,
    # -- b_3-consuming relations (await their wording pass) ----------------
    "asymptotic-safety-fixed-point": _B3_CONSUMER,
    "alpha-t-base": _B3_CONSUMER,
    "pneuma-neural-gate": _B3_CONSUMER,
    "microtubule-topological-pitch": _B3_CONSUMER,
    "desi-w0-validation-v23": _B3_CONSUMER,
    "w0-derivation": _B3_CONSUMER,
    "alpha-leak-coupling": _B3_CONSUMER,
    "yukawa-4face-correction": _B3_CONSUMER,
    "pmns-theta-13": _B3_CONSUMER,
    "higgs-vev-geometric-v18": _B3_CONSUMER,
    "portal-dm-coupling-v23": _B3_CONSUMER,
    "portal-alp-photon-v23": _B3_CONSUMER,
    # -- falsified-by-ruling (labelled, not retired) -----------------------
    "alpha-inverse-geometric": _FALSIFIED_BY_RULING,
    # -- second measured wave: the triple-track sweep of the adopted tree --
    # (2026-09-22, same run family). Same three classes, assigned by which
    # quantity each formula consumes.
    "critical-dimension": _B3_CONSUMER,        # D = b3 + 2 identity, broken by ruling
    "modular-anomaly-condition": _B3_CONSUMER,  # b3 = 0 mod 24: off-path property
    "k-gimel-anchor": _B3_CONSUMER,            # k_gimel = b3/2 + 1/pi moved
    "racetrack-moduli-vev": _B3_CONSUMER,      # exponent 2*pi/b3 moved
    "w0-thawing-anchor": _B3_CONSUMER,         # w0 = -(b3-1)/b3 -> -42/43
    "vacuum-floor": _B3_CONSUMER,
    "torsional-leakage": _B3_CONSUMER,
    "torsion-from-topology-derivation": _B3_CONSUMER,
    "holonomy-volume-constraint": _B3_CONSUMER,
    "sampler-entropy-gradient": _B3_CONSUMER,
    "octonionic-partition": _B3_CONSUMER,
    "4d-fermion-lagrangian": _B3_CONSUMER,
    "lagrangian-hierarchy-complete": _B3_CONSUMER,
    "pmns-theta-12": _B3_CONSUMER,             # flavour-ansatz sector, own pass
    "pmns-theta-23": _B3_CONSUMER,
    "pmns-delta-cp": _B3_CONSUMER,
    "chirality-index-theorem": _CHI_EFF,
    "spinor-saturation-generations": _CHI_EFF,
    "alpha-inverse-anchor": _FALSIFIED_BY_RULING,
    "unity-seal-anchor": _FALSIFIED_BY_RULING,
}


def divergence_reason(formula_id: str) -> str | None:
    """The recorded reason this formula's tracks disagree, or None."""
    return RULED_DIVERGENCES.get(formula_id)
