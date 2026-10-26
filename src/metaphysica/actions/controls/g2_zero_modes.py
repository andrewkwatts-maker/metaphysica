"""Control: zero-mode counting for 11D supergravity on a G2-holonomy manifold.

Computed by `actions.zero_modes.zero_modes`.

Citation-level rule (Papadopoulos and Townsend, Phys. Lett. B357 (1995) 300;
Acharya, hep-th/9812205): on a compact G2 manifold X with b1 = 0, M-theory
gives 4D N = 1 supergravity with b2(X) U(1) vector multiplets and b3(X) neutral
chiral multiplets. Joyce's T^7/Z2^3 example with (b2, b3) = (12, 43) is the
recorded known case. This is not applied to any PM manifold here.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Dict, Mapping

from fractions import Fraction

from metaphysica.actions.correspondence import Correspondence
from metaphysica.actions.model import Field
from metaphysica.actions.zero_modes import zero_modes

REF = ("Papadopoulos & Townsend 1995 (PLB 357, 300); Acharya hep-th/9812205; "
       "Joyce, Compact Manifolds with Special Holonomy (2000)")
JOYCE_EXAMPLE = {"name": "Joyce T^7/Z2^3 example", "betti": {0: 1, 1: 0, 2: 12, 3: 43}}


SUGRA_11D = (Field("g", "metric", 1, Fraction(0)), Field("C", "form:3", 1, Fraction(3)),
             Field("psi", "spinor", 32, Fraction(5, 2)))


def zero_mode_rule(betti: Mapping[int, int]) -> Dict[str, int]:
    """Betti numbers of a G2 manifold -> 4D N = 1 multiplet counts, through `zero_modes`.

    A chiral multiplet is a complex scalar: b3 metric moduli plus b3 axions = 2 b3 real scalars.
    """
    got = zero_modes(SUGRA_11D, 7, betti, "G2")
    return {"u1_vector_multiplets": got.get("vector", 0),
            "chiral_multiplets": got.get("scalar", 0) // 2}


def _compute(swap: bool):
    b = JOYCE_EXAMPLE["betti"]
    got = zero_mode_rule({1: 0, 2: b[3], 3: b[2]} if swap else b)
    want = {"u1_vector_multiplets": 12, "chiral_multiplets": 43}
    return str(got), got == want, "Joyce example (b2, b3) = (12, 43)"


def correspondence() -> Correspondence:
    return Correspondence("g2_zero_mode_counting", "11D sugra on G2", REF, lambda: _compute(False))


def control() -> Correspondence:
    """Failing control: b2 and b3 swapped."""
    return Correspondence("g2_control_swapped_betti", "11D sugra on G2", REF,
                          lambda: _compute(True))
