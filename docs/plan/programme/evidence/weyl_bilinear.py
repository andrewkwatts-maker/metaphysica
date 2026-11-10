"""Does a single Weyl spinor of Cl(s,t) have a non-zero Hermitian kinetic or mass bilinear?

Mostly-plus: spacelike gammas square to +1 (Hermitian), timelike to -1 (anti-Hermitian).
Dirac adjoint: Psi-bar = Psi^dagger A, A = product of the timelike gammas (the Spin(s,t)_0
invariant sesquilinear form). Reports max |P_L^dag A Gamma^M P_L| and max |P_L^dag A P_L|.
"""
import sys
from functools import reduce
import numpy as np
import scipy.sparse as sp

SX = sp.csr_matrix(np.array([[0, 1], [1, 0]], dtype=complex))
SY = sp.csr_matrix(np.array([[0, -1j], [1j, 0]], dtype=complex))
SZ = sp.csr_matrix(np.array([[1, 0], [0, -1]], dtype=complex))
I2 = sp.identity(2, dtype=complex, format="csr")


def kron(ms):
    return reduce(lambda a, b: sp.kron(a, b, format="csr"), ms)


def euclid_gammas(d):
    """2k Hermitian gammas squaring to +1, dimension 2^k."""
    k = d // 2
    out = []
    for i in range(k):
        out.append(kron([SZ] * i + [SX] + [I2] * (k - i - 1)))
        out.append(kron([SZ] * i + [SY] + [I2] * (k - i - 1)))
    return out, kron([SZ] * k)


def amax(m):
    return float(abs(m).max()) if m.nnz else 0.0


def report(s, t):
    d = s + t
    eu, chir = euclid_gammas(d)
    gam = [g for g in eu[:s]] + [1j * g for g in eu[s:]]
    n = gam[0].shape[0]
    for i, g in enumerate(gam):
        sq = (g @ g)
        want = 1 if i < s else -1
        assert amax(sq - want * sp.identity(n)) < 1e-12
    A = reduce(lambda a, b: a @ b, gam[s:])
    # invariance: A G A^-1 = +- G^dagger, the same sign for every M
    signs = set()
    Ainv = sp.csr_matrix(np.linalg.inv(A.toarray())) if n <= 64 else None
    PL = (sp.identity(n, dtype=complex) + chir) / 2
    kin = max(amax(PL.getH() @ A @ g @ PL) for g in gam)
    mass = amax(PL.getH() @ A @ PL)
    comm = amax(A @ chir - chir @ A)
    print("(%2d,%d) D=%2d dim=%5d  s-t mod 8=%d  [A,chi]=0:%-5s  kinetic(LL)=%g  mass(LL)=%g"
          % (s, t, d, n, (s - t) % 8, comm < 1e-12, kin, mass))


for sig in [(3, 1), (9, 1), (5, 1), (2, 2), (4, 2), (8, 2), (10, 2)] + \
        ([(24, 2)] if "--full" in sys.argv else []):
    report(*sig)
