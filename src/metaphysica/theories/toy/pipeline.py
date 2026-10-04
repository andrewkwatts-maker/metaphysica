"""The toy theory's full-run pipeline: two `python -c` stages.

``compute`` writes ``toy_output.json`` for the selection forced through the
environment; ``generate`` renders it as ``toy_summary.txt``. Each stage runs in
a fresh process with cwd = the isolated run root, which is all the runner's
full path needs to be exercised end to end (fresh process, env forcing,
artifact, stamp, artifact signal).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import sys
from typing import Sequence, Tuple

from metaphysica.testground.theory import Stage

__all__ = ["STAGES", "ToyPipeline"]

_CALL = "import sys; from metaphysica.theories.toy.model import main; " \
        "sys.exit(main([%r]))"


def _stage(stage_id: str, kind: str) -> Stage:
    return Stage(id=stage_id, kind=kind,
                 command=(sys.executable, "-c", _CALL % stage_id),
                 timeout_s=60.0)


STAGES: Tuple[Stage, ...] = (_stage("compute", "compute"),
                             _stage("generate", "generate"))


class ToyPipeline:
    """Pipeline: the toy's ordered stages."""

    def stages(self) -> Sequence[Stage]:
        return STAGES
