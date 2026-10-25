"""CG.13: the holonomy-G2 metric exists by theorem, and says why when it does not.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.closed_geometry.certificate import (
    certificate,
)


def _cg13():
    return next(e for e in certificate() if e["id"] == "y7-holonomy-g2-metric")


def test_cg13_holds_on_the_active_path():
    entry = _cg13()
    assert entry["label"] == "(CG.13)"
    assert entry["holds"] and entry["derived"]
    assert "No explicit metric is claimed" in entry["statement"]
    assert entry["evidence"]["spinors"] == 1


@pytest.mark.parametrize("env, value, failure, derived", [
    ("METAPHYSICA_VARIANT_G2_FORM_CONVENTION", "all_plus_one", "H2", True),
    ("METAPHYSICA_VARIANT_B3_SEED", "seed_24", "H3", False),
])
def test_cg13_names_the_failing_hypothesis_off_path(monkeypatch, env, value,
                                                    failure, derived):
    monkeypatch.setenv(env, value)
    entry = _cg13()
    assert entry["holds"] is False
    assert entry["derived"] is derived
    assert "NOT established" in entry["statement"]
    assert "hypothesis %s" % failure in entry["statement"]
