"""Catalogue: flavour forks.

Split out of the former single-file variants.py; text moved verbatim.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from typing import Dict

from ..model import Fork, VariantOption
from ..adopted import (
    _flavour_seed_coupling_adopted,
)

FORKS: Dict[str, Fork] = {
    "flavour_seed_coupling": Fork(
        id="flavour_seed_coupling",
        question="Which b_3 does the flavour-ansatz sector consume?",
        source="simulations.PM.particle.yukawa_derivation.resolve_flavour_b3",
        status="RULED",
        read_adopted=_flavour_seed_coupling_adopted,
        notes=(
            "Opened 2026-09-22 with the b3_seed adoption. The v25 flavour "
            "formulas CLAIM b_3 in their text (theta_13 = arcsin(sqrt(2/3) "
            "* sqrt(2) * sin(pi/b3))) but were CALIBRATED at 24 and "
            "registered particle.b3 = 24 regardless of the seed -- the last "
            "seed-blind writer. A formula claiming a topological origin must "
            "consume the topology; one that will not follow the seed is a "
            "calibrated constant wearing b_3's name and must say so. "
            "MEASURED at the flip: theta_13 = 8.6686 deg at b_3 = 24 "
            "(0.8 sigma vs NuFIT), 4.8351 deg at b_3 = 43."
        ),
        options=[
            VariantOption(
                id="follow_seed",
                summary="the flavour formulas consume the live seed's b_3",
                consequence=(
                    "BUYS: consistency with the adopted path -- a formula "
                    "claiming b_3 gets b_3, and particle.b3 stops being a "
                    "frozen 24. theta_13 moves to 4.8351 deg (measured), "
                    "publishing the ansatz's real disagreement with NuFIT.\n"
                    "COSTS: the v25 'PMNS derived at 0.8 sigma' result is "
                    "exposed as a property of the off-path calibration."
                ),
                adopted=True,
            ),
            VariantOption(
                id="calibrated_24",
                summary="the flavour formulas keep their 24 as a calibrated constant",
                consequence=(
                    "BUYS: the v25 agreement figures remain reproducible "
                    "for costing, regression-pinned under this branch.\n"
                    "COSTS: the 24 must be ADMITTED to be a calibrated "
                    "constant, not b_3 -- the formula text's claim to a "
                    "topological origin is false on this branch."
                ),
            ),
        ],
    ),
}
