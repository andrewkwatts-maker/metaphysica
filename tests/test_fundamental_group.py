"""pi_1(Y) = 1 at the canonical point, and with it the Wilson-line dock closes.

Flavour had one remaining KNOWN mechanism needing no singularity: a discrete
Wilson line, i.e. a homomorphism out of pi_1(Y). Armstrong's theorem makes
pi_1 of the resolved quotient computable from the same enumeration data that
fixed b_2 and b_3 -- and at the canonical point the answer is TRIVIAL, because
the singular elements span Gamma over F_2 and their flips cover all seven
coordinates, so every generator of the affine group lies in the normal closure
of the fixed-point elements. Joyce states simple connectivity for his
examples; this reproduces it from the enumeration alone.

MEASURED 2026-09-22: canonical point H_1 = 0, criterion True; the no-singular
control gives H_1 = (Z/2)^7 and criterion False, so neither computation is a
constant wearing a function.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.fundamental_group import (
    abelianization_presentation,
    fundamental_group_report,
    h1_of_resolution,
    pi1_triviality_criterion,
    wilson_line_verdict,
)
from metaphysica.simulations.PM.geometry.intersection_tensor import (
    canonical_point,
)


# ------------------------------------------------- the canonical point

def test_h1_is_trivial_at_the_canonical_point():
    h1 = h1_of_resolution()
    assert h1["invariant_factors"] == []
    assert h1["free_rank"] == 0
    assert h1["is_trivial"] is True


def test_free_rank_zero_agrees_with_the_derived_b1():
    """b_1 = 0 (R5) sees the free rank; the torsion is this module's to add."""
    assert h1_of_resolution()["free_rank"] == 0


def test_pi1_is_provably_trivial_not_merely_abelianised_away():
    crit = pi1_triviality_criterion()
    assert crit["singular_span_is_gamma"] is True
    assert crit["singular_flips_cover_all_coordinates"] is True
    assert crit["pi1_provably_trivial"] is True


def test_the_wilson_line_dock_is_closed_by_derivation():
    verdict = wilson_line_verdict()
    assert verdict["status"] == "CLOSED_BY_DERIVATION"
    assert "no discrete wilson line" in verdict["sentence"].lower()
    assert verdict["layer"] == "TOPOLOGICAL"


# ------------------------------------------------- the computation responds

def _point_without_singular():
    pt = dict(canonical_point())
    pt["singular"] = []
    return pt


def test_removing_the_singular_elements_opens_the_dock():
    """Without Armstrong's killing, seven Z/2 torsion classes survive."""
    pt = _point_without_singular()
    h1 = h1_of_resolution(pt)
    assert h1["invariant_factors"] == [2, 2, 2, 2, 2, 2, 2]
    assert h1["is_trivial"] is False
    assert wilson_line_verdict(pt)["status"] == "OPEN"


def test_one_singular_element_is_not_enough():
    """A single involution kills only its own four flips; torsion survives."""
    pt = dict(canonical_point())
    pt["singular"] = [canonical_point()["singular"][0]]
    crit = pi1_triviality_criterion(pt)
    assert crit["singular_span_is_gamma"] is False
    assert crit["singular_flips_cover_all_coordinates"] is False
    h1 = h1_of_resolution(pt)
    assert h1["is_trivial"] is False, (
        "one singular involution cannot close the dock; if this became "
        "trivial the Armstrong rows are killing more than their theorem allows"
    )


# ------------------------------------------------- loudness and honesty

def test_a_singular_element_with_a_half_shift_on_a_fixed_coordinate_is_loud():
    """'Singular' MEANS integral shift on fixed coordinates; lying must raise."""
    pt = dict(canonical_point())
    elements = {tuple(k): v for k, v in pt["elements"].items()} \
        if isinstance(pt["elements"], dict) else dict(pt["elements"])
    label, (signs, halves) = pt["singular"][0]
    fixed = next(i for i in range(7) if signs[i] == 1)
    broken = list(halves)
    broken[fixed] = 1
    elements[tuple(label)] = (signs, tuple(broken))
    pt["elements"] = elements
    pt["singular"] = [(label, (signs, tuple(broken)))]
    with pytest.raises(ValueError):
        abelianization_presentation(pt)


def test_the_presentation_names_what_its_generators_are():
    """The A4 bar: deck translations and lifts, not Betti numbers."""
    pres = abelianization_presentation()
    assert "Neither is a Betti number" in pres["what_generators_are"]
    assert len(pres["columns"]) == 14  # 7 translations + 7 lifts


def test_the_report_records_the_crosscheck_as_a_reproduction():
    report = fundamental_group_report()
    assert "reproduction, not a citation" in report["external_crosscheck"]
    assert report["wilson_line_dock"] == "CLOSED_BY_DERIVATION"
