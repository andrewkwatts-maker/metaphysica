"""The closed geometry as a certificate: each theorem, its proof, how it could fail.

WHY ONE CERTIFICATE
===================
The geometric results are spread across a dozen modules: the enumeration, the
contribution table, the flat sector, the fundamental group, the resolution.
Prose that restates them by hand drifts. That is how "b_3 = 24" outlived the
seed that produced it. This module is the single place that paper, website and
beginner guide read the geometry from. It composes existing computations,
adds no physics, and recomputes nothing another module owns.

Every theorem carries:

  statement   rendered from the live evidence, never typed
  counts      what the quantity counts (the A4 bar)
  proof       the method, in one paragraph
  test        the pytest node that fails if the statement is false
  falsifier   what would refute it
  scope       the conditions it holds under
  references  verified sources only

It follows the active seed. Flip METAPHYSICA_VARIANT_B3_SEED and every
statement is re-derived for that family member. Off the family, it reports
that nothing derives the geometry, instead of printing numbers.

GROWTH
======
G0 of the closure plan (2026-09-30) seeds it with four topological theorems:
the resolved cohomology, chi(Y_7) = 0, the singular components, and pi_1
across the family. G2 adds two physics theorems, each scoped: the gauge
content (U(1)^12 on the resolution; N = 4 SU(2) at each orbifold locus, so no
gaugino condensate), and the flux runaway (G4 flux fixes no modulus at
leading order). Later items add theirs.

The holonomy SELECTION is held back from publication until the real-form
ruling (G3): only (12, 43) has holonomy exactly G_2. Holonomy is a Riemannian
statement and the adopted convention is the split form. See
holonomy_selection_pending().

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from metaphysica.simulations.PM.geometry.closed_geometry.certificate import (
    THEOREMS,
    certificate,
    holonomy_selection_pending,
)
from metaphysica.simulations.PM.geometry.closed_geometry.simulation import (
    ClosedGeometrySimulation,
)
from metaphysica.simulations.PM.geometry.closed_geometry.theorem import (
    Spec,
    Theorem,
    build,
)

__all__ = [
    "Theorem",
    "Spec",
    "build",
    "THEOREMS",
    "certificate",
    "holonomy_selection_pending",
    "ClosedGeometrySimulation",
]
