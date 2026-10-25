"""D-023: every hypothesis of Joyce's existence theorem is measured and can fail."""

import pytest

from metaphysica.simulations.PM.geometry import g2_closure as gc
from metaphysica.simulations.PM.geometry import glued_orbit_scan as gos

COMPACT = gc.phi_for("octonion_derived")
SPLIT = gc.phi_for("all_plus_one")
PLANE = (1, 1, 1, -1, -1, -1, -1)


def test_compact_triples_are_hyperkahler_and_split_ones_are_not():
    assert gc.triple_definiteness(COMPACT)["holds"]
    assert not gc.triple_definiteness(SPLIT)["holds"]


def test_eguchi_hanson_triple_is_closed_in_exactly_one_orientation():
    rep = gc.eh_triple_closure()
    assert rep["closed_by_orientation"] == {"ASD": [True] * 3, "SD": [False] * 3}
    assert rep["hyperkahler_orientation"] == "ASD"


def test_local_model_is_torsion_free_only_with_the_matching_orientation():
    assert gc.local_model_torsion(COMPACT, PLANE)["holds"]
    wrong = gc.local_model_torsion(COMPACT, PLANE, orientation="SD")
    assert not wrong["d_phi_zero"] and not wrong["d_star_phi_zero"]
    assert not gc.local_model_torsion(SPLIT, PLANE)["holds"]


def test_gamma_fixes_exactly_one_spinor_and_the_controls_do_not():
    assert gc.invariant_spinor_count(COMPACT)["counts_over_lifts"] == [1] * 8
    one_generator = [e for e in gc.gamma_elements(COMPACT)][:2]
    assert gc.invariant_spinor_count(COMPACT, one_generator)["count"] == 4
    assert gc.invariant_spinor_count(COMPACT, [(1, 1, 1, 1, 1, -1, -1)])["count"] == 0
    assert gc.invariant_spinor_count(SPLIT)["count"] is None


def test_closure_verdict_on_the_active_path_and_on_the_split_form():
    rep = gc.closure_report("octonion_derived")
    assert rep["verdict"] == "CLOSED_BY_THEOREM"
    assert all(h["measured"] and h["holds"] for h in rep["hypotheses"])
    split = gc.closure_report("all_plus_one")
    assert split["verdict"] == "OPEN" and split["first_failure"] == "H2"
    failed = {h["id"] for h in split["hypotheses"] if not h["holds"]}
    assert {"H2", "H4a", "H4c", "H7", "H8"} <= failed


def test_glued_scan_honours_an_explicit_split_request():
    sig = gos.orbit_at(gos._flat_phi("all_plus_one"))["signature_unordered"]
    assert sig == (4, 3)


def test_an_unbuilt_construction_is_refused_with_its_reason(monkeypatch):
    """D-023: fano_tcs has no building blocks here, so it must not pass silently."""
    from metaphysica.simulations.PM.geometry.g2_closure import (
        require_buildable_construction,
    )

    assert require_buildable_construction() == "joyce_orbifold"
    monkeypatch.setenv("METAPHYSICA_VARIANT_G2_CONSTRUCTION", "fano_tcs")
    with pytest.raises(ValueError, match="no cited building blocks"):
        require_buildable_construction()
