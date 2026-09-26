"""w_0 has three DESI anchors, and the sigma depends on which one you pick.

THE FINDING
===========
`b3_path`'s docstring states the adopted path's cost as "0.94 sigma against
the registry's DESI anchor", as though the framework had one anchor for w_0.
It has at least three, registered separately, and the SAME prediction
(w_0 = -42/43 on the adopted seed) scores very differently against them:

    geometry.w0_observed_DESI  -0.958 +/- 0.02   -> 0.937 sigma
    desi.w0                    -0.957 +/- 0.067  -> 0.295 sigma
    desi.w0_thawing            -0.957 +/- 0.33   -> 0.060 sigma

A sixteen-fold spread in the error bar for one quantity. `established.py`
declares `desi.w0` the PRIMARY scoring anchor -- the DR2 headline -- and
`cosmology_sector_complete`, `dark_energy_thawing` and `established` itself
all cite that. `b3_path` scores against the `geometry.*` pair instead.

That direction is the safe one to be wrong in: the tightest anchor reports the
adoption as costing MORE than the primary anchor does, so the published cost is
pessimistic rather than flattering. It is still an undeclared choice, and a
prediction whose sigma can be selected is weaker evidence than one whose anchor
is named. So `downstream()` now names the anchor it used and publishes the
primary anchor's sigma beside it. The numbers are unchanged.

Choosing ONE anchor for w_0 is the author's ruling. Publishing which one is in
force is not, and is what this test enforces.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import pathlib

import pytest

_BUNDLED = (
    pathlib.Path(__file__).resolve().parents[1]
    / "src" / "metaphysica" / "data" / "parameters.json"
)
_B3_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "src" / "metaphysica" / "simulations" / "PM" / "geometry" / "b3_path.py"
)


@pytest.fixture(scope="module")
def params():
    return json.loads(_BUNDLED.read_text(encoding="utf-8"))["parameters"]


def _val(params, key):
    row = params.get(key)
    return row.get("value") if isinstance(row, dict) else row


def _w0_adopted():
    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path, seed_values,
    )
    b3 = seed_values(resolve_path())[0]
    return -(b3 - 1) / b3


# ------------------------------------------------------- the anchors disagree


def test_the_three_anchors_give_materially_different_sigmas(params):
    """Pinned so the spread cannot quietly widen or be papered over."""
    w0 = _w0_adopted()
    anchors = {
        "geometry": (_val(params, "geometry.w0_observed_DESI"),
                     _val(params, "geometry.w0_error_DESI")),
        "primary": (_val(params, "desi.w0"),
                    _val(params, "abstract.desi_w0_uncertainty")),
        "thawing": (_val(params, "desi.w0_thawing"), 0.33),
    }
    for name, (obs, err) in anchors.items():
        assert obs is not None and err, "anchor %s lost a row" % name

    sigmas = {n: abs(w0 - obs) / err for n, (obs, err) in anchors.items()}
    assert sigmas["geometry"] == pytest.approx(0.937, abs=0.01)
    assert sigmas["primary"] == pytest.approx(0.295, abs=0.01)
    assert sigmas["thawing"] == pytest.approx(0.060, abs=0.01)
    # The point of the test: they are not interchangeable.
    assert sigmas["geometry"] > 3 * sigmas["primary"], (
        "the anchors converged; if that is real, b3_path's undeclared choice "
        "stopped mattering and this test should be rewritten"
    )


def test_the_tightest_anchor_is_the_one_b3_path_uses(params):
    """So the published cost is pessimistic, not flattering. Worth pinning:
    if this ever flips, the framework would be quoting its best case."""
    w0 = _w0_adopted()
    geo = abs(w0 - _val(params, "geometry.w0_observed_DESI")) / _val(
        params, "geometry.w0_error_DESI")
    primary = abs(w0 - _val(params, "desi.w0")) / _val(
        params, "abstract.desi_w0_uncertainty")
    assert geo > primary, (
        "b3_path's anchor now reports a SMALLER sigma than the declared "
        "primary anchor, so the published cost has become the flattering one"
    )


# ------------------------------------------------- the choice must be declared


def test_b3_path_names_the_anchor_it_scored_against():
    """A sigma with no named anchor is the defect; the source must declare it."""
    src = _B3_PATH.read_text(encoding="utf-8")
    assert "w0_sigma_anchor" in src
    assert "w0_sigma_vs_primary_anchor" in src
    assert "w0_sigma_anchor_is_primary" in src


def test_the_uncertainty_is_read_from_a_row_not_typed():
    """A literal 0.067 here would be exactly the ghost literal this campaign
    removes. There is no desi.w0_sigma row, so the value must be read from
    abstract.desi_w0_uncertainty."""
    src = _B3_PATH.read_text(encoding="utf-8")
    assert 'abstract.desi_w0_uncertainty' in src
    sigma_block = src[src.index("w0_sigma_anchor"):]
    assert "0.067" not in sigma_block, (
        "the primary anchor's uncertainty was typed as a literal instead of "
        "read from its registered row"
    )


def test_downstream_publishes_the_anchor_whenever_it_publishes_a_sigma():
    """The two must travel together, or a reader meets a bare sigma again.

    In a bare process the registry has no w_0 rows, so no sigma is published
    and there is nothing to name -- that is consistent, and asserted rather
    than skipped so the pairing is checked in both states.
    """
    from metaphysica.simulations.PM.geometry.b3_path import (
        downstream, resolve_path,
    )
    out = downstream(resolve_path())
    if "w0_sigma_vs_desi" in out:
        assert out.get("w0_sigma_anchor"), (
            "a sigma was published with no anchor named"
        )
        assert out.get("w0_sigma_anchor_is_primary") is False
    else:
        assert "w0_sigma_anchor" not in out, (
            "an anchor was named without a sigma to go with it"
        )
