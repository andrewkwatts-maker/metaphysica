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
    unmeasurable = {}
    checked = []
    for fid, fork in variants.FORKS.items():
        if fork.read_adopted is None:
            continue
        try:
            live = fork.read_adopted()
        except variants.SourceUnmeasurable as exc:
            # Recorded, not skipped silently. Until 2026-09-26 this fork's
            # reader returned the literal "b3_24" whenever it could not
            # measure, so this assertion compared the declaration against
            # itself and passed no matter what the sector computed -- a test
            # that could not fail, which this repo treats as a defect. It now
            # raises, and the unmeasurable set is asserted below rather than
            # being allowed to grow unnoticed.
            unmeasurable[fid] = str(exc)
            continue
        checked.append(fid)
        assert live == fork.default(), (
            f"{fid}: source says {live!r} but the declaration "
            f"marks {fork.default()!r} as adopted"
        )

    assert checked, "no fork source was actually read; the guard is inert"
    # Pinned in both directions: a NEW unmeasurable fork fails this, and so
    # does wiring one up, which is the edit that should come with the fix.
    assert set(unmeasurable) == {"dark_energy_betti"}, (
        "the set of forks whose source cannot be measured in a bare process "
        f"changed: {unmeasurable}"
    )
    assert "w0_derived" in unmeasurable["dark_energy_betti"], (
        "dark_energy_betti should be unmeasurable because the registry has "
        "no w0 yet -- if the reason changed, the reader changed"
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


def test_a_forks_status_matches_whether_its_criterion_is_derived():
    """This asserted face_genericity was OPEN with a "NOT derived" criterion.

    It was, and the test was right to pin it. The criterion has since been
    derived: block_labelling_analysis enumerates all 3^7 line-to-block
    labellings and finds the 28 line-containing 4-point sets admit none
    while each of the 7 arcs admits 18, so requiring genericity is a
    consequence rather than a choice. The fork is RULED accordingly.

    What must stay true is that the remaining INPUT is visible -- the
    global-labelling premise is still an assumption, and the option text
    has to say so, or a derived-looking status would overstate the case.
    """
    face = variants.FORKS["face_genericity"]
    assert face.status == "RULED"
    adopted = next(o for o in face.options if o.adopted)
    assert "NOW DERIVED" in adopted.consequence
    assert "stated, not derived" in adopted.consequence, (
        "the global-labelling premise has stopped being flagged as an "
        "assumption; a RULED status then claims more than was shown"
    )


def test_theory_uncertainty_policy_is_still_open():
    """A fork with no derivation behind it must not drift to RULED."""
    fork = variants.FORKS["theory_uncertainty_policy"]
    assert fork.status == "OPEN"
