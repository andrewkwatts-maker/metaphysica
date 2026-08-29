"""Is an EML render actually showable?

WHY THIS EXISTS
---------------
generate_formula_renders.py guarded the wrong thing. It caught failures at
*parse* time (``parse_eml_tree`` raising) but then accepted whatever
``to_latex()`` / ``flow_html()`` returned, on the sole test ``r is not None``.
A string reading ``<parse error: invalid syntax (<unknown>, line 2)>`` is not
None, so twelve formulas -- including w0-derivation, alpha-t-derivation and
dark-matter-abundance -- shipped that error text to the website AS their EML
rendering, and the build reported them as successful renders.

Three further classes were passing the same way:

* bare leaves -- ``g2-holonomy`` rendering as the single glyph ``1``, and
  ``gut-scale`` as ``M_{GUT}``: a picture of one symbol, depicting no relation
* unresolved internals -- ``betti-numbers`` rendering as ``b3_leaf``, leaking
  a parser-internal name into published output
* empty output

This module is the single place that decides. It returns a reason, not just a
boolean, so the build can name what is wrong with each one rather than
silently dropping it.

NO INVENTED THRESHOLDS
----------------------
An earlier pass of this audit classified renders by counting ``<text``
elements in the SVG and calling anything under three "trivial". That number
was invented -- it was tuned to the observed data and would have quietly
reclassified formulas on any future renderer change. It is replaced by a
structural question with a real answer: does the tree contain an *operator*?
A diagram depicts a relation between things. A tree with no operator node has
no relation to depict, whatever its pixel count.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import re
from typing import Any, Optional, Sequence, Tuple

__all__ = [
    "OPERATOR_KINDS",
    "LEAF_KINDS",
    "REASON_OK",
    "tree_operator_count",
    "classify_render",
    "REQUIRE_OPERATOR",
]

#: Node kinds that denote an operation (see eml_trees.json ``_kind_map``).
#: 'c' compound, 's' structural, 'p' primitive -- all of these combine
#: operands. Leaves are scalars, vectors, constants, pi, bottom, unknown.
OPERATOR_KINDS = frozenset({"c", "s", "p"})
LEAF_KINDS = frozenset({"#", "v", "P", "C", "_", "?"})

REASON_OK = "ok"

#: When True a render must depict at least one operator to be offered.
#:
#: RESOLVED BY BRANCH COMPARISON, not by preference. Both policies were run
#: against the live formula set:
#:
#:   permissive (False) -> 395 offered, 15 withheld
#:   strict     (True)  -> 389 offered, 21 withheld
#:
#: The six formulas that differ are the whole argument. Under the permissive
#: policy the website offers, as the EML form of each statement:
#:
#:   g2-automorphism-relation   G_2 = Aut(O)              rendered as  "8"
#:   g2-holonomy                Hol(g) < G_2 <=> ...      rendered as  "1"
#:   hysteresis-lock            d(alpha)/dt = 0           rendered as  "0"
#:   gut-scale                  M_GUT : min_mu sigma[..]  rendered as  "M_{GUT}"
#:   gr-ricci-tensor-v19        full Ricci contraction    rendered as  one term
#:   g2-holonomy-foundations    Hol(g) < G_2 <=> ...      "G2_{holonomy}"
#:
#: These are not merely uninformative -- each is a truncation that
#: misrepresents its own formula. "8" for "G_2 = Aut(O)" is the case that
#: settles it: 8 is the dimension of the octonions, so the render is wrong in
#: a way that reads as content, and a reader toggling to EML would take it for
#: the framework's claim. Withholding beats publishing that.
REQUIRE_OPERATOR = True

#: Parser-internal leaf names that must never reach published output.
_INTERNAL_LEAF_RE = re.compile(r"^[A-Za-z0-9_\\{}^]+_leaf$")

#: Any rendered payload containing this is an error message, not content.
_ERROR_MARKERS = ("parse error", "traceback", "nameerror", "syntaxerror")


def _walk_kinds(node: Any, out: list) -> None:
    """Collect kind codes from a serialised tree ``[label, kind, *children]``."""
    if not isinstance(node, (list, tuple)) or len(node) < 2:
        return
    out.append(node[1])
    for child in node[2:]:
        _walk_kinds(child, out)


def tree_operator_count(tree: Any) -> int:
    """Number of operator nodes in a serialised EML tree."""
    kinds: list = []
    _walk_kinds(tree, kinds)
    return sum(1 for k in kinds if k in OPERATOR_KINDS)


def classify_render(
    renders: dict,
    tree: Optional[Any] = None,
    *,
    require_operator: Optional[bool] = None,
    formats: Sequence[str] = ("latex", "html"),
) -> Tuple[bool, str]:
    """Return ``(is_renderable, reason)`` for one formula's rendered output.

    *renders* maps format name -> rendered string. *tree* is the serialised
    EML tree, used only for the operator test. The checks run cheapest and
    most-certain first, so the reported reason names the worst defect rather
    than the first one noticed.
    """
    if require_operator is None:
        require_operator = REQUIRE_OPERATOR

    present = {f: renders.get(f) for f in formats}

    missing = [f for f, v in present.items() if v is None]
    if missing:
        return False, f"missing render format(s): {', '.join(missing)}"

    empty = [f for f, v in present.items() if not str(v).strip()]
    if empty:
        return False, f"empty render for format(s): {', '.join(empty)}"

    for fmt, value in present.items():
        low = str(value).lower()
        for marker in _ERROR_MARKERS:
            if marker in low:
                return False, (
                    f"{fmt} render contains an error message ({marker!r}) -- "
                    "the renderer failed and returned its failure as content"
                )

    latex = str(present.get("latex", "")).strip()
    if _INTERNAL_LEAF_RE.match(latex):
        return False, (
            f"latex is an unresolved parser-internal name ({latex!r}); "
            "publishing it would leak implementation detail"
        )

    if require_operator and tree is not None:
        if tree_operator_count(tree) == 0:
            return False, (
                "tree has no operator node -- a lone symbol depicts no "
                "relation, so there is no diagram to show"
            )

    return True, REASON_OK
