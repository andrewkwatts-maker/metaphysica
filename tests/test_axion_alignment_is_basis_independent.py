"""The lattice supplies no axion alignment, and the old Q said otherwise.

WHAT THIS CAUGHT
----------------
``compute_axion_alignment_matrix`` sums over the 24 **generator rows** and
flags itself honestly::

    derivation_honest: False
    "The 11/12 ratio is an artifact of this particular Construction A
     generator, not a canonical lattice invariant."

Round 2 of the debate recorded inside that method named the fix and it was
never applied::

    "the norm-4 shell of the Leech lattice forms a spherical 11-design,
     making certain averages over all 196,560 minimal vectors
     basis-independent. ... A basis-independent alignment would use the full
     minimal vector set, not the generator matrix."

Applied, it is decisive:

===========================  ===================  ==================
source                       off-diagonal max     condition number
===========================  ===================  ==================
generator rows (24)          --                   49827
Leech minimal shell (196560) 2.5e-13              1
E8^3 root shell (720)        exactly 0            1
===========================  ===================  ==================

Both shells give Q proportional to the **identity**. KNP alignment is an
enhancement produced by OFF-DIAGONAL correlation between axion directions, so
an isotropic Q supplies none: the lattice contributes no alignment
enhancement at all, and the structure in the generator-based Q is a property
of the chosen basis.

The isotropy is forced rather than lucky. Aut(L) acts irreducibly on the span,
so ``sum_v v_a v_b`` over a complete shell must be proportional to
``delta_ab``. The diagonal entries check independently:

    Leech : 196560 * 4 / 24 * 2 = 65520
    E8^3  :    720 * 2 / 24 * 2 =   120

so the numbers are predicted from the kissing number, the norm and the
dimension alone, with no reference to any basis.
"""
from __future__ import annotations

import numpy as np
import pytest

from metaphysica.simulations.PM.algebra.leech_lattice import LeechLattice


def test_the_shell_alignment_is_isotropic_under_leech():
    lat = LeechLattice()
    if lat._lattice_choice() != "leech":
        pytest.skip("lattice_24d fork is not on the leech branch")

    res = lat.compute_axion_alignment_from_shell()
    assert res["n_vectors"] == 196560, (
        "expected the full Leech shell, got %d vectors" % res["n_vectors"]
    )
    assert res["is_diagonal"], (
        "Q is not diagonal; max off-diagonal %g" % res["max_abs_offdiagonal"]
    )
    assert res["alignment_enhancement"] is False
    assert res["derivation_honest"] is True

    # every diagonal entry equals kissing * norm / dim * 2, predicted with no
    # reference to a basis
    expected = 196560 * 4 / 24 * 2
    diag = np.diag(np.asarray(res["Q"]))
    assert np.allclose(diag, expected, rtol=1e-9), (
        "diagonal %g..%g, expected %g" % (diag.min(), diag.max(), expected)
    )


def test_the_shell_alignment_is_isotropic_under_e8x3():
    """The other fork branch must reach the same conclusion by itself."""
    lat = LeechLattice()
    V = lat._niemeier_e8x3_generator()      # force the branch's geometry
    assert V.shape == (24, 24)

    # build the E8^3 shell directly rather than via the env switch
    import itertools
    E8 = lat._e8_basis()
    Einv = np.linalg.inv(E8)

    def in_e8(v):
        c = v @ Einv
        return np.allclose(c, np.round(c), atol=1e-9)

    block = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1.0, -1.0):
            for sj in (1.0, -1.0):
                v = np.zeros(8)
                v[i], v[j] = si, sj
                if in_e8(v):
                    block.append(v)
    for signs in itertools.product((0.5, -0.5), repeat=8):
        v = np.array(signs)
        if abs(v @ v - 2.0) > 1e-12 or sum(1 for s in signs if s < 0) % 2:
            continue
        if in_e8(v):
            block.append(v)
    assert len(block) == 240, "E8 has 240 roots, found %d" % len(block)

    shell = []
    for k in range(3):
        for b in block:
            v = np.zeros(24)
            v[8 * k:8 * (k + 1)] = b
            shell.append(v)
    S = np.array(shell)
    assert len(S) == 720

    Q = np.zeros((12, 12))
    for i in range(12):
        ci = slice(2 * i, 2 * i + 2)
        for j in range(12):
            cj = slice(2 * j, 2 * j + 2)
            Q[i, j] = float(np.sum(S[:, ci] * S[:, cj]))

    off = Q - np.diag(np.diag(Q))
    assert np.abs(off).max() == 0.0, "E8^3 shell Q is not exactly diagonal"
    expected = 720 * 2 / 24 * 2
    assert np.allclose(np.diag(Q), expected), (
        "E8^3 diagonal should be %g" % expected
    )


def test_the_generator_based_matrix_is_anisotropic_and_says_so():
    """The contrast is the finding, so both halves have to hold.

    If the generator-based Q ever came out isotropic too, the claim that its
    structure is a basis artifact would lose its evidence.
    """
    lat = LeechLattice()
    branch = lat._lattice_choice()
    res = lat.compute_axion_alignment_matrix()
    Q = np.asarray(res["Q"])
    off = Q - np.diag(np.diag(Q))
    eig = np.linalg.eigvalsh(Q)
    kappa = float(eig.max() / eig.min())

    assert res["derivation_honest"] is False, (
        "the generator-based matrix must keep declaring itself basis-dependent"
    )
    assert res.get("superseded_by") == "compute_axion_alignment_from_shell", (
        "it should point at the basis-independent computation"
    )

    # How BADLY conditioned depends on the lattice, and that is itself the
    # finding. Measured: Construction A gives max off-diagonal 26729.8 and
    # condition 49827; the block-diagonal E8^3 basis gives 0.5 and 4.617.
    # Both are anisotropic -- neither matches the shell, which is exactly
    # isotropic with condition 1 on both branches.
    assert kappa > 1.0 + 1e-9, (
        "the generator-based Q must differ from the shell result, or there is "
        "nothing to contrast; got condition number %g on branch %r"
        % (kappa, branch)
    )
    if branch == "leech":
        assert np.abs(off).max() > 1.0
        assert kappa > 100.0, (
            "Construction A should be badly conditioned (was ~5e4); got %g"
            % kappa
        )
    else:
        # E8^3: block-diagonal, so the artifact is small but non-zero.
        assert kappa < 100.0, (
            "the E8^3 generator is block-diagonal and was measured at ~4.6; "
            "got %g" % kappa
        )


def test_isotropy_means_no_knp_enhancement():
    """State the physics as an assertion so it cannot quietly be reversed.

    KNP alignment enhances the effective decay constant through off-diagonal
    correlation. Q proportional to the identity has none, so the enhancement
    factor over the naive sqrt(N) counting is exactly 1.
    """
    res = LeechLattice().compute_axion_alignment_from_shell()
    Q = np.asarray(res["Q"])
    eig = np.linalg.eigvalsh(Q)
    assert res["condition_number"] == pytest.approx(1.0, abs=1e-6), (
        "an isotropic Q has condition number 1; got %r" % res["condition_number"]
    )
    assert eig.max() == pytest.approx(eig.min(), rel=1e-9)
    assert res["alignment_enhancement"] is False
