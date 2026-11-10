"""Re-export of `metaphysica.config.path_valued` (kept for existing importers).

The metaclass lives one level up so `config.constants` can use it without
importing the `config.parameters` package, which imports `config.constants`.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from ..path_valued import (NotEvaluable, PATH_NAMES, PathValued,
                           TCS187_PATH, tcs187_only)

__all__ = ["PathValued", "PATH_NAMES", "NotEvaluable", "TCS187_PATH", "tcs187_only"]
