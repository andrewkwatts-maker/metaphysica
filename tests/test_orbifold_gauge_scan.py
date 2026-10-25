"""Tests for the D-028 orbifold gauge scan (orbifold_gauge_scan)."""
import numpy as np
import pytest

from metaphysica.simulations.PM.geometry import orbifold_gauge_scan as o


@pytest.fixture(scope="module")
def phi():
    return o.phi_active()


@pytest.fixture(scope="module")
def active(phi):
    lat = o.z7_lattice()
    return lat, o.close_group(o.active_generators(lat, phi))


def test_active_z2_cubed_has_12_a1_t3_loci_and_12_43(active):
    from metaphysica.simulations.PM.geometry.joyce_resolution import (
        resolution_report,
    )

    lat, G = active
    rec = o.analyse(G, lat)
    assert rec["order"] == 8 and rec["flat_betti"] == (1, 0, 0, 7, 7, 0, 0, 1)
    assert len(rec["strata"]) == 12 and rec["n_loci"] == 48
    assert all(r["label"] == "A1" and r["betti"] == (1, 3, 3, 1)
               for r in rec["strata"])
    assert rec["gauge"]["text"] == "SU(2)^12" and rec["codim7"] == []
    assert (rec["betti"][2], rec["betti"][3]) == (12, 43)
    ref = resolution_report()
    assert (ref["b2"], ref["b3"]) == (12, 43)
    assert rec["betti"] == ref["betti"]


def test_validation_on_joyce_z2_cubed_example():
    """Joyce's own Z2^3 (Joyce 2000, Ch. 12) in his phi0 frame: (12, 43)."""
    lat, gens = o.joyce_z2_cubed()
    G = o.close_group(gens)
    rec = o.analyse(G, lat)
    assert len(G) == 8 and rec["gauge"]["factors"] == {2: 12}
    assert rec["crossings"] == 0 and rec["codim7"] == []
    assert (rec["betti"][2], rec["betti"][3]) == (12, 43)
    assert rec["flat_betti"] == (1, 0, 0, 7, 7, 0, 0, 1)


def test_keeping_loci_singular_removes_their_exceptional_classes(active):
    lat, G = active
    rec = o.analyse(G, lat)
    kept = o.betti_with_keep(rec["flat_betti"], rec["strata"], keep=(2,))
    assert (kept[2], kept[3]) == (0, 7)


def test_non_g2_rotation_is_rejected(phi):
    c, s = np.cos(np.pi / 2), np.sin(np.pi / 2)
    A = np.eye(7)
    A[np.ix_([0, 1], [0, 1])] = [[c, -s], [s, c]]       # one plane only
    with pytest.raises(o.ScanError, match="G2"):
        o.from_euclid(A, np.zeros(7), o.z7_lattice(), phi)


def test_non_orthogonal_and_non_lattice_maps_are_rejected(phi):
    with pytest.raises(o.ScanError, match="orthogonal"):
        o.from_euclid(2 * np.eye(7), np.zeros(7), o.z7_lattice(), phi)
    A = np.eye(7)
    with pytest.raises(o.ScanError, match="Lambda"):
        o.from_euclid(A, np.full(7, 0.123), o.z7_lattice(), phi)


def test_group_closure_and_fail_early(active):
    lat, G = active
    keys = {g.key for g in G}
    assert all(o.compose(a, b).key in keys for a in G for b in G)
    assert all(o.compose(o.inverse(g), g) == o.identity() for g in G)
    trans = [o.Iso(np.eye(7), np.eye(7, dtype=int)[i]) for i in range(7)]
    with pytest.raises(o.ScanError, match="exceeds"):
        o.close_group(trans)


def _hex_z3(phi):
    A, lat = o.hex_rotations(phi)[0]
    return lat, o.close_group([o.from_euclid(A, np.zeros(7), lat, phi)])


def test_z3_in_su2_gives_a2_and_su3(phi):
    lat, G = _hex_z3(phi)
    assert len(G) == 3
    rec = o.analyse(G, lat)
    # 3 fixed points per A2 plane, two planes: 9 A2 loci
    assert [r["label"] for r in rec["strata"]] == ["A2"] * 9
    assert rec["gauge"]["factors"] == {3: 9} and rec["gauge"]["has_su3_su2"] is False
    assert {r["b1"] for r in rec["strata"]} == {3} and rec["codim7"] == []


def test_class_is_finite_and_g2_checked(phi):
    for A, lat, n, _fam in o.candidate_A(phi)[:50]:
        assert o.preserves_phi(A, phi) and n in (3, 4)
    assert o.class_size(phi)["total"] > 0


def test_order3_extension_of_active_z2_cubed_exceeds_64(phi):
    A, lat = o.hex_rotations(phi)[0]
    base = o.active_generators(lat, phi)
    delta = o.from_euclid(A, np.zeros(7), lat, phi)
    with pytest.raises(o.ScanError, match="exceeds 64"):
        o.close_group(base + [delta], 64)


def test_default_cap_is_1536():
    assert o.MAX_ORDER == 1536


def test_den_represents_thirds_and_sixths(phi):
    assert o.DEN % 3 == 0 and o.DEN % 6 == 0 and o.DEN % 4 == 0
    A, lat = o.hex_rotations(phi)[0]
    b = o.translations(A, lat, 3)[1]
    d = o.from_euclid(A, b, lat, phi)
    assert set(d.c.tolist()) <= {0, o.DEN // 3, 2 * o.DEN // 3}
    assert o.element_order(d) == 3


def test_order3_extension_closes_with_order_384(phi):
    A, lat = o.hex_rotations(phi)[0]
    base = o.active_generators(lat, phi)
    G = o.close_group(base + [o.from_euclid(A, np.zeros(7), lat, phi)])
    assert len(G) == 384


def test_raised_cap_closes_order3_extension_and_fails_early_above(phi):
    A, lat = o.hex_rotations(phi)[0]
    base = o.active_generators(lat, phi)
    delta = o.from_euclid(A, np.zeros(7), lat, phi)
    G = o.close_group(base + [delta], 1536)
    assert 64 < len(G) <= 1536
    with pytest.raises(o.ScanError, match="exceeds 64"):
        o.close_group(base + [delta], 64)
    # a signed-permutation order-3 candidate that does not close below 1536
    sp = [c for c in o.candidate_A(phi) if c[3] == "signed-perm" and c[2] == 3][0]
    A2, lat2 = sp[0], sp[1]
    base2 = o.active_generators(lat2, phi)
    d2 = o.from_euclid(A2, o.translations(A2, lat2, 3)[1], lat2, phi)
    with pytest.raises(o.ScanError, match="exceeds 1536"):
        o.close_group(base2 + [d2], 1536)


def test_a_type_ks_finds_a2_in_z3(phi):
    _lat, G = _hex_z3(phi)
    assert o.a_type_ks(G) == {3: 9}


def test_normaliser_preserves_active_group(phi):
    lat = o.z7_lattice()
    base = o.active_generators(lat, phi)
    norm = o.normaliser(lat, phi, base)
    keys = frozenset(g.key for g in o.close_group(base))
    assert len(norm) > 0
    assert all(o.group_orbit_keys(o.close_group(base), [n]) == {keys}
               for n in norm[:20])


def test_vectorised_orbit_digests_match_key_orbits(phi):
    lat = o.z7_lattice()
    base = o.active_generators(lat, phi)
    norm = o.normaliser(lat, phi, base)
    G = o.close_group(base)
    assert o.group_orbit_digests(G, norm) == {o.group_digest(G)}
    A, lat3 = o.hex_rotations(phi)[0]
    base3 = o.active_generators(lat3, phi)
    H = o.close_group(base3 + [o.from_euclid(A, np.zeros(7), lat3, phi)])
    norm3 = o.normaliser(lat3, phi, base3)
    assert len(o.group_orbit_digests(H, norm3)) == len(o.group_orbit_keys(H, norm3))
