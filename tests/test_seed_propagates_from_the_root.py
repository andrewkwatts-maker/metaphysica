"""The b_3 seed must reach the pipeline, and the fork coupling must be able to fire.

TWO DEFECTS THIS FILE PINS CLOSED
=================================
1. `g2_geometry` is the ROOT topology simulation -- nothing feeds it, and it
   EMITS topology.elder_kads, topology.b2, topology.mephorash_chi and
   topology.n_gen. Those were literals (`self._b3 = 24  # From TCS
   construction`), so the `b3_seed` fork could not propagate at all: flipping it
   moved b3_path's own report and nothing downstream, because the pipeline's
   source of b_3 was here and was constant. The comment was also false --
   fano_tcs exhibits 71 <= b_3 <= 155, so TCS #187 does not supply 24.

2. `n_gen_source` was INERT. `n_gen_report` read `PATHS[key]["n_gen_source"]`
   and nothing ever called `resolve("n_gen_source")`, so the fork was slaved to
   b3_seed. That made the coupling between the two forks UNFALSIFIABLE: no
   inconsistent combination was reachable, so a guard against one could not
   fire, and a check that cannot fire is a defect. The fork is now live with the
   path's own declaration as its default, so an explicit override reaches the
   inconsistent state and the guard has something to catch.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.b3_path import n_gen_report, seed_values


def _root():
    """The root topology simulation class, located rather than hardcoded."""
    import metaphysica.simulations.PM.geometry.g2_geometry as module

    holders = [v for v in vars(module).values()
               if isinstance(v, type) and hasattr(v, "_resolve_n_gen")]
    assert holders, "the root simulation no longer resolves n_gen"
    return holders[0]


# ------------------------------------------------------- propagation

def test_the_root_reads_the_seed_instead_of_a_literal(monkeypatch):
    """ADOPTED seed_43_joyce (author ruling 2026-09-22): the default IS the
    found solution, and the root must read it from the fork, not a literal."""
    monkeypatch.delenv("METAPHYSICA_VARIANT_B3_SEED", raising=False)
    monkeypatch.delenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", raising=False)
    sim = _root()()
    b3, b2 = seed_values("seed_43_joyce")
    assert sim._b3 == b3 == 43
    assert sim._b2 == b2 == 12
    assert sim._b3_seed_path == "seed_43_joyce", (
        "the adopted branch is the ruled one; changing it is the author's"
    )


def test_flipping_the_seed_moves_the_root_outputs(monkeypatch):
    """The whole point: topology.* must respond to the fork -- now exercised
    by flipping to the labelled OFF-PATH branch."""
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_24")
    monkeypatch.setenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", "b3_over_dim_O")
    sim = _root()()
    assert sim._b3 == 24
    assert sim._b2 == 4
    assert sim._n_gen == 3, "three generations hold on the off-path route too"
    # k_gimel = b_3/2 + 1/pi rides on the seed and must move with it
    assert sim._k_gimel < 13.0


def test_the_emitted_topology_rows_move_with_the_seed(monkeypatch):
    """Not just the attributes -- the dict run() actually publishes."""
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_24")
    monkeypatch.setenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", "b3_over_dim_O")
    at_24 = _root()()
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_43_joyce")
    monkeypatch.setenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", "b2_over_faces")
    at_43 = _root()()

    assert (at_24._b3, at_24._b2) != (at_43._b3, at_43._b2), (
        "the root produced identical topology under both seeds, so the fork "
        "still cannot propagate"
    )


# ------------------------------------------------- the chi_eff divergence

def test_the_two_chi_eff_routes_agree_at_24_and_diverge_at_43(monkeypatch):
    """Matching values are not the same statement, caught live.

    chi_eff has two claimed origins: 2(h11 - h21 + h31) from the TCS Hodge
    numbers, which never references b_3, and b_3^2/4 from FormulasRegistry.
    Both give 144 at b_3 = 24. At b_3 = 43 the second gives 462.25, which is not
    even an integer -- so the agreement at 24 was a coincidence of two different
    statements, exactly the trap the register names.
    """
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_24")
    monkeypatch.setenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", "b3_over_dim_O")
    at_24 = _root()()
    assert at_24._chi_eff_from_hodge == 144
    assert at_24._chi_eff_from_b3 == pytest.approx(144.0)
    assert at_24._chi_eff_routes_agree is True

    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_43_joyce")
    monkeypatch.setenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", "b2_over_faces")
    at_43 = _root()()
    assert at_43._chi_eff_from_hodge == 144
    assert at_43._chi_eff_from_b3 == pytest.approx(462.25)
    assert at_43._chi_eff_routes_agree is False, (
        "the divergence must be reported, not smoothed over -- it is now the "
        "ADOPTED branch's honest state, awaiting the chi_eff ruling"
    )


# ------------------------------------------- the coupling, now reachable

def test_the_n_gen_source_fork_is_no_longer_inert(monkeypatch):
    """An explicit override must actually select a source."""
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_43_joyce")

    monkeypatch.delenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", raising=False)
    default = n_gen_report()
    assert default["declared_source"] == "b2_over_faces"
    assert default["equals_three"] is True

    monkeypatch.setenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", "b3_over_dim_O")
    forced = n_gen_report()
    assert forced["declared_source"] == "b3_over_dim_O", (
        "the override did not take effect; the fork is still slaved to b3_seed"
    )
    assert forced["n_gen"] == pytest.approx(43 / 8)
    assert forced["equals_three"] is False


def test_the_coupling_guard_fires_on_the_inconsistent_combination(monkeypatch):
    """43 with b_3/8 gives 5.375 generations. The root must refuse it."""
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_43_joyce")
    monkeypatch.setenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", "b3_over_dim_O")
    with pytest.raises(ValueError, match="not three"):
        _root()()


def test_the_consistent_combinations_do_not_raise(monkeypatch):
    """The guard must not be so eager that it blocks valid states."""
    for seed, source in (("seed_24", "b3_over_dim_O"),
                         ("seed_43_joyce", "b2_over_faces")):
        monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", seed)
        monkeypatch.setenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", source)
        sim = _root()()
        assert sim._n_gen == 3, (seed, source, sim._n_gen)


# ------------------------------------------- the CERTIFICATES, not just run()

def _formulas(sim):
    return {f.id: f for f in sim.get_formulas()}


def test_the_published_certificates_move_with_the_seed(monkeypatch):
    """run() consumed the fork while the certificates still said 24.

    The Formula rows are what the website, the paper and the datasheets
    publish. While their `value`, `latex` and `terms` were literals, a reader
    of the generated artifacts could not tell the fork existed -- the simulation
    emitted 43 and every certificate next to it still read 24.
    """
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_24")
    monkeypatch.setenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", "b3_over_dim_O")
    at_24 = _formulas(_root()())
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_43_joyce")
    monkeypatch.setenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", "b2_over_faces")
    at_43 = _formulas(_root()())

    assert at_24["betti-numbers"].value == 24.0
    assert at_43["betti-numbers"].value == 43.0
    assert "b3=24" in at_24["betti-numbers"].plain_text
    assert "b3=43" in at_43["betti-numbers"].plain_text
    assert "b2=4," in at_24["betti-numbers"].plain_text
    assert "b2=12," in at_43["betti-numbers"].plain_text

    # Poincare duality must survive the move, in the published string.
    assert "b4=43" in at_43["betti-numbers"].plain_text
    assert "b5=12" in at_43["betti-numbers"].plain_text


def test_no_certificate_term_still_carries_a_frozen_seed(monkeypatch):
    """Every `terms` entry bound to a seed-derived param must follow the seed."""
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_43_joyce")
    forms = _formulas(_root()())
    terms = forms["betti-numbers"].terms
    by_param = {v.get("param_id"): v.get("value")
                for v in terms.values() if isinstance(v, dict)}
    assert by_param["topology.elder_kads"] == "43"
    assert by_param["topology.b2"] == "12"


def test_the_adopted_branch_publishes_the_found_solution(monkeypatch):
    """The default certificates carry (12, 43) -- and the labelled off-path
    branch still publishes exactly what it always did, so nothing was lost
    in the adoption (author ruling 2026-09-22)."""
    monkeypatch.delenv("METAPHYSICA_VARIANT_B3_SEED", raising=False)
    monkeypatch.delenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", raising=False)
    forms = _formulas(_root()())
    assert forms["betti-numbers"].value == 43.0
    assert forms["euler-characteristic"].value == 144.0, (
        "chi_eff stays 144 pending its own ruling; the seed flip decides b_3"
    )
    assert forms["three-generations"].value == 3.0
    assert (forms["betti-numbers"].plain_text
            == "b0=1, b1=0, b2=12, b3=43, b4=43, b5=12, b6=0, b7=1")

    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_24")
    monkeypatch.setenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", "b3_over_dim_O")
    off = _formulas(_root()())
    assert off["betti-numbers"].value == 24.0
    assert (off["betti-numbers"].plain_text
            == "b0=1, b1=0, b2=4, b3=24, b4=24, b5=4, b6=0, b7=1"), (
        "the off-path branch must keep publishing its own record unchanged"
    )


def test_the_k_matching_identity_is_reported_as_broken_on_the_43_path(
        monkeypatch):
    """K = h^{1,1} = b_2 is a chain of two claims, and the seed breaks the
    second one. It must be reported, not silently left reading 4 = 4."""
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_24")
    monkeypatch.setenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", "b3_over_dim_O")
    at_24 = _root()()
    assert at_24._k_matching_equals_b2 is True

    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_43_joyce")
    monkeypatch.setenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", "b2_over_faces")
    at_43 = _root()()
    assert at_43._K_matching == 4, "h^{1,1} is a TCS Hodge number, not a seed"
    assert at_43._b2 == 12
    assert at_43._k_matching_equals_b2 is False

    steps = _formulas(at_43)["cycle-matching"].derivation["steps"]
    assert any("BREAKS" in s for s in steps), (
        "the broken identity must appear in the published derivation"
    )


def test_the_chi_eff_divergence_reaches_the_published_certificate(monkeypatch):
    """The two chi_eff routes diverge at 43; the certificate must say so."""
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_43_joyce")
    steps = _formulas(_root()())["euler-characteristic"].derivation["steps"]
    assert any("DIVERGE" in s for s in steps)


def test_the_default_path_is_the_adopted_ruling(monkeypatch):
    """The default state is the RULED one (b3_seed adoption 2026-09-22):
    seed_43_joyce with n_gen = b_2/4 = 3 via b2_over_faces."""
    monkeypatch.delenv("METAPHYSICA_VARIANT_B3_SEED", raising=False)
    monkeypatch.delenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", raising=False)
    report = n_gen_report()
    assert report["path"] == "seed_43_joyce"
    assert report["declared_source"] == "b2_over_faces"
    assert report["n_gen"] == 3.0
