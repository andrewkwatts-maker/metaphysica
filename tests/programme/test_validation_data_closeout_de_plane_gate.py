"""XV-16: the DE plane gate scores the registered (w0, wa), not -(b3-1)/b3.

w0 is registered by the dark_energy_betti fork (-(n-1)/n); the gate used to
recompute it as -(B3-1)/B3 at the live b3, which on seed_43_joyce gave -42/43
while the register holds -(n-1)/n at the fork's n. Expected values below come
from the fork readers, the seed reader and the DESI loader, never typed.

Review round: an INPUT w0 is not scored (the plane is INPUT_CONDITIONED, wa
1D is the scored number); the note, the kill condition and the anchors are
built from the computed values; the gate and the scored wa_derived row report
one wa tension.
"""
from __future__ import annotations

import math
import re

import pytest

from metaphysica.simulations.core.canonical_values import CANON
from metaphysica.simulations.core.variants import selection
from metaphysica.simulations.PM.cosmology.late_time_routes import (
    de_betti_n,
    resolve_de_betti,
)
from metaphysica.simulations.PM.geometry.b3_path import resolve_path, seed_values
from metaphysica.simulations.PM.validation.de_plane_gate import (
    build_payload,
    framework_point,
    standardized,
)


def _registered_point() -> dict:
    n = de_betti_n(resolve_de_betti())
    b3 = seed_values(resolve_path())[0]
    return {"w0": -(n - 1) / n, "wa": -1.0 / math.sqrt(b3)}


def test_point_is_the_registered_point_on_the_active_path():
    expected = _registered_point()
    p = framework_point()
    assert p["w0"] == pytest.approx(expected["w0"], abs=1e-12)
    assert p["wa"] == pytest.approx(expected["wa"], abs=1e-12)


def test_w0_follows_the_dark_energy_betti_fork_not_b3():
    """Under a frozen fork option w0 is -(n-1)/n at that n, whatever b3 is."""
    b3 = seed_values(resolve_path())[0]
    for option in ("b3_24", "bridges_12"):
        n = de_betti_n(option)
        with selection.forced({"dark_energy_betti": option}):
            w0 = framework_point()["w0"]
        assert w0 == pytest.approx(-(n - 1) / n, abs=1e-12)
        if n != b3:
            assert w0 != pytest.approx(-(b3 - 1) / b3, abs=1e-9)


@pytest.mark.parametrize("seed", ["seed_24", "seed_43_joyce"])
def test_b3_live_scores_the_plane_on_each_seed(seed):
    """Under b3_live w0 = -(b3-1)/b3 is PREDICTED, so the plane is scored."""
    with selection.forced({"b3_seed": seed, "dark_energy_betti": "b3_live"}):
        b3 = seed_values(resolve_path())[0]
        w0 = framework_point()["w0"]
        payload = build_payload()
    assert w0 == pytest.approx(-(b3 - 1) / b3, abs=1e-12)
    assert payload["framework_status"]["w0"]["status"] == "PREDICTED"
    assert payload["scored"] == "plane"
    assert payload["verdict"].startswith("TENSION_")
    assert payload["scored_sigma"] == min(payload["sigma_range"])


def test_input_w0_is_not_scored():
    """Rule 4: under a frozen option w0 is INPUT and the plane is not scored."""
    with selection.forced({"dark_energy_betti": "b3_24"}):
        assert CANON["w0"]["status"] == "INPUT"
        payload = build_payload()
    assert payload["verdict"] == "INPUT_CONDITIONED"
    assert payload["scored"] == "wa"
    assert payload["scored_sigma"] == payload["one_d_marginals_sigma"]["wa"]
    assert "INPUT" in payload["note"] and "INPUT" in payload["kill_condition"]


def _numbers(text: str) -> list:
    return [float(x) for x in re.findall(r"\d+\.\d\d(?!\d)", text)]


def test_note_quotes_the_computed_marginals_and_band():
    payload = build_payload()
    found = _numbers(payload["note"])
    marg = payload["one_d_marginals_sigma"]
    lo, hi = payload["sigma_range"]
    for value in (marg["w0"], marg["wa"], lo, hi, payload["uncorrelated_2d_sigma"]):
        assert round(value, 2) in found, value
    assert "3.62-sigma (w0) and 2.98-sigma (wa)" not in payload["note"]


def test_kill_condition_names_the_registered_forms():
    payload = build_payload()
    for key in ("w0", "wa"):
        assert CANON[key]["form"] in payload["kill_condition"]
        assert CANON[key]["status"] in payload["kill_condition"]


def test_gate_and_scored_row_report_one_wa_tension():
    from metaphysica.simulations.PM.cosmology.dark_energy import DarkEnergyV16

    row = next(r for r in DarkEnergyV16().get_output_param_definitions()
               if r.path == "cosmology.wa_derived")
    payload = build_payload()
    assert payload["anchors"]["wa"] == [row.experimental_bound, row.uncertainty]
    expected = abs(framework_point()["wa"] - row.experimental_bound) / row.uncertainty
    assert abs(standardized()[1]) == pytest.approx(expected, rel=1e-12)
