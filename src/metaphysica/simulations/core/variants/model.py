"""Fork model: environment constants and the testground model, re-exported.

`VariantOption`, `Fork`, the status vocabulary and `SourceUnmeasurable` are
defined once, in `metaphysica.testground.switches.model`. This module keeps the
names this package and its callers import, and holds the two environment
constants that are specific to the PM registry.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from metaphysica.testground.switches.model import (  # noqa: F401
    ACTIVE,
    CONSIDERED,
    DISABLED,
    OPTION_STATUSES,
    STATUS_PRIORITY as _STATUS_PRIORITY,
    Fork,
    SourceUnmeasurable,
    VariantOption,
)

#: Environment prefix: METAPHYSICA_VARIANT_<FORK_ID_UPPER>=<option id>
_ENV_PREFIX = "METAPHYSICA_VARIANT_"
#: Path to a JSON {fork: option} map honoured by resolve() (Track G1).
_SELECTION_ENV = "METAPHYSICA_SELECTION"
