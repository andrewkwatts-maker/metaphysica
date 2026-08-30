"""The executable-fork registry.

WHY THIS EXISTS
---------------
Open decisions were documented (CANON's "RESOLUTION OPTIONS (author's call)")
but not runnable, so seeing what an option changes meant editing code and
comparing by hand. This registry makes a fork selectable.

The tests that matter here are the ones guarding against it becoming a
parameter fitter, and against a default drifting away from the value actually
adopted at its source.
"""
from __future__ import annotations

import pytest

from metaphysica.simulations.core import variants


def test_every_fork_declares_exactly_one_adopted_option():
    for fid, fork in variants.FORKS.items():
        adopted = [o for o in fork.options if o.adopted]
        assert len(adopted) == 1, f"{fid}: {len(adopted)} adopted options"


def test_every_fork_offers_a_real_choice():
    """A fork with one option is a constant wearing a switch's clothes."""
    for fid, fork in variants.FORKS.items():
        assert len(fork.options) >= 2, f"{fid} has no alternative"
        assert len(set(fork.option_ids())) == len(fork.options), f"{fid}: dup ids"


def test_defaults_match_the_value_adopted_at_the_source():
    """The registry is a VIEW, not a store.

    If a module switch is flipped without updating the declaration, the two
    disagree and this fails -- the same drift guard the SSOT audits apply to
    constants. Without it the registry becomes a fifth place a value lives.
    """
    for fid, fork in variants.FORKS.items():
        if fork.read_adopted is None:
            continue
        assert fork.read_adopted() == fork.default(), (
            f"{fid}: source says {fork.read_adopted()!r} but the declaration "
            f"marks {fork.default()!r} as adopted"
        )


def test_describe_reports_no_drift():
    for fid, entry in variants.describe()["forks"].items():
        assert entry["drift"] is None, f"{fid}: {entry['drift']}"


# ── selection precedence ────────────────────────────────────────────────────


def test_default_is_used_when_nothing_overrides():
    assert variants.resolve("render_policy") == "strict"


def test_environment_overrides_the_default(monkeypatch):
    monkeypatch.setenv("METAPHYSICA_VARIANT_RENDER_POLICY", "permissive")
    assert variants.resolve("render_policy") == "permissive"


def test_explicit_argument_beats_the_environment(monkeypatch):
    monkeypatch.setenv("METAPHYSICA_VARIANT_RENDER_POLICY", "permissive")
    assert variants.resolve("render_policy", "strict") == "strict"


def test_an_unknown_option_is_refused_not_silently_defaulted():
    """Silently falling back would run one thing while reporting another."""
    with pytest.raises(ValueError) as exc:
        variants.resolve("render_policy", "whatever")
    assert "permissive" in str(exc.value), "the error should list the options"


def test_an_unknown_fork_is_refused():
    with pytest.raises(KeyError):
        variants.resolve("no_such_fork")


def test_a_bad_environment_value_fails_loudly(monkeypatch):
    monkeypatch.setenv("METAPHYSICA_VARIANT_RENDER_POLICY", "nonsense")
    with pytest.raises(ValueError):
        variants.resolve("render_policy")


# ── the tuning hazard ───────────────────────────────────────────────────────


def test_no_fork_ranks_its_options_by_agreement_with_data():
    """The guardrail that keeps this from becoming a parameter fitter.

    Options carry consequences, not scores. If a 'best', 'sigma' or 'rank'
    field ever appears, the registry has started choosing physics by fit --
    which is the anchor-shopping this repo retired an advertised agreement
    over.
    """
    banned = ("best", "score", "rank", "sigma", "preferred", "recommended")
    for fid, fork in variants.FORKS.items():
        for option in fork.options:
            for field_name in ("id", "summary"):
                value = getattr(option, field_name).lower()
                for word in banned:
                    assert word not in value, (
                        f"{fid}.{option.id}: {field_name} contains {word!r} -- "
                        f"options must be described, not scored"
                    )


def test_every_option_states_a_consequence():
    """An option with no stated consequence cannot inform a ruling."""
    for fid, fork in variants.FORKS.items():
        for option in fork.options:
            assert len(option.consequence) > 40, (
                f"{fid}.{option.id} has no substantive consequence"
            )


def test_open_forks_are_marked_open():
    """A fork whose criterion is not derived must not read as settled."""
    face = variants.FORKS["face_genericity"]
    assert face.status == "OPEN"
    adopted = next(o for o in face.options if o.adopted)
    assert "NOT derived" in adopted.consequence
