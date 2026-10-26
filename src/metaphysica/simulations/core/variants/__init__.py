"""Executable forks: run the pipeline under a choice that is not yet ruled.

WHY THIS EXISTS
---------------
The framework already records its open decisions well. ``CANON["bulk"]``
carries a STRUCTURAL_CHALLENGED status, a multi-page ``challenge``, a
``resolution_evidence`` block and an explicit "RESOLUTION OPTIONS (author's
call): (a) ... (b) ... (c) ...". The four-face choice, the render policy, the
Path A/B question and the person-within-a-face reading are all documented the
same way.

What none of them can do is **run**. The options are prose, so seeing what
option (b) actually changes means editing code, rebuilding, remembering to
put it back, and comparing by hand -- which is how the strict/permissive
render policy was decided (two git branches, manually diffed). That works
once. It does not scale to a dozen open forks, and nothing stops a switch
being flipped and silently left flipped.

This module makes a fork a first-class object: declared, enumerable,
selectable, and defaulted to whatever CANON says is currently adopted.

NOT A NEW CONSTANT STORE
------------------------
Every default here must correspond to a value that already exists elsewhere
(a CANON entry, a module-level policy switch, a registry property). This is a
*view* over decisions, in the same sense that PhysicsConfig is a view over
FormulasRegistry. If a variant's default and its source disagree, that is a
bug and ``test_variants`` fails on it.

THE TUNING HAZARD -- READ THIS BEFORE ADDING A FORK
---------------------------------------------------
A switchboard for physics choices is one keystroke away from being a
parameter fitter: run every option, keep whichever agrees best with the
anchors, report that. That is anchor-shopping with better tooling, and this
repo has already retired one advertised agreement that came from exactly
that pattern.

Three rules follow, and the comparison runner enforces the first two:

1. A comparison reports **every** option's outcome. It never returns "the
   best one".
2. It never ranks by agreement with experimental anchors. Consequences are
   recorded; the ordering is declaration order.
3. Adopting an option is an explicit author act recorded at its source (the
   CANON entry or the module switch), not a default quietly changed here.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from .catalogue import FORKS  # noqa: F401
from .model import (  # noqa: F401
    _ENV_PREFIX,
    _SELECTION_ENV,
    ACTIVE,
    CONSIDERED,
    DISABLED,
    OPTION_STATUSES,
    SourceUnmeasurable,
    _STATUS_PRIORITY,
    VariantOption,
    Fork,
)
from .adopted import (  # noqa: F401
    _re_t_adoption_adopted,
    _spectral_index_route_adopted,
    _h0_route_adopted,
    _dark_energy_mechanism_adopted,
    _b3_seed_adopted,
    _flavour_seed_coupling_adopted,
    _b3_origin_adopted,
    _g2_form_adopted,
    _metric_construction_adopted,
    _twisted_norm_convention_adopted,
    _chi_eff_route_adopted,
    _bulk_signature_adopted,
    _DE_BETTI_BY_N,
    _dark_energy_betti_adopted,
    _render_policy_adopted,
    _theory_uncertainty_policy_adopted,
    _face_genericity_adopted,
    _seed_selection_adopted,
)
from .selection import (  # noqa: F401
    validate_constraints,
    violations,
    compatible,
    departures,
    canonical_departures,
    selection_id,
    reads,
    closed_gate_reads,
    reset_reads,
    untracked,
    write_reads,
    load_selection,
    _SELECTION_CACHE,
    _env_selection,
    _FORCED,
    forced,
    is_explicit,
    resolve,
    selected_status,
    off_table_selections,
    active_selection,
)
from .report import (  # noqa: F401
    describe,
    write_report,
    main,
)

__all__ = [
    "VariantOption",
    "Fork",
    "FORKS",
    "resolve",
    "active_selection",
    "describe",
    "ACTIVE",
    "CONSIDERED",
    "DISABLED",
    "OPTION_STATUSES",
    "SourceUnmeasurable",
    "selected_status",
    "off_table_selections",
    "selection_id",
    "load_selection",
    "departures",
    "compatible",
    "violations",
    "validate_constraints",
    "forced",
    "is_explicit",
]

#: A requires/excludes naming an undeclared fork or option fails at import.
validate_constraints(FORKS)
