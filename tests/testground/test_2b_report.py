"""Lane 2B: the path_assessment report -- schema, K5, voiding, disclosure.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json

import pytest

from metaphysica.testground.assessment import report as report_mod
from metaphysica.testground.assessment.config import AssessmentConfig
from metaphysica.testground.assessment.criteria import score_configuration
from metaphysica.testground.assessment.report import (build_report,
                                                      dumps_report,
                                                      k5_control,
                                                      normalize_mode,
                                                      validate_report,
                                                      voided_by)
from metaphysica.testground.assessment.standing import standing_failures
from metaphysica.testground.configurations.model import (ACTIVE,
                                                         Configuration)
from metaphysica.testground.signals.model import Measurement
from metaphysica.testground.theory import ScoredRow

_YAML = """\
theory: toy
target_facts:
  - {id: n_gen, signal: gens, expected: 3}
policy_forks: [render]
"""


def _m(signal, count=0, failures=None, **detail):
    if failures is not None:
        detail["failures"] = failures
    return Measurement(signal, count=count, detail=detail)


def _measure(free, gens=3, omega=0):
    return {"validity": [_m("kinds", 1, ["re_t"]),
                         Measurement("gens", detail={"value": gens})],
            "closure": [_m("free", free)],
            "consistency": [_m("omega", omega)],
            "elegance": [_m("leaves", 1)]}


@pytest.fixture
def assess(tmp_path):
    path = tmp_path / "assessment.yaml"
    path.write_text(_YAML, encoding="utf-8")
    return AssessmentConfig.load(path)


@pytest.fixture
def run(assess):
    """Three configurations: the active, one losing on closure, one with
    the wrong number of generations. Every one fails kinds:re_t."""
    active = Configuration.of("toy", {"seed": "s43", "render": "r"},
                              lifecycle=ACTIVE, name="active")
    extra = Configuration.of("toy", {"seed": "s24", "render": "r"})
    one_gen = Configuration.of("toy", {"seed": "s1", "render": "r"})
    cfgs = [active, extra, one_gen]
    ms = {active.digest: _measure(0), extra.digest: _measure(1),
          one_gen.digest: _measure(0, gens=1)}
    standing = standing_failures(ms)
    vectors = [score_configuration(c, ms[c.digest], assess, standing)
               for c in cfgs]
    return cfgs, vectors, standing


def test_an_end_to_end_report_validates_and_confirms_the_active(assess, run):
    cfgs, vectors, standing = run
    rep = build_report(theory="toy", mode="ASSESS", configurations=cfgs,
                       vectors=vectors, active_digest=cfgs[0].digest,
                       assess_cfg=assess, standing=standing,
                       recorded_sha256=assess.sha256,
                       enumeration={"valid": 3}, generated_at="2026-10-02")
    assert validate_report(rep) == []
    assert rep["verdict"] == "ACTIVE_CONFIRMED"
    assert rep["standing_failures"] == ["kinds:re_t"]
    assert rep["pre_registration"]["sha256"] == assess.sha256
    assert rep["controls"]["K5"]["fired"] is False
    assert rep["mode"] == "assess" and rep["generated_at"] == "2026-10-02"
    entries = {c["digest"]: c for c in rep["configurations"]}
    assert entries[cfgs[0].digest]["group"] == 0
    assert entries[cfgs[1].digest]["group"] == 1
    assert entries[cfgs[2].digest]["verdict"] == "REJECTED"
    assert entries[cfgs[2].digest]["group"] is None
    assert rep["ranking"]["unranked"] == {"REJECTED": [cfgs[2].digest]}
    assert rep["active"]["in_top_group"]
    assert rep["enumeration"] == {"valid": 3, "assessed": 3}
    assert json.loads(dumps_report(rep)) == json.loads(dumps_report(rep))


def test_a_changed_pre_registration_voids_the_run(assess, run):
    """K5: a run against any other sha256 is void."""
    cfgs, vectors, standing = run
    rep = build_report(theory="toy", mode="assess", configurations=cfgs,
                       vectors=vectors, active_digest=cfgs[0].digest,
                       assess_cfg=assess, standing=standing,
                       recorded_sha256="0" * 64)
    assert rep["controls"]["K5"]["fired"] is True
    assert rep["verdict"] == "UNDECIDED"
    assert rep["recommendation"]["void"] is True
    assert validate_report(rep) == []


def test_a_fired_null_control_voids_the_run(run):
    cfgs, vectors, _ = run
    rep = build_report(theory="toy", mode="single", configurations=cfgs,
                       vectors=vectors, active_digest=cfgs[0].digest,
                       controls={"K3": {"fired": True}, "K2": {"fired": True}})
    assert rep["verdict"] == "UNDECIDED"
    assert rep["recommendation"]["reasons"] == [
        "run void: kill condition K3 fired"]
    assert voided_by({"K1": {"fired": False}, "K5": "x"}) == []


def test_a_change_names_the_comparison_with_the_top(assess):
    active = Configuration.of("toy", {"seed": "a", "render": "r"})
    top = Configuration.of("toy", {"seed": "b", "render": "r"})
    vectors = [score_configuration(active, _measure(2), assess),
               score_configuration(top, _measure(0), assess)]
    rows = {active.digest: [ScoredRow("x", "PASS")],
            top.digest: [ScoredRow("x", "PASS")]}
    rep = build_report(theory="toy", mode="reassess",
                       configurations=[active, top], vectors=vectors,
                       active_digest=active.digest, assess_cfg=assess,
                       rows=rows)
    assert rep["verdict"] == "RECOMMEND_CHANGE"
    assert rep["recommendation"]["target"] == top.digest
    assert rep["active"]["comparison_with_top"]["deciding_criterion"] == (
        "closure")
    assert rep["controls"]["K5"]["checked"] is False
    assert validate_report(rep) == []


def test_tied_groups_disclose_their_tiebreak(assess):
    a = Configuration.of("toy", {"seed": "a", "render": "r"})
    b = Configuration.of("toy", {"seed": "b", "render": "r"})
    vectors = [score_configuration(c, _measure(0), assess) for c in (a, b)]
    rep = build_report(theory="toy", mode="assess", configurations=[a, b],
                       vectors=vectors, active_digest=a.digest,
                       assess_cfg=assess)
    tb = rep["ranking"]["tiebreaks"][0]
    assert tb["group"] == 0 and tb["trials_factor_k"] == 2
    assert rep["verdict"] == "ACTIVE_CONFIRMED"


def test_policy_forks_must_be_held_at_the_active_option(assess):
    a = Configuration.of("toy", {"seed": "a", "render": "r"})
    b = Configuration.of("toy", {"seed": "a", "render": "other"})
    vectors = [score_configuration(c, _measure(0), assess) for c in (a, b)]
    with pytest.raises(ValueError, match="amendment \\(d\\)"):
        build_report(theory="toy", mode="assess", configurations=[a, b],
                     vectors=vectors, active_digest=a.digest,
                     assess_cfg=assess)


def test_configurations_and_vectors_must_match(run):
    cfgs, vectors, _ = run
    with pytest.raises(ValueError, match="do not match"):
        build_report(theory="toy", mode="assess", configurations=cfgs[:2],
                     vectors=vectors, active_digest=cfgs[0].digest)


def test_modes_are_normalized_and_unknown_ones_refused():
    assert normalize_mode("ARCHAEOLOGY") == "archaeology"
    with pytest.raises(ValueError, match="probe"):
        normalize_mode("probe-constraint")


def test_k5_without_an_annex_sha_is_recorded_unchecked():
    k5 = k5_control(AssessmentConfig.empty(), None)
    assert k5 == {"checked": False, "fired": False, "sha256": "",
                  "detail": "no annex sha256 supplied"}


def test_the_validator_reports_errors_and_the_fallback_agrees(run):
    cfgs, vectors, _ = run
    rep = build_report(theory="toy", mode="assess", configurations=cfgs,
                       vectors=vectors, active_digest=cfgs[0].digest)
    schema = json.loads(report_mod.SCHEMA_PATH.read_text(encoding="utf-8"))
    assert report_mod._structural_errors(rep, schema) == []
    broken = dict(rep, verdict="BEST", criteria_order=["data"],
                  schema="x", configurations=[{"verdict": "GOOD"}])
    del broken["theory"]
    assert validate_report(broken)
    errors = report_mod._structural_errors(broken, schema)
    assert "missing 'theory'" in errors and "verdict" in errors
    assert "criteria_order" in errors and "schema id" in errors
    assert "configuration verdict 'GOOD'" in errors
