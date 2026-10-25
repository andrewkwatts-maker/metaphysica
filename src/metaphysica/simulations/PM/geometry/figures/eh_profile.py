"""Figure b: the Eguchi-Hanson neck profile f(r) = sqrt(1 - a^4/r^4), r >= a."""
import math

from .svgkit import line, svg_doc, text

TITLE = "Eguchi-Hanson neck profile f(r)"


def profile_points(samples: int = 60, r_max: float = 4.0):
    """(r/a, f) pairs sampled from the formula, a = 1."""
    if samples < 2 or r_max <= 1.0:
        raise ValueError("need samples >= 2 and r_max > a")
    out = []
    for i in range(samples):
        r = 1.0 + (r_max - 1.0) * i / (samples - 1)
        out.append((r, math.sqrt(max(0.0, 1.0 - 1.0 / r ** 4))))
    return out


def eh_profile_figure(samples: int = 60, r_max: float = 4.0) -> str:
    pts = profile_points(samples, r_max)
    x0, y0, w, h = 60, 20, 540, 200
    poly = " ".join("%.1f,%.1f" % (x0 + w * (r - 1.0) / (r_max - 1.0), y0 + h * (1 - f))
                    for r, f in pts)
    body = [
        line(x0, y0 + h, x0 + w, y0 + h), line(x0, y0, x0, y0 + h),
        '<polyline class="curve" points="%s"/>' % poly,
        text(x0 + w / 2, y0 + h + 38, "radius r / a  (r = a is the bolt, a 2-sphere)",
             "tx", "middle"),
        text(14, y0 + h / 2, "f(r)", "tx"),
        text(x0 - 6, y0 + 4, "1", "sm", "end"), text(x0 - 6, y0 + h + 4, "0", "sm", "end"),
        text(x0, y0 + h + 16, "1", "sm", "middle"),
        text(x0 + w, y0 + h + 16, "%g" % r_max, "sm", "end"),
        text(x0 + w / 2, y0 + 30, "f(r) = sqrt(1 - a^4 / r^4) tends to 1: flat far away",
             "sm", "middle"),
    ]
    desc = ("f(r)=sqrt(1-a^4/r^4) rises from 0 at the bolt r=a toward 1 as r grows, "
            "sampled at %d points up to r=%g a." % (samples, r_max))
    return svg_doc(640, 270, TITLE, desc, body)
