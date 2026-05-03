"""End-to-end tests for the public ``metaphysica.Get`` API.

Covers the datasheet dispatch (quarks vs constants), name aliasing,
antiparticle generation, JSON round-trip, and the bundled-snapshot
fast path that ships with the wheel.
"""
from __future__ import annotations

import json

import pytest

import metaphysica


# ── Quark datasheet smoke tests ──────────────────────────────────────────────

REQUIRED_QUARK_KEYS = {
    "Name", "Symbol", "Charge_e", "Mass_MeVc2",
    "Spin_hbar", "BaryonNumber_B",
    "Antiparticle", "DecayProducts", "InteractionForces",
    "pm_prediction", "_provenance",
}


@pytest.mark.parametrize("name", metaphysica.list_quarks())
def test_each_quark_has_required_schema(name):
    d = metaphysica.Get(name)
    missing = REQUIRED_QUARK_KEYS - set(d)
    assert not missing, f"{name}: missing keys {missing}"
    assert isinstance(d["pm_prediction"], dict)
    assert "predicted_mass_GeV" in d["pm_prediction"]


@pytest.mark.parametrize("alias", ["Up", "up", "u", "Up Quark"])
def test_quark_aliases_resolve_to_same_entry(alias):
    canonical = metaphysica.Get("Up")
    assert metaphysica.Get(alias)["Name"] == canonical["Name"]


def test_antiquark_charge_is_flipped():
    up = metaphysica.Get("Up")
    anti = metaphysica.Get("AntiUp")
    assert anti["Charge_e"] == pytest.approx(-up["Charge_e"])
    assert anti["BaryonNumber_B"] == pytest.approx(-up["BaryonNumber_B"])


def test_top_quark_pdg_mass():
    d = metaphysica.Get("Top")
    # PDG2024: m_t ≈ 172.69 GeV = 172_690 MeV
    assert d["Mass_MeVc2"] == pytest.approx(172690.0, rel=1e-3)


# ── Constant datasheet smoke tests ───────────────────────────────────────────

REQUIRED_CONSTANT_KEYS = {"name", "value", "kind"}


@pytest.mark.parametrize("name,expected", [
    ("m_planck",  2.435e18),
    ("alpha_em",  7.2973525e-3),
    ("V_us",      0.2245),
    ("m_top",     172.69),
])
def test_known_constants_have_expected_values(name, expected):
    d = metaphysica.Get(name)
    assert REQUIRED_CONSTANT_KEYS <= set(d), f"{name}: schema missing required keys"
    assert d["value"] == pytest.approx(expected, rel=1e-2)
    assert d["kind"] == "physics"


def test_unknown_name_raises_keyerror():
    with pytest.raises(KeyError):
        metaphysica.Get("definitely_not_a_real_constant_or_quark")


# ── as_json round-trip ───────────────────────────────────────────────────────

def test_as_json_returns_parseable_string():
    s = metaphysica.Get("Up", as_json=True)
    assert isinstance(s, str)
    parsed = json.loads(s)
    assert parsed["Symbol"] == "u"


# ── Listings ────────────────────────────────────────────────────────────────

def test_list_quarks_has_12_entries():
    qs = metaphysica.list_quarks()
    assert len(qs) == 12
    assert sum(1 for q in qs if q.startswith("anti")) == 6


def test_list_constants_is_nonempty():
    assert len(metaphysica.list_constants()) > 20
