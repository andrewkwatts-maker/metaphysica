"""The test ground's command line: list, validate, assess, explain, accept,
retire, reinstate, export-graph, run.

    python -m metaphysica.testground <command> [--theory NAME] [options]

GOVERNANCE
==========
Only the D-019 comparator ranks. ``assess`` enumerates the valid
configurations, measures them, scores them by the decision rule and REPORTS
the comparator's verdict -- it never writes the selection store. Changing the
active path is a separate, explicit act: ``accept <target> --decision D-NNN``,
which records a decision. ``retire`` / ``reinstate`` likewise record one.

THEORIES
========
``--theory NAME`` is looked up through the theory registry
(``metaphysica.theories.get_theory``), imported by NAME at run time so the
test ground keeps no static dependency on theory code. ``--theory
package.module:ATTRIBUTE`` names a Theory (or a factory of one) directly.
Without ``--theory`` the registry's default is used.

DEPENDENCIES
============
Each command imports the modules it needs when it runs. A module that is not
there yet is reported as ``not yet available: <module>`` (exit 2), so every
other command keeps working.

EXIT CODES
==========
0 ok  ·  1 usage (bad arguments, unknown theory/target)  ·  2 refused (an
accept the rules refuse, a theory that fails validation, a run that failed,
a module not yet available).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import (Any, Callable, Dict, FrozenSet, Iterable, List, Mapping,
                    Optional, Sequence, Tuple)

from metaphysica.testground.assessment.score import (CRITERIA, CLOSURE,
                                                     DECIDING_CRITERIA,
                                                     CriterionScore,
                                                     ScoreVector)
from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.constraints import violations
from metaphysica.testground.signals.model import (ARTIFACT, FULL, LIVE,
                                                  SCREEN, Measurement)

__all__ = [
    "OK",
    "USAGE",
    "REFUSED",
    "REGISTRY",
    "COMMANDS",
    "UsageError",
    "Refused",
    "NotAvailable",
    "need",
    "load_theory",
    "resolve_target",
    "AssessmentRun",
    "run_assessment",
    "validate_theory",
    "build_parser",
    "main",
]

OK, USAGE, REFUSED = 0, 1, 2
#: The theory registry, imported by name at run time (never statically).
REGISTRY = "metaphysica.theories"
COMMANDS = ("list", "validate", "assess", "explain", "accept", "retire",
            "reinstate", "export-graph", "run")

_TG = "metaphysica.testground."
M_MODES = _TG + "configurations.modes"
M_ENUMERATE = _TG + "configurations.enumerate"
M_LIFECYCLE = _TG + "configurations.lifecycle"
M_SCREEN = _TG + "runner.screen"
M_POOL = _TG + "runner.pool"
M_WORKER = _TG + "runner.worker"
M_CACHE = _TG + "runner.cache"
M_FINGERPRINT = _TG + "runner.fingerprint"
M_CONFIG = _TG + "assessment.config"
M_CRITERIA = _TG + "assessment.criteria"
M_STANDING = _TG + "assessment.standing"
M_COMPARATOR = _TG + "assessment.comparator"
M_REPORT = _TG + "assessment.report"
M_ACCEPT = _TG + "accept"
M_EXPORT = _TG + "graph.export"
M_DECISION_LOG = _TG + "decisions.log"

_DIGEST = re.compile(r"^[0-9a-f]{16}$")
_DECISION = re.compile(r"^D-\d{3}$")


# ------------------------------------------------------------------ errors


class UsageError(Exception):
    """Bad arguments, or a theory / target that does not exist (exit 1)."""


class Refused(Exception):
    """The rules refuse the act, or it could not be carried out (exit 2)."""


class NotAvailable(Refused):
    """A module the command needs is not there (yet)."""

    def __init__(self, module: str) -> None:
        super().__init__("not yet available: %s" % module)
        self.module = module


def need(module: str) -> Any:
    """Import ``module`` now; a missing module becomes `NotAvailable`."""
    try:
        return importlib.import_module(module)
    except ModuleNotFoundError as exc:
        raise NotAvailable(exc.name or module) from exc


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ------------------------------------------------------------------ theories


def _from_reference(ref: str) -> Any:
    module, _, attr = ref.partition(":")
    try:
        obj = importlib.import_module(module)
        for part in (attr or "THEORY").split("."):
            obj = getattr(obj, part)
    except (ImportError, AttributeError) as exc:
        raise UsageError("cannot load theory %r: %s" % (ref, exc)) from exc
    if hasattr(obj, "switches") and hasattr(obj, "selections"):
        return obj
    if callable(obj):
        return obj()
    raise UsageError("%r is neither a Theory nor a factory of one" % ref)


def _registry() -> Optional[Any]:
    try:
        return importlib.import_module(REGISTRY)
    except ModuleNotFoundError:
        return None


def load_theory(name: Optional[str]) -> Any:
    """The theory called ``name`` (registry), or at ``module:attribute``."""
    registry = _registry()
    if registry is None:
        if name and ":" in name:
            return _from_reference(name)
        raise NotAvailable(REGISTRY)
    try:
        return registry.get_theory(name)
    except LookupError as exc:
        raise UsageError(str(exc)) from exc


def theory_reference(name: Optional[str]) -> Optional[str]:
    """``module:attribute`` a fresh process can import the theory from."""
    registry = _registry()
    if registry is not None and hasattr(registry, "theory_ref"):
        return registry.theory_ref(name)
    return name if name and ":" in name else None


# ------------------------------------------------------------------ targets


def _pairs(text: str, forks: Mapping[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for item in (p.strip() for p in text.split(",") if p.strip()):
        fork_id, sep, option_id = item.partition("=")
        if not sep or fork_id not in forks:
            raise UsageError("%r is not fork=option for a declared fork "
                             "(forks: %s)" % (item, ", ".join(forks)))
        if option_id not in forks[fork_id].option_ids():
            raise UsageError("fork %s has no option %r (options: %s)" % (
                fork_id, option_id, ", ".join(forks[fork_id].option_ids())))
        out[fork_id] = option_id
    return out


def _by_digest(theory: Any, digest: str) -> Optional[Configuration]:
    enumerate_ = need(M_ENUMERATE)
    modes = need(M_MODES)
    for mode in (modes.ARCHAEOLOGY, modes.PROBE_CONSTRAINT):
        for cfg in enumerate_.enumerate_configurations(theory, mode):
            if cfg.digest == digest:
                return cfg
    return None


def resolve_target(theory: Any, text: Optional[str]) -> Configuration:
    """A labelled configuration from ``active``, a stored name, a digest, or
    ``fork=option[,fork=option]`` applied to the active selection."""
    lifecycle = need(M_LIFECYCLE)
    active = theory.selections.active()
    if not text or text == "active" or text == active.name:
        return lifecycle.configuration_for(theory, active.mapping,
                                           name=active.name)
    if "=" in text:
        overrides = _pairs(text, theory.switches.forks())
        return lifecycle.configuration_for(
            theory, dict(active.mapping, **overrides))
    named = theory.selections.named()
    if text in named:
        return lifecycle.configuration_for(theory, named[text].mapping,
                                           name=text)
    for name, cfg in sorted(named.items()):
        if cfg.digest == text:
            return lifecycle.configuration_for(theory, cfg.mapping, name=name)
    if _DIGEST.match(text):
        if active.digest == text:
            return lifecycle.configuration_for(theory, active.mapping,
                                               name=active.name)
        found = _by_digest(theory, text)
        if found is not None:
            return found
    raise UsageError("no configuration %r in theory %r (use 'active', a "
                     "stored name, a digest or fork=option,...)"
                     % (text, theory.id))


# ---------------------------------------------------------------- assessment


@dataclass
class AssessmentRun:
    """Everything one assessment produced; ``report`` is path_assessment.json."""

    theory_id: str
    mode: str
    configurations: List[Configuration]
    measurements: Dict[str, Dict[str, List[Measurement]]]
    standing: FrozenSet[str]
    vectors: Dict[str, ScoreVector]
    active: Configuration
    report: Dict[str, Any]
    rows: Optional[Dict[str, List[Any]]] = None
    runs: Dict[str, Any] = field(default_factory=dict)

    @property
    def verdict(self) -> str:
        return self.report["verdict"]

    @property
    def recommendation(self) -> Optional[Dict[str, Any]]:
        return self.report.get("recommendation")

    def find(self, key: str) -> Configuration:
        """A configuration of this run by digest or name."""
        for cfg in self.configurations:
            if key in (cfg.digest, cfg.name):
                return cfg
        raise UsageError("%r is not among the %d assessed configurations"
                         % (key, len(self.configurations)))

    def vector(self, key: str) -> ScoreVector:
        return self.vectors[self.find(key).digest]


def _assessment_config(theory: Any) -> Any:
    config = need(M_CONFIG)
    path = theory.assessment_config
    if path is None:
        return config.AssessmentConfig.empty()
    if not Path(path).is_file():
        raise Refused("assessment configuration %s does not exist" % path)
    return config.AssessmentConfig.load(Path(path))


def _grouped(theory: Any, cfg: Configuration, ms: Sequence[Measurement],
             lookup: Mapping[str, str]) -> Dict[str, List[Measurement]]:
    """criterion -> measurements, plus the test ground's own discrete-inputs
    count under closure (options declaring ``adds_discrete_input``)."""
    criteria = need(M_CRITERIA)
    out: Dict[str, List[Measurement]] = {c: [] for c in CRITERIA}
    for m in ms:
        if m.signal not in lookup:
            raise Refused("measurement of undeclared signal %r" % m.signal)
        out[lookup[m.signal]].append(m)
    if not cfg.not_runnable:
        out[getattr(criteria, "DISCRETE_INPUTS_CRITERION", CLOSURE)].append(
            criteria.discrete_inputs(theory.switches.forks(), cfg))
    return out


def _was_measured(cfg: Configuration, ms: Sequence[Measurement]) -> bool:
    return not cfg.not_runnable and any(m.measured for m in ms)


def _signature(ms: Iterable[Measurement]) -> List[Tuple[Any, ...]]:
    return sorted((m.signal, m.status, m.count) for m in ms)


def _null_control(theory: Any, active: Configuration,
                  first: Sequence[Measurement], signals: Sequence[Any]
                  ) -> Dict[str, Any]:
    """K3: the active configuration screened again must be identical."""
    screen = need(M_SCREEN)
    chosen = [s for s in signals if s.cost == SCREEN]
    again = screen.evaluate_configuration(theory, active, chosen)
    ids = {s.id for s in chosen}
    same = _signature(again) == _signature(m for m in first if m.signal in ids)
    return {"checked": True, "fired": not same, "detail": (
        "the active configuration screened twice gives identical "
        "measurements" if same else "the active configuration screened "
        "twice gives DIFFERENT measurements: the run is void")}


def _full_pass(theory: Any, cfgs: List[Configuration],
               measured: Dict[str, List[Measurement]], signals: Sequence[Any],
               jobs: int, progress: Any, runs_dir: Optional[Path],
               roots: Sequence[Path], timeout: Optional[float]
               ) -> Tuple[List[Configuration], Dict[str, Any],
                          Optional[Dict[str, List[Any]]], Dict[str, Any]]:
    """Full runs of every runnable configuration; FULL signals read their
    artifacts. A run that fails makes its configuration NOT_RUNNABLE.
    Returns (configurations, runs, data rows, provenance)."""
    pool, cache, fingerprint = need(M_POOL), need(M_CACHE), need(M_FINGERPRINT)
    screen = need(M_SCREEN)
    base = Path(runs_dir) if runs_dir else cache.default_runs_dir()
    roots = list(roots) or fingerprint.engine_roots()
    stamp = fingerprint.engine_fingerprint(roots)
    provenance = {"engine_fingerprint": stamp, "runs_dir": str(base),
                  "fingerprint_roots": [str(r) for r in roots]}
    runnable = [c for c in cfgs if not c.not_runnable]
    tasks = pool.full_run_tasks(theory, runnable, base, stamp, timeout,
                                cache=cache.RunCache(base))
    results = {r.digest: r for r in pool.run_pool(tasks, jobs, progress)}
    full_signals = [s for s in signals if s.cost == FULL]
    rows: Dict[str, List[Any]] = {}
    runs: Dict[str, Any] = {}
    out: List[Configuration] = []
    for cfg in cfgs:
        result = results.get(cfg.digest)
        run = getattr(result, "value", None)
        if cfg.not_runnable:
            out.append(cfg)
            continue
        runs[cfg.digest] = run
        if run is None or not getattr(run, "completed", False):
            why = getattr(run, "reason", "") or getattr(result, "error", "") \
                or "the full run did not complete"
            out.append(dataclasses.replace(
                cfg, not_runnable=True, reasons=cfg.reasons + (why,)))
            continue
        measured[cfg.digest] += list(screen.evaluate_configuration(
            theory, cfg, full_signals, root=run.root))
        if theory.anchors is not None:
            rows[cfg.digest] = list(theory.anchors.scored_rows(Path(run.root)))
        out.append(cfg)
    return out, runs, (rows or None), provenance


def run_assessment(theory: Any, mode: str = "assess", *,
                   forks: Optional[Sequence[str]] = None,
                   cap: Optional[int] = None, jobs: int = 1,
                   progress: Any = None, full: bool = False,
                   runs_dir: Optional[Path] = None,
                   fingerprint_roots: Sequence[Path] = (),
                   timeout: Optional[float] = None,
                   recorded_sha256: Optional[str] = None,
                   theory_ref: Optional[str] = None) -> AssessmentRun:
    """Enumerate, measure, score and report. Reads the store; never writes."""
    modes, enumerate_ = need(M_MODES), need(M_ENUMERATE)
    mode = modes.parse_mode(mode)
    if mode == modes.PROBE_CONSTRAINT:
        raise UsageError("probe-constraint yields INVALID combinations; list "
                         "them with `list configurations --mode "
                         "probe-constraint` -- they are never assessed")
    if cap is not None and cap < 1:
        raise UsageError("--cap must be at least 1 (the active comes first)")
    cfgs = list(enumerate_.enumerate_configurations(theory, mode, forks=forks,
                                                    cap=cap))
    counted = enumerate_.count_configurations(theory, mode, forks=forks,
                                              cap=cap).as_dict()
    active = theory.selections.active()
    if active.digest not in {c.digest for c in cfgs}:
        raise Refused("the active configuration %s is not among the "
                      "enumerated configurations" % active.digest)
    signals = list(theory.signals.signals())
    lookup = {s.id: s.criterion for s in signals}
    screened = need(M_SCREEN).screen(theory, cfgs, signals, jobs=jobs,
                                     progress=progress, theory_ref=theory_ref)
    measured = {c.digest: list(screened.measurements.get(c.digest, ()))
                for c in cfgs}
    first_active = list(measured[active.digest])
    runs: Dict[str, Any] = {}
    rows = None
    provenance: Dict[str, Any] = {}
    if full:
        cfgs, runs, rows, provenance = _full_pass(
            theory, cfgs, measured, signals, jobs, progress, runs_dir,
            fingerprint_roots, timeout)
    grouped = {c.digest: _grouped(theory, c, measured[c.digest], lookup)
               for c in cfgs}
    standing = need(M_STANDING).standing_failures(
        {c.digest: grouped[c.digest] for c in cfgs
         if _was_measured(c, measured[c.digest])})
    assess_cfg = _assessment_config(theory)
    criteria = need(M_CRITERIA)
    stage = "full" if full else "screen"
    vectors = {c.digest: criteria.score_configuration(
        c, grouped[c.digest], assess_cfg, standing, stage_reached=stage)
        for c in cfgs}
    active_cfg = next(c for c in cfgs if c.digest == active.digest)
    controls = {"K3": _null_control(theory, active_cfg, first_active, signals)}
    report = need(M_REPORT).build_report(
        theory=theory.id, mode=mode, configurations=cfgs,
        vectors=list(vectors.values()), active_digest=active.digest,
        assess_cfg=assess_cfg, standing=standing, rows=rows,
        enumeration=dict(counted, stage=stage, sweep=list(forks or [])),
        controls=controls, recorded_sha256=recorded_sha256,
        generated_at=_now())
    if provenance:
        report["provenance"] = provenance
    return AssessmentRun(theory.id, mode, cfgs, grouped, standing, vectors,
                         active_cfg, report, rows, runs)


# ---------------------------------------------------------------- validation


def _validate_forks(forks: Mapping[str, Any]) -> List[str]:
    problems: List[str] = []
    if not forks:
        problems.append("the theory declares no forks")
    for fork_id, fork in forks.items():
        if fork.id != fork_id:
            problems.append("fork key %r holds fork %r" % (fork_id, fork.id))
        try:
            fork.default()
        except ValueError as exc:
            problems.append(str(exc))
    return problems


def _validate_constraints(forks: Mapping[str, Any],
                          constraints: Sequence[Any]) -> List[str]:
    problems: List[str] = []
    for c in constraints:
        refs = ([(c.fork, {c.option}), (c.needs_fork, set(c.needs_options))]
                if hasattr(c, "needs_fork") else
                [(c.fork_a, {c.option_a}), (c.fork_b, {c.option_b})])
        for fork_id, options in refs:
            if fork_id not in forks:
                problems.append("constraint %s names undeclared fork %r"
                                % (c.describe(), fork_id))
            elif options - set(forks[fork_id].option_ids()):
                problems.append("constraint %s names undeclared options %s"
                                % (c.describe(), sorted(
                                    options - set(forks[fork_id].option_ids()))))
        if not getattr(c, "rationale", "") or not getattr(c, "source", ""):
            problems.append("constraint %s lacks a rationale or a source"
                            % c.describe())
    return problems


def _validate_store(theory: Any, forks: Mapping[str, Any],
                    constraints: Sequence[Any]) -> List[str]:
    try:
        active = theory.selections.active()
        theory.selections.named()
    except (ValueError, OSError) as exc:
        return ["selection store: %s" % exc]
    problems = ["the active selection names no option for fork %r" % f
                for f in forks if f not in active.mapping]
    problems += ["the active selection violates %s -- %s" % pair
                 for pair in violations(active.mapping, constraints)]
    if active.not_runnable:
        problems.append("the active selection uses an unimplemented option")
    if active.theory != theory.id:
        problems.append("the store belongs to theory %r" % active.theory)
    return problems


def _validate_signals(signals: Sequence[Any]) -> List[str]:
    problems: List[str] = []
    ids = [s.id for s in signals]
    problems += ["signal %r declared twice" % i for i in sorted(set(ids))
                 if ids.count(i) > 1]
    for s in signals:
        if s.criterion not in CRITERIA:
            problems.append("signal %r: unknown criterion %r"
                            % (s.id, s.criterion))
        if s.binding not in (LIVE, ARTIFACT) or s.cost not in (SCREEN, FULL):
            problems.append("signal %r: binding %r / cost %r"
                            % (s.id, s.binding, s.cost))
    covered = {s.criterion for s in signals}
    problems += ["no signal measures %s" % c for c in DECIDING_CRITERIA
                 if c != CLOSURE and c not in covered]
    return problems


def _validate_assessment(theory: Any, forks: Mapping[str, Any],
                         constraints: Sequence[Any],
                         signals: Sequence[Any]) -> List[str]:
    try:
        cfg = _assessment_config(theory)
    except (ValueError, Refused, NotAvailable) as exc:
        return ["assessment configuration: %s" % exc]
    problems: List[str] = []
    if cfg.theory not in (None, theory.id):
        problems.append("assessment configuration belongs to %r" % cfg.theory)
    for fork_id in cfg.policy_forks:
        if fork_id not in forks:
            problems.append("policy fork %r is not declared" % fork_id)
        elif forks[fork_id].kind != "policy":
            problems.append("policy fork %r is declared kind %r"
                            % (fork_id, forks[fork_id].kind))
    ids = {s.id for s in signals} | {"discrete_inputs"}
    problems += ["target fact %s reads undeclared signal %r"
                 % (f.id, f.signal) for f in cfg.target_facts
                 if f.signal not in ids]
    for criterion, layout in sorted(cfg.key_layout.items()):
        problems += ["key layout of %s names undeclared signal %r"
                     % (criterion, s) for position in layout for s in position
                     if s not in ids]
    declared = {c.describe() for c in constraints}
    problems += ["assessment configuration refers to undeclared constraint "
                 "%r" % c for c in cfg.constraints if c not in declared]
    return problems


def _validate_pipeline(theory: Any) -> List[str]:
    stages = list(theory.pipeline.stages())
    ids = [s.id for s in stages]
    problems = ["the pipeline declares no stage"] if not stages else []
    problems += ["stage %r declared twice" % i for i in sorted(set(ids))
                 if ids.count(i) > 1]
    problems += ["stage %r has no command" % s.id for s in stages
                 if not s.command]
    return problems


def validate_theory(theory: Any) -> List[str]:
    """Every problem in the theory's declarations (empty when valid)."""
    forks = dict(theory.switches.forks())
    constraints = list(theory.switches.constraints())
    signals = list(theory.signals.signals())
    problems = _validate_forks(forks)
    problems += _validate_constraints(forks, constraints)
    if not problems:
        problems += _validate_store(theory, forks, constraints)
    problems += _validate_signals(signals)
    problems += _validate_assessment(theory, forks, constraints, signals)
    problems += _validate_pipeline(theory)
    problems += ["narrative entry %r lacks an id or a label" % (n,)
                 for n in theory.narrative
                 if not n.get("id") or not (n.get("label") or n.get("title"))]
    log = theory.decisions.decision_log_path() if theory.decisions else None
    if log is not None and not Path(log).is_file():
        problems.append("decision log %s does not exist" % log)
    return problems


# ------------------------------------------------------------------ output


def _emit(args: argparse.Namespace, payload: Any, text: str) -> None:
    """Write JSON to --out (when given); print JSON (--json) or ``text``."""
    blob = json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n"
    out = getattr(args, "out", None)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(blob, encoding="utf-8")
    print(blob if getattr(args, "json", False) else text, end="" if getattr(
        args, "json", False) else "\n")


def _key(score: Mapping[str, Any]) -> str:
    key = score.get("key")
    return "-" if key is None else "(%s)" % ", ".join(str(k) for k in key)


def _short(cfg: Mapping[str, Any]) -> str:
    name = cfg.get("name")
    return "%s%s" % (cfg["digest"], " (%s)" % name if name else "")


def _assessment_text(report: Mapping[str, Any]) -> str:
    cfgs = report["configurations"]
    verdicts: Dict[str, int] = {}
    for c in cfgs:
        verdicts[c["verdict"]] = verdicts.get(c["verdict"], 0) + 1
    by = {c["digest"]: c for c in cfgs}
    groups = report.get("ranking", {}).get("groups", [])
    active = report["active"]
    pre = report.get("pre_registration", {})
    lines = [
        "theory %s | mode %s | %d configurations assessed (%s)" % (
            report["theory"], report["mode"], len(cfgs), ", ".join(
                "%s %d" % kv for kv in sorted(verdicts.items()))),
        "assessment configuration sha256 %s%s" % (
            pre.get("sha256") or "-", " (decision %s)" % pre["decision"]
            if pre.get("decision") else ""),
        "standing failures (excluded from the comparison, disclosed): %s"
        % (", ".join(report.get("standing_failures") or []) or "none"),
    ]
    if groups:
        lines.append("top group (%d): %s" % (len(groups[0]), ", ".join(
            _short(by[d]) for d in groups[0])))
    lines.append("active %s: group %s%s" % (
        _short(by.get(active["digest"], active)), active.get("group"),
        ", in the top group" if active.get("in_top_group") else ""))
    lines.append("VERDICT %s" % report["verdict"])
    rec = report.get("recommendation")
    if rec:
        lines.append("recommendation: target %s; deciding criterion %s" % (
            rec.get("target") or "none (choose among: %s)" % ", ".join(
                rec.get("candidates") or []) or "-",
            rec.get("deciding_criterion") or "-"))
        lines += ["  - %s" % r for r in rec.get("reasons") or []]
    lines.append("assess recommends and never adopts; adopting is an explicit "
                 "`accept <target> --decision D-NNN`.")
    return "\n".join(lines)


def _vector_from_entry(entry: Mapping[str, Any]) -> ScoreVector:
    """A ScoreVector rebuilt from a report's configuration entry."""
    scores = []
    for criterion in CRITERIA:
        s = entry["scores"][criterion]
        scores.append(CriterionScore(
            criterion, tuple(s["key"]) if s.get("key") is not None else None,
            s.get("status", "MEASURED"), dict(s.get("components") or {}),
            tuple(s.get("failures") or ()), tuple(s.get("unmeasured") or ())))
    return ScoreVector(entry["digest"], tuple(scores), entry["verdict"],
                       tuple(entry.get("reasons") or ()),
                       entry.get("stage_reached", "screen"))


def _explain_text(entry: Mapping[str, Any], against: Mapping[str, Any],
                  comparison: Mapping[str, Any]) -> str:
    diff = {f: (o, against["selection"].get(f))
            for f, o in sorted(entry["selection"].items())
            if against["selection"].get(f) != o}
    lines = ["configuration %s | lifecycle %s | verdict %s | group %s" % (
        _short(entry), entry["lifecycle"], entry["verdict"], entry.get("group")),
        "  differs from %s on: %s" % (_short(against), ", ".join(
            "%s=%s (vs %s)" % (f, a, b) for f, (a, b) in diff.items())
            or "nothing")]
    for criterion in CRITERIA:
        s = entry["scores"][criterion]
        extra = "; ".join(filter(None, [
            "failures: %s" % ", ".join(s["failures"]) if s.get("failures")
            else "", "unmeasured: %s" % "; ".join(s["unmeasured"])
            if s.get("unmeasured") else ""]))
        lines.append("  %-12s key %-14s %s" % (criterion, _key(s), extra))
    lines += ["  reason: %s" % r for r in entry.get("reasons") or []]
    winner = {"a": _short(against), "b": _short(entry)}.get(
        comparison["winner"], comparison["winner"])
    lines.append("compared with %s: %s%s" % (
        _short(against), winner if comparison["winner"] in ("TIE",
                                                            "UNDECIDED")
        else "%s is ahead" % winner, " on %s" % comparison[
            "deciding_criterion"] if comparison.get("deciding_criterion")
        else ""))
    if comparison.get("pareto_note"):
        lines.append("  %s" % comparison["pareto_note"])
    lines += ["  %s" % r for r in comparison.get("reasons") or []]
    return "\n".join(lines)


# ------------------------------------------------------------------ helpers


def _progress(value: Optional[str]) -> Any:
    """``jsonl`` / ``-``: JSON lines on stderr; any other value: a file."""
    if not value:
        return None
    if value in ("jsonl", "-"):
        def to_stderr(event: Dict[str, Any]) -> None:
            sys.stderr.write(json.dumps(event, sort_keys=True,
                                        default=str) + "\n")
            sys.stderr.flush()
        return to_stderr
    return Path(value)


def _sweep(text: Optional[str]) -> Optional[List[str]]:
    return [f.strip() for f in text.split(",") if f.strip()] if text else None


def _decision(value: Optional[str], required: bool = True) -> Optional[str]:
    if value is None:
        if required:
            raise UsageError("--decision D-NNN is required: the act is "
                             "recorded in the decision log")
        return None
    if not _DECISION.match(value):
        raise UsageError("--decision must look like D-NNN, not %r" % value)
    return value


def _load_report(path: Optional[str]) -> Optional[Dict[str, Any]]:
    if not path:
        return None
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise UsageError("cannot read assessment %s: %s" % (path, exc)) \
            from exc


def _result_dict(result: Any) -> Dict[str, Any]:
    if dataclasses.is_dataclass(result) and not isinstance(result, type):
        return dataclasses.asdict(result)
    return dict(result) if isinstance(result, Mapping) else {"result": result}


def _act_text(data: Mapping[str, Any]) -> str:
    """One readable paragraph for an accept / retire / reinstate result."""
    head = "%s%s: decision %s, %s" % (
        "DRY RUN (nothing written) -- " if data.get("dry_run") else "",
        data.get("theory") or "%s.%s" % (data.get("fork"), data.get("option")),
        data.get("decision_id"), "written" if data.get("written")
        else "not written")
    lines = [head]
    if "diff" in data:
        lines.append("diff: %s" % (", ".join(
            "%s %s -> %s" % (f, a, b) for f, (a, b) in sorted(
                data["diff"].items())) or "none"))
        lines.append("previous active kept as %s" % data.get("kept_as"))
    if "new_status" in data:
        lines.append("%s -> %s%s" % (data.get("old_status"),
                                     data.get("new_status"),
                                     " (%s)" % data["certainty"]
                                     if data.get("certainty") else ""))
    lines += ["pending edit: %s" % e for e in data.get("pending_edits") or ()]
    lines += ["stale: %s" % r for r in data.get("stale_reasons") or ()]
    lines.append("decision log %s:
%s" % (data.get("log_path"),
                                           data.get("entry_text", "")))
    return "
".join(lines)


def _act(args: argparse.Namespace, fn: Callable[..., Any], *pos: Any,
         **kwargs: Any) -> int:
    """Run an explicit act (accept / retire / reinstate) and report it."""
    try:
        result = fn(*pos, **kwargs)
    except Exception as exc:
        if "refus" in type(exc).__name__.lower():
            raise Refused(str(exc)) from exc
        raise
    data = _result_dict(result)
    _emit(args, data, _act_text(data))
    return OK


def _current_fingerprint(report: Optional[Mapping[str, Any]],
                         roots: Sequence[str]) -> Optional[str]:
    """The engine fingerprint now, over the roots the assessment recorded
    (only when it recorded one)."""
    provenance = (report or {}).get("provenance") or {}
    if not provenance.get("engine_fingerprint"):
        return None
    chosen = roots or provenance.get("fingerprint_roots") or ()
    return need(M_FINGERPRINT).engine_fingerprint([Path(r) for r in chosen])


# ------------------------------------------------------------------ commands


def cmd_list(args: argparse.Namespace, theory: Any) -> int:
    what = args.what
    if what == "theories":
        registry = _registry()
        names = registry.available_theories() if registry else []
        default = registry.default_theory_name() if registry else None
        _emit(args, {"theories": names, "default": default}, "\n".join(
            "%s%s" % (n, "  (default)" if n == default else "")
            for n in names) or "no theories registered")
        return OK
    theory = theory if theory is not None else load_theory(args.theory)
    if what == "forks":
        return _list_forks(args, theory)
    if what == "named":
        named = {n: {"digest": c.digest, "selection": c.mapping}
                 for n, c in sorted(theory.selections.named().items())}
        _emit(args, named, "\n".join("%s  %s" % (v["digest"], n)
                                     for n, v in named.items()) or "none")
        return OK
    enumerate_ = need(M_ENUMERATE)
    cfgs = list(enumerate_.enumerate_configurations(
        theory, args.mode, forks=_sweep(args.sweep), cap=args.cap))
    payload = [{"digest": c.digest, "name": c.name, "lifecycle": c.lifecycle,
                "not_runnable": c.not_runnable, "selection": c.mapping}
               for c in cfgs]
    _emit(args, payload, "\n".join(
        "%s  %-20s %s%s" % (c.digest, c.lifecycle, " NOT_RUNNABLE"
                            if c.not_runnable else "", " " + c.name
                            if c.name else "") for c in cfgs))
    return OK


def _list_forks(args: argparse.Namespace, theory: Any) -> int:
    forks = theory.switches.forks()
    payload = {f.id: {"kind": f.kind, "binding": f.binding,
                      "question": f.question,
                      "options": {o.id: {"status": o.status,
                                         "certainty": o.certainty,
                                         "implemented": o.implemented,
                                         "adds_discrete_input":
                                             o.adds_discrete_input}
                                  for o in f.options}}
               for f in forks.values()}
    payload["constraints"] = [c.describe() for c in
                              theory.switches.constraints()]
    lines = []
    for f in forks.values():
        lines.append("%s [%s, %s] %s" % (f.id, f.kind, f.binding, f.question))
        for o in f.options:
            flags = [o.status.upper()] + ([o.certainty] if o.certainty else [])
            flags += [] if o.implemented else ["not implemented"]
            flags += ["adds a discrete input"] if o.adds_discrete_input else []
            lines.append("    %-16s %s" % (o.id, ", ".join(flags)))
    lines += ["constraint: %s" % c for c in payload["constraints"]]
    _emit(args, payload, "\n".join(lines))
    return OK


def cmd_validate(args: argparse.Namespace, theory: Any) -> int:
    problems = validate_theory(theory)
    forks = theory.switches.forks()
    summary = {"theory": theory.id, "valid": not problems,
               "forks": len(forks),
               "options": sum(len(f.options) for f in forks.values()),
               "constraints": len(theory.switches.constraints()),
               "signals": len(theory.signals.signals()),
               "problems": problems}
    text = ("theory %s: valid (%d forks, %d options, %d constraints, %d "
            "signals)" % (theory.id, summary["forks"], summary["options"],
                          summary["constraints"], summary["signals"])
            if not problems else "theory %s: %d problem(s)\n%s" % (
                theory.id, len(problems), "\n".join("  - " + p
                                                    for p in problems)))
    _emit(args, summary, text)
    if problems:
        raise Refused("theory %s failed validation" % theory.id)
    return OK


def _assess_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    return dict(forks=_sweep(args.sweep), cap=args.cap, jobs=args.jobs,
                progress=_progress(args.progress), full=args.full,
                runs_dir=Path(args.runs_dir) if args.runs_dir else None,
                fingerprint_roots=[Path(p) for p in args.fingerprint_root],
                timeout=args.timeout, recorded_sha256=args.annex_sha256,
                theory_ref=theory_reference(args.theory))


def cmd_assess(args: argparse.Namespace, theory: Any) -> int:
    if args.dry_run:
        counted = need(M_ENUMERATE).count_configurations(
            theory, args.mode, forks=_sweep(args.sweep), cap=args.cap)
        data = counted.as_dict()
        _emit(args, data, "dry run: %s mode %s would assess %d "
              "configurations (%s not runnable); nothing measured"
              % (theory.id, data["mode"], data["yielded"],
                 data["not_runnable"]))
        return OK
    run = run_assessment(theory, args.mode, **_assess_kwargs(args))
    _emit(args, run.report, _assessment_text(run.report))
    return OK


def cmd_explain(args: argparse.Namespace, theory: Any) -> int:
    report = _load_report(args.assessment)
    if report is None:
        report = run_assessment(theory, args.mode,
                                **_assess_kwargs(args)).report
    entries = {c["digest"]: c for c in report["configurations"]}
    by_name = {c["name"]: c for c in report["configurations"] if c["name"]}

    def entry_for(text: Optional[str]) -> Mapping[str, Any]:
        if not text or text == "active":
            return entries[report["active"]["digest"]]
        if text in by_name or text in entries:
            return by_name.get(text) or entries[text]
        digest = resolve_target(theory, text).digest
        if digest not in entries:
            raise UsageError("%s was not assessed in this report" % text)
        return entries[digest]

    entry, against = entry_for(args.target), entry_for(args.against)
    compare = need(M_COMPARATOR).compare
    comparison = compare(_vector_from_entry(against),
                         _vector_from_entry(entry)).as_dict()
    payload = {"configuration": entry, "against": against["digest"],
               "comparison": comparison, "verdict": report["verdict"]}
    _emit(args, payload, _explain_text(entry, against, comparison))
    return OK


def cmd_accept(args: argparse.Namespace, theory: Any) -> int:
    decision = _decision(args.decision)
    if args.override and not (args.reason or "").strip():
        raise UsageError("--override needs --reason: an override is recorded "
                         "with its reason")
    accept = need(M_ACCEPT).accept
    target = resolve_target(theory, args.target)
    report = _load_report(args.assessment)
    return _act(args, accept, theory, target, decision, assessment=report,
                dry_run=args.dry_run, override=args.override,
                reason=args.reason or "",
                fingerprint=_current_fingerprint(report,
                                                 args.fingerprint_root))


def cmd_retire(args: argparse.Namespace, theory: Any) -> int:
    decision = _decision(args.decision)
    if not (args.reason or "").strip():
        raise UsageError("--reason is required: a retirement says why")
    retire = need(M_ACCEPT).retire
    return _act(args, retire, theory, args.fork, args.option, decision,
                args.certainty, args.reason, dry_run=args.dry_run)


def cmd_reinstate(args: argparse.Namespace, theory: Any) -> int:
    decision = _decision(args.decision)
    if not (args.reason or "").strip():
        raise UsageError("--reason is required: a reinstatement says why")
    reinstate = need(M_ACCEPT).reinstate
    return _act(args, reinstate, theory, args.fork, args.option, decision,
                args.reason, dry_run=args.dry_run)


def cmd_export_graph(args: argparse.Namespace, theory: Any) -> int:
    export = need(M_EXPORT).export_graph
    out = Path(args.out or "path_graph.json")
    graph = export(theory, out, assessment_path=args.assessment,
                   html=args.html or False)
    viewer = (out.with_suffix(".html") if args.html is True
              else args.html)
    print("wrote %s (%d nodes, %d edges)%s" % (
        out, len(graph["nodes"]), len(graph["edges"]),
        " and %s" % viewer if viewer else ""))
    return OK


def cmd_run(args: argparse.Namespace, theory: Any) -> int:
    worker, screen = need(M_WORKER), need(M_SCREEN)
    cache, fingerprint = need(M_CACHE), need(M_FINGERPRINT)
    if args.target:
        cfg = resolve_target(theory, args.target)
    else:
        enumerate_, modes = need(M_ENUMERATE), need(M_MODES)
        cfg = next(iter(enumerate_.enumerate_configurations(theory,
                                                            modes.SINGLE)))
    if cfg.not_runnable:
        raise Refused("%s is NOT_RUNNABLE: %s" % (cfg.digest,
                                                  "; ".join(cfg.reasons)))
    base = Path(args.runs_dir) if args.runs_dir else cache.default_runs_dir()
    stamp = fingerprint.engine_fingerprint(
        [Path(p) for p in args.fingerprint_root])
    result = worker.run_configuration(theory, cfg, base, stamp, args.timeout)
    payload: Dict[str, Any] = {"configuration": {
        "digest": cfg.digest, "name": cfg.name, "lifecycle": cfg.lifecycle,
        "selection": cfg.mapping}, "run": result.to_dict()}
    if result.completed:
        ms = list(screen.evaluate_configuration(
            theory, cfg, list(theory.signals.signals()), root=result.root))
        ms.append(need(M_CRITERIA).discrete_inputs(theory.switches.forks(),
                                                   cfg))
        payload["measurements"] = [dataclasses.asdict(m) for m in ms]
    text = "run %s: %s%s (root %s)" % (
        cfg.digest, result.status, " -- %s" % result.reason
        if result.reason else "", result.root)
    _emit(args, payload, text)
    if not result.completed:
        raise Refused("the run of %s did not complete" % cfg.digest)
    return OK


HANDLERS: Dict[str, Callable[[argparse.Namespace, Any], int]] = {
    "list": cmd_list, "validate": cmd_validate, "assess": cmd_assess,
    "explain": cmd_explain, "accept": cmd_accept, "retire": cmd_retire,
    "reinstate": cmd_reinstate, "export-graph": cmd_export_graph,
    "run": cmd_run,
}


# ------------------------------------------------------------------ parser


class _Parser(argparse.ArgumentParser):
    """argparse that raises UsageError instead of exiting with code 2."""

    def error(self, message: str) -> None:  # type: ignore[override]
        raise UsageError(message)


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--theory", help="theory name, or module:ATTRIBUTE "
                   "(default: the registry's default)")
    p.add_argument("--json", action="store_true",
                   help="print JSON instead of text")
    p.add_argument("--out", help="also write the JSON result to this file")


def _sweep_options(p: argparse.ArgumentParser) -> None:
    p.add_argument("--mode", default="assess",
                   help="assess | reassess | archaeology | single"
                        " (list also: probe-constraint)")
    p.add_argument("--sweep", help="sweep only these forks (comma-separated);"
                                   " the rest are held at the active option")
    p.add_argument("--cap", type=int, help="stop after N configurations")


def _run_options(p: argparse.ArgumentParser) -> None:
    p.add_argument("--jobs", type=int, default=1, help="parallel workers")
    p.add_argument("--progress", help="'jsonl' for JSON-lines progress on "
                                      "stderr, or a file path")
    p.add_argument("--full", action="store_true",
                   help="also run every runnable configuration's pipeline "
                        "and read its artifacts")
    p.add_argument("--runs-dir", help="base directory of isolated run roots")
    p.add_argument("--fingerprint-root", action="append", default=[],
                   help="source root hashed into the engine fingerprint "
                        "(repeatable; default: the engine package)")
    p.add_argument("--timeout", type=float, help="per-stage timeout, seconds")
    p.add_argument("--annex-sha256", help="sha256 recorded in the "
                   "pre-registration annex (checks kill condition K5)")


def _act_options(p: argparse.ArgumentParser) -> None:
    p.add_argument("--decision", help="decision id recorded for the act, "
                                      "D-NNN")
    p.add_argument("--reason", help="why (required for overrides, "
                                    "retire and reinstate)")
    p.add_argument("--dry-run", action="store_true",
                   help="show what would be written; write nothing")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="python -m metaphysica.testground",
                     description="The test ground: assess a theory's "
                                 "configurations under the D-019 decision "
                                 "rule. Only the comparator ranks; accept "
                                 "is an explicit act.")
    sub = parser.add_subparsers(dest="command", parser_class=_Parser)
    p = sub.add_parser("list", help="theories, forks, named or enumerated "
                                    "configurations")
    p.add_argument("what", nargs="?", default="theories",
                   choices=("theories", "forks", "named", "configurations"))
    _common(p)
    _sweep_options(p)
    p = sub.add_parser("validate", help="check a theory's declarations")
    _common(p)
    p = sub.add_parser("assess", help="score every configuration of a mode "
                                      "and report the verdict (never adopts)")
    _common(p)
    _sweep_options(p)
    _run_options(p)
    p.add_argument("--dry-run", action="store_true",
                   help="count the configurations; measure nothing")
    p = sub.add_parser("explain", help="one configuration's scores and its "
                                       "comparison with the active one")
    p.add_argument("target", nargs="?", help="digest, name, fork=option,... "
                                             "(default: active)")
    p.add_argument("--against", help="compare with this configuration "
                                     "instead of the active one")
    p.add_argument("--assessment", help="read a path_assessment.json instead "
                                        "of assessing now")
    _common(p)
    _sweep_options(p)
    _run_options(p)
    p = sub.add_parser("accept", help="adopt a configuration (explicit act, "
                                      "records a decision)")
    p.add_argument("target", help="digest, name or fork=option,...")
    p.add_argument("--assessment", help="the path_assessment.json the accept "
                                        "rests on")
    p.add_argument("--override", action="store_true",
                   help="accept despite the rules' refusal (needs --reason)")
    p.add_argument("--fingerprint-root", action="append", default=[],
                   help="source root of the current engine fingerprint "
                        "(default: the roots the assessment recorded)")
    _common(p)
    _act_options(p)
    for name, text in (("retire", "demote an option to DISABLED (records a "
                                  "decision)"),
                       ("reinstate", "restore a DISABLED option (records a "
                                     "decision)")):
        p = sub.add_parser(name, help=text)
        p.add_argument("fork")
        p.add_argument("option")
        if name == "retire":
            p.add_argument("--certainty", default="reassessable",
                           choices=("certain", "reassessable"))
        _common(p)
        _act_options(p)
    p = sub.add_parser("export-graph", help="write path_graph.json (and an "
                                            "optional HTML viewer)")
    p.add_argument("--assessment", help="overlay a path_assessment.json")
    p.add_argument("--html", nargs="?", const=True, default=None,
                   help="also write a standalone HTML viewer (beside the "
                        "JSON, or at the given path)")
    p.add_argument("--theory", help="theory name, or module:ATTRIBUTE")
    p.add_argument("--out", help="path_graph.json to write "
                                 "(default: ./path_graph.json)")
    p = sub.add_parser("run", help="one configuration's full run in an "
                                   "isolated root")
    p.add_argument("target", nargs="?", help="digest, name, fork=option,... "
                                             "(default: the one in force)")
    _common(p)
    _run_options(p)
    return parser


def main(argv: Optional[Sequence[str]] = None, theory: Any = None) -> int:
    """Run one command; ``theory`` (tests) bypasses the --theory lookup."""
    parser = build_parser()
    try:
        try:
            args = parser.parse_args(argv)
        except SystemExit as exc:          # --help
            return int(exc.code or 0)
        if args.command is None:
            parser.print_help()
            return USAGE
        needs_theory = not (args.command == "list"
                            and args.what == "theories")
        if theory is None and needs_theory:
            theory = load_theory(args.theory)
        return HANDLERS[args.command](args, theory)
    except UsageError as exc:
        print("usage error: %s" % exc, file=sys.stderr)
        return USAGE
    except NotAvailable as exc:
        print(str(exc), file=sys.stderr)
        return REFUSED
    except Refused as exc:
        print("refused: %s" % exc, file=sys.stderr)
        return REFUSED
    except LookupError as exc:
        print("usage error: %s" % exc, file=sys.stderr)
        return USAGE
    except ValueError as exc:
        print("refused: %s" % exc, file=sys.stderr)
        return REFUSED
