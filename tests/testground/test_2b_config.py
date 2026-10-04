"""Lane 2B: the pre-registered assessment configuration (D-019 annex).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import hashlib

import pytest

from metaphysica.testground.assessment.config import (AssessmentConfig,
                                                      TargetFact,
                                                      policy_drift,
                                                      sha256_of_file)

_YAML = """\
theory: toy
decision: D-019
target_facts:
  - id: n_gen
    signal: generations
    expected: 3
    source: D-019 (b)
policy_forks: [render_policy]
constraints:
  - "origin=input_24 requires seed in {seed_24}"
budget: {jobs: 4, timeout_s: 60}
key_layout:
  closure: [[free_set_size, discrete_inputs], [n_calibrated]]
  elegance: [unrooted, literal_leaves]
  data: []
"""


def _write(tmp_path, text=_YAML):
    path = tmp_path / "assessment.yaml"
    path.write_bytes(text.encode("utf-8"))
    return path


def test_load_reads_every_field_and_hashes_the_exact_bytes(tmp_path):
    path = _write(tmp_path)
    cfg = AssessmentConfig.load(path)
    assert cfg.sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
    assert cfg.sha256 == sha256_of_file(path)
    assert cfg.theory == "toy" and cfg.decision == "D-019"
    assert cfg.target_facts == (TargetFact("n_gen", "generations", 3,
                                           source="D-019 (b)"),)
    assert cfg.policy_forks == ("render_policy",)
    assert cfg.budget == {"jobs": 4, "timeout_s": 60}
    assert cfg.layout("closure") == (("free_set_size", "discrete_inputs"),
                                     ("n_calibrated",))
    assert cfg.layout("elegance") == (("unrooted",), ("literal_leaves",))
    assert cfg.layout("data") == ()
    assert cfg.layout("consistency") is None
    assert cfg.target_signals() == frozenset({"generations"})


def test_one_changed_byte_changes_the_sha256(tmp_path):
    a = AssessmentConfig.load(_write(tmp_path))
    b = AssessmentConfig.load(_write(tmp_path, _YAML + "\n"))
    assert a.sha256 != b.sha256
    assert a.matches(a.sha256) and not a.matches(b.sha256)
    assert not a.matches(None) and not a.matches("")


def test_an_empty_file_is_an_empty_pre_registration(tmp_path):
    cfg = AssessmentConfig.load(_write(tmp_path, ""))
    assert cfg.target_facts == () and cfg.key_layout == {}
    assert AssessmentConfig.empty().sha256 == ""


@pytest.mark.parametrize("data, message", [
    ({"target_fact": []}, "unknown"),
    ({"target_facts": [{"id": "x"}]}, "lacks"),
    ({"key_layout": {"beauty": [["a"]]}}, "unknown criterion"),
    ({"key_layout": {"validity": [["a"]]}}, "gate"),
    ({"key_layout": {"closure": "a"}}, "list of lists"),
    ({"key_layout": {"closure": [[]]}}, "non-empty"),
    ({"key_layout": ["closure"]}, "mapping"),
    ({"policy_forks": "render_policy"}, "list"),
    ({"budget": [1]}, "mapping"),
])
def test_a_malformed_pre_registration_is_refused(data, message):
    with pytest.raises(ValueError, match=message):
        AssessmentConfig.from_mapping(data)


def test_a_non_mapping_is_refused():
    with pytest.raises(ValueError):
        AssessmentConfig.from_mapping(["theory"])


def test_the_summary_records_the_sha256_and_rules(tmp_path):
    cfg = AssessmentConfig.load(_write(tmp_path))
    s = cfg.summary()
    assert s["sha256"] == cfg.sha256
    assert s["target_facts"][0]["expected"] == 3
    assert s["key_layout"]["closure"] == [["free_set_size", "discrete_inputs"],
                                          ["n_calibrated"]]
    assert s["assessment_config"].endswith("assessment.yaml")


def test_policy_drift_names_forks_not_held_at_the_active_option():
    active = {"render_policy": "a", "physics": "x"}
    assert policy_drift({"render_policy": "b", "physics": "y"}, active,
                        ["render_policy"]) == ["render_policy"]
    assert policy_drift({"render_policy": "a"}, active,
                        ["render_policy", "absent"]) == []
