#!/usr/bin/env python3
"""Sparse differential forms: wedge product, exterior derivative, integration.

WHY THIS EXISTS
---------------
The framework writes `int F ^ phi` and `G_4 = dC_3` in dozens of LaTeX strings
across lagrangian_master.py, master_action.py and the appendices, and has never
computed a single wedge product or exterior derivative. The one place that
looks like it does -- g2_differential.compute_d_phi() -- is

    return np.zeros((7, 7, 7, 7))

with the comment "For constant-coefficient forms on flat space, d = 0". That is
true, and it means the framework's central 4-form flux has never actually been
differentiated. A test asserting d(d omega) == 0 passes against that stub while
verifying nothing at all.

WHAT IS ESTABLISHED HERE
------------------------
One Form type whose coefficients are EITHER float (numeric) OR sympy.Expr
(symbolic). `wedge` is written once and serves both, because it only multiplies
and adds coefficients. `exterior_d` is defined only for symbolic coefficients,
where d^2 = 0 falls out as a STRUCTURAL zero: Clairaut symmetry makes the terms
cancel as expressions, yielding an empty component map rather than 1e-15.

THE REPRESENTATION IS A SAFETY DECISION
---------------------------------------
Components are stored sparsely, keyed by a strictly increasing multi-index.
Dense (n,)*p storage is a machine-killing trap at the dimensions this framework
cares about:

    n= 7, p=7  ->          1 independent component,   6.3 MB dense
    n=13, p=4  ->        715 independent components, 223 KB dense
    n=28, p=7  ->  1,184,040 independent components, 100.5 GB dense   <-- HAZARD
    n=13, p=13 ->          1 independent component,   2.2 PiB dense   <-- HAZARD

A single naive np.zeros((28,)*7) allocates 100.5 GB. The most dangerous line of
code that could be added to this module is a `levi_civita_Nd(n)` generalisation:
the 7D epsilon is 6.59 MB and fine, the 13D one is 2.2 PETABYTES, and there is
no safe interpolation between those facts. levi_civita_7d() below is therefore
deliberately NOT parameterised by dimension.

Every allocation passes guard_form_size() first, and wedge additionally guards
|A| x |B| -- a cost that is invisible in the component counts and would present
as a hang rather than a crash (20,475^2 = 4.19e8 pure-Python iterations at
n=28, p=q=4).

WHAT IS NOT ESTABLISHED
-----------------------
This is flat-space form algebra with an explicit coordinate chart. There are no
harmonic representatives, no cohomology, and no compact manifold. Integrating a
top form here multiplies a coefficient by a volume; it does not compute a
topological invariant. Genuine topological content needs a compact G2 manifold
with b3 = 24 -- the discrete-exterior-calculus work that is deliberately
deferred, not silently assumed.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import comb
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

__all__ = [
    "Form",
    "FormBudgetError",
    "component_count",
    "guard_form_size",
    "guard_wedge_cost",
    "wedge",
    "exterior_d",
    "top_coefficient",
    "integrate_top",
    "levi_civita_7d",
    "form_from_dense",
    "to_dense",
]

MultiIndex = Tuple[int, ...]

#: Dense arrays above this many float64 entries are refused. 4_194_304 entries
#: is 32 MB, which admits (13,)*4 at 0.22 MB and (28,)*4 at 4.69 MB with orders
#: of magnitude to spare, and refuses (28,)*7 at 100.5 GB.
MAX_DENSE_ENTRIES: int = 4_194_304

#: Sparse maps above this many components are refused. A tuple key plus a float
#: value costs roughly 150-200 bytes in CPython, so 2e6 entries is ~300-400 MB.
#: Admits every p <= 5 case in every dimension of interest; refuses the
#: middle-degree blowups such as C(28,14) = 40,116,600.
MAX_SPARSE_COMPONENTS: int = 2_000_000

#: Wedge is |A| x |B| pair operations. This bound is about TIME, not memory.
MAX_WEDGE_PAIRS: int = 5_000_000


class FormBudgetError(MemoryError):
    """Raised before an allocation that would exceed a size budget."""


def component_count(n: int, p: int) -> int:
    """Number of independent components of a p-form in n dimensions."""
    if p < 0 or p > n:
        return 0
    return comb(n, p)


def guard_form_size(n: int, p: int, *, dense: bool = False) -> int:
    """Refuse an over-budget allocation BEFORE it happens.

    Returns the component count when the allocation is permitted.
    """
    if dense:
        entries = n ** p
        if entries > MAX_DENSE_ENTRIES:
            raise FormBudgetError(
                f"dense {p}-form in {n}D needs {entries:,} float64 entries "
                f"({entries * 8 / 1024 ** 3:.1f} GB); the cap is "
                f"{MAX_DENSE_ENTRIES:,} entries (32 MB). Use the sparse "
                f"representation -- it needs only {component_count(n, p):,} "
                f"independent components."
            )
        return entries

    count = component_count(n, p)
    if count > MAX_SPARSE_COMPONENTS:
        raise FormBudgetError(
            f"sparse {p}-form in {n}D has {count:,} independent components, "
            f"over the cap of {MAX_SPARSE_COMPONENTS:,} (~300-400 MB of dict)"
        )
    return count


def guard_wedge_cost(n_a: int, n_b: int) -> int:
    """Refuse a wedge whose pair count would present as a hang."""
    pairs = n_a * n_b
    if pairs > MAX_WEDGE_PAIRS:
        raise FormBudgetError(
            f"wedge of {n_a:,} x {n_b:,} components is {pairs:,} pair "
            f"operations, over the cap of {MAX_WEDGE_PAIRS:,}. This is a TIME "
            f"budget: it would not crash, it would appear to hang."
        )
    return pairs


def _sort_sign(idx: Sequence[int]) -> Tuple[int, MultiIndex]:
    """Sort a multi-index, returning (sign of the permutation, sorted index).

    Returns sign 0 when any index repeats, since dx^i ^ dx^i = 0. Insertion
    sort is used deliberately: it counts inversions as it goes, and the
    multi-indices here are short (p <= 13).
    """
    items = list(idx)
    sign = 1
    for i in range(1, len(items)):
        key = items[i]
        j = i - 1
        while j >= 0 and items[j] > key:
            items[j + 1] = items[j]
            j -= 1
            sign = -sign
        items[j + 1] = key
    for i in range(1, len(items)):
        if items[i] == items[i - 1]:
            return 0, tuple(items)
    return sign, tuple(items)


@dataclass(frozen=True)
class Form:
    """A differential p-form on an n-dimensional coordinate chart.

    `components` maps a STRICTLY INCREASING multi-index to its coefficient.
    Antisymmetry is enforced at construction rather than checked afterwards, so
    a key is never in an invalid state.
    """

    dim: int
    degree: int
    components: Mapping[MultiIndex, Any]

    def __post_init__(self) -> None:
        if self.degree < 0 or self.degree > self.dim:
            if self.components:
                raise ValueError(
                    f"a {self.degree}-form in {self.dim}D must be zero, "
                    f"but {len(self.components)} components were given"
                )
        for key in self.components:
            if len(key) != self.degree:
                raise ValueError(
                    f"multi-index {key} has length {len(key)}, expected "
                    f"{self.degree}"
                )
            if any(k < 0 or k >= self.dim for k in key):
                raise ValueError(f"multi-index {key} out of range for {self.dim}D")
            if any(key[i] >= key[i + 1] for i in range(len(key) - 1)):
                raise ValueError(
                    f"multi-index {key} is not strictly increasing -- build "
                    f"forms through wedge() or Form.from_terms(), which "
                    f"canonicalise"
                )

    @classmethod
    def from_terms(
        cls, dim: int, degree: int, terms: Iterable[Tuple[Sequence[int], Any]]
    ) -> "Form":
        """Build a form from possibly-unsorted, possibly-repeating indices.

        Applies the permutation sign, drops repeated indices, and accumulates
        duplicate keys -- the canonicalisation the constructor refuses to guess.
        """
        guard_form_size(dim, degree)
        out: Dict[MultiIndex, Any] = {}
        for raw, coeff in terms:
            sign, key = _sort_sign(raw)
            if sign == 0:
                continue
            out[key] = out.get(key, 0) + sign * coeff
        return cls(dim=dim, degree=degree, components=_drop_zeros(out))

    @classmethod
    def zero(cls, dim: int, degree: int) -> "Form":
        return cls(dim=dim, degree=degree, components={})

    @classmethod
    def scalar(cls, dim: int, value: Any) -> "Form":
        """A 0-form (scalar field)."""
        return cls(dim=dim, degree=0, components={(): value})

    def __len__(self) -> int:
        return len(self.components)

    def __bool__(self) -> bool:
        return bool(self.components)

    def is_zero(self) -> bool:
        return not self.components


def _drop_zeros(mapping: Dict[MultiIndex, Any]) -> Dict[MultiIndex, Any]:
    """Remove exactly-zero coefficients so `is_zero` means what it says."""
    out: Dict[MultiIndex, Any] = {}
    for key, val in mapping.items():
        if val is None:
            continue
        try:
            if val == 0:
                continue
        except (TypeError, ValueError):  # pragma: no cover - exotic coefficient
            pass
        out[key] = val
    return out


def wedge(a: Form, b: Form) -> Form:
    """Exterior product a ^ b.

    0-forms take a fast path: a scalar wedge is a plain multiplication across
    the other form's coefficient map, with no permutation machinery. This
    matters because scalars -- the breathing fluctuation, background couplings
    -- get wedged against higher-degree forms constantly.
    """
    if a.dim != b.dim:
        raise ValueError(f"dimension mismatch: {a.dim} vs {b.dim}")

    degree = a.degree + b.degree
    if degree > a.dim:
        return Form.zero(a.dim, degree if degree <= a.dim else a.dim)

    # 0-form fast paths -- no sorting, no sign tracking.
    if a.degree == 0:
        if not a.components:
            return Form.zero(a.dim, b.degree)
        scale = a.components[()]
        return Form(a.dim, b.degree,
                    _drop_zeros({k: scale * v for k, v in b.components.items()}))
    if b.degree == 0:
        if not b.components:
            return Form.zero(a.dim, a.degree)
        scale = b.components[()]
        return Form(a.dim, a.degree,
                    _drop_zeros({k: v * scale for k, v in a.components.items()}))

    guard_wedge_cost(len(a.components), len(b.components))
    guard_form_size(a.dim, degree)

    out: Dict[MultiIndex, Any] = {}
    for ia, va in a.components.items():
        set_a = set(ia)
        for ib, vb in b.components.items():
            if set_a & set(ib):
                continue  # a repeated index kills the term: dx^i ^ dx^i = 0
            sign, key = _sort_sign(ia + ib)
            if sign == 0:
                continue
            out[key] = out.get(key, 0) + sign * va * vb
    return Form(a.dim, degree, _drop_zeros(out))


def exterior_d(form: Form, coords: Sequence[Any]) -> Form:
    """Exterior derivative, for SYMBOLIC coefficients only.

    Raises TypeError on float coefficients rather than quietly returning zeros.
    That silent-zero behaviour is exactly the defect this module was written to
    repair: g2_differential.compute_d_phi() returns np.zeros(...) uncondit-
    ionally, so `assert d(d(w)) == 0` passes there while proving nothing.

    d^2 = 0 holds here as a STRUCTURAL zero, not to a tolerance: Clairaut
    symmetry of the mixed partials makes the terms cancel as expressions, so
    the result is an empty component map.
    """
    import sympy as sp

    if len(coords) != form.dim:
        raise ValueError(
            f"got {len(coords)} coordinate symbols for a {form.dim}D form"
        )
    for val in form.components.values():
        if not isinstance(val, sp.Expr):
            raise TypeError(
                "exterior_d requires sympy.Expr coefficients; got "
                f"{type(val).__name__}. A float-valued form on a flat chart "
                "has d = 0 identically, and returning that zero would be "
                "indistinguishable from a broken derivative -- so it is "
                "refused rather than faked."
            )

    degree = form.degree + 1
    if degree > form.dim:
        return Form.zero(form.dim, form.dim)
    guard_form_size(form.dim, degree)

    out: Dict[MultiIndex, Any] = {}
    for idx, val in form.components.items():
        for axis in range(form.dim):
            if axis in idx:
                continue
            key = tuple(sorted((axis,) + idx))
            sign = (-1) ** key.index(axis)
            term = sign * sp.diff(val, coords[axis])
            if term == 0:
                continue
            out[key] = sp.expand(out.get(key, 0) + term)
    return Form(form.dim, degree, _drop_zeros(out))


def top_coefficient(form: Form) -> Any:
    """The single component of a top-degree form (C(n,n) = 1)."""
    if form.degree != form.dim:
        raise ValueError(
            f"not a top form: degree {form.degree} in {form.dim} dimensions"
        )
    key = tuple(range(form.dim))
    return form.components.get(key, 0)


def integrate_top(form: Form, *, volume: float) -> Any:
    """Integrate a constant-coefficient top form over a region of `volume`.

    NOT a topological invariant. On a flat chart with constant coefficients
    this is coefficient x volume -- a number. See the module docstring.
    """
    return top_coefficient(form) * volume


@lru_cache(maxsize=1)
def levi_civita_7d():
    """The 7D Levi-Civita tensor, shared process-wide and read-only.

    Delegates to g2_differential._levi_civita_7d() rather than duplicating the
    permutation logic. That function costs ~0.36 s and 6.59 MB per call and is
    invoked by every G2DifferentialGeometry construction, so this caches one
    copy and marks it non-writeable because it is now shared.

    DELIBERATELY NOT PARAMETERISED BY DIMENSION. The 13D analogue would be
    13^13 x 8 bytes = 2.2 PEBIBYTES. Path A must enumerate index splits
    (13!/(3!4!4!2!) = 900,900), never contract an epsilon.
    """
    from metaphysica.simulations.PM.geometry.g2_differential import (
        _levi_civita_7d,
    )

    eps = _levi_civita_7d()
    eps.flags.writeable = False
    return eps


def form_from_dense(array, degree: int) -> Form:
    """Convert a dense antisymmetric ndarray into the sparse representation."""
    import numpy as np

    arr = np.asarray(array)
    dim = arr.shape[0] if arr.ndim else 0
    if arr.ndim != degree or any(s != dim for s in arr.shape):
        raise ValueError(
            f"expected a {degree}-index array with all axes of length {dim}, "
            f"got shape {arr.shape}"
        )
    guard_form_size(dim, degree)
    from itertools import combinations

    out: Dict[MultiIndex, Any] = {}
    for key in combinations(range(dim), degree):
        val = float(arr[key]) if degree else float(arr)
        if val != 0.0:
            out[key] = val
    return Form(dim=dim, degree=degree, components=out)


def to_dense(form: Form):
    """Expand to a dense antisymmetric ndarray. Guarded -- see the caps above."""
    import numpy as np
    from itertools import permutations

    guard_form_size(form.dim, form.degree, dense=True)
    arr = np.zeros((form.dim,) * form.degree, dtype=float)
    for key, val in form.components.items():
        for perm in permutations(range(form.degree)):
            permuted = tuple(key[i] for i in perm)
            sign, _ = _sort_sign(permuted)
            arr[permuted] = sign * val
    return arr
