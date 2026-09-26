"""A declared fork that nothing reads is a switch that does nothing.

THE CRITERION IS THE MODULE'S OWN
=================================
`variants.FORKS` carries this, at the top of the declaration:

    The forks that are executable today. Documented-but-not-runnable
    decisions (Path A/B, the person-within-a-face reading) are deliberately
    absent: [...] Declaring them here would imply a switch that does
    nothing.

Measured on 2026-09-26, seven of eighteen forks do exactly that: no module in
the simulation pipeline resolves them, so selecting any of their options
changes nothing that runs. Between them they carry 25 declared, described and
costed options that are inert.

This is a sharper problem than a stale number, and it is the reason to check
it here rather than to note it in a document. An inert fork still publishes
into `variants.json` with its question, its options and its consequence
prose, so a reader of the artifact -- or of the website built from it --
cannot distinguish a decision the engine can actually execute either way
from one that is only written down. `dark_energy_betti` is the sharpest case:
status RULED, seven options with full sigma accounting, and nothing selects
any of them.

WHAT THIS TEST IS FOR
=====================
Not to fail until every fork is wired -- that is a body of work, some of it
requiring author rulings. It pins the inert set EXACTLY, so:

  * a NEW inert fork fails this test, because the set grew; and
  * WIRING one up also fails it, because the set shrank, and the pin has to
    be edited deliberately by whoever did the wiring.

A count that can only move one way is not a check, which is this
repository's most transferable lesson and the reason several defects
survived as long as they did.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pathlib
import re

from metaphysica.simulations.core.variants import FORKS

_SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "metaphysica"

#: The registry itself and the harnesses that exist to ENUMERATE forks rather
#: than to act on one. A fork read only by these is inert as physics: the
#: sweep reports it, nothing computes differently because of it.
_NOT_A_CONSUMER = {
    "variants.py",          # the declaration
    "switch_search.py",     # sweeps every fork by construction
    "fork_implications.py",  # the implication matrix, same
}

#: Forks that no pipeline module resolves. MEASURED, then pinned.
#: Wiring one up is the fix; editing this set is part of that fix.
_INERT = {
    "b3_origin",          # OPEN, 5 options
    "chi_eff_route",      # OPEN, 3 options -- unruled by standing instruction
    "g2_construction",    # OPEN, 2 options
    "moduli_indexing",    # OPEN, 3 options
    "bulk_signature",     # RULED, 3 options
    "dark_energy_betti",  # RULED, 7 options -- the sharpest case
    "face_genericity",    # RULED, 2 options
}


def _consumers() -> dict:
    """fork id -> pipeline modules that resolve it.

    A consumer names the fork in a `resolve(...)` call or reads its
    environment override. Both are how a module actually branches on a fork;
    merely importing `variants` is not.
    """
    found = {fid: [] for fid in FORKS}
    for path in _SRC.rglob("*.py"):
        if path.name in _NOT_A_CONSUMER:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for fid in FORKS:
            if re.search(r"resolve\(\s*[\"']%s[\"']" % re.escape(fid), text) \
                    or ("VARIANT_" + fid.upper()) in text:
                found[fid].append(str(path.relative_to(_SRC)))
    return found


def test_the_inert_fork_set_is_exactly_what_is_pinned():
    consumers = _consumers()
    inert = {fid for fid, c in consumers.items() if not c}
    assert inert == _INERT, (
        "the set of forks no pipeline module resolves changed.\n"
        "  newly inert (a fork was declared, or its consumer was removed): %s\n"
        "  newly wired (good -- update _INERT in this file): %s"
        % (sorted(inert - _INERT), sorted(_INERT - inert))
    )


def test_the_wired_forks_really_are_wired():
    """The other direction, so this file cannot pass on an empty walk."""
    consumers = _consumers()
    wired = {fid: c for fid, c in consumers.items() if c}
    assert len(wired) == len(FORKS) - len(_INERT)
    assert wired, "no fork has a consumer; the detector is broken, not the code"
    # b3_seed is the load-bearing one: the whole active path hangs off it.
    assert consumers["b3_seed"], "b3_seed must be resolved by the pipeline"


def test_the_detector_would_notice_a_consumer_disappearing():
    """Feed it a fork id nothing mentions and require it to come up empty."""
    text_hits = []
    fake = "a_fork_no_module_mentions"
    for path in _SRC.rglob("*.py"):
        if path.name in _NOT_A_CONSUMER:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"resolve\(\s*[\"']%s[\"']" % fake, text):
            text_hits.append(path.name)
    assert not text_hits, (
        "the detector matched a fork id that does not exist, so its hits on "
        "real ids prove nothing"
    )


def test_how_many_options_are_inert_is_recorded():
    """The number that says how much of the decision space is decoration."""
    inert_options = sum(len(FORKS[fid].options) for fid in _INERT)
    total_options = sum(len(f.options) for f in FORKS.values())
    assert (inert_options, total_options) == (25, 51), (
        "inert/total option counts moved: %s of %s"
        % (inert_options, total_options)
    )


def test_an_inert_fork_still_publishes_as_if_it_were_executable():
    """Records the consequence, so the artifact's reader is not misled twice.

    Until an inert fork is either wired or moved out of FORKS, `describe()`
    presents it identically to a live one. This test states that plainly so
    the behaviour is documented rather than discovered.
    """
    from metaphysica.simulations.core.variants import describe

    payload = describe()
    for fid in _INERT:
        entry = payload["forks"][fid]
        assert entry["options"], fid
        assert entry["selected"] == entry["default"], (
            "%s is inert, so nothing should be able to select away from its "
            "default in an ordinary run" % fid
        )
