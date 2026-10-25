"""Figure a: the fold of T^7 under the three (Z/2) generators."""
from typing import Any, Dict

from .svgkit import refusal_figure, rect, svg_doc, text

TITLE = "T^7 folded by three Z/2 generators, creases resolved"


def fold_figure(data: Dict[str, Any]) -> str:
    if data.get("refusal"):
        return refusal_figure(TITLE, data["refusal"])
    res = data["resolution"]
    gens, comps = res["n_singular_involutions"], res["n_components"]
    orbit = ", ".join(map(str, res["orbit_sizes"]))
    body = [
        rect(10, 20, 150, 90, "fg"), text(85, 70, "flat T^7", "tx", "middle"),
        text(85, 130, "7-dim torus", "sm", "middle"),
        rect(215, 20, 190, 90, "ac"),
        text(310, 55, "%d folding generators" % gens, "tx", "middle"),
        text(310, 75, "(Z/2)^3 acts", "sm", "middle"),
        text(310, 130, "each fold pinches the torus", "sm", "middle"),
        rect(460, 20, 170, 90, "ok"),
        text(545, 55, "%d singular 3-tori" % comps, "tx", "middle"),
        text(545, 75, "each a crease T^3 x C^2/Z2", "sm", "middle"),
        text(545, 130, "orbit size(s): %s" % orbit, "sm", "middle"),
        text(185, 68, "→", "tx", "middle"), text(432, 68, "→", "tx", "middle"),
        rect(215, 160, 415, 50, "ac"),
        text(422, 182, "each crease replaced by an Eguchi-Hanson patch", "tx", "middle"),
        text(422, 200, "b2 = %d exceptional 2-classes (engine)" % res["b2"], "sm", "middle"),
    ]
    desc = ("Flat T^7 is folded by %d generators into %d singular 3-tori; each is "
            "resolved by an Eguchi-Hanson patch, giving b2 = %d."
            % (gens, comps, res["b2"]))
    return svg_doc(640, 225, TITLE, desc, body)
