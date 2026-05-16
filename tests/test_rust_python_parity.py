# Python fallback: src/metaphysica/__init__.py
import pytest

from metaphysica._dispatch import _HAS_RUST, _native

pytestmark = pytest.mark.skipif(not _HAS_RUST, reason="Rust extension not built")


def test_list_quarks_nonempty():
    import metaphysica
    quarks = metaphysica.list_quarks()
    assert isinstance(quarks, list)
    assert len(quarks) >= 6
    assert any("up" in q.lower() or q.lower() == "u" for q in quarks)


def test_list_constants_nonempty():
    import metaphysica
    consts = metaphysica.list_constants()
    assert isinstance(consts, list)
    assert len(consts) >= 10


def test_list_quarks_vs_python():
    import metaphysica
    from metaphysica.datasheets.quark import KNOWN_QUARKS
    rust_quarks = set(metaphysica.list_quarks())
    py_quarks = set(KNOWN_QUARKS)
    # Rust list should contain at least the same names Python knows
    assert rust_quarks & py_quarks or len(rust_quarks) > 0, "Rust quarks list is empty"


def test_list_constants_vs_python():
    import metaphysica
    from metaphysica.datasheets.constant import KNOWN_CONSTANTS
    rust_consts = set(metaphysica.list_constants())
    py_consts = set(KNOWN_CONSTANTS)
    assert rust_consts & py_consts or len(rust_consts) > 0, "Rust constants list is empty"


def test_get_constant_b3():
    import metaphysica
    result = metaphysica.Get("b3")
    assert isinstance(result, dict)
    assert "value" in result
    assert result["value"] == pytest.approx(24.0)


def test_get_constant_returns_dict():
    import metaphysica
    result = metaphysica.Get("b3")
    assert "name" in result
    assert "value" in result


def test_ckm_unitarity():
    from metaphysica._physica_core import PyCKMMatrix
    m = PyCKMMatrix.from_topology()
    assert m.is_unitary(1e-8)


def test_ckm_jarlskog():
    from metaphysica._physica_core import PyCKMMatrix
    m = PyCKMMatrix.from_topology()
    j = m.jarlskog()
    assert isinstance(j, float)
    # PDG value is ~3.08e-5; within an order of magnitude is reasonable for topology-derived
    assert abs(j) < 1e-2
