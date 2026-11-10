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
    # Path-dependent names follow the seed in force (2026-11-11); the
    # seed_24 values (24, 4, 144) were the defect this test used to pin.
    from metaphysica.simulations.PM.geometry.b3_path import seed_values
    assert (B3, B2) == seed_values()
    assert CHI_SECTOR * 2 == CHI_EFF
    # shadow bookkeeping: 13 = 4 spacetime + 7 (V7) + 2 (T2)
    assert 4 + 7 + 2 == 13
    # Signature ruling (2026-08-31): bulk 26D (24,2), D_crit withdrawn;
    # spinor 4096 = Weyl of Cl(24,2), shadows (12,1)+(12,1) = 26.
    assert 2 ** 13 // 2 == 4096
    bulk = CANON["bulk"]
    assert bulk["value"] == 26
    assert 13 + 13 == bulk["value"]


def test_w0_ruling():
    e = get("w0")
    # the adopted dark_energy_betti option is the frozen n = 24: an input
    assert abs(e["value"] + 23 / 24) < 1e-15
    assert e["status"] == "INPUT"
    c = e["comparison"]
    assert sigma(e["value"], c["exp"], c["unc"]) < 0.05


def test_wa_ruling_minimal_form():
    e = get("wa")
    assert abs(e["value"] + 1 / math.sqrt(B3)) < 1e-15
    assert e["spare_vars"] == 0
    c = e["comparison"]
    s = sigma(e["value"], c["exp"], c["unc"])
    # an honest tension, recorded: 1.88 sigma at seed_24, 2.06 at seed_43
    assert c["sigma"] == s and "%.2f sigma" % s in e["note"]
    if B3 == 43:
        assert 2.0 < s < 2.1
    # the retired projection is the registered x dim(Psi) = 4 variant
    assert "%.4f" % (4 * e["value"]) in e["superseded"]


def test_h0_is_not_topology_first():
    from metaphysica.simulations.core.parameter_artifact import parameter_value
    e = get("H0_km_s_Mpc")
    assert e["status"] == "FITTED_COMPOSITE"
    # read from the artifact, never typed
    assert e["value"] == parameter_value("cosmology.H0_local")
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
    assert abs(e["value"] - 1 / math.sqrt(CHI_EFF / B3)) < 1e-15
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
