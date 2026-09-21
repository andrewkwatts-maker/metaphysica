"""G2 holonomy is claimed across 92 files. On the adopted branch it is false.

It is not a find-and-replace, because it is PATH-DEPENDENT: on
`g2_form_convention = octonion_derived` the claim is true, and on the adopted
`all_plus_one` it is not -- phi is the SPLIT real form, its induced metric has
signature (4,3), and no Riemannian G2-holonomy manifold exists behind it.

The only stable fix is to stop writing these sentences by hand. This file pins
that the generated narration REWRITES under a fork switch rather than
contradicting the code, and that it refuses to narrate the one claim nobody has
ruled on.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.geometry_narration import (
    betti_claim,
    chi_eff_claim,
    forbidden_phrases,
    generation_claim,
    holonomy_claim,
    metric_claim,
    narrate,
)


# ------------------------------------------------- the adopted branch

def test_the_adopted_branch_may_not_claim_g2_holonomy(monkeypatch):
    monkeypatch.delenv("METAPHYSICA_VARIANT_G2_FORM_CONVENTION", raising=False)
    claim = holonomy_claim()
    assert claim["branch"] == "all_plus_one"
    assert claim["real_form"].startswith("split")
    assert claim["signature"] == (4, 3)
    assert claim["is_riemannian"] is False
    assert claim["may_claim_g2_holonomy"] is False
    assert "SPLIT" in claim["sentence"]


def test_the_compact_branch_may(monkeypatch):
    claim = holonomy_claim("octonion_derived")
    assert claim["signature"] == (7, 0)
    assert claim["is_riemannian"] is True
    assert claim["may_claim_g2_holonomy"] is True


def test_the_two_branches_say_different_things():
    """If the narration did not move, it would be a constant wearing a fork."""
    split = holonomy_claim("all_plus_one")
    compact = holonomy_claim("octonion_derived")
    assert split["sentence"] != compact["sentence"]
    assert split["lambda2_14_is"] != compact["lambda2_14_is"]


def test_the_14_is_named_correctly_on_each_branch():
    """Dimensions are right on both; only the IDENTIFICATION differs."""
    assert "g2*" in holonomy_claim("all_plus_one")["lambda2_14_is"]
    assert holonomy_claim("octonion_derived")["lambda2_14_is"].startswith("g2,")


# ------------------------------------------------- the metric

def test_the_quadratic_metric_is_described_as_unable_to_certify(monkeypatch):
    monkeypatch.delenv("METAPHYSICA_VARIANT_METRIC_CONSTRUCTION", raising=False)
    claim = metric_claim()
    assert claim["branch"] == "quadratic_contraction"
    assert "cannot certify" in claim["sentence"]
    assert "Hitchin's construction is cubic" in claim["sentence"]


def test_the_cubic_metric_branch_narrates_differently():
    assert metric_claim("hitchin_cubic")["sentence"] != \
        metric_claim("quadratic_contraction")["sentence"]


# ------------------------------------------------- betti and generations

def test_the_adopted_seed_is_narrated_as_off_the_family(monkeypatch):
    monkeypatch.delenv("METAPHYSICA_VARIANT_B3_SEED", raising=False)
    claim = betti_claim()
    assert (claim["b3"], claim["b2"]) == (24, 4)
    assert claim["on_reachable_family"] is False
    assert "FAILS here" in claim["sentence"]


def test_the_43_seed_is_narrated_as_one_input(monkeypatch):
    claim = betti_claim("seed_43_joyce")
    assert (claim["b3"], claim["b2"]) == (43, 12)
    assert claim["on_reachable_family"] is True
    assert "ONE topological input" in claim["sentence"]


def test_the_b2_route_narrates_the_rank_result():
    claim = generation_claim("b2_over_faces", "seed_43_joyce")
    assert "RANK" in claim["sentence"]
    assert "rank(Gamma) = 3" in claim["sentence"]
    assert "measured correspondence" in claim["caveat"]


def test_the_b3_route_narrates_that_it_is_empty_on_the_family():
    claim = generation_claim("b3_over_dim_O", "seed_43_joyce")
    assert "NOWHERE on the family" in claim["sentence"]
    assert "incompatible" in claim["caveat"]


# ------------------------------------------------- the unruled one

def test_chi_eff_is_not_narrated_as_derived():
    """Inventing a default here would be making the ruling."""
    claim = chi_eff_claim()
    assert claim["may_claim_a_derivation"] is False
    assert claim["ruling_required"] is True
    assert claim["branch"] == "UNRULED"
    assert "CONSTANT" in claim["dichotomy"]
    assert "SEED-DEPENDENT" in claim["dichotomy"]


def test_chi_eff_stays_forbidden_on_every_branch(monkeypatch):
    """Unlike holonomy, no fork setting makes this claim sayable.

    An earlier version of this test ended `... or True`, which made it
    unfalsifiable -- the exact defect this suite exists to catch, written into
    the file that checks the wording. It now actually switches the branch.
    """
    for convention in ("all_plus_one", "octonion_derived"):
        monkeypatch.setenv("METAPHYSICA_VARIANT_G2_FORM_CONVENTION", convention)
        assert "chi_eff is derived" in forbidden_phrases(), convention
        assert chi_eff_claim()["may_claim_a_derivation"] is False


# ------------------------------------------------- the forbidden list

def test_the_forbidden_list_is_generated_not_maintained(monkeypatch):
    """It must shrink when the branch makes the claim true."""
    monkeypatch.delenv("METAPHYSICA_VARIANT_G2_FORM_CONVENTION", raising=False)
    on_split = forbidden_phrases()
    assert "G2 holonomy" in on_split

    monkeypatch.setenv("METAPHYSICA_VARIANT_G2_FORM_CONVENTION",
                       "octonion_derived")
    on_compact = forbidden_phrases()
    assert "G2 holonomy" not in on_compact, (
        "the forbidden list did not respond to the fork, so it is a hand "
        "maintained blacklist rather than a generated one"
    )
    assert "chi_eff is derived" in on_compact


def test_every_forbidden_phrase_carries_its_reason():
    for phrase, reason in forbidden_phrases().items():
        assert len(reason) > 30, (phrase, reason)


# ------------------------------------------------- the whole narration

def test_narrate_covers_every_geometric_claim():
    result = narrate()
    assert set(result["claims"]) == {
        "holonomy", "metric", "betti", "generations", "chi_eff"}
    assert result["paragraph"]
    for claim in result["claims"].values():
        assert claim["sentence"]


def test_switching_forks_rewrites_the_paragraph():
    """The property the whole module exists for."""
    a = narrate(g2_form_convention="all_plus_one", b3_seed="seed_24",
                n_gen_source="b3_over_dim_O")["paragraph"]
    b = narrate(g2_form_convention="octonion_derived",
                b3_seed="seed_43_joyce",
                n_gen_source="b2_over_faces")["paragraph"]
    assert a != b
    assert "SPLIT real form" in a
    assert "COMPACT real form" in b
