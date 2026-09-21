"""What the framework may currently CLAIM about its geometry, generated.

WHY THIS EXISTS
===============
The corpus mentions G2 holonomy across 92 files (measured). On the adopted `g2_form_convention`
branch that claim is false: the framework's phi is a G2-structure for the SPLIT
real form G2*, whose induced metric has signature (4,3), so there is no
Riemannian G2-holonomy manifold behind it. On the `octonion_derived` branch the
same claim is true.

So "G2 holonomy" is not a sentence to find-and-replace. It is PATH-DEPENDENT,
and the only stable fix is to stop writing it by hand. This module generates
each claim from the LIVE fork state, extending the `b3_path.narration` pattern
across every geometric statement the framework makes, so switching a fork
rewrites the text instead of contradicting it.

WHAT IT COVERS, AND WHICH FORK DECIDES EACH
===========================================
    holonomy / real form / metric signature   g2_form_convention
    which metric construction is in force     metric_construction
    b_3, b_2, and their relation              b3_seed
    where n_gen comes from                    n_gen_source
    what chi_eff is                           UNRULED -- reported as a dichotomy

THE ONE THAT CANNOT BE NARRATED YET
===================================
chi_eff has three claimed derivations that agree only at b_3 = 24, where the two
b_3-dependent ones cross uniquely. There is no fork for it because the framework
has not ruled which route is meant, and inventing a default here would be
choosing the ruling. `chi_eff_claim()` therefore returns the dichotomy rather
than a value, and says so.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

__all__ = [
    "holonomy_claim",
    "metric_claim",
    "betti_claim",
    "generation_claim",
    "chi_eff_claim",
    "narrate",
    "forbidden_phrases",
]


def _resolve(fork_id: str, fallback: str) -> str:
    try:
        from metaphysica.simulations.core.variants import resolve

        return resolve(fork_id)
    except Exception:                      # fork absent / import cycle
        return fallback


def holonomy_claim(convention: Optional[str] = None) -> Dict[str, Any]:
    """What may be said about holonomy, on the branch actually in force."""
    convention = convention or _resolve("g2_form_convention", "all_plus_one")

    if convention == "octonion_derived":
        return {
            "fork": "g2_form_convention",
            "branch": convention,
            "real_form": "compact G2",
            "signature": (7, 0),
            "is_riemannian": True,
            "may_claim_g2_holonomy": True,
            "sentence": (
                "phi is a G2-structure for the COMPACT real form. Hitchin's "
                "cubic construction gives an induced metric of signature (7,0), "
                "so a Riemannian G2-holonomy manifold is available and Joyce's "
                "construction applies."
            ),
            "lambda2_14_is": "g2, the compact real form",
        }

    return {
        "fork": "g2_form_convention",
        "branch": convention,
        "real_form": "split G2* (G2^{2,14})",
        "signature": (4, 3),
        "is_riemannian": False,
        "may_claim_g2_holonomy": False,
        "sentence": (
            "phi is a G2-structure for the SPLIT real form G2*, not the compact "
            "one. Hitchin's cubic construction gives an induced metric of "
            "signature (4,3), which is not Riemannian, so there is no "
            "G2-HOLONOMY manifold behind it and Joyce's construction -- which "
            "needs the compact form -- does not apply to this phi. The "
            "stabiliser is still 14-dimensional; it is g2*, whose maximal "
            "compact SU(2)xSU(2) has dimension 6."
        ),
        "lambda2_14_is": (
            "g2*, the SPLIT real form -- the dimensions 7 + 14 and 1 + 7 + 27 "
            "are correct on both branches, but the 14 is not compact g2 here"
        ),
    }


def metric_claim(construction: Optional[str] = None) -> Dict[str, Any]:
    """Which object the word 'metric' currently refers to."""
    construction = construction or _resolve("metric_construction",
                                            "quadratic_contraction")
    if construction == "hitchin_cubic":
        return {
            "fork": "metric_construction",
            "branch": construction,
            "sentence": (
                "the metric is Hitchin's cubic construction, g = B/|det B|^(1/9) "
                "with B cubic in phi. It depends on the GL(7) orbit and so "
                "reports the real form honestly."
            ),
        }
    return {
        "fork": "metric_construction",
        "branch": construction,
        "sentence": (
            "the metric in force is the QUADRATIC contraction "
            "phi_iab phi_jab / 6. It returns 1.0 * I_7 for both real forms, so "
            "it cannot certify any orientation as Riemannian and must not be "
            "cited as evidence that one is. It is a consistency identity, not a "
            "metric derivation; Hitchin's construction is cubic."
        ),
    }


def betti_claim(seed: Optional[str] = None) -> Dict[str, Any]:
    """b_3, b_2 and the relation between them, on the seed in force."""
    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path,
        seed_values,
    )

    seed = seed or resolve_path()
    b3, b2 = seed_values(seed)
    on_family = (b3 == 7 + 3 * b2)

    if on_family:
        relation = (
            "b_3 = 7 + 3 b_2 holds, so b_2 and b_3 are NOT independent -- the "
            "construction carries ONE topological input, not two."
        )
    else:
        relation = (
            "b_3 = 7 + 3 b_2 FAILS here (7 + 3*%d = %d, not %d), so this pair "
            "is not on the Joyce-reachable family at all. That is an "
            "independent exclusion, alongside b_3 = 7 (mod 12) and the TCS "
            "range 71-155." % (b2, 7 + 3 * b2, b3)
        )

    return {
        "fork": "b3_seed",
        "branch": seed,
        "b3": b3,
        "b2": b2,
        "on_reachable_family": on_family,
        "sentence": "b_3 = %d and b_2 = %d. %s" % (b3, b2, relation),
    }


def generation_claim(source: Optional[str] = None,
                     seed: Optional[str] = None) -> Dict[str, Any]:
    """Where three generations come from, and what that rests on."""
    from metaphysica.simulations.PM.geometry.b3_path import (
        n_gen_report,
        resolve_path,
    )

    seed = seed or resolve_path()
    report = n_gen_report(seed)
    declared = source or report["declared_source"]

    if declared == "b2_over_faces":
        sentence = (
            "n_gen = b_2 / 4 = %s. Measured over the live enumeration this is "
            "not a ratio but a RECOVERY: n_families = 4 x n_singular at every "
            "admissible assignment, so b_2/4 returns the number of SINGULAR "
            "INVOLUTIONS. Those are independent over F_2 wherever three are "
            "singular, so they form a basis of Gamma and cannot exceed "
            "rank(Gamma) = 3. Three generations is the RANK of the diagonal "
            "stabiliser of phi, and it is the maximum this construction admits."
            % report["n_gen"]
        )
        caveat = (
            "the chain crosses type boundaries -- group rank, group elements, "
            "orbits, cohomology classes, generations -- and each arrow is a "
            "measured correspondence, not an identification. The weakest is "
            "b_2/n_faces = n_gen, which is this fork."
        )
    else:
        from metaphysica.simulations.PM.geometry.b3_path import seed_values

        b3, b2 = seed_values(seed)
        on_family = (b3 == 7 + 3 * b2)
        where = (
            "and b_3 = %d IS on that family, so no generation count is "
            "available here at all" % b3
            if on_family else
            "b_3 = %d is not on that family, so this route returns %s only "
            "because the seed sits off it" % (b3, report["n_gen"])
        )
        sentence = (
            "n_gen = b_3 / 8 = %s. On the Joyce-reachable family b_3 is ODD at "
            "every profile and 8 divides no odd number, so this route yields "
            "an integer NOWHERE on the family -- not merely a wrong value at "
            "one point. Here %s." % (report["n_gen"], where)
        )
        caveat = (
            "this branch is incompatible with the Joyce construction entirely; "
            "it is retained so the alternative can be run and costed."
        )

    return {
        "fork": "n_gen_source",
        "branch": declared,
        "n_gen": report["n_gen"],
        "holds": report["equals_three"],
        "sentence": sentence,
        "caveat": caveat,
    }


def chi_eff_claim() -> Dict[str, Any]:
    """chi_eff has no ruled derivation. Report the dichotomy, invent nothing."""
    return {
        "fork": None,
        "branch": "UNRULED",
        "sentence": (
            "chi_eff = 144 has THREE claimed derivations -- 2(h11-h21+h31), "
            "b_3^2/4 and 6 b_3 -- which agree only at b_3 = 24. The two "
            "b_3-dependent ones cross at exactly one point, and it is the "
            "adopted seed, so their agreement is the definition of that "
            "crossing rather than evidence for it. The Hodge-number route is "
            "a Calabi-Yau THREEFOLD Euler characteristic and a Joyce orbifold "
            "has no h21 or h31."
        ),
        "dichotomy": (
            "chi_eff is either a CONSTANT independent of the seed, in which "
            "case n_gen = chi_eff/48 carries no topological content; or it is "
            "SEED-DEPENDENT, in which case it is not 144 on the 43 path. The "
            "framework currently wants both."
        ),
        "may_claim_a_derivation": False,
        "ruling_required": True,
    }


def forbidden_phrases() -> Dict[str, str]:
    """Phrases that are FALSE on the branch currently in force, with the reason.

    Used by the corpus ratchet. Empty on a branch where the claims are true,
    which is the point: the list is generated, not maintained.
    """
    out: Dict[str, str] = {}
    holonomy = holonomy_claim()
    if not holonomy["may_claim_g2_holonomy"]:
        reason = (
            "phi is the SPLIT real form on this branch; its induced metric has "
            "signature (4,3) and no Riemannian G2 holonomy exists"
        )
        for phrase in ("G2 holonomy", "G2-holonomy", "holonomy group G2",
                       "Riemannian G2 manifold"):
            out[phrase] = reason

    chi = chi_eff_claim()
    if not chi["may_claim_a_derivation"]:
        out["chi_eff is derived"] = (
            "chi_eff has three competing derivations and no ruling; see the "
            "dichotomy"
        )
    return out


def narrate(**overrides) -> Dict[str, Any]:
    """Every geometric claim, generated from the live fork state."""
    claims = {
        "holonomy": holonomy_claim(overrides.get("g2_form_convention")),
        "metric": metric_claim(overrides.get("metric_construction")),
        "betti": betti_claim(overrides.get("b3_seed")),
        "generations": generation_claim(overrides.get("n_gen_source"),
                                        overrides.get("b3_seed")),
        "chi_eff": chi_eff_claim(),
    }
    return {
        "claims": claims,
        "paragraph": " ".join(c["sentence"] for c in claims.values()),
        "forbidden_phrases": forbidden_phrases(),
        "note": (
            "generated from the live forks. Switching a fork rewrites these "
            "sentences; it does not leave them contradicting the code."
        ),
    }
