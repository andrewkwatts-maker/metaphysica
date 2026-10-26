"""Control: 11D supergravity on the flat T^7 gives 4D N = 8 supergravity.

Cremmer and Julia, Nucl. Phys. B159 (1979) 141; Cremmer, Julia, Scherk, Phys. Lett. B76
(1978) 409: the 4D N = 8 theory has 28 vectors and 70 scalars (63 from the metric moduli and
the 3-form, 7 more from dualising the 7 two-forms), and 8 gravitini. Computed through
`actions.zero_modes`; the failing control drops the dualisation.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from math import comb

from metaphysica.actions.controls.g2_zero_modes import SUGRA_11D
from metaphysica.actions.correspondence import Correspondence
from metaphysica.actions.zero_modes import dualise_forms, zero_modes

REF = "Cremmer & Julia, Nucl. Phys. B159 (1979) 141; Cremmer, Julia & Scherk, PLB 76 (1978) 409"
WANT = {"vector": 28, "scalar": 70, "spinor": 8, "metric": 1}


def _compute(dualise: bool):
    betti = {k: comb(7, k) for k in range(8)}
    got = zero_modes(SUGRA_11D, 7, betti, "flat")
    if dualise:
        got = dualise_forms(got, 4)
    got = {k: v for k, v in got.items() if k in WANT}
    return str(sorted(got.items())), got == WANT, "N = 8: 28 vectors, 70 scalars, 8 gravitini"


def correspondence() -> Correspondence:
    return Correspondence("t7_n8_supergravity", "11D sugra on T^7", REF, lambda: _compute(True))


def control() -> Correspondence:
    """Failing control: the 7 two-forms are not dualised, so 63 scalars."""
    return Correspondence("t7_control_no_dualisation", "11D sugra on T^7", REF,
                          lambda: _compute(False))
