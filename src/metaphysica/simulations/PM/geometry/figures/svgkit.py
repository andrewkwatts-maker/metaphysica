"""Tiny SVG helpers shared by the geometry figures (no external libraries).

Colour comes only from `currentColor` and CSS custom properties with
fallbacks (--pm-fig-ok / --pm-fig-bad / --pm-fig-off / --pm-fig-accent), so
the same markup reads in light and dark themes. Status is also carried by a
word, never by colour alone.
"""
from typing import List
from xml.sax.saxutils import escape

STYLE = (
    ".fg{fill:none;stroke:currentColor;stroke-width:1.5}"
    ".tx{fill:currentColor;font:13px sans-serif}"
    ".sm{fill:currentColor;font:11px sans-serif;opacity:.8}"
    ".ok{fill:var(--pm-fig-ok,#2e9e5b);fill-opacity:.25;stroke:var(--pm-fig-ok,#2e9e5b);stroke-width:1.5}"
    ".bad{fill:var(--pm-fig-bad,#d6453d);fill-opacity:.25;stroke:var(--pm-fig-bad,#d6453d);stroke-width:1.5}"
    ".off{fill:var(--pm-fig-off,#8a8a8a);fill-opacity:.2;stroke:var(--pm-fig-off,#8a8a8a);"
    "stroke-width:1.5;stroke-dasharray:4 3}"
    ".ac{fill:var(--pm-fig-accent,#4a7bd0);fill-opacity:.25;stroke:var(--pm-fig-accent,#4a7bd0);stroke-width:1.5}"
    ".curve{fill:none;stroke:var(--pm-fig-accent,#4a7bd0);stroke-width:2.5}"
)


def esc(value) -> str:
    return escape(str(value))


def svg_doc(width: int, height: int, title: str, desc: str, body: List[str]) -> str:
    """Wrap `body` in a responsive, accessible <svg>."""
    if width <= 0 or height <= 0:
        raise ValueError("figure size must be positive")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'role="img" class="pm-fig" style="max-width:100%%;height:auto;color:inherit">'
        '<title>%s</title><desc>%s</desc><style>%s</style>%s</svg>'
        % (width, height, esc(title), esc(desc), STYLE, "".join(body)))


def text(x, y, content, cls="tx", anchor="start") -> str:
    return '<text x="%s" y="%s" class="%s" text-anchor="%s">%s</text>' % (
        x, y, cls, anchor, esc(content))


def rect(x, y, w, h, cls="fg", rx=6) -> str:
    return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" class="%s"/>' % (
        x, y, w, h, rx, cls)


def line(x1, y1, x2, y2, cls="fg") -> str:
    return '<line x1="%s" y1="%s" x2="%s" y2="%s" class="%s"/>' % (x1, y1, x2, y2, cls)


def _wrap(reason: str, width: int = 62) -> List[str]:
    lines, cur = [], ""
    for word in str(reason).split():
        if cur and len(cur) + len(word) > width:
            lines.append(cur)
            cur = ""
        cur = (cur + " " + word).strip()
    lines.append(cur)
    return lines


def refusal_figure(title: str, reason: str) -> str:
    """The figure shown when the engine refuses: the reason, not numbers."""
    if not reason:
        raise ValueError("a refusal figure needs the engine's reason")
    lines = _wrap(reason)
    body = [rect(10, 10, 620, 50 + 18 * len(lines), "off"),
            text(24, 36, "Not available on this seed: the engine refuses.", "tx")]
    body += [text(24, 58 + 18 * i, ln, "sm") for i, ln in enumerate(lines)]
    return svg_doc(640, 70 + 18 * len(lines), title,
                   "The engine refused to produce this figure: " + str(reason), body)
