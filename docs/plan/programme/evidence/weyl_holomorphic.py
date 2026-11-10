"""Holomorphic (Majorana-type) kinetic bilinear Psi^T C Gamma^M d_M Psi for one Weyl spinor.

Non-zero for anticommuting Psi only if P_L^T C Gamma^M P_L is non-zero and SYMMETRIC.
Also the holomorphic mass bilinear Psi^T C Psi (needs antisymmetric and non-zero).
"""
import sys
from functools import reduce
import numpy as np
import scipy.sparse as sp

SX = sp.csr_matrix(np.array([[0, 1], [1, 0]], dtype=complex))
SY = sp.csr_matrix(np.array([[0, -1j], [1j, 0]], dtype=complex))
SZ = sp.csr_matrix(np.array([[1, 0], [0, -1]], dtype=complex))
I2 = sp.identity(2, dtype=complex, format="csr")
kron = lambda ms: reduce(lambda a, b: sp.kron(a, b, format="csr"), ms)
amax = lambda m: float(abs(m).max()) if m.nnz else 0.0


def gammas(s, t):
    k = (s + t) // 2
    eu = []
    for i in range(k):
        eu.append(kron([SZ] * i + [SX] + [I2] * (k - i - 1)))
        eu.append(kron([SZ] * i + [SY] + [I2] * (k - i - 1)))
    return [g for g in eu[:s]] + [1j * g for g in eu[s:]], kron([SZ] * k)


def sym_class(m):
    if amax(m) < 1e-12:
        return "zero"
    if amax(m - m.T) < 1e-12:
        return "sym"
    if amax(m + m.T) < 1e-12:
        return "antisym"
    return "mixed"


def report(s, t):
    gam, chi = gammas(s, t)
    n = gam[0].shape[0]
    PL = (sp.identity(n, dtype=complex) + chi) / 2
    symm = [g for g in gam if amax(g - g.T) < 1e-12]
    anti = [g for g in gam if amax(g + g.T) < 1e-12]
    for name, fac in (("C=prod(sym)", symm), ("C=prod(antisym)", anti)):
        C = reduce(lambda a, b: a @ b, fac)
        Cinv = C.getH()  # C is unitary (product of unitaries)
        sgn = {round(float((C @ g @ Cinv).multiply(g.T.conj()).sum().real / n)) for g in gam}
        kin = {sym_class(PL.T @ C @ g @ PL) for g in gam}
        mass = sym_class(PL.T @ C @ PL)
        print("(%2d,%d) D=%2d %-16s C G C^-1 = %s G^T   LL kinetic: %s   LL mass: %s"
              % (s, t, s + t, name, sorted(sgn), sorted(kin), mass))


for sig in [(3, 1), (9, 1), (8, 2), (1, 1)] + ([(24, 2)] if "--full" in sys.argv else []):
    report(*sig)
