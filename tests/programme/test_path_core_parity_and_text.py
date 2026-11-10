"""L1 path-core round 5: parity guard, named-constants text, nomenclature,
CANON tau_p and the shape_search entry point read the path in force."""
from __future__ import annotations

import json
import math

import pytest

from metaphysica.simulations.core.variants import selection
from metaphysica.simulations.PM.geometry.b3_path import resolve_path, seed_values


def _forced(seed):
    return selection.forced({"b3_seed": seed}) if seed else selection.forced({})


def _registry():
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    return FormulasRegistry()


def test_canon_tau_p_is_read_from_the_artifact():
    from metaphysica.simulations.core.canonical_values import canon
    from metaphysica.simulations.core.parameter_artifact import parameter_value

    row = "proton_decay.tau_p_years"
    entry = canon()["tau_p_years"]
    assert entry["value"] == parameter_value(row)
    assert row in entry["source"]
    assert entry["comparison"]["ratio"] == entry["value"] / entry["comparison"]["exp"]


@pytest.mark.parametrize("seed", [None, "seed_24"])
def test_parity_check_is_an_identity_on_every_seed(seed):
    with _forced(seed):
        reg = _registry()
        b3 = seed_values(resolve_path())[0]
        assert reg.verify_parity()
        assert reg.parity_sum_on_path() == pytest.approx(
            163 / (10 * b3 - 1) + reg.tzimtzum_pressure, abs=1e-12)
    if seed == "seed_24":
        assert reg.parity_sum == pytest.approx(163 / 239 + 23 / 24, abs=1e-12)


def test_named_constants_verification_text_is_computed():
    with _forced(None):
        reg = _registry()
        manifest = reg.generate_named_constants_json()
    b3 = reg.elder_kads
    assert b3 != 24
    ver = manifest["verification"]
    assert ver["status"] == "IDENTITY"
    assert all(ver[k]["status"] == "IDENTITY" and ver[k]["valid"]
               for k in ("integer_closure", "parity_check", "tzimtzum_fraction"))
    assert "163/%d" % (10 * b3 - 1) in ver["parity_check"]["formula"]
    c_kaf = manifest["precision_constants"]["c_kaf"]["formula"]
    assert "%s * %s / %s" % (b3, b3 - 7, b3 - 9) in c_kaf and "27.2" not in c_kaf
    text = json.dumps(manifest, ensure_ascii=False)
    assert "163/239" not in text and "1.6403" not in text
    assert '"formula": "23/24' not in text and "-23/24" not in text


@pytest.mark.parametrize("seed", [None, "seed_24"])
def test_nomenclature_k_gimel_and_c_kaf_follow_the_path(seed):
    from metaphysica.config import BraneNomenclature, HebrewPhysicsNomenclature

    with _forced(seed):
        b3 = seed_values(resolve_path())[0]
        k_gimel = b3 / 2 + 1 / math.pi
        c_kaf = b3 * (b3 - 7) / (b3 - 9)
        assert HebrewPhysicsNomenclature.K_GIMEL == pytest.approx(k_gimel)
        assert BraneNomenclature.K_GIMEL == pytest.approx(k_gimel)
        assert HebrewPhysicsNomenclature.C_KAF == pytest.approx(c_kaf)
        rows = HebrewPhysicsNomenclature.get_all_parameters()["parameters"]
        assert rows["k_gimel"]["value"] == pytest.approx(k_gimel)
        assert rows["C_kaf"]["value"] == pytest.approx(c_kaf)
        assert "%s/2" % b3 in rows["k_gimel"]["derivation"]
        assert "-%s /" % b3 in HebrewPhysicsNomenclature.C_KAF_APPLICATION
        assert BraneNomenclature.localization_factor(1) == pytest.approx(
            math.exp(-k_gimel * math.pi / 3))


def test_shape_search_primitives_read_the_path():
    from metaphysica.simulations.core import shape_search

    with _forced("seed_24"):
        prims = shape_search.primitives()
        assert prims["b3"][0] == 24 == seed_values(resolve_path())[0]


def test_shape_search_missing_primitive_raises(monkeypatch):
    from metaphysica.simulations.core import arithma_formula, shape_search

    monkeypatch.setattr(arithma_formula, "registry_value", lambda path: None)
    with pytest.raises(ValueError, match="D_bulk"):
        shape_search.primitives()


def test_shape_search_has_a_command_line_entry(capsys):
    from metaphysica.simulations.core import shape_search

    assert shape_search.main(["137.036", "--name", "alpha_inv"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["target_name"] == "alpha_inv"
    assert out["n_searched"] > 0 and "verdict" in out
