"""Abstract and introduction text for the core paper (D-025), from live state.

Every number is a placeholder filled from the engine: the geometry fragments
(``geometry_narration.fragments``), the closed-geometry certificate, the
scoreboard and chi-squared (``conclusions.load_fit_summary``) and the path
summaries. A source that is missing prints OPEN, never a number. The
templates contain no digits except inside placeholders; a test enforces it.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from metaphysica.simulations.PM.paper.core_manifest import CORE_MANIFEST

_OPEN = "OPEN"
_SEED_24_PATH = "b3_seed--seed_24"
_MAIN_PATH = "main"


def _cert() -> Dict[str, Dict[str, Any]]:
    from metaphysica.simulations.PM.geometry.closed_geometry.certificate import (
        certificate,
    )
    return {t["label"]: t for t in certificate()}


def _fit_text() -> str:
    """Scoreboard and chi-squared, or OPEN with the reason."""
    from metaphysica.simulations.PM.paper.conclusions import load_fit_summary

    fit = load_fit_summary()
    if not fit["available"]:
        return "%s (%s)" % (_OPEN, fit["why"])
    c = fit["counts"]
    return ("%d pass, %d marginal, %d tension and %d fail, with chi-squared "
            "%.3g over %d scored rows" % (c["pass"], c["marginal"],
                                         c["tension"], c["fail"],
                                         fit["chi2"], fit["n"]))


def _path_summary(name: str) -> Optional[Dict[str, Any]]:
    """Scoreboard and chi2 for ``name`` from the committed path snapshot.

    Not ``autogen_dir()/paths``: a path run has none, so the prose would
    differ from main in every run (see ``path_snapshot``).
    """
    from metaphysica.simulations.PM.paper.path_snapshot import load

    return load(name)


def _path_phrase(name: str) -> str:
    s = _path_summary(name)
    if s is None:
        return _OPEN
    return "%d pass and %d fail, chi-squared %.5g over %d dof" % (
        s["scoreboard"]["PASS"], s["scoreboard"]["FAIL"],
        s["chi2"]["value"], s["chi2"]["dof"])


def _compare() -> str:
    """Whether the retired seed scores better, from the two summaries."""
    main, old = _path_summary(_MAIN_PATH), _path_summary(_SEED_24_PATH)
    if main is None or old is None:
        return _OPEN
    better = (old["scoreboard"]["PASS"] > main["scoreboard"]["PASS"]
              and old["chi2"]["value"] < main["chi2"]["value"])
    return ("it fits the data better" if better
            else "it does not fit the data better")


def _values() -> Dict[str, str]:
    """Placeholder values shared by the abstract and the introduction."""
    from metaphysica.simulations.PM.geometry.geometry_narration import (
        fragments,
    )

    cert = _cert()
    t13, t10, t11 = cert["(CG.13)"], cert["(CG.10)"], cert["(CG.11)"]
    ev = t13["evidence"]
    vals = dict(fragments("html"))
    vals.update(
        joyce=ev["conclusions"][0]["by"].split(";")[0],
        n_held=str(ev["n_held"]), n_hyp=str(ev["n_hypotheses"]),
        verdict=ev["verdict"].replace("_", " ").lower(),
        cg5=cert["(CG.5)"]["label"], cg9=cert["(CG.9)"]["label"],
        cg10=t10["label"], cg11=t11["label"],
        cg_held=str(sum(1 for t in cert.values() if t["holds"])),
        cg_total=str(len(cert)), fit=_fit_text(),
        main_path=_path_phrase(_MAIN_PATH),
        seed24_path=_path_phrase(_SEED_24_PATH), compare=_compare(),
    )
    return vals


_ABSTRACT = (
    "<p>Principia Metaphysica is a speculative geometric model and has not "
    "been peer reviewed.</p>"
    "<p><strong>Assumed.</strong> {bulk}, split into two shadows. This is a "
    "postulate; nothing below derives it.</p>"
    "<p><strong>Geometry.</strong> The internal space of each shadow is "
    "{manifold}, {construction}: a closed manifold with {betti_pair} and "
    "{n_gen_route}. A metric of holonomy exactly G<sub>2</sub> exists by "
    "{joyce}: {n_held} of {n_hyp} hypotheses are measured on the active seed "
    "and hold ({verdict}). No explicit metric is claimed; none is known for "
    "any compact G<sub>2</sub> manifold.</p>"
    "<p><strong>What follows.</strong> Read from the topology: the gauge content {cg5}, one K3 "
    "surface per singular involution {cg9} and {chi_eff}. Two results are "
    "negative: holonomy exactly G<sub>2</sub> excludes the confining sector "
    "that racetrack stabilisation needs {cg10}, and the leading flux "
    "potential cannot accelerate the universe {cg11}.</p>"
    "<p><strong>Against data.</strong> Scoreboard: {fit}. The model does not "
    "fit the data globally. Chirality, moduli stabilisation, dark energy and "
    "flavour are open.</p>"
)

_INTRO_PARAS = {
    "problem": (
        "<h3>The problem</h3><p>The Standard Model leaves its own parameters "
        "free: gauge couplings, the number of generations, fermion masses "
        "and mixing, the Higgs scale and the dark-energy equation of state "
        "are inputs. Kaluza-Klein and M-theory programmes ask whether they "
        "can instead be read from the geometry of extra dimensions. This "
        "paper tests that question on one concrete geometry and reports "
        "where it succeeds and where it does not.</p>"),
    "idea": (
        "<h3>The one idea</h3><p>Physics is read from the topology of one "
        "compact G<sub>2</sub> manifold, {manifold}, {construction}, with "
        "{betti_pair}. The integers counted on it are the inputs to the "
        "chain below. The only postulate is the bulk: {bulk}, split into two "
        "shadows. The manifold is {structure}; its existence is a theorem "
        "(Section 2.4), not an assumption, and no explicit metric is "
        "claimed.</p>"),
    "chain_head": "<h3>The chain of the argument</h3>",
    "status": (
        "<h3>What is proved, calibrated and failing</h3>"
        "<p><strong>Proved.</strong> {cg_held} of {cg_total} statements of "
        "the closed-geometry certificate hold on the active seed. Existence "
        "of the holonomy-G<sub>2</sub> metric rests on {joyce}, with "
        "{n_held} of {n_hyp} hypotheses measured.</p>"
        "<p><strong>Calibrated.</strong> A quantity that needs a number the "
        "topology does not fix, such as the K&auml;hler modulus Re(T), is a "
        "calibration. It is labelled CALIBRATED wherever it appears, and a "
        "result computed with it is not a prediction.</p>"
        "<p><strong>Failing.</strong> Scoreboard: {fit}. Chirality, moduli "
        "stabilisation, dark energy and flavour are open. On the active "
        "path scores {main_path}; the retired seed scores {seed24_path} "
        "({compare}). The active path is kept because only it has a closure "
        "theorem ({joyce}), which the retired seed lacks "
        "(<a href=\"paths.html#b3_seed--seed_24\">path comparison</a>).</p>"),
    "reading": (
        "<h3>How to read this paper</h3><p>The core argument is the "
        "sections listed above, in that order; the paper page opens on it. "
        "Choose &ldquo;Full paper&rdquo; to see every section, where the "
        "rest are marked supplementary. The previous introduction is kept "
        "unchanged as the extended introduction (supplementary). Section 7 "
        "reports the conclusions, including every failure.</p>"),
}


def _fill(template: str, vals: Dict[str, str]) -> str:
    return template.format(**vals)


def abstract_parts() -> Tuple[str, Dict[str, str]]:
    """The abstract template and its live placeholder values."""
    return _ABSTRACT, _values()


def abstract_html() -> str:
    """The abstract, rendered from live state."""
    template, vals = abstract_parts()
    return _fill(template, vals)


def abstract_summary() -> str:
    """One-sentence abstract for the section header."""
    vals = _values()
    return _fill(
        "A speculative geometric model: {bulk}, split into two shadows, each "
        "with internal space {manifold}, {betti_pair}, existing by {joyce}. "
        "The model does not fit the data globally.", vals)


def chain_items() -> List[str]:
    """One sentence per core step, from the manifest."""
    return ["<strong>Section %s.</strong> %s" % (sid, role)
            for sid, role in CORE_MANIFEST if sid not in ("0", "1")]


def intro_parts() -> Tuple[Dict[str, str], Dict[str, str]]:
    """Introduction paragraph templates and their live values."""
    return _INTRO_PARAS, _values()


def intro_blocks_html() -> List[Tuple[str, Any]]:
    """Ordered ('html', text) or ('list', items) pairs for the introduction."""
    paras, vals = intro_parts()
    out: List[Tuple[str, Any]] = [
        ("html", _fill(paras["problem"], vals)),
        ("html", _fill(paras["idea"], vals)),
        ("html", paras["chain_head"]),
        ("list", chain_items()),
        ("html", _fill(paras["status"], vals)),
        ("html", _fill(paras["reading"], vals)),
    ]
    return out
