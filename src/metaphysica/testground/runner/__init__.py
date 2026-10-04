"""The runner: how configurations are executed, isolated and cached.

- ``plan``        order, de-duplicate and group configurations (one fresh
                  process per group of import-time-bound fork options);
- ``isolation``   one stamped scratch root per configuration;
- ``screen``      the cheap in-process pass over SCREEN-cost signals;
- ``worker``      a full run: the theory's pipeline stages in fresh processes;
- ``pool``        many runs at once, with JSON-lines progress;
- ``cache``       results keyed by (theory, digest, engine fingerprint);
- ``fingerprint`` the engine fingerprint those keys use.

The screen entry point is ``metaphysica.testground.runner.screen.screen``; it is
deliberately NOT re-exported here, because binding a function named ``screen``
on the package would shadow the ``screen`` submodule.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from metaphysica.testground.runner.cache import RunCache, default_runs_dir
from metaphysica.testground.runner.fingerprint import engine_fingerprint
from metaphysica.testground.runner.isolation import (prepare_root, read_stamp,
                                                     root_for, stamp_digest,
                                                     stamped_context)
from metaphysica.testground.runner.plan import RunGroup, RunPlan, build_plan
from metaphysica.testground.runner.pool import (PoolResult, PoolTask,
                                                ProgressLog, full_run_tasks,
                                                run_pool)
from metaphysica.testground.runner.screen import (ScreenResult,
                                                  evaluate_configuration,
                                                  load_theory)
from metaphysica.testground.runner.worker import (COMPLETED, NOT_RUNNABLE,
                                                  RunResult, StageResult,
                                                  run_configuration, run_full)

__all__ = [
    "RunCache",
    "default_runs_dir",
    "engine_fingerprint",
    "prepare_root",
    "read_stamp",
    "root_for",
    "stamp_digest",
    "stamped_context",
    "RunGroup",
    "RunPlan",
    "build_plan",
    "PoolResult",
    "PoolTask",
    "ProgressLog",
    "full_run_tasks",
    "run_pool",
    "ScreenResult",
    "evaluate_configuration",
    "load_theory",
    "COMPLETED",
    "NOT_RUNNABLE",
    "RunResult",
    "StageResult",
    "run_configuration",
    "run_full",
]
