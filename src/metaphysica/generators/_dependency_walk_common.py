"""Shared scaffolding for the Arithma (S3.4) and EML (S3.5) dependency walkers.

Both walkers traverse a per-formula symbolic representation, identify the
leaves that derive from b₃ = 24, and emit a JSON file with the same
top-level shape so the website's b₃-tracer widget and the audit script
can consume them interchangeably::

    {
      "version":             "1.0",
      "kind":                "arithma" | "eml",
      "root_seed":           "b3=24",
      "total_formulas":      <int>,
      "b3_rooted_count":     <int>,
      "ambiguous_count":     <int>,
      "non_b3_rooted_count": <int>,
      "chains": {
        "<formula-id>": {
          "depth":               <int>,
          "leaves":              <int>,   # EML walker only
          "b3_leaf_count":       <int>,
          "raw_24_leaves_count": <int>,
          "b3_rooted":           <bool>,
          "path":                [...],   # token path or formula-id chain
          "via":                 [...],   # intermediate param names (Arithma)
          "paths":               [...],   # all b₃ leaf paths (EML)
          "degraded_walk":       <bool>,
        }, ...
      }
    }

The EML walker fills ``paths`` and ``leaves``; the Arithma walker fills
``path`` and ``via``. The shared fields (``depth``, ``b3_rooted``,
``b3_leaf_count``, ``raw_24_leaves_count``) are populated by both.
"""
from __future__ import annotations

from typing import Iterable

B3_VALUE: float = 24.0
B3_TOLERANCE: float = 1e-6

# Token markers recognised as direct b₃ references in either tree
# (label nodes that are *not* raw scalars). ``b3_leaf()`` itself emits
# only an ``eml_scalar(24.0)`` shape, but any future labelled-leaf
# convention should land in this set so both walkers stay in sync.
B3_LABEL_TOKENS: frozenset[str] = frozenset({
    "b3", "b_3", "B3", "\\beta_3",
    "topology.elder_kads", "elder_kads",
})


def is_b3_scalar(text: str) -> bool:
    """True if *text* parses to a float ≈ 24.0 within tolerance.

    This is the marker for the literal ``eml_scalar(24.0)`` that
    ``b3_leaf()`` returns and that ``parse_eml_tree`` serialises as a
    ``"#"``-kind leaf with label ``"24"`` in the compact form.
    """
    if text is None:
        return False
    s = str(text).strip()
    try:
        return abs(float(s) - B3_VALUE) < B3_TOLERANCE
    except (TypeError, ValueError):
        return False


def is_b3_label(text: str) -> bool:
    """True if *text* matches a known b₃ label token (case-sensitive)."""
    if not text:
        return False
    return str(text) in B3_LABEL_TOKENS


def truncate_paths(paths: Iterable[list[str]], max_paths: int = 8,
                   max_path_len: int = 16) -> list[list[str]]:
    """Keep at most *max_paths* paths; clip each to *max_path_len* tokens.

    Keeps the JSON small without losing the headline trace. Truncated
    paths get a trailing ``"…"`` marker so the website widget can
    surface "trace continues" hints.
    """
    out: list[list[str]] = []
    for p in paths:
        if len(out) >= max_paths:
            break
        if len(p) <= max_path_len:
            out.append(list(p))
        else:
            out.append(list(p[:max_path_len - 1]) + ["…"])
    return out


__all__ = [
    "B3_VALUE",
    "B3_TOLERANCE",
    "B3_LABEL_TOKENS",
    "is_b3_scalar",
    "is_b3_label",
    "truncate_paths",
]
