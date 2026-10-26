"""Options whose single deviation changes no row.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import List, Mapping

from metaphysica.testground.audit.rows import Option, Rows, changed

__all__ = ["no_op_options"]


def no_op_options(base: Rows, singles: Mapping[Option, Rows]) -> List[Option]:
    """Single deviations that change no row, sorted."""
    return sorted(opt for opt, rows in singles.items() if not changed(base, rows))
