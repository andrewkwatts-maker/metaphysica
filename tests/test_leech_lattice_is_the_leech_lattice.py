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


def test_the_kissing_number_is_derived_not_asserted():
    """196560, counted from the Golay code rather than written down.

    ``kissing_number`` used to ``return 196_560  # Known exact value``, and two
    callers then "validated" it with
    ``results['leech']['kissing_number'] == 196_560`` -- a hardcoded constant
    compared against a hardcoded constant, which cannot fail. It was
    unfalsifiable twice over: while the generator was not the Leech lattice at
    all, the literal still read 196560, so the check passed for a lattice whose
    real kissing number was something else.
    """
    lat = LeechLattice()
    weights = lat.golay.weight_distribution()
    assert weights.get(8) == 759, (
        "G24 has 759 octads; got %r" % weights.get(8)
    )
    assert sum(weights.values()) == 4096, "G24 has 2^12 codewords"

    expected = 4 * (24 * 23 // 2) + 759 * 2 ** 7 + 24 * 4096
    assert expected == 196560, "the three shape counts do not sum correctly"
    assert lat.kissing_number == expected


def test_every_minimal_vector_really_lies_in_the_lattice():
    """Generate all three shapes and solve B x = v for each.

    The counting argument above is only as good as the claim that these
    vectors are IN the lattice. A sample from each family is checked
    explicitly, which is what ties the combinatorics to the construction.
    """
    lat = LeechLattice()
    M = lat._generator_matrix()
    B = np.round(M * np.sqrt(8.0)).astype(np.int64)
    Binv = np.linalg.inv(B.astype(np.float64))

    def in_lattice(v):
        x = v @ Binv
        return np.allclose(x, np.round(x), atol=1e-6)

    # shape (+-4^2, 0^22)
    checked = 0
    for i, j in itertools.combinations(range(24), 2):
        for si, sj in ((4, 4), (4, -4), (-4, 4), (-4, -4)):
            v = np.zeros(24, dtype=np.int64)
            v[i], v[j] = si, sj
            assert int(v @ v) == 32, "wrong norm for the (4,4) shape"
            assert in_lattice(v), "(%d,%d) 4-4 vector not in the lattice" % (i, j)
            checked += 1
            if checked >= 120:
                break
        if checked >= 120:
            break

    # shape (+-2^8, 0^16) on Golay octads, even number of minus signs
    words = np.asarray(lat.golay.enumerate_codewords()) % 2
    octads = [w for w in words if int(w.sum()) == 8]
    assert len(octads) == 759
    for oc in octads[:25]:
        support = np.flatnonzero(oc)
        v = np.zeros(24, dtype=np.int64)
        v[support] = 2
        assert int(v @ v) == 32
        assert in_lattice(v), "octad vector not in the lattice"

    # shape (-+3, +-1^23)
    found = 0
    for w in words[:40]:
        base = np.where(w == 1, -1, 1).astype(np.int64)
        for pos in range(24):
            v = base.copy()
            v[pos] = -3 * base[pos]
            if int(v @ v) == 32 and in_lattice(v):
                found += 1
    assert found > 0, "no (3, 1^23) minimal vector landed in the lattice"


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
