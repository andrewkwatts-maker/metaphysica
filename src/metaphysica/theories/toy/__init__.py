"""The toy theory: a tiny, fictitious model with a KNOWN ANSWER.

It exists to prove the test ground right before the test ground judges a real
theory. It runs in milliseconds, touches no real physics, and every outcome
of an assessment of it is known in advance.

Forks (``forks.py``)
====================
=================  ==========  =================================================
fork               kind        options (ACTIVE first)
=================  ==========  =================================================
coupling_route     physics     geometric | fitted | numerology (DISABLED, certain)
cutoff             physics     planck | string_scale | lattice (DISABLED,
                               reassessable)
mass_rule          physics     seesaw | dirac_only | radiative (not implemented)
extra_param        physics     none | scalar_singlet (adds a discrete input)
matching           physics     one_loop | tree
render_policy      policy      plain | verbose (held fixed)
=================  ==========  =================================================

Constraints: ``extra_param=scalar_singlet`` Requires ``matching=one_loop``;
``coupling_route=numerology`` Excludes ``matching=one_loop``. One narrative
entry (what the seed counts) is drawn but never run.

KNOWN ANSWER (asserted by tests/testground/test_toy_end_to_end.py)
==================================================================
With the shipped ``configs/active.yaml`` (every fork at its ACTIVE option):

(i)   ``coupling_route=fitted`` fits the data BETTER (no tension, lower chi^2)
      but needs one fitted input: it LOSES to the active configuration, and the
      deciding criterion is CLOSURE.
(ii)  ``cutoff=string_scale`` ties the active configuration on every
      criterion, data included: a complete tie keeps the active, so the
      verdict is ACTIVE_CONFIRMED.
(iii) ``mass_rule=dirac_only`` makes the light state tachyonic: REJECTED, with
      the reason "tachyonic light state ...".
(iv)  ``coupling_route=numerology`` (DISABLED, certain) is enumerated only in
      ARCHAEOLOGY mode; ``cutoff=lattice`` (DISABLED, reassessable) from
      REASSESS mode on.
(v)   With ``configs/fixtures/active_recommend_change.yaml`` as the active
      selection (``matching=tree``, which breaks the Ward identity), the
      configuration with ``matching=one_loop`` beats it on CONSISTENCY and the
      verdict is RECOMMEND_CHANGE.

Also: ``mass_rule=radiative`` configurations are NOT_RUNNABLE; the
strong-CP-like phase fails on every path and must surface as a STANDING
failure (excluded from the comparison, disclosed); ``render_policy`` is held at
``plain``.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Optional, Sequence

from metaphysica.testground.constraints import Constraint
from metaphysica.testground.switches.model import Fork
from metaphysica.testground.theory import Theory
from metaphysica.theories.toy import model
from metaphysica.theories.toy.forks import CONSTRAINTS, FORKS, NARRATIVE
from metaphysica.theories.toy.pipeline import ToyPipeline
from metaphysica.theories.toy.signals import SIGNALS, ToyAnchors, ToySignals
from metaphysica.theories.toy.store import LazyYamlStore, ToyDecisions

__all__ = [
    "CONFIGS",
    "FIXTURES",
    "RECOMMEND_CHANGE_ACTIVE",
    "FORKS",
    "CONSTRAINTS",
    "SIGNALS",
    "ToySwitches",
    "make_theory",
    "THEORY",
    "THEORY_RECOMMEND_CHANGE",
]

CONFIGS = Path(__file__).resolve().parent / "configs"
FIXTURES = CONFIGS / "fixtures"
RECOMMEND_CHANGE_ACTIVE = FIXTURES / "active_recommend_change.yaml"


class ToySwitches:
    """SwitchProvider: the toy's forks and constraints."""

    def forks(self) -> Mapping[str, Fork]:
        return FORKS

    def constraints(self) -> Sequence[Constraint]:
        return CONSTRAINTS


def make_theory(configs_dir: Optional[Path] = None,
                active_path: Optional[Path] = None) -> Theory:
    """The toy over ``configs_dir`` (default: the package's own configs).

    Tests pass a temporary copy, so accept/retire never touch the package;
    ``active_path`` swaps only the adopted selection (fixture (v)).
    """
    root = Path(configs_dir) if configs_dir is not None else CONFIGS
    active = Path(active_path) if active_path is not None else \
        root / "active.yaml"
    return Theory(
        id="toy",
        title="Toy theory (one seed, one coupling, one light mass)",
        env_prefix=model.ENV_PREFIX,
        switches=ToySwitches(),
        selections=LazyYamlStore(active, root / "configurations.yaml",
                                 forks=FORKS, theory_id="toy"),
        pipeline=ToyPipeline(),
        signals=ToySignals(),
        anchors=ToyAnchors(),
        decisions=ToyDecisions(root / "DECISIONS.md"),
        assessment_config=root / "assessment.yaml",
        invalidate_caches=model.clear_cache,
        narrative=NARRATIVE,
        lineage=root / "lineage.yaml" if (root / "lineage.yaml").is_file()
        else None,
    )


THEORY = make_theory()
THEORY_RECOMMEND_CHANGE = make_theory(active_path=RECOMMEND_CHANGE_ACTIVE)
