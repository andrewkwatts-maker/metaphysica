"""The beginner story is generated from the live fork, corrections baked in.

The site's reading toggle demands a plain statement for every derivation as an
audit instrument. This file pins that the plain-register topology story (1) is
generated, so a seed switch rewrites it, (2) carries the adopted numbers, and
(3) keeps the three corrections against the circulated draft -- Betti numbers
COUNT (never lengths or areas), the seams are 3-DIMENSIONAL, and generations
enter as the RANK of the folding symmetry, not a dial.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from metaphysica.simulations.PM.geometry.geometry_narration import (
    layperson_narration,
)


def test_the_adopted_story_carries_the_found_solution(monkeypatch):
    monkeypatch.delenv("METAPHYSICA_VARIANT_B3_SEED", raising=False)
    r = layperson_narration()
    assert (r["b3"], r["b2"]) == (43, 12)
    assert r["on_reachable_family"] is True
    assert "7 + 3 x 12 = 43" in r["story"]["the_total"]
    assert "36 repair-generated chambers" in r["story"]["the_total"]


def test_the_off_path_story_says_the_relation_fails():
    r = layperson_narration("seed_24")
    assert (r["b3"], r["b2"]) == (24, 4)
    assert "FAILS" in r["story"]["the_total"]
    assert "19" in r["story"]["the_total"]  # 7 + 3*4, computed not typed


def test_switching_the_seed_rewrites_the_story():
    a = layperson_narration("seed_43_joyce")["paragraph"]
    b = layperson_narration("seed_24")["paragraph"]
    assert a != b


def test_betti_numbers_are_counts_never_areas():
    """The circulated draft said b_2 'measures surface area' -- wrong fact."""
    r = layperson_narration()
    assert "never lengths or areas" in r["story"]["hole_counter"]
    assert "area" not in r["story"]["the_seams"].lower()


def test_the_seams_are_three_dimensional_not_lines():
    r = layperson_narration()
    assert "3-dimensional seams" in r["story"]["the_seams"] \
        or "3D" in r["story"]["the_seams"]
    assert "line" not in r["story"]["the_seams"].lower()


def test_generations_are_the_rank_not_a_dial():
    r = layperson_narration()
    assert "rank 3" in r["story"]["the_generations"]
    assert "not a dial" in r["story"]["the_generations"]


def test_every_number_in_the_total_is_computed_from_the_seed():
    """b2 = 5 would be off both branches; the story must follow the input."""
    r = layperson_narration()
    assert str(r["b2"]) in r["story"]["the_seams"]
    assert r["corrections_applied"]
