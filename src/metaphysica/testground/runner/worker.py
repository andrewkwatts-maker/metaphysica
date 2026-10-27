"""Worker: one configuration's full run, stage by stage, in fresh processes.

The theory's pipeline stages run as subprocesses with ``cwd`` = the
configuration's isolated root and ``env`` = the current environment plus
``theory.env_for(selection)``. Nothing else is added: in particular this
module never sets ``METAPHYSICA_OUT`` -- a theory whose stages need it
declares it in the stage command itself. A caller may instead name inherited
variables to drop (``unset_env``), so a global output path set in the parent
shell cannot leak into an isolated run.

Each stage's exit code, wall time and stdout/stderr tails go to
``root/run_log.json`` (full logs in ``root/run_logs/``). A stage that cannot
start, exits with an untolerated code or exceeds its timeout stops the run and
marks the configuration NOT_RUNNABLE with the reason; a cancelled run is
CANCELLED, which says nothing about the configuration and is never cached.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from metaphysica.testground.assessment.score import NOT_RUNNABLE
from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.runner.cache import RunCache
from metaphysica.testground.runner.isolation import (
    prepare_root,
    stamp_digest,
    stamp_fingerprint,
    write_json_atomic,
)
from metaphysica.testground.theory import Stage, Theory

__all__ = [
    "COMPLETED",
    "COMPLETED_WITH_FAILURES",
    "NOT_RUNNABLE",
    "CANCELLED",
    "RUN_LOG_NAME",
    "LOG_DIR",
    "StageResult",
    "RunResult",
    "stage_env",
    "run_stage",
    "run_full",
    "run_configuration",
]

PathLike = Union[str, Path]

COMPLETED = "COMPLETED"
COMPLETED_WITH_FAILURES = "COMPLETED_WITH_FAILURES"
CANCELLED = "CANCELLED"
RUN_LOG_NAME = "run_log.json"
LOG_DIR = "run_logs"
TAIL_CHARS = 4000
_POLL_S = 0.1
_REAP_S = 30.0
_UNSAFE = re.compile(r"[^A-Za-z0-9_.-]+")


@dataclass(frozen=True)
class StageResult:
    """What one stage did."""

    id: str
    kind: str
    command: Tuple[str, ...]
    exit_code: Optional[int]
    tolerated_exit_codes: Tuple[int, ...]
    timeout_s: Optional[float]
    wall_s: float
    timed_out: bool = False
    cancelled: bool = False
    stdout_tail: str = ""
    stderr_tail: str = ""
    error: str = ""

    @property
    def ok(self) -> bool:
        return (not self.error and not self.timed_out and not self.cancelled
                and self.exit_code in self.tolerated_exit_codes)

    def failure_reason(self) -> str:
        """Why the stage stopped the run ("" when it did not)."""
        if self.error:
            return "stage %s could not start: %s" % (self.id, self.error)
        if self.cancelled:
            return "stage %s cancelled" % self.id
        if self.timed_out:
            return "stage %s timed out after %ss" % (self.id, self.timeout_s)
        if not self.ok:
            return "stage %s exited %s (tolerated: %s)" % (
                self.id, self.exit_code, list(self.tolerated_exit_codes))
        return ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["command"] = list(self.command)
        data["tolerated_exit_codes"] = list(self.tolerated_exit_codes)
        data["ok"] = self.ok
        return data

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "StageResult":
        fields = {k: v for k, v in data.items() if k != "ok"}
        fields["command"] = tuple(fields.get("command", ()))
        fields["tolerated_exit_codes"] = tuple(
            fields.get("tolerated_exit_codes", ()))
        return cls(**fields)


@dataclass(frozen=True)
class RunResult:
    """One configuration's full run."""

    theory: str
    digest: str
    root: str
    status: str
    reason: str = ""
    stages: Tuple[StageResult, ...] = ()
    wall_s: float = 0.0
    fingerprint: Optional[str] = None
    cached: bool = field(default=False, compare=False)

    @property
    def completed(self) -> bool:
        return self.status == COMPLETED

    @property
    def has_rows(self) -> bool:
        """True when the run wrote its rows (also with failed steps)."""
        return self.status in (COMPLETED, COMPLETED_WITH_FAILURES)

    @property
    def timed_out(self) -> bool:
        return any(stage.timed_out for stage in self.stages)

    @property
    def cacheable(self) -> bool:
        """Only verdicts about the configuration; never timeouts/cancels."""
        return (self.status in (COMPLETED, COMPLETED_WITH_FAILURES, NOT_RUNNABLE)
                and not self.timed_out)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theory": self.theory,
            "digest": self.digest,
            "root": self.root,
            "status": self.status,
            "reason": self.reason,
            "stages": [stage.to_dict() for stage in self.stages],
            "wall_s": self.wall_s,
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any],
                  cached: bool = False) -> "RunResult":
        return cls(
            theory=data["theory"], digest=data["digest"], root=data["root"],
            status=data["status"], reason=data.get("reason", ""),
            stages=tuple(StageResult.from_dict(s)
                         for s in data.get("stages", ())),
            wall_s=data.get("wall_s", 0.0),
            fingerprint=data.get("fingerprint"), cached=cached)


def stage_env(theory: Theory, cfg: Configuration,
              unset_env: Sequence[str] = ()) -> Dict[str, str]:
    """The current environment (minus ``unset_env``) plus ``cfg``'s variables."""
    env = dict(os.environ)
    for name in unset_env:
        env.pop(name, None)
    env.update(theory.env_for(cfg.mapping))
    return env


def _log_paths(root: Path, index: int, stage_id: str) -> Tuple[Path, Path]:
    logs = root / LOG_DIR
    logs.mkdir(parents=True, exist_ok=True)
    stem = "%02d-%s" % (index, _UNSAFE.sub("_", stage_id) or "stage")
    return logs / (stem + ".stdout.log"), logs / (stem + ".stderr.log")


def _tail(path: Path, chars: int) -> str:
    try:
        with open(path, "rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - 4 * chars))
            text = handle.read().decode("utf-8", errors="replace")
    except OSError:
        return ""
    return text[-chars:] if chars > 0 else ""


def _group_kwargs() -> Dict[str, Any]:
    """Start the stage in its own process group, so the tree can be killed."""
    if sys.platform == "win32":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}  # pragma: no cover - POSIX


def _kill_tree(proc: subprocess.Popen) -> None:
    """Kill the stage and everything it started."""
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=False)
    else:  # pragma: no cover - POSIX
        import signal
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    if proc.poll() is None:
        proc.kill()
    try:
        proc.wait(timeout=_REAP_S)
    except subprocess.TimeoutExpired:  # pragma: no cover - defensive
        pass


def _wait(proc: subprocess.Popen, limit: Optional[float],
          cancel: Optional[threading.Event]) -> Tuple[bool, bool]:
    """Wait for the stage; returns (timed_out, cancelled)."""
    deadline = None if limit is None else time.monotonic() + limit
    while True:
        slice_s = _POLL_S if deadline is None else max(
            0.0, min(_POLL_S, deadline - time.monotonic()))
        try:
            proc.wait(timeout=slice_s)
            return False, False
        except subprocess.TimeoutExpired:
            pass
        if cancel is not None and cancel.is_set():
            _kill_tree(proc)
            return False, True
        if deadline is not None and time.monotonic() >= deadline:
            _kill_tree(proc)
            return True, False


def run_stage(stage: Stage, root: Path, env: Mapping[str, str], index: int = 0,
              default_timeout: Optional[float] = None,
              cancel: Optional[threading.Event] = None,
              tail_chars: int = TAIL_CHARS) -> StageResult:
    """Run one stage in a fresh process with ``cwd=root``."""
    limit = stage.timeout_s if stage.timeout_s is not None else default_timeout
    out_path, err_path = _log_paths(root, index, stage.id)
    common = dict(id=stage.id, kind=stage.kind, command=tuple(stage.command),
                  tolerated_exit_codes=tuple(stage.tolerated_exit_codes),
                  timeout_s=limit)
    started = time.perf_counter()
    try:
        with open(out_path, "wb") as out, open(err_path, "wb") as err:
            proc = subprocess.Popen(
                list(stage.command), cwd=str(root), env=dict(env),
                stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                **_group_kwargs())
            timed_out, cancelled = _wait(proc, limit, cancel)
    except (OSError, ValueError) as exc:
        return StageResult(exit_code=None, wall_s=time.perf_counter() - started,
                           error="%s: %s" % (type(exc).__name__, exc), **common)
    return StageResult(
        exit_code=proc.returncode, wall_s=time.perf_counter() - started,
        timed_out=timed_out, cancelled=cancelled,
        stdout_tail=_tail(out_path, tail_chars),
        stderr_tail=_tail(err_path, tail_chars), **common)


def _wrote_rows(stage: Stage, result: StageResult, root: Path) -> bool:
    """True for a stage that exited untolerated but, by the theory's own
    ``rows_written`` test, wrote its rows first (never for a crash to start,
    a timeout or a cancel)."""
    if stage.rows_written is None or result.error or result.timed_out             or result.cancelled or result.exit_code is None:
        return False
    return bool(stage.rows_written(root))


def _outcome(stages: List[StageResult],
             declared: Sequence[Stage] = (),
             root: Optional[Path] = None) -> Tuple[str, str]:
    failed = next((s for s in stages if not s.ok), None)
    if failed is None:
        return COMPLETED, ""
    stage = next((d for d in declared if d.id == failed.id), None)
    if stage is not None and root is not None             and _wrote_rows(stage, failed, root):
        return COMPLETED_WITH_FAILURES, failed.failure_reason()
    status = CANCELLED if failed.cancelled else NOT_RUNNABLE
    return status, failed.failure_reason()


def _finish(theory: Theory, cfg: Configuration, root: Path, status: str,
            reason: str, stages: List[StageResult],
            started: float) -> RunResult:
    result = RunResult(
        theory=theory.id, digest=cfg.digest, root=str(root), status=status,
        reason=reason, stages=tuple(stages),
        wall_s=time.perf_counter() - started,
        fingerprint=stamp_fingerprint(root))
    write_json_atomic(root / RUN_LOG_NAME, result.to_dict())
    return result


def run_full(theory: Theory, cfg: Configuration, root: PathLike,
             timeout: Optional[float] = None, *,
             cancel: Optional[threading.Event] = None,
             tail_chars: int = TAIL_CHARS,
             unset_env: Sequence[str] = ()) -> RunResult:
    """Run every pipeline stage for ``cfg`` in ``root`` (prepared and stamped).

    ``timeout`` applies per stage, unless the stage declares its own.
    """
    root = Path(root)
    if stamp_digest(root) != cfg.digest:
        raise ValueError("%s is not stamped for configuration %s; call "
                         "prepare_root first" % (root, cfg.digest))
    started = time.perf_counter()
    if cfg.not_runnable:
        why = "; ".join(cfg.reasons) or "declared not runnable"
        return _finish(theory, cfg, root, NOT_RUNNABLE,
                       "configuration is not runnable: " + why, [], started)
    env = stage_env(theory, cfg, unset_env)
    stages: List[StageResult] = []
    declared = list(theory.pipeline.stages())
    for index, stage in enumerate(declared):
        result = run_stage(stage, root, env, index, timeout, cancel, tail_chars)
        stages.append(result)
        if not result.ok:
            break
    status, reason = _outcome(stages, declared, root)
    return _finish(theory, cfg, root, status, reason, stages, started)


def run_configuration(theory: Theory, cfg: Configuration, base_dir: PathLike,
                      fingerprint: str, timeout: Optional[float] = None, *,
                      cache: Optional[RunCache] = None, refresh: bool = False,
                      cancel: Optional[threading.Event] = None,
                      unset_env: Sequence[str] = ()) -> RunResult:
    """Isolate, run and cache one configuration (a cache hit skips the run)."""
    if cache is not None and cache.base_dir.resolve() != Path(base_dir).resolve():
        raise ValueError("the cache lives in %s but the run base is %s"
                         % (cache.base_dir, base_dir))
    if cache is not None and not refresh:
        payload = cache.get(theory.id, cfg.digest, fingerprint)
        if payload is not None:
            return RunResult.from_dict(payload, cached=True)
    root = prepare_root(base_dir, theory, cfg, fingerprint, fresh=True)
    result = run_full(theory, cfg, root, timeout, cancel=cancel,
                      unset_env=unset_env)
    if cache is not None and result.cacheable:
        cache.put(theory.id, cfg.digest, fingerprint, result.to_dict())
    return result
