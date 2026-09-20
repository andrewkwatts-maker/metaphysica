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
    monkeypatch.delenv("METAPHYSICA_VARIANT_B3_SEED", raising=False)
    monkeypatch.delenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", raising=False)
    sim = _root()()
    b3, b2 = seed_values("seed_24")
    assert sim._b3 == b3 == 24
    assert sim._b2 == b2 == 4
    assert sim._b3_seed_path == "seed_24", (
        "the adopted branch must stay the status quo; adoption is the author's"
    )


def test_flipping_the_seed_moves_the_root_outputs(monkeypatch):
    """The whole point: topology.* must respond to the fork."""
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_43_joyce")
    sim = _root()()
    assert sim._b3 == 43
    assert sim._b2 == 12
    assert sim._n_gen == 3, "three generations must survive the relocation"
    # k_gimel = b_3/2 + 1/pi rides on the seed and must move with it
    assert sim._k_gimel > 21.0


def test_the_emitted_topology_rows_move_with_the_seed(monkeypatch):
    """Not just the attributes -- the dict run() actually publishes."""
    monkeypatch.delenv("METAPHYSICA_VARIANT_B3_SEED", raising=False)
    at_24 = _root()()
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_43_joyce")
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
    monkeypatch.delenv("METAPHYSICA_VARIANT_B3_SEED", raising=False)
    at_24 = _root()()
    assert at_24._chi_eff_from_hodge == 144
    assert at_24._chi_eff_from_b3 == pytest.approx(144.0)
    assert at_24._chi_eff_routes_agree is True

    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_43_joyce")
    at_43 = _root()()
    assert at_43._chi_eff_from_hodge == 144
    assert at_43._chi_eff_from_b3 == pytest.approx(462.25)
    assert at_43._chi_eff_routes_agree is False, (
        "the divergence must be reported, not smoothed over"
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


def test_the_default_path_is_untouched_by_the_fork_going_live(monkeypatch):
    """Making n_gen_source live must not move the adopted state."""
    monkeypatch.delenv("METAPHYSICA_VARIANT_B3_SEED", raising=False)
    monkeypatch.delenv("METAPHYSICA_VARIANT_N_GEN_SOURCE", raising=False)
    report = n_gen_report()
    assert report["path"] == "seed_24"
    assert report["declared_source"] == "b3_over_dim_O"
    assert report["n_gen"] == 3.0
