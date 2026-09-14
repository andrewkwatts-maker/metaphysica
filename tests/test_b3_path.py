"""The two b_3 paths, and the coupling between the seed and the generations.

The 43 path exists because b_3 = 24 is not reachable by the Joyce construction
(derived_contribution_table) while (12, 43) is, and is Joyce's canonical
published pair. These tests pin what each path derives, what it costs, and the
one structural fact that decides between generation sources: a generation count
must be an integer.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.b3_path import (
    PATHS,
    compare_paths,
    downstream,
    n_gen_report,
    seed_values,
)


def test_both_paths_are_declared_with_provenance():
    assert set(PATHS) == {"seed_24", "seed_43_joyce"}
    for key, spec in PATHS.items():
        assert spec["b3_provenance"], key
        assert spec["b2_provenance"], key
        assert spec["n_gen_source"] in ("b3_over_dim_O", "b2_over_faces")


def test_the_adopted_path_is_still_the_status_quo():
    """Nothing published moves until the author rules."""
    b3, b2 = seed_values("seed_24")
    assert (b3, b2) == (24, 4)
    from metaphysica.simulations.core.variants import FORKS

    assert FORKS["b3_seed"].default() == "seed_24"
    assert FORKS["n_gen_source"].default() == "b3_over_dim_O"


def test_the_43_path_derives_both_betti_numbers():
    b3, b2 = seed_values("seed_43_joyce")
    assert (b3, b2) == (43, 12)
    spec = PATHS["seed_43_joyce"]
    assert "DERIVED" in spec["b3_provenance"]
    assert "DERIVED" in spec["b2_provenance"]
    assert spec["reachable_by_joyce"] is True
    assert PATHS["seed_24"]["reachable_by_joyce"] is False


# ------------------------------------------- the generation count, both ways


def test_three_generations_survive_on_both_paths():
    """The 43 path does not lose them -- it relocates their origin."""
    for key in PATHS:
        report = n_gen_report(key)
        assert report["equals_three"], (
            "%s gives n_gen = %s via %s"
            % (key, report["n_gen"], report["declared_source"])
        )


def test_each_generation_source_fails_on_the_other_path():
    """Why the two forks are coupled, asserted rather than asserted-in-prose."""
    at_24 = n_gen_report("seed_24")
    at_43 = n_gen_report("seed_43_joyce")

    # b_3/8 works at 24, fails at 43
    assert at_24["b3_over_dim_O"]["integer"] is True
    assert at_43["b3_over_dim_O"]["integer"] is False
    assert at_43["b3_over_dim_O"]["value"] == pytest.approx(43 / 8)

    # b_2/4 works at 43, gives the wrong count at 24
    assert at_43["b2_over_faces"]["value"] == pytest.approx(3.0)
    assert at_24["b2_over_faces"]["value"] == pytest.approx(1.0)


def test_integrality_is_the_stated_discriminator_not_w0():
    report = n_gen_report("seed_43_joyce")
    assert "number of things" in report["why_this_decides"]
    assert "0.0017" in report["why_this_decides"], (
        "the w_0 insensitivity finding must stay attached to this reasoning"
    )


# --------------------------------------------------- costs, recorded not hidden


def test_the_plus_two_identity_breaks_on_the_43_path_and_says_so():
    at_24 = downstream("seed_24")
    at_43 = downstream("seed_43_joyce")
    if "plus_two_identity_holds" not in at_24:
        pytest.skip("D_bulk not registered")
    assert at_24["plus_two_identity_holds"] is True
    assert at_43["plus_two_identity_holds"] is False
    assert at_43["d_bulk_minus_b3"] == -17
    assert "BROKEN" in at_43["plus_two_identity_note"]
    assert "not dropped" in at_43["plus_two_identity_note"]


def test_w0_worsens_on_the_43_path_and_is_reported():
    at_24 = downstream("seed_24")
    at_43 = downstream("seed_43_joyce")
    assert at_43["w0"] == pytest.approx(-42 / 43)
    if "w0_sigma_vs_desi" not in at_24:
        pytest.skip("DESI anchor not registered")
    assert at_24["w0_sigma_vs_desi"] < at_43["w0_sigma_vs_desi"], (
        "the 43 path must be reported as the worse w_0 fit; concealing that "
        "would be the anchor-shopping this project has already retired once"
    )
    assert at_43["w0_sigma_vs_desi"] < 2.0, (
        "at ~0.94 sigma the cost is real but not fatal; if it exceeds 2 sigma "
        "the trade has changed and the register must be revisited"
    )


def test_every_b3_consumer_moves_with_the_seed():
    at_24 = downstream("seed_24")
    at_43 = downstream("seed_43_joyce")
    for key in ("racetrack_exponent", "k_bary_cycles", "wa_thawing"):
        assert at_24[key] != at_43[key], (
            "%s did not respond to the seed; it is not reading b_3" % key
        )
    assert at_43["k_bary_cycles"] == 29      # 43 - 14


# ------------------------------------------------------------ the comparison


def test_the_comparison_selects_nothing():
    result = compare_paths()
    assert result["verdict"] == "NO_SELECTION_MADE"
    assert "never by agreement" in result["ordering"]
    paths = [r["path"] for r in result["rows"]]
    assert paths == sorted(paths), "rows must be ordered by path id"
    assert result["both_pass_structurally"] is True, (
        "both paths give three generations, so the structural test does NOT "
        "decide between them -- the ruling is genuinely the author's"
    )


def test_the_ruling_is_framed_with_both_sides():
    text = compare_paths()["what_the_author_is_ruling_on"]
    assert "no geometric home left" in text
    assert "Joyce's canonical published pair" in text
    assert "0.94 sigma" in text
    assert "broken +2 identity" in text


# ------------------------------------------------- the paper follows the path


def test_the_narration_is_generated_not_hardcoded():
    """Switching the seed must rewrite the paper's claim, not contradict it."""
    from metaphysica.simulations.PM.geometry.b3_path import narration

    at_24 = narration("seed_24")
    at_43 = narration("seed_43_joyce")
    assert "b_3 / 8" in at_24["n_gen_assertion"]
    assert "b_2 / 4" in at_43["n_gen_assertion"]
    assert at_24["n_gen_assertion"] != at_43["n_gen_assertion"]
    for text in (at_24, at_43):
        assert "= 3 (exact)" in text["n_gen_assertion"], (
            "both paths must still narrate three generations"
        )


def test_the_false_tcs_provenance_is_corrected():
    """The appendix asserted b_3 = 24 comes from TCS #187. It does not."""
    from metaphysica.simulations.PM.geometry.b3_path import narration

    at_24 = narration("seed_24")
    assert "NOT supplied by TCS #187" in at_24["seed_sentence"]
    assert "71 <= b_3 <= 155" in at_24["seed_sentence"]
    assert "That is false" in at_24["provenance_correction"]


def test_the_appendix_certificate_reads_the_path():
    import metaphysica.simulations.PM.paper.appendices.appendix_c_derivations as m

    holders = [v for v in vars(m).values()
               if isinstance(v, type) and hasattr(v, "_generation_certificate")]
    assert holders, "the generated certificate helper went missing"
    cert = holders[0]._generation_certificate()
    assert cert["status"] == "EXACT"
    assert cert["b3_path"] in PATHS
    assert "TCS #187" in cert["provenance_correction"]
    assert "24 / 8" in cert["assertion"] or "12 / 4" in cert["assertion"]
