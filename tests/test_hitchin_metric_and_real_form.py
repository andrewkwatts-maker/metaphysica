"""The metric must be able to tell which G2 it has, and the old one could not.

THE FINDING THIS FILE PINS
==========================
The register recorded that the framework's phi "is not a G2 form", measured by a
6-dimensional annihilator in so(7) where g2 needs 14. That is true but it
understates and slightly misnames the situation. Measured here:

    octonion_derived   gl(7) stabiliser 14,  Hitchin signature (7,0)  COMPACT G2
    all_plus_one       gl(7) stabiliser 14,  Hitchin signature (4,3)  SPLIT G2*

BOTH lie in open GL(7,R) orbits of Lambda^3(R^7) -- there are exactly two, and
both have 14-dimensional stabilisers. So the framework's phi IS a G2-structure,
with a genuine 14-dimensional symmetry algebra. What it is not is RIEMANNIAN:
its induced metric has signature (4,3), the stabiliser is the SPLIT real form
G2* whose maximal compact is SU(2) x SU(2) (dimension 6 -- which is where the
register's 6 comes from), and no Riemannian G2-holonomy manifold sits behind it.
Joyce's construction needs the compact form.

WHY THE OLD METRIC COULD NOT SEE THIS
=====================================
compute_metric() is the QUADRATIC contraction phi_iab phi_jab / 6. It returns
exactly 1.0 * I_7 for both real forms, so every statement made through it about
"the unique compatible Riemannian metric" was unfalsifiable. Hitchin's
construction is CUBIC, and cubic is the lowest degree that sees the difference.

WHAT IS NOT AFFECTED, AND IT IS LOAD-BEARING
============================================
The diagonal (Z/2)^3 stabiliser depends only on phi's SUPPORT -- which triples
are non-zero -- and the two branches share that exactly. So R1-R4, the
half-shift enumeration, the A1 census and b_3 = 7 + 3 n_T3 are all
fork-independent. The geometric closure rides on Fano incidence, not on the real
form. A test below asserts it, because if it ever stopped being true the b_3
result would move with the fork and that must not happen silently.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools

import numpy as np
import pytest

from metaphysica.simulations.PM.geometry.g2_differential import (
    G2_TRIPLES,
    G2DifferentialGeometry,
    phi_from_octonion_product,
)


def _all_plus_phi() -> np.ndarray:
    """The framework's tabulated all-(+1) phi, built independently here."""
    phi = np.zeros((7, 7, 7))
    for (i, j, k, s) in G2_TRIPLES:
        for perm, sgn in (((i, j, k), s), ((j, k, i), s), ((k, i, j), s),
                          ((j, i, k), -s), ((i, k, j), -s), ((k, j, i), -s)):
            phi[perm] = sgn
    return phi


def _push(phi: np.ndarray, h: np.ndarray) -> np.ndarray:
    """Pull phi back by h, staying inside its GL(7,R) orbit."""
    return np.einsum('ia,jb,kc,abc->ijk', h, h, h, phi)


_COMPACT = phi_from_octonion_product()
_SPLIT = _all_plus_phi()


# ------------------------------------------------------- the defect, pinned

def test_the_quadratic_contraction_cannot_tell_the_two_apart():
    """GREEN while the old metric is blind. The reason the cubic one exists."""
    q_compact = G2DifferentialGeometry(_COMPACT).compute_metric()
    q_split = G2DifferentialGeometry(_SPLIT).compute_metric()

    assert np.allclose(q_compact, np.eye(7)), q_compact
    assert np.allclose(q_split, np.eye(7)), q_split
    assert np.allclose(q_compact, q_split), (
        "the quadratic contraction now distinguishes the real forms. If that "
        "is a deliberate change, this test should be deleted -- but the "
        "identity phi_iab phi_jab = 6 g_ij holds for both, so it should not."
    )


def test_the_hitchin_metric_can():
    compact = G2DifferentialGeometry(_COMPACT)
    split = G2DifferentialGeometry(_SPLIT)

    g_compact = compact.compute_hitchin_metric()
    g_split = split.compute_hitchin_metric()

    assert not np.allclose(g_compact, g_split), (
        "the cubic construction must separate what the quadratic could not"
    )
    # compact: positive definite
    assert np.all(np.linalg.eigvalsh(g_compact) > 0)
    # split: genuinely indefinite, 4 of one sign and 3 of the other
    eig = np.linalg.eigvalsh(g_split)
    assert np.sum(eig > 0) == 4 and np.sum(eig < 0) == 3, eig


# ------------------------------------------------------- the classification

def test_the_two_real_forms_are_named_correctly():
    compact = G2DifferentialGeometry(_COMPACT).real_form_report()
    split = G2DifferentialGeometry(_SPLIT).real_form_report()

    assert compact["real_form"] == "COMPACT_G2"
    assert compact["hitchin_signature_unordered"] == (7, 0)
    assert compact["is_riemannian"] is True
    assert compact["supports_g2_holonomy"] is True

    assert split["real_form"] == "SPLIT_G2_STAR"
    assert split["hitchin_signature_unordered"] == (4, 3)
    assert split["is_riemannian"] is False
    assert split["supports_g2_holonomy"] is False


def test_both_lie_in_open_orbits_so_dim_14_does_not_discriminate():
    """The refinement: 'not a G2 form' understates it. Both ARE G2-structures."""
    for phi in (_COMPACT, _SPLIT):
        report = G2DifferentialGeometry(phi).real_form_report()
        assert report["stabiliser_dim_gl7"] == 14, (
            "a stable 3-form has a 14-dimensional GL(7) stabiliser in either "
            "real form; %s" % report
        )


def test_the_coordinate_so7_count_is_reported_as_frame_dependent():
    """It is 14 vs 6 here, which is where the register's 6 came from -- but it
    must not be the classifier, because it collapses under a frame change."""
    compact = G2DifferentialGeometry(_COMPACT).real_form_report()
    split = G2DifferentialGeometry(_SPLIT).real_form_report()
    assert compact["stabiliser_dim_so7_coordinate"] == 14
    assert split["stabiliser_dim_so7_coordinate"] == 6
    assert "frame-dependent" in compact["classified_by"]


# ------------------------------------------------------- frame robustness

@pytest.mark.parametrize("label", ["rotation", "general_gl", "reflection"])
def test_the_real_form_survives_a_frame_change(label):
    from scipy.linalg import expm

    rng = np.random.default_rng(7)
    a = rng.normal(size=(7, 7))
    q = expm(0.7 * (a - a.T))
    if label == "rotation":
        h = q
    elif label == "general_gl":
        h = np.diag([1.0, 1.3, 0.8, 1.7, 0.6, 1.1, 0.9]) @ q
    else:
        h = np.eye(7)
        h[0, 0] = -1.0

    for phi, expected in ((_COMPACT, "COMPACT_G2"), (_SPLIT, "SPLIT_G2_STAR")):
        moved = G2DifferentialGeometry(_push(phi, h)).real_form_report()
        assert moved["real_form"] == expected, (
            "%s changed the real form under %s, which is a GL(7) invariant: %s"
            % (expected, label, moved["hitchin_signature"])
        )


def test_a_reflection_flips_the_signature_but_not_the_form():
    """Why the classifier uses the UNORDERED signature."""
    h = np.eye(7)
    h[0, 0] = -1.0
    moved = G2DifferentialGeometry(_push(_COMPACT, h)).real_form_report()
    assert moved["hitchin_signature"] == (0, 7)
    assert moved["hitchin_signature_unordered"] == (7, 0)
    assert moved["real_form"] == "COMPACT_G2"


# ------------------------------------------------------- degenerate input

def test_an_unstable_form_raises_rather_than_returning_a_metric():
    phi = np.zeros((7, 7, 7))
    for perm, sgn in ((( 0, 1, 2), 1), ((1, 2, 0), 1), ((2, 0, 1), 1),
                      ((1, 0, 2), -1), ((0, 2, 1), -1), ((2, 1, 0), -1)):
        phi[perm] = sgn
    g2 = G2DifferentialGeometry(phi)
    assert abs(np.linalg.det(g2.hitchin_bilinear())) < 1e-9
    with pytest.raises(ValueError, match="not stable"):
        g2.compute_hitchin_metric()
    assert g2.real_form_report()["real_form"] == "DEGENERATE"


# ------------------------------------- the fact the b_3 closure rests on

def _diagonal_stabiliser(phi: np.ndarray):
    basis = list(itertools.combinations(range(7), 3))
    vec = np.array([phi[t] for t in basis])
    out = []
    for eps in itertools.product((1, -1), repeat=7):
        acted = np.array([eps[i] * eps[j] * eps[k] for (i, j, k) in basis]) * vec
        if np.allclose(acted, vec):
            out.append(eps)
    return sorted(out)


def test_the_z2_cubed_stabiliser_is_fork_independent():
    """b_3 = 7 + 3 n_T3 must not move with the real form.

    The sign-flip action multiplies each triple's coefficient by eps_i eps_j
    eps_k, so invariance constrains only the SUPPORT of phi -- and both
    branches have the same support. If this ever fails, every R1-R4 result and
    the whole half-shift enumeration become fork-dependent, and the b_3 ruling
    would silently acquire a second axis.
    """
    support_compact = sorted(t for t in itertools.combinations(range(7), 3)
                             if abs(_COMPACT[t]) > 1e-12)
    support_split = sorted(t for t in itertools.combinations(range(7), 3)
                           if abs(_SPLIT[t]) > 1e-12)
    assert support_compact == support_split

    stab_compact = _diagonal_stabiliser(_COMPACT)
    stab_split = _diagonal_stabiliser(_SPLIT)
    assert len(stab_compact) == 8
    assert stab_compact == stab_split, (
        "the diagonal stabiliser now differs between real forms; b_3 would "
        "move with g2_form_convention"
    )


def test_the_live_module_agrees_with_this_files_independent_construction():
    """Guards against the test passing by rebuilding the same bug twice."""
    assert np.allclose(G2DifferentialGeometry._standard_phi(), _SPLIT) or \
        np.allclose(G2DifferentialGeometry._standard_phi(), _COMPACT), (
            "neither branch matches the module's _standard_phi(); the fork "
            "options have changed and this file needs updating"
        )


# ------------------------------------------------------- falsifiability

def test_a_moved_form_moves_the_hitchin_metric():
    """A metric that ignored its input would pass everything above."""
    base = G2DifferentialGeometry(_COMPACT).compute_hitchin_metric()
    stretch = np.diag([1.0, 1.4, 0.7, 1.2, 0.9, 1.1, 0.8])
    moved = G2DifferentialGeometry(
        _push(_COMPACT, stretch)).compute_hitchin_metric()
    assert not np.allclose(base, moved), (
        "the Hitchin metric did not respond to a genuine frame change"
    )


def test_the_bilinear_is_cubic_in_phi():
    """Degree 3 is the whole point; a quadratic form would scale as s^2."""
    g2 = G2DifferentialGeometry(_COMPACT)
    b_one = g2.hitchin_bilinear()
    b_two = G2DifferentialGeometry(2.0 * _COMPACT).hitchin_bilinear()
    assert np.allclose(b_two, 8.0 * b_one), (
        "B did not scale as s^3 under phi -> s phi; it is not Hitchin's form"
    )


# --------------------------------- the irrep decomposition, both real forms

@pytest.mark.parametrize("label,phi", [("compact", _COMPACT), ("split", _SPLIT)])
def test_the_irrep_dimensions_are_identical_on_both_real_forms(label, phi):
    """The register lists Lambda^2 = 7 + 14 and Lambda^3 = 1 + 7 + 27 as part of
    the "BROKEN blast radius" of the wrong phi. Measured, the DIMENSIONS are
    correct on both forms -- as they must be, since the split and compact real
    forms share a complexification and therefore share irrep dimensions.

    What the split branch actually breaks is the IDENTIFICATION of the 14 with
    the compact g2. That is a naming error with physical consequences, not a
    dimension error, and the distinction matters: nothing needs recomputing,
    but every sentence calling the 14 "g2" is wrong on that branch.
    """
    g2 = G2DifferentialGeometry(phi)
    s3 = g2._lambda3_subspaces()
    s2 = g2._lambda2_subspaces()

    r3 = [np.linalg.matrix_rank(s3[k], tol=1e-9) for k in ("V1", "V7", "V27")]
    r2 = [np.linalg.matrix_rank(s2[k], tol=1e-9) for k in ("V7", "V14")]

    assert r3 == [1, 7, 27], "%s: Lambda^3 split is %s" % (label, r3)
    assert sum(r3) == 35
    assert r2 == [7, 14], "%s: Lambda^2 split is %s" % (label, r2)
    assert sum(r2) == 21


def test_the_unantisymmetrised_v7_spans_the_same_space():
    """Pins the factor-of-24 non-bug, so it is not 'fixed' into a regression.

    The V7 rows are built from a single ordered tuple rather than a full wedge.
    The epsilon contraction antisymmetrises regardless, so the properly
    antisymmetrised construction spans the identical subspace and differs by
    exactly 24. These rows are a span for a least-squares projection; scale is
    irrelevant. If someone antisymmetrises the loop, this test still passes --
    which is the point.
    """
    import itertools as _it

    basis = list(_it.combinations(range(7), 3))

    def perm_sign(seq):
        s, q = 1, list(seq)
        for i in range(len(q)):
            for j in range(i + 1, len(q)):
                if q[i] > q[j]:
                    s = -s
        return s

    from metaphysica.simulations.PM.geometry.g2_differential import (
        _levi_civita_7d,
    )
    eps = _levi_civita_7d()

    for phi in (_COMPACT, _SPLIT):
        rows = []
        for i in range(7):
            four = np.zeros((7, 7, 7, 7))
            for (a, b, c) in basis:
                val = phi[a, b, c]
                if val == 0.0 or i in (a, b, c):
                    continue
                idx = (i, a, b, c)
                for p in _it.permutations(range(4)):
                    four[tuple(idx[k] for k in p)] += perm_sign(p) * val
            three = np.einsum('abcd,abcdijk->ijk', four, eps) / 24.0
            rows.append(np.array([three[t] for t in basis]))
        full = np.array(rows)

        current = G2DifferentialGeometry(phi)._lambda3_subspaces()["V7"]
        assert np.linalg.matrix_rank(current, tol=1e-9) == 7
        assert np.linalg.matrix_rank(full, tol=1e-9) == 7
        assert np.linalg.matrix_rank(np.vstack([current, full]), tol=1e-9) == 7, (
            "the two constructions no longer span the same subspace"
        )
