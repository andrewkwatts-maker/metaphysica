"""Lane 2B: scoring one configuration (validity gate, gaps, layouts).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from metaphysica.testground.assessment.config import AssessmentConfig
from metaphysica.testground.assessment.criteria import (DATA_DEFERRED,
                                                        discrete_inputs,
                                                        score_configuration,
                                                        score_criterion)
from metaphysica.testground.configurations.model import INVALID, Configuration
from metaphysica.testground.signals.model import Measurement, Signal
from metaphysica.testground.switches.model import Fork, VariantOption

CFG = Configuration.of("toy", {"seed": "s43", "origin": "o1"})


def _m(signal, count=0, failures=None, status="MEASURED", **detail):
    if failures is not None:
        detail["failures"] = failures
    reasons = ("why",) if status != "MEASURED" else ()
    return Measurement(signal, status=status,
                       count=count if status == "MEASURED" else None,
                       detail=detail, reasons=reasons)


def _clean(**override):
    ms = {"validity": [_m("kinds")], "closure": [_m("free", 2)],
          "consistency": [_m("omega"), _m("beacons", 1)],
          "elegance": [_m("leaves", 3)]}
    ms.update(override)
    return ms


def test_a_fully_measured_clean_configuration_is_adoptable():
    v = score_configuration(CFG, _clean())
    assert v.verdict == "ADOPTABLE" and v.decided()
    assert v.digest == CFG.digest
    assert v.keys()[:4] == ((0,), (2,), (1,), (3,))
    assert v.score("consistency").components == {"omega": 0, "beacons": 1}
    assert v.score("data").status == "UNMEASURED"
    assert v.score("data").unmeasured == (DATA_DEFERRED,)


def test_a_validity_failure_rejects_with_reasons():
    bad = Measurement("kinds", count=1, detail={"failures": ["CONTRADICTION"]},
                      reasons=("w0 stated twice",))
    v = score_configuration(CFG, _clean(validity=[bad]))
    assert v.verdict == "REJECTED"
    assert "kinds:CONTRADICTION" in v.reasons
    assert "kinds: w0 stated twice" in v.reasons
    assert v.score("validity").key == (1,)


def test_an_unitemized_validity_count_is_still_a_failure():
    v = score_configuration(CFG, _clean(validity=[_m("kinds", 2)]))
    assert v.verdict == "REJECTED" and v.reasons == ("kinds",)


def test_a_count_beyond_its_listed_items_is_named_with_its_count():
    m = _m("kinds", 2, ["re_t"])
    v = score_configuration(CFG, _clean(validity=[m]),
                            standing=frozenset({"kinds:re_t"}))
    assert v.verdict == "REJECTED" and "kinds (count 1)" in v.reasons


def test_standing_failures_are_excluded_from_the_gate():
    m = _m("kinds", 1, ["re_t"])
    v = score_configuration(CFG, _clean(validity=[m]),
                            standing=frozenset({"kinds:re_t"}))
    assert v.verdict == "ADOPTABLE" and v.score("validity").key == (0,)


def test_target_facts_gate_validity():
    facts = AssessmentConfig.from_mapping({"target_facts": [
        {"id": "n_gen", "signal": "gens", "expected": 3, "source": "(b)"}]})
    ok = _clean(validity=[_m("kinds"),
                          Measurement("gens", detail={"value": 3})])
    assert score_configuration(CFG, ok, facts).verdict == "ADOPTABLE"
    wrong = _clean(validity=[_m("kinds"),
                             Measurement("gens", detail={"value": 1})])
    v = score_configuration(CFG, wrong, facts)
    assert v.verdict == "REJECTED"
    assert v.reasons == ("target:n_gen: expected 3, got 1 ((b))",)


def test_a_target_fact_without_a_reading_leaves_validity_open():
    facts = AssessmentConfig.from_mapping({"target_facts": [
        {"id": "n_gen", "signal": "gens", "expected": 3}]})
    missing = score_configuration(CFG, _clean(), facts)
    assert missing.verdict == "UNDECIDED"
    no_field = _clean(validity=[_m("kinds"), Measurement("gens")])
    assert "reports no 'value'" in score_configuration(
        CFG, no_field, facts).reasons[0]
    gap = _clean(validity=[_m("kinds"), _m("gens", status="UNMEASURED")])
    assert score_configuration(CFG, gap, facts).verdict == "UNDECIDED"


def test_a_target_reading_in_another_criterion_is_not_a_count():
    facts = AssessmentConfig.from_mapping({"target_facts": [
        {"id": "n_gen", "signal": "gens", "expected": 3}]})
    ms = _clean(closure=[_m("free", 2), Measurement("gens",
                                                    detail={"value": 3})])
    v = score_configuration(CFG, ms, facts)
    assert v.verdict == "ADOPTABLE" and v.score("closure").key == (2,)


def test_a_constraint_violating_configuration_is_rejected():
    probe = Configuration.of("toy", {"seed": "s24"}, lifecycle=INVALID,
                             reasons=("origin requires seed_24",))
    v = score_configuration(probe, _clean())
    assert v.verdict == "REJECTED"
    assert v.reasons == ("constraint: origin requires seed_24",)
    bare = Configuration.of("toy", {"seed": "s24"}, lifecycle=INVALID)
    assert score_configuration(bare, {}).reasons == (
        "constraint: violates a declared constraint",)


def test_an_unmeasured_criterion_never_falls_through():
    ms = _clean(closure=[_m("free", status="UNMEASURED")])
    v = score_configuration(CFG, ms)
    assert v.verdict == "UNDECIDED" and not v.decided()
    assert v.score("closure").key is None
    assert v.reasons[0].startswith("closure: free UNMEASURED")


def test_an_unevaluable_reading_is_reported_as_such():
    ms = _clean(elegance=[_m("leaves", status="UNEVALUABLE")])
    v = score_configuration(CFG, ms)
    assert v.verdict == "UNDECIDED"
    assert v.score("elegance").status == "UNEVALUABLE"


def test_a_not_runnable_configuration_passes_through_unscored():
    cfg = Configuration.of("toy", {"seed": "fano"}, not_runnable=True,
                           reasons=("fano_tcs not implemented",))
    v = score_configuration(cfg, _clean())
    assert v.verdict == "NOT_RUNNABLE"
    assert v.reasons == ("fano_tcs not implemented",)
    assert all(s.key is None for s in v.scores)
    bare = Configuration.of("toy", {"seed": "fano"}, not_runnable=True)
    assert score_configuration(bare, {}).reasons == ("not runnable",)


def test_a_pre_registered_layout_builds_a_multi_position_key():
    assess = AssessmentConfig.from_mapping({"key_layout": {
        "closure": [["free", "discrete_inputs"], ["calibrated"]],
        "elegance": []}})
    ms = _clean(closure=[_m("free", 2), _m("discrete_inputs", 1),
                         _m("calibrated", 4)], elegance=[])
    v = score_configuration(CFG, ms, assess)
    assert v.verdict == "ADOPTABLE"
    assert v.score("closure").key == (3, 4)
    assert v.score("elegance").key == ()


def test_a_layout_mismatch_leaves_the_criterion_unmeasured():
    assess = AssessmentConfig.from_mapping({"key_layout": {
        "closure": [["free"], ["calibrated"]]}})
    extra = _clean(closure=[_m("free"), _m("calibrated"), _m("surprise")])
    s = score_configuration(CFG, extra, assess).score("closure")
    assert s.key is None and "surprise is not in" in s.unmeasured[0]
    short = _clean(closure=[_m("free")])
    s = score_configuration(CFG, short, assess).score("closure")
    assert "calibrated pre-registered" in s.unmeasured[0]


def test_malformed_measurements_leave_the_criterion_unmeasured():
    s = score_criterion("closure", [_m("free", 1), _m("free", 2)])
    assert s.key is None and "measured twice" in s.unmeasured[0]
    s = score_criterion("closure", [Measurement("free")])
    assert "without a count" in s.unmeasured[0]
    s = score_criterion("closure", [])
    assert "no signal measured" in s.unmeasured[0]
    v = score_configuration(CFG, _clean(validity=[Measurement("kinds")]))
    assert v.verdict == "UNDECIDED"
    assert score_configuration(CFG, _clean(validity=[])).verdict == "UNDECIDED"


def test_data_signals_are_scored_when_present_and_never_gate():
    ms = _clean(data=[_m("fails", 2)])
    v = score_configuration(CFG, ms)
    assert v.score("data").key == (2,) and v.verdict == "ADOPTABLE"
    ms = _clean(data=[_m("fails", status="UNMEASURED")])
    assert score_configuration(CFG, ms).verdict == "ADOPTABLE"


def test_measurements_can_come_as_signals_and_readings():
    sigs = [Signal("kinds", "validity", "live", "screen", lambda c: None),
            Signal("free", "closure", "live", "screen", lambda c: None),
            Signal("omega", "consistency", "live", "screen", lambda c: None),
            Signal("leaves", "elegance", "live", "screen", lambda c: None)]
    flat = [_m("kinds"), _m("free", 1), _m("omega"), _m("leaves")]
    v = score_configuration(CFG, flat, signals=sigs, stage_reached="full")
    assert v.verdict == "ADOPTABLE" and v.stage_reached == "full"


def test_discrete_inputs_counts_the_options_that_declare_one():
    forks = {
        "seed": Fork("seed", "q", "src", [
            VariantOption("s43", "s", "c", adopted=True),
            VariantOption("s24", "s", "c", adds_discrete_input=True)], "OPEN"),
        "origin": Fork("origin", "q", "src", [
            VariantOption("o1", "s", "c", adopted=True,
                          adds_discrete_input=True)], "OPEN"),
    }
    m = discrete_inputs(forks, CFG)
    assert m.signal == "discrete_inputs" and m.count == 1
    assert m.detail["inputs"] == ["origin=o1"]
    m = discrete_inputs(forks, CFG.with_overrides({"seed": "s24"}))
    assert m.count == 2
