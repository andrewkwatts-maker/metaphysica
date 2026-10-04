"""The toy theory's forks, constraints and narrative.

Five physics forks, one policy fork, one narrative entry. Between them they
carry every status the test ground distinguishes: an ACTIVE option per fork,
live CONSIDERED rivals, a DISABLED option refuted for CERTAIN (swept only in
ARCHAEOLOGY mode), a DISABLED option marked REASSESSABLE (swept from REASSESS
mode), an option no code implements (its configurations are NOT_RUNNABLE), an
option that adds a discrete input, one Requires and one Excludes constraint.

Option texts use the BUYS / COSTS / DEMOTED / RULED OUT headings the path graph
splits rationale on; decision ids refer to the toy's own decision log
(``configs/DECISIONS.md``).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from metaphysica.testground.constraints import Constraint, Excludes, Requires
from metaphysica.testground.switches.model import (
    CERTAIN,
    DISABLED,
    REASSESSABLE,
    Fork,
    VariantOption,
)

__all__ = ["FORKS", "CONSTRAINTS", "NARRATIVE", "defaults", "fork_list"]

_SRC = "metaphysica.theories.toy.model.FORMULAS"


def _opt(id: str, summary: str, consequence: str, **kw) -> VariantOption:
    return VariantOption(id=id, summary=summary, consequence=consequence, **kw)


def _coupling_route() -> Fork:
    return Fork(
        id="coupling_route", question="Where does the coupling g0 come from?",
        source=_SRC, status="RULED", kind="physics", binding="call_time",
        consumers=("metaphysica.theories.toy.model",),
        legacy_option="geometric",
        notes="The coupling is the one number every observable depends on.",
        options=[
            _opt("geometric", "g0 = 1/(2 SEED + 1), derived from the seed",
                 "BUYS: no fitted input; g0 is an output of the seed.\n"
                 "COSTS: alpha_low sits 2.6 sigma from the toy datum (a "
                 "TENSION).", adopted=True, decision_refs=("D-001",)),
            _opt("fitted", "g0 fitted to the alpha_low datum",
                 "BUYS: alpha_low agrees exactly and m_light improves.\n"
                 "COSTS: one fitted input -- the closure criterion counts it, "
                 "so this option loses to the derived one whatever the data "
                 "say.", priority=0,
                 kill_condition="adopted only if the derived route fails "
                                "validity"),
            _opt("numerology", "g0 = 0.0729, a numerical coincidence",
                 "RULED OUT: a typed number with no mechanism behind it; kept "
                 "runnable for archaeology.", status=DISABLED,
                 certainty=CERTAIN, decision_refs=("D-001",),
                 restored_from="toy@v0:model.py"),
        ])


def _cutoff() -> Fork:
    return Fork(
        id="cutoff", question="Which ultraviolet regulator closes the loops?",
        source=_SRC, status="RULED", kind="physics", binding="call_time",
        consumers=("metaphysica.theories.toy.model",),
        notes="Low-energy observables are cutoff-independent after "
              "renormalisation, so a continuum cutoff changes no number.",
        options=[
            _opt("planck", "a continuum cutoff at the Planck scale",
                 "BUYS: Lorentz invariance is exact.\nCOSTS: nothing the "
                 "toy measures.", adopted=True, decision_refs=("D-002",)),
            _opt("string_scale", "a continuum cutoff at the string scale",
                 "BUYS: the same as planck.\nCOSTS: the same as planck -- a "
                 "complete tie, so the active option stays.", priority=1),
            _opt("lattice", "a hypercubic lattice with spacing 1/10",
                 "BUYS: a non-perturbative definition.\nCOSTS: breaks the "
                 "Lorentz identity at O(a^2).\nDEMOTED 2026-10-02 (D-002): "
                 "reassessable if an improved action removes the O(a^2) "
                 "term.", status=DISABLED, certainty=REASSESSABLE,
                 decision_refs=("D-002",)),
        ])


def _mass_rule() -> Fork:
    return Fork(
        id="mass_rule", question="How does the light state get its mass?",
        source=_SRC, status="OPEN", kind="physics", binding="call_time",
        consumers=("metaphysica.theories.toy.model",),
        options=[
            _opt("seesaw", "m_light = g0^2 / SEED",
                 "BUYS: a small positive mass from the seed.\nCOSTS: assumes "
                 "a heavy partner.", adopted=True, decision_refs=("D-001",)),
            _opt("dirac_only", "m^2 = g0^2 - g0 / SEED",
                 "BUYS: no heavy partner.\nCOSTS: m^2 < 0 for the derived "
                 "coupling -- a tachyon, which the validity gate rejects.",
                 priority=1),
            _opt("radiative", "the mass is generated at one loop",
                 "OPEN: no code implements it yet; its configurations are "
                 "NOT_RUNNABLE, not failed.", priority=1, implemented=False),
        ])


def _extra_param() -> Fork:
    return Fork(
        id="extra_param", question="Does the model carry an extra scalar?",
        source=_SRC, status="RULED", kind="physics", binding="call_time",
        consumers=("metaphysica.theories.toy.model",),
        options=[
            _opt("none", "no extra field", "BUYS: nothing to choose.",
                 adopted=True, decision_refs=("D-001",)),
            _opt("scalar_singlet", "a gauge-singlet scalar",
                 "BUYS: a dark-matter candidate the toy does not test.\n"
                 "COSTS: its charge is CHOSEN, not derived -- one discrete "
                 "input under closure.\nASSUMES: one-loop matching (a "
                 "Requires constraint).", priority=1,
                 adds_discrete_input=True),
        ])


def _matching() -> Fork:
    return Fork(
        id="matching", question="At what order are heavy states matched out?",
        source=_SRC, status="RULED", kind="physics", binding="call_time",
        consumers=("metaphysica.theories.toy.model",),
        options=[
            _opt("one_loop", "include the threshold correction g0/(SEED+1)",
                 "BUYS: the Ward identity holds exactly.", adopted=True,
                 decision_refs=("D-002",)),
            _opt("tree", "drop the threshold correction",
                 "BUYS: one formula fewer.\nCOSTS: the Ward identity breaks "
                 "by g0/(SEED+1) -- one consistency failure.", priority=1),
        ])


def _render_policy() -> Fork:
    return Fork(
        id="render_policy", question="How are results rendered?",
        source="metaphysica.theories.toy.model.write_summary", status="RULED",
        kind="policy", stage="generation", binding="call_time",
        notes="A policy fork: held at its active option in every comparison.",
        options=[
            _opt("plain", "one line per run", "BUYS: short output.",
                 adopted=True),
            _opt("verbose", "every intermediate value",
                 "COSTS: longer output; changes no physics.", priority=1),
        ])


def fork_list() -> List[Fork]:
    """The forks in declaration order."""
    return [_coupling_route(), _cutoff(), _mass_rule(), _extra_param(),
            _matching(), _render_policy()]


FORKS: Dict[str, Fork] = {f.id: f for f in fork_list()}

CONSTRAINTS: Tuple[Constraint, ...] = (
    Requires("extra_param", "scalar_singlet", "matching",
             frozenset({"one_loop"}),
             rationale="the singlet is defined by its one-loop threshold; "
                       "without that matching it is not the same field",
             source="toy D-002"),
    Excludes("coupling_route", "numerology", "matching", "one_loop",
             rationale="a typed coupling has no threshold to match: the "
                       "one-loop correction is defined from a derived g0",
             source="toy D-001"),
)

NARRATIVE: Tuple[Dict[str, object], ...] = (
    {
        "id": "narrative:seed_reading",
        "label": "What the seed counts",
        "title": "What the seed counts",
        "text": "SEED = 7 is read as a count of internal cycles. The reading "
                "changes what a result MEANS, not what the code computes.\n"
                "ASSUMES: the count is topological.\n"
                "OPEN: no second observable fixes the reading (D-001).",
        "decision_refs": ("D-001",),
    },
)


def defaults() -> Dict[str, str]:
    """fork -> its declared ACTIVE option."""
    return {fork_id: fork.default() for fork_id, fork in FORKS.items()}
