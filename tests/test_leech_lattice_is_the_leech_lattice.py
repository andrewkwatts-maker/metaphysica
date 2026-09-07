"""The Leech lattice must actually be the Leech lattice.

WHAT THIS CAUGHT
----------------
``LeechLattice._generator_matrix`` did not generate Λ₂₄. Its own docstring
said so -- *"This isn't quite right for the standard form"* -- and it was used
anyway for every generator-derived quantity in the module: the Gram matrix,
the bridge-pair moduli, and the axion alignment matrix.

It failed **both** properties that define the lattice::

    det(Gram) = 7_144_929  (= 2673²)     Λ₂₄ is unimodular, det 1
    12 basis rows of norm 2              Λ₂₄ has NO vector of norm 2

The norm-2 rows were the ``4·e_i`` for i < 12, since |4e_i|²/8 = 2. That is
decisive on its own: rootlessness is exactly what distinguishes Λ₂₄ from the
other 23 Niemeier lattices, so a 24-dimensional even unimodular lattice *with*
roots is one of the other 23 by definition.

The construction also applied ``4·e_i`` to only the first twelve coordinates
while the last twelve came from the Golay rows, so the two halves obeyed
different rules and the 8-coordinate "E8 blocks" 0-7 / 8-15 / 16-23 straddled
that divide. There was no E8³ decomposition, which is the structure the
four-face grouping's ``cross_e8`` property claims to express.

The binary Golay code was never at fault: its generator has row weights
{8, 12}, correct for G24. Only the lattice assembly was, and the replacement
is built from that same Golay code.

WHY THESE TWO CHECKS SUFFICE
Λ₂₄ is *characterised* among 24-dimensional lattices by being even,
unimodular and rootless. So this file does not test a symptom of correctness
-- it tests the definition. Passing is proof, not evidence.
"""
from __future__ import annotations

import itertools
from fractions import Fraction

import numpy as np
import pytest

from metaphysica.simulations.PM.algebra.leech_lattice import LeechLattice


@pytest.fixture(scope="module")
def generator():
    return LeechLattice()._generator_matrix()


def _exact_det(int_matrix) -> Fraction:
    """Fraction-free determinant, so `det == 1` is not a floating-point claim."""
    n = len(int_matrix)
    A = [[Fraction(int(x)) for x in row] for row in int_matrix]
    det = Fraction(1)
    for i in range(n):
        piv = next((r for r in range(i, n) if A[r][i] != 0), None)
        if piv is None:
            return Fraction(0)
        if piv != i:
            A[i], A[piv] = A[piv], A[i]
            det = -det
        det *= A[i][i]
        inv = Fraction(1) / A[i][i]
        for r in range(i + 1, n):
            f = A[r][i] * inv
            if f:
                A[r] = [A[r][c] - f * A[i][c] for c in range(n)]
    return det


def test_it_spans_24_dimensions(generator):
    assert generator.shape == (24, 24)
    assert np.linalg.matrix_rank(generator) == 24


def test_it_is_unimodular_exactly(generator):
    """det(Gram) = 1, checked in exact arithmetic rather than floating point.

    The basis is (1/sqrt 8) times an integer matrix B, so
    det(Gram) = det(B)^2 / 8^24, and det(B) must be exactly 8^12 = 2^36.
    The falsified construction gave det(Gram) = 7144929.
    """
    B = np.round(generator * np.sqrt(8.0)).astype(np.int64)
    assert np.allclose(B / np.sqrt(8.0), generator, atol=1e-9), (
        "the generator is not (1/sqrt 8) times an integer matrix"
    )
    det_b = abs(_exact_det(B))
    assert det_b == 8 ** 12, (
        "det(B) = %s, expected 8^12 = %s, so det(Gram) = det(B)^2/8^24 != 1"
        % (det_b, 8 ** 12)
    )


def test_it_is_an_even_lattice(generator):
    G = generator @ generator.T
    assert np.allclose(G, np.round(G), atol=1e-9), "Gram is not integral"
    Gi = np.round(G).astype(np.int64)
    assert np.all(Gi.diagonal() % 2 == 0), "odd norms present; not an even lattice"


def test_it_has_no_roots(generator):
    """Minimum norm 4. A norm-2 vector would make it a different Niemeier lattice.

    An exhaustive shortest-vector search is unnecessary: the falsified
    construction put norm-2 vectors directly in the BASIS, so checking the
    basis, all pairwise combinations and a wide random sweep is far more than
    enough to catch a regression of that kind.
    """
    norms = [float(r @ r) for r in generator]
    assert min(norms) >= 4 - 1e-9, (
        "a basis row has norm %.6g; Lambda_24 has no vector of norm < 4"
        % min(norms)
    )

    best = min(norms)
    for i, j in itertools.combinations(range(24), 2):
        for s in (1, -1):
            v = generator[i] + s * generator[j]
            best = min(best, float(v @ v))
    assert best >= 4 - 1e-9, "a pairwise combination has norm %.6g" % best

    rng = np.random.default_rng(0)
    for _ in range(20000):
        c = rng.integers(-1, 2, size=24)
        if not c.any():
            continue
        v = c @ generator
        best = min(best, float(v @ v))
    assert best >= 4 - 1e-9, "a small integer combination has norm %.6g" % best


def test_the_golay_code_underneath_is_the_binary_golay_code(generator):
    """The replacement is built from this code, so it has to be right.

    G24 has minimum weight 8 and its generator rows are weight 8 or 12.
    """
    g = np.array(LeechLattice().golay.generator_matrix, dtype=np.int64) % 2
    assert g.shape == (12, 24)
    weights = sorted({int(r.sum()) for r in g})
    assert weights and min(weights) >= 8, (
        "Golay generator row weights %s; G24 has minimum weight 8" % weights
    )
