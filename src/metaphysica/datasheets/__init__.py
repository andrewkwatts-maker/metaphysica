"""metaphysica.datasheets — JSON datasheet builders for quarks + physics constants.

Public surface:

* :data:`KNOWN_QUARKS` — list of canonical quark names (12: 6 SM + 6 antis).
* :data:`KNOWN_CONSTANTS` — list of canonical physics-constant names.
* :func:`build_quark_datasheet(name) -> dict`
* :func:`build_constant_datasheet(name) -> dict`

Both functions return JSON-serialisable dicts. They are the source of
truth used by :func:`metaphysica.Get` and the bundled `data/` snapshots.
"""
from metaphysica.datasheets.quark import (
    KNOWN_QUARKS,
    canonical_quark_name,
    build_quark_datasheet,
)
from metaphysica.datasheets.constant import (
    KNOWN_CONSTANTS,
    canonical_constant_name,
    build_constant_datasheet,
)

__all__ = [
    "KNOWN_QUARKS",
    "KNOWN_CONSTANTS",
    "canonical_quark_name",
    "canonical_constant_name",
    "build_quark_datasheet",
    "build_constant_datasheet",
]
