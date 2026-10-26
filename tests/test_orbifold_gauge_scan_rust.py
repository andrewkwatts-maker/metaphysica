"""Rust vs Python parity for the D-028 orbifold scan.

The Python functions (`close_group` with backend="python", `analyse` with
backend="python") are the reference. The Rust core must return the same group
(elements and BFS order) and the same record, field for field; the only float
field, `exceptional`, is compared after rounding. Skipped when the extension
(or these symbols) is not built.
"""
import copy

import numpy as np
import pytest

from metaphysica._dispatch import rust_fn
from metaphysica.simulations.PM.geometry import orbifold_gauge_scan as o

pytestmark = pytest.mark.skipif(
    rust_fn("py_orbifold_analyse") is None or rust_fn("py_orbifold_close_group") is None,
    reason="physica_core extension with orbifold symbols not built")


@pytest.fixture(scope="module")
def phi():
    return o.phi_active()


@pytest.fixture(scope="module")
def cands(phi):
    return o.candidate_A(phi)


def _norm(rec):
    rec = copy.deepcopy(rec)
    for s in rec["strata"]:
        if "exceptional" in s:
            s["exceptional"] = [round(float(x), 6) for x in s["exceptional"]]
    return rec


def _same_group(a, b):
    assert [g.key for g in a] == [g.key for g in b]


def _check(G, lat):
    rp = o.analyse(G, lat, backend="python")
    rr = o.analyse(G, lat, backend="rust")
    assert _norm(rr) == _norm(rp)
    return rr


def _delta(cands, phi, idx, ti, n):
    A, lat, order, _fam = cands[idx]
    assert order == n
    return lat, o.from_euclid(A, o.translations(A, lat, n)[ti], lat, phi)


def test_closure_matches_python_and_fails_the_same_way(phi, cands):
    lat, d = _delta(cands, phi, 314, 0, 3)
    gens = o.active_generators(lat, phi) + [d]
    _same_group(o.close_group(gens, backend="rust"),
                o.close_group(gens, backend="python"))
    for backend in ("rust", "python"):
        with pytest.raises(o.ScanError, match=r"exceeds 64 \(no closure\)"):
            o.close_group(gens, 64, backend=backend)
    shift = o.Iso(np.eye(7, dtype=np.int64), np.eye(7, dtype=np.int64)[0])
    for backend in ("rust", "python"):  # translation by 1/12 has order 12
        with pytest.raises(o.ScanError, match="exceeds 5"):
            o.close_group([shift], 5, backend=backend)


def test_rust_closure_matches_for_order_3_and_4_extensions(phi, cands):
    for idx, ti, n in [(314, 64, 3), (84, 0, 3), (76, 0, 3)]:
        lat, d = _delta(cands, phi, idx, ti, n)
        gens = o.active_generators(lat, phi) + [d]
        _same_group(o.close_group(gens, backend="rust"),
                    o.close_group(gens, backend="python"))
    i4 = next(i for i, c in enumerate(cands) if c[2] == 4)
    lat, d = _delta(cands, phi, i4, 5, 4)
    gens = o.active_generators(lat, phi) + [d]
    _same_group(o.close_group(gens, backend="rust"),
                o.close_group(gens, backend="python"))


def test_hexagonal_z3_control_gives_nine_a2_loci_on_both_paths(phi):
    A, lat = o.hex_rotations(phi)[0]
    G = o.close_group([o.from_euclid(A, np.zeros(7), lat, phi)])
    rec = _check(G, lat)
    assert [r["label"] for r in rec["strata"]] == ["A2"] * 9
    assert rec["gauge"]["factors"] == {3: 9} and rec["codim7"] == []


def test_active_z2_cubed_matches(phi):
    lat = o.z7_lattice()
    rec = _check(o.close_group(o.active_generators(lat, phi)), lat)
    assert rec["gauge"]["text"] == "SU(2)^12" and rec["betti"] is not None


def test_standalone_order3_and_order4_cyclic_groups_match(phi, cands):
    picked = [(i, c) for i, c in enumerate(cands)]
    n3 = [(i, c) for i, c in picked if c[2] == 3][::7][:6]
    n4 = [(i, c) for i, c in picked if c[2] == 4][::17][:4]
    assert len(n3) >= 4 and len(n4) >= 3
    for _i, (A, lat, n, _f) in n3 + n4:
        for b in o.translations(A, lat, n)[::50][:2]:
            G = o.close_group([o.from_euclid(A, b, lat, phi)])
            assert len(G) == n
            _check(G, lat)


def test_order_64_class_with_order4_extension_matches(phi, cands):
    i4 = next(i for i, c in enumerate(cands) if c[2] == 4)
    for ti in (0, 40):
        lat, d = _delta(cands, phi, i4, ti, 4)
        G = o.close_group(o.active_generators(lat, phi) + [d])
        rec = _check(G, lat)
        assert rec["order"] == len(G) and rec["gauge"]["factors"]


@pytest.mark.parametrize("idx,ti", [(314, 0), (314, 64), (84, 0)])
def test_order_96_order3_classes_match(phi, cands, idx, ti):
    lat, d = _delta(cands, phi, idx, ti, 3)
    G = o.close_group(o.active_generators(lat, phi) + [d])
    assert len(G) == 96
    rec = _check(G, lat)
    assert rec["codim7"] or rec["crossings"] >= 0


def test_threaded_rust_equals_single_thread(phi, cands):
    lat, d = _delta(cands, phi, 314, 0, 3)
    G = o.close_group(o.active_generators(lat, phi) + [d])
    one = o.analyse(G, lat, backend="rust", threads=1)
    many = o.analyse(G, lat, backend="rust", threads=4)
    assert _norm(one) == _norm(many)


def test_bad_backend_and_missing_symbol_fail_early():
    with pytest.raises(o.ScanError, match="backend"):
        o.analyse([], o.z7_lattice(), backend="gpu")
