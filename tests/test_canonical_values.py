# -*- coding: utf-8 -*-
"""Internal-consistency tests for the canonical-value rulings.

Each ruling must (a) recompute exactly from its stated form, (b) sit at
the sigma its weighing claimed against the named dataset, and (c) never
coincide with one of its own superseded values — the regression that
created the original mess.
"""
import math

from metaphysica.simulations.core.canonical_values import (
    B3, CHI_EFF, CHI_SECTOR, B2, CANON, all_canonical, get,
)


def sigma(value, exp, unc):
    return abs(value - exp) / unc


def test_structural_identities():
    assert B3 == 24
    assert CHI_EFF == 6 * B3 == 144
    assert CHI_SECTOR == 72
    assert B2 == 4
    # shadow bookkeeping: 13 = 4 spacetime + 7 (V7) + 2 (T2)
    assert 4 + 7 + 2 == 13
    # Two-time ruling (2026-08-19): spinor 4096 = Weyl of Cl(24,2)
    # (Dirac 2^13 = 8192, chiral half 4096); bulk = D_crit = b3 + 2 = 26,
    # shadows (12,1)+(12,1) = 26 exactly.
    assert 2 ** 13 // 2 == 4096
    bulk = CANON["bulk"]
    assert bulk["value"] == 26 == B3 + 2
    assert 13 + 13 == bulk["value"]


def test_w0_ruling():
    e = get("w0")
    assert e["value"] == -(B3 - 1) / B3
    assert abs(e["value"] + 23 / 24) < 1e-15
    c = e["comparison"]
    assert sigma(e["value"], c["exp"], c["unc"]) < 0.05
    assert e["spare_vars"] == 0


def test_wa_ruling_minimal_form():
    e = get("wa")
    assert abs(e["value"] + 1 / math.sqrt(24)) < 1e-15
    c = e["comparison"]
    s = sigma(e["value"], c["exp"], c["unc"])
    # alive (below 2 sigma) but honestly not a close fit — that is the point
    assert 1.5 < s < 2.0
    # the retired projection is exactly 4x the canonical (b2 structural)
    assert abs(4 * e["value"] + 0.8165) < 1e-3
    assert e["spare_vars"] == 0


def test_h0_is_not_topology_first():
    e = get("H0_km_s_Mpc")
    assert e["status"] == "FITTED_COMPOSITE"
    # O'Dowd composite recomputes: 288/4 - 163/144 + 0.6819
    assert abs((288 / 4 - 163 / 144 + 0.6819) - e["value"]) < 5e-3
    c = e["comparison"]
    assert sigma(e["value"], c["exp"], c["unc"]) < 1.5   # SH0ES
    # and the superseded ricci variant is the one that FAILs
    assert "76.34" in e["superseded"]


def test_falsified_elegant_candidates_stay_falsified():
    th = get("theta13_deg")
    c = th["comparison"]
    # the beautiful asin(1/6) candidate really is dead
    assert sigma(math.degrees(math.asin(1 / 6)), c["exp"], c["unc"]) > 4
    # and the canonical form is alive
    assert sigma(th["value"], c["exp"], c["unc"]) < 0.5

    lc = get("lambda_cabibbo")
    c = lc["comparison"]
    assert sigma(math.exp(-math.pi / 2), c["exp"], c["unc"]) > 20
    assert sigma(lc["value"], c["exp"], c["unc"]) < 3


def test_sin2_theta_w_scheme_split():
    e = get("sin2_theta_w")
    assert e["value"] == 0.23122
    # the geometric candidate is superseded under this symbol
    assert "0.23190" in e["superseded"]
    # tree ratio from the registered couplings really is scheme-inequivalent
    gp2, g22 = 0.34971 ** 2, 0.65240 ** 2
    assert abs(gp2 / (gp2 + g22) - 0.2232) < 5e-4


def test_bounds_rulings():
    tp = get("tau_p_years")
    assert tp["value"] / 2.4e34 > 1.0     # above the Super-K bound
    mn = get("sum_mnu_eV")
    assert mn["value"] > 0.072            # honestly EXCEEDS the DESI bound
    assert mn["status"] == "TENSION"      # and says so


def test_alpha_leak_naming():
    e = get("alpha_leak")
    assert abs(e["value"] - 1 / math.sqrt(6)) < 1e-15
    assert "0.57" in e["superseded"]


def test_no_canonical_equals_its_superseded():
    for symbol, e in all_canonical().items():
        v = e.get("value")
        if v is None:
            continue
        for sv in e.get("superseded", {}):
            try:
                s = float(sv.split()[0])
            except ValueError:
                continue
            assert abs(s - v) > 1e-6, f"{symbol}: superseded {sv} equals canonical"
