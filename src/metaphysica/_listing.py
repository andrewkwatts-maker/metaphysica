"""Sprint 5 — catalog + iteration helpers.

Provides per-kind list/iter functions and a global ``list_all()``. Every
helper is a thin wrapper around :func:`metaphysica._catalog.list_kind`
plus an entity-iterator that yields :class:`~metaphysica._catalog.EntityRef`
records for callers who need the payload + source path alongside the
canonical id.
"""
from __future__ import annotations

from typing import Dict, Iterator, List

from ._catalog import (
    EntityRef,
    KIND_CERTIFICATE,
    KIND_CONSTANT,
    KIND_DERIVATION,
    KIND_FORMULA,
    KIND_GATE,
    KIND_PARAMETER,
    KIND_PLOT,
    KIND_QUARK,
    KIND_REFERENCE,
    KIND_SECTION,
    KIND_SIMULATION,
    KINDS,
    get_catalog,
    list_kind,
)


# ---------------------------------------------------------------------------
# Per-kind list helpers — return sorted canonical ids.
# ---------------------------------------------------------------------------


def list_formulas() -> List[str]:
    """Return every formula id (sorted, deduplicated)."""
    return list_kind(KIND_FORMULA)


def list_parameters() -> List[str]:
    """Return every parameter id (sorted, deduplicated).

    Parameters use the dotted-key form ``"<section>.<name>"`` (e.g.
    ``"constants.M_PLANCK"``).
    """
    return list_kind(KIND_PARAMETER)


def list_gates() -> List[str]:
    """Return every gate id, typically ``G01..G72``."""
    return list_kind(KIND_GATE)


def list_certificates() -> List[str]:
    """Return every certificate id (includes the 97 named per-category certs)."""
    return list_kind(KIND_CERTIFICATE)


def list_sections() -> List[str]:
    """Return every paper-section id."""
    return list_kind(KIND_SECTION)


def list_plots() -> List[str]:
    """Return every plot id from ``plots-manifest.json``."""
    return list_kind(KIND_PLOT)


def list_derivations() -> List[str]:
    """Return every derivation-chain id (bundled + build-output)."""
    return list_kind(KIND_DERIVATION)


def list_references() -> List[str]:
    """Return every reference id from ``references.json``."""
    return list_kind(KIND_REFERENCE)


def list_simulations() -> List[str]:
    """Return every simulation-script id from ``simulations-index.json``."""
    return list_kind(KIND_SIMULATION)


def list_particles() -> List[str]:
    """Return every Standard Model particle id (quarks today; leptons in v2.3)."""
    # Today the catalog only ships KIND_QUARK; the helper exists for
    # forward-compat with the lepton extension queued for v2.3.
    return list_kind(KIND_QUARK)


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------


def list_all() -> Dict[str, List[str]]:
    """Return ``{kind: [canonical_id, ...]}`` for every kind in the catalog.

    Empty kinds are still present in the result (mapped to ``[]``) so
    callers can iterate ``KINDS`` deterministically.
    """
    return {kind: list_kind(kind) for kind in KINDS}


# ---------------------------------------------------------------------------
# Entity iterators — for callers who want the payload alongside the id.
# ---------------------------------------------------------------------------


def iter_kind(kind: str) -> Iterator[EntityRef]:
    """Yield every :class:`EntityRef` registered under *kind*.

    De-duplicates aliases (the same ref shows up in the catalog under
    multiple normalised keys); each :class:`EntityRef` is yielded once.
    Iteration order follows the sorted canonical-id order.
    """
    cat = get_catalog()
    seen: set = set()
    by_canonical: Dict[str, EntityRef] = {}
    for ref in cat.get(kind, {}).values():
        if ref.canonical_id in seen:
            continue
        seen.add(ref.canonical_id)
        by_canonical[ref.canonical_id] = ref
    for cid in sorted(by_canonical):
        yield by_canonical[cid]


def iter_formulas() -> Iterator[EntityRef]:
    """Yield every formula's :class:`EntityRef` in id order."""
    yield from iter_kind(KIND_FORMULA)


def iter_parameters() -> Iterator[EntityRef]:
    """Yield every parameter's :class:`EntityRef` in id order."""
    yield from iter_kind(KIND_PARAMETER)


def iter_gates() -> Iterator[EntityRef]:
    """Yield every gate's :class:`EntityRef`."""
    yield from iter_kind(KIND_GATE)


def iter_sections() -> Iterator[EntityRef]:
    """Yield every section's :class:`EntityRef`."""
    yield from iter_kind(KIND_SECTION)


def iter_plots() -> Iterator[EntityRef]:
    """Yield every plot's :class:`EntityRef`."""
    yield from iter_kind(KIND_PLOT)


def iter_all() -> Iterator[EntityRef]:
    """Yield every catalogued :class:`EntityRef` across every kind.

    Iteration order is per-kind then per-canonical-id within the kind.
    """
    for kind in KINDS:
        yield from iter_kind(kind)


__all__ = [
    # Per-kind list helpers
    "list_formulas",
    "list_parameters",
    "list_gates",
    "list_certificates",
    "list_sections",
    "list_plots",
    "list_derivations",
    "list_references",
    "list_simulations",
    "list_particles",
    # Aggregate
    "list_all",
    # Iterators
    "iter_kind",
    "iter_formulas",
    "iter_parameters",
    "iter_gates",
    "iter_sections",
    "iter_plots",
    "iter_all",
]
