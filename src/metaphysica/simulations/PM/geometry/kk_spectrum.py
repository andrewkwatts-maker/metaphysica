"""Exact scalar-Laplacian spectrum on the flat orbifold T^7/Gamma (task C5).

T^7 = R^7/Z^7 with diagonal radii R_i (moduli).  Modes e^{2 pi i k.x}, k in
Z^7, eigenvalue 4 pi^2 q(k), q(k) = sum k_i^2 / R_i^2 (exact Fraction).
An element g = (eps, s): x -> eps*x + s/2 (eps_i = +-1, s_i in {0,1}) sends
f_k to e^{i pi k.s} f_{eps k}.  Its trace on a degenerate level is the sum
over k fixed by eps (k_i = 0 where eps_i = -1) of (-1)^{k.s}, an integer.
Gamma-invariant multiplicity = (1/|Gamma|) sum_g trace  (exact, integer).

Gamma here is the active Joyce Example 3 group, Z2^3, (b2, b3) = (12, 43),
with Joyce's half-period translations (the same elements as
intersection_tensor.canonical_point()).

D-027: radii are moduli.  Radius-independent: Gamma, the multiplicities of
|k|-vector classes (generic_classes), existence/absence of a class.
Radius-dependent: which classes merge into one level, the ordering, and all
mass ratios.  Equal-radii ratios are "at the symmetric point (a choice)".
"""
from fractions import Fraction
from itertools import product
from math import isqrt
from typing import Dict, List, Sequence, Tuple

DIM = 7
Elem = Tuple[Tuple[int, ...], Tuple[int, ...]]  # (eps, s)

_ID: Elem = ((1,) * DIM, (0,) * DIM)
_ALPHA: Elem = ((1, 1, 1, -1, -1, -1, -1), (0,) * 7)
_BETA: Elem = ((1, -1, -1, 1, 1, -1, -1), (0, 0, 0, 0, 0, 1, 0))
_GAMMA: Elem = ((-1, 1, -1, 1, -1, 1, -1), (0, 0, 0, 0, 1, 0, 1))


def compose(a: Elem, b: Elem) -> Elem:
    """a after b; half-shifts add mod 2 (eps*s = s mod 2)."""
    eps = tuple(x * y for x, y in zip(a[0], b[0]))
    s = tuple((x + y) % 2 for x, y in zip(a[1], b[1]))
    return eps, s


def generate_group(gens: Sequence[Elem]) -> List[Elem]:
    """Closure of the generators under composition."""
    group = {_ID}
    frontier = [_ID]
    while frontier:
        new = []
        for h in frontier:
            for g in gens:
                p = compose(g, h)
                if p not in group:
                    group.add(p)
                    new.append(p)
        frontier = new
    return sorted(group)


def joyce_gamma() -> List[Elem]:
    """The 8 elements of the active Z2^3."""
    return generate_group([_ALPHA, _BETA, _GAMMA])


def trivial_gamma() -> List[Elem]:
    return [_ID]


def _check_radii(radii: Sequence[Fraction]) -> Tuple[Fraction, ...]:
    if len(radii) != DIM:
        raise ValueError("need exactly %d radii" % DIM)
    out = tuple(Fraction(r) for r in radii)
    if any(r <= 0 for r in out):
        raise ValueError("radii must be positive")
    return out


def _check_group(group: Sequence[Elem]) -> None:
    if not group or _ID not in group:
        raise ValueError("group must contain the identity")
    for eps, s in group:
        if len(eps) != DIM or len(s) != DIM:
            raise ValueError("bad group element")
        if any(e not in (1, -1) for e in eps) or any(x not in (0, 1) for x in s):
            raise ValueError("eps must be +-1 and s in {0,1}")


def trace(g: Elem, k: Tuple[int, ...]) -> int:
    """Contribution of mode k to the trace of g on its level (integer)."""
    eps, s = g
    if any(e == -1 and ki != 0 for e, ki in zip(eps, k)):
        return 0
    return -1 if sum(ki * si for ki, si in zip(k, s)) % 2 else 1


def invariant_count(group: Sequence[Elem], ks: Sequence[Tuple[int, ...]]) -> int:
    """(1/|G|) sum_g sum_k trace; exact, raises if not an integer."""
    total = sum(trace(g, k) for g in group for k in ks)
    if total % len(group):
        raise ArithmeticError("non-integer multiplicity: not a group action")
    return total // len(group)


def lattice_points(radii: Tuple[Fraction, ...], qmax: Fraction):
    """All k in Z^7 with q(k) <= qmax, by pruned recursion."""
    inv = [1 / (r * r) for r in radii]

    def rec(i: int, left: Fraction, pre: Tuple[int, ...]):
        if i == DIM:
            yield pre
            return
        kmax = isqrt(int(left / inv[i]) + 1)
        for ki in range(-kmax, kmax + 1):
            rest = left - ki * ki * inv[i]
            if rest >= 0:
                yield from rec(i + 1, rest, pre + (ki,))

    yield from rec(0, qmax, ())


def q_of(radii: Tuple[Fraction, ...], k: Tuple[int, ...]) -> Fraction:
    return sum((Fraction(ki * ki) / (r * r) for ki, r in zip(k, radii)),
               Fraction(0))


def spectrum(group: Sequence[Elem], n_levels: int,
             radii: Sequence[Fraction] = (1,) * DIM,
             qmax: Fraction = None):
    """First n_levels nonzero levels as (q, mult_T7, mult_T7/Gamma).

    q is in units of 4 pi^2.  Levels whose orbifold multiplicity is 0 are
    absent from T^7/Gamma and are skipped (but counted in mult_T7 lists via
    `all_levels`).  Zero-mode multiplicity is checked to be 1 for a
    connected quotient.
    """
    rad = _check_radii(radii)
    _check_group(group)
    if n_levels < 1:
        raise ValueError("n_levels must be >= 1")
    qm = Fraction(qmax) if qmax is not None else Fraction(1)
    while True:
        by_q: Dict[Fraction, List[Tuple[int, ...]]] = {}
        for k in lattice_points(rad, qm):
            by_q.setdefault(q_of(rad, k), []).append(k)
        zero = invariant_count(group, by_q.pop(Fraction(0)))
        if zero != 1:
            raise ArithmeticError("zero-mode count %d != 1" % zero)
        rows = [(q, len(ks), invariant_count(group, ks))
                for q, ks in sorted(by_q.items())]
        rows = [r for r in rows if r[2] > 0]
        if len(rows) >= n_levels or qm > 400:
            return rows[:n_levels]
        qm *= 2


def mass_ratios(rows) -> List[float]:
    """m_n/m_1 = sqrt(q_n/q_1) (float, derived from exact rationals)."""
    if not rows:
        raise ValueError("no levels")
    q1 = rows[0][0]
    return [float(r[0] / q1) ** 0.5 for r in rows]


def generic_classes(group: Sequence[Elem], kmax: int = 2):
    """Radius-independent data: for each |k|-vector class (generic radii every
    class is its own level) -> (mult_T7 = 2^{#nonzero}, mult_T7/Gamma)."""
    _check_group(group)
    out = {}
    for absk in product(range(kmax + 1), repeat=DIM):
        if not any(absk):
            continue
        signs = [(-a, a) if a else (0,) for a in absk]
        ks = list(product(*signs))
        out[absk] = (len(ks), invariant_count(group, ks))
    return out
