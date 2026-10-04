"""The YAML selection store: the adopted selection and the named configurations.

Two files, both hand-readable and both written atomically (a temporary file in
the same directory, flushed and fsynced, then ``os.replace``), so a failed
write leaves the old file byte-identical and never a half-written one.

``active.yaml``::

    theory: toy
    name: adopted-2026-10-02
    selection: {fork_a: option_1, fork_b: option_2}
    decided_by: {fork_a: [D-015]}
    digest: 0123456789abcdef        # digest_of(selection); verified on load
    data_tiebreak_dof: 0            # fitted dof added by data tie-breaks
    decision: D-015                 # the decision that wrote this state
    note: ...
    updated: 2026-10-02T00:00:00+00:00
    previous: [...]                 # every earlier active state, oldest first

``configurations.yaml``::

    theory: toy
    configurations:
      previous-active-2026-10-02:   # a fixed selection
        selection: {fork_a: option_0, fork_b: option_2}
        digest: ...                 # optional; verified when present
      probe-b:                      # relative: base (default "active") + overrides
        base: active
        overrides: {fork_b: option_3}
        note: ...

Load rules: the digest must match; values must be strings (quote YAML-ish
ids); with ``forks`` supplied, every fork and option must be declared, the
active selection may not use a DISABLED option, and a fork the selection
predates is filled from its ``legacy_option`` (an active selection without one
is an error; a named one falls back to its base, with a reason recorded).
The store never deletes: a write appends the replaced state to ``previous`` and
named configurations are only added (or replaced on explicit request).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import copy
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import (Any, Callable, Dict, List, Mapping, Optional, Tuple,
                    Union)

import yaml

from metaphysica.testground.configurations.model import (
    ACTIVE,
    CONSIDERED,
    Configuration,
    digest_of,
)
from metaphysica.testground.switches.model import DISABLED, Fork
from metaphysica.testground.switches.resolve import ACTIVE_ALIAS

__all__ = [
    "StoreError",
    "DigestMismatchError",
    "atomic_write_text",
    "YamlSelectionStore",
]

ForksSource = Union[Mapping[str, Fork], Callable[[], Mapping[str, Fork]]]

_ACTIVE_HEADER = (
    "# The adopted selection. Change it through `accept`, which records a\n"
    "# decision; the digest is verified on load.\n")
_NAMED_HEADER = (
    "# Named configurations: a fixed selection, or a base plus overrides.\n")


class StoreError(ValueError):
    """The store's files are missing, malformed or inconsistent."""


class DigestMismatchError(StoreError):
    """The recorded digest is not the digest of the recorded selection."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def atomic_write_text(path: Union[str, Path], text: str) -> None:
    """Write ``text`` to ``path`` atomically (temp file + ``os.replace``)."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + target.name + ".",
                               suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def _render(header: str, doc: Mapping[str, Any]) -> str:
    return header + yaml.safe_dump(dict(doc), sort_keys=False,
                                   default_flow_style=False,
                                   allow_unicode=True, width=88)


# ------------------------------------------------------------ field checks


def _str_map(value: Any, what: str) -> Dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise StoreError("%s must be a mapping, not %s"
                         % (what, type(value).__name__))
    for key, item in value.items():
        if not isinstance(key, str) or not isinstance(item, str):
            raise StoreError("%s: %r: %r must map strings to strings (quote "
                             "ids YAML would read as other types)"
                             % (what, key, item))
    return dict(value)


def _decided_by(value: Any, what: str) -> Dict[str, Tuple[str, ...]]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise StoreError("%s.decided_by must be a mapping" % what)
    out: Dict[str, Tuple[str, ...]] = {}
    for fork_id, ids in value.items():
        if (not isinstance(fork_id, str) or not isinstance(ids, list)
                or not all(isinstance(i, str) for i in ids)):
            raise StoreError("%s.decided_by.%s must be a list of decision "
                             "ids" % (what, fork_id))
        out[fork_id] = tuple(ids)
    return out


def _verify_digest(selection: Mapping[str, str], recorded: Any,
                   what: str) -> None:
    actual = digest_of(selection)
    if recorded != actual:
        raise DigestMismatchError(
            "%s: recorded digest %r is not the digest of its selection (%s) "
            "-- the selection was edited without re-recording, or the digest "
            "was" % (what, recorded, actual))


class YamlSelectionStore:
    """A `SelectionStore` backed by ``active.yaml`` and ``configurations.yaml``."""

    def __init__(self, active_path: Union[str, Path],
                 named_path: Optional[Union[str, Path]] = None,
                 forks: Optional[ForksSource] = None,
                 theory_id: Optional[str] = None) -> None:
        self.active_path = Path(active_path)
        self.named_path = Path(named_path) if named_path is not None else None
        self._forks_source = forks
        self.theory_id = theory_id
        self._parsed: Dict[Path, Tuple[bytes, Any]] = {}

    # ----------------------------------------------------------- reading

    def _forks(self) -> Optional[Mapping[str, Fork]]:
        source = self._forks_source
        return source() if callable(source) else source

    def _read(self, path: Path, missing_ok: bool = False) -> Any:
        """Parsed YAML of ``path``, re-parsed only when its bytes change."""
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            if missing_ok:
                return None
            raise StoreError("no selection store file at %s" % path) from None
        cached = self._parsed.get(path)
        if cached is not None and cached[0] == raw:
            return cached[1]
        try:
            data = yaml.safe_load(raw.decode("utf-8"))
        except (yaml.YAMLError, UnicodeDecodeError) as exc:
            raise StoreError("%s is not readable YAML: %s" % (path, exc)) \
                from exc
        self._parsed[path] = (raw, data)
        return data

    def _check_options(self, selection: Mapping[str, str], what: str,
                       allow_disabled: bool) -> None:
        forks = self._forks()
        if forks is None:
            return
        for fork_id, option_id in selection.items():
            if fork_id not in forks:
                raise StoreError("%s names undeclared fork %r"
                                 % (what, fork_id))
            if option_id not in forks[fork_id].option_ids():
                raise StoreError("%s: fork %r has no option %r (declared: %s)"
                                 % (what, fork_id, option_id,
                                    forks[fork_id].option_ids()))
            option = forks[fork_id].option(option_id)
            if option.status == DISABLED and not allow_disabled:
                raise StoreError(
                    "%s selects DISABLED option %s=%s; reinstate it (a "
                    "recorded decision) before it can be active"
                    % (what, fork_id, option_id))

    def _extend(self, selection: Dict[str, str], what: str,
                base: Optional[Mapping[str, str]],
                ) -> Tuple[Dict[str, str], Tuple[str, ...]]:
        """Fill forks the selection predates: legacy option, else ``base``."""
        forks = self._forks()
        if forks is None:
            return selection, ()
        out = dict(selection)
        notes: List[str] = []
        for fork_id, fork in forks.items():
            if fork_id in out:
                continue
            if fork.legacy_option is not None:
                out[fork_id] = fork.legacy_option
                notes.append("%s absent from %s; extended with its legacy "
                             "option %s" % (fork_id, what, fork.legacy_option))
            elif base is not None and fork_id in base:
                out[fork_id] = base[fork_id]
                notes.append("%s absent from %s; extended with the active "
                             "option %s" % (fork_id, what, base[fork_id]))
            else:
                raise StoreError("%s names no option for fork %r, which "
                                 "declares no legacy_option" % (what, fork_id))
        return out, tuple(notes)

    def _validate_active(self, doc: Any, what: str) -> Dict[str, Any]:
        """``doc`` checked as an ``active.yaml`` (structure and digest)."""
        if not isinstance(doc, Mapping):
            raise StoreError("%s must be a mapping" % what)
        theory = doc.get("theory")
        if not isinstance(theory, str) or not theory:
            raise StoreError("%s: 'theory' must be a non-empty string" % what)
        if self.theory_id is not None and theory != self.theory_id:
            raise StoreError("%s belongs to theory %r, not %r"
                             % (what, theory, self.theory_id))
        name = doc.get("name")
        if name is not None and not isinstance(name, str):
            raise StoreError("%s: 'name' must be a string" % what)
        if "selection" not in doc:
            raise StoreError("%s has no 'selection'" % what)
        selection = _str_map(doc["selection"], what + ".selection")
        _verify_digest(selection, doc.get("digest"), what)
        decided = _decided_by(doc.get("decided_by"), what)
        stray = sorted(set(decided) - set(selection))
        if stray:
            raise StoreError("%s.decided_by names forks %s that the selection "
                             "does not" % (what, stray))
        dof = doc.get("data_tiebreak_dof", 0)
        if not isinstance(dof, int) or isinstance(dof, bool) or dof < 0:
            raise StoreError("%s: data_tiebreak_dof must be a non-negative "
                             "integer" % what)
        if not isinstance(doc.get("previous", []) or [], list):
            raise StoreError("%s: 'previous' must be a list" % what)
        return dict(doc)

    def _active_document(self) -> Dict[str, Any]:
        """The parsed, verified ``active.yaml``."""
        return self._validate_active(self._read(self.active_path),
                                     str(self.active_path))

    def document(self) -> Dict[str, Any]:
        """A copy of the verified ``active.yaml`` contents."""
        return copy.deepcopy(self._active_document())

    def active(self) -> Configuration:
        """The adopted configuration (lifecycle ACTIVE)."""
        doc = self._active_document()
        what = str(self.active_path)
        selection = _str_map(doc["selection"], what)
        full, notes = self._extend(selection, what, None)
        self._check_options(full, what, allow_disabled=False)
        return Configuration.of(
            doc["theory"], full, lifecycle=ACTIVE, name=doc.get("name"),
            not_runnable=self._uses_unimplemented(full),
            decided_by=tuple(sorted(
                _decided_by(doc.get("decided_by"), what).items())),
            reasons=notes)

    def _uses_unimplemented(self, selection: Mapping[str, str]) -> bool:
        forks = self._forks()
        return forks is not None and any(
            not forks[f].option(o).implemented for f, o in selection.items())

    def data_tiebreak_dof(self) -> int:
        """Fitted degrees of freedom added by accepting on a data tie-break."""
        return int(self._active_document().get("data_tiebreak_dof", 0))

    def previous(self) -> List[Dict[str, Any]]:
        """Every earlier active state, oldest first (copies)."""
        return copy.deepcopy(list(self._active_document().get("previous")
                                  or []))

    def _validate_named(self, doc: Any, what: str) -> Dict[str, Any]:
        """The entries of ``doc`` checked as a ``configurations.yaml``."""
        if doc is None:
            return {}
        if not isinstance(doc, Mapping):
            raise StoreError("%s must be a mapping" % what)
        theory = doc.get("theory")
        expected = self.theory_id or self._active_document()["theory"]
        if theory is not None and theory != expected:
            raise StoreError("%s belongs to theory %r, not %r"
                             % (what, theory, expected))
        entries = doc.get("configurations") or {}
        if not isinstance(entries, Mapping):
            raise StoreError("%s: 'configurations' must be a mapping" % what)
        if ACTIVE_ALIAS in entries:
            raise StoreError("%s: %r is reserved for the active configuration"
                             % (what, ACTIVE_ALIAS))
        return dict(entries)

    def _named_entries(self) -> Dict[str, Any]:
        if self.named_path is None:
            return {}
        return self._validate_named(
            self._read(self.named_path, missing_ok=True), str(self.named_path))

    def named_document(self) -> Dict[str, Any]:
        """A copy of the raw named entries (notes included)."""
        return copy.deepcopy(self._named_entries())

    def _resolve_named(self, name: str, entries: Mapping[str, Any],
                       active: Mapping[str, str], stack: Tuple[str, ...],
                       ) -> Dict[str, str]:
        """The selection a named entry denotes (bases resolved recursively)."""
        what = "%s:%s" % (self.named_path, name)
        if name in stack:
            raise StoreError("%s: base cycle %s"
                             % (what, " -> ".join(stack + (name,))))
        entry = entries.get(name)
        if not isinstance(entry, Mapping):
            raise StoreError("%s is not a mapping (or does not exist)" % what)
        if "selection" in entry and "base" in entry:
            raise StoreError("%s has both 'selection' and 'base'" % what)
        if "selection" in entry:
            start = _str_map(entry["selection"], what + ".selection")
        else:
            base = entry.get("base", ACTIVE_ALIAS)
            start = (dict(active) if base == ACTIVE_ALIAS else
                     self._resolve_named(base, entries, active,
                                         stack + (name,)))
        start.update(_str_map(entry.get("overrides"), what + ".overrides"))
        return start

    def _build_named(self, entries: Mapping[str, Any],
                     ) -> Dict[str, Configuration]:
        if not entries:
            return {}
        theory = self._active_document()["theory"]
        active = self.active().mapping
        out: Dict[str, Configuration] = {}
        for name in sorted(entries):
            what = "%s:%s" % (self.named_path, name)
            selection = self._resolve_named(name, entries, active, ())
            self._check_options(selection, what, allow_disabled=True)
            if "digest" in entries[name]:
                _verify_digest(selection, entries[name]["digest"], what)
            full, notes = self._extend(selection, what, active)
            out[name] = Configuration.of(
                theory, full, lifecycle=CONSIDERED, name=name,
                not_runnable=self._uses_unimplemented(full),
                decided_by=tuple(sorted(_decided_by(
                    entries[name].get("decided_by"), what).items())),
                reasons=notes)
        return out

    def named(self) -> Dict[str, Configuration]:
        """Every named configuration, resolved to a full Configuration."""
        return self._build_named(self._named_entries())

    # ----------------------------------------------------------- writing

    def _complete(self, selection: Mapping[str, str], what: str) -> None:
        forks = self._forks()
        missing = sorted(set(forks or ()) - set(selection))
        if missing:
            raise StoreError("%s names no option for forks %s"
                             % (what, missing))

    def _merged_decisions(self, selection: Mapping[str, str],
                          old: Optional[Mapping[str, Any]], decision_id: str,
                          cfg: Configuration) -> Dict[str, List[str]]:
        """Changed forks are decided by ``decision_id``; unchanged forks keep
        their record; the configuration's own record is unioned in."""
        old_sel = dict((old or {}).get("selection") or {})
        old_db = _decided_by((old or {}).get("decided_by"), "previous")
        given = dict(cfg.decided_by)
        out: Dict[str, List[str]] = {}
        for fork_id in sorted(selection):
            unchanged = old_sel.get(fork_id) == selection[fork_id]
            ids = list(old_db.get(fork_id, ())) if unchanged else [decision_id]
            for extra in given.get(fork_id, ()):
                if extra not in ids:
                    ids.append(extra)
            if ids:
                out[fork_id] = ids
        return out

    @staticmethod
    def _history_entry(old: Mapping[str, Any],
                       decision_id: str) -> Dict[str, Any]:
        entry = {key: copy.deepcopy(old[key])
                 for key in ("name", "selection", "digest", "decided_by",
                             "data_tiebreak_dof", "decision", "note",
                             "updated")
                 if key in old}
        entry["superseded_by"] = decision_id
        entry["superseded_on"] = _now()
        return entry

    def write_active(self, cfg: Configuration, decision_id: str,
                     note: str = "", *, name: Optional[str] = None,
                     data_tiebreak_dof: Optional[int] = None) -> None:
        """Make ``cfg`` the active selection, recording ``decision_id``.

        The replaced state is appended to ``previous``; nothing is dropped.
        """
        if not decision_id or not isinstance(decision_id, str):
            raise StoreError("a decision id is required to change the active "
                             "selection")
        what = "active selection for %s" % self.active_path
        selection = cfg.mapping
        if self.theory_id is not None and cfg.theory != self.theory_id:
            raise StoreError("configuration of theory %r cannot be written to "
                             "a store of theory %r"
                             % (cfg.theory, self.theory_id))
        self._check_options(selection, what, allow_disabled=False)
        self._complete(selection, what)
        old = (self._active_document() if self.active_path.exists()
               else None)
        if old is not None and old["theory"] != cfg.theory:
            raise StoreError("%s holds theory %r, not %r"
                             % (self.active_path, old["theory"], cfg.theory))
        if data_tiebreak_dof is None:
            data_tiebreak_dof = int((old or {}).get("data_tiebreak_dof", 0))
        unchanged = old is not None and dict(old["selection"]) == selection
        doc: Dict[str, Any] = {
            "theory": cfg.theory,
            "name": (name or cfg.name
                     or ((old or {}).get("name") if unchanged else None)
                     or "active-" + _now()[:10]),
            "selection": dict(sorted(selection.items())),
            "decided_by": self._merged_decisions(selection, old, decision_id,
                                                 cfg),
            "digest": digest_of(selection),
            "data_tiebreak_dof": data_tiebreak_dof,
            "decision": decision_id,
            "note": note,
            "updated": _now(),
            "previous": (list(copy.deepcopy(old.get("previous") or []))
                         + [self._history_entry(old, decision_id)]
                         if old is not None else []),
        }
        text = _render(_ACTIVE_HEADER, doc)
        self._validate_active(yaml.safe_load(text), what)
        atomic_write_text(self.active_path, text)

    def write_named(self, name: str, cfg: Configuration, note: str = "", *,
                    replace: bool = False) -> None:
        """Record ``cfg`` as a fixed named configuration (never deletes one;
        an existing name is replaced only when ``replace`` is True)."""
        if self.named_path is None:
            raise StoreError("this store has no named-configurations file")
        if not name or not isinstance(name, str) or name == ACTIVE_ALIAS:
            raise StoreError("invalid configuration name %r" % (name,))
        what = "%s:%s" % (self.named_path, name)
        selection = cfg.mapping
        self._check_options(selection, what, allow_disabled=True)
        entries = copy.deepcopy(self._named_entries())   # refuses a bad file
        raw = self._read(self.named_path, missing_ok=True)
        doc = copy.deepcopy(dict(raw)) if raw is not None else {}
        doc.setdefault("theory", cfg.theory)
        if doc["theory"] != cfg.theory:
            raise StoreError("%s holds theory %r, not %r"
                             % (self.named_path, doc["theory"], cfg.theory))
        if name in entries and not replace:
            raise StoreError("%s already exists; pass replace=True to "
                             "overwrite it" % what)
        entry: Dict[str, Any] = {"selection": dict(sorted(selection.items())),
                                 "digest": digest_of(selection)}
        if cfg.decided_by:
            entry["decided_by"] = {f: list(ids) for f, ids in cfg.decided_by}
        if note:
            entry["note"] = note
        entry["written"] = _now()
        entries[name] = entry
        doc["configurations"] = entries
        text = _render(_NAMED_HEADER, doc)
        self._build_named(self._validate_named(yaml.safe_load(text), what))
        atomic_write_text(self.named_path, text)
