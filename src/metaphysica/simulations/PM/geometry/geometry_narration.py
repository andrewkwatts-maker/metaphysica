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
chi_eff's three historical routes agree only at b_3 = 24. D-009 found a reading
that holds on the whole family -- twice the Euler characteristics of the Kummer
K3 surfaces transverse to the singular involutions, 48 n -- but adopting it is
the author's ruling, and inventing a default here would be making it.
`chi_eff_claim()` therefore reports the candidate and the old dichotomy, not a
derivation.

FRAGMENTS (the wording pass's API)
==================================
`fragments(register)` returns the phrases prose uses for the geometry -- the
Betti pair and sequence, the construction, the generation route, the chi_eff
label -- generated from the live seed in plain, HTML or LaTeX. `render(template)`
fills a template from them and raises on an unknown key. A sentence written
through them follows the seed when it is flipped; a typed "(12, 43)" would sit
beside the values and contradict them.

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
    "fork_reads_degraded",
    "fragments",
    "render",
    "FRAGMENT_KEYS",
]


#: Set by `_resolve` whenever it had to fall back, and read by
#: `narrate`/`forbidden_phrases` so a degraded read is REPORTED rather than
#: presented as a live one.
_FALLBACKS_USED: Dict[str, str] = {}


def _resolve(fork_id: str, fallback: str) -> str:
    """The live branch of `fork_id`, or a LOUD failure.

    WHAT THIS USED TO DO, AND WHY IT WAS THE WRONG SHAPE
    ====================================================
    It caught bare `Exception` and returned `fallback`. That made the module
    built to stop silent defaults contain one: `variants.resolve` raises
    KeyError for a fork that is not declared and ValueError for an option that
    does not exist, and both were swallowed. A renamed or deleted fork would
    have left this module narrating `all_plus_one` while its own docstring
    promised it was reading the live fork -- the exact failure the narration
    was written to prevent, in the narration.

    Now only ImportError is tolerated, because that is the one condition the
    fallback was ever meant for: `variants` importing this module back during
    a partial import. Every other failure propagates with the fork named.

    Even the tolerated case is not silent: it is recorded in `_FALLBACKS_USED`
    and surfaced by `narrate()` as `fork_reads_degraded`, so a consumer can
    tell a live read from a fallback instead of having to trust that there was
    no difference.
    """
    try:
        from metaphysica.simulations.core.variants import resolve
    except ImportError as exc:             # import cycle: the one real case
        _FALLBACKS_USED[fork_id] = (
            "variants could not be imported (%s); narrated the declared "
            "fallback %r instead of a live read" % (exc, fallback)
        )
        return fallback

    branch = resolve(fork_id)
    _FALLBACKS_USED.pop(fork_id, None)
    return branch


def fork_reads_degraded() -> Dict[str, str]:
    """Forks whose branch came from a fallback rather than a live read.

    Empty is the healthy state. Non-empty means some sentence below was
    generated from a declared default, and the caller is entitled to know which.
    """
    return dict(_FALLBACKS_USED)


def holonomy_claim(convention: Optional[str] = None) -> Dict[str, Any]:
    """What may be said about holonomy, on the branch actually in force."""
    convention = convention or _resolve("g2_form_convention",
                                        "octonion_derived")

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


def layperson_narration(seed: Optional[str] = None) -> Dict[str, Any]:
    """The plain-register story of the topology, generated from the live fork.

    The site's reading toggle (pm-layperson-toggle.js) demands a plain
    statement for every derivation, as an audit instrument: a derivation whose
    plain statement cannot be written without hand-waving does not exist. This
    is that statement for the topological layer, with every number read from
    the fork rather than typed, so a seed switch rewrites the story instead of
    leaving it contradicting the code.

    Three corrections against the circulated draft are baked in, because each
    would teach a wrong fact: Betti numbers COUNT, they do not measure area
    (area is metric data; this layer is metric-free); the seams are
    3-DIMENSIONAL tori, not lines; and the generation count enters as the
    RANK of the folding symmetry, not as a dial anyone sets.
    """
    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path,
        seed_values,
    )

    seed = seed or resolve_path()
    b3, b2 = seed_values(seed)
    on_family = (b3 == 7 + 3 * b2)

    story = {
        "hole_counter": (
            "Think of Betti numbers as a hole counter for shapes. b_1 counts "
            "loops a rubber band can wrap without slipping off (a coffee "
            "mug's handle has one); b_2 counts trapped 2D bubbles; b_3 counts "
            "trapped 3D chambers. They are COUNTS of independent holes -- "
            "never lengths or areas, which is why no ruler is needed to fix "
            "them."
        ),
        "the_base": (
            "Start with a flat 7-dimensional torus. Of its 35 possible 3D "
            "direction-combinations, folding by the symmetry group leaves "
            "exactly 7 global 3D hallways intact. That is the constant 7."
        ),
        "the_seams": (
            "The folding pinches the space along 3-dimensional seams -- "
            "creases, each one a small 3D torus. Counting the independent "
            "families of seams gives b_2 = %d: each repaired seam family "
            "traps exactly one new 2D bubble." % b2
        ),
        "the_repairs": (
            "Physics cannot live on a crease, so each seam is repaired by "
            "gluing in a smooth patch (an Eguchi-Hanson space). Every repair "
            "spawns exactly 3 new independent 3D chambers along its seam."
        ),
        "the_total": (
            "So the chamber count is locked by an assembly line: "
            "b_3 = 7 + 3 x b_2 = 7 + 3 x %d = %d. Seven global hallways plus "
            "%d repair-generated chambers." % (b2, 7 + 3 * b2, 3 * b2)
            if on_family else
            "On this branch b_3 = %d and b_2 = %d, and the assembly-line "
            "relation b_3 = 7 + 3 b_2 FAILS (it would give %d) -- which is "
            "one of the reasons this branch is off the constructible family."
            % (b3, b2, 7 + 3 * b2)
        ),
        "the_generations": (
            "Why three generations of particles? The folding symmetry has "
            "rank 3 -- three independent folds. Each fold that pinches the "
            "space contributes one family of seams, and counting seams "
            "recovers the same three. The number of generations is the rank "
            "of the folding, not a dial anyone set."
        ),
    }

    return {
        "fork": "b3_seed",
        "branch": seed,
        "b3": b3,
        "b2": b2,
        "on_reachable_family": on_family,
        "story": story,
        "paragraph": " ".join(story.values()),
        "register": "layperson",
        "corrections_applied": (
            "counts-not-areas; seams are 3D tori, not lines; generations "
            "enter as the rank of the folding symmetry"
        ),
    }


#: The ruled reading of chi_eff -- the `chi_eff_route` fork's source.
#: RULED 2026-10-01 by the author (D-015): the K3 reading of D-009. The other
#: routes stay switchable through METAPHYSICA_VARIANT_CHI_EFF_ROUTE.
CHI_EFF_READING = "k3_reading"


def chi_eff_claim(branch: Optional[str] = None) -> Dict[str, Any]:
    """What may be said about chi_eff, on the branch in force.

    On the adopted `k3_reading` branch chi_eff is DERIVED: twice the Euler
    characteristics of the Kummer K3 surfaces transverse to the n singular
    involutions (one per shadow), 48 n -- 144 at n = 3 (D-009, ruled D-015).
    The other branches narrate what they are: `unruled` the old dichotomy,
    `constant_144` and `seed_dependent` the routes D-009 tested.
    """
    branch = branch or _resolve("chi_eff_route", CHI_EFF_READING)
    if branch == "k3_reading":
        from metaphysica.simulations.PM.geometry.b3_path import n_gen_report

        n = n_gen_report()["n_gen"]
        return {
            "fork": "chi_eff_route",
            "branch": "k3_reading",
            "value": 48 * n,
            "sentence": (
                "chi_eff = 2 x sum over the n singular involutions of "
                "chi(K3) = 48 n = %g: each singular involution has a Kummer "
                "K3 surface transverse to its fixed three-tori (chi = 24), "
                "counted once per shadow (D-009; ruled D-015). It is an index "
                "of those surfaces, NOT the Euler characteristic of Y_7, "
                "which is 0. n_gen = chi_eff/48 = n restates the ruled "
                "generation route b_2/4; it is not a second derivation, and "
                "it is not an index theorem for chirality, which stays open."
                % (48 * n)
            ),
            "dichotomy": (
                "The old dichotomy -- chi_eff a CONSTANT independent of the "
                "seed, or SEED-DEPENDENT -- is resolved: the K3 reading is "
                "SEED-DEPENDENT through n and equals 144 on the adopted point."
            ),
            "candidate": {
                "reading": "K3",
                "formula": "chi_eff = 2 * sum_sigma chi(K3_sigma) = 48 n",
                "decision": "D-009, ruled D-015",
                "module": "PM/geometry/kummer_index.py",
            },
            "may_claim_a_derivation": True,
            "ruling_required": False,
        }
    return {
        "fork": "chi_eff_route",
        "branch": "UNRULED" if branch == "unruled" else branch,
        "sentence": (
            "chi_eff = 144 is an effective index, not the Euler "
            "characteristic of Y_7, which is 0 for every closed "
            "odd-dimensional manifold. Its three historical routes -- "
            "2(h11-h21+h31), b_3^2/4 and 6 b_3 -- agree only at the off-path "
            "seed b_3 = 24: a Joyce orbifold has no h21 or h31, b_3^2/4 is "
            "not an integer at odd b_3, and 6 b_3 is 258 at b_3 = 43. One "
            "reading survives on the whole family (D-009, unruled): chi_eff "
            "= 2 x sum over the n singular involutions of chi(K3) = 48 n, "
            "the Kummer K3 surfaces transverse to the singular loci counted "
            "once per shadow."
        ),
        "dichotomy": (
            "The old dichotomy: chi_eff is either a CONSTANT independent of "
            "the seed, in which case n_gen = chi_eff/48 carries no "
            "topological content; or it is SEED-DEPENDENT, in which case it "
            "must follow the seed. The K3 reading is SEED-DEPENDENT through "
            "n and equals 144 on the adopted point, so it resolves the "
            "dichotomy if the author adopts it -- and then n_gen = "
            "chi_eff/48 = n restates the ruled route rather than adding a "
            "second derivation."
        ),
        "candidate": {
            "reading": "K3",
            "formula": "chi_eff = 2 * sum_sigma chi(K3_sigma) = 48 n",
            "decision": "D-009, ruled D-015 (adopted branch: k3_reading)",
            "module": "PM/geometry/kummer_index.py",
        },
        "may_claim_a_derivation": False,
        "ruling_required": branch == "unruled",
    }


# ---------------------------------------------------------------- fragments
#: Keys every register provides. `render` refuses any other key, so a typo in
#: a template fails loudly instead of printing a literal brace.
FRAGMENT_KEYS = (
    "b2", "b3", "n_gen", "manifold", "construction", "structure",
    "betti_pair", "betti_sequence", "b3_split", "n_gen_route", "chi_eff",
    "chi_y7", "off_path_seed", "calibrated_at_24", "bulk",
)

_REGISTERS = ("plain", "html", "latex")


def fragments(register: str = "plain",
              seed: Optional[str] = None) -> Dict[str, str]:
    """The phrases prose uses for the geometry, generated from the live seed.

    Lane-0 API for the wording pass: a sentence written as
    ``render("Y_7 has {betti_pair}.")`` follows the seed when it is flipped,
    where a typed "(12, 43)" would silently contradict the values printed
    beside it. Holonomy is deliberately absent: what may be said about it
    depends on the real-form fork, and `holonomy_claim()` owns that.
    """
    if register not in _REGISTERS:
        raise ValueError("register %r is not one of %s" % (register,
                                                          _REGISTERS))
    from metaphysica.simulations.PM.geometry.b3_path import (
        n_gen_report,
        resolve_path,
        seed_values,
    )

    seed = seed or resolve_path()
    b3, b2 = seed_values(seed)
    n_gen = n_gen_report(seed)["n_gen"]
    n_txt = "%g" % n_gen
    seq = (1, 0, b2, b3, b3, b2, 0, 1)
    seq_txt = "(%s)" % ", ".join(str(x) for x in seq)
    k3 = chi_eff_claim()["may_claim_a_derivation"]
    chi_val = "%g" % (48 * n_gen)

    if register == "html":
        return {
            "b2": str(b2), "b3": str(b3), "n_gen": n_txt,
            "manifold": "Y<sub>7</sub>",
            "construction": ("Joyce&rsquo;s resolution of "
                             "T<sup>7</sup>/(&#8484;/2)<sup>3</sup>"),
            "structure": ("a compact 7-manifold with a torsion-free "
                          "G<sub>2</sub>-structure"),
            "betti_pair": ("(b<sub>2</sub>, b<sub>3</sub>) = (%d, %d)"
                           % (b2, b3)),
            "betti_sequence": seq_txt,
            "b3_split": ("b<sub>3</sub> = 7 + 3b<sub>2</sub> = 7 + %d"
                         % (3 * b2)),
            "n_gen_route": ("n<sub>gen</sub> = b<sub>2</sub>/4 = %s, the "
                            "number of singular involutions" % n_txt),
            "chi_eff": (("the effective index &chi;<sub>eff</sub> = 48n = "
                         "%s (the K3 reading; the Euler characteristic of "
                         "Y<sub>7</sub> is 0)" % chi_val) if k3 else
                        ("the effective index &chi;<sub>eff</sub> (an open "
                         "ruling; the Euler characteristic of Y<sub>7</sub> "
                         "is 0)")),
            "chi_y7": "&chi;(Y<sub>7</sub>) = 0",
            "off_path_seed": "the off-path seed b<sub>3</sub> = 24",
            "calibrated_at_24": ("calibrated at the off-path seed "
                                 "b<sub>3</sub> = 24"),
            "bulk": ("a 26D bulk of signature (24,2): 24 space directions "
                     "and 2 times, one per shadow"),
        }
    if register == "latex":
        return {
            "b2": str(b2), "b3": str(b3), "n_gen": n_txt,
            "manifold": r"$Y_7$",
            "construction": r"Joyce's resolution of $T^7/(\mathbb{Z}_2)^3$",
            "structure": (r"a compact 7-manifold with a torsion-free "
                          r"$G_2$-structure"),
            "betti_pair": r"$(b_2, b_3) = (%d, %d)$" % (b2, b3),
            "betti_sequence": r"$%s$" % seq_txt,
            "b3_split": r"$b_3 = 7 + 3b_2 = 7 + %d$" % (3 * b2),
            "n_gen_route": (r"$n_{\rm gen} = b_2/4 = %s$, the number of "
                            r"singular involutions" % n_txt),
            "chi_eff": ((r"the effective index $\chi_{\rm eff} = 48n = %s$ "
                         r"(the K3 reading; the Euler characteristic of $Y_7$ "
                         r"is 0)" % chi_val) if k3 else
                        (r"the effective index $\chi_{\rm eff}$ (an open "
                         r"ruling; the Euler characteristic of $Y_7$ is 0)")),
            "chi_y7": r"$\chi(Y_7) = 0$",
            "off_path_seed": r"the off-path seed $b_3 = 24$",
            "calibrated_at_24": r"calibrated at the off-path seed $b_3 = 24$",
            "bulk": (r"a 26D bulk of signature $(24,2)$: 24 space directions "
                     r"and 2 times, one per shadow"),
        }
    return {
        "b2": str(b2), "b3": str(b3), "n_gen": n_txt,
        "manifold": "Y_7",
        "construction": "Joyce's resolution of T^7/(Z/2)^3",
        "structure": "a compact 7-manifold with a torsion-free G2-structure",
        "betti_pair": "(b_2, b_3) = (%d, %d)" % (b2, b3),
        "betti_sequence": seq_txt,
        "b3_split": "b_3 = 7 + 3 b_2 = 7 + %d" % (3 * b2),
        "n_gen_route": ("n_gen = b_2/4 = %s, the number of singular "
                        "involutions" % n_txt),
        "chi_eff": (("the effective index chi_eff = 48n = %s (the K3 "
                     "reading; the Euler characteristic of Y_7 is 0)"
                     % chi_val) if k3 else
                    ("the effective index chi_eff (an open ruling; the Euler "
                     "characteristic of Y_7 is 0)")),
        "chi_y7": "chi(Y_7) = 0",
        "off_path_seed": "the off-path seed b_3 = 24",
        "calibrated_at_24": "calibrated at the off-path seed b_3 = 24",
        "bulk": ("a 26D bulk of signature (24,2): 24 space directions and "
                 "2 times, one per shadow"),
    }


class _Strict(dict):
    def __missing__(self, key):
        raise KeyError(
            "unknown fragment {%s}; available: %s"
            % (key, ", ".join(FRAGMENT_KEYS)))


def render(template: str, register: str = "plain",
           seed: Optional[str] = None) -> str:
    """Fill `template`'s {keys} from `fragments`; an unknown key raises."""
    return template.format_map(_Strict(fragments(register, seed)))


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
    degraded = fork_reads_degraded()
    return {
        "claims": claims,
        "paragraph": " ".join(c["sentence"] for c in claims.values()),
        "forbidden_phrases": forbidden_phrases(),
        "fork_reads_degraded": degraded,
        "all_reads_were_live": not degraded,
        "note": (
            "generated from the live forks. Switching a fork rewrites these "
            "sentences; it does not leave them contradicting the code."
            if not degraded else
            "WARNING: %d fork read(s) fell back to a declared default rather "
            "than reading the live registry, so the sentences above are not "
            "guaranteed to describe the branch in force: %s"
            % (len(degraded), degraded)
        ),
    }
