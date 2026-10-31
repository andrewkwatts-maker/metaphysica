"""The toy's reader for `testground rank` (invented tiers, known answers).

consistent  no tachyonic light state (m^2 >= 0)
ladder      the Ward and Lorentz identities (2 checks)
gates       the strong-CP phase (fails on every path) and the closure gate
            (no fitted input): 2 gates
chi2        the data rows that carry a sigma

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from metaphysica.testground.theory import RunReading
from metaphysica.theories.toy import model

__all__ = ["ToyRanking"]

_LADDER = ("ward_identity", "lorentz_identity")


class ToyRanking:
    """RankingProvider: reads the run's toy_output.json."""

    def read(self, root: Path, selection: Mapping[str, str]) -> RunReading:
        path = Path(root) / model.ARTIFACT
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return RunReading(missing=(model.ARTIFACT,))
        ids = data["identities"]
        sigmas = [r["sigma"] for r in data["rows"] if r.get("sigma") is not None]
        gates = [ids["strong_cp_phase"] > model.TOLERANCE,
                 data["fitted_inputs"] > 0]
        return RunReading(
            consistent=data["observables"]["m2"] >= 0,
            ladder_failed=sum(ids[k] > model.TOLERANCE for k in _LADDER),
            ladder_total=len(_LADDER),
            gates_failed=sum(gates), gates_applicable=len(gates),
            chi2=sum(s * s for s in sigmas), dof=len(sigmas))
