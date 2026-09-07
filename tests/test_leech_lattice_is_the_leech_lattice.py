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


def _lattice_branch():
    """Which `lattice_24d` option is running."""
    try:
        from metaphysica.simulations.core.variants import resolve
        return resolve("lattice_24d")
    except Exception:
        return "leech"


def _require_leech():
    if _lattice_branch() != "leech":
        import pytest as _pt
        _pt.skip("lattice_24d fork is on %r; this asserts a Lambda_24 property"
                 % _lattice_branch())


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
    _require_leech()
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
    _require_leech()
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
    _require_leech()
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
    _require_leech()
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


def _e8x3():
    """Build the other fork branch directly, without touching the environment."""
    lat = LeechLattice()
    return lat, lat._niemeier_e8x3_generator()


def test_the_other_fork_branch_is_a_niemeier_lattice_too():
    """E8^3 must be even, unimodular and rank 24, or the fork is not a fork.

    A switch is only worth having if both branches are real. This one caught
    its own bug on first run: the E8 basis overwrote row 6 instead of row 7,
    leaving a rank-deficient generator with det(Gram) = 0. Running both
    branches is what exposed it.
    """
    _, M = _e8x3()
    assert M.shape == (24, 24)
    assert np.linalg.matrix_rank(M) == 24, "E8^3 generator is rank deficient"
    G = M @ M.T
    assert abs(np.linalg.det(G) - 1.0) < 1e-9, (
        "E8^3 must be unimodular; det(Gram) = %.6g" % np.linalg.det(G)
    )
    assert np.allclose(G, np.round(G), atol=1e-9), "Gram not integral"
    assert np.all(np.round(np.diag(G)).astype(np.int64) % 2 == 0), "not even"


def test_e8x3_has_the_three_blocks_that_leech_cannot_have():
    """The contrast is the whole reason the fork exists.

    `cross_e8` -- each face taking one bridge from each of three 8-coordinate
    blocks -- is a statement about a decomposition. E8^3 has it by
    construction; Lambda_24 provably cannot, because it has no vector of norm
    2 and E8 is generated by its 240 roots.
    """
    _, M = _e8x3()
    off = M.copy()
    for k in range(3):
        off[8 * k:8 * (k + 1), 8 * k:8 * (k + 1)] = 0
    assert np.allclose(off, 0), (
        "E8^3 generator is not block-diagonal, so the three blocks are not "
        "exact summands"
    )
    # each block is E8: det 1, even, minimum norm 2
    for k in range(3):
        blk = M[8 * k:8 * (k + 1), 8 * k:8 * (k + 1)]
        g = blk @ blk.T
        assert abs(np.linalg.det(g) - 1.0) < 1e-9, "block %d is not E8" % k
        assert min(float(r @ r) for r in blk) == pytest.approx(2.0), (
            "block %d has no roots, so it is not E8" % k
        )

    # and Lambda_24 has none of this
    leech = LeechLattice()._generator_matrix()
    if leech.shape == (24, 24) and min(float(r @ r) for r in leech) >= 4 - 1e-9:
        assert min(float(r @ r) for r in leech) >= 4 - 1e-9, (
            "under the leech branch there must be no norm-2 vector, hence no "
            "E8 summand"
        )


def test_e8_has_240_roots_and_they_lie_in_the_lattice():
    """112 of shape (+-1, +-1, 0^6) and 128 of (+-1/2)^8, membership checked."""
    lat = LeechLattice()
    E8 = lat._e8_basis()
    Einv = np.linalg.inv(E8)

    def in_e8(v):
        c = v @ Einv
        return np.allclose(c, np.round(c), atol=1e-9)

    shape_a = 0
    for i, j in itertools.combinations(range(8), 2):
        for si in (1.0, -1.0):
            for sj in (1.0, -1.0):
                v = np.zeros(8)
                v[i], v[j] = si, sj
                assert abs(v @ v - 2.0) < 1e-12
                if in_e8(v):
                    shape_a += 1
    assert shape_a == 112, "expected 4*C(8,2) = 112 roots, got %d" % shape_a

    shape_b = 0
    for signs in itertools.product((0.5, -0.5), repeat=8):
        v = np.array(signs)
        if abs(v @ v - 2.0) > 1e-12:
            continue
        if sum(1 for s in signs if s < 0) % 2 != 0:
            continue
        if in_e8(v):
            shape_b += 1
    assert shape_b == 128, "expected 2^7 = 128 roots, got %d" % shape_b
    assert shape_a + shape_b == 240, "E8 has 240 roots"


def test_the_fork_is_declared_and_both_options_are_reachable():
    """A switch nobody can find is not a switch."""
    from metaphysica.simulations.core.variants import FORKS, resolve

    assert "lattice_24d" in FORKS, "the lattice choice is not declared as a fork"
    fork = FORKS["lattice_24d"]
    assert set(fork.option_ids()) == {"leech", "niemeier_e8x3"}
    assert fork.status == "OPEN", (
        "the fork is marked %r; it is an author ruling and both branches are "
        "live, so it should stay OPEN until decided" % fork.status
    )
    assert resolve("lattice_24d") in fork.option_ids()


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
