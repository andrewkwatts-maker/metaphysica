"""Engine fingerprint: one short hash that changes when the code that computes changes.

A cached run is only reusable while the code that produced it is unchanged.
The fingerprint is a sha256 over every ``*.py`` file under the given source
roots (relative path + content, sorted, line endings normalised so a checkout
with CRLF hashes like one with LF) plus the versions of the key dependencies
and the Python version. It is a pure function of those inputs, so it is stable
across runs and across machines with the same code and dependencies.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import hashlib
import sys
from importlib import metadata
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Sequence, Tuple, Union

__all__ = [
    "DEFAULT_DEPENDENCIES",
    "DEFAULT_PATTERNS",
    "FINGERPRINT_LENGTH",
    "engine_roots",
    "source_files",
    "dependency_versions",
    "fingerprint_manifest",
    "engine_fingerprint",
]

PathLike = Union[str, Path]

#: Distributions whose version can change a computed number.
DEFAULT_DEPENDENCIES: Tuple[str, ...] = (
    "numpy", "scipy", "sympy", "mpmath", "eml-math", "PyYAML")
DEFAULT_PATTERNS: Tuple[str, ...] = ("*.py",)
#: Hex characters kept; matches the configuration digest length.
FINGERPRINT_LENGTH = 16

_SKIPPED_PARTS = ("__pycache__",)


def engine_roots() -> List[Path]:
    """The engine's own package directory (``src/metaphysica``)."""
    return [Path(__file__).resolve().parents[2]]


def _skipped(relative: Path) -> bool:
    """Caches and hidden directories never take part in the hash."""
    return any(part in _SKIPPED_PARTS or part.startswith(".")
               for part in relative.parts[:-1])


def source_files(root: PathLike,
                 patterns: Sequence[str] = DEFAULT_PATTERNS) -> List[Path]:
    """Files under ``root`` matching ``patterns``, sorted by relative path."""
    base = Path(root)
    found = set()
    for pattern in patterns:
        for path in base.rglob(pattern):
            if path.is_file() and not _skipped(path.relative_to(base)):
                found.add(path)
    return sorted(found, key=lambda p: p.relative_to(base).as_posix())


def dependency_versions(names: Sequence[str] = DEFAULT_DEPENDENCIES
                        ) -> Dict[str, str]:
    """name -> installed version ("absent" when not installed)."""
    versions = {}
    for name in sorted(names, key=str.lower):
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = "absent"
    return versions


def _normalised_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def _ordered_roots(roots: Iterable[PathLike]) -> List[Path]:
    """Distinct roots, sorted, so the argument order does not matter."""
    unique = {Path(r).resolve() for r in roots}
    return sorted(unique, key=lambda p: (p.name, p.as_posix()))


def _file_records(roots: Iterable[PathLike],
                  patterns: Sequence[str]) -> Iterator[Tuple[str, bytes]]:
    """(label, content) per file; the label is root name + relative path."""
    for root in _ordered_roots(roots):
        for path in source_files(root, patterns):
            label = "%s/%s" % (root.name, path.relative_to(root).as_posix())
            yield label, _normalised_bytes(path)


def _python_version() -> str:
    return "%s-%d.%d.%d" % ((sys.implementation.name,) + sys.version_info[:3])


def fingerprint_manifest(roots: Iterable[PathLike],
                         dependencies: Sequence[str] = DEFAULT_DEPENDENCIES,
                         patterns: Sequence[str] = DEFAULT_PATTERNS
                         ) -> Dict[str, object]:
    """What went into the fingerprint, for a report or a debugging diff."""
    files = {label: hashlib.sha256(data).hexdigest()
             for label, data in _file_records(roots, patterns)}
    return {
        "files": files,
        "dependencies": dependency_versions(dependencies),
        "python": _python_version(),
        "patterns": list(patterns),
    }


def engine_fingerprint(roots: Iterable[PathLike] = (),
                       dependencies: Sequence[str] = DEFAULT_DEPENDENCIES,
                       patterns: Sequence[str] = DEFAULT_PATTERNS,
                       length: int = FINGERPRINT_LENGTH) -> str:
    """sha256 over the sorted sources of ``roots`` plus dependency versions.

    With no roots, the engine's own package directory is hashed.
    """
    roots = list(roots) or engine_roots()
    digest = hashlib.sha256()
    for label, data in _file_records(roots, patterns):
        digest.update(b"file\0" + label.encode("utf-8") + b"\0")
        digest.update(hashlib.sha256(data).digest())
    for name, version in dependency_versions(dependencies).items():
        digest.update(("dep\0%s\0%s\0" % (name, version)).encode("utf-8"))
    digest.update(("python\0%s" % _python_version()).encode("utf-8"))
    return digest.hexdigest()[:length]
