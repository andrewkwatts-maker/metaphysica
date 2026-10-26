"""The fork catalogue, assembled in the original declaration order.

The documented-but-not-runnable decisions (Path A/B, the person-within-a-face
reading) are deliberately absent: declaring them would imply a switch that
does nothing.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from typing import Dict

from ..model import Fork
from . import cosmology
from . import seed
from . import g2_forms
from . import g2_metric
from . import flavour
from . import algebra
from . import policy

_BY_DOMAIN: Dict[str, Fork] = {}
_BY_DOMAIN.update(cosmology.FORKS)
_BY_DOMAIN.update(seed.FORKS)
_BY_DOMAIN.update(g2_forms.FORKS)
_BY_DOMAIN.update(g2_metric.FORKS)
_BY_DOMAIN.update(flavour.FORKS)
_BY_DOMAIN.update(algebra.FORKS)
_BY_DOMAIN.update(policy.FORKS)

#: Explicit key order: this is the order the report and every sweep use.
_ORDER = (
    "spectral_index_route",
    "h0_route",
    "dark_energy_mechanism",
    "re_t_adoption",
    "b3_seed",
    "n_gen_source",
    "b3_origin",
    "joyce_contribution_table",
    "g2_form_convention",
    "flavour_seed_coupling",
    "metric_construction",
    "chi_eff_route",
    "twisted_norm_convention",
    "lattice_24d",
    "g2_construction",
    "moduli_indexing",
    "bulk_signature",
    "dark_energy_betti",
    "render_policy",
    "theory_uncertainty_policy",
    "face_genericity",
    "seed_selection",
)

FORKS: Dict[str, Fork] = {k: _BY_DOMAIN[k] for k in _ORDER}
assert set(FORKS) == set(_BY_DOMAIN), set(_BY_DOMAIN) ^ set(FORKS)
