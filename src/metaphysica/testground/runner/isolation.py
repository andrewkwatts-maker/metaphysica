"""Isolation: one scratch root per configuration, stamped with what it holds.

Every full run writes into ``<base>/<theory>/<fingerprint>/<digest>/`` and
nowhere else. Before the run, the root receives ``configuration.json`` -- the
selection, its digest, the engine fingerprint, the environment that forces it,
and when it was created. A signal that reads an artifact compares the digest in
this stamp with the configuration it is measuring; a mismatch is UNMEASURED,
never a stale number (D-019 kill condition K4).

Each path component is checked to be a plain name, and the resolved root is
checked to lie inside the base directory, so nothing here can touch a path
outside it.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.signals.model import SignalContext
from metaphysica.testground.theory import Theory

__all__ = [
    "STAMP_NAME",
    "STAMP_VERSION",
    "safe_segment",
    "root_for",
    "stamp_payload",
    "write_json_atomic",
    "prepare_root",
    "read_stamp",
    "stamp_digest",
    "stamp_fingerprint",
    "stamped_context",
]

PathLike = Union[str, Path]

STAMP_NAME = "configuration.json"
STAMP_VERSION = 1

_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def safe_segment(value: str, what: str) -> str:
    """Return ``value`` if it is a plain path component, else raise."""
    if not isinstance(value, str) or not _SEGMENT.match(value) or ".." in value:
        raise ValueError("%s %r is not a plain path component" % (what, value))
    return value


_EXT_PREFIX = chr(92) * 2 + "?" + chr(92)      # the extended-length prefix
_EXT_UNC = _EXT_PREFIX + "UNC" + chr(92)


def _plain(path: Path) -> Path:
    """``path.resolve()`` without the Windows extended-length prefix.

    ``resolve`` returns the prefixed form for a path whose parents another
    thread is creating at that moment, and the plain form once they exist, so
    two resolutions of the same tree could fail ``is_relative_to``.
    """
    resolved = path.resolve()
    text = str(resolved)
    if text.startswith(_EXT_UNC):
        return Path(chr(92) * 2 + text[len(_EXT_UNC):])
    if text.startswith(_EXT_PREFIX):
        return Path(text[len(_EXT_PREFIX):])
    return resolved


def _inside(base: Path, path: Path) -> Path:
    """Resolve ``path`` and refuse it unless it lies within ``base``."""
    resolved = _plain(path)
    if not resolved.is_relative_to(_plain(base)):
        raise ValueError("%s is outside the run base %s" % (resolved, base))
    return resolved


def root_for(base_dir: PathLike, theory_id: str, digest: str,
             fingerprint: str) -> Path:
    """``<base>/<theory>/<fingerprint>/<digest>``, checked to stay in base."""
    base = Path(base_dir)
    path = (base / safe_segment(theory_id, "theory id")
            / safe_segment(fingerprint, "fingerprint")
            / safe_segment(digest, "digest"))
    return _inside(base, path)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp_payload(theory: Theory, cfg: Configuration,
                  fingerprint: str) -> Dict[str, Any]:
    """The stamp contents (valid against configuration.schema.json)."""
    return {
        "stamp_version": STAMP_VERSION,
        "theory": cfg.theory,
        "name": cfg.name,
        "selection": cfg.mapping,
        "digest": cfg.digest,
        "lifecycle": cfg.lifecycle,
        "not_runnable": cfg.not_runnable,
        "decided_by": {fork: list(ids) for fork, ids in cfg.decided_by},
        "engine_fingerprint": fingerprint,
        "env": theory.env_for(cfg.mapping),
        "created": _utc_now(),
    }


def write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    """Write JSON through a temp file and ``os.replace`` (never half-written)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", suffix=".json",
                               dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, default=str)
            handle.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def prepare_root(base_dir: PathLike, theory: Theory, cfg: Configuration,
                 fingerprint: str, *, fresh: bool = True) -> Path:
    """Create (and by default empty) the configuration's root, then stamp it."""
    if cfg.theory != theory.id:
        raise ValueError("configuration belongs to theory %r, not %r"
                         % (cfg.theory, theory.id))
    root = root_for(base_dir, theory.id, cfg.digest, fingerprint)
    if fresh and root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    write_json_atomic(root / STAMP_NAME, stamp_payload(theory, cfg, fingerprint))
    return root


def read_stamp(root: PathLike) -> Optional[Dict[str, Any]]:
    """The stamp in ``root``, or None if it is missing or unreadable."""
    path = Path(root) / STAMP_NAME
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def stamp_digest(root: PathLike) -> Optional[str]:
    """The configuration digest recorded in ``root``'s stamp (None if absent)."""
    stamp = read_stamp(root)
    value = stamp.get("digest") if stamp else None
    return value if isinstance(value, str) else None


def stamp_fingerprint(root: PathLike) -> Optional[str]:
    """The engine fingerprint recorded in ``root``'s stamp (None if absent)."""
    stamp = read_stamp(root)
    value = stamp.get("engine_fingerprint") if stamp else None
    return value if isinstance(value, str) else None


def stamped_context(cfg: Configuration,
                    root: Optional[PathLike] = None) -> SignalContext:
    """A SignalContext for ``cfg``, carrying ``root``'s stamp if there is one."""
    path = Path(root) if root is not None else None
    return SignalContext(
        theory=cfg.theory,
        digest=cfg.digest,
        selection=cfg.selection,
        root=path,
        stamp_digest=stamp_digest(path) if path is not None else None,
    )
