"""dark_energy_betti acts only under dark_energy_mechanism=thawing_quintessence.

Under mep_11_13 no consumer may read it, and every option gives one w0. If
mep ever reads n, these tests fail.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.core import variants as V
from metaphysica.simulations.core.FormulasRegistry import get_registry
from metaphysica.simulations.PM.cosmology import late_time_routes as ltr
from metaphysica.simulations.PM.geometry.geometric_anchors_core import (
    GeometricAnchors,
)

MEP = "mep_11_13"
THAWING = "thawing_quintessence"
OPTIONS = V.FORKS["dark_energy_betti"].option_ids()


def _callers():
    """Each of the callers' w0 under the current resolution."""
    out = {
        "geometric_anchors_core": GeometricAnchors().w_zero,
        "formulas_registry": get_registry().calculate_w0(),
        # dark_energy.py (two call sites) and demon_lock_guard use exactly
        # this call shape; their consumers are too heavy to build here.
        "late_time_routes": ltr.w0_for_mechanism(
            ltr.resolve_de_mechanism(), thawing=ltr.thawing_w0),
        "thunk_without_n": ltr.w0_for_mechanism(
            ltr.resolve_de_mechanism(), thawing=lambda: -23.0 / 24.0),
    }
    from metaphysica.simulations.core.demon_lock_guard import DemonLockGuard

    DemonLockGuard(registry=get_registry()).verify_w0_seal()
    return out


def test_every_betti_option_gives_the_same_w0_under_mep():
    seen = {}
    for opt in OPTIONS:
        with V.forced({"dark_energy_mechanism": MEP,
                       "dark_energy_betti": opt}):
            for name, w0 in _callers().items():
                if name != "thunk_without_n":
                    seen.setdefault(name, set()).add(w0)
    assert all(len(v) == 1 for v in seen.values()), seen


def test_betti_is_never_read_under_mep():
    for opt in OPTIONS:
        with V.forced({"dark_energy_mechanism": MEP,
                       "dark_energy_betti": opt}):
            V.reset_reads()
            _callers()
            assert "dark_energy_betti" not in V.reads()
            assert "dark_energy_betti" not in V.closed_gate_reads()


def test_selection_ids_ignore_a_gated_off_betti():
    assert (V.selection_id({"dark_energy_mechanism": MEP,
                            "dark_energy_betti": "b2_4"})
            == V.selection_id({"dark_energy_mechanism": MEP}))
    assert (V.selection_id({"dark_energy_mechanism": THAWING,
                            "dark_energy_betti": "b2_4"})
            != V.selection_id({"dark_energy_mechanism": THAWING}))


def test_combinations_dedupe_the_gated_off_fork():
    from metaphysica.simulations.core import switch_search as ss

    ids = ["dark_energy_mechanism", "dark_energy_betti"]
    combos = ss.combinations_for(ids)
    n_betti = len(OPTIONS)
    assert len(combos) == n_betti + 1
    assert ss.count_compatible(ids) == n_betti + 1


@pytest.mark.parametrize("opt", [o for o in OPTIONS if o != "b3_24"])
def test_options_differ_under_thawing(opt):
    with V.forced({"dark_energy_mechanism": THAWING,
                   "dark_energy_betti": "b3_24"}):
        base = GeometricAnchors().w_zero
    with V.forced({"dark_energy_mechanism": THAWING,
                   "dark_energy_betti": opt}):
        assert GeometricAnchors().w_zero != base
