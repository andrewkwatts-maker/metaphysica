"""Reduction checks and the standard ladder."""

from __future__ import annotations

import json
from fractions import Fraction


from metaphysica.actions.controls import (
    g2_zero_modes, ricci_flat_compactification as rfc, standard_ladder,
)
from metaphysica.actions.model import INPUT, Action, Coefficient, Field, Term
from metaphysica.actions.reduction import InternalSpace, Reduction, check_reduction


def _act(dim, sig, fields=(), symbol="c", cdim=2):
    c = Coefficient(symbol, Fraction(cdim), INPUT, "p")
    return Action("a%d" % dim, dim, sig, tuple(fields), (Term("t", c, ("R",)),))


def test_dimensions_must_add_up():
    p, c = _act(10, (9, 1), symbol="M"), _act(5, (4, 1), symbol="N")
    red = Reduction(p, c, InternalSpace("K", 6, True, None, "Vol"), {})
    assert [x.id for x in check_reduction(red) if not x.holds] == ["reduction_dim:a5"]


def test_signature_times_must_be_preserved_or_declared():
    p, c = _act(6, (5, 1)), _act(4, (4, 0))
    internal = InternalSpace("K", 2, True, None, "Vol")
    assert [x.id for x in check_reduction(Reduction(p, c, internal, {}))
            if not x.holds] == ["reduction_time:a4"]
    declared = Reduction(p, c, internal, {}, signature_change=True)
    assert all(x.holds for x in check_reduction(declared))


def test_planck_mass_map_and_its_failing_control():
    assert all(c.holds for c in rfc.planck_checks())
    assert not all(c.holds for c in rfc.planck_checks(wrong=True))


def test_zero_modes_checked_when_betti_given():
    fields = (Field("u1_vector_multiplets", "vector", 12, Fraction(1)),
              Field("chiral_multiplets", "scalar", 43, Fraction(1)))
    p, c = _act(11, (10, 1), symbol="M"), _act(4, (3, 1), fields, symbol="N")
    internal = InternalSpace("X", 7, True, g2_zero_modes.JOYCE_EXAMPLE["betti"], "Vol")
    red = Reduction(p, c, internal, {}, zero_mode_rule=g2_zero_modes.zero_mode_rule)
    assert all(x.holds for x in check_reduction(red))
    wrong = InternalSpace("X", 7, True, {1: 0, 2: 8, 3: 47}, "Vol")
    red2 = Reduction(p, c, wrong, {}, zero_mode_rule=g2_zero_modes.zero_mode_rule)
    assert [x.id for x in check_reduction(red2) if not x.holds] == [
        "zero_modes:chiral_multiplets", "zero_modes:u1_vector_multiplets"]


def test_standard_ladder_is_validated_and_json_ready():
    report = standard_ladder().report()
    assert report["verdict"] == "VALIDATED"
    assert json.loads(json.dumps(report)) == report
    assert report == standard_ladder().report()
