"""RECORDED DEFECT: the framework's phi is not a G2 3-form.

This file documents a measured defect rather than hiding it, in the same style
as test_racetrack_is_an_ansatz_not_a_vacuum.py. Every test here is GREEN while
the defect stands, and the file fails the moment phi is changed -- which is the
point, because changing phi is a physics ruling and must not happen silently.

THE MEASUREMENT
===============
g2 is by definition the subalgebra of so(7) annihilating phi, and it has
dimension 14. Building the linear map A -> A.phi on so(7) and taking its kernel:

    framework phi (all +1 on the 7 Fano triples)  ->  dim ann = 6
    Bryant phi    (+,+,+,+,-,-,-, same triples)   ->  dim ann = 14

The dimension of the annihilator is a GL(7) similarity invariant, so 6 != 14
proves the two forms lie in DIFFERENT GL(7) orbits. The framework's phi is not
a G2 3-form under any change of basis, and no relabelling or sign convention
can make it one. Exactly 16 of the 128 sign assignments on those 7 triples give
a genuine G2 form; all-(+1) is not among them.

WHY IT WAS NOT CAUGHT
=====================
The obvious sanity check does not discriminate. The naive metric
g_ij = phi_imn phi_jmn comes out 6 * I for BOTH forms, so "the induced metric is
positive definite and isotropic" passes either way.

THE BLAST RADIUS, MEASURED NOT ASSUMED
======================================
SAFE -- these depend only on WHICH 7 triples carry phi, not on their signs, and
are verified below to be identical for both forms:
  * R1 the diagonal stabiliser is (Z/2)^3, order 8
  * R2 each involution moves an arc and fixes a line
  * R3 the invariant 3-forms are exactly phi's 7 triples
  * R4 the Fano plane on Gamma
  * the arc flag identity 24 = 12 x 2

BROKEN -- these need phi to be a G2 form and it is not:
  * Lambda^2 = 7 + 14 with the 14 identified as g2
  * Lambda^3 = 1 + 7 + 27 as G2 irreps
  * the torsion classes computed by projection onto those subspaces

NOT FIXED HERE. Substituting a signed phi changes the framework's own convention
and may move published numbers, so it is a ruling for the author, staged as a
fork rather than applied. Evidence is prepared; the decision is not taken.
"""

from __future__ import annotations

import itertools

import numpy as np
import pytest

_TRIPLES = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5),
            (1, 4, 6), (2, 3, 6), (2, 4, 5)]
_PAIRS = list(itertools.combinations(range(7), 2))


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


# --------------------------------------------------------- the method is sound


def test_the_annihilator_test_recognises_a_known_g2_form():
    """Calibration. If this fails, the measurement below means nothing."""
    assert _annihilator_dim(_build([1, 1, 1, 1, -1, -1, -1])) == 14


def test_the_annihilator_test_can_return_something_other_than_14():
    """Guard against a measurement that always says 14."""
    assert _annihilator_dim(_build([1] * 7)) != 14


# ------------------------------------------------------------- the defect


def test_the_frameworks_phi_is_the_all_plus_one_form():
    phi = _framework_phi()
    support = [t for t in itertools.combinations(range(7), 3)
               if abs(phi[t]) > 1e-12]
    assert sorted(support) == sorted(_TRIPLES)
    assert all(phi[t] == pytest.approx(1.0) for t in _TRIPLES), (
        "this file documents the all-(+1) form; phi has changed and the "
        "recorded defect must be re-measured and the register updated"
    )


def test_the_frameworks_phi_has_a_six_dimensional_annihilator_not_fourteen():
    """THE DEFECT. Green while it stands; fails when phi is corrected."""
    dim = _annihilator_dim(_framework_phi())
    assert dim == 6, "measured dim ann(phi) = %d, expected the recorded 6" % dim
    assert dim != 14, "phi now looks like a G2 form -- update the register"


def test_no_change_of_basis_can_rescue_it():
    """dim ann is a GL(7) invariant, so 6 != 14 settles orbit membership."""
    fw = _annihilator_dim(_framework_phi())
    bryant = _annihilator_dim(_build([1, 1, 1, 1, -1, -1, -1]))
    assert fw != bryant, (
        "the annihilator dimension is invariant under GL(7); differing values "
        "prove the forms lie in different orbits, so no relabelling helps"
    )


def test_no_sign_flip_relates_the_two_forms():
    """Explicitly: it is not a coordinate convention."""
    fw = _framework_phi()
    bry = _build([1, 1, 1, 1, -1, -1, -1])
    for eps in itertools.product((1, -1), repeat=7):
        t = fw.copy()
        for a in range(7):
            if eps[a] < 0:
                t[a, :, :] *= -1
                t[:, a, :] *= -1
                t[:, :, a] *= -1
        assert not (np.allclose(t, bry) or np.allclose(t, -bry)), (
            "a sign flip maps the framework form to a G2 form, which would "
            "contradict the differing annihilator dimensions"
        )


def test_a_correct_choice_exists_and_is_not_unique():
    """16 of the 128 sign assignments on these triples are genuine G2 forms."""
    good = sum(1 for s in itertools.product((1, -1), repeat=7)
               if _annihilator_dim(_build(s)) == 14)
    assert good == 16, "expected 16 G2 sign assignments, measured %d" % good


def test_the_naive_metric_check_does_not_discriminate():
    """Why this went unnoticed: the obvious check passes for both forms."""
    for phi in (_framework_phi(), _build([1, 1, 1, 1, -1, -1, -1])):
        g = np.einsum("imn,jmn->ij", phi, phi)
        w = np.linalg.eigvalsh(g)
        assert np.allclose(w, 6.0), (
            "g_ij = phi.phi is 6*I for both forms, so it cannot be used to "
            "detect the defect"
        )


# --------------------------------------------------- the blast radius, measured


def test_the_combinatorial_results_survive_a_correct_g2_form():
    """R1-R4 and the flag identity depend on the triples, not the signs.

    This is what bounds the damage. If it ever fails, the defect reaches the
    derived 7-layer results too and the register must say so.
    """
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


def test_the_lambda2_split_is_not_g2_and_the_d4_calibration_says_so():
    """The A6 calibration gate must report uncalibrated, not quietly pass."""
    from metaphysica.simulations.PM.geometry.d4_root_shell import (
        g2_branching_calibration,
    )

    calib = g2_branching_calibration()
    assert calib["lambda2_is_7_plus_14"] is True, "the dimensions are still 7+14"
    assert calib["v14_annihilates_phi"] is False, (
        "V14 now annihilates phi -- the defect may be fixed; re-measure"
    )
    assert calib["calibrated"] is False
    assert calib["why_not_calibrated"]
    assert "not a G2 3-form" in calib["why_not_calibrated"]
