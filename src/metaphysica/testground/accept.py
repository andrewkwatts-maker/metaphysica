"""The 1-step accept: make a configuration the active path by one explicit act.

D-019: the assessment proposes, an explicit accept adopts, nothing is adopted
automatically. `accept` is that act. It

- resolves the target (a named configuration, a digest, a Configuration or a
  selection mapping) and refuses one that selects a DISABLED or unimplemented
  option, violates a declared constraint, or is already active;
- refuses a stale assessment -- one whose recorded active digest or engine
  fingerprint differs from the current ones -- unless ``override`` is given
  with a reason (and refuses an override without a reason);
- refuses a decision id already used by a PATH ACCEPT entry for a different
  target (the id may already carry a pre-registration: accept adds its entry);
- with ``dry_run`` returns the full selection diff and entry text and writes
  nothing;
- otherwise writes ONLY through the theory's SelectionStore (the old active is
  kept as the named configuration ``previous-active-<date>``; the new active
  carries ``decided_by``) and the decision log, where it appends a PATH ACCEPT
  entry. Nothing is ever deleted.

`retire` and `reinstate` change an option's standing (DISABLED with a
certainty, or back to CONSIDERED) the same way: a decision entry, and the
store's optional ``write_option_status`` when it has one -- otherwise the
declaration edit to make is returned in ``pending_edits``.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import datetime as _dt
import inspect
from dataclasses import dataclass, field
from pathlib import Path
from typing import (Any, Callable, Dict, List, Mapping, Optional, Sequence,
                    Tuple, Union)

from metaphysica.testground.assessment.score import (CRITERIA, NOT_RUNNABLE,
                                                     REJECTED)
from metaphysica.testground.configurations import model as cfgmodel
from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.constraints import violations
from metaphysica.testground.decisions.log import (ACCEPT, REINSTATE, RETIRE,
                                                  DecisionLog, is_decision_id)
from metaphysica.testground.decisions.write import (AcceptEntry,
                                                    ReinstateEntry,
                                                    RetireEntry, append_entry,
                                                    render_accept,
                                                    render_reinstate,
                                                    render_retire)
from metaphysica.testground.graph.build import (AssessmentView,
                                                assessment_view,
                                                load_assessment)
from metaphysica.testground.switches.model import (CERTAIN, CONSIDERED,
                                                   DISABLED, REASSESSABLE)

__all__ = [
    "AcceptRefused",
    "AcceptResult",
    "StandingChange",
    "previous_name",
    "accept",
    "retire",
    "reinstate",
]

Target = Union[str, Configuration, Mapping[str, str]]
AssessmentLike = Union[None, Mapping[str, Any], str, Path]

#: Names of the store methods used beyond the SelectionStore protocol.
NAMED_WRITERS = ("write_named", "add_named")
STATUS_WRITER = "write_option_status"


class AcceptRefused(ValueError):
    """An accept, retire or reinstate that must not happen, with every reason."""

    def __init__(self, reasons: Sequence[str]) -> None:
        self.reasons: Tuple[str, ...] = tuple(reasons)
        super().__init__("refused: " + "; ".join(self.reasons))


@dataclass(frozen=True)
class AcceptResult:
    """What an accept did (or, on a dry run, would do)."""

    decision_id: str
    date: str
    theory: str
    target: Configuration
    previous: Configuration
    kept_as: str
    diff: Dict[str, Tuple[Optional[str], Optional[str]]]
    entry_text: str
    log_path: Path
    dry_run: bool
    written: bool
    data_tiebreak: bool = False
    trials_factor: Optional[int] = None
    override_reason: str = ""
    stale_reasons: Tuple[str, ...] = ()
    notes: Tuple[str, ...] = ()
    store_calls: Tuple[str, ...] = ()


@dataclass(frozen=True)
class StandingChange:
    """What a retire or reinstate did (or would do)."""

    decision_id: str
    date: str
    fork: str
    option: str
    old_status: str
    new_status: str
    certainty: Optional[str]
    entry_text: str
    log_path: Path
    dry_run: bool
    written: bool
    store_calls: Tuple[str, ...] = ()
    pending_edits: Tuple[str, ...] = field(default_factory=tuple)


# -- small shared steps -------------------------------------------------------

def _today(date: Optional[str]) -> str:
    return date or _dt.date.today().isoformat()


def _log_path(theory: Any, log_path: Union[None, str, Path]) -> Optional[Path]:
    if log_path is not None:
        return Path(log_path)
    provider = getattr(theory, "decisions", None)
    path = provider.decision_log_path() if provider is not None else None
    return Path(path) if path is not None else None


def _load_assessment(assessment: AssessmentLike) -> Optional[AssessmentView]:
    if isinstance(assessment, (str, Path)):
        assessment = load_assessment(assessment)
    return assessment_view(assessment)


def previous_name(named: Mapping[str, Any], date: str) -> str:
    """``previous-active-<date>``, numbered when that name is already taken."""
    base = "previous-active-%s" % date
    if base not in named:
        return base
    n = 2
    while "%s-%d" % (base, n) in named:
        n += 1
    return "%s-%d" % (base, n)


def _lifecycle(theory: Any, selection: Mapping[str, str]) -> str:
    """The lifecycle a non-active selection has, from its options' standing."""
    forks = theory.switches.forks()
    options = [forks[f].option(o) for f, o in selection.items() if f in forks
               and o in forks[f].option_ids()]
    if any(o.retired_certain for o in options):
        return cfgmodel.RETIRED_CERTAIN
    if any(o.status == DISABLED for o in options):
        return cfgmodel.RETIRED_REASSESSABLE
    return cfgmodel.CONSIDERED


# -- target resolution and checks -------------------------------------------

def _match_digest(digest: str, named: Mapping[str, Configuration],
                  view: Optional[AssessmentView], previous: Configuration
                  ) -> Optional[Tuple[Dict[str, str], Optional[str]]]:
    for name, cfg in sorted(named.items()):
        if cfg.digest == digest:
            return cfg.mapping, name
    row = view.configuration(digest) if view is not None else None
    if row is not None:
        return dict(row.get("selection") or {}), row.get("name")
    if previous.digest == digest:
        return previous.mapping, previous.name
    return None


def _resolve_target(target: Target, named: Mapping[str, Configuration],
                    view: Optional[AssessmentView], previous: Configuration
                    ) -> Tuple[Dict[str, str], Optional[str]]:
    """(selection, name) of the target; raises AcceptRefused when unknown."""
    if isinstance(target, Configuration):
        return target.mapping, target.name
    if isinstance(target, Mapping):
        return dict(target), None
    if target in named:
        return named[target].mapping, target
    found = _match_digest(str(target), named, view, previous)
    if found is None:
        raise AcceptRefused(["unknown target %r: not a named configuration "
                             "and no known configuration has that digest"
                             % (target,)])
    return found


def _selection_problems(theory: Any, selection: Mapping[str, str]) -> List[str]:
    forks = theory.switches.forks()
    problems: List[str] = []
    for fork_id, option_id in sorted(selection.items()):
        if fork_id not in forks:
            problems.append("unknown fork %r" % fork_id)
            continue
        if option_id not in forks[fork_id].option_ids():
            problems.append("fork %r has no option %r" % (fork_id, option_id))
            continue
        option = forks[fork_id].option(option_id)
        if option.status == DISABLED:
            problems.append("selects DISABLED option %s=%s (reinstate it "
                            "first)" % (fork_id, option_id))
        if not option.implemented:
            problems.append("selects unimplemented option %s=%s"
                            % (fork_id, option_id))
    for describe, rationale in violations(selection,
                                          theory.switches.constraints()):
        problems.append("violates constraint %s (%s)" % (describe, rationale))
    return problems


def _id_conflicts(log: DecisionLog, decision_id: str, kind: str, name: str,
                  digest: Optional[str]) -> List[str]:
    """A PATH entry of this kind already using the id for another target."""
    out = []
    for entry in log.entries_for(decision_id):
        if entry.kind != kind:
            continue
        same = (entry.target_digest == digest if entry.target_digest and digest
                else entry.target_name == name)
        if not same:
            out.append("%s already records a %s for %r (line %d)"
                       % (decision_id, kind, entry.target_name, entry.line))
    return out


def _stale_reasons(view: AssessmentView, previous: Configuration,
                   fingerprint: Optional[str]) -> List[str]:
    out = []
    if view.active_digest != previous.digest:
        out.append("the assessment was made against active digest %s; the "
                   "active digest is now %s" % (view.active_digest,
                                                 previous.digest))
    if view.engine_fingerprint and fingerprint is None:
        out.append("the assessment records engine fingerprint %s and no "
                   "current fingerprint was supplied to compare"
                   % view.engine_fingerprint)
    elif view.engine_fingerprint and fingerprint != view.engine_fingerprint:
        out.append("engine fingerprint %s differs from the assessment's %s"
                   % (fingerprint, view.engine_fingerprint))
    return out


def _named_writer(store: Any) -> Optional[Callable[..., Any]]:
    for name in NAMED_WRITERS:
        writer = getattr(store, name, None)
        if callable(writer):
            return writer
    return None


def _takes(func: Callable[..., Any], parameter: str) -> bool:
    try:
        return parameter in inspect.signature(func).parameters
    except (TypeError, ValueError):
        return False


# -- the score rows of the entry --------------------------------------------

def _cell(row: Optional[Mapping[str, Any]], criterion: str) -> str:
    if row is None:
        return "not assessed"
    score = (row.get("scores") or {}).get(criterion)
    if isinstance(score, Mapping):
        key = score.get("key")
        status = score.get("status")
        text = "—" if key is None else "(%s)" % ", ".join(str(k) for k in key)
        return text if status in (None, "MEASURED") else "%s %s" % (text,
                                                                     status)
    if isinstance(score, (list, tuple)):
        return "(%s)" % ", ".join(str(k) for k in score)
    return "—" if score is None else str(score)


def _score_rows(view: Optional[AssessmentView], previous_digest: str,
                digest: str) -> List[Tuple[str, str, str]]:
    if view is None:
        return []
    before, after = view.configuration(previous_digest), view.configuration(
        digest)
    if before is None and after is None:
        return []
    return [(c, _cell(before, c), _cell(after, c)) for c in CRITERIA]


# -- accept -------------------------------------------------------------------

@dataclass(frozen=True)
class _Plan:
    """A checked accept, ready to render and write."""

    selection: Dict[str, str]
    name: Optional[str]
    notes: List[str]
    stale: List[str]
    view: Optional[AssessmentView]


def _plan(theory: Any, target: Target, decision_id: str,
          view: Optional[AssessmentView], previous: Configuration,
          named: Mapping[str, Configuration], log: Optional[DecisionLog],
          override: bool, reason: str, fingerprint: Optional[str]) -> _Plan:
    """Resolve and check an accept; raise AcceptRefused with every reason."""
    refusals: List[str] = []
    if not is_decision_id(decision_id):
        raise AcceptRefused(["%r is not a decision id (D-NNN)" % decision_id])
    if log is None:
        refusals.append("no decision log path: the theory provides none and "
                        "none was given")
    selection, name = _resolve_target(target, named, view, previous)
    notes: List[str] = []
    missing = sorted(set(previous.mapping) - set(selection))
    if missing:
        notes.append("forks the target does not name keep their active "
                     "option: %s" % ", ".join(missing))
        selection = {**{f: previous.mapping[f] for f in missing}, **selection}
    refusals += _selection_problems(theory, selection)
    digest = cfgmodel.digest_of(selection)
    if digest == previous.digest:
        refusals.append("the target %s is already the active configuration"
                        % digest)
    if log is not None:
        refusals += _id_conflicts(log, decision_id, ACCEPT, name or digest,
                                  digest)
    if _named_writer(theory.selections) is None:
        refusals.append("the selection store cannot keep the old active as a "
                        "named configuration (it has none of %s)"
                        % ", ".join(NAMED_WRITERS))
    stale: List[str] = []
    if view is not None:
        if view.theory and view.theory != theory.id:
            refusals.append("the assessment is of theory %r, not %r"
                            % (view.theory, theory.id))
        stale = _stale_reasons(view, previous, fingerprint)
        row = view.configuration(digest)
        if row is None:
            notes.append("the target was not among the assessed "
                         "configurations")
        elif row.get("verdict") in (REJECTED, NOT_RUNNABLE):
            stale.append("the assessment's verdict on the target is %s"
                         % row.get("verdict"))
        if view.proposed_digest and view.proposed_digest != digest:
            notes.append("not the configuration the assessment proposes "
                         "(%s)" % view.proposed_digest)
    if override and not reason.strip():
        refusals.append("an override needs a reason")
    if stale and not override:
        refusals += ["stale or contested assessment: %s (pass override with "
                     "a reason to accept anyway)" % s for s in stale]
    if refusals:
        raise AcceptRefused(refusals)
    return _Plan(selection, name, notes, stale, view)


def _write_active(store: Any, cfg: Configuration, decision_id: str, note: str,
                  data_tiebreak: bool) -> None:
    if data_tiebreak and _takes(store.write_active, "data_tiebreak"):
        store.write_active(cfg, decision_id, note, data_tiebreak=True)
    else:
        store.write_active(cfg, decision_id, note)


def accept(theory: Any, target: Target, decision_id: str,
           assessment: AssessmentLike = None, dry_run: bool = False,
           override: bool = False, reason: str = "", *,
           log_path: Union[None, str, Path] = None,
           date: Optional[str] = None,
           fingerprint: Optional[str] = None) -> AcceptResult:
    """Make ``target`` the active configuration of ``theory`` (see module doc).

    ``assessment`` is a report dict or the path of one; ``fingerprint`` is the
    current engine fingerprint, compared with the one the assessment records;
    ``log_path`` overrides the theory's decision log; ``date`` (ISO) defaults
    to today. Raises AcceptRefused with every reason when it must not happen.
    """
    store = theory.selections
    previous = store.active()
    named = dict(store.named())
    path = _log_path(theory, log_path)
    log = DecisionLog.load(path) if path is not None else None
    view = _load_assessment(assessment)
    plan = _plan(theory, target, decision_id, view, previous, named, log,
                 override, reason, fingerprint)
    day = _today(date)
    kept_as = previous_name(named, day)
    digest = cfgmodel.digest_of(plan.selection)
    diff = Configuration.of(theory.id, previous.mapping).differs_from(
        Configuration.of(theory.id, plan.selection))
    decided = dict(previous.decided_by)
    decided.update({f: (decision_id,) for f in diff})
    new_active = Configuration.of(
        theory.id, plan.selection, lifecycle=cfgmodel.ACTIVE, name=plan.name,
        decided_by=tuple(sorted(decided.items())),
        reasons=("accepted by %s on %s" % (decision_id, day),))
    kept = Configuration(
        theory=theory.id, selection=previous.selection,
        lifecycle=_lifecycle(theory, previous.mapping), name=kept_as,
        decided_by=previous.decided_by,
        reasons=("the active path until %s, replaced by %s"
                 % (day, decision_id),))
    tiebreak = bool(view is not None and view.data_tiebreak
                    and view.proposed_digest == digest)
    notes = list(plan.notes)
    if tiebreak and not _takes(store.write_active, "data_tiebreak"):
        notes.append("the selection store records no data_tiebreak_dof; the "
                     "fitted degree of freedom is recorded in this entry")
    target_row = view.configuration(digest) if view else None
    text = render_accept(AcceptEntry(
        decision_id=decision_id, date=day, theory=theory.id,
        name=plan.name or digest, digest=digest,
        previous_name=previous.name or previous.digest,
        previous_digest=previous.digest, kept_as=kept_as, diff=diff,
        reason=reason.strip(),
        assessment_verdict=view.verdict if view else None,
        target_verdict=(target_row or {}).get("verdict") if view else None,
        deciding_criterion=view.deciding_criterion if view else None,
        scores=_score_rows(view, previous.digest, digest),
        data_tiebreak=tiebreak,
        trials_factor=view.trials_factor if tiebreak and view else None,
        override_reason=reason.strip() if override else "",
        stale_reasons=tuple(plan.stale) if override else (),
        notes=tuple(notes)))
    note = "%s: accepted %s (%s)" % (decision_id, plan.name or digest, digest)
    writer = _named_writer(store)
    calls = ("%s(%r, %s)" % (getattr(writer, "__name__", NAMED_WRITERS[0]),
                             kept_as, previous.digest),
             "append PATH ACCEPT %s to %s" % (decision_id, path.name),
             "write_active(%s, %r)" % (digest, decision_id))
    result = AcceptResult(
        decision_id=decision_id, date=day, theory=theory.id,
        target=new_active, previous=previous, kept_as=kept_as, diff=diff,
        entry_text=text, log_path=path, dry_run=dry_run, written=not dry_run,
        data_tiebreak=tiebreak,
        trials_factor=view.trials_factor if tiebreak and view else None,
        override_reason=reason.strip() if override else "",
        stale_reasons=tuple(plan.stale) if override else (),
        notes=tuple(notes), store_calls=calls)
    if dry_run:
        return result
    writer(kept_as, kept)
    append_entry(path, text)
    try:
        _write_active(store, new_active, decision_id, note, tiebreak)
    except Exception as exc:
        append_entry(path, "**Store write failed.** The active configuration "
                     "did not change: %s: %s" % (type(exc).__name__, exc),
                     separate=False)
        raise
    return result


# -- retire / reinstate -------------------------------------------------------

def _standing_checks(theory: Any, fork_id: str, option_id: str,
                     decision_id: str, reason: str, log_path: Optional[Path]
                     ) -> Tuple[Any, List[str]]:
    refusals: List[str] = []
    if not is_decision_id(decision_id):
        refusals.append("%r is not a decision id (D-NNN)" % decision_id)
    if not reason.strip():
        refusals.append("a reason is required")
    if log_path is None:
        refusals.append("no decision log path: the theory provides none and "
                        "none was given")
    forks = theory.switches.forks()
    if fork_id not in forks or option_id not in forks[fork_id].option_ids():
        raise AcceptRefused(refusals + ["unknown option %s.%s"
                                        % (fork_id, option_id)])
    return forks[fork_id].option(option_id), refusals


def _status_call(store: Any, fork_id: str, option_id: str, status: str,
                 certainty: Optional[str], decision_id: str
                 ) -> Tuple[Optional[Callable[[], Any]], Tuple[str, ...]]:
    """The store call that records a new standing, or the edit to make."""
    writer = getattr(store, STATUS_WRITER, None)
    if callable(writer):
        return (lambda: writer(fork_id, option_id, status, certainty,
                               decision_id)), ()
    edit = ("declare %s.%s status=%s%s and add %s to its decision_refs (the "
            "selection store has no %s)" % (
                fork_id, option_id, status.upper(),
                " certainty=%s" % certainty if certainty else "", decision_id,
                STATUS_WRITER))
    return None, (edit,)


def _commit(path: Path, text: str, call: Optional[Callable[[], Any]]) -> None:
    append_entry(path, text)
    if call is not None:
        call()


def retire(theory: Any, fork_id: str, option_id: str, decision_id: str,
           certainty: str, reason: str, *, evidence: str = "",
           dry_run: bool = False, log_path: Union[None, str, Path] = None,
           date: Optional[str] = None) -> StandingChange:
    """Demote ``fork_id.option_id`` to DISABLED with ``certainty``.

    Refuses the option on the active path (accept a path without it first)
    and an option already retired with the same certainty. Never deletes.
    """
    path = _log_path(theory, log_path)
    option, refusals = _standing_checks(theory, fork_id, option_id,
                                        decision_id, reason, path)
    if certainty not in (CERTAIN, REASSESSABLE):
        refusals.append("certainty must be %r or %r" % (CERTAIN, REASSESSABLE))
    if theory.selections.active().mapping.get(fork_id) == option_id:
        refusals.append("%s.%s is on the active path; accept a path without "
                        "it first" % (fork_id, option_id))
    current = option.certainty or REASSESSABLE
    if option.status == DISABLED and current == certainty:
        refusals.append("%s.%s is already retired (%s)" % (fork_id, option_id,
                                                           certainty))
    target = "%s.%s" % (fork_id, option_id)
    if path is not None:
        refusals += _id_conflicts(DecisionLog.load(path), decision_id, RETIRE,
                                  target, None)
    if refusals:
        raise AcceptRefused(refusals)
    day = _today(date)
    text = render_retire(RetireEntry(
        decision_id=decision_id, date=day, theory=theory.id, fork=fork_id,
        option=option_id, certainty=certainty, reason=reason.strip(),
        previous_status=option.status, evidence=evidence.strip(),
        kill_condition=option.kill_condition))
    call, edits = _status_call(theory.selections, fork_id, option_id, DISABLED,
                               certainty, decision_id)
    if not dry_run:
        _commit(path, text, call)
    return StandingChange(
        decision_id=decision_id, date=day, fork=fork_id, option=option_id,
        old_status=option.status, new_status=DISABLED, certainty=certainty,
        entry_text=text, log_path=path, dry_run=dry_run, written=not dry_run,
        store_calls=("%s(%s, %s)" % (STATUS_WRITER, target, DISABLED),)
        if call else (), pending_edits=edits)


def reinstate(theory: Any, fork_id: str, option_id: str, decision_id: str,
              reason: str, *, dry_run: bool = False,
              log_path: Union[None, str, Path] = None,
              date: Optional[str] = None) -> StandingChange:
    """Put a DISABLED option back on the table as CONSIDERED. Never deletes."""
    path = _log_path(theory, log_path)
    option, refusals = _standing_checks(theory, fork_id, option_id,
                                        decision_id, reason, path)
    if option.status != DISABLED:
        refusals.append("%s.%s is %s, not DISABLED" % (fork_id, option_id,
                                                       option.status))
    target = "%s.%s" % (fork_id, option_id)
    if path is not None:
        refusals += _id_conflicts(DecisionLog.load(path), decision_id,
                                  REINSTATE, target, None)
    if refusals:
        raise AcceptRefused(refusals)
    day = _today(date)
    text = render_reinstate(ReinstateEntry(
        decision_id=decision_id, date=day, theory=theory.id, fork=fork_id,
        option=option_id, reason=reason.strip(),
        previous_certainty=option.certainty))
    call, edits = _status_call(theory.selections, fork_id, option_id,
                               CONSIDERED, None, decision_id)
    if not dry_run:
        _commit(path, text, call)
    return StandingChange(
        decision_id=decision_id, date=day, fork=fork_id, option=option_id,
        old_status=option.status, new_status=CONSIDERED, certainty=None,
        entry_text=text, log_path=path, dry_run=dry_run, written=not dry_run,
        store_calls=("%s(%s, %s)" % (STATUS_WRITER, target, CONSIDERED),)
        if call else (), pending_edits=edits)
