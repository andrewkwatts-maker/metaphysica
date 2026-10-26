"""C4b: the 8 containers still naming TCS unqualified on the site now qualify it in engine source."""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

# Copied from PrincipiaMetaphysica/docs/plan/geometry/tcs_scope.py
Q = re.compile(r"retired|refused|off-path|false|superseded|withdrawn|exclu|not a |cannot|"
               r"no published|formerly|used to|abandon|legacy|historical|seed_24|seed 24|"
               r"relocated|demoted|was described|earlier|parity|kovalev|chnp|range|"
               r"reading|belonged|not taken from|no longer", re.I)

SRC = Path(__file__).resolve().parents[1] / "src" / "metaphysica"
SIM = "simulations/PM/"
LAG = SIM + "derivations/lagrangian_master.py"
PD = SIM + "particle/proton_decay.py"
APP = SIM + "paper/appendices/"

#: (file, anchor text that identifies the source string)
CASES = [
    (LAG, "independent Kahler moduli T_1,...,T_4 (one per face"),
    (LAG, "4 independent Kahler moduli "),
    (LAG, "Kahler modulus for face i (i=1..4)"),
    (LAG, "instanton action for wrapping the i-th cycle"),
    (LAG, "TCS face i (i=1..4)"),
    (PD, "Geometric suppression factor from"),
    (PD, "glues two ACyl CY3 blocks"),
    (PD, "K3 fibre matching number (K=4 "),
    (APP + "appendix_r_vacuum_stability.py", "Third Betti number of the TCS G2 manifold"),
    ("simulations/base/established.py", "torsion class parameter T_"),
    (APP + "appendix_k_sterile_constants.py", "third Betti number of the off-path TCS #187"),
    (APP + "appendix_o_kk_reduction.py", "Per-shadow G2 holonomy compactification"),
]


def _strings(path: Path):
    for n in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            yield n.value


@pytest.mark.parametrize("rel,anchor", CASES)
def test_tcs_string_is_qualified(rel, anchor):
    # anchor may have been rewritten; match on the stable prefix only
    key = anchor.replace("the off-path TCS #187", "TCS #187")
    hits = [s for s in _strings(SRC / rel) if key in s and "TCS" in s]
    if rel.endswith("appendix_k_sterile_constants.py"):
        hits = [s for s in _strings(SRC / rel) if "third Betti number of" in s and "#187 " in s]
    assert hits, (rel, anchor)
    for s in hits:
        assert Q.search(s), s


def test_euler_characteristic_term_description_is_qualified():
    text = (SRC / "generators/generate_interactive_html.py").read_text(encoding="utf-8")
    i = text.index("Kahler moduli count = 4")
    seg = text[i:i + 120]
    assert "TCS" in seg and Q.search(seg), seg
