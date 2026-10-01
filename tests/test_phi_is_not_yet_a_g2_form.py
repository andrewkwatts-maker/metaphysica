"""phi's real form: the defect that was recorded, and the ruling that fixed it.

HISTORY
=======
Measured 2026-09-13: the framework's phi -- all +1 on the 7 Fano triples -- is
not a G2 3-form. g2 is the subalgebra of so(7) annihilating phi and has
dimension 14; the all-(+1) form has a 6-dimensional annihilator. dim ann is a
GL(7) similarity invariant, so no change of basis or sign convention rescues
it. The form the framework's own octonion product implies differs in one sign,
on (1,3,5), and is a genuine G2 form. This file used to be GREEN while the
defect stood, and was written to fail the moment phi changed, so the change
could not happen silently.

RULED 2026-10-01 by the author (D-015): the compact form (`octonion_derived`)
is the active path; the split form (`all_plus_one`) stays a switchable path.
So the file now checks BOTH paths: on the active path phi is a G2 form; on the
split switch the recorded defect is still exactly what was measured.

WHY IT WAS NOT CAUGHT
=====================
The naive metric g_ij = phi_imn phi_jmn is 6 * I for BOTH forms.

THE BLAST RADIUS (unchanged)
============================
R1-R4 and the arc flag identity depend only on WHICH triples carry phi, not
their signs, and are identical on both paths. What the split form breaks --
Lambda^2 = 7 + 14 with the 14 as g2, Lambda^3 = 1 + 7 + 27 as G2 irreps, the
torsion classes -- holds on the active path.
"""

from __future__ import annotations

import itertools

import numpy as np
import pytest

_TRIPLES = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5),
            (1, 4, 6), (2, 3, 6), (2, 4, 5)]
_PAIRS = list(itertools.combinations(range(7), 2))
_ENV = "METAPHYSICA_VARIANT_G2_FORM_CONVENTION"


def _build(signs):
    """A 3-form supported on the 7 Fano triples with the given signs."""
    phi = np.zeros((7, 7, 7))
    for (i, j, k), s in zip(_TRIPLES, signs):
        for perm, sg in (((i, j, k), 1), ((j, k, i), 1), ((k, i, j), 1),
                         ((j, i, k), -1), ((i, k, j), -1), ((k, j, i), -1)):
            phi[perm] = s * sg
    return phi


def _annihilator_dim(phi):
    """dim {A in so(7) : A acts trivially on phi}. Equals 14 exactly on G2 forms."""
    def as_matrix(vec):
        a = np.zeros((7, 7))
        for c, (i, j) in zip(vec, _PAIRS):
            a[i, j] = c
            a[j, i] = -c
        return a

    def action(a):
        return (np.einsum("mi,mjk->ijk", a, phi)
                + np.einsum("mj,imk->ijk", a, phi)
                + np.einsum("mk,ijm->ijk", a, phi))

    basis = np.eye(21)
    cols = np.array([action(as_matrix(basis[b])).ravel() for b in range(21)]).T
    sv = np.linalg.svd(cols, compute_uv=False)
    return 21 - int((sv > 1e-9 * max(sv)).sum())


class _FakePhi:
    def __init__(self, phi):
        self.phi = phi


def _framework_phi():
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )
    return np.asarray(G2DifferentialGeometry().phi, dtype=float)


@pytest.fixture
def split(monkeypatch):
    """The split-form switch path (all_plus_one)."""
    monkeypatch.setenv(_ENV, "all_plus_one")


@pytest.fixture
def adopted(monkeypatch):
    """The active path, with no override in the environment."""
    monkeypatch.delenv(_ENV, raising=False)


# --------------------------------------------------------- the method is sound


def test_the_annihilator_test_recognises_a_known_g2_form():
    """Calibration. If this fails, the measurements below mean nothing."""
    assert _annihilator_dim(_build([1, 1, 1, 1, -1, -1, -1])) == 14


def test_the_annihilator_test_can_return_something_other_than_14():
    """Guard against a measurement that always says 14."""
    assert _annihilator_dim(_build([1] * 7)) != 14


# ------------------------------------------------- the two paths, measured


def test_the_frameworks_phi_is_the_all_plus_one_form(split):
    """On the split switch phi is still the recorded all-(+1) form."""
    phi = _framework_phi()
    support = [t for t in itertools.combinations(range(7), 3)
               if abs(phi[t]) > 1e-12]
    assert sorted(support) == sorted(_TRIPLES)
    assert all(phi[t] == pytest.approx(1.0) for t in _TRIPLES)


def test_the_adopted_phi_carries_the_octonion_signs(adopted):
    """Same support, one sign different: -1 on (1,3,5)."""
    phi = _framework_phi()
    support = [t for t in itertools.combinations(range(7), 3)
               if abs(phi[t]) > 1e-12]
    assert sorted(support) == sorted(_TRIPLES)
    assert phi[(1, 3, 5)] == pytest.approx(-1.0)
    assert all(phi[t] == pytest.approx(1.0)
               for t in _TRIPLES if t != (1, 3, 5))


def test_the_frameworks_phi_has_a_six_dimensional_annihilator_not_fourteen(
        split):
    """THE RECORDED DEFECT, still measurable on the split switch."""
    assert _annihilator_dim(_framework_phi()) == 6


def test_the_adopted_phi_is_a_g2_form(adopted):
    """The ruling's point: on the active path phi is a genuine G2 form."""
    assert _annihilator_dim(_framework_phi()) == 14


def test_no_change_of_basis_can_rescue_it(split):
    """dim ann is a GL(7) invariant, so 6 != 14 settles orbit membership."""
    fw = _annihilator_dim(_framework_phi())
    bryant = _annihilator_dim(_build([1, 1, 1, 1, -1, -1, -1]))
    assert fw != bryant


def test_no_sign_flip_relates_the_two_forms(split):
    """Explicitly: the split form is not a coordinate convention."""
    fw = _framework_phi()
    bry = _build([1, 1, 1, 1, -1, -1, -1])
    for eps in itertools.product((1, -1), repeat=7):
        t = fw.copy()
        for a in range(7):
            if eps[a] < 0:
                t[a, :, :] *= -1
                t[:, a, :] *= -1
                t[:, :, a] *= -1
        assert not (np.allclose(t, bry) or np.allclose(t, -bry))


def test_a_correct_choice_exists_and_is_not_unique():
    """16 of the 128 sign assignments on these triples are genuine G2 forms."""
    good = sum(1 for s in itertools.product((1, -1), repeat=7)
               if _annihilator_dim(_build(s)) == 14)
    assert good == 16, "expected 16 G2 sign assignments, measured %d" % good


def test_the_naive_metric_check_does_not_discriminate():
    """Why the defect went unnoticed: the obvious check passes for both."""
    for phi in (_build([1] * 7), _build([1, 1, 1, 1, -1, -1, -1])):
        g = np.einsum("imn,jmn->ij", phi, phi)
        assert np.allclose(np.linalg.eigvalsh(g), 6.0)


# --------------------------------------------------- the blast radius, measured


def test_the_combinatorial_results_survive_a_correct_g2_form():
    """R1-R4 and the flag identity depend on the triples, not the signs."""
    from metaphysica.simulations.PM.geometry.arc_flag_structure import (
        arc_flag_report,
    )
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        diagonal_stabiliser,
        group_fano_lines,
        invariant_three_forms,
        involution_arc_correspondence,
    )

    for signs in ([1] * 7, [1, 1, 1, 1, -1, -1, -1]):
        f = _FakePhi(_build(signs))
        assert len(diagonal_stabiliser(f)) == 8
        corr = involution_arc_correspondence(f)
        assert len(corr) == 7
        assert all(c["moved_is_arc"] for c in corr)
        assert all(c["fixed_is_line"] for c in corr)
        assert sorted(invariant_three_forms(f)) == sorted(_TRIPLES)
        assert len(group_fano_lines(f)) == 7
        r = arc_flag_report(f)
        assert r["automorphism_order"] == 168
        assert r["stabiliser_order"] == 24
        assert r["identity_holds"] is True


def test_the_lambda2_split_is_not_g2_and_the_d4_calibration_says_so(split):
    """On the split switch the A6 gate reports uncalibrated, not a quiet pass."""
    from metaphysica.simulations.PM.geometry.d4_root_shell import (
        g2_branching_calibration,
    )

    calib = g2_branching_calibration()
    assert calib["lambda2_is_7_plus_14"] is True
    assert calib["v14_annihilates_phi"] is False
    assert calib["calibrated"] is False
    assert calib["why_not_calibrated"]


def test_the_d4_calibration_passes_on_the_adopted_path(adopted):
    from metaphysica.simulations.PM.geometry.d4_root_shell import (
        g2_branching_calibration,
    )

    calib = g2_branching_calibration()
    assert calib["lambda2_is_7_plus_14"] is True
    assert calib["v14_annihilates_phi"] is True
    assert calib["calibrated"] is True


# ------------------------------------------------------- the root cause, located


def _octonions():
    from metaphysica.simulations.PM.algebra.octonions import OctonionAlgebra

    return OctonionAlgebra()


def test_the_octonion_product_is_genuinely_octonionic():
    """The algebra was never at fault: norm-multiplicative and alternative."""
    o = _octonions()
    rng = np.random.default_rng(0)
    worst_norm = 0.0
    worst_alt = 0.0
    for _ in range(200):
        a = rng.normal(size=8)
        b = rng.normal(size=8)
        lhs = np.linalg.norm(o.multiply(a, b))
        rhs = np.linalg.norm(a) * np.linalg.norm(b)
        worst_norm = max(worst_norm, abs(lhs - rhs) / rhs)
        left = o.multiply(o.multiply(a, a), b)
        right = o.multiply(a, o.multiply(a, b))
        worst_alt = max(worst_alt,
                        np.linalg.norm(left - right) / (np.linalg.norm(left) + 1e-30))
    assert worst_norm < 1e-12, "multiply() is not norm-multiplicative"
    assert worst_alt < 1e-12, "multiply() is not alternative"


def test_the_form_implied_by_the_product_is_a_genuine_g2_form():
    """phi[i,j,k] = (e_i e_j)_k has a 14-dimensional annihilator."""
    from metaphysica.simulations.PM.geometry.g2_differential import (
        phi_from_octonion_product,
    )

    assert _annihilator_dim(phi_from_octonion_product()) == 14


def test_the_extraction_disagrees_with_the_product_it_claims_to_come_from(
        split):
    """THE ROOT CAUSE, on the split switch: the all-(+1) tensor is returned
    rather than the 3-form the multiplication implies."""
    from metaphysica.simulations.PM.geometry.g2_differential import (
        phi_from_octonion_product,
    )

    extracted = np.asarray(_octonions().g2_structure_as_3form(), dtype=float)
    implied = phi_from_octonion_product()
    assert not np.allclose(extracted, implied)
    assert _annihilator_dim(extracted) == 6
    assert _annihilator_dim(implied) == 14


def test_the_extraction_agrees_with_the_product_on_the_adopted_path(adopted):
    from metaphysica.simulations.PM.geometry.g2_differential import (
        phi_from_octonion_product,
    )

    extracted = np.asarray(_octonions().g2_structure_as_3form(), dtype=float)
    assert np.allclose(extracted, phi_from_octonion_product())
    assert np.allclose(extracted, _framework_phi())


def test_they_differ_in_exactly_one_triple(split):
    """One sign, on (1,3,5). The correct form was already in the codebase."""
    from metaphysica.simulations.PM.geometry.g2_differential import (
        phi_from_octonion_product,
    )

    extracted = np.asarray(_octonions().g2_structure_as_3form(), dtype=float)
    implied = phi_from_octonion_product()
    differing = [t for t in itertools.combinations(range(7), 3)
                 if not np.isclose(extracted[t], implied[t])]
    assert differing == [(1, 3, 5)]
    assert np.isclose(extracted[(1, 3, 5)], -implied[(1, 3, 5)])


def test_the_correction_is_adopted_and_the_split_form_stays_switchable():
    """D-015: the compact form is active; the split form is one switch away."""
    from metaphysica.simulations.core.variants import FORKS

    fork = FORKS["g2_form_convention"]
    assert fork.status == "RULED"
    assert fork.option_ids() == ["all_plus_one", "octonion_derived"]
    assert fork.default() == "octonion_derived"
    assert fork.read_adopted() == fork.default(), "fork has drifted from source"
    assert fork.option("all_plus_one").status == "considered", (
        "the split form must stay runnable for comparison")
