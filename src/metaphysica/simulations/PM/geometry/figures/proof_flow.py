"""Figure d: hypotheses -> Joyce Thm 11.6.1 -> torsion-free -> Ric = 0 -> Hol = G2."""
from typing import Any, Dict

from .svgkit import rect, svg_doc, text

TITLE = "From the hypotheses to holonomy exactly G2"
_CLS = {"holds": "ok", "fails": "bad", "not measured": "off"}


def status(row: Dict[str, Any]) -> str:
    """'holds', 'fails' or 'not measured' for one hypothesis row."""
    if not row.get("measured", True):
        return "not measured"
    return "holds" if row.get("holds") else "fails"


def _chain(conclusions, top: float, height: float):
    """One box per conclusion, labelled with the engine's claim and `by` source."""
    step = height / len(conclusions)
    out = []
    for i, c in enumerate(conclusions):
        cy, ok = top + i * step, c["established"]
        src = c["by"].split(":")[0]
        out += [rect(380, cy + 4, 250, step - 12, "ok" if ok else "off", 6),
                text(505, cy + step / 2 - 4, str(c["claim"])[:40], "tx", "middle"),
                text(505, cy + step / 2 + 14, src + ("" if ok else " (not reached)"),
                     "sm", "middle")]
    return out


def proof_flow_figure(data: Dict[str, Any]) -> str:
    report = data["closure"]
    rows = report["hypotheses"]
    if not rows or not report["conclusions"]:
        raise ValueError("closure report lacks hypotheses or conclusions")
    body, y = [], 10
    for row in rows:
        st = status(row)
        body += [rect(10, y, 330, 26, _CLS[st], 4),
                 text(18, y + 17, "%s  %s" % (row["id"], st), "tx"),
                 text(130, y + 17, str(row["hypothesis"])[:38], "sm")]
        y += 32
    body += _chain(report["conclusions"], 10, y - 10)
    body.append(text(360, 10 + (y - 10) / 2 + 5, "→", "tx", "middle"))
    desc = "Hypotheses %s feed three conclusions; verdict %s." % (
        ", ".join("%s %s" % (r["id"], status(r)) for r in rows), report["verdict"])
    return svg_doc(640, y + 5, TITLE, desc, body)
