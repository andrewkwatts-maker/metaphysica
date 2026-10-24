"""Build the path graph of a theory: forks, options, constraints, decisions.

`build_graph(theory, assessment=None)` returns one JSON-ready dict (schema
``metaphysica.path_graph/2``) that the website Paths tab and the app both draw:

- nodes: the theory, every fork (kind, stage, binding, status, consumers,
  wired), every option (status, class, rationale sections, decision refs,
  priority, certainty, restored_from, kill condition, and assessment stats when
  an assessment is given), one decision node per decision referenced anywhere
  (date, title, status, summary from the decision log), and the theory's
  narrative nodes;
- edges: has_option, requires / excludes (from the declared constraints, with
  their rationale), decided_by (option, fork or narrative -> decision) and
  path_step along the active configuration (class ``active``) and along the
  configuration the assessment recommends (class ``recommended``);
- ``theory.active`` (name, digest, decided_by, why), the assessed
  ``configurations``, and the integer ``layout``.

This module also owns `assessment_view`, the one reader of an assessment
report's verdict and recommendation fields used outside the comparator (it is
one of the modules allowed to use ranking words). It reports what the
assessment says; it never compares configurations itself.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import (Any, Dict, Iterable, List, Mapping, Optional, Sequence,
                    Tuple, Union)

from metaphysica.testground import __version__
from metaphysica.testground.constraints import Excludes, Requires
from metaphysica.testground.decisions.log import DecisionLog, is_decision_id
from metaphysica.testground.graph.layout import (column_key,
                                                 constraint_depths,
                                                 layout_graph)
from metaphysica.testground.graph.lineage_graph import (add_lineage,
                                                        merge_declared)
from metaphysica.testground.graph.rationale import (decision_refs,
                                                    rationale_sections)
from metaphysica.testground.lineage.layout import layout_lineage
from metaphysica.testground.lineage.load import load_lineage
from metaphysica.testground.lineage.model import Lineage
from metaphysica.testground.switches.model import ACTIVE, DISABLED, Fork

__all__ = [
    "SCHEMA_ID",
    "OPTION_CLASSES",
    "LEGEND",
    "AssessmentView",
    "assessment_view",
    "load_assessment",
    "theory_node_id",
    "fork_node_id",
    "option_node_id",
    "decision_node_id",
    "fork_column_order",
    "build_graph",
]

SCHEMA_ID = "metaphysica.path_graph/2"

ACTIVE_CLASS = "active"
RECOMMENDED_CLASS = "recommended"
CONSIDERED_CLASS = "considered"
DISABLED_CLASS = "disabled"
RETIRED_CERTAIN_CLASS = "retired_certain"
NOT_IMPLEMENTED_CLASS = "not_implemented"
OPTION_CLASSES = (ACTIVE_CLASS, CONSIDERED_CLASS, DISABLED_CLASS,
                  RETIRED_CERTAIN_CLASS, NOT_IMPLEMENTED_CLASS)

DATA_TIEBREAK_VERDICT = "DATA_TIEBREAK_SUGGESTS"
DATA_CRITERION = "data"

#: What each class means and the colour the standalone viewer uses (the site
#: maps the classes onto its own CSS variables).
LEGEND: Dict[str, Dict[str, str]] = {
    ACTIVE_CLASS: {"label": "active path (generates the paper)",
                   "color": "#ffd93d"},
    RECOMMENDED_CLASS: {"label": "path the assessment recommends",
                        "color": "#4ade80"},
    CONSIDERED_CLASS: {"label": "considered: a live rival",
                       "color": "#4fc3f7"},
    DISABLED_CLASS: {"label": "retired (reassessable), kept runnable",
                     "color": "#8a8a99"},
    RETIRED_CERTAIN_CLASS: {"label": "retired (certain), archaeology only",
                            "color": "#5c5c6b"},
    NOT_IMPLEMENTED_CLASS: {"label": "declared, not implemented yet",
                            "color": "#b388ff"},
    "rejected": {"label": "assessed and rejected by a validity check",
                 "color": "#ff5c5c"},
    "trunk": {"label": "trunk: the line the theory followed",
              "color": "#e0c060"},
    "branch": {"label": "branch: explored alongside the trunk",
               "color": "#4fc3f7"},
    "dead_end": {"label": "dead end: abandoned, kept on record",
                 "color": "#ff8a65"},
}


# -- node ids ---------------------------------------------------------------

def theory_node_id(theory_id: str) -> str:
    return "theory:%s" % theory_id


def fork_node_id(fork_id: str) -> str:
    return "fork:%s" % fork_id


def option_node_id(fork_id: str, option_id: str) -> str:
    """Same form as `configurations.model.option_paths`."""
    return "option:%s.%s" % (fork_id, option_id)


def decision_node_id(ref: str) -> str:
    return "decision:%s" % ref


def _narrative_node_id(item_id: str) -> str:
    return "narrative:%s" % item_id


# -- the assessment, read ---------------------------------------------------

def _dig(data: Mapping[str, Any], *path: str) -> Any:
    node: Any = data
    for key in path:
        if not isinstance(node, Mapping):
            return None
        node = node.get(key)
    return node


def _first(data: Mapping[str, Any], paths: Iterable[Tuple[str, ...]]) -> Any:
    for path in paths:
        value = _dig(data, *path)
        if value is not None:
            return value
    return None


def _json_copy(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True))


@dataclass(frozen=True)
class AssessmentView:
    """What an assessment report says, in the fields the graph and accept use."""

    theory: Optional[str]
    mode: Optional[str]
    verdict: Optional[str]
    active_digest: Optional[str]
    engine_fingerprint: Optional[str]
    recommended_digest: Optional[str]
    deciding_criterion: Optional[str]
    trials_factor: Optional[int]
    margins: Dict[str, Any] = field(default_factory=dict)
    configurations: Tuple[Dict[str, Any], ...] = ()

    @property
    def proposed_digest(self) -> Optional[str]:
        """Alias of `recommended_digest` for modules outside the comparator."""
        return self.recommended_digest

    @property
    def data_tiebreak(self) -> bool:
        """True when agreement with data decided between tied configurations."""
        return (self.verdict == DATA_TIEBREAK_VERDICT
                or self.deciding_criterion == DATA_CRITERION)

    def configuration(self, digest: Optional[str]) -> Optional[Dict[str, Any]]:
        return next((c for c in self.configurations
                     if digest and c.get("digest") == digest), None)

    def top_group(self) -> Optional[int]:
        groups = [c["group"] for c in self.configurations
                  if isinstance(c.get("group"), int)]
        return min(groups) if groups else None


def assessment_view(assessment: Optional[Mapping[str, Any]]
                    ) -> Optional[AssessmentView]:
    """Read an assessment report (path_assessment.schema.json), or None.

    The engine fingerprint is looked for at the top level, then under
    ``controls``, ``provenance`` and ``active``; the trials factor under
    ``recommendation.trials_factor`` / ``recommendation.k`` /
    ``ranking.trials_factor``.
    """
    if not assessment:
        return None
    rec = assessment.get("recommendation") or {}
    k = _first(assessment, (("recommendation", "trials_factor"),
                            ("recommendation", "k"),
                            ("ranking", "trials_factor")))
    return AssessmentView(
        theory=assessment.get("theory"),
        mode=assessment.get("mode"),
        verdict=assessment.get("verdict"),
        active_digest=_dig(assessment, "active", "digest"),
        engine_fingerprint=_first(assessment, (
            ("engine_fingerprint",), ("controls", "engine_fingerprint"),
            ("provenance", "engine_fingerprint"),
            ("active", "engine_fingerprint"))),
        recommended_digest=rec.get("digest") if isinstance(rec, Mapping)
        else None,
        deciding_criterion=rec.get("deciding_criterion")
        if isinstance(rec, Mapping) else None,
        trials_factor=k if isinstance(k, int) and not isinstance(k, bool)
        else None,
        margins=_json_copy(rec.get("margins") or {})
        if isinstance(rec, Mapping) else {},
        configurations=tuple(_json_copy(c) for c in
                             assessment.get("configurations") or ()),
    )


def load_assessment(path: Union[str, Path]) -> Dict[str, Any]:
    """An assessment report from disk (UTF-8 JSON)."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


# -- forks and the active path ----------------------------------------------

def fork_column_order(forks: Mapping[str, Fork],
                      constraints: Sequence[Any]) -> List[str]:
    """Fork ids in column order (constraint depth, kind, declaration)."""
    ids = list(forks)
    depths = constraint_depths(ids, constraints)
    return sorted(ids, key=lambda f: column_key(depths[f], forks[f].kind,
                                                ids.index(f)))


def _declared_active(fork: Fork) -> Optional[str]:
    """The option the declarations mark ACTIVE, if exactly one."""
    marked = fork.options_by_status(ACTIVE)
    return marked[0] if len(marked) == 1 else None


def _active_option(fork: Fork, selection: Mapping[str, str]) -> Tuple[str, str]:
    """(option on the active path, where it came from).

    The selection store decides; a fork it does not mention falls back to the
    fork's legacy option, then to the declared ACTIVE option, then (flagged
    ``unresolved``) to its first option.
    """
    if fork.id in selection:
        return selection[fork.id], "store"
    if fork.legacy_option:
        return fork.legacy_option, "legacy"
    declared = _declared_active(fork)
    if declared is not None:
        return declared, "declaration"
    if not any(o.implemented for o in fork.options):
        return "", "undeclared"      # a declared-only fork has no path option
    return fork.options[0].id, "unresolved"


def _option_class(option: Any, on_active: bool) -> str:
    if on_active:
        return ACTIVE_CLASS
    if not option.implemented:
        return NOT_IMPLEMENTED_CLASS
    if option.retired_certain:
        return RETIRED_CERTAIN_CLASS
    if option.status == DISABLED:
        return DISABLED_CLASS
    return CONSIDERED_CLASS


def _option_refs(option: Any) -> List[str]:
    refs = list(option.decision_refs)
    for ref in decision_refs(option.summary + "\n" + option.consequence):
        if ref not in refs:
            refs.append(ref)
    return refs


def _option_stats(view: AssessmentView, fork_id: str, option_id: str,
                  recommended: Mapping[str, str]) -> Dict[str, Any]:
    rows = [c for c in view.configurations
            if (c.get("selection") or {}).get(fork_id) == option_id]
    top = view.top_group()
    verdicts = Counter(str(c.get("verdict")) for c in rows)
    return {
        "assessed": len(rows),
        "verdicts": dict(sorted(verdicts.items())),
        "top_group": sum(1 for c in rows
                         if top is not None and c.get("group") == top),
        "recommended": recommended.get(fork_id) == option_id,
    }


# -- graph assembly -----------------------------------------------------------

class _Builder:
    """Accumulates nodes, edges and referenced decisions in a fixed order."""

    def __init__(self) -> None:
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self._edge_keys: Dict[Tuple[str, str, str], int] = {}
        self.refs: Dict[str, None] = {}
        self.warnings: List[str] = []

    def node(self, node: Dict[str, Any]) -> None:
        self.nodes.append(node)

    def edge(self, kind: str, source: str, target: str,
             cls: Optional[str] = None, rationale: Optional[str] = None,
             attrs: Optional[Dict[str, Any]] = None) -> None:
        key = (kind, source, target)
        if key in self._edge_keys:
            existing = self.edges[self._edge_keys[key]]
            if cls == ACTIVE_CLASS:
                existing["class"] = ACTIVE_CLASS
            return
        edge: Dict[str, Any] = {"type": kind, "source": source,
                                "target": target, "class": cls,
                                "rationale": rationale}
        if attrs:
            edge["attrs"] = attrs
        self._edge_keys[key] = len(self.edges)
        self.edges.append(edge)

    def cite(self, source: str, refs: Iterable[str],
             cls: Optional[str] = None) -> None:
        for ref in refs:
            self.refs.setdefault(ref, None)
            self.edge("decided_by", source, decision_node_id(ref), cls)


def _fork_node(fork: Fork, order: int, depth: int, column: int,
               active: Tuple[str, str], refs: List[str]) -> Dict[str, Any]:
    return {
        "id": fork_node_id(fork.id), "type": "fork", "label": fork.id,
        "status": fork.status, "class": fork.kind,
        "attrs": {
            "fork": fork.id, "kind": fork.kind, "stage": fork.stage,
            "binding": fork.binding, "status": fork.status,
            "consumers": list(fork.consumers), "wired": bool(fork.consumers),
            "question": fork.question, "source": fork.source,
            "legacy_option": fork.legacy_option, "depth": depth,
            "order": order, "column": column, "active_option": active[0],
            "active_from": active[1], "n_options": len(fork.options),
            "decision_refs": refs,
        },
        "rationale": {"summary": fork.question,
                      "sections": rationale_sections(fork.notes),
                      "decision_refs": refs},
    }


def _option_node(fork: Fork, option: Any, order: int, on_active: bool,
                 on_recommended: bool, refs: List[str],
                 stats: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    node: Dict[str, Any] = {
        "id": option_node_id(fork.id, option.id), "type": "option",
        "label": option.id, "status": option.status,
        "class": _option_class(option, on_active),
        "attrs": {
            "fork": fork.id, "order": order, "priority": option.priority,
            "certainty": option.certainty,
            "implemented": option.implemented,
            "adds_discrete_input": option.adds_discrete_input,
            "restored_from": option.restored_from,
            "kill_condition": option.kill_condition,
            "decision_refs": refs, "summary": option.summary,
            "on_active_path": on_active,
            "on_recommended_path": on_recommended,
            "declared_active": option.status == ACTIVE,
            "legacy": fork.legacy_option == option.id,
        },
        "rationale": {"summary": option.summary,
                      "sections": rationale_sections(option.consequence),
                      "decision_refs": refs},
    }
    if stats is not None:
        node["stats"] = stats
    return node


def _add_forks(b: _Builder, forks: Mapping[str, Fork], order: List[str],
               depths: Mapping[str, int], active: Mapping[str, Tuple[str, str]],
               recommended: Mapping[str, str],
               view: Optional[AssessmentView]) -> None:
    declared = list(forks)
    for column, fork_id in enumerate(order):
        fork = forks[fork_id]
        refs = list(decision_refs(fork.notes))
        b.node(_fork_node(fork, declared.index(fork_id), depths[fork_id],
                          column, active[fork_id], refs))
        b.cite(fork_node_id(fork_id), refs)
        for i, option in enumerate(fork.options):
            on_active = active[fork_id][0] == option.id
            o_refs = _option_refs(option)
            stats = (_option_stats(view, fork_id, option.id, recommended)
                     if view is not None else None)
            node = _option_node(fork, option, i, on_active,
                                recommended.get(fork_id) == option.id,
                                o_refs, stats)
            b.node(node)
            b.edge("has_option", fork_node_id(fork_id), node["id"],
                   node["class"])
            b.cite(node["id"], o_refs, ACTIVE_CLASS if on_active else None)


def _known(forks: Mapping[str, Fork], fork_id: str, option_id: str) -> bool:
    return fork_id in forks and option_id in forks[fork_id].option_ids()


def _add_constraints(b: _Builder, forks: Mapping[str, Fork],
                     constraints: Sequence[Any]) -> None:
    for c in constraints:
        attrs = {"source": c.source, "constraint": c.describe()}
        if isinstance(c, Requires):
            pairs = [((c.fork, c.option), (c.needs_fork, o))
                     for o in sorted(c.needs_options)]
            kind = "requires"
        elif isinstance(c, Excludes):
            pairs = [((c.fork_a, c.option_a), (c.fork_b, c.option_b))]
            kind = "excludes"
        else:
            b.warnings.append("unknown constraint type %s" % type(c).__name__)
            continue
        for (fa, oa), (fb, ob) in pairs:
            if not (_known(forks, fa, oa) and _known(forks, fb, ob)):
                b.warnings.append("constraint %s names an undeclared option"
                                  % c.describe())
                continue
            b.edge(kind, option_node_id(fa, oa), option_node_id(fb, ob),
                   "constraint", c.rationale, attrs)


def _add_path(b: _Builder, theory_id: str, order: List[str],
              selection: Mapping[str, str], cls: str) -> None:
    steps = [theory_node_id(theory_id)] + [
        option_node_id(f, selection[f]) for f in order if f in selection]
    for source, target in zip(steps, steps[1:]):
        b.edge("path_step", source, target, cls)


def _narrative_nodes(b: _Builder, narrative: Sequence[Mapping[str, Any]]
                     ) -> None:
    for i, item in enumerate(narrative):
        item_id = str(item.get("id") or "narrative-%d" % (i + 1))
        text = str(item.get("text", ""))
        summary = str(item.get("summary", ""))
        refs = list(item.get("decision_refs", ()))
        refs += [r for r in decision_refs(summary + "\n" + text)
                 if r not in refs]
        attrs = {k: v for k, v in sorted(item.items())
                 if k not in ("text", "summary", "decision_refs")}
        node_id = _narrative_node_id(item_id)
        b.node({"id": node_id, "type": "narrative",
                "label": str(item.get("label") or item.get("title") or item_id),
                "status": item.get("status"), "class": "narrative",
                "attrs": _json_copy(attrs),
                "rationale": {"summary": summary,
                              "sections": rationale_sections(text),
                              "decision_refs": refs}})
        b.cite(node_id, refs)


def _decision_node(ref: str, log: Optional[DecisionLog]) -> Dict[str, Any]:
    decision = log.decision(ref) if (log is not None
                                     and is_decision_id(ref)) else None
    if decision is not None:
        attrs = decision.as_dict()
        attrs["decision_id"] = attrs.pop("id")
        attrs["in_log"] = True
        return {"id": decision_node_id(ref), "type": "decision", "label": ref,
                "status": decision.status, "class": "decision",
                "attrs": attrs}
    is_ruling = ref.startswith("ruling:")
    date = ref.split(":", 1)[1] if is_ruling else None
    return {"id": decision_node_id(ref), "type": "decision",
            "label": ref.replace(":", " ") if is_ruling else ref,
            "status": "RULING" if is_ruling else "NOT IN LOG",
            "class": "ruling" if is_ruling else "decision",
            "attrs": {"decision_id": ref, "date": date,
                      "title": "ruling of %s" % date if is_ruling else "",
                      "status": "RULING" if is_ruling else "NOT IN LOG",
                      "summary": "", "entries": [], "in_log": False}}


def _resolve_log(theory: Any, decision_log: Union[None, DecisionLog, str, Path]
                 ) -> Optional[DecisionLog]:
    if isinstance(decision_log, DecisionLog):
        return decision_log
    if decision_log is not None:
        return DecisionLog.load(decision_log)
    provider = getattr(theory, "decisions", None)
    path = provider.decision_log_path() if provider is not None else None
    return DecisionLog.load(path) if path is not None else None


def _active_block(cfg: Any, forks: Mapping[str, Fork],
                  active: Mapping[str, Tuple[str, str]],
                  log: Optional[DecisionLog],
                  view: Optional[AssessmentView]) -> Dict[str, Any]:
    decided = {f: list(ids) for f, ids in cfg.decided_by}
    why = list(cfg.reasons)
    for ref in sorted({r for ids in decided.values() for r in ids}):
        decision = log.decision(ref) if log is not None else None
        why.append("%s — %s" % (ref, decision.title) if decision else ref)
    if view is not None:
        why.append("assessment verdict: %s" % view.verdict)
    return {
        "name": cfg.name, "digest": cfg.digest, "lifecycle": cfg.lifecycle,
        "decided_by": decided, "why": why,
        "missing_forks": sorted(f for f, (_, src) in active.items()
                                if src != "store"),
        "drift": sorted(f for f in forks
                        if _declared_active(forks[f]) not in (None,
                                                              active[f][0])),
        "verdict": view.verdict if view is not None else None,
    }


def _recommended_block(view: Optional[AssessmentView], active_digest: str,
                       active_sel: Mapping[str, str]
                       ) -> Tuple[Optional[Dict[str, Any]], Dict[str, str]]:
    if view is None or not view.recommended_digest:
        return None, {}
    cfg = view.configuration(view.recommended_digest) or {}
    selection = dict(cfg.get("selection") or {})
    full = dict(active_sel)
    full.update(selection)
    differs = {f: [active_sel.get(f), full[f]] for f in sorted(full)
               if active_sel.get(f) != full[f]}
    block = {"digest": view.recommended_digest, "name": cfg.get("name"),
             "verdict": view.verdict,
             "deciding_criterion": view.deciding_criterion,
             "trials_factor": view.trials_factor,
             "is_active": view.recommended_digest == active_digest,
             "differs": differs}
    return block, full


def _configurations(view: Optional[AssessmentView], order: List[str],
                    active_digest: str) -> List[Dict[str, Any]]:
    if view is None:
        return []
    out = []
    for cfg in view.configurations:
        selection = cfg.get("selection") or {}
        row = dict(cfg)
        row["path"] = [option_node_id(f, selection[f]) for f in order
                       if f in selection]
        row["is_active"] = cfg.get("digest") == active_digest
        row["is_recommended"] = cfg.get("digest") == view.recommended_digest
        out.append(row)
    return out


def _load_lineage(theory: Any) -> Optional[Lineage]:
    path = getattr(theory, "lineage", None)
    if path is None:
        return None
    return load_lineage(path, theory.switches.forks())


def build_graph(theory: Any, assessment: Optional[Mapping[str, Any]] = None,
                decision_log: Union[None, DecisionLog, str, Path] = None
                ) -> Dict[str, Any]:
    """The path graph of ``theory`` (dict valid against path_graph.schema.json).

    ``decision_log`` defaults to the theory's own log (its
    DecisionLogProvider); decisions not found there are drawn as NOT IN LOG.
    """
    lineage = _load_lineage(theory)
    forks = merge_declared(theory.switches.forks(), lineage)
    constraints = list(theory.switches.constraints())
    cfg = theory.selections.active()
    log = _resolve_log(theory, decision_log)
    view = assessment_view(assessment)
    order = fork_column_order(forks, constraints)
    depths = constraint_depths(list(forks), constraints)
    active = {f: _active_option(forks[f], cfg.mapping) for f in forks}
    active_sel = {f: o for f, (o, _) in active.items() if o}
    rec_block, rec_sel = _recommended_block(view, cfg.digest, active_sel)
    if rec_block is not None and rec_block["is_active"]:
        rec_sel = {}

    b = _Builder()
    if log is None and getattr(theory, "decisions", None) is not None:
        b.warnings.append("decision log not found: decisions are drawn as "
                          "NOT IN LOG")
    b.node({"id": theory_node_id(theory.id), "type": "theory",
            "label": theory.title, "status": "ACTIVE", "class": "theory",
            "attrs": {"theory": theory.id, "env_prefix": theory.env_prefix,
                      "n_forks": len(forks),
                      "n_options": sum(len(f.options) for f in forks.values()),
                      "n_constraints": len(constraints)}})
    _add_forks(b, forks, order, depths, active, rec_sel, view)
    _add_constraints(b, forks, constraints)
    _narrative_nodes(b, theory.narrative)
    if lineage is not None:
        add_lineage(b, lineage)
    for fork_id, ids in cfg.decided_by:
        if fork_id in active:
            b.cite(option_node_id(fork_id, active[fork_id][0]), ids,
                   ACTIVE_CLASS)
    _add_path(b, theory.id, order, active_sel, ACTIVE_CLASS)
    if rec_sel:
        _add_path(b, theory.id, order, rec_sel, RECOMMENDED_CLASS)
    decisions = [_decision_node(ref, log) for ref in sorted(b.refs)]
    b.nodes.extend(decisions)

    graph: Dict[str, Any] = {
        "schema": SCHEMA_ID,
        "theory": {"id": theory.id, "title": theory.title,
                   "active": _active_block(cfg, forks, active, log, view),
                   "recommended": rec_block},
        "provenance": {
            "generator": "metaphysica.testground.graph",
            "testground_version": __version__,
            "decision_log": log.path.name if log is not None and log.path
            else None,
            "assessment": None if view is None else {
                "mode": view.mode, "verdict": view.verdict,
                "active_digest": view.active_digest,
                "engine_fingerprint": view.engine_fingerprint,
                "stale_active": view.active_digest != cfg.digest},
            "warnings": b.warnings,
        },
        "legend": LEGEND,
        "nodes": b.nodes,
        "edges": b.edges,
        "configurations": _configurations(view, order, cfg.digest),
        "decisions": [{k: n["attrs"][k] for k in
                       ("decision_id", "date", "title", "status", "in_log")}
                      for n in decisions],
    }
    graph = _json_copy(graph)
    graph["layout"] = layout_graph(graph)
    if lineage is not None:
        graph["layout"]["lineage"] = layout_lineage(lineage)
    graph["views"] = ["lineage", "switches"] if lineage else ["switches"]
    return graph
