"""The arc flag derivation: 24 = 12 x 2 = (4 faces x 3 blocks) x (flag stab).

Every count below is asserted by a test that FAILS when phi is perturbed. That
is the point of the file. A computation returning 24 for any input would have
verified nothing, which is the defect class this project keeps finding, so
test_a_perturbed_phi_breaks_the_identity is the load-bearing test here and the
rest are only meaningful because it passes.

The last two tests guard the OTHER direction: that the module does not overclaim.
The identity is a statement about a group order, so it must stay labelled
NUMERICAL and must not be presented as deriving b_3 = 24.
"""

from __future__ import annotations

import numpy as np
import pytest

from metaphysica.simulations.PM.geometry.arc_flag_structure import (
    arc_flag_report,
    arc_stabiliser,
    arcs_and_complements,
    fano_automorphisms,
    fano_lines,
    fixed_locus_components,
    flag_pair_bijection,
    kernel_to_line_symmetry,
    orbit_and_stabiliser,
)


class _FakePhi:
    """A stand-in carrying an arbitrary 3-form, matching the joyce_orbifold tests."""

    def __init__(self, phi):
        self.phi = phi


def _perturbed_phi():
    """phi with the non-associative triple (0,1,3) added antisymmetrically.

    The same perturbation the joyce_orbifold suite uses, so the two files agree
    on what "perturbed" means.
    """
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )

    phi = G2DifferentialGeometry().phi.copy()
    for perm, sign in (((0, 1, 3), 1), ((1, 3, 0), 1), ((3, 0, 1), 1),
                       ((1, 0, 3), -1), ((0, 3, 1), -1), ((3, 1, 0), -1)):
        phi[perm] = sign
    return _FakePhi(phi)


# ------------------------------------------------------------------ the plane


def test_the_fano_plane_has_seven_lines_and_168_automorphisms():
    assert len(fano_lines()) == 7
    autos = fano_automorphisms()
    assert len(autos) == 168, (
        "Aut(PG(2,2)) = PSL(3,2) has order 168; got %d" % len(autos)
    )


def test_every_arc_is_the_complement_of_a_line():
    """The 4 + 3 split is the moved/fixed split of a group element, not a choice."""
    lines = {frozenset(line) for line in fano_lines()}
    pairs = arcs_and_complements()
    assert len(pairs) == 7
    for arc, line in pairs:
        assert len(arc) == 4 and len(line) == 3
        assert frozenset(line) in lines, "the fixed set is not a line"
        assert frozenset(arc) | frozenset(line) == frozenset(range(7))
        # an arc contains no line
        assert not any(m <= frozenset(arc) for m in lines)


# ------------------------------------------------------------------ step (i)


def test_the_twelve_flags_biject_with_arc_times_line():
    lines = fano_lines()
    arc, line = arcs_and_complements()[0]
    b = flag_pair_bijection(arc, line, lines)
    assert b["n_flags"] == 12
    assert b["n_pairs"] == 12
    assert b["is_bijection"], (
        "the flags must biject with A x L, giving the complete K(4,3)"
    )
    # each arc point reaches all three points of the line, once each
    for a, hits in b["arc_point_to_line_points"].items():
        assert sorted(hits) == sorted(line), (a, hits)


# ------------------------------------------------------------------ step (ii)


def test_the_arc_stabiliser_is_s4_of_order_24():
    autos = fano_automorphisms()
    arc, _ = arcs_and_complements()[0]
    stab = arc_stabiliser(arc, autos)
    assert len(stab) == 24, "168 / 7 arcs = 24; got %d" % len(stab)
    # faithful on the arc, and onto Sym(arc) -- so it IS S4, not merely order 24
    actions = {tuple(p[i] for i in sorted(arc)) for p in stab}
    assert len(actions) == 24, (
        "the stabiliser must act faithfully and transitively enough to realise "
        "all 24 permutations of the arc; got %d distinct actions" % len(actions)
    )


# ----------------------------------------------------------------- step (iii)


def test_the_kernel_is_order_four_and_acts_freely_on_the_arc():
    """Freeness is the step that forces Stab(a) onto Sym(L). Not decorative."""
    autos = fano_automorphisms()
    arc, line = arcs_and_complements()[0]
    stab = arc_stabiliser(arc, autos)
    k = kernel_to_line_symmetry(arc, line, stab)
    assert k["kernel_order"] == 4
    assert k["acts_freely_on_arc"], (
        "a non-identity kernel element fixing an arc point would break the "
        "surjection onto Sym(L), and transitivity on A x L with it"
    )


def test_the_action_on_the_twelve_pairs_is_transitive():
    autos = fano_automorphisms()
    arc, line = arcs_and_complements()[0]
    stab = arc_stabiliser(arc, autos)
    o = orbit_and_stabiliser(arc, line, stab)
    assert o["n_pairs"] == 12
    assert o["orbit_size"] == 12
    assert o["is_transitive"]


# ------------------------------------------------------------------ step (iv)


def test_the_flag_stabiliser_has_order_two_so_24_equals_12_times_2():
    autos = fano_automorphisms()
    arc, line = arcs_and_complements()[0]
    stab = arc_stabiliser(arc, autos)
    o = orbit_and_stabiliser(arc, line, stab)
    assert o["flag_stabiliser_order"] == 2
    assert len(stab) == o["orbit_size"] * o["flag_stabiliser_order"] == 24


def test_the_identity_holds_for_all_seven_arcs_not_just_the_first():
    """Otherwise the result could be an artefact of which arc was picked."""
    autos = fano_automorphisms()
    lines = fano_lines()
    for arc, line in arcs_and_complements():
        stab = arc_stabiliser(arc, autos)
        o = orbit_and_stabiliser(arc, line, stab)
        b = flag_pair_bijection(arc, line, lines)
        assert b["is_bijection"]
        assert (len(stab), o["orbit_size"], o["flag_stabiliser_order"]) == (24, 12, 2), (
            "arc %s failed: |stab|=%d orbit=%d fixer=%d"
            % (arc, len(stab), o["orbit_size"], o["flag_stabiliser_order"])
        )


def test_the_report_assembles_the_identity():
    r = arc_flag_report()
    assert r["automorphism_order"] == 168
    assert r["stabiliser_order"] == 24
    assert r["orbit"]["orbit_size"] == 12
    assert r["orbit"]["flag_stabiliser_order"] == 2
    assert r["identity_holds"] is True


# ------------------------------------------- the test that makes it a computation


def test_a_perturbed_phi_breaks_the_identity():
    """THE load-bearing test.

    Perturbing phi must move these numbers. If it does not, the module is
    returning constants rather than reading the form it was handed, and every
    other test in this file is vacuous.
    """
    fake = _perturbed_phi()

    # the perturbed form is not a G2 form, so its "lines" are not a Fano plane
    assert len(fano_lines(fake)) != 7
    assert len(fano_automorphisms(fake)) != 168
    assert len(arcs_and_complements(fake)) != 7

    r = arc_flag_report(fake)
    assert r["identity_holds"] is False, (
        "a perturbed phi still satisfied 24 = 12 x 2, so the derivation is not "
        "reading phi and proves nothing"
    )


def test_the_perturbation_is_a_real_perturbation():
    """Guard the guard: the fake phi must actually differ from the real one."""
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )

    real = G2DifferentialGeometry().phi
    fake = _perturbed_phi().phi
    assert not np.allclose(real, fake)


# ------------------------------------------------------------ the A4 guardrails


def test_the_result_is_labelled_numerical_not_geometric():
    """A group order is an integer, not a set of 3-cycles.

    The project's diagnosed failure mode is index structure mistaken for
    geometric structure. This test fails if the module is ever upgraded to
    GEOMETRIC without a 3-cycle count appearing.
    """
    r = arc_flag_report()
    assert r["verdict"] == "NUMERICAL", (
        "the flag identity may only be labelled GEOMETRIC once something "
        "exhibits 24 actual 3-cycles or harmonic 3-forms"
    )
    assert "NOT adopted" in r["verdict_reason"]


def test_the_module_does_not_claim_to_derive_b3():
    """No key may assert b_3 = 24 is derived here."""
    import json

    from metaphysica.simulations.PM.geometry import arc_flag_structure

    blob = json.dumps(arc_flag_report(), default=str).lower()
    for forbidden in ("b_3 = 24 is derived", "derives b_3", "origin of b_3 = 24 is"):
        assert forbidden not in blob, "module overclaims: %r" % forbidden

    doc = (arc_flag_structure.__doc__ or "").lower()
    assert "not adopted as the origin of b_3" in doc


def test_the_canon_4x3_ruling_is_addressed_not_ignored():
    """CANON rules that 4 x 3 is not a structure on 24. It must be answered."""
    r = arc_flag_report()
    note = r["does_not_contradict_canon_4x3_ruling"]
    assert "partitions 24 points" in note
    assert "subgroup order" in note


# --------------------------------------------------- where the geometry is not


def test_the_linear_action_leaves_112_components_and_needs_half_shifts():
    """The only genuine 3-cycles here, and the reason they do not reach 24.

    Each involution fixes 2^4 = 16 three-tori and a sign flip cannot permute
    them, because negating a half-period returns it mod 1. So the linear action
    identifies nothing and the half-shift data is load-bearing.
    """
    f = fixed_locus_components()
    assert f["n_involutions"] == 7
    assert f["components_per_involution"] == 16
    assert f["total_three_torus_components"] == 112
    assert f["linear_action_identifies_any"] is False
    assert f["half_shifts_are_load_bearing"] is True
    assert f["total_three_torus_components"] != 24
    assert f["total_three_torus_components"] != 17


def test_the_fixed_locus_count_moves_when_phi_does():
    """The 112 must be computed from the group, not written down."""
    before = fixed_locus_components()["total_three_torus_components"]
    after = fixed_locus_components(_perturbed_phi())["total_three_torus_components"]
    assert before == 112
    assert after != before, (
        "the component count did not respond to a perturbed phi, so it is a "
        "literal rather than a computation"
    )
