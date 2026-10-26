"""The PM engine's own compatibility and testground's agree on every pair."""
from __future__ import annotations

import itertools

from metaphysica.simulations.core import variants
from metaphysica.testground.configurations.enumerate import (
    enumerate_configurations)
from metaphysica.testground.constraints import (
    constraints_from_options, is_valid)
from metaphysica.theories.pm import PmSwitches

from .test_2a_support import make_theory


def _options(fork):
    return fork.option_ids()


def test_every_cross_fork_pair_agrees():
    cons = list(PmSwitches().constraints())
    assert cons, "PM declares constraints; an empty list hides the join"
    forks = variants.FORKS
    for fa, fb in itertools.combinations(forks, 2):
        for oa in _options(forks[fa]):
            for ob in _options(forks[fb]):
                sel = {fa: oa, fb: ob}
                assert variants.compatible(sel) == is_valid(sel, cons), sel


def test_assess_enumeration_yields_nothing_variants_refuses():
    forks = dict(variants.FORKS)
    theory = make_theory(
        forks=forks, constraints=constraints_from_options(forks),
        selection=variants.active_selection(), theory_id="pm_engine")
    seen = 0
    for cfg in enumerate_configurations(theory, "assess", cap=4000):
        assert not variants.violations(dict(cfg.mapping)), cfg.mapping
        seen += 1
    assert seen > 1
