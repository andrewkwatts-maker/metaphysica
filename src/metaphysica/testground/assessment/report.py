"""The path-assessment report: one JSON document per assessment run.

Builds the dict that ``path_assessment.json`` holds (schema
``schemas/path_assessment.schema.json``): every assessed configuration with
its scores and verdict, the standing failures (disclosed, amendment (c)), the
comparator's groups and tie-breaks, the active configuration's place, and the
recommendation -- which is only ever a recommendation (adoption is an explicit
accept).

Pre-registration and kill conditions
====================================
The report records the sha256 of the assessment configuration. Given the
sha256 recorded in the D-019 annex, it checks K5; K1 (published build), K3
(null control) are supplied by the caller in ``controls``. A fired K1, K3 or
K5 VOIDS the run: the verdict is UNDECIDED and no recommendation is made. K4
is enforced by the comparator itself (a deciding criterion never rests on an
UNMEASURED value; such comparisons are UNDECIDED). K2 voids only the screen
rejections of the forks involved -- the caller marks those configurations.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import (Any, Dict, FrozenSet, Iterable, List, Mapping, Optional,
                    Sequence)

from metaphysica.testground.assessment.comparator import (compare, groups_of,
                                                          rank, unranked)
from metaphysica.testground.assessment.config import (AssessmentConfig,
                                                      policy_drift)
from metaphysica.testground.assessment.recommend import (UNDECIDED,
                                                         recommend)
from metaphysica.testground.assessment.score import (CRITERIA,
                                                     CriterionScore,
                                                     ScoreVector)
from metaphysica.testground.assessment.tiebreak import tiebreak
from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.theory import ScoredRow

__all__ = [
    "SCHEMA_ID",
    "SCHEMA_PATH",
    "MODES",
    "VOIDING_CONTROLS",
    "normalize_mode",
    "score_dict",
    "k5_control",
    "voided_by",
    "build_report",
    "validate_report",
    "dumps_report",
]

SCHEMA_ID = "metaphysica.path_assessment/1"
SCHEMA_PATH = (Path(__file__).resolve().parents[1] / "schemas"
               / "path_assessment.schema.json")
MODES = ("assess", "reassess", "archaeology", "single")
#: Kill conditions whose firing voids the whole run.
VOIDING_CONTROLS = ("K1", "K3", "K5")


def normalize_mode(mode: str) -> str:
    """``ASSESS`` / ``assess`` -> ``assess``; refuses modes the schema lacks."""
    value = str(mode).strip().lower().replace("-", "_")
    if value not in MODES:
        raise ValueError("mode %r has no path_assessment report (schema "
                         "modes: %s)" % (mode, ", ".join(MODES)))
    return value


def score_dict(s: CriterionScore) -> Dict[str, Any]:
    return {
        "key": list(s.key) if s.key is not None else None,
        "status": s.status,
        "components": dict(sorted(s.components.items())),
        "failures": list(s.failures),
        "unmeasured": list(s.unmeasured),
    }


def _configuration_entry(cfg: Configuration, v: ScoreVector,
                         group: Optional[int]) -> Dict[str, Any]:
    return {
        "digest": cfg.digest,
        "name": cfg.name,
        "selection": cfg.mapping,
        "lifecycle": cfg.lifecycle,
        "verdict": v.verdict,
        "stage_reached": v.stage_reached,
        "group": group,
        "scores": {s.criterion: score_dict(s) for s in v.scores},
        "reasons": list(v.reasons),
    }


def k5_control(assess_cfg: AssessmentConfig,
               recorded_sha256: Optional[str]) -> Dict[str, Any]:
    """K5: the assessment configuration's sha256 against the annex."""
    if not recorded_sha256:
        return {"checked": False, "fired": False, "sha256": assess_cfg.sha256,
                "detail": "no annex sha256 supplied"}
    fired = not assess_cfg.matches(recorded_sha256)
    return {"checked": True, "fired": fired, "sha256": assess_cfg.sha256,
            "recorded_sha256": recorded_sha256,
            "detail": ("the assessment configuration differs from the annex"
                       if fired else "matches the annex")}


def voided_by(controls: Mapping[str, Any]) -> List[str]:
    """The voiding kill conditions that fired."""
    return [k for k in VOIDING_CONTROLS
            if isinstance(controls.get(k), Mapping)
            and controls[k].get("fired") is True]


def _check_alignment(configurations: Sequence[Configuration],
                     vectors: Mapping[str, ScoreVector]) -> None:
    digests = [c.digest for c in configurations]
    missing = sorted(set(digests) - set(vectors))
    extra = sorted(set(vectors) - set(digests))
    if missing or extra or len(set(digests)) != len(digests):
        raise ValueError("configurations and score vectors do not match "
                         "(no vector: %s; no configuration: %s)"
                         % (missing, extra))


def _check_policy(configurations: Sequence[Configuration], active: str,
                  policy_forks: Sequence[str]) -> None:
    """Amendment (d): policy forks are held at their active option."""
    by = {c.digest: c for c in configurations}
    if active not in by or not policy_forks:
        return
    held = by[active].mapping
    drift = {c.digest: policy_drift(c.mapping, held, policy_forks)
             for c in configurations}
    drift = {d: f for d, f in drift.items() if f}
    if drift:
        raise ValueError("policy forks not held at the active option "
                         "(amendment (d)): %s" % drift)


def _ranking(vectors: Sequence[ScoreVector],
             rows: Optional[Mapping[str, Sequence[ScoredRow]]]
             ) -> Dict[str, Any]:
    groups = groups_of(vectors)
    return {
        "comparator": "lexicographic over %s; data is a tie-break only "
                      "(D-019)" % ", ".join(CRITERIA),
        "groups": rank(vectors, rows),
        "tiebreaks": [dict(tiebreak(g, rows).as_dict(), group=i)
                      for i, g in enumerate(groups) if len(g) > 1],
        "unranked": unranked(vectors),
    }


def _active_section(active: str, configurations: Sequence[Configuration],
                    by: Mapping[str, ScoreVector],
                    groups: List[List[str]]) -> Dict[str, Any]:
    cfg = next((c for c in configurations if c.digest == active), None)
    group = next((i for i, g in enumerate(groups) if active in g), None)
    out: Dict[str, Any] = {
        "digest": active,
        "name": cfg.name if cfg else None,
        "verdict": by[active].verdict if active in by else None,
        "group": group,
        "in_top_group": group == 0,
    }
    if groups and active in by and group != 0:
        out["comparison_with_top"] = compare(by[groups[0][0]],
                                             by[active]).as_dict()
    return out


def build_report(*, theory: str, mode: str,
                 configurations: Sequence[Configuration],
                 vectors: Iterable[ScoreVector], active_digest: str,
                 assess_cfg: Optional[AssessmentConfig] = None,
                 standing: FrozenSet[str] = frozenset(),
                 rows: Optional[Mapping[str, Sequence[ScoredRow]]] = None,
                 enumeration: Optional[Mapping[str, Any]] = None,
                 controls: Optional[Mapping[str, Any]] = None,
                 recorded_sha256: Optional[str] = None,
                 generated_at: Optional[str] = None) -> Dict[str, Any]:
    """The ``path_assessment.json`` dict for one assessment run."""
    assess_cfg = assess_cfg or AssessmentConfig.empty()
    vector_list = list(vectors)
    by = {v.digest: v for v in vector_list}
    _check_alignment(configurations, by)
    _check_policy(configurations, active_digest, assess_cfg.policy_forks)
    ranking = _ranking(vector_list, rows)
    group_of = {d: i for i, g in enumerate(ranking["groups"]) for d in g}
    all_controls = dict(controls or {})
    all_controls["K5"] = k5_control(assess_cfg, recorded_sha256)
    all_controls.setdefault("K4", {
        "fired": False, "guard": "the comparator never decides on an "
        "UNMEASURED value; such comparisons are UNDECIDED"})
    verdict, rec = recommend(active_digest, vector_list, rows)
    recommendation = rec.as_dict() if rec else None
    void = voided_by(all_controls)
    if void:
        verdict = UNDECIDED
        recommendation = {"active": active_digest, "target": None,
                          "void": True, "reasons": [
                              "run void: kill condition %s fired" % k
                              for k in void]}
    report: Dict[str, Any] = {
        "schema": SCHEMA_ID,
        "theory": theory,
        "mode": normalize_mode(mode),
        "criteria_order": list(CRITERIA),
        "pre_registration": dict(assess_cfg.summary(),
                                 recorded_sha256=recorded_sha256,
                                 k5=all_controls["K5"]),
        "enumeration": dict(enumeration or {},
                            assessed=len(vector_list)),
        "controls": all_controls,
        "standing_failures": sorted(standing),
        "configurations": [_configuration_entry(c, by[c.digest],
                                                group_of.get(c.digest))
                           for c in configurations],
        "ranking": ranking,
        "active": _active_section(active_digest, configurations, by,
                                  ranking["groups"]),
        "recommendation": recommendation,
        "verdict": verdict,
    }
    if generated_at is not None:
        report["generated_at"] = generated_at
    return report


def _structural_errors(report: Mapping[str, Any],
                       schema: Mapping[str, Any]) -> List[str]:
    """A small check used only when jsonschema is not installed."""
    errors = ["missing %r" % k for k in schema["required"] if k not in report]
    props = schema["properties"]
    if report.get("schema") != props["schema"]["const"]:
        errors.append("schema id")
    if report.get("criteria_order") != props["criteria_order"]["const"]:
        errors.append("criteria_order")
    if report.get("verdict") not in props["verdict"]["enum"]:
        errors.append("verdict")
    item = props["configurations"]["items"]
    for cfg in report.get("configurations", ()):
        errors += ["configuration missing %r" % k for k in item["required"]
                   if k not in cfg]
        if cfg.get("verdict") not in item["properties"]["verdict"]["enum"]:
            errors.append("configuration verdict %r" % cfg.get("verdict"))
    return errors


def validate_report(report: Mapping[str, Any]) -> List[str]:
    """Schema errors of ``report`` (empty when valid)."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        import jsonschema
    except ImportError:  # pragma: no cover - jsonschema is installed here
        return _structural_errors(report, schema)
    validator = jsonschema.Draft202012Validator(schema)
    return sorted(e.message for e in validator.iter_errors(report))


def dumps_report(report: Mapping[str, Any]) -> str:
    """Deterministic JSON text (sorted keys) for ``path_assessment.json``."""
    return json.dumps(report, indent=2, sort_keys=True, default=str) + "\n"
