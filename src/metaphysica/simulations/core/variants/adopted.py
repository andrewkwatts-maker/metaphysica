"""Readers of each fork's currently adopted option, read live from its source.

Split out of the former single-file variants.py; text moved verbatim.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from .model import SourceUnmeasurable


def _re_t_adoption_adopted() -> str:
    """Structural read, no restated numerals: the module's fallback branch
    returns its declared RE_T_CALIBRATED constant, and computed_vacuum can
    only arrive via the fork override -- so the source-adopted branch is the
    calibrated one exactly while that fallback exists. Importing the constant
    verifies the source is intact without comparing against a magic copy."""
    from metaphysica.simulations.PM.cosmology import baryon_asymmetry

    assert hasattr(baryon_asymmetry, "RE_T_CALIBRATED")
    return "calibrated"


def _spectral_index_route_adopted() -> str:
    """Which n_s route the inflation source takes: the module's own constant."""
    from metaphysica.simulations.PM.cosmology.spectral_routes import (
        ADOPTED_ROUTE,
    )

    return ADOPTED_ROUTE


def _h0_route_adopted() -> str:
    """Which H0 route the registry takes: the late-time routes module's constant."""
    from metaphysica.simulations.PM.cosmology.late_time_routes import (
        ADOPTED_H0_ROUTE,
    )

    return ADOPTED_H0_ROUTE


def _dark_energy_mechanism_adopted() -> str:
    """Which w0 mechanism the source takes: the late-time routes module's constant."""
    from metaphysica.simulations.PM.cosmology.late_time_routes import (
        ADOPTED_DE_MECHANISM,
    )

    return ADOPTED_DE_MECHANISM


def _b3_seed_adopted() -> str:
    """ADOPTED seed_43_joyce by author ruling, 2026-09-22.

    The author directed that the active path match the found solution --
    (b_2, b_3) = (12, 43), selected by n_gen = rank(Gamma) = 3 out of the four
    enumerated candidates, with b_3 = 7 + 3 b_2 making the pair one input.
    seed_24 stays on the books as the labelled off-path branch: it remains
    runnable via METAPHYSICA_VARIANT_B3_SEED=seed_24, its costs stay recorded
    in the option's consequence field, and nothing is deleted.

    The chi_eff dichotomy is NOT decided by this ruling; the EML track stays
    pinned on it.
    """
    from metaphysica.simulations.PM.geometry.b3_path import PATHS

    assert "seed_24" in PATHS and "seed_43_joyce" in PATHS
    return "seed_43_joyce"


def _flavour_seed_coupling_adopted() -> str:
    """Behavioural read: which b_3 the flavour entry point actually resolves.

    follow_seed exactly while resolve_flavour_b3() returns the live seed's
    value; if the module reverts to its calibrated 24 while the seed says
    otherwise, this stops matching and the drift guard fires.
    """
    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path,
        seed_values,
    )
    from metaphysica.simulations.PM.particle.yukawa_derivation import (
        resolve_flavour_b3,
    )

    return ("follow_seed"
            if resolve_flavour_b3() == seed_values(resolve_path())[0]
            else "calibrated_24")


def _b3_origin_adopted() -> str:
    """input_24 exactly while the seed row's declared status says INPUT.

    Read from the registration source (run_all_simulations sets
    topology.elder_kads with source INPUT:B3_ORIGIN_OPEN under the 2026-09-14
    ruling); if a derivation ever lands and the status moves, this stops
    matching and the drift guard fires, which is the point.

    BRANCH-AWARE since 2026-09-22: on a Joyce-reachable seed the origin
    question is ANSWERED (b_2 is the A1 family count, b_3 = 7 + 3 b_2), so
    the adopted origin is derived_joyce_a1 and run_all registers the row
    DERIVED. On seed_24 nothing derives the seed and the 2026-09-14 INPUT
    ruling stands.
    """
    from metaphysica.simulations.PM.geometry.b3_path import PATHS, resolve_path

    return ("derived_joyce_a1"
            if PATHS[resolve_path()].get("reachable_by_joyce")
            else "input_24")


def _g2_form_adopted() -> str:
    """Read the live signs off G2_TRIPLES rather than restating them here."""
    from metaphysica.simulations.PM.geometry.g2_differential import G2_TRIPLES

    signs = [s for (_i, _j, _k, s) in G2_TRIPLES]
    return "all_plus_one" if all(s > 0 for s in signs) else "octonion_derived"


def _metric_construction_adopted() -> str:
    """Which construction the live dispatcher actually returns.

    A genuine read of behaviour, not a restated constant: build both candidate
    metrics and report which one ``metric_by_convention()`` matches. If the
    dispatcher's default is ever changed this moves with it, which is the whole
    point of a drift guard -- three forks in this file return a string literal
    and cannot detect their own source changing at all.
    """
    import numpy as np

    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )

    g2 = G2DifferentialGeometry()
    live = g2.metric_by_convention()
    if np.allclose(live, g2.compute_metric()):
        return "quadratic_contraction"
    try:
        if np.allclose(live, g2.compute_hitchin_metric()):
            return "hitchin_cubic"
    except ValueError:                     # unstable phi: no Hitchin metric
        pass
    return "quadratic_contraction"


def _twisted_norm_convention_adopted() -> str:
    """Which normalisation the live pairing actually applies.

    A behavioural read, following `_metric_construction_adopted` rather than
    the three forks in this file that return a string literal and so cannot
    detect their own source changing: build one family's twisted entry at a
    known orbit size and see whether the orbit factor is present. If
    metric_pairing's default moves, this moves with it.
    """
    import sympy as sp

    from metaphysica.simulations.PM.geometry.metric_pairing import (
        _resolve_orbit_convention,
        twisted_block_entry,
    )

    probe_orbit = 4
    live = twisted_block_entry(probe_orbit, _resolve_orbit_convention())
    averaged = twisted_block_entry(probe_orbit, "orbit_average")
    return ("orbit_average" if sp.simplify(live - averaged) == 0
            else "orbit_sum")


def _chi_eff_route_adopted() -> str:
    """Whether the framework is still refusing to name a chi_eff derivation.

    RULED 2026-10-01 (D-015): the source is `CHI_EFF_READING` in the
    narration, and the narration's claim on that branch must agree with it --
    a derivation is claimable exactly on `k3_reading`. A disagreement means the
    declaration and the narration have diverged, and one of them is wrong.
    """
    from metaphysica.simulations.PM.geometry.geometry_narration import (
        CHI_EFF_READING,
        chi_eff_claim,
    )

    claim = chi_eff_claim(CHI_EFF_READING)
    if claim["may_claim_a_derivation"] != (CHI_EFF_READING == "k3_reading"):
        raise RuntimeError(
            "chi_eff_claim on %r %s a derivation, which the fork's declared "
            "reading contradicts; the declaration and the narration have "
            "diverged and one of them is wrong"
            % (CHI_EFF_READING, "permits" if claim["may_claim_a_derivation"]
               else "refuses")
        )
    return CHI_EFF_READING


def _bulk_signature_adopted() -> str:
    """Which signature CANON["bulk"] actually states.

    The trailing fallback here used to be `return "24_2"` -- the option this
    fork declares adopted -- reached both when CANON carried no "form" key at
    all and when it carried a signature no option claims. So a bulk rewritten
    to an undeclared signature (the withdrawn (24,1) and 27D readings among
    them) reported "no drift", which is the one thing this reader exists to
    rule out. Same shape as `_dark_energy_betti_adopted`, found by the same
    sweep on 2026-09-26.
    """
    from metaphysica.simulations.core.canonical_values import CANON

    try:
        form = CANON["bulk"]["form"]
    except KeyError as exc:
        raise SourceUnmeasurable(
            f"CANON['bulk'] states no signature: {exc}"
        ) from exc
    for option, token in (("26_2", "(26,2)"), ("25_1", "(25,1)"), ("24_2", "(24,2)")):
        if token in form:
            return option
    raise SourceUnmeasurable(
        f"CANON['bulk']['form'] = {form!r} names no declared option; "
        f"declared: ['26_2', '25_1', '24_2']"
    )



#: n -> option id for the dark-energy Betti fork. Declared once, so the
#: reader cannot invent a mapping and the test can assert over the same table.
_DE_BETTI_BY_N = {
    24: "b3_24", 12: "bridges_12", 8: "octonion_8",
    6: "chi_over_b3_6", 4: "b2_4", 3: "ngen_3",
}


def _dark_energy_betti_adopted() -> str:
    """Which integer n currently sets w0 = -(n-1)/n.

    Measured, not declared: n = 1/(1 + w0), so the live value of w0 reports
    which option is in force and a silent change to the derivation cannot
    leave this fork claiming the wrong one.

    THAT PROMISE USED TO BE FALSE, in three ways at once. The body caught
    bare Exception and returned the literal "b3_24"; a w0 of None or <= -1
    returned the same literal; and an n outside the mapping returned it via
    a `.get(n, "b3_24")` default. Since "b3_24" is also the DECLARED adopted
    option, all three failure paths confirmed the declaration -- and the
    ordinary case is a failure path, because `cosmology.w0_derived` is not in
    the registry until a sim run populates it, so the except branch fired and
    nothing was ever measured. A drift detector that answers "no drift"
    whenever it cannot see is worse than none, because `describe()`
    publishes its verdict.

    Now: it measures when it can, and says it cannot when it cannot. The
    caller distinguishes the two because unmeasurable RAISES rather than
    returning an option id -- the same discipline
    `test_silent_fork_defaults.py` imposed on every other fork-reading
    module, which never covered this file.
    """
    try:
        from metaphysica.simulations.base.registry import PMRegistry
    except ImportError as exc:  # the one tolerated failure: an import cycle
        raise SourceUnmeasurable(f"registry unimportable: {exc}") from exc

    try:
        w0 = PMRegistry.get_instance().get("cosmology.w0_derived")
    except Exception as exc:
        # Not yet computed. The honest answer is "cannot tell", never the
        # name of the option that happens to be declared adopted.
        raise SourceUnmeasurable(
            f"cosmology.w0_derived unavailable: {exc}"
        ) from exc

    if w0 is None:
        raise SourceUnmeasurable("cosmology.w0_derived is None")
    # Deferred: selection imports the catalogue, which imports this module.
    from .selection import resolve

    mechanism = resolve("dark_energy_mechanism")
    if mechanism != "thawing_quintessence":
        # w0 is not -(n-1)/n under another mechanism (mep_11_13 gives -11/13,
        # which rounds to n = 6 and used to report chi_over_b3_6).
        raise SourceUnmeasurable(
            f"dark_energy_mechanism = {mechanism}: w0 does not encode n")
    w0 = float(w0)
    if w0 <= -1.0:
        raise SourceUnmeasurable(
            f"w0 = {w0} is not of the form -(n-1)/n for positive n"
        )
    n = round(1.0 / (1.0 + w0))
    # The live-seed reading, checked before the frozen table: if the sector
    # has moved with the seed, n is the live b_3 and no fixed table entry
    # would name it. Skipped when the live b_3 is itself 24, where the two
    # readings coincide and the frozen option is the one declared.
    try:
        from metaphysica.simulations.PM.geometry.b3_path import (
            resolve_path, seed_values,
        )
        live_b3 = seed_values(resolve_path())[0]
    except ImportError:  # pragma: no cover - import cycle
        live_b3 = None
    if live_b3 is not None and n == live_b3 and n not in _DE_BETTI_BY_N:
        return "b3_live"
    if n not in _DE_BETTI_BY_N:
        # The case that matters: if the sector moved to n = b_3 on the
        # adopted seed, n = 43 is not in the table. Reporting "b3_24" here
        # would hide exactly the change this fork exists to catch.
        raise SourceUnmeasurable(
            f"w0 = {w0} implies n = {n}, which no declared option claims; "
            f"declared: {sorted(_DE_BETTI_BY_N)}"
        )
    return _DE_BETTI_BY_N[n]


def _render_policy_adopted() -> str:
    from metaphysica.generators.eml_render_validity import REQUIRE_OPERATOR

    return "strict" if REQUIRE_OPERATOR else "permissive"


def _theory_uncertainty_policy_adopted() -> str:
    from metaphysica.generators.generate_validation_certificates import (
        DEFAULT_THEORY_UNCERTAINTY_POLICY,
    )

    return DEFAULT_THEORY_UNCERTAINTY_POLICY


def _face_genericity_adopted() -> str:
    from metaphysica.simulations.PM.gauge.topological_terms import (
        face_assignment_candidates,
    )

    status = face_assignment_candidates()["status"]
    return "generic" if status == "CRITERION_STATED_NOT_DERIVED" else "all"


def _seed_selection_adopted() -> str:
    """The selection route's source constant, checked against the options."""
    from metaphysica.simulations.PM.geometry.closed_geometry.selection import (
        SELECTION_ROUTE,
    )

    return SELECTION_ROUTE


def _owner_recommended(item: int):
    from metaphysica.simulations.PM.gauge.master_ladder import OWNER_ITEMS

    return OWNER_ITEMS[item][2]


def _action_bulk_sectors_adopted() -> str:
    """Item 1 has no recommendation: build_ladder then treats it as undecided."""
    return "undecided" if _owner_recommended(1) is None else str(_owner_recommended(1))


def _action_bulk_spinor_adopted() -> str:
    return str(_owner_recommended(2))


def _action_planck_exponent_adopted() -> str:
    return "exponent_%d" % int(_owner_recommended(4))


def _action_sign_convention_adopted() -> str:
    return str(_owner_recommended(5))
