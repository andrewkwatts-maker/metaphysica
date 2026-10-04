"""Where the toy keeps its adopted selection and its decisions.

The selection store is the test ground's YAML store
(``testground.configurations.store.YamlSelectionStore``) over the toy's
``configs/active.yaml`` and ``configs/configurations.yaml``. It is bound
lazily: the toy imports, declares its forks and computes its signals without
it, and the store is constructed on first use (every attribute the real store
has is reachable through this proxy).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Mapping, Optional

from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.switches.model import Fork

__all__ = ["STORE_MODULE", "LazyYamlStore", "ToyDecisions"]

STORE_MODULE = "metaphysica.testground.configurations.store"


class LazyYamlStore:
    """SelectionStore over two YAML files, built on first use."""

    def __init__(self, active_path: Path, named_path: Path,
                 forks: Optional[Mapping[str, Fork]] = None,
                 theory_id: Optional[str] = None) -> None:
        self.active_path = Path(active_path)
        self.named_path = Path(named_path)
        self._forks = forks
        self._theory_id = theory_id
        self._store: Optional[Any] = None

    def _real(self) -> Any:
        if self._store is None:
            cls = getattr(importlib.import_module(STORE_MODULE),
                          "YamlSelectionStore")
            self._store = cls(self.active_path, self.named_path,
                              forks=self._forks, theory_id=self._theory_id)
        return self._store

    def active(self) -> Configuration:
        return self._real().active()

    def named(self) -> Mapping[str, Configuration]:
        return self._real().named()

    def write_active(self, cfg: Configuration, decision_id: str,
                     note: str = "") -> None:
        self._real().write_active(cfg, decision_id, note)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._real(), name)


class ToyDecisions:
    """DecisionLogProvider: the toy's own decision log."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def decision_log_path(self) -> Optional[Path]:
        return self._path
