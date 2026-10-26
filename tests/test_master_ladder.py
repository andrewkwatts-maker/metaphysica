"""The PM master action as a checked ladder (lane L2a)."""

from __future__ import annotations

import importlib
import json

import pytest

from metaphysica.simulations.PM.gauge import master_ladder as ML
from metaphysica.simulations.PM.gauge import master_ladder_steps as S

# Ratchet: these only go down. Recorded 2026-10-27 under the recommended options.
MAX_OPEN_TERMS = 15
MAX_FAILING_CHECKS = 1


def _dump(rep):
    return json.dumps(rep, sort_keys=True)


def _ids(rep):
    return {c["id"]: c for s in rep["ladder"]["steps"] for c in s["checks"]}


def test_report_is_deterministic_and_json_ready():
    assert _dump(ML.report()) == _dump(ML.report())
    assert _dump(ML.report({2: "dirac"})) == _dump(ML.report({2: "dirac"}))


def test_every_non_open_term_balances_dimensionally():
    ladder = ML.build_ladder(ML.resolve_options())
    for step in ladder.steps:
        a = step.action
        for t in a.terms:
            if not t.open:
                assert a.term_dim(t) == a.dim, (a.id, t.id)


def test_failing_control_wrong_planck_exponent_breaks_balance():
    rep = ML.report({4: 23})
    assert not _ids(rep)["dim:A26:R"]["holds"]
    assert _ids(ML.report())["dim:A26:R"]["holds"]


def test_every_provider_is_importable_or_term_is_open():
    ladder = ML.build_ladder(ML.resolve_options())
    seen = set()
    for step in ladder.steps:
        for t in step.action.terms:
            c = t.coefficient
            if c.source == "OPEN":
                assert c.provider is None and t.open
            else:
                importlib.import_module(c.provider)
                seen.add(c.provider)
    assert seen == {S.P_MASTER, S.P_LADDER}


def test_open_terms_cite_the_audit():
    rep = ML.report()
    assert all("master_action_audit" in v for v in rep["open_terms"].values())
    assert {"undefined:rho_breath", "undefined:OR^i", "undefined:V_bridge",
            "undefined:V_face", "undefined:V_tor", "A26:L_C"} <= set(rep["open_terms"])


def test_weyl_and_dirac_differ_only_in_mass_quartic_and_spinor_counts():
    weyl, dirac = ML.report(), ML.report({2: "dirac"})
    assert set(dirac["open_terms"]) - set(weyl["open_terms"]) == {"A26:psi_mass",
                                                                  "A26:psi_quartic"}
    assert set(weyl["open_terms"]) <= set(dirac["open_terms"])
    w, d = _ids(weyl), _ids(dirac)
    only = set(w) ^ set(d)
    assert only == {"dim:A26:psi_mass", "source:A26:psi_mass", "open:A26:psi_mass",
                    "dim:A26:psi_quartic", "source:A26:psi_quartic", "open:A26:psi_quartic"}
    assert {k: v["holds"] for k, v in w.items() if k in d} == \
           {k: v["holds"] for k, v in d.items() if k in w}
    assert w["spinor_product:26D"]["measured"] == "4096"
    assert d["spinor_product:26D"]["measured"] == "8192"
    assert weyl["spinors"] == dirac["spinors"]


def test_a_dirac_mass_on_a_weyl_field_would_fail():
    from metaphysica.actions.dimensions import check_action
    from dataclasses import replace
    a = S.action_26("weyl", 24, "mostly_plus")
    mass = S.action_26("dirac", 24, "mostly_plus").terms[2]
    bad = replace(a, terms=a.terms + (mass,))
    assert [c.id for c in check_action(bad) if not c.holds] == ["weyl_mass:A26:psi_mass"]


def test_item_11_product_rule():
    r = ML.item_11()
    assert r["product_13_13"] == 8192 == r["dirac_26"] and r["weyl_26"] == 4096
    assert r["naive_64x64"] == 4096 and r["supports"].startswith("dirac_8192")


def test_item_6_gate_is_the_first_failure():
    rep = ML.report()
    assert rep["ladder"]["verdict"] == "owner_item_6"
    assert rep["failing_checks"] == ["owner_item_6"]
    assert rep["owner_items_used"] == {"2": "weyl", "4": 24, "5": "mostly_plus_mtw",
                                       "11": "computed"}


def test_unknown_override_fails_early():
    with pytest.raises(KeyError):
        ML.report({99: 1})
    with pytest.raises(ValueError):
        ML.report({2: "majorana"})


def test_ratchet_never_goes_up():
    c = ML.report()["counts"]
    assert c["open_terms"] <= MAX_OPEN_TERMS
    assert c["failing_checks"] <= MAX_FAILING_CHECKS


def test_g2_betti_come_from_the_adopted_seed():
    ladder = ML.build_ladder(ML.resolve_options())
    betti = ladder.steps[2].reduction.internal.betti
    assert (betti[2], betti[3]) == (12, 43) and betti[1] == 0


def test_map_covers_every_published_action_formula():
    import os
    from metaphysica.simulations.PM.gauge import master_ladder_map as M
    root = os.environ.get("PM_PUBLISHED_ROOT", M.DEFAULT_ROOT)
    if not os.path.isdir(root):
        pytest.skip("published artifacts not present")
    rows = M.build_rows(M.published_ids())
    assert {r[1] for r in rows} <= set(M.KINDS)
    assert "step" in M.render(rows)


def test_map_fails_on_an_unmapped_formula():
    from metaphysica.simulations.PM.gauge import master_ladder_map as M
    with pytest.raises(KeyError):
        M.build_rows(["brand-new-action"])
