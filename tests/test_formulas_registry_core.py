"""
Unit Tests for FormulasRegistry - Core Infrastructure
=====================================================
Tests the Single Source of Truth (SSoT) for correctness of
Ten Pillar Seeds, derived quantities, and precision context.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

import math
import sys
from decimal import getcontext, ROUND_HALF_EVEN
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "simulations"))

from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry, get_registry, lock_geometric_context


@pytest.fixture(scope="module")
def registry():
    """Get the singleton FormulasRegistry instance."""
    return get_registry()


def _registry_on_seed(monkeypatch, seed: str) -> FormulasRegistry:
    """A FRESH registry built under a named branch of the b3_seed fork.

    get_registry() hands back a singleton constructed at first use, so an
    environment override cannot reach it -- the object the fixture holds was
    built before the variable moved. A new instance re-reads the fork.

    The fork was RULED on 2026-09-22: seed_43_joyce is adopted, so the
    default resolution is (b_3, b_2) = (43, 12). seed_24 = (24, 4) stays
    runnable as the labelled off-path branch, which is what the twin
    assertions below exercise.
    """
    from metaphysica.simulations.core.variants import _ENV_PREFIX

    monkeypatch.setenv(_ENV_PREFIX + "B3_SEED", seed)
    return FormulasRegistry()


class TestPrecisionContext:
    """Tests for the geometric precision context."""

    def test_precision_is_64_digits(self):
        lock_geometric_context()
        ctx = getcontext()
        assert ctx.prec == 64

    def test_rounding_mode(self):
        lock_geometric_context()
        ctx = getcontext()
        assert ctx.rounding == ROUND_HALF_EVEN


class TestTenPillarSeeds:
    """Tests for the Ten Pillar Seeds - the ONLY hardcoded inputs."""

    def test_b3_follows_the_adopted_seed(self, registry, monkeypatch):
        """Third Betti number b3 (elder_kads) is 43 on the adopted path.

        Was pinned at 24. The b3_seed fork adopted seed_43_joyce by author
        ruling 2026-09-22, which makes b_3 DERIVED (7 flat + 3 x 12 A1
        families) rather than an input of open origin. The off-path branch
        keeps its old value and is asserted alongside so the switch stays
        demonstrably live.
        """
        # 43 measured 2026-09-22, b3_seed adoption (was 24)
        assert registry.elder_kads == 43
        # 24 measured 2026-09-22 on the labelled off-path branch
        assert _registry_on_seed(monkeypatch, "seed_24").elder_kads == 24

    def test_golden_ratio(self, registry):
        """Golden ratio phi = (1 + sqrt(5)) / 2."""
        expected = (1.0 + math.sqrt(5.0)) / 2.0
        assert registry._phi == pytest.approx(expected, rel=1e-15)

    def test_demiurgic_coupling(self, registry, monkeypatch):
        """kappa_Delta = b_3/2 + 1/pi, so it moves with the seed."""
        # 21.81830988618379 measured 2026-09-22, b3_seed adoption
        # (was 12.31830988618379, which is the seed_24 reading below)
        assert registry.demiurgic_coupling == pytest.approx(
            21.81830988618379, rel=1e-12
        )
        off_path = _registry_on_seed(monkeypatch, "seed_24")
        assert off_path.demiurgic_coupling == pytest.approx(
            12.31830988618379, rel=1e-12
        )
        # the formula itself is unchanged by the ruling; only its input moved
        assert registry.demiurgic_coupling == pytest.approx(
            registry.elder_kads / 2 + 1 / math.pi, rel=1e-12
        )

    def test_tzimtzum_pressure(self, registry):
        """sigma_T = 23/24."""
        assert registry._tzimtzum_pressure == pytest.approx(23.0 / 24.0, rel=1e-15)

    def test_sophian_drag(self, registry, monkeypatch):
        """eta_S = 163 / (10 b_3 - 1), derived from b_3 and so seed-following."""
        # 0.37995337995337997 (= 163/429) measured 2026-09-22, b3_seed
        # adoption (was 0.6820083682008368 = 163/239 under seed_24)
        assert registry._sophian_drag == pytest.approx(
            0.37995337995337997, rel=1e-12
        )
        off_path = _registry_on_seed(monkeypatch, "seed_24")
        assert off_path._sophian_drag == pytest.approx(
            0.6820083682008368, rel=1e-12
        )

    def test_odowd_bulk_pressure(self, registry):
        """O'Dowd Bulk Pressure = 163."""
        assert registry._odowd_bulk_pressure == 163

    def test_penrose_hameroff_bridge(self, registry):
        """Penrose-Hameroff Bridge = 13."""
        assert registry._penrose_hameroff_bridge == 13

    def test_hossenfelder_root(self, registry):
        """Hossenfelder Root = sqrt(24)."""
        assert registry._hossenfelder_root == pytest.approx(math.sqrt(24), rel=1e-15)


class TestDerivedQuantities:
    """Tests for quantities derived from the Ten Pillar Seeds."""

    def test_parity_sum(self, registry, monkeypatch):
        """Parity sum = sophian_drag + tzimtzum_pressure.

        sigma_T = 23/24 is fixed, so the whole move comes from eta_S, which
        follows b_3.
        """
        # 1.3382867132867133 measured 2026-09-22, b3_seed adoption
        # (was 1.6403417015341701 = 163/239 + 23/24 under seed_24)
        assert registry.parity_sum == pytest.approx(
            1.3382867132867133, rel=1e-12
        )
        off_path = _registry_on_seed(monkeypatch, "seed_24")
        assert off_path.parity_sum == pytest.approx(
            1.6403417015341701, rel=1e-12
        )

    def test_n_gen_equals_3(self, registry):
        """UNBLOCKED same day: registry.n_gen now routes through the FORK.

        The property was chi_eff // b_3 (72 // 43 = 1 on the adopted seed,
        measured) -- an unruled numerator over a moved denominator. It now
        resolves n_gen_source live (b2_over_faces RULED -> b_2/4 = 3), so
        this asserts the registry agrees with the ruled route on the
        adopted branch, integrally -- and a future re-ruling changes the
        fork's option, not this property's code.
        """
        assert registry.n_gen == 3
        assert isinstance(registry.n_gen, int)

    def _superseded_note(self):
        """The old skip text, kept for the record:

        registry.n_gen was chi_eff // b_3. The b3_seed adoption (2026-09-22)
        made that 72 // 43 = 1, measured. It was NOT repinned to 1,
        because the generation count itself did not move: the n_gen_source
        fork was ruled to b_2 / n_faces = 12 / 4 = 3, which the test below
        asserts live. Whether the chi_eff route also returns 3 depends on
        the chi_eff ruling, which has not landed, and this test must not
        pre-empt it.
        """

    def test_n_gen_comes_from_b2_over_faces(self):
        """The RULED generation route: n_gen = b_2 / n_faces = 12 / 4 = 3.

        The n_gen_source fork was ruled to b2_over_faces alongside the
        b3_seed adoption (2026-09-22). It relocates the origin of the three
        generations from b_3 and dim O to b_2 and the faces; both sides are
        derived, and the old route stops being integral, which is what makes
        the relocation forced rather than chosen.
        """
        from metaphysica.simulations.PM.geometry.b3_path import n_gen_report

        report = n_gen_report()
        assert report["declared_source"] == "b2_over_faces"
        # 3.0 measured 2026-09-22, b3_seed adoption
        assert report["n_gen"] == 3
        assert report["equals_three"] is True
        # 5.375 measured 2026-09-22: 43/8 is not a count of anything
        assert report["b3_over_dim_O"]["value"] == 5.375
        assert report["b3_over_dim_O"]["integer"] is False

    def test_chi_eff_positive(self, registry):
        """Effective Euler characteristic must be positive."""
        assert registry.chi_eff > 0


class TestSingleton:
    """Tests that the registry is a proper singleton."""

    def test_get_registry_returns_same_instance(self):
        """Multiple calls to get_registry() return the same object."""
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_registry_has_required_attributes(self, registry):
        """Registry exposes all required seed attributes."""
        required = ['elder_kads', 'demiurgic_coupling', 'parity_sum', 'n_gen', 'chi_eff']
        for attr in required:
            assert hasattr(registry, attr), f"Registry missing attribute: {attr}"


class TestLegacyAliases:
    """Tests that legacy accessor names still work."""

    def test_b3_property(self, registry):
        """b3 property should equal elder_kads."""
        assert registry.b3 == registry.elder_kads
