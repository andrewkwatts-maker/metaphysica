"""The 24 roots of D4 as a candidate origin for the number 24 -- and its gap.

WHY D4 WAS WORTH TESTING
========================
The framework's holonomy sits in the chain G2 = Aut(O) inside Spin(7) inside
Spin(8) = D4, so D4 is not imported from outside. And its root count is not
matched, it is FORCED: for any finite root system the number of roots equals
rank x Coxeter number, and D4 has rank 4 with Coxeter number 6, so 24 follows
from structure. The Coxeter number is computed here as the order of a Coxeter
element rather than looked up, because |roots| / rank would be circular.

The roots also form a SHELL -- 24 vectors of equal norm about the origin, the
4-dimensional kissing configuration -- and they split canonically into 12
positive and 12 negative. That is the shape the two-shadow reading wants.

THE GAP, AND IT IS DECISIVE
===========================
The 24 roots live in the 4-DIMENSIONAL Cartan subspace of so(8). A b_3 of 24
would be 24 harmonic 3-forms on a 7-manifold. There is no natural map from a
4-dimensional root space to H^3 of a 7-manifold, and none is constructed here.

Worse for the candidate: 24 is not a dimension of any G2 irreducible
representation. The small G2 dimensions are 1, 7, 14, 27, 35, 64, 77 -- no 24.
So b_3 = 24 cannot be read off G2 representation theory either.

Verdict: NUMERICAL. The integer is forced, which is more than any previous
candidate managed, but the objects carrying it are directions in a 4-space, not
3-cycles in a 7-manifold. Recorded, not adopted.

A SECOND HONEST CAVEAT
======================
The 12 + 12 split is NOT invariant. Choosing which roots are positive means
choosing a Weyl chamber, and the Weyl group moves that choice around. So "two
shadows of 12" would still cost a choice here, exactly as the 12 + 12 split of
the 24-dimensional lattice does. This candidate does not make that choice free.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Tuple

import numpy as np

_RANK = 4


def d4_roots() -> np.ndarray:
    """All +-e_i +- e_j for i < j in 4 dimensions. Built, not tabulated."""
    roots = []
    for i, j in itertools.combinations(range(_RANK), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = np.zeros(_RANK, dtype=np.int64)
                v[i] = si
                v[j] = sj
                roots.append(v)
    return np.array(roots, dtype=np.int64)


def simple_roots() -> np.ndarray:
    """A standard base for D4: e1-e2, e2-e3, e3-e4, e3+e4."""
    return np.array([
        [1, -1, 0, 0],
        [0, 1, -1, 0],
        [0, 0, 1, -1],
        [0, 0, 1, 1],
    ], dtype=np.int64)


def _reflection(alpha: np.ndarray) -> np.ndarray:
    """The matrix of the reflection in the hyperplane orthogonal to alpha."""
    a = alpha.astype(np.float64)
    return np.eye(_RANK) - 2.0 * np.outer(a, a) / float(a @ a)


def coxeter_number() -> int:
    """The order of a Coxeter element -- computed, so 24 = rank x h is a CHECK.

    Taking h = |roots| / rank would make the identity circular. Here h is the
    multiplicative order of the product of the simple reflections, which is an
    independent quantity, and the root count is then compared against rank x h.
    """
    c = np.eye(_RANK)
    for alpha in simple_roots():
        c = c @ _reflection(alpha)

    power = np.eye(_RANK)
    for k in range(1, 64):
        power = power @ c
        if np.allclose(power, np.eye(_RANK), atol=1e-9):
            return k
    raise RuntimeError("Coxeter element had no finite order under 64")


def positive_roots(regular: np.ndarray | None = None) -> np.ndarray:
    """The roots on the positive side of a generic hyperplane.

    The regular vector is a CHOICE of Weyl chamber. It is exposed as an argument
    rather than hidden so that the arbitrariness is visible: there is no
    canonical half of a root system.
    """
    roots = d4_roots()
    if regular is None:
        # generic: no root is orthogonal to it, checked below
        regular = np.array([8.0, 4.0, 2.0, 1.0])
    prods = roots.astype(np.float64) @ regular
    if np.any(np.abs(prods) < 1e-12):
        raise ValueError("the chosen vector is not regular: a root is orthogonal")
    return roots[prods > 0]


def is_shell(roots: np.ndarray) -> Dict[str, Any]:
    """Equal norm about the origin, and closed under negation."""
    norms = np.einsum("ij,ij->i", roots, roots)
    as_set = {tuple(int(x) for x in r) for r in roots}
    return {
        "count": int(len(roots)),
        "all_same_norm": bool(np.all(norms == norms[0])),
        "norm_squared": int(norms[0]),
        "closed_under_negation": all(
            tuple(-x for x in r) in as_set for r in as_set
        ),
        "sums_to_zero": bool(np.all(roots.sum(axis=0) == 0)),
    }


def g2_branching_calibration() -> Dict[str, Any]:
    """A6 calibration: reproduce the published so(8) -> g2 branching.

    The published statement is so(8) = 28 decomposing under G2 as
    g2(14) + 7 + 7, via so(8) = so(7) + 7 and so(7) = g2 + 7.

    Dimension counting alone would be a weak check, so the 14 is verified to be
    g2 by its DEFINING property instead: g2 is exactly the subalgebra of so(7)
    annihilating phi. Every basis element of the framework's V14 must kill phi,
    and every element of V7 must not. If that fails, the calibration fails and
    the novel output below is uncalibrated.
    """
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )

    g2 = G2DifferentialGeometry()
    subs = g2._lambda2_subspaces()
    pairs = list(subs["pairs"])
    phi = np.asarray(g2.phi, dtype=np.float64)

    def _as_matrix(vec: np.ndarray) -> np.ndarray:
        """A 21-vector in the pairs basis -> an antisymmetric 7x7 matrix."""
        a = np.zeros((7, 7), dtype=np.float64)
        for coeff, (i, j) in zip(vec, pairs):
            a[i, j] = coeff
            a[j, i] = -coeff
        return a

    def _action_norm(a: np.ndarray) -> float:
        """Norm of the so(7) action of A on phi. Zero exactly on g2."""
        out = (
            -np.einsum("im,mjk->ijk", a, phi)
            - np.einsum("jm,imk->ijk", a, phi)
            - np.einsum("km,ijm->ijk", a, phi)
        )
        return float(np.linalg.norm(out))

    v7 = np.asarray(subs["V7"], dtype=np.float64)
    v14 = np.asarray(subs["V14"], dtype=np.float64)

    scale = float(np.linalg.norm(phi)) or 1.0
    v14_norms = [_action_norm(_as_matrix(r)) / scale for r in v14]
    v7_norms = [_action_norm(_as_matrix(r)) / scale for r in v7]

    dims = {"V7": int(v7.shape[0]), "V14": int(v14.shape[0])}
    dims_ok = dims == {"V7": 7, "V14": 14}
    v14_kills_phi = bool(v14_norms and max(v14_norms) < 1e-9)
    v7_does_not = bool(v7_norms and min(v7_norms) > 1e-6)

    so8, so7 = 28, 21
    branching_ok = (so8 - so7 == 7) and (so7 - 14 == 7)

    return {
        "lambda2_split": dims,
        "lambda2_is_7_plus_14": dims_ok,
        "v14_annihilates_phi": v14_kills_phi,
        "v14_max_action_norm": max(v14_norms) if v14_norms else None,
        "v7_min_action_norm": min(v7_norms) if v7_norms else None,
        "v7_does_not_annihilate_phi": v7_does_not,
        "dim_so8": so8,
        "dim_so7": so7,
        "branching_dimensions_consistent": branching_ok,
        "calibrated": dims_ok and v14_kills_phi and v7_does_not and branching_ok,
        "what_this_checks": (
            "so(8) = so(7) + 7 and so(7) = g2 + 7, so so(8) -> g2 + 7 + 7. The "
            "14 is verified to BE g2 by annihilating phi, not by counting to 14."
        ),
        "why_not_calibrated": (
            None if (dims_ok and v14_kills_phi and v7_does_not and branching_ok)
            else (
                "V14 has the right dimension but does not annihilate phi, so it "
                "is not g2. The cause is upstream and is recorded separately: "
                "the framework's phi is the all-(+1) form on the 7 Fano "
                "triples, whose annihilator in so(7) is 6-dimensional, not 14. "
                "It is therefore not a G2 3-form at all, and no Lambda^2 "
                "splitting of it can produce g2. See "
                "tests/test_phi_is_not_yet_a_g2_form.py."
            )
        ),
    }


def g2_representation_dimensions() -> List[int]:
    """Small G2 irrep dimensions, for the containment check below.

    Listed to make one negative point checkable: 24 is not among them, so
    b_3 = 24 cannot be a G2 representation dimension.
    """
    return [1, 7, 14, 27, 35, 64, 77]


def d4_shell_report() -> Dict[str, Any]:
    """The candidate, its forced count, and the gap that stops it."""
    roots = d4_roots()
    h = coxeter_number()
    pos = positive_roots()
    shell = is_shell(roots)
    calib = g2_branching_calibration()

    return {
        "rank": _RANK,
        "n_roots": int(len(roots)),
        "coxeter_number": h,
        "rank_times_coxeter": _RANK * h,
        "count_is_forced": int(len(roots)) == _RANK * h,
        "n_simple_roots": int(len(simple_roots())),
        "n_positive": int(len(pos)),
        "n_negative": int(len(roots) - len(pos)),
        "splits_12_plus_12": len(pos) == len(roots) - len(pos) == 12,
        "split_requires_a_chamber_choice": True,
        "shell": shell,
        "calibration": calib,
        "root_space_dimension": _RANK,
        "b3_would_live_on_a_7_manifold": True,
        "map_to_three_forms_exists": False,
        "24_is_a_g2_irrep_dimension": 24 in g2_representation_dimensions(),
        "verdict": "NUMERICAL",
        "verdict_reason": (
            "The count 24 = rank x Coxeter = 4 x 6 is forced rather than "
            "matched, which is more than earlier candidates achieved. But the "
            "roots are directions in a 4-dimensional Cartan space while b_3 "
            "would count harmonic 3-forms on a 7-manifold, and no map between "
            "them is constructed. 24 is also not a G2 irrep dimension. "
            "Recorded as a candidate, NOT adopted."
        ),
    }
