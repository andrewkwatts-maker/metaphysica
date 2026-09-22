"""Integer flux on the 43 basis: the measured null, and why it is structural.

MEASURED 2026-09-22: NO TIGHTENING, and the reason is not unfinished work.

At leading order K_IJ is diagonal with exactly two distinct entries -- L^7/8 on
the 7 flat classes and 32 pi^2 L^3 on the 36 twisted ones -- and its ONLY free
symbol is L. **t does not appear.** So a flux potential built on it can freeze
at most the overall torus scale and can freeze no t-modulus, because there is
no t in it to freeze.

Consequences, all measured below:

  * 43 integers collapse to 2. W sees n only through A = sum of flat quanta and
    B = sum of twisted quanta.
  * dW/dL = 0 has a positive root iff A and B have opposite signs, and it is a
    minimum there. 8 of 25 (A, B) pairs in the box |A|,|B| <= 2 qualify.
  * none of the 2 FLUX_DEPENDENT or 7 METRIC_DEPENDENT ledger rows is frozen,
    so the continuous count stays at **22**.

The test that matters most is `test_t_is_absent_from_the_leading_order_pairing`:
if t ever appears there, this whole null stops holding and the module's verdict
must be recomputed rather than adjusted.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest
import sympy as sp

from metaphysica.simulations.PM.geometry import flux_quantization as fq
from metaphysica.simulations.PM.geometry.metric_pairing import pairing_symbols


# ------------------------------------------------------- the structural fact

def test_t_is_absent_from_the_leading_order_pairing():
    """The load-bearing measurement. Everything else follows from it."""
    pairing = fq.moduli_in_the_pairing()
    assert pairing["contains_L"] is True
    assert pairing["contains_t"] is False, (
        "t has appeared in the leading-order K_IJ. The null result this module "
        "records no longer holds and the flux analysis must be REDONE, not "
        "adjusted: flux could now freeze a t-modulus."
    )
    assert pairing["free_symbols"] == ["L"]


def test_the_pairing_is_diagonal_with_two_distinct_entries():
    pairing = fq.moduli_in_the_pairing()
    assert pairing["is_diagonal"] is True
    assert pairing["n_distinct_diagonal_entries"] == 2, (
        "K_IJ no longer has exactly two distinct diagonal entries, so the "
        "collapse of 43 integers to 2 invariants is not valid: %s"
        % pairing["distinct_diagonal_entries"]
    )


def test_there_are_forty_three_periods_seven_flat_and_thirty_six_twisted():
    pis = fq.periods()
    assert len(pis) == fq.N_BASIS == 43
    kinds = fq._basis_kinds()
    assert kinds.count("flat") == 7
    assert kinds.count("twisted") == 36


# ----------------------------------------------------------- the collapse

def test_forty_three_integers_collapse_to_two_invariants():
    """Two different flux vectors with the same (A, B) must give the same W."""
    a = [1] * 7 + [1] + [0] * 35
    b = [0] * 6 + [7] + [0] + [1] + [0] * 34
    inv_a, inv_b = fq.flux_invariants(a), fq.flux_invariants(b)
    assert (inv_a["A_flat_sum"], inv_a["B_twisted_sum"]) == \
           (inv_b["A_flat_sum"], inv_b["B_twisted_sum"])
    assert sp.simplify(fq.superpotential(a) - fq.superpotential(b)) == 0, (
        "two flux vectors with identical invariants give different W, so the "
        "collapse to (A, B) is wrong"
    )


def test_different_invariants_give_different_superpotentials():
    """The converse, or the collapse would be vacuous."""
    a = [1] * 7 + [0] * 36
    b = [2] * 7 + [0] * 36
    assert sp.simplify(fq.superpotential(a) - fq.superpotential(b)) != 0


def test_non_integer_flux_is_refused():
    """Flux quanta are integers; a float is a category error, not a value."""
    with pytest.raises(ValueError):
        fq.flux_invariants([0.5] + [0] * 42)


def test_a_wrong_length_flux_vector_is_refused():
    with pytest.raises(ValueError):
        fq.flux_invariants([0] * 42)


# -------------------------------------------------------- the stationarity

def test_opposite_signs_are_required_for_a_stationary_point():
    """L_*^4 = -768 pi^2 B / (7 A): positive only when A and B disagree."""
    same_sign = fq.stationary_scale([1] * 7 + [1] * 36)
    opposite = fq.stationary_scale([1] * 7 + [-1] * 36)
    assert same_sign["stationarity_of_W"] is False, (
        "a stationary point appeared with A and B of the same sign, which the "
        "closed form forbids"
    )
    assert opposite["stationarity_of_W"] is True
    assert opposite["nature"] == "minimum"


def test_the_stationary_scale_satisfies_the_closed_form():
    """Check the solver against the algebra, not against itself."""
    L, _t = pairing_symbols()
    n = [1] * 7 + [-1] * 36
    result = fq.stationary_scale(n)
    a, b = result["A_flat_sum"], result["B_twisted_sum"]
    predicted = (-768 * sp.pi ** 2 * b / (7 * a)) ** sp.Rational(1, 4)
    got = sp.sympify(result["L_star"])
    assert sp.simplify(got - predicted) == 0, (
        "solver gave %s, closed form gives %s" % (got, predicted))


def test_the_sweep_finds_stationary_points_only_at_opposite_signs():
    sweep = fq.scan_flux_vectors(2)
    assert sweep["n_invariant_pairs"] == 25
    assert sweep["n_with_stationary_point"] == 8
    assert sweep["all_have_opposite_signs"] is True


def test_stationarity_of_W_is_never_called_a_vacuum():
    """The object the framework lacks must not be quietly supplied."""
    result = fq.stationary_scale([1] * 7 + [-1] * 36)
    assert "stationarity_of_W" in result
    assert "vacuum" not in [k.lower() for k in result]
    assert "not a vacuum" in result["not_a_vacuum"].lower()
    assert "Kahler" in result["not_a_vacuum"]


# ------------------------------------------------------------- the ledger

def test_the_ledger_targets_are_the_two_and_the_seven():
    """Read live, so a reclassification reaches this rather than a stale list."""
    targets = fq.ledger_targets()
    assert targets["n_flux_dependent"] == 2, (
        "the FLUX_DEPENDENT layer is no longer 2 rows: %s"
        % targets["flux_dependent_rows"])
    assert targets["n_metric_dependent"] == 7, (
        "the METRIC_DEPENDENT layer is no longer 7 rows: %s"
        % targets["metric_dependent_rows"])


def test_no_ledger_row_is_frozen_and_the_null_is_recorded():
    targets = fq.ledger_targets()
    assert targets["frozen_by_leading_order_flux"] == []
    assert targets["why_none"], "a null must carry its reason"
    assert targets["what_would_change_it"], (
        "a null must say what would overturn it, or it is unfalsifiable"
    )
    assert "t^2" in targets["what_would_change_it"]


def test_the_verdict_is_no_tightening_and_the_count_stays_at_22():
    report = fq.flux_report()
    assert report["tightening"] == 0
    assert "NO TIGHTENING" in report["verdict"]
    assert "22" in report["verdict"]
    assert report["moduli_frozen"] == ["L"]
    assert report["moduli_not_frozen"] == ["t"]


def test_L_is_not_itself_a_ledger_row():
    """Freezing L is real and is NOT a reduction of the continuous count."""
    from metaphysica.simulations.core.closure_ledger import closure_ledger

    names = {row["name"] for row in closure_ledger()}
    assert not any(name == "L" or name.endswith(".L") for name in names), (
        "L has become a ledger row, so freezing it WOULD be a tightening and "
        "the verdict must be recomputed"
    )


# ------------------------------------------------------------- order tags

def test_every_output_carries_its_order_tag():
    for report in (fq.moduli_in_the_pairing(),
                   fq.stationary_scale([1] * 7 + [-1] * 36),
                   fq.scan_flux_vectors(1),
                   fq.ledger_targets(),
                   fq.flux_report()):
        assert report["order"] == "leading-order-in-t", (
            "exact and asymptotic must never be conflated, at every consumer"
        )
