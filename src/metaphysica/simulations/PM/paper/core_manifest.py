"""The core manifest (D-025): the sections that carry the argument, in order.

Each entry is ``(section_id, role)``; the role is one sentence on what that
step establishes. It states no number: values live in the sections it names.
Every other section stays published and is labelled supplementary. The
introduction (section 1) builds its chain of argument from this tuple, and
``generators/generate_core_paper.py`` writes it to ``core_paper.json``.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from typing import Tuple

CORE_MANIFEST: Tuple[Tuple[str, str], ...] = (
    ("0", "States what is assumed, what the closed geometry is, what follows "
          "from it and where it stands against data."),
    ("1", "Poses the problem, names the one idea, and says how to read the "
          "paper."),
    ("2", "Defines the geometric framework: the bulk, the two shadows and the "
          "compact G2 internal space."),
    ("2.4", "Proves the closed geometry theorem by theorem, including the "
            "existence of the holonomy-G2 metric by Joyce's theorem."),
    ("3.2", "Reads the Standard Model gauge sectors off the geometry."),
    ("3", "Derives gauge coupling unification and the GUT scale from the "
          "same inputs."),
    ("4.1", "Treats chirality and the spinor structure, and says what is "
            "still open."),
    ("4.2", "Counts fermion generations from the topology and sets the Yukawa "
            "texture."),
    ("4.3", "Obtains quark mixing from the geometry and compares it with "
            "data."),
    ("4.4", "Fixes the Higgs mass through moduli stabilisation and records "
            "where that step is calibrated."),
    ("5.1", "Derives four-dimensional gravity by Kaluza-Klein reduction."),
    ("5.2", "Derives the dark-energy sector from the dimensional reduction "
            "and states its status."),
    ("6", "Lists the falsifiable predictions with their status."),
    ("7", "Gives the conclusions, the scoreboard and the global fit, "
          "including every failure."),
)


def manifest_ids() -> Tuple[str, ...]:
    """Section ids in manifest order."""
    return tuple(sid for sid, _ in CORE_MANIFEST)


def validate() -> None:
    """Fail early on a duplicate id or an empty role."""
    ids = manifest_ids()
    if len(set(ids)) != len(ids):
        raise ValueError("core manifest repeats a section id: %s" % (ids,))
    for sid, role in CORE_MANIFEST:
        if not role.strip():
            raise ValueError("core manifest section %s has no role" % sid)


validate()
