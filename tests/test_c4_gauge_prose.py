"""Ratchet (C4 audit): gauge prose states what the active geometry gives.

The active manifold is the smooth Joyce resolution Y7 with (b2, b3) = (12, 43).
It gives U(1)^12, and SU(2)^12 only at the unresolved orbifold point (A1 loci).
SU(3)xSU(2)xU(1) and chirality are OPEN (D-011). So the gauge and paper sources
may not (1) name TCS as the active manifold, (2) put A2 loci on Y7, or (3) take
SU(2) from co-associative cycles, unless the same passage marks the claim as
retired, generic, a lead or OPEN. Prose only; no numeric checks here.
"""
from __future__ import annotations

import re
from pathlib import Path

PM = Path(__file__).resolve().parents[1] / "src" / "metaphysica" / "simulations" / "PM"
SOURCES = (
    sorted((PM / "gauge").glob("*.py"))
    + sorted((PM / "paper").rglob("*.py"))
    + [PM / "derivations" / "gauge_sector_complete.py"]
)
JOIN = re.compile(r'"\s*\n\s*(?:f|r)?"')
QUALIFIER = re.compile(
    r"retired|REFUSED|refused|RETIRED|OFF-PATH|off-path|false|superseded|Superseded"
    r"|legacy|generic|OPEN|NOT the TCS|lead|no A2|absent|not a TCS|abandoned|ABANDONED|toy",
)
WINDOW = 220


def _text(path: Path) -> str:
    return JOIN.sub("", path.read_text(encoding="utf-8"))


def _unqualified(pattern: str) -> list[str]:
    rx = re.compile(pattern)
    bad = []
    for path in SOURCES:
        text = _text(path)
        for m in rx.finditer(text):
            lo, hi = max(0, m.start() - WINDOW), m.end() + WINDOW
            if not QUALIFIER.search(text[lo:hi]):
                bad.append("%s: %s" % (path.name, text[m.start():m.end()][:60]))
    return bad


def test_no_tcs_as_active_manifold_in_gauge_sources():
    gauge_files = {p.name for p in SOURCES if p.parent.name in ("gauge", "derivations")}
    bad = [b for b in _unqualified(r"TCS") if b.split(":")[0] in gauge_files]
    assert not bad, bad


def test_no_a2_loci_on_y7():
    bad = _unqualified(r"A2[- ](?:type |\(SU\(3\)\) |ADE )?(?:singularit|loci|locus)")
    assert not bad, bad


def test_no_su2_from_coassociative_cycles():
    bad = _unqualified(r"SU\(2\)[^.\n]{0,100}co-?associative|co-?associative[^.\n]{0,100}SU\(2\)")
    assert not bad, bad


def test_engine_states_the_open_status():
    text = _text(PM / "gauge" / "non_abelian_kk_gauge.py")
    assert "OPEN (D-011)" in text and "U(1)^12" in text


def test_cycle_type_labels_say_open():
    """gauge.qcd/weak_cycle_type published the retired mechanisms as GEOMETRIC."""
    from metaphysica.simulations.PM.derivations.gauge_sector_complete import (
        GaugeSectorCompleteDerivations as G,
    )
    defs = {p.path: p for p in G().get_output_param_definitions()}
    for path in ("gauge.qcd_cycle_type", "gauge.weak_cycle_type"):
        assert defs[path].status == "ANSATZ", path
        assert "OPEN" in defs[path].description, path
