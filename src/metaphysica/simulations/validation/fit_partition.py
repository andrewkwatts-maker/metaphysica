"""Generic fit bookkeeping: one scored row per observable, predictions only.

No PM import. The PM binding (``PM/validation/observables.py``) supplies the
observable groups and the status vocabulary; this module applies them.

Rows are dicts with ``path``, ``status`` (the verdict), ``registry_status``,
``predicted_value``, ``experimental_value``, ``uncertainty``, ``sigma`` and
``bound_type``.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence

Row = Dict[str, Any]


def chi_squared(rows: Iterable[Row]) -> Dict[str, Any]:
    """chi2 and N over rows that carry a value, a reference and an error > 0."""
    chi, n = 0.0, 0
    for row in rows:
        unc = float(row["uncertainty"])
        if unc <= 0:
            raise ValueError(f"{row.get('path')}: uncertainty must be > 0")
        chi += ((float(row["predicted_value"])
                 - float(row["experimental_value"])) / unc) ** 2
        n += 1
    return {"chi_squared": chi, "n": n,
            "reduced": (chi / n) if n else None}


def kind_of(row: Row, non_pred_statuses: Mapping[str, str],
            non_pred_verdicts: Mapping[str, str]) -> str:
    """Return 'prediction' or the name of the non-prediction block."""
    verdict = str(row.get("status") or "").upper()
    if verdict in non_pred_verdicts:
        return non_pred_verdicts[verdict]
    reg = str(row.get("registry_status") or "").upper()
    return non_pred_statuses.get(reg, "prediction")


def _group_index(groups: Mapping[str, Sequence[str]]) -> Dict[str, str]:
    index: Dict[str, str] = {}
    for name, members in groups.items():
        for path in members:
            if path in index:
                raise ValueError(f"{path} is in groups {index[path]} and {name}")
            index[path] = name
    return index


def _dup_entry(row: Row, primary: str) -> Row:
    return {"path": row["path"], "duplicate_of": primary,
            "sigma": row.get("sigma"), "verdict": row.get("status")}


def dedupe_by_group(rows: Sequence[Row], groups: Mapping[str, Sequence[str]]):
    """Keep the first row of each group (in group order); return (kept, dups)."""
    index = _group_index(groups)
    by_path = {r["path"]: r for r in rows}
    first: Dict[str, Row] = {}
    dups: List[Row] = []
    for name, members in groups.items():
        present = [by_path[p] for p in members if p in by_path]
        if not present:
            continue
        first[name] = present[0]
        dups += [_dup_entry(r, present[0]["path"]) for r in present[1:]]
    kept = [r for r in rows
            if r["path"] not in index or first[index[r["path"]]] is r]
    return kept, dups


def undeclared_duplicates(rows: Sequence[Row]) -> List[List[str]]:
    """Scored rows sharing one experimental reference (value and error)."""
    seen: Dict[tuple, List[str]] = {}
    for r in rows:
        key = (float(r["experimental_value"]), float(r["uncertainty"]))
        seen.setdefault(key, []).append(r["path"])
    return sorted(sorted(v) for v in seen.values() if len(v) > 1)


def top_contributors(rows: Sequence[Row], limit: int = 10) -> List[Row]:
    """Rows ranked by their share of chi2."""
    total = chi_squared(rows)["chi_squared"]
    out = []
    for r in rows:
        c = chi_squared([r])["chi_squared"]
        out.append({"path": r["path"], "chi_squared": c,
                    "share": (c / total) if total else None,
                    "verdict": r.get("status"),
                    "registry_status": r.get("registry_status")})
    return sorted(out, key=lambda d: -d["chi_squared"])[:limit]


def partition(rows: Sequence[Row], groups: Mapping[str, Sequence[str]],
              non_pred_statuses: Mapping[str, str],
              non_pred_verdicts: Mapping[str, str],
              scoring_verdicts: Iterable[str]) -> Dict[str, Any]:
    """Split rows into scored predictions, duplicates and non-predictions.

    ``non_predictions`` carry no sigma: a tuned, circular, identity or
    unit-check row is reported, never scored and never counted as PASS.
    """
    scoring = frozenset(scoring_verdicts)
    preds: List[Row] = []
    non_preds: List[Row] = []
    for r in rows:
        kind = kind_of(r, non_pred_statuses, non_pred_verdicts)
        if kind != "prediction":
            non_preds.append({"path": r["path"], "kind": kind,
                              "registry_status": r.get("registry_status"),
                              "verdict_reported": r.get("status")})
        elif r.get("status") in scoring and r.get("comparable", True):
            preds.append(r)
    scored, dups = dedupe_by_group(preds, groups)
    return {"scored": scored, "duplicates": dups,
            "non_predictions": non_preds,
            "undeclared_duplicates": undeclared_duplicates(scored)}


def fit_summary(scored: Sequence[Row], withdrawn_status: str = "FALSIFIED"):
    """The three published numbers, each computed from the rows with its N."""
    live = [r for r in scored
            if str(r.get("registry_status") or "").upper() != withdrawn_status]
    return {
        "all_scoring_rows": {
            **chi_squared(scored),
            "label": "all scored predictions, recorded falsifications "
                     "included, duplicates removed (headline)"},
        "excluding_falsified": {
            **chi_squared(live),
            "label": f"same without rows recorded as {withdrawn_status}"},
        "top_contributors": top_contributors(scored),
        "scored_rows": [
            {"path": r["path"], "verdict": r.get("status"),
             "sigma": abs(float(r["predicted_value"])
                          - float(r["experimental_value"]))
                      / float(r["uncertainty"])} for r in scored],
        "withdrawn_rows": sorted(
            ({"path": r["path"], "sigma": r.get("sigma"),
              "verdict": r.get("status")} for r in scored
             if r not in live), key=lambda d: -(d["sigma"] or 0.0)),
    }
