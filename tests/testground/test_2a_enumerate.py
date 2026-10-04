"""Lane 2A: lazy, constraint-pruned enumeration and counting without building.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
import random
import time

import pytest

from metaphysica.testground.configurations import enumerate as en
from metaphysica.testground.configurations.enumerate import (
    InvalidSelectionError,
    count_configurations,
    enumerate_configurations,
    ordered_options,
    plan_enumeration,
)
from metaphysica.testground.configurations.model import (
    ACTIVE,
    INVALID,
    RETIRED_CERTAIN,
    RETIRED_REASSESSABLE,
)
from metaphysica.testground.configurations.modes import MODES
from metaphysica.testground.constraints import Excludes, Requires, is_valid
from metaphysica.testground.switches.model import (
    CERTAIN,
    DISABLED,
    Fork,
    VariantOption,
)
from metaphysica.testground.switches.resolve import CONFIG_ENV
from tests.testground.test_2a_support import (
    ACTIVE_SELECTION,
    ASSESS_ORDER,
    ENV_PREFIX,
    HAND_COUNTS,
    MemoryStore,
    make_theory,
    random_theory,
    tiny_forks,
)

_SWEPT = ("seed", "origin", "shape")


def _triples(cfgs):
    return [tuple(c.mapping[f] for f in _SWEPT) for c in cfgs]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for fork in ACTIVE_SELECTION:
        monkeypatch.delenv(ENV_PREFIX + fork.upper(), raising=False)
    monkeypatch.delenv(CONFIG_ENV, raising=False)


# ---------------------------------------------------------------- order


def test_the_assess_order_is_active_then_priority_then_declaration():
    cfgs = list(enumerate_configurations(make_theory(), "assess"))
    assert _triples(cfgs) == ASSESS_ORDER
    assert cfgs[0].lifecycle == ACTIVE and cfgs[0].name == "adopted"
    assert all(c.lifecycle != ACTIVE for c in cfgs[1:])


def test_option_order_puts_the_active_first_even_when_declared_last():
    forks = tiny_forks()
    assert ordered_options(forks["seed"], "a", "archaeology") == (
        "a", "p0", "p1", "dr", "dc")
    assert ordered_options(forks["seed"], "p1", "assess") == ("p1", "a", "p0")


def test_enumeration_is_deterministic():
    theory = make_theory()
    first = [c.digest for c in enumerate_configurations(theory, "reassess")]
    again = [c.digest for c in enumerate_configurations(theory, "reassess")]
    assert first == again and len(set(first)) == len(first)


# ---------------------------------------------------------------- modes


@pytest.mark.parametrize("mode", sorted(HAND_COUNTS))
def test_every_mode_yields_the_hand_count(mode):
    raw, total, not_runnable = HAND_COUNTS[mode]
    cfgs = list(enumerate_configurations(make_theory(), mode))
    assert len(cfgs) == total
    assert sum(c.not_runnable for c in cfgs) == not_runnable
    count = count_configurations(make_theory(), mode)
    assert (count.raw, count.total, count.not_runnable) == HAND_COUNTS[mode]
    assert count.exact and not count.capped


def test_retired_options_appear_only_in_their_modes():
    def seeds(mode):
        return {c.mapping["seed"] for c in
                enumerate_configurations(make_theory(), mode)}
    assert seeds("assess") == {"a", "p0", "p1"}
    assert seeds("reassess") == {"a", "p0", "p1", "dr"}
    assert seeds("archaeology") == {"a", "p0", "p1", "dr", "dc"}
    labels = {c.mapping["seed"]: c.lifecycle for c in
              enumerate_configurations(make_theory(), "archaeology")}
    assert labels["dr"] == RETIRED_REASSESSABLE
    assert labels["dc"] == RETIRED_CERTAIN


@pytest.mark.parametrize("mode", MODES)
def test_policy_and_narrative_forks_are_held_in_every_mode(mode):
    for cfg in enumerate_configurations(make_theory(), mode):
        assert cfg.mapping["render"] == "plain"
        assert cfg.mapping["meaning"] == "literal"


@pytest.mark.parametrize("mode", [m for m in MODES if m != "probe-constraint"])
def test_invalid_configurations_are_never_yielded_outside_probe(mode):
    for cfg in enumerate_configurations(make_theory(), mode):
        assert cfg.lifecycle != INVALID


def test_probe_constraint_yields_the_excluded_combinations_labelled():
    cfgs = list(enumerate_configurations(make_theory(), "probe-constraint"))
    invalid = [c for c in cfgs if c.lifecycle == INVALID]
    assert len(invalid) == 5
    assert all(any(r.startswith("violates ") for r in c.reasons)
               for c in invalid)
    assert _triples(cfgs)[:4] == [("a", "native", "round"),
                                  ("a", "native", "flat"),
                                  ("a", "input", "round"),
                                  ("a", "input", "flat")]


def test_unimplemented_options_are_yielded_and_marked_not_runnable():
    cfgs = [c for c in enumerate_configurations(make_theory(), "assess")
            if c.mapping["origin"] == "input"]
    assert len(cfgs) == 2
    assert all(c.not_runnable for c in cfgs)
    assert all("origin=input is not implemented" in c.reasons for c in cfgs)


# --------------------------------------------------------------- single


def test_single_is_the_active_when_nothing_is_set():
    cfgs = list(enumerate_configurations(make_theory(), "single"))
    assert [c.mapping for c in cfgs] == [ACTIVE_SELECTION]
    assert cfgs[0].lifecycle == ACTIVE


def test_single_follows_the_environment(monkeypatch):
    monkeypatch.setenv(ENV_PREFIX + "SEED", "p0")
    (cfg,) = enumerate_configurations(make_theory(), "single")
    assert cfg.mapping["seed"] == "p0"


def test_single_follows_a_named_configuration(monkeypatch):
    store = MemoryStore("tiny", ACTIVE_SELECTION,
                        named={"alt": dict(ACTIVE_SELECTION, seed="dr")})
    monkeypatch.setenv(CONFIG_ENV, "alt")
    (cfg,) = enumerate_configurations(make_theory(store=store), "single")
    assert cfg.name == "alt" and cfg.lifecycle == RETIRED_REASSESSABLE


def test_single_holds_a_policy_fork_and_says_so(monkeypatch):
    monkeypatch.setenv(ENV_PREFIX + "RENDER", "fancy")
    (cfg,) = enumerate_configurations(make_theory(), "single")
    assert cfg.mapping["render"] == "plain"
    assert any("policy fork render held" in r for r in cfg.reasons)


def test_single_refuses_a_selection_that_breaks_a_constraint(monkeypatch):
    monkeypatch.setenv(ENV_PREFIX + "ORIGIN", "input")
    with pytest.raises(InvalidSelectionError, match="origin=input"):
        enumerate_configurations(make_theory(), "single")
    assert count_configurations(make_theory(), "single").total == 0


# ---------------------------------------------------------- forks / cap


def test_a_fork_subset_holds_everything_else_at_active():
    cfgs = list(enumerate_configurations(make_theory(), "assess",
                                         forks=["shape"]))
    assert _triples(cfgs) == [("a", "native", "round"),
                              ("a", "native", "flat")]
    assert [c.mapping["shape"] for c in
            enumerate_configurations(make_theory(), "assess", forks="shape")
            ] == ["round", "flat"]


def test_a_policy_fork_cannot_be_swept_by_asking():
    plan = plan_enumeration(make_theory(), "assess", forks=["render"])
    assert plan.swept == () and plan.raw == 1
    assert plan.notes == ("policy fork render is held at its active option "
                          "in every mode",)


def test_an_unknown_fork_in_the_subset_is_refused():
    with pytest.raises(KeyError, match="ghost"):
        enumerate_configurations(make_theory(), "assess", forks=["ghost"])


def test_a_cap_truncates_the_same_order():
    theory = make_theory()
    full = [c.digest for c in enumerate_configurations(theory, "reassess")]
    for cap in (0, 1, 3, 50):
        got = [c.digest for c in
               enumerate_configurations(theory, "reassess", cap=cap)]
        assert got == full[:cap]
    count = count_configurations(theory, "reassess", cap=3)
    assert count.yielded == 3 and count.capped and count.total == 11
    assert not count_configurations(theory, "reassess", cap=50).capped


@pytest.mark.parametrize("cap", [-1, True])
def test_a_bad_cap_is_refused(cap):
    with pytest.raises(ValueError):
        enumerate_configurations(make_theory(), "assess", cap=cap)


def test_a_bad_mode_is_refused_at_call_time():
    with pytest.raises(ValueError):
        enumerate_configurations(make_theory(), "everything")


# ------------------------------------------------------------- plan


def test_the_plan_lists_the_domains_it_walks():
    plan = plan_enumeration(make_theory(), "archaeology")
    assert plan.swept == _SWEPT and plan.held == ("render", "meaning")
    assert plan.domain("seed") == ("a", "p0", "p1", "dr", "dc")
    assert plan.domain("render") == ("plain",)
    assert plan.raw == 20 and plan.prunes


# --------------------------------------------- laziness and scale


def _wide_theory(n_forks: int, n_options: int, constraints=()):
    forks = {}
    for f in range(n_forks):
        opts = [VariantOption("o0", "s", "c", adopted=True)] + [
            VariantOption("o%d" % k, "s", "c", priority=1)
            for k in range(1, n_options)]
        forks["f%02d" % f] = Fork("f%02d" % f, "q", "t", opts, "OPEN")
    selection = {f: "o0" for f in forks}
    return make_theory(forks=forks, constraints=list(constraints),
                       selection=selection, theory_id="wide")


def test_enumeration_is_lazy_on_a_huge_space():
    # 3**26 ~ 2.5e12 raw combinations; the first few must come at once.
    first = Requires("f00", "o1", "f25", frozenset({"o2"}), "r", "t")
    theory = _wide_theory(26, 3, [first])
    start = time.perf_counter()
    gen = enumerate_configurations(theory, "assess")
    head = list(itertools.islice(gen, 5))
    assert time.perf_counter() - start < 2.0
    assert head[0].lifecycle == ACTIVE
    assert [c.mapping["f25"] for c in head] == ["o0", "o1", "o2", "o0", "o1"]


def test_counting_a_huge_space_does_not_materialise_it():
    constraints = [
        Requires("f00", "o1", "f25", frozenset({"o2"}), "r", "t"),
        Excludes("f03", "o2", "f04", "o2", "x", "t"),
    ]
    theory = _wide_theory(26, 3, constraints)
    start = time.perf_counter()
    count = count_configurations(theory, "assess")
    assert time.perf_counter() - start < 2.0
    # f00=o1 forces f25=o2 (removes 2 of 9 pairs); f03=o2,f04=o2 removed.
    assert count.raw == 3 ** 26
    assert count.valid == 3 ** 22 * 7 * 8
    assert count.exact and count.pruned == count.raw - count.valid


def test_counting_past_the_limit_is_flagged_inexact():
    count = count_configurations(make_theory(), "archaeology", limit=3,
                                 cap=100)
    assert not count.exact and count.not_runnable is None
    assert count.capped                     # cannot promise the cap held
    assert count.as_dict()["exact"] is False


# ------------------------------------------------- awkward constraints


class _Custom:
    """A constraint type the enumerator does not recognise."""

    rationale = "custom"

    def violated_by(self, selection):
        return selection.get("seed") == "p0" and \
            selection.get("shape") == "flat"

    def describe(self):
        return "custom"


@pytest.mark.parametrize("constraint", [
    Requires("seed", "p0", "ghost", frozenset({"x"}), "unknown fork", "t"),
    Excludes("ghost", "x", "seed", "p0", "never fires", "t"),
    Requires("ghost", "x", "spook", frozenset({"y"}), "never fires", "t"),
    Excludes("render", "plain", "meaning", "literal", "held pair", "t"),
    _Custom(),
])
@pytest.mark.parametrize("mode", MODES)
def test_count_matches_enumeration_for_awkward_constraints(constraint, mode,
                                                           monkeypatch):
    theory = make_theory(constraints=[constraint])
    try:
        cfgs = list(enumerate_configurations(theory, mode))
    except InvalidSelectionError:
        cfgs = []
    count = count_configurations(theory, mode)
    assert count.total == len(cfgs)
    assert count.not_runnable == sum(c.not_runnable for c in cfgs)


def test_a_theory_without_forks_has_one_empty_configuration():
    theory = make_theory(forks={}, constraints=[], selection={})
    (cfg,) = enumerate_configurations(theory, "archaeology")
    assert cfg.selection == () and cfg.lifecycle == ACTIVE
    assert count_configurations(theory, "assess").total == 1


def test_an_empty_domain_yields_nothing():
    plan_domains = [("a",), ()]
    assert list(en._walk(["x", "y"], plan_domains, [])) == []
    assert en._count(["x", "y"], plan_domains, [], 10) == (0, True)


# ------------------------------------------ randomised cross-checks


def _reference(theory, mode):
    """A naive second implementation: full product, then filter."""
    from metaphysica.testground.configurations.modes import spec, sweeps

    mode_spec = spec(mode)
    forks = theory.switches.forks()
    active = theory.selections.active().mapping
    domains = []
    for fid, fork in forks.items():
        if mode_spec.single or fork.kind != "physics":
            domains.append([active[fid]])
            continue
        ranked = sorted(enumerate(fork.options),
                        key=lambda p: (p[1].id != active[fid],
                                       p[1].priority, p[0]))
        domains.append([o.id for _, o in ranked
                        if o.id == active[fid] or sweeps(mode, o)])
    out = []
    for combo in itertools.product(*domains):
        sel = dict(zip(forks, combo))
        if mode_spec.prunes and not is_valid(
                sel, theory.switches.constraints()):
            continue
        out.append(sel)
    return out


@pytest.mark.parametrize("seed", range(40))
def test_enumeration_and_count_agree_with_a_naive_product(seed):
    rng = random.Random(seed)
    theory = random_theory(rng, rng.randint(2, 6), rng.randint(0, 5))
    for mode in MODES:
        expected = _reference(theory, mode)
        try:
            got = list(enumerate_configurations(theory, mode))
        except InvalidSelectionError:
            assert mode == "single" and expected == []
            got = []
        assert [c.mapping for c in got] == expected, mode
        count = count_configurations(theory, mode)
        assert count.total == len(expected), mode
        assert count.not_runnable == sum(c.not_runnable for c in got)
        assert all(c.lifecycle != INVALID for c in got
                   if mode != "probe-constraint")


def test_disabled_certain_only_ever_appears_in_archaeology():
    rng = random.Random(7)
    for _ in range(25):
        theory = random_theory(rng, 4, 2)
        forks = theory.switches.forks()
        for mode in ("assess", "reassess", "probe-constraint"):
            for cfg in enumerate_configurations(theory, mode):
                for fid, oid in cfg.selection:
                    option = forks[fid].option(oid)
                    assert not (option.status == DISABLED
                                and option.certainty == CERTAIN)
