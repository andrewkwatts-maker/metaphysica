"""Shared "superseded path" callout for prose that describes the retired geometry.

D-025 ruling 3: every citation of the retired b3 = 24 / TCS path is either the
active value or a callout. The callout says what is retired, what is active,
and the awkward fact that the retired seed scores better on the sweep. The
old text is kept inside the callout, never deleted. All figures are read live
from the two path summary.json files, or print OPEN.
"""
from __future__ import annotations

from typing import Any

from metaphysica.simulations.PM.paper.core_text import (
    _MAIN_PATH,
    _OPEN,
    _SEED_24_PATH,
    _compare,
    _path_phrase,
    _path_summary,
)

#: Leads every callout; the scanner treats a string containing it as covered.
MARK = "Superseded path"
LINK = "paths.html#%s" % _SEED_24_PATH


def _comparison() -> str:
    """Sentence on how seed_24 scores against main, live or OPEN."""
    if _path_summary(_MAIN_PATH) is None or _path_summary(_SEED_24_PATH) is None:
        return "sweep comparison: %s" % _OPEN
    return ("on the sweep %s (seed_24: %s; main: %s)"
            % (_compare(), _path_phrase(_SEED_24_PATH),
               _path_phrase(_MAIN_PATH)))


def _sentence(text: str) -> str:
    """text with its first letter capitalised, so it can open a sentence."""
    return text[:1].upper() + text[1:]


def superseded_text() -> str:
    """The shared callout statement (HTML), identical wherever it appears."""
    return (
        "<strong>%s.</strong> The text below describes the retired "
        "seed_24/TCS path (b<sub>3</sub> = 24). The active path is "
        "seed_43_joyce, closed by Joyce 11.6.1. seed_24 has no closure "
        "theorem. %s (<a href=\"%s\">path comparison</a>)."
        % (MARK, _sentence(_comparison()), LINK))


def superseded(old_text: str) -> str:
    """Wrap retired prose: the callout statement, then the old text intact."""
    if not old_text:
        raise ValueError("superseded: empty text; nothing to preserve")
    return "%s <em>Retired text:</em> %s" % (superseded_text(), old_text)


def superseded_block(old_text: str, **kw: Any):
    """A ContentBlock callout holding the wrapped retired text."""
    from metaphysica.simulations.base import ContentBlock
    return ContentBlock(type="callout", callout_type="warning",
                        title=MARK, content=superseded(old_text), **kw)


def active_b3() -> int:
    """Third Betti number in force, read from the b3_seed fork."""
    from metaphysica.simulations.PM.geometry.geometric_anchors import live_b3
    return live_b3()
