"""metaphysica.testground -- a generic test ground for physics theories.

A theory declares its switches (forks and options), the constraints between
them, a pipeline that runs one configuration, and the signals measured from a
run. The test ground enumerates valid configurations, runs them in isolation,
scores them by the decision rule (D-019: validity > closure > consistency >
elegance > data as tie-break), recommends -- never adopts -- and exports the
whole space as a path graph for the website and the app.

Theory-agnostic by construction: nothing here imports `metaphysica.simulations`,
`metaphysica.generators` or `metaphysica.website`.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

__all__ = ["__version__"]
__version__ = "0.1.0"
