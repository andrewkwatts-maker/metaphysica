"""The closed-geometry certificate: every theorem holds, reads the live seed,
and names a test that exists.

The certificate (PM/geometry/closed_geometry.py) is where paper, website and
beginner guide read the geometry from, so its failure modes are the ones prose
has always had: a statement that no longer matches the computation, a number
typed instead of derived, a cited test that was renamed away, and a switch
that no longer moves anything. Each has a test here.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from metaphysica.simulations.PM.geometry.closed_geometry import (
    THEOREMS,
    ClosedGeometrySimulation,
    build,
    certificate,
    holonomy_selection_pending,
)
from metaphysica.simulations.core.triple_validator import triple_assert

_REPO = Path(__file__).resolve().parents[1]


def _cert(monkeypatch, seed):
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", seed)
    return {e["id"]: e for e in certificate()}


def test_every_theorem_holds_on_the_adopted_seed(monkeypatch):
    for entry in _cert(monkeypatch, "seed_43_joyce").values():
        assert entry["derived"], entry["id"]
        assert entry["holds"], (entry["id"], entry["statement"])


def test_statements_carry_the_derived_numbers(monkeypatch):
    cert = _cert(monkeypatch, "seed_43_joyce")
    assert "(1, 0, 12, 43, 43, 12, 0, 1)" in cert[
        "y7-resolved-betti-numbers"]["statement"]
    assert "chi(Y_7) = sum (-1)^k b_k = 0" in cert[
        "y7-euler-characteristic"]["statement"]
    assert "12 disjoint three-tori" in cert[
        "y7-singular-components"]["statement"]
    assert "pi_1(Y_7) = 1" in cert["y7-fundamental-group"]["statement"]
    assert "b_3 = 24 is not among them" in cert["joyce-reachable-set"][
        "statement"]


def test_the_certificate_follows_the_seed_within_the_family(monkeypatch):
    """Flip to (8, 31): every statement is re-derived for that member."""
    cert = _cert(monkeypatch, "seed_31_joyce")
    assert "(1, 0, 8, 31, 31, 8, 0, 1)" in cert[
        "y7-resolved-betti-numbers"]["statement"]
    assert cert["y7-resolved-betti-numbers"]["holds"]
    pi1 = cert["y7-fundamental-group"]
    assert "infinite" in pi1["statement"]
    assert pi1["evidence"]["k"] == 1 and pi1["holds"]


def test_off_the_family_only_the_family_level_theorem_publishes(monkeypatch):
    """On seed_24 nothing member-specific is derived -- and the reachable-set
    theorem, which is WHY seed_24 is off the family, still holds."""
    by_id = {t.id: t for t in THEOREMS}
    cert = _cert(monkeypatch, "seed_24")
    for entry in cert.values():
        if by_id[entry["id"]].seed_following:
            assert entry["derived"] is False
            assert entry["holds"] is False
            assert "not reachable by the construction" in entry["statement"]
        else:
            assert entry["derived"] and entry["holds"]
    published = [f.id for f in ClosedGeometrySimulation().get_formulas()]
    family_level = [t.id for t in THEOREMS if not t.seed_following]
    assert published == family_level
    assert "joyce-reachable-set" in published


def test_every_cited_test_exists():
    """A certificate that cites a renamed-away test certifies nothing."""
    for thm in THEOREMS:
        path, _, func = thm.test.partition("::")
        assert (_REPO / path).is_file(), thm.test
        module = importlib.import_module("tests." + Path(path).stem)
        assert callable(getattr(module, func, None)), thm.test


def test_every_theorem_states_what_it_counts_and_how_it_fails():
    for thm in THEOREMS:
        assert thm.counts and thm.proof and thm.falsifier, thm.id
        assert thm.references, thm.id


def test_formulas_pass_the_triple_check_on_two_routes(monkeypatch):
    """The float leg is the module's computation; the symbolic legs evaluate
    the closed form. They are different routes, and they must agree."""
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_43_joyce")
    formulas = ClosedGeometrySimulation().get_formulas()
    assert [f.id for f in formulas] == [t.id for t in THEOREMS]
    for f in formulas:
        triple_assert(f.arithma, f.eml, f.value, rel=f.triple_rel,
                      abs_=f.triple_abs, name=f.id)


def test_the_spec_builder_is_one_formula_in_three_views():
    eml, arithma, text, value = build(("add", 7, ("mul", 3, 12)))
    assert value == 43.0
    assert text == "ops.add(eml_scalar(7), ops.mul(eml_scalar(3), " \
                   "eml_scalar(12)))"
    triple_assert(arithma, eml, 43.0, name="spec")


def test_the_triple_check_can_fail():
    """A closed form that disagrees with the computation must be caught."""
    from metaphysica.simulations.core.triple_validator import (
        FormulaConsistencyError,
    )

    eml, arithma, _text, _value = build(("add", 7, ("mul", 3, 11)))
    with pytest.raises(FormulaConsistencyError):
        triple_assert(arithma, eml, 43.0, name="wrong closed form")


def test_chi_parameter_is_published_only_when_derived(monkeypatch):
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_43_joyce")
    assert ClosedGeometrySimulation().run(None) == {"topology.chi_y7": 0.0}
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_24")
    assert ClosedGeometrySimulation().run(None) == {}


def test_the_holonomy_selection_is_held_back_until_the_real_form_ruling():
    pending = holonomy_selection_pending()
    assert pending["status"] == "PENDING_G3_REAL_FORM_RULING"
    assert pending["selected"] == (12, 43)
    published = {t.id for t in THEOREMS}
    assert not any("holonomy" in pid for pid in published)
