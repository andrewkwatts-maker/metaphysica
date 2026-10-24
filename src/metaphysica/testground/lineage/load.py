"""Load and validate a lineage catalogue; every check fails early.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, Tuple, Union

import yaml

from metaphysica.testground.lineage.model import (
    ACTIVE, OPTION_STATUSES, SCHEMA, VERSION_STATUSES, DeclaredFork,
    DeclaredOption, KeyResult, Lineage, Version)

__all__ = ["LineageError", "load_lineage", "parse_lineage"]

_ID = re.compile(r"^[a-z0-9_]+$")
_ERA = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")
_MAPS = re.compile(r"^[a-z0-9_]+\.[A-Za-z0-9_]+$")


class LineageError(ValueError):
    """The catalogue is invalid; the message names the file and the entry."""


def _need(where: str, data: Any, key: str) -> Any:
    if not isinstance(data, Mapping) or key not in data:
        raise LineageError("%s: missing %r" % (where, key))
    return data[key]


def _strs(where: str, value: Any) -> Tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)) or not all(
            isinstance(s, str) for s in value):
        raise LineageError("%s: expected a list of strings" % where)
    return tuple(value)


def _key_results(where: str, value: Any) -> Tuple[KeyResult, ...]:
    out = []
    for i, item in enumerate(value or ()):
        w = "%s/key_results/%d" % (where, i)
        out.append(KeyResult(str(_need(w, item, "quantity")),
                             str(_need(w, item, "value")),
                             str(_need(w, item, "source"))))
    return tuple(out)


def _considered(where: str, value: Any) -> Tuple[Mapping[str, Any], ...]:
    out = []
    for i, item in enumerate(value or ()):
        if not isinstance(item, Mapping) or "title" not in item:
            raise LineageError("%s/branches_considered/%d: needs a title"
                               % (where, i))
        out.append(dict(item))
    return tuple(out)


def _version(raw: Any, i: int) -> Version:
    where = "versions/%d" % i
    vid = _need(where, raw, "id")
    if not isinstance(vid, str) or not _ID.match(vid):
        raise LineageError("%s: id %r must match [a-z0-9_]+" % (where, vid))
    where = "version %s" % vid
    era, status = str(_need(where, raw, "era")), _need(where, raw, "status")
    if not _ERA.match(era):
        raise LineageError("%s: era %r is not YYYY-MM or YYYY-MM-DD"
                           % (where, era))
    if status not in VERSION_STATUSES:
        raise LineageError("%s: unknown status %r (expected %s)"
                           % (where, status, list(VERSION_STATUSES)))
    maps = _strs(where + "/maps_to", raw.get("maps_to"))
    for m in maps:
        if not _MAPS.match(m):
            raise LineageError("%s: maps_to %r is not fork.option"
                               % (where, m))
    return Version(
        id=vid, label=str(_need(where, raw, "label")), era=era, status=status,
        parent=raw.get("parent"), superseded_by=raw.get("superseded_by"),
        framing=str(raw.get("framing") or ""), why=str(raw.get("why") or ""),
        worked=_strs(where + "/worked", raw.get("worked")),
        failed=_strs(where + "/failed", raw.get("failed")),
        key_results=_key_results(where, raw.get("key_results")),
        evidence=_strs(where + "/evidence", raw.get("evidence")),
        maps_to=maps,
        branches_considered=_considered(where, raw.get("branches_considered")))


def _check_versions(versions: Sequence[Version]) -> None:
    ids = [v.id for v in versions]
    for vid in sorted({i for i in ids if ids.count(i) > 1}):
        raise LineageError("duplicate version id %r" % vid)
    known = set(ids)
    for v in versions:
        for field_name in ("parent", "superseded_by"):
            ref = getattr(v, field_name)
            if ref is not None and ref not in known:
                raise LineageError("version %s: unknown %s %r"
                                   % (v.id, field_name, ref))
    active = [v.id for v in versions if v.status == ACTIVE]
    if len(active) != 1:
        raise LineageError("exactly one version must be active, found %d %s"
                           % (len(active), active))
    _check_acyclic(versions)


def _check_acyclic(versions: Sequence[Version]) -> None:
    parent = {v.id: v.parent for v in versions}
    for start in parent:
        seen, node = {start}, parent[start]
        while node is not None:
            if node in seen:
                raise LineageError("parent cycle through version %r" % node)
            seen.add(node)
            node = parent[node]


def _fork(raw: Any, i: int) -> DeclaredFork:
    where = "forks/%d" % i
    fid = _need(where, raw, "id")
    if not isinstance(fid, str) or not _ID.match(fid):
        raise LineageError("%s: id %r must match [a-z0-9_]+" % (where, fid))
    return DeclaredFork(fid, str(_need(where, raw, "question")),
                        str(raw.get("source") or ""),
                        str(raw.get("notes") or ""))


def _option(raw: Any, i: int) -> DeclaredOption:
    where = "options/%d" % i
    fork, oid = _need(where, raw, "fork"), _need(where, raw, "id")
    status = raw.get("status", "considered")
    if status not in OPTION_STATUSES:
        raise LineageError("%s: unknown status %r (expected %s)"
                           % (where, status, list(OPTION_STATUSES)))
    return DeclaredOption(
        fork=str(fork), id=str(oid),
        summary=str(_need(where, raw, "summary")),
        consequence=str(raw.get("consequence") or ""), status=status,
        restored_from=str(raw.get("restored_from") or ""),
        source=str(raw.get("source") or ""),
        kill_condition=str(raw.get("kill_condition") or ""),
        decision_refs=_strs(where + "/decision_refs", raw.get("decision_refs")))


def _check_options(forks: Sequence[DeclaredFork],
                   options: Sequence[DeclaredOption],
                   known_forks: Iterable[str]) -> None:
    fork_ids = [f.id for f in forks]
    for fid in sorted({i for i in fork_ids if fork_ids.count(i) > 1}):
        raise LineageError("duplicate declared fork %r" % fid)
    allowed = set(fork_ids) | set(known_forks)
    seen = set()
    for o in options:
        if o.fork not in allowed:
            raise LineageError("option %s.%s: fork %r is not declared"
                               % (o.fork, o.id, o.fork))
        if (o.fork, o.id) in seen:
            raise LineageError("duplicate option %s.%s" % (o.fork, o.id))
        seen.add((o.fork, o.id))


def parse_lineage(data: Any, known_forks: Iterable[str] = ()) -> Lineage:
    """Validate a parsed catalogue. ``known_forks``: engine fork ids that
    declared options may attach to, besides the catalogue's own forks."""
    if not isinstance(data, Mapping) or data.get("schema") != SCHEMA:
        raise LineageError("schema must be %r" % SCHEMA)
    versions = tuple(_version(v, i)
                     for i, v in enumerate(data.get("versions") or ()))
    _check_versions(versions)
    forks = tuple(_fork(f, i) for i, f in enumerate(data.get("forks") or ()))
    options = tuple(_option(o, i)
                    for i, o in enumerate(data.get("options") or ()))
    _check_options(forks, options, known_forks)
    return Lineage(versions, forks, options, str(data.get("sources") or ""))


def load_lineage(path: Union[str, Path],
                 known_forks: Iterable[str] = ()) -> Lineage:
    """Read ``path`` (UTF-8 YAML) and validate it; raises LineageError."""
    path = Path(path)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise LineageError("%s: %s" % (path, exc)) from exc
    try:
        return parse_lineage(data, known_forks)
    except LineageError as exc:
        raise LineageError("%s: %s" % (path, exc)) from exc
