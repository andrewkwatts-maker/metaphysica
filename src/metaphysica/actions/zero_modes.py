"""Zero-mode counting: fields of a parent action -> fields of the child over a compact space.

Generic and theory-agnostic. Rules (Kaluza-Klein on a compact n-manifold X):
- a p-form gives b_k(X) (p-k)-forms in the child, for each k <= min(p, n);
  b_k = b_(n-k) by Poincare duality (Hodge theory on a compact oriented manifold);
- the metric gives the child metric, b1 vectors (isometries / graviphotons) and the
  metric moduli: n(n+1)/2 for the flat torus (constant deformations of the metric),
  b3 for G2 holonomy (Joyce 2000; Acharya hep-th/9812205);
- a spinor gives one child spinor per parallel spinor on X: all `dirac_dim(n)` for the
  flat torus, 1 of the dirac_dim(7) = 8 for G2 holonomy (Joyce 2000, Ch. 10-11;
  Wang 1989: parallel spinors <-> holonomy).
Counts are per kind: "metric", "scalar", "vector", "form:q" (q >= 2), "spinor".
A child 0-form is a scalar and a child 1-form a vector. Dualising forms is a separate,
explicit step (`dualise_forms`); it is never applied here.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Dict, Iterable, Mapping

from metaphysica.actions.model import Field
from metaphysica.actions.spinors import dirac_dim

HOLONOMIES = ("flat", "G2")
G2_DIM = 7


def full_betti(betti: Mapping[int, int], n: int) -> Dict[int, int]:
    """Betti numbers b_0..b_n, filling gaps by Poincare duality; raises if inconsistent."""
    b = {k: int(v) for k, v in betti.items()}
    b.setdefault(0, 1)
    b.setdefault(n, 1)
    for k in range(n + 1):
        if k not in b and (n - k) in b:
            b[k] = b[n - k]
    missing = [k for k in range(n + 1) if k not in b]
    if missing:
        raise ValueError("Betti numbers missing for degrees %s" % missing)
    for k in range(n + 1):
        if b[k] != b[n - k]:
            raise ValueError("Poincare duality fails: b_%d = %d but b_%d = %d"
                             % (k, b[k], n - k, b[n - k]))
    return b


def _kind(degree: int) -> str:
    return "scalar" if degree == 0 else "vector" if degree == 1 else "form:%d" % degree


def _form_degree(f: Field):
    if f.kind == "scalar":
        return 0
    if f.kind == "vector":
        return 1
    return int(f.kind[5:]) if f.kind.startswith("form:") else None


def _moduli(n: int, b: Mapping[int, int], holonomy: str) -> int:
    return n * (n + 1) // 2 if holonomy == "flat" else b[3]


def _check_inputs(n: int, b: Mapping[int, int], holonomy: str) -> None:
    if holonomy not in HOLONOMIES:
        raise ValueError("holonomy %r is not supported; use one of %s" % (holonomy, HOLONOMIES))
    if holonomy == "G2" and n != G2_DIM:
        raise ValueError("G2 holonomy needs internal dimension 7, got %d" % n)
    if holonomy == "G2" and b[1] != 0:
        raise ValueError("full G2 holonomy needs b1 = 0, got b1 = %d" % b[1])


def _add(out: Dict[str, int], kind: str, count: int) -> None:
    if count:
        out[kind] = out.get(kind, 0) + count


def zero_modes(parent_fields: Iterable[Field], internal_dim: int,
               betti: Mapping[int, int], holonomy: str) -> Dict[str, int]:
    """Per-kind count of child fields from the parent's fields; see the module docstring."""
    n = internal_dim
    if holonomy not in HOLONOMIES:
        raise ValueError("holonomy %r is not supported; use one of %s" % (holonomy, HOLONOMIES))
    b = full_betti(betti, n)
    _check_inputs(n, b, holonomy)
    out: Dict[str, int] = {}
    for f in parent_fields:
        if f.kind == "metric":
            _add(out, "metric", 1)
            _add(out, "vector", b[1])
            _add(out, "scalar", _moduli(n, b, holonomy))
        elif f.kind == "spinor":
            _add(out, "spinor", dirac_dim(n) if holonomy == "flat" else 1)
        else:
            p = _form_degree(f)
            if p is None:
                raise ValueError("field %s: unknown kind %r" % (f.name, f.kind))
            for k in range(min(p, n) + 1):
                _add(out, _kind(p - k), b[k])
    return out


def dualise_forms(counts: Mapping[str, int], child_dim: int) -> Dict[str, int]:
    """Explicit dualisation: in child_dim dimensions a q-form is dual to a (child_dim-2-q)-form.

    Only the (child_dim-2)-form -> scalar case is applied (a 2-form in 4D is a scalar).
    """
    top = child_dim - 2
    out = dict(counts)
    kind = _kind(top)
    moved = out.pop(kind, 0)
    _add(out, "scalar", moved)
    return out
