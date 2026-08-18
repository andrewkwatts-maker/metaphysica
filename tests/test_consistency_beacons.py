"""Tests for the seven v2.2.0 textbook consistency beacons.

Every beacon is a standard-physics cross-check that should pass by
construction — failures here indicate framework drift, not new physics.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from metaphysica.simulations.PM.validation.consistency_beacons import (
    ConsistencyBeacon,
    beacon_alpha_em_running,
    beacon_e8_freudenthal_dimension,
    beacon_g2_spinor_bundle_dimension,
    beacon_jarlskog_bound,
    beacon_km_unitarity,
    beacon_nufit_delta_m21,
    beacon_nufit_delta_m31,
    beacon_weyl_character_g2_fundamental,
    run_all_beacons,
    write_report,
)


def test_run_all_beacons_returns_thirteen_records():
    """12 beacons: 8 textbook checks + 4 LIVE registry beacons added by the
    2026-08 validation-coverage audit (PMNS unitarity, G_F-M_W-sin2thetaW
    identity, Friedmann closure, hbar*c unit chain) — the LIVE beacons read
    one side from the build's parameters.json so they can actually catch
    framework drift — plus the 2026-08-19 two-time bulk-accounting beacon
    (b3+2 = 26 = 2x13; Weyl(Cl(24,2)) = 4096) locking the dimensional
    ruling."""
    beacons = run_all_beacons()
    assert len(beacons) == 13
    for b in beacons:
        assert isinstance(b, ConsistencyBeacon)
        assert b.id.startswith("beacon.")


def test_km_unitarity_passes():
    b = beacon_km_unitarity()
    assert b.status == "PASS", f"CKM row-1 unitarity should pass; got delta={b.delta_pct}%"


def test_e8_freudenthal_dimension_exact():
    b = beacon_e8_freudenthal_dimension()
    assert b.value == 248
    assert b.status == "PASS"


def test_g2_spinor_bundle_dim_exact():
    b = beacon_g2_spinor_bundle_dimension()
    assert b.value == 8
    assert b.status == "PASS"


def test_weyl_g2_fundamental_exact():
    b = beacon_weyl_character_g2_fundamental()
    assert b.value == 7
    assert b.status == "PASS"


def test_nufit_delta_m_splittings_pass():
    assert beacon_nufit_delta_m21().status == "PASS"
    assert beacon_nufit_delta_m31().status == "PASS"


def test_alpha_em_running_passes():
    b = beacon_alpha_em_running()
    assert b.status == "PASS"


def test_jarlskog_bound_holds():
    b = beacon_jarlskog_bound()
    assert b.status == "PASS"


def test_all_beacons_pass_by_construction():
    """Textbook identities must all satisfy their tolerance thresholds.

    A FAIL here signals framework drift from standard physics — treat as
    a release blocker.
    """
    beacons = run_all_beacons()
    failures = [b for b in beacons if b.status != "PASS"]
    assert not failures, "Beacon failures: " + ", ".join(f.id for f in failures)


def test_write_report_produces_valid_json(tmp_path):
    beacons = run_all_beacons()
    path = write_report(beacons, out_path=tmp_path / "beacons.json")
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["count"] == len(beacons)
    assert payload["n_pass"] + payload["n_fail"] == payload["count"]
    assert isinstance(payload["beacons"], list)
    assert all("status" in b and "value" in b for b in payload["beacons"])
    assert "not predictions" in payload["note"].lower() or \
           "NOT predictions" in payload["note"]
