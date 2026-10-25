"""Gauge content of flat G2 orbifolds T^7/Gamma (decision D-028 scan).

WHAT THIS MODULE DOES
=====================
For a finite group Gamma of affine isometries of R^7/Lambda that preserve the
flat G2 form phi0, it computes, exactly:

  * the fixed locus of every non-identity element, as a union of rational
    subtori u0 + span(B) in the lattice coordinates u (x = L u), found by a
    Smith normal form solve of (M - I) u = -c mod Z^7;
  * the Gamma-orbits of those loci (the singular components of the quotient),
    their pointwise stabiliser H (acting on the normal space) and setwise
    stabiliser S (acting on the locus);
  * the type of each stratum: A_{k-1} (R^3 x C^2/Z_k, cyclic H of order k on a
    3-torus), other codimension-4 strata, circle strata, and codimension-7
    points (a point whose stabiliser has no fixed vector);
  * the gauge group at the orbifold point (SU(k) per A_{k-1} orbit), b1 of
    each locus (adjoint chirals), and the Betti numbers after resolving the
    A-type loci that are not kept singular.

RESOLUTION FORMULA
==================
Joyce, Compact Manifolds with Special Holonomy (OUP 2000), Ch. 11-12:
H^k(Y) = H^k(T^7/Gamma) + sum over resolved components L_j of
(k_j - 1) * H^{k-2}(L_j) for a C^2/Z_{k_j} resolved by k_j - 1 exceptional
curves (k_j = 2 is the Eguchi-Hanson case used by joyce_resolution). H^*(L_j)
is the stabiliser-invariant part of H^*(T^3); if an element of the setwise
stabiliser inverts the cyclic generator it swaps exceptional curves and the
trace of that permutation replaces k_j - 1. The formula is stated only for
pairwise disjoint A-type loci; any other configuration is reported as
betti = None, never guessed.

LIMITS
======
Codimension-7 points are detected (stabiliser with no fixed vector) but their
local type (C^3/Z_N or otherwise) is not classified here. Only the flat
orbifold is analysed.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

DEN = 12
MAX_ORDER = 1536
_FULL_CHECK_MAX = 128  # O(n^2) closure audit only for small groups
_TOL = 1e-8
_N = 7


class ScanError(ValueError):
    """An element or group that is not admissible; the message says why."""


# --------------------------------------------------------------- lattices

class Lattice:
    """R^7 / (L Z^7); the columns of L are the basis in Euclidean coordinates."""

    def __init__(self, name: str, L: np.ndarray):
        self.name = name
        self.L = np.asarray(L, dtype=float)
        self.Linv = np.linalg.inv(self.L)


def z7_lattice() -> Lattice:
    return Lattice("Z7", np.eye(_N))


def hex_lattice(pairs: Sequence[Tuple[int, int]]) -> Lattice:
    """A2 (hexagonal) in each coordinate plane (p, q) of `pairs`, Z elsewhere."""
    L = np.eye(_N)
    for p, q in pairs:
        L[p, q], L[q, q] = -0.5, np.sqrt(3.0) / 2.0
    return Lattice("A2x%d" % len(pairs), L)


# ---------------------------------------------------------- phi and G2 tests

def phi_active() -> np.ndarray:
    """The active phi0 convention of the engine (g2_closure.phi_for)."""
    from metaphysica.simulations.PM.geometry.g2_closure import phi_for

    return phi_for()


def preserves_phi(A: np.ndarray, phi: np.ndarray) -> bool:
    """A.phi0 = phi0, i.e. A is in G2 (given A orthogonal)."""
    out = np.einsum("ia,jb,kc,abc->ijk", A, A, A, phi, optimize=True)
    return bool(np.allclose(out, phi, atol=_TOL))


# ----------------------------------------------------------- affine elements

class Iso:
    """x -> M x + c/DEN in lattice coordinates u (M integer, c mod DEN)."""

    __slots__ = ("M", "c", "key")

    def __init__(self, M, c):
        self.M = np.asarray(M, dtype=np.int64)
        self.c = np.asarray(c, dtype=np.int64) % DEN
        self.key = (self.M.tobytes(), self.c.tobytes())

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)


def identity() -> Iso:
    return Iso(np.eye(_N, dtype=np.int64), np.zeros(_N, dtype=np.int64))


def compose(g: Iso, h: Iso) -> Iso:
    """g after h."""
    return Iso(g.M @ h.M, g.M @ h.c + g.c)


def inverse(g: Iso) -> Iso:
    Minv = np.rint(np.linalg.inv(g.M)).astype(np.int64)
    return Iso(Minv, -(Minv @ g.c))


def from_euclid(A, b, lat: Lattice, phi: np.ndarray) -> Iso:
    """Build an isometry (A, b) of R^7/Lambda, failing early with the reason.

    Checks A orthogonal, A.phi0 = phi0 (A in G2) and Lambda-compatibility
    (A L = L M with M integer; b in Lambda/DEN).
    """
    A = np.asarray(A, dtype=float)
    if not np.allclose(A @ A.T, np.eye(_N), atol=_TOL):
        raise ScanError("A is not orthogonal")
    if not preserves_phi(A, phi):
        raise ScanError("A does not preserve phi0 (A not in G2)")
    M = lat.Linv @ A @ lat.L
    if not np.allclose(M, np.rint(M), atol=_TOL):
        raise ScanError("A L != L M with integer M: not lattice compatible")
    c = lat.Linv @ np.asarray(b, dtype=float) * DEN
    if not np.allclose(c, np.rint(c), atol=1e-6):
        raise ScanError("translation not in Lambda/%d" % DEN)
    return Iso(np.rint(M), np.rint(c))


def euclid_A(g: Iso, lat: Lattice) -> np.ndarray:
    return lat.L @ g.M @ lat.Linv


def element_order(g: Iso, limit: int = MAX_ORDER) -> int:
    e, cur = identity(), g
    for n in range(1, limit + 1):
        if cur == e:
            return n
        cur = compose(g, cur)
    raise ScanError("element order exceeds %d" % limit)


# --------------------------------------------------------------- group closure

def close_group(gens: Sequence[Iso], limit: int = MAX_ORDER) -> List[Iso]:
    """Group generated by `gens` modulo Lambda; raises if order > limit."""
    seen = {identity().key: identity()}
    frontier = [identity()]
    while frontier:
        nxt = []
        for x in frontier:
            for g in gens:
                y = compose(g, x)
                if y.key not in seen:
                    seen[y.key] = y
                    nxt.append(y)
        if len(seen) > limit:
            raise ScanError("group order exceeds %d (no closure)" % limit)
        frontier = nxt
    elems = list(seen.values())
    if len(elems) <= _FULL_CHECK_MAX and not _is_closed(elems):
        raise ScanError("generated set is not closed under products")
    return elems


def _is_closed(elems: Sequence[Iso]) -> bool:
    keys = {g.key for g in elems}
    return all(compose(a, b).key in keys for a in elems for b in elems)


# ---------------------------------------------------- Smith form, torus solve

def _swap_rows(A, U, i, j):
    A[i], A[j] = A[j], A[i]
    U[i], U[j] = U[j], U[i]


def _swap_cols(A, V, i, j):
    for M in (A, V):
        for row in M:
            row[i], row[j] = row[j], row[i]


def _row_add(A, U, i, r, f):
    """row_i += f row_r in A and in the left transform U."""
    for M in (A, U):
        M[i] = [x + f * y for x, y in zip(M[i], M[r])]


def _col_add(A, V, j, r, f):
    """col_j += f col_r in A and in the right transform V."""
    for M in (A, V):
        for row in M:
            row[j] += f * row[r]


def _pivot(A, r):
    best = None
    for i in range(r, len(A)):
        for j in range(r, len(A[0])):
            v = abs(A[i][j])
            if v and (best is None or v < best[0]):
                best = (v, i, j)
    return None if best is None else (best[1], best[2])


def _clear(A, U, V, r) -> bool:
    p = A[r][r]
    for i in range(r + 1, len(A)):
        q = A[i][r] // p
        if q:
            _row_add(A, U, i, r, -q)
    for j in range(r + 1, len(A[0])):
        q = A[r][j] // p
        if q:
            _col_add(A, V, j, r, -q)
    return (all(A[i][r] == 0 for i in range(r + 1, len(A)))
            and all(A[r][j] == 0 for j in range(r + 1, len(A[0]))))


def smith(A) -> Tuple[List, List, List, int]:
    """U A V = D (diagonal, not necessarily divisibility-ordered); rank."""
    A = [[int(x) for x in row] for row in A]
    m, n = len(A), len(A[0])
    U = [[int(i == j) for j in range(m)] for i in range(m)]
    V = [[int(i == j) for j in range(n)] for i in range(n)]
    r = 0
    while r < min(m, n):
        piv = _pivot(A, r)
        if piv is None:
            break
        _swap_rows(A, U, r, piv[0])
        _swap_cols(A, V, r, piv[1])
        if _clear(A, U, V, r):
            r += 1
    return U, A, V, r


def torus_solve(A, rhs: Sequence[Fraction]) -> Tuple[list, Optional[np.ndarray]]:
    """All solutions y in R^n / Z^n of A y = rhs (mod 1), A integer m x n.

    Returns (base points, B): the solution set is the union over the base
    points u0 of u0 + span(B) (B integer n x f, the free directions).
    """
    U, D, V, r = smith(A)
    m, n = len(A), len(A[0])
    t = [sum(U[i][j] * rhs[j] for j in range(m)) for i in range(m)]
    if any(t[i] % 1 != 0 for i in range(r, m)):
        return [], None
    choices = [[(t[i] + k) / D[i][i] for k in range(abs(D[i][i]))]
               for i in range(r)]
    pts = []
    for ys in itertools.product(*choices):
        y = list(ys) + [Fraction(0)] * (n - r)
        pts.append(tuple(sum(V[i][j] * y[j] for j in range(n)) % 1
                         for i in range(n)))
    return pts, np.array(V, dtype=np.int64)[:, r:]


def annihilator(B: np.ndarray) -> np.ndarray:
    """Saturated integer rows K with K B = 0 and rank = 7 - dim span(B)."""
    if B.shape[1] == 0:
        return np.eye(_N, dtype=np.int64)
    _U, _D, V, r = smith(B.T.tolist())
    return np.array(V, dtype=np.int64)[:, r:].T


# ------------------------------------------------------------------- loci

def hnf_rows(K: np.ndarray) -> Tuple[Tuple[int, ...], ...]:
    """Row Hermite normal form of an integer matrix (canonical for the row lattice)."""
    rows = [[int(x) for x in r] for r in K]
    r = 0
    for col in range(_N):
        while True:
            nz = [i for i in range(r, len(rows)) if rows[i][col]]
            if len(nz) <= 1:
                break
            i0 = min(nz, key=lambda i: abs(rows[i][col]))
            for i in nz:
                if i != i0:
                    q = rows[i][col] // rows[i0][col]
                    rows[i] = [x - q * y for x, y in zip(rows[i], rows[i0])]
        nz = [i for i in range(r, len(rows)) if rows[i][col]]
        if not nz:
            continue
        rows[r], rows[nz[0]] = rows[nz[0]], rows[r]
        if rows[r][col] < 0:
            rows[r] = [-x for x in rows[r]]
        for i in range(r):
            q = rows[i][col] // rows[r][col]
            rows[i] = [x - q * y for x, y in zip(rows[i], rows[r])]
        r += 1
    return tuple(tuple(row) for row in rows[:r])


def _finish(u0, B: np.ndarray, K: np.ndarray) -> Dict[str, Any]:
    H = hnf_rows(K)
    key = (H, tuple(sum(row[j] * u0[j] for j in range(_N)) % 1 for row in H))
    return {"u0": tuple(u0), "B": B, "K": K, "dim": B.shape[1], "key": key}


def make_locus(u0, B: np.ndarray) -> Dict[str, Any]:
    B = np.asarray(B, dtype=np.int64).reshape(_N, -1)
    return _finish(u0, B, annihilator(B))


def fixed_loci(g: Iso) -> List[Dict[str, Any]]:
    """Components of Fix(g) in R^7/Lambda (empty list if g has no fixed point)."""
    A = (g.M - np.eye(_N, dtype=np.int64)).tolist()
    rhs = [-Fraction(int(x), DEN) for x in g.c]
    pts, B = torus_solve(A, rhs)
    return [make_locus(p, B) for p in pts]


def _frac_int(vec) -> bool:
    return all(Fraction(x) % 1 == 0 for x in vec)


def contains(a: Dict, b: Dict) -> bool:
    """Locus b is contained in locus a."""
    if a["dim"] < b["dim"] or (a["K"] @ b["B"]).any():
        return False
    d = [x - y for x, y in zip(b["u0"], a["u0"])]
    return all(_frac_int([sum(int(row[j]) * d[j] for j in range(_N))])
               for row in a["K"])


def same_locus(a: Dict, b: Dict) -> bool:
    return a["key"] == b["key"]


def image_locus(h: Iso, a: Dict) -> Dict[str, Any]:
    u = [sum(int(h.M[i][j]) * a["u0"][j] for j in range(_N))
         + Fraction(int(h.c[i]), DEN) for i in range(_N)]
    Minv = np.rint(np.linalg.inv(h.M)).astype(np.int64)
    return _finish([x % 1 for x in u], h.M @ a["B"], a["K"] @ Minv)


def meet(a: Dict, b: Dict) -> List[Dict[str, Any]]:
    """Components of the intersection of two loci (possibly empty)."""
    cols = np.hstack([a["B"], -b["B"]])
    if cols.shape[1] == 0:
        return []
    rhs = [x - y for x, y in zip(b["u0"], a["u0"])]
    pts, V = torus_solve(cols.tolist(), rhs)
    da = a["dim"]
    out = []
    for t in pts:
        u = tuple((a["u0"][i] + sum(int(a["B"][i][j]) * t[j] for j in range(da)))
                  % 1 for i in range(_N))
        out.append(make_locus(u, a["B"] @ V[:da]))
    return out


def fixes_pointwise(h: Iso, loc: Dict) -> bool:
    N = h.M - np.eye(_N, dtype=np.int64)
    if (N @ loc["B"]).any():
        return False
    return _frac_int(sum(int(N[i][j]) * loc["u0"][j] for j in range(_N))
                     + Fraction(int(h.c[i]), DEN) for i in range(_N))


# --------------------------------------------------------- unique loci, orbits

def unique_loci(elems: Sequence[Iso]) -> List[Dict[str, Any]]:
    """Distinct fixed components over all non-identity elements."""
    out: Dict[Any, Dict[str, Any]] = {}
    for g in elems:
        if g == identity():
            continue
        for loc in fixed_loci(g):
            out.setdefault(loc["key"], loc)
    return list(out.values())


def orbits_of_loci(elems: Sequence[Iso], loci: List[Dict]) -> List[List[int]]:
    """Gamma-orbits of loci, as lists of indices into `loci`."""
    index = {loc["key"]: i for i, loc in enumerate(loci)}
    left, orbits = set(range(len(loci))), []
    while left:
        i = min(left)
        orb = {index[image_locus(h, loci[i])["key"]] for h in elems}
        left -= orb
        orbits.append(sorted(orb))
    return orbits


# ---------------------------------------------------------- Euclidean frames

def _frames(loc: Dict, lat: Lattice) -> Tuple[np.ndarray, np.ndarray]:
    """Orthonormal bases (tangent, normal) of the locus in R^7."""
    d = loc["dim"]
    if d == 0:
        return np.zeros((_N, 0)), np.eye(_N)
    q, _ = np.linalg.qr(lat.L @ loc["B"].astype(float), mode="complete")
    return q[:, :d], q[:, d:]


def _elem_sym(Amat: np.ndarray, p: int) -> float:
    """p-th elementary symmetric function of the eigenvalues (trace of Lambda^p)."""
    if Amat.shape[0] == 0:
        return 1.0 if p == 0 else 0.0
    if p > Amat.shape[0]:
        return 0.0
    return float(((-1) ** p) * np.poly(Amat)[p].real)


def _avg_forms(mats: Sequence[np.ndarray], dim: int,
               weights: Optional[Sequence[float]] = None) -> List[float]:
    w = list(weights) if weights is not None else [1.0] * len(mats)
    return [sum(wi * _elem_sym(m, p) for wi, m in zip(w, mats)) / len(mats)
            for p in range(dim + 1)]


def _as_ints(vals: Sequence[float]) -> Tuple[int, ...]:
    out = tuple(int(round(v)) for v in vals)
    if any(abs(v - o) > 1e-6 for v, o in zip(vals, out)):
        raise ScanError("non-integer invariant dimension %r" % (vals,))
    return out


def flat_betti(elems: Sequence[Iso], lat: Lattice) -> Tuple[int, ...]:
    """b_0..b_7 of T^7/Gamma: Gamma-invariant constant forms."""
    mats = [euclid_A(g, lat) for g in elems]
    return _as_ints(_avg_forms(mats, _N))


# ---------------------------------------------------------- stratum analysis

def _is_cyclic(H: Sequence[Iso]) -> bool:
    return any(element_order(h) == len(H) for h in H)


def _stratum_type(d: int, H: Sequence[Iso]) -> Dict[str, Any]:
    k, cyc = len(H), _is_cyclic(H)
    if d == 3 and cyc:
        return {"kind": "A", "k": k, "label": "A%d" % (k - 1)}
    if d == 3:
        return {"kind": "ADE-noncyclic", "k": k, "label": "D/E(|H|=%d)" % k}
    if d == 0:
        return {"kind": "codim7", "k": k, "label": "pt(|H|=%d)" % k}
    kind = "circle" if d == 1 else "other-dim%d" % d
    return {"kind": kind, "k": k,
            "label": ("C3/Z%d" % k if cyc else "nonabelian(|H|=%d)" % k)
            if d == 1 else "dim%d(|H|=%d)" % (d, k)}


def _tau(h: Iso, gen: Iso, k: int) -> int:
    """Trace of h on the k-1 exceptional classes of C^2/Z_k (identity or swap)."""
    conj = compose(compose(h, gen), inverse(h))
    cur = identity()
    for j in range(1, k):
        cur = compose(gen, cur)
        if cur == conj:
            if j == 1:
                return k - 1
            if j == k - 1:
                return (k - 1) % 2
            raise ScanError("stabiliser acts on exceptional curves non-simply")
    raise ScanError("stabiliser does not normalise the local group")


def _normal_free(H: Sequence[Iso], Qn: np.ndarray, lat: Lattice) -> bool:
    """Every non-identity element of H has no fixed normal vector."""
    for h in H:
        if h == identity():
            continue
        An = Qn.T @ euclid_A(h, lat) @ Qn
        if np.linalg.matrix_rank(An - np.eye(An.shape[0]), tol=1e-7) < An.shape[0]:
            return False
    return True


def stratum_row(elems: Sequence[Iso], loc: Dict, lat: Lattice,
                orbit_size: int) -> Dict[str, Any]:
    """Type, stabilisers, cohomology and resolution contribution of one orbit."""
    Qv, Qn = _frames(loc, lat)
    H = [h for h in elems if fixes_pointwise(h, loc)]
    S = [h for h in elems if same_locus(image_locus(h, loc), loc)]
    row = _stratum_type(loc["dim"], H)
    row.update({"dim": loc["dim"], "orbit_size": orbit_size,
                "stabiliser_order": len(S), "free_normal": _normal_free(H, Qn, lat)})
    mats = [Qv.T @ euclid_A(h, lat) @ Qv for h in S]
    row["betti"] = _as_ints(_avg_forms(mats, loc["dim"]))
    row["b1"] = row["betti"][1] if loc["dim"] >= 1 else 0
    if row["kind"] == "A":
        gen = next(h for h in H if element_order(h) == len(H))
        taus = [_tau(h, gen, row["k"]) for h in S]
        row["exceptional"] = _avg_forms(mats, loc["dim"], taus)
    return row


# ----------------------------------------------------------- codimension 7

def point_loci(reps: List[Dict], loci: List[Dict], rounds: int = 3) -> List[Dict]:
    """0-dimensional loci reached by intersecting orbit representatives with
    the loci repeatedly (every point is Gamma-equivalent to one on a rep)."""
    pool = {l["key"]: l for l in loci}
    front = [(a, b) for a in reps for b in loci if a["key"] != b["key"]]
    for _ in range(rounds):
        new = {}
        for a, b in front:
            for m in meet(a, b):
                if m["key"] not in pool and m["key"] not in new:
                    new[m["key"]] = m
        if not new:
            break
        pool.update(new)
        front = [(m, l) for m in new.values() for l in pool.values()
                 if m["key"] != l["key"]]
    return [p for p in pool.values() if p["dim"] == 0]


def _stab_no_fixed_vector(H: Sequence[Iso], lat: Lattice) -> bool:
    rows = [euclid_A(h, lat) - np.eye(_N) for h in H]
    return np.linalg.matrix_rank(np.vstack(rows), tol=1e-7) == _N


def codim7_points(elems: Sequence[Iso], reps: List[Dict], loci: List[Dict],
                  lat: Lattice) -> List[Dict[str, Any]]:
    """Gamma-orbits of points whose stabiliser fixes no vector."""
    pts = {}
    for p in point_loci(reps, loci):
        H = [h for h in elems if fixes_pointwise(h, p)]
        if _stab_no_fixed_vector(H, lat):
            pts[p["key"]] = (p, H)
    out, seen = [], set()
    for key, (p, H) in pts.items():
        if key in seen:
            continue
        orb = {image_locus(h, p)["key"] for h in elems}
        seen |= orb
        out.append({"orbit_size": len(orb), "stabiliser_order": len(H)})
    return out


def crossing_count(reps: List[Dict], loci: List[Dict]) -> int:
    """Pairs (orbit representative, other locus) that meet (incl. nested)."""
    return sum(1 for a in reps for b in loci
               if a["key"] != b["key"] and meet(a, b))


def row_crossings(reps: List[Dict], loci: List[Dict],
                  orbs: List[List[int]]) -> List[List[int]]:
    """For each orbit representative, the orbit indices of the other loci
    it meets (nested loci included)."""
    orb_of = {i: k for k, o in enumerate(orbs) for i in o}
    out = []
    for a in reps:
        hit = {orb_of[i] for i, b in enumerate(loci)
               if a["key"] != b["key"] and meet(a, b)}
        out.append(sorted(hit))
    return out


# ------------------------------------------------------------------- report

def _gauge(rows: Sequence[Dict]) -> Dict[str, Any]:
    a_rows = [r for r in rows if r["kind"] == "A"]
    counts: Dict[int, int] = {}
    for r in a_rows:
        counts[r["k"]] = counts.get(r["k"], 0) + 1
    other = [r["label"] for r in rows if r["kind"] != "A"]
    text = " x ".join("SU(%d)%s" % (k, "^%d" % n if n > 1 else "")
                      for k, n in sorted(counts.items())) or "none"
    return {"factors": counts, "text": text, "non_A_strata": other,
            "has_su3_su2": 2 in counts and 3 in counts}


def betti_with_keep(flat: Sequence[int], rows: Sequence[Dict],
                    keep: Sequence[int] = ()) -> Dict[int, int]:
    """Betti numbers; A-type orbits whose k is in `keep` stay singular."""
    b = {p: flat[p] for p in range(_N + 1)}
    for r in rows:
        if r["k"] in keep:
            continue
        for p, v in enumerate(r["exceptional"]):
            b[p + 2] += int(round(v))
    return b


def analyse(elems: Sequence[Iso], lat: Lattice) -> Dict[str, Any]:
    """Full D-028 record of one group (see module docstring)."""
    loci = unique_loci(elems)
    orbs = orbits_of_loci(elems, loci)
    reps = [loci[o[0]] for o in orbs]
    rows = [stratum_row(elems, loci[o[0]], lat, len(o)) for o in orbs]
    flat = flat_betti(elems, lat)
    cross = crossing_count(reps, loci)
    for r, hit in zip(rows, row_crossings(reps, loci, orbs)):
        r["crosses_orbits"] = hit
    c7 = codim7_points(elems, reps, loci, lat)
    all_a = bool(rows) and all(r["kind"] == "A" for r in rows)
    ok = all_a and cross == 0 and all(r["free_normal"] for r in rows)
    rec = {"order": len(elems), "flat_betti": flat, "strata": rows,
           "n_loci": len(loci), "gauge": _gauge(rows), "crossings": cross,
           "codim7": c7, "betti_valid": ok, "betti": None,
           "b1_values": sorted({r["b1"] for r in rows})}
    if ok:
        rec["betti"] = betti_with_keep(flat, rows)
    return rec


def a_type_ks(elems: Sequence[Iso]) -> Dict[int, int]:
    """Cheap test: k -> number of distinct 3-dimensional fixed loci whose
    pointwise stabiliser is cyclic of order k (an A_{k-1} locus, SU(k))."""
    seen: Dict[tuple, int] = {}
    e = identity()
    for g in elems:
        if g == e:
            continue
        for loc in fixed_loci(g):
            if loc["dim"] != 3 or loc["key"] in seen:
                continue
            H = [h for h in elems if fixes_pointwise(h, loc)]
            seen[loc["key"]] = len(H) if _is_cyclic(H) else 0
    out: Dict[int, int] = {}
    for k in seen.values():
        out[k] = out.get(k, 0) + 1
    return out


# ------------------------------------------------- Joyce's published example

_JOYCE_TRIPLES = (((1, 2, 3), 1), ((1, 4, 5), 1), ((1, 6, 7), 1),
                  ((2, 4, 6), 1), ((2, 5, 7), -1), ((3, 4, 7), -1),
                  ((3, 5, 6), -1))


def joyce_phi0() -> np.ndarray:
    """Joyce's phi0 = dx123 + dx145 + dx167 + dx246 - dx257 - dx347 - dx356."""
    phi = np.zeros((_N, _N, _N))
    for trip, sgn in _JOYCE_TRIPLES:
        idx = [t - 1 for t in trip]
        for perm in itertools.permutations(range(3)):
            parity = np.linalg.det(np.eye(3)[list(perm)])
            phi[tuple(idx[a] for a in perm)] = sgn * parity
    return phi


def joyce_z2_cubed() -> Tuple[Lattice, List[Iso]]:
    """Joyce's Z2^3 on T^7 = R^7/Z^7, in Joyce's phi0 frame:
    alpha = (x1,x2,x3,-x4,-x5,-x6,-x7),
    beta  = (x1,-x2,-x3,x4,x5,1/2-x6,-x7),
    gamma = (-x1,x2,-x3,x4,1/2-x5,x6,1/2-x7)."""
    lat, phi = z7_lattice(), joyce_phi0()
    spec = [({4, 5, 6, 7}, {}), ({2, 3, 6, 7}, {6: .5}),
            ({1, 3, 5, 7}, {5: .5, 7: .5})]
    gens = []
    for flips, shift in spec:
        A = np.diag([-1.0 if i + 1 in flips else 1.0 for i in range(_N)])
        b = np.zeros(_N)
        for coord, val in shift.items():
            b[coord - 1] = val
        gens.append(from_euclid(A, b, lat, phi))
    return lat, gens


# ===================================================================== scan
#
# The D-028 class (finite, sized by `class_size`): Gamma = <alpha, beta, gamma,
# delta> with alpha, beta, gamma the active canonical Z2^3 (shifts read in the
# lattice basis) and delta = (A, b) of order exactly 3 or 4 modulo Lambda:
#   (i)  A a signed permutation matrix in G2, order 3 or 4, lattice Z^7;
#   (ii) A a rotation by 2 pi/3 in two orthogonal coordinate 2-planes (angles
#        +-2 pi/3 each) on the complement of a phi0 line, lattice A2 x A2 x Z^3;
# with b = w/3 (order 3) or w/2 (order 4), w in {0,1}^7 in lattice coordinates,
# subject to delta^order = identity.

def active_generators(lat: Lattice, phi: np.ndarray) -> List[Iso]:
    """alpha, beta, gamma of the active canonical point."""
    from metaphysica.simulations.PM.geometry.intersection_tensor import (
        canonical_point,
    )

    cp = canonical_point()
    out = []
    for bits in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        eps, s = cp["elements"][bits]
        out.append(from_euclid(np.diag(eps), lat.L @ (np.array(s) / 2.0),
                               lat, phi))
    return out


def phi_lines(phi: np.ndarray) -> List[Tuple[int, int, int]]:
    """The 7 index triples carrying phi0."""
    return sorted({tuple(sorted(t)) for t in map(tuple, np.argwhere(phi != 0))
                   if len(set(t)) == 3})


def signed_perms_in_g2(phi: np.ndarray) -> List[np.ndarray]:
    """All signed permutation matrices preserving phi0 (expected 8 * 168)."""
    lines = {frozenset(t) for t in phi_lines(phi)}
    out = []
    for sig in itertools.permutations(range(_N)):
        if {frozenset(sig[i] for i in t) for t in lines} != lines:
            continue
        for eps in itertools.product((1, -1), repeat=_N):
            A = np.zeros((_N, _N))
            for j in range(_N):
                A[sig[j], j] = eps[j]
            if preserves_phi(A, phi):
                out.append(A)
    return out


def _mat_order(A: np.ndarray, limit: int = 12) -> int:
    cur = np.eye(_N)
    for n in range(1, limit + 1):
        cur = A @ cur
        if np.allclose(cur, np.eye(_N), atol=_TOL):
            return n
    return 0


def hex_rotations(phi: np.ndarray) -> List[Tuple[np.ndarray, Lattice]]:
    """Order-3 coordinate-plane rotations in G2 with their A2 lattices."""
    out, th = [], 2.0 * np.pi / 3.0
    for line in phi_lines(phi):
        rest = [i for i in range(_N) if i not in line]
        for pairs in ([(rest[0], rest[1]), (rest[2], rest[3])],
                      [(rest[0], rest[2]), (rest[1], rest[3])],
                      [(rest[0], rest[3]), (rest[1], rest[2])]):
            for s1, s2 in itertools.product((1, -1), repeat=2):
                A = np.eye(_N)
                for (p, q), s in zip(pairs, (s1, s2)):
                    c, sn = np.cos(s * th), np.sin(s * th)
                    A[np.ix_([p, q], [p, q])] = [[c, -sn], [sn, c]]
                if preserves_phi(A, phi):
                    out.append((A, hex_lattice(pairs)))
    return out


def candidate_A(phi: np.ndarray) -> List[Tuple[np.ndarray, Lattice, int, str]]:
    """(A, lattice, order, family) for every linear part in the class."""
    z7 = z7_lattice()
    out = []
    for A in signed_perms_in_g2(phi):
        n = _mat_order(A)
        if n in (3, 4):
            out.append((A, z7, n, "signed-perm"))
    for A, lat in hex_rotations(phi):
        out.append((A, lat, 3, "hex-rotation"))
    return out


def translations(A: np.ndarray, lat: Lattice, n: int) -> List[np.ndarray]:
    """Euclidean b = L w/den (den 3 or 2) with delta^n = identity mod Lambda."""
    den = 3 if n == 3 else 2
    M = np.rint(lat.Linv @ A @ lat.L).astype(np.int64)
    S = sum(np.linalg.matrix_power(M, j) for j in range(n))
    out = []
    for w in itertools.product((0, 1), repeat=_N):
        c = np.array(w) * (DEN // den)
        if not ((S @ c) % DEN).any():
            out.append(lat.L @ (np.array(w) / float(den)))
    return out


def class_size(phi: np.ndarray) -> Dict[str, int]:
    """How many (A, b) pairs the class contains, by family."""
    sizes: Dict[str, int] = {}
    for A, lat, n, fam in candidate_A(phi):
        sizes[fam] = sizes.get(fam, 0) + len(translations(A, lat, n))
    sizes["total"] = sum(sizes.values())
    return sizes


_NORM_CACHE: Dict[bytes, list] = {}


def normaliser(lat: Lattice, phi: np.ndarray, base: Sequence[Iso]) -> list:
    """Affine symmetries n = (P, t) of the class: P a lattice-compatible signed
    permutation in G2, t in Lambda/2, with n <base> n^-1 = <base>. Conjugating
    Gamma by n gives an equivalent orbifold with the same gauge data."""
    hit = _NORM_CACHE.get(lat.L.tobytes())
    if hit is not None:
        return hit
    gb = {g.key for g in close_group(base)}
    out = []
    for A in signed_perms_in_g2(phi):
        try:
            P = from_euclid(A, np.zeros(_N), lat, phi)
        except ScanError:
            continue
        conj = [compose(compose(P, g), inverse(P)) for g in base]
        for w in itertools.product((0, 1), repeat=_N):
            tr = np.array(w) * (DEN // 2)
            if all(Iso(h.M, h.c + tr - h.M @ tr).key in gb for h in conj):
                out.append((P, tr))
    _NORM_CACHE[lat.L.tobytes()] = out
    return out


def _conjugate_key(G: Sequence[Iso], P: Iso, tr: np.ndarray) -> frozenset:
    Pi = inverse(P)
    out = set()
    for g in G:
        h = compose(compose(P, g), Pi)
        out.add(Iso(h.M, h.c + tr - h.M @ tr).key)
    return frozenset(out)


def group_orbit_keys(G: Sequence[Iso], norm: list) -> set:
    """Keys of every conjugate of G under the class symmetries."""
    return {_conjugate_key(G, P, tr) for P, tr in norm}


def _stack(G: Sequence[Iso]) -> np.ndarray:
    """Rows [M.flatten(), c] of the elements as one int64 array."""
    return np.array([np.concatenate([g.M.ravel(), g.c]) for g in G],
                    dtype=np.int64)


def _digest(rows: np.ndarray) -> bytes:
    """Order-independent digest of a set of element rows."""
    import hashlib

    order = np.lexsort(rows.T[::-1])
    return hashlib.blake2b(np.ascontiguousarray(rows[order]).tobytes(),
                           digest_size=16).digest()


def group_digest(G: Sequence[Iso]) -> bytes:
    return _digest(_stack(G))


def group_orbit_digests(G: Sequence[Iso], norm: list) -> set:
    """Digests of every conjugate of G under the class symmetries
    (vectorised; same conjugation as `_conjugate_key`)."""
    rows = _stack(G)
    Ms = rows[:, :_N * _N].reshape(-1, _N, _N)
    cs = rows[:, _N * _N:]
    out = set()
    for P, tr in norm:
        Pi = inverse(P)
        Mh = P.M @ Ms @ Pi.M
        ch = (np.einsum("ij,nj->ni", P.M, np.einsum("nij,j->ni", Ms, Pi.c) + cs)
              + P.c)
        ch = (ch + tr - np.einsum("nij,j->ni", Mh, tr)) % DEN
        out.add(_digest(np.concatenate([Mh.reshape(len(G), -1), ch], axis=1)))
    return out


def _analyse_job(job):
    """Pool worker: rebuild the group and analyse it."""
    name, L, mats = job
    lat = Lattice(name, L)
    return analyse([Iso(M, c) for M, c in mats], lat)


def scan_classes(phi: Optional[np.ndarray] = None,
                 max_order: int = MAX_ORDER,
                 delta_orders: Sequence[int] = (3, 4)):
    """Enumerate the class: (symmetry classes of closing Gamma, tally).
    `max_order` caps the group order (fail early above it)."""
    phi = phi_active() if phi is None else phi
    known: Dict[bytes, int] = {}
    classes: List[Dict[str, Any]] = []
    tally = {"candidates": 0, "valid_candidates": 0, "distinct_groups": 0,
             "rejected": {}}
    for A, lat, n, fam in candidate_A(phi):
        if n not in delta_orders:
            continue
        base = active_generators(lat, phi)
        for b in translations(A, lat, n):
            tally["candidates"] += 1
            try:
                G = close_group(base + [from_euclid(A, b, lat, phi)], max_order)
            except ScanError as exc:
                why = "%s (delta order %d)" % (exc, n)
                tally["rejected"][why] = tally["rejected"].get(why, 0) + 1
                continue
            tally["valid_candidates"] += 1
            key = group_digest(G)
            if key not in known:
                tally["distinct_groups"] += 1
                known.update({k: len(classes) for k in group_orbit_digests(
                    G, normaliser(lat, phi, base))})
                known.setdefault(key, len(classes))
                classes.append({"G": G, "lat": lat, "family": fam,
                                "delta_order": n, "candidates": 0})
            classes[known[key]]["candidates"] += 1
    return classes, tally


def scan(phi: Optional[np.ndarray] = None, workers: int = 1,
         max_order: int = MAX_ORDER, delta_orders: Sequence[int] = (3, 4),
         analyse_limit: Optional[int] = None) -> Dict[str, Any]:
    """Run the class; one record per symmetry class of valid Gamma.
    Classes of order above `analyse_limit` are listed (order only) but not
    analysed."""
    classes, tally = scan_classes(phi, max_order, delta_orders)
    return _finish_scan(classes, tally, workers, analyse_limit)


def _finish_scan(classes, tally, workers: int,
                 analyse_limit: Optional[int] = None) -> Dict[str, Any]:
    cap = analyse_limit if analyse_limit is not None else 10 ** 9
    todo = [c for c in classes if len(c["G"]) <= cap]
    skipped = [{"order": len(c["G"]), "family": c["family"],
                "delta_order": c["delta_order"], "analysed": False}
               for c in classes if len(c["G"]) > cap]
    jobs = [(c["lat"].name, c["lat"].L, [(g.M, g.c) for g in c["G"]])
            for c in todo]
    if workers > 1:
        import multiprocessing as mp

        with mp.Pool(workers) as pool:
            recs = pool.map(_analyse_job, jobs, chunksize=1)
    else:
        recs = [_analyse_job(j) for j in jobs]
    for rec, c in zip(recs, todo):
        rec.update({"family": c["family"], "lattice": c["lat"].name,
                    "delta_order": c["delta_order"], "analysed": True,
                    "candidates": c["candidates"]})
    return {"records": recs + skipped, "n_classes": len(classes), **tally}
