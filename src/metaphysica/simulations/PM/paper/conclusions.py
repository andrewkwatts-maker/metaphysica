"""Section 7 conclusions, generated from live state.

Nothing here is a literal result. Geometry comes from
``closed_geometry.certificate.certificate()`` (labels CG.x); fit quality from
the build artifacts ``statistical_rigor_report.json`` (chi^2) and
``validation_report.json`` (PASS/MARGINAL/TENSION/FAIL counts), located next
to ``parameters.json`` by the existing resolver
``core.parameter_artifact``; each physics conclusion reads its value and its
status from the registry row and maps the registry status onto one of
derived / calibrated / fitted / open / predicted.

A missing artifact is shown, in the text, as NOT AVAILABLE. It is never
replaced by a number.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from metaphysica.simulations.base import ContentBlock
from metaphysica.simulations.core.parameter_artifact import params_source

STATUS_TAGS = ("derived", "calibrated", "fitted", "open", "predicted")
ADOPTED_PATH = "seed_43_joyce"
PATHS_LINK = "paths.html#b3_seed--seed_24"

#: registry status -> status tag. Inputs (ESTABLISHED, MEASURED, ...) are
#: deliberately absent: an input is not a conclusion, so mapping one is an error.
_STATUS_MAP = {
    "DERIVED": "derived", "GEOMETRIC": "derived", "EXACT": "derived",
    "TERMINAL": "derived", "FOUNDATIONAL": "derived",
    "CALIBRATED": "calibrated", "ANCHORED": "calibrated",
    "FITTED": "fitted", "FITTED_COMPOSITE": "fitted",
    "RETRODICTED_VARIANT": "fitted",
    "PREDICTED": "predicted", "PREDICTIONS": "predicted",
    "ANSATZ": "open", "SPECULATIVE": "open", "TOPOLOGY_CANDIDATE": "open",
    "FALSIFIED": "open",
}

#: certificate labels shown as the geometry statements of 7.1
GEOMETRY_LABELS = ("(CG.1)", "(CG.2)", "(CG.3)", "(CG.4)", "(CG.9)",
                   "(CG.12)", "(CG.13)")
#: certificate labels that say a modulus or construction is unresolved
OPEN_GEOMETRY_LABELS = ("(CG.6)", "(CG.10)")


def status_tag(registry_status: str) -> str:
    """Map a registry status onto a tag; an unmapped status is an error."""
    key = str(registry_status).upper()
    if key not in _STATUS_MAP:
        raise ValueError(
            "registry status %r has no conclusion tag (inputs and "
            "validation rows are not conclusions)" % registry_status)
    return _STATUS_MAP[key]


@dataclass(frozen=True)
class Conclusion:
    """One physics conclusion: where its value and status are read from."""
    key: str
    title: str
    path: str
    fmt: str = "{:.5g}"
    units: str = ""
    expect: Optional[str] = None      # name of a live-seed cross-check


CONCLUSIONS: Tuple[Conclusion, ...] = (
    Conclusion("n_gen", "Fermion generations", "geometry.n_generations",
               "{:.0f}", "", "b2_over_4"),
    Conclusion("w0", "Dark-energy w0", "cosmology.w0_derived", "{:.5f}", "",
               "one_minus_inv_b3"),
    Conclusion("wa", "Dark-energy wa", "cosmology.wa_thawing", "{:.5f}"),
    Conclusion("H0", "Local H0", "cosmology.H0_local", "{:.2f}",
               "km/s/Mpc"),
    Conclusion("m_kk", "KK graviton mass", "geometry.m_KK_central",
               "{:.3g}", "TeV"),
    Conclusion("alp", "ALP mass", "alp.mass_meV", "{:.3g}", "meV"),
    Conclusion("proton", "Proton lifetime", "proton_decay.tau_p_years",
               "{:.3e}", "yr"),
    Conclusion("m_gut", "GUT scale", "gauge.M_GUT", "{:.3e}", "GeV"),
    Conclusion("alpha", "Inverse fine-structure constant",
               "geometry.alpha_inverse", "{:.6f}"),
    Conclusion("re_t", "Re(T) modulus", "cosmology.racetrack_Re_T",
               "{:.4g}"),
    Conclusion("cabibbo", "Cabibbo racetrack derivation",
               "algebra.gaugino_cabibbo_derived", "{:.5f}"),
)


# --------------------------------------------------------------- fit quality

def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def load_fit_summary(artifact_dir: Optional[Path] = None) -> Dict[str, Any]:
    """chi^2 and scoreboard counts from the build artifacts, or why absent.

    ``available`` is False when either file or any needed key is missing; the
    caller must then print ``why`` and no numbers.
    """
    if artifact_dir is None:
        src = params_source()
        if not src["available"]:
            return {"available": False, "why": src["why"]}
        artifact_dir = Path(src["path"]).parent
    rigor = _read_json(artifact_dir / "statistical_rigor_report.json")
    report = _read_json(artifact_dir / "validation_report.json")
    try:
        chi = rigor["chi_squared_from_rows"]
        counts = {k: int(report["summary"][k])
                  for k in ("pass", "marginal", "tension", "fail")}
        return {
            "available": True, "dir": str(artifact_dir), "counts": counts,
            "chi2": float(chi["all_scoring_rows"]["chi_squared"]),
            "n": int(chi["all_scoring_rows"]["n"]),
            "reduced": float(chi["all_scoring_rows"]["reduced"]),
            "chi2_live": float(chi["excluding_falsified"]["chi_squared"]),
            "n_live": int(chi["excluding_falsified"]["n"]),
            "n_withdrawn": len(chi.get("withdrawn_rows", [])),
        }
    except (TypeError, KeyError, ValueError):
        return {"available": False, "why": (
            "statistical_rigor_report.json / validation_report.json not "
            "found next to parameters.json, or missing "
            "chi_squared_from_rows / summary keys (searched %s)" %
            artifact_dir)}


def fit_blocks(fit: Dict[str, Any]) -> List[ContentBlock]:
    """Paragraph stating the global fit, or a visible NOT AVAILABLE."""
    if not fit["available"]:
        return [ContentBlock(
            type="callout", callout_type="error", label="fit-unavailable",
            title="Fit quality: NOT AVAILABLE",
            content="NOT AVAILABLE. The global fit is not stated because its build "
                    "artifact is absent: " + fit["why"])]
    c = fit["counts"]
    return [ContentBlock(
        type="paragraph", label="fit-quality",
        content=(
            "<strong>Fit quality (computed from the validation artifacts, "
            "not asserted):</strong> chi&sup2; = {chi2:,.2f} over n = {n} "
            "scoring rows (reduced {red:,.4g}); excluding the {w} rows "
            "withdrawn as FALSIFIED, chi&sup2; = {cl:,.2f} over n = {nl}. A "
            "reduced chi&sup2; near 1 would indicate consistency with the "
            "stated uncertainties. Scoreboard: PASS {p}, MARGINAL {m}, "
            "TENSION {t}, FAIL {f}."
        ).format(chi2=fit["chi2"], n=fit["n"], red=fit["reduced"],
                 w=fit["n_withdrawn"], cl=fit["chi2_live"], nl=fit["n_live"],
                 p=c["pass"], m=c["marginal"], t=c["tension"], f=c["fail"]))]


# ------------------------------------------------------------------ geometry

def _certificate_by_label() -> Dict[str, Dict[str, Any]]:
    from metaphysica.simulations.PM.geometry.closed_geometry.certificate import (
        certificate,
    )
    return {t["label"]: t for t in certificate()}


def path_blocks() -> List[ContentBlock]:
    """The active path, stated; flags a run that is not on the adopted one."""
    from metaphysica.simulations.PM.geometry import b3_path

    path = b3_path.resolve_path()
    b3, b2 = b3_path.seed_values(path)
    nar = b3_path.narration(path)
    text = ("Active path: <code>%s</code>, (b<sub>2</sub>, b<sub>3</sub>) = "
            "(%d, %d). %s %s." % (path, b2, b3, nar["seed_sentence"],
                                  nar["n_gen_sentence"]))
    if path != ADOPTED_PATH:
        text += (" <strong>This run is not on the adopted path (%s, D-015); "
                 "every statement below is computed for the active path "
                 "and is not a statement about the adopted one.</strong>"
                 % ADOPTED_PATH)
    return [ContentBlock(type="paragraph", content=text, label="active-path")]


def artifact_seed_blocks() -> List[ContentBlock]:
    """A visible note when the registry artifact was built under another seed."""
    from metaphysica.simulations.PM.geometry import b3_path

    row = params_source()["params"].get("particle.b3")
    built = row.get("value") if isinstance(row, dict) else None
    live = b3_path.seed_values()[0]
    if built is None or built == live:
        return []
    return [ContentBlock(
        type="callout", callout_type="warning", label="artifact-seed-mismatch",
        content="The registry artifact was built with b3 = %s but the active "
                "path has b3 = %s: the physics values below are the "
                "artifact's, not the active path's. Rebuild to refresh them."
                % (built, live))]


def geometry_blocks(cert: Dict[str, Dict[str, Any]]) -> List[ContentBlock]:
    """Geometry statements, verbatim from the certificate, with CG labels."""
    items = []
    for label in GEOMETRY_LABELS:
        t = cert[label]
        verdict = "holds" if t["holds"] else "DOES NOT HOLD on the active path"
        items.append("<strong>%s</strong> %s: %s [%s]" %
                     (label, t["title"], t["statement"], verdict))
    return [ContentBlock(type="list", items=items, label="geometry-claims")]


# ------------------------------------------------------------------- physics

def _live_expectation(name: Optional[str]) -> Optional[Tuple[float, str]]:
    if name is None:
        return None
    from metaphysica.simulations.PM.geometry import b3_path
    b3, b2 = b3_path.seed_values()
    if name == "b2_over_4":
        return b2 / 4.0, "b2/4 = %d/4" % b2
    if name == "one_minus_inv_b3":
        return -1.0 + 1.0 / b3, "-1 + 1/b3 = -1 + 1/%d" % b3
    raise ValueError("unknown live-seed expectation %r" % name)


def _conclusion_row(spec: Conclusion, rows: Dict[str, Any]) -> Dict[str, Any]:
    row = rows.get(spec.path)
    if not isinstance(row, dict) or not isinstance(
            row.get("value"), (int, float)):
        return {"spec": spec, "tag": "open", "text": "no registry row",
                "source": "NOT AVAILABLE", "note": ""}
    value = float(row["value"])
    text = spec.fmt.format(value) + (" " + spec.units if spec.units else "")
    note = ""
    exp = _live_expectation(spec.expect)
    if exp is not None and abs(value - exp[0]) > 1e-9 * max(1.0, abs(exp[0])):
        note = (" Registry value differs from the live-seed %s = %.5g: the "
                "artifact was built under another seed, or the source is "
                "not yet corrected." % (exp[1], exp[0]))
    src = row.get("source_simulation") or row.get("source") or "unknown"
    return {"spec": spec, "tag": status_tag(row.get("status", "")),
            "text": text, "source": src, "note": note}


def physics_rows() -> List[Dict[str, Any]]:
    """Every conclusion with value, status tag and derivation source."""
    src = params_source()
    return [_conclusion_row(c, src["params"]) for c in CONCLUSIONS]


def physics_blocks(rows: List[Dict[str, Any]]) -> List[ContentBlock]:
    """One tagged paragraph per conclusion."""
    out = []
    for r in rows:
        s = r["spec"]
        out.append(ContentBlock(
            type="paragraph", label="conclusion-" + s.key,
            content="<strong>[%s]</strong> %s: %s. Derivation: %s "
                    "(registry row <code>%s</code>).%s" %
                    (r["tag"], s.title, r["text"], r["source"], s.path,
                     r["note"])))
    return out


# --------------------------------------------------------------- open items

def open_problem_items(rows: List[Dict[str, Any]],
                       cert: Dict[str, Dict[str, Any]]) -> List[str]:
    """What the engine marks open, calibrated or fitted, plus failed theorems."""
    items = []
    for r in rows:
        if r["tag"] in ("open", "calibrated", "fitted"):
            items.append("%s is %s (%s)." %
                         (r["spec"].title, r["tag"], r["source"]))
    for label, t in cert.items():
        if not t["holds"]:
            items.append("%s %s does not hold on the active path." %
                         (label, t["title"]))
    for label in OPEN_GEOMETRY_LABELS:
        items.append("%s %s: a stabilisation or construction result that "
                     "leaves a modulus unfixed." % (label, cert[label]["title"]))
    unclaimed = cert["(CG.13)"]["evidence"]["what_is_not_claimed"]
    items.append("Not claimed (CG.13): %s" % (
        unclaimed if isinstance(unclaimed, str) else "; ".join(unclaimed)))
    return items


def superseded_block() -> ContentBlock:
    """The one place the dead ends are named, as dead ends."""
    return ContentBlock(
        type="paragraph", label="superseded-paths",
        content=("<strong>Superseded paths.</strong> Twisted-connected-sum "
                 "(TCS) G<sub>2</sub> manifolds and the b<sub>3</sub> = 24 "
                 "seed are superseded. They stay runnable as labelled "
                 "off-path branches and are documented on the <a href=\"%s\">"
                 "paths page</a>; no conclusion above is stated on them."
                 % PATHS_LINK))


def section7_blocks() -> List[ContentBlock]:
    """All section-7 blocks, in order."""
    cert = _certificate_by_label()
    rows = physics_rows()
    blocks = [
        ContentBlock(type="heading", content="Conclusion", level=1),
        ContentBlock(type="paragraph", label="conclusion-scope", content=(
            "This section states only what the engine establishes on the "
            "active path. Every number below is computed when the paper is "
            "rendered, and every conclusion carries a status "
            "(derived, calibrated, fitted, open or predicted) taken from "
            "its registry row.")),
        ContentBlock(type="heading", content="7.1 Summary of Results",
                     level=2),
    ]
    blocks += path_blocks() + artifact_seed_blocks() + geometry_blocks(cert)
    blocks.append(ContentBlock(
        type="heading", content="Physics conclusions and their status",
        level=3))
    blocks += physics_blocks(rows)
    blocks.append(ContentBlock(type="heading", content="Fit quality",
                               level=3))
    blocks += fit_blocks(load_fit_summary())
    blocks.append(ContentBlock(type="formula",
                               formula_id="discussion-global-alignment"))
    blocks += [
        ContentBlock(type="heading", content="7.2 Open problems", level=2),
        ContentBlock(type="list", label="open-problems",
                     items=open_problem_items(rows, cert)),
        superseded_block(),
    ]
    return blocks


# ------------------------------------------------- sections 8 and 9 and TA

#: registry rows that each carry a Re(T) value; all are shown, none chosen
RE_T_PATHS = ("geometry.ReT", "cosmology.racetrack_Re_T",
              "moduli.re_t_attractor", "moduli.re_t_phenomenological")


def parameter_census() -> Dict[str, Any]:
    """Registry row counts by status tag; statuses with no tag are inputs."""
    src = params_source()
    if not src["available"]:
        return {"available": False, "why": src["why"]}
    counts = {t: 0 for t in STATUS_TAGS}
    other = 0
    for row in src["params"].values():
        st = str(row.get("status", "")).upper() if isinstance(row, dict) else ""
        if st in _STATUS_MAP:
            counts[_STATUS_MAP[st]] += 1
        else:
            other += 1
    return {"available": True, "total": len(src["params"]), "other": other,
            "counts": counts, "path": src["path"]}


def census_text() -> str:
    """One sentence replacing the hardcoded '58 parameters'."""
    c = parameter_census()
    if not c["available"]:
        return "Parameter census: NOT AVAILABLE (%s)." % c["why"]
    tags = ", ".join("%s %d" % (t, c["counts"][t]) for t in STATUS_TAGS)
    return ("Parameter census from the registry (%d rows): %s; %d further "
            "rows are experimental inputs, validation rows or system rows "
            "and are not conclusions." % (c["total"], tags, c["other"]))


def re_t_rows() -> List[List[str]]:
    """Table rows [value, registry row, classification, source] for Re(T)."""
    rows = params_source()["params"]
    out = []
    for path in RE_T_PATHS:
        r = rows.get(path)
        if isinstance(r, dict) and isinstance(r.get("value"), (int, float)):
            out.append(["%.4g" % r["value"], "<code>%s</code>" % path,
                        str(r.get("status")),
                        str(r.get("source_simulation") or r.get("source"))])
        else:
            out.append(["NOT AVAILABLE", "<code>%s</code>" % path, "OPEN",
                        "no registry row"])
    return out


def re_t_mismatch_text() -> str:
    """Flag, without choosing, when the Re(T) rows disagree."""
    vals = {r[0] for r in re_t_rows() if r[0] != "NOT AVAILABLE"}
    if len(vals) <= 1:
        return "The registry Re(T) rows agree."
    return ("MISMATCH: the registry carries %d different Re(T) values, "
            "with the classifications shown. They are not reconciled here; "
            "which one the paper adopts is an author ruling." % len(vals))


def edof_items() -> List[str]:
    """Input summary generated from the live seed and registry census."""
    from metaphysica.simulations.PM.geometry import b3_path

    path = b3_path.resolve_path()
    b3, b2 = b3_path.seed_values(path)
    c = parameter_census()
    items = ["<strong>Geometric seed:</strong> (b<sub>2</sub>, b<sub>3</sub>) "
             "= (%d, %d) on the active path <code>%s</code>." % (b2, b3, path)]
    if c["available"]:
        items.append("<strong>Calibrated rows:</strong> %d. <strong>Fitted "
                     "rows:</strong> %d (registry statuses)." %
                     (c["counts"]["calibrated"], c["counts"]["fitted"]))
    else:
        items.append("Calibrated and fitted counts: NOT AVAILABLE.")
    items.append("<strong>Re(T):</strong> OPEN. " + re_t_mismatch_text())
    items.append("<strong>Effective degrees of freedom and compression "
                 "ratio:</strong> OPEN, not recomputed by the engine for the "
                 "active path.")
    items.append("Superseded path: the earlier EDOF and compression-ratio "
                 "accounting was made at the b<sub>3</sub> = 24 seed; see "
                 "the <a href=\"%s\">paths page</a>." % PATHS_LINK)
    return items


def prediction_rows() -> List[List[str]]:
    """Rows of the 8.2 table that the registry can supply."""
    by = {r["spec"].key: r for r in physics_rows()}
    names = (("n_gen", "Generation Count"), ("m_gut", "GUT scale"),
             ("proton", "Proton lifetime"), ("m_kk", "KK graviton mass"),
             ("w0", "Dark Energy w0"))
    rows = [[n, by[k]["text"], "source: " + str(by[k]["source"]), "[%s]" % by[k]["tag"]]
            for k, n in names]
    rows.insert(3, ["Proton channel fractions / mass ordering",
                    "OPEN: no registry row", "NuFIT 6.0", "[open]"])
    return rows
