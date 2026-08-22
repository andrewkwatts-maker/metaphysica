"""Tests for the exterior-degree gate.

The gate exists because a proposed cross-shadow coupling reached the design
stage with degrees 3+2+2 = 7 integrated over a 13-manifold. These tests pin
both directions: that well-formed terms pass, and -- the part that matters --
that malformed ones are actually rejected.
"""
from __future__ import annotations

import json

import pytest

from metaphysica.simulations.PM.validation.exterior_degree_gate import (
    enumerate_completions,
    run_all_checks,
    validate_action_term,
    write_report,
)


def test_wellformed_terms_pass():
    """M-theory's 11D Chern-Simons term: 3 + 4 + 4 = 11."""
    assert validate_action_term((3, 4, 4), 11) is True


def test_the_originally_proposed_term_is_rejected():
    """int_13 C_3 ^ F_A ^ F_B is a 7-form on a 13-manifold -- short by six.

    This is the whole reason the gate exists. If it ever stops raising, the
    gate has been broken.
    """
    with pytest.raises(ValueError, match="short by 6"):
        validate_action_term((3, 2, 2), 13, name="flux")


def test_rejection_message_names_the_shortfall():
    with pytest.raises(ValueError) as exc:
        validate_action_term((3, 2, 2), 13)
    msg = str(exc.value)
    assert "3 + 2 + 2 = 7" in msg
    assert "13-form" in msg


def test_over_degree_is_rejected_too():
    """The check is an equality, not a lower bound."""
    with pytest.raises(ValueError, match="over by 2"):
        validate_action_term((3, 4, 4, 4), 13)


def test_negative_degree_is_rejected():
    with pytest.raises(ValueError, match="negative form degree"):
        validate_action_term((3, -1), 2)


def test_path_a_and_path_b_are_both_wellformed():
    """The two author-supplied completions must actually integrate."""
    assert validate_action_term((3, 4, 4, 2), 13) is True   # Path A, 13D
    assert validate_action_term((3, 2, 2), 7) is True       # Path B, Sigma_7


def test_enumerate_completions_finds_path_a():
    """Given C_3 ^ F_A ^ F_B on 13D, the deficit-6 completions must be listed."""
    out = enumerate_completions([3, 2, 2], 13)
    assert out, "no completions found for a deficit of 6"
    for combo in out:
        assert sum(combo) == 13
    assert [3, 2, 2, 2, 4] in [sorted(c[:3]) + sorted(c[3:]) for c in out] or any(
        sorted(c) == sorted([3, 2, 2, 2, 4]) for c in out
    )


def test_enumerate_completions_is_bounded():
    """Every returned multiset is exact; the search cannot run away."""
    out = enumerate_completions([1], 13, max_extra_factors=3)
    assert len(out) <= 200
    assert all(sum(c) == 13 for c in out)


def test_enumerate_completions_on_exact_term_is_identity():
    assert enumerate_completions([3, 4, 4], 11) == [[3, 4, 4]]


def test_enumerate_completions_on_overshoot_is_empty():
    assert enumerate_completions([5, 5, 5], 11) == []


def test_shipped_checks_include_a_deliberate_failure():
    """A gate whose every shipped record passes proves nothing about rejection."""
    checks = run_all_checks()
    statuses = {c.term_id: c.status for c in checks}
    assert statuses["flux-13d-original"] == "FAIL"
    assert statuses["flux-13d-path-a"] == "PASS"
    assert statuses["flux-sigma7-path-b"] == "PASS"
    assert statuses["m-theory-cs-reference"] == "PASS"


def test_domain_dims_come_from_the_registry_not_literals():
    """Terms must follow the SSOT, so an open signature ruling can't strand them."""
    from metaphysica.simulations.core.physics_config import PhysicsConfig

    cfg = PhysicsConfig.from_registry()
    by_id = {c.term_id: c for c in run_all_checks()}
    assert by_id["flux-13d-path-a"].domain_dim == cfg.d_shadow_total
    assert by_id["flux-sigma7-path-b"].domain_dim == cfg.d_g2_total


def test_write_report_produces_valid_json(tmp_path):
    out = write_report(out_path=tmp_path / "exterior_degree_gate.json")
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["n_pass"] + payload["n_fail"] == payload["count"]
    assert payload["n_fail"] == 1, "the deliberate FAIL record must be present"
    assert len(payload["checks"]) == payload["count"]
    assert "necessary but not sufficient" in payload["note"]
