"""chi_eff_total is an Euler characteristic, so it must be an integer.

`seed_dependent` gives b_3^2/4, integral only for even b_3. PM accepts exactly
the (b3_seed, chi_eff_route) pairs with an integral chi_eff_total, and the
fail-early check in registry_chi_eff_total refuses the rest.
"""
import pytest

from metaphysica.simulations.core.variants import FORKS
from metaphysica.simulations.core.variants.selection import compatible
from metaphysica.simulations.PM.geometry.b3_path import seed_values
from metaphysica.simulations.PM.geometry.chi_eff_branches import (
    registry_chi_eff_total)

SEEDS = [o.id for o in FORKS["b3_seed"].options]
ROUTES = [o.id for o in FORKS["chi_eff_route"].options]
PAIRS = [(s, r) for s in SEEDS for r in ROUTES]


def _integral(seed, route):
    try:
        return float(registry_chi_eff_total(route, seed_values(seed)[0])).is_integer()
    except ValueError:
        return False


@pytest.mark.parametrize("seed,route", PAIRS)
def test_catalogue_accepts_exactly_the_integral_pairs(seed, route):
    sel = {"b3_seed": seed, "chi_eff_route": route}
    assert compatible(sel) == _integral(seed, route)


def test_integral_pairs_are_the_constant_routes_plus_seed_24():
    ok = {p for p in PAIRS if _integral(*p)}
    assert ("seed_24", "seed_dependent") in ok
    assert not any(r == "seed_dependent" and s != "seed_24" for s, r in ok)
    assert len(ok) == len(SEEDS) * (len(ROUTES) - 1) + 1


def test_non_integral_chi_raises_like_the_n_gen_check():
    with pytest.raises(ValueError, match="not an integer"):
        registry_chi_eff_total("seed_dependent", 43)
