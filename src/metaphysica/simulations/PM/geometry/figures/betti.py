"""Figure c: Betti counting, 7 flat 3-forms + 3 x b2 = b3."""
from typing import Any, Dict

from .svgkit import refusal_figure, rect, svg_doc, text

TITLE = "Counting b3: flat hallways plus three per repair"


def betti_figure(data: Dict[str, Any]) -> str:
    if data.get("refusal"):
        return refusal_figure(TITLE, data["refusal"])
    res = data["resolution"]
    b2, b3 = res["b2"], res["b3"]
    flat = b3 - 3 * b2
    if flat != 7:
        raise ValueError("engine b3 - 3*b2 = %d, not the 7 flat 3-forms" % flat)
    body = [
        rect(10, 20, 130, 70, "fg"), text(75, 50, "%d" % flat, "tx", "middle"),
        text(75, 72, "flat 3-forms", "sm", "middle"),
        text(160, 60, "+", "tx", "middle"),
        rect(180, 20, 190, 70, "ac"),
        text(275, 50, "3 × %d = %d" % (b2, 3 * b2), "tx", "middle"),
        text(275, 72, "twisted 3-forms (3 per repair)", "sm", "middle"),
        text(390, 60, "=", "tx", "middle"),
        rect(410, 20, 220, 70, "ok"), text(520, 50, "b3 = %d" % b3, "tx", "middle"),
        text(520, 72, "b2 = %d repairs (engine)" % b2, "sm", "middle"),
    ]
    desc = "b3 = %d equals %d flat 3-forms plus 3 times b2 = %d, i.e. %d." % (
        b3, flat, b2, 3 * b2)
    return svg_doc(640, 110, TITLE, desc, body)
