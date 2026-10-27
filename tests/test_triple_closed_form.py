"""closed_form builds independent Arithma and EML trees; non_numeric fails early.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import math

import pytest

from metaphysica.simulations.base import Formula
from metaphysica.simulations.core.triple_helpers import closed_form
from metaphysica.simulations.core.triple_validator import triple_assert


def test_closed_form_legs_agree_with_the_float():
    spec = ("mul", ("div", "b3", "chi"), ("sub", 1, ("div", 1, ("sqrt", "b3"))))
    kw = closed_form(spec, {"chi": 144.0})
    from metaphysica.simulations.core.FormulasRegistry import get_registry
    b3 = float(get_registry().elder_kads)
    value = (b3 / 144.0) * (1.0 - 1.0 / math.sqrt(b3))
    res = triple_assert(kw["arithma"], kw["eml"], value,
                        env=kw["triple_env"], name="cf")
    assert res.arithma_used and res.eml_used


def test_closed_form_rejects_unbound_names_and_bad_nodes():
    with pytest.raises(ValueError):
        closed_form(("add", 1, "nope"))
    with pytest.raises(ValueError):
        closed_form(("frob", 1, 2))


def test_a_value_cannot_be_non_numeric():
    from metaphysica.simulations.base.registry import PMRegistry
    f = Formula(id="x-nn", label="(x)", latex="x", plain_text="x",
                category="DERIVED", description="d",
                non_numeric="symbolic identity with no number", value=1.0)
    with pytest.raises(ValueError):
        PMRegistry().add_formula(f, source="test")
