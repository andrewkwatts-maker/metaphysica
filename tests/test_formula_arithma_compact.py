"""Sprint 3.2 — arithma_compact field on Formula records.

Covers:

1. A formula registered with ``arithma=Expression.number(3.14)`` produces a
   non-empty ``arithma_compact`` (skipped when Arithma's wheel is absent).
2. Round-trip via ``Expression.from_compact(arithma_compact)`` returns an
   equivalent expression (skipped when ``from_compact`` is unavailable).
3. ``audit_formulas.py``'s ``_classify`` helper sees a formula with a non-None
   ``arithma_compact`` (plus the symbolic ``arithma`` + ``eml`` + ``value``
   legs) as TRIPLE — proving the new field is audit-friendly.
4. When Arithma is unavailable, registration MUST NOT raise and
   ``arithma_compact`` MUST be ``None``.

These tests do not require Arithma to be installed; the symbolic legs are
skipped when the wheel is missing.
"""
from __future__ import annotations

import importlib
import math
import sys
from pathlib import Path

import pytest

# Make sure src/ is on the path (mirrors conftest.py).
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from metaphysica.simulations.base.registry import PMRegistry
from metaphysica.simulations.base.simulation_base import Formula


# ── Optional Arithma availability probe ──────────────────────────────────────


def _arithma_available() -> bool:
    try:
        import arithma  # type: ignore[import-not-found]
    except Exception:
        return False
    return getattr(arithma, "Expression", None) is not None


ARITHMA_AVAILABLE = _arithma_available()


@pytest.fixture(autouse=True)
def _reset_registry():
    """Ensure each test sees a clean PMRegistry singleton."""
    PMRegistry.reset_instance()
    yield
    PMRegistry.reset_instance()


def _make_formula(fid: str = "test_pi_const") -> Formula:
    """Build a minimal Formula record for the test."""
    return Formula(
        id=fid,
        label="(T.1)",
        latex=r"\pi_{\text{test}} = 3.14",
        plain_text="pi_test = 3.14",
        category="DERIVED",
        description="Test scalar used by Sprint 3.2 arithma_compact tests.",
    )


# ── Field plumbing ──────────────────────────────────────────────────────────


def test_arithma_compact_field_exists_and_defaults_to_none():
    """The new dataclass field must be present and default to None so old
    callers continue to construct Formula() without breakage."""
    f = _make_formula()
    assert hasattr(f, "arithma_compact"), (
        "Formula dataclass missing arithma_compact field (Sprint 3.2)"
    )
    assert f.arithma_compact is None


def test_add_formula_does_not_raise_without_arithma():
    """Registration must succeed even when Arithma is unavailable; the
    field stays at its default and triple_status reflects FLOAT_ONLY."""
    registry = PMRegistry.get_instance()
    f = _make_formula("test_no_arithma")
    # No arithma supplied → triple_status should fall through to FLOAT_ONLY
    # (value present) or "" (nothing present).
    registry.add_formula(f, source="test", value=3.14)
    stored = registry.get_formula("test_no_arithma")
    assert stored is not None
    assert stored.arithma_compact is None
    assert stored.triple_status in ("FLOAT_ONLY", "")


# ── With Arithma installed ──────────────────────────────────────────────────


@pytest.mark.skipif(not ARITHMA_AVAILABLE, reason="arithma wheel not installed")
def test_arithma_compact_populated_when_to_compact_exists():
    """When Arithma is available AND exposes to_compact(), registering a
    formula with an Expression should populate arithma_compact with a
    non-None value."""
    import arithma  # type: ignore[import-not-found]

    expr = arithma.Expression.number(3.14)

    if not hasattr(expr, "to_compact"):
        pytest.skip("arithma.Expression has no to_compact() yet (Sprint 3.1)")

    registry = PMRegistry.get_instance()
    f = _make_formula("test_pi_arithma")
    registry.add_formula(f, source="test", arithma=expr, value=3.14)

    stored = registry.get_formula("test_pi_arithma")
    assert stored is not None
    assert stored.arithma_compact is not None, (
        "arithma_compact should be captured at registration time"
    )
    # Non-empty payload — typically dict-or-str — just check truthiness.
    assert stored.arithma_compact, (
        f"arithma_compact unexpectedly empty: {stored.arithma_compact!r}"
    )


@pytest.mark.skipif(not ARITHMA_AVAILABLE, reason="arithma wheel not installed")
def test_arithma_compact_roundtrip_via_from_compact():
    """Round-tripping arithma_compact through Expression.from_compact should
    yield a numerically equivalent expression."""
    import arithma  # type: ignore[import-not-found]

    expr = arithma.Expression.number(3.14)

    if not (hasattr(expr, "to_compact") and hasattr(arithma.Expression, "from_compact")):
        pytest.skip("arithma to_compact/from_compact not yet implemented (Sprint 3.1)")

    registry = PMRegistry.get_instance()
    f = _make_formula("test_pi_roundtrip")
    registry.add_formula(f, source="test", arithma=expr, value=3.14)
    stored = registry.get_formula("test_pi_roundtrip")
    assert stored.arithma_compact is not None

    revived = arithma.Expression.from_compact(stored.arithma_compact)
    # Evaluate both views and compare numerically — round-trip should be
    # lossless for a constant scalar.
    original_value = float(expr.evaluate({}))
    revived_value = float(revived.evaluate({}))
    assert math.isclose(original_value, revived_value, rel_tol=1e-12, abs_tol=0.0)


# ── Export plumbing ─────────────────────────────────────────────────────────


def test_export_formulas_carries_arithma_compact_key():
    """``export_formulas()`` must surface the arithma_compact key for every
    formula, even when it's None (so JSON schema stays uniform)."""
    registry = PMRegistry.get_instance()
    registry.add_formula(_make_formula("test_export_key"), source="test", value=3.14)
    exported = registry.export_formulas()
    assert "test_export_key" in exported
    assert "arithma_compact" in exported["test_export_key"]


# ── Audit-friendly classification ───────────────────────────────────────────


def test_audit_formulas_classifies_triple_when_arithma_present():
    """audit_formulas._classify should label a formula carrying arithma + eml
    + value as TRIPLE. arithma_compact is an output of registration, not an
    input to classification — but a formula with a non-None arithma_compact
    is by definition one that had a real arithma view, so it must classify
    as TRIPLE (or ARITHMA_ONLY when eml is absent)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    audit_mod = importlib.import_module("audit_formulas")

    # Sentinel objects masquerading as arithma + eml views. _classify only
    # checks ``is not None`` on the three legs.
    class _Sentinel:
        pass

    f_triple = _make_formula("test_classify_triple")
    f_triple.arithma = _Sentinel()
    f_triple.eml = _Sentinel()
    f_triple.value = 3.14
    f_triple.arithma_compact = {"kind": "number", "value": 3.14}
    assert audit_mod._classify(f_triple) == "TRIPLE"

    f_arithma_only = _make_formula("test_classify_arithma_only")
    f_arithma_only.arithma = _Sentinel()
    f_arithma_only.value = 3.14
    f_arithma_only.arithma_compact = {"kind": "number", "value": 3.14}
    assert audit_mod._classify(f_arithma_only) == "ARITHMA_ONLY"
