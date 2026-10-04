"""Run cache: a finished run, reusable while the engine code is unchanged.

Results are keyed by (theory, digest, engine fingerprint) and live next to the
artifacts they describe, in the configuration's isolated root
(``<base>/<theory>/<fingerprint>/<digest>/result.json``). A different
fingerprint is a different directory, so a code change is a miss by
construction; ``invalidate`` removes the directories of every other
fingerprint. A hit also requires the root's stamp to name the same digest and
fingerprint, so a cached result never points at someone else's artifacts.

The default base is ``.runs/`` at the engine repository root (gitignored), or
``$METAPHYSICA_RUNS_DIR`` when set.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import os
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

from metaphysica.testground.runner.isolation import (
    read_stamp,
    root_for,
    safe_segment,
    write_json_atomic,
)

__all__ = [
    "RESULT_NAME",
    "RUNS_DIR_ENV",
    "default_runs_dir",
    "RunCache",
]

PathLike = Union[str, Path]

RESULT_NAME = "result.json"
RUNS_DIR_ENV = "METAPHYSICA_RUNS_DIR"


def _plain(name: str) -> bool:
    try:
        safe_segment(name, "name")
    except ValueError:
        return False
    return True


def default_runs_dir() -> Path:
    """``$METAPHYSICA_RUNS_DIR``, else ``<engine repo>/.runs``, else ``./.runs``."""
    override = os.environ.get(RUNS_DIR_ENV)
    if override:
        return Path(override)
    repo = Path(__file__).resolve().parents[4]
    if (repo / "pyproject.toml").is_file():
        return repo / ".runs"
    return Path.cwd() / ".runs"


class RunCache:
    """Results keyed by (theory, digest, fingerprint), with hit/miss counts."""

    def __init__(self, base_dir: Optional[PathLike] = None) -> None:
        self.base_dir = Path(base_dir) if base_dir is not None \
            else default_runs_dir()
        self.hits = 0
        self.misses = 0
        self._lock = threading.Lock()

    def root(self, theory_id: str, digest: str, fingerprint: str) -> Path:
        """The configuration's isolated root (where its result is kept)."""
        return root_for(self.base_dir, theory_id, digest, fingerprint)

    def _count(self, hit: bool) -> None:
        with self._lock:
            if hit:
                self.hits += 1
            else:
                self.misses += 1

    @staticmethod
    def _matches(envelope: Mapping[str, Any], theory_id: str, digest: str,
                 fingerprint: str) -> bool:
        return (envelope.get("theory") == theory_id
                and envelope.get("digest") == digest
                and envelope.get("fingerprint") == fingerprint
                and isinstance(envelope.get("payload"), dict))

    @staticmethod
    def _stamp_agrees(root: Path, digest: str, fingerprint: str) -> bool:
        stamp = read_stamp(root)
        return bool(stamp) and stamp.get("digest") == digest \
            and stamp.get("engine_fingerprint") == fingerprint

    def _load(self, theory_id: str, digest: str,
              fingerprint: str) -> Optional[Dict[str, Any]]:
        root = self.root(theory_id, digest, fingerprint)
        try:
            envelope = json.loads((root / RESULT_NAME).read_text("utf-8"))
        except (OSError, ValueError):
            return None
        if not isinstance(envelope, dict) or not self._matches(
                envelope, theory_id, digest, fingerprint):
            return None
        if not self._stamp_agrees(root, digest, fingerprint):
            return None
        return envelope["payload"]

    def get(self, theory_id: str, digest: str,
            fingerprint: str) -> Optional[Dict[str, Any]]:
        """The cached payload, or None (a miss) -- counted either way."""
        payload = self._load(theory_id, digest, fingerprint)
        self._count(payload is not None)
        return payload

    def put(self, theory_id: str, digest: str, fingerprint: str,
            payload: Mapping[str, Any]) -> Path:
        """Store ``payload`` for the key; the root must already be stamped."""
        root = self.root(theory_id, digest, fingerprint)
        if not self._stamp_agrees(root, digest, fingerprint):
            raise ValueError("refusing to cache into %s: its stamp does not "
                             "name digest %s and fingerprint %s"
                             % (root, digest, fingerprint))
        envelope = {
            "theory": theory_id,
            "digest": digest,
            "fingerprint": fingerprint,
            "stored": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "payload": dict(payload),
        }
        path = root / RESULT_NAME
        write_json_atomic(path, envelope)
        return path

    def fingerprints(self, theory_id: str) -> List[str]:
        """Every fingerprint with a directory for ``theory_id``."""
        base = self.base_dir / safe_segment(theory_id, "theory id")
        if not base.is_dir():
            return []
        return sorted(p.name for p in base.iterdir()
                      if p.is_dir() and _plain(p.name))

    def stale_fingerprints(self, theory_id: str,
                           fingerprint: str) -> List[str]:
        """Fingerprints other than the current one (their results are stale)."""
        return [fp for fp in self.fingerprints(theory_id) if fp != fingerprint]

    def invalidate(self, theory_id: str, fingerprint: str) -> List[Path]:
        """Remove every fingerprint directory except ``fingerprint``'s."""
        removed = []
        for stale in self.stale_fingerprints(theory_id, fingerprint):
            path = self.base_dir / theory_id / safe_segment(stale, "fingerprint")
            shutil.rmtree(path)
            removed.append(path)
        return removed

    def stats(self) -> Dict[str, int]:
        with self._lock:
            return {"hits": self.hits, "misses": self.misses}
