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
    "classify_source",
    "classify_eml_description",
    "eml_operator_surface",
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


#: Recognises an EML operator call inside a line of prose or comment.
_OPS_CALL_RE = re.compile(r"ops\.[A-Za-z_]+\s*\(")


#: Internal leaf spellings -> the symbol a reader should see.
#: ``b3_leaf()`` is metaphysica's way of writing "the b3 leaf" in an EML
#: expression. It is not an eml-math builtin, so the parser labels the node
#: with the identifier verbatim and every renderer prints it -- ``b3_leaf``
#: was visible in 92 published formula renders. Stripping the marker and
#: subscripting the index turns it into ``b_3``, which MathJax draws as b₃.
_LEAF_SUFFIX_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9]*?)(\d*)_leaf\b")


def normalise_leaf_names(expr: str) -> str:
    """Rewrite internal ``*_leaf`` identifiers to display symbols.

    Applied to the expression BEFORE parsing, so the tree carries the
    display label and every output format (latex, flow SVG, MathML) picks
    it up without any of them post-processing strings.

    ``b3_leaf()`` -> ``b_3``; the trailing ``()`` is dropped because the
    result is a symbol, not a call.
    """
    def repl(match):
        stem, digits = match.group(1), match.group(2)
        return f"{stem}_{digits}" if digits else stem

    out = _LEAF_SUFFIX_RE.sub(repl, expr)
    # `b3_leaf()` becomes `b_3()`; strip the empty call parens.
    return re.sub(r"\b([A-Za-z][A-Za-z0-9_]*)\(\)", r"\1", out)


def classify_source(expr: str) -> Tuple[bool, str]:
    """Diagnose the SOURCE expression before it is handed to the parser.

    Worth doing separately because the parser's own message is useless to
    whoever has to fix it. All twelve formulas that shipped
    ``<parse error: invalid syntax (<unknown>, line 2)>`` have the same
    cause, and it is not a syntax error in any meaningful sense: their
    ``eml_tree_str`` is a **comment block**. The expression is right there,
    but every line begins with ``#``, so the parser sees no code::

        # w0 derivation in EML operator tree:
        # w0 = ops.add(ops.neg(eml_scalar(1.0)), ops.inv(b3_leaf()))
        #    = ops.div(ops.neg(eml_scalar(23.0)), b3_leaf())

    Reporting "invalid syntax on line 2" sends the reader hunting for a
    typo. Reporting "every line is commented out, 2 candidate expressions
    inside" names the fix.

    This deliberately does NOT uncomment anything. Only one of the twelve
    carries a single candidate; the rest hold two to six alternative or
    intermediate forms, and choosing among them is an authoring decision
    about which form is canonical -- not something a generator should make
    silently on the author's behalf.
    """
    if not expr or not expr.strip():
        return False, "no EML expression"

    body = expr.split("EML:", 1)[-1] if expr.startswith("EML:") else expr
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    if not lines:
        return False, "no EML expression"

    if all(ln.startswith("#") for ln in lines):
        n_candidates = sum(1 for ln in lines if _OPS_CALL_RE.search(ln))
        if n_candidates:
            return False, (
                f"eml_tree_str is entirely commented out -- the expression "
                f"exists but every line starts with '#', so the parser sees "
                f"no code ({n_candidates} candidate expression"
                f"{'s' if n_candidates != 1 else ''} inside). Uncomment the "
                f"canonical form; which one is canonical is an authoring "
                f"decision, so it is not chosen here"
            )
        return False, (
            "eml_tree_str is entirely commented out and contains no "
            "recognisable ops.* call"
        )

    return True, REASON_OK


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
        # REQUIRE_OPERATOR is the ADOPTED default and stays the declared
        # source of truth. The variant registry is consulted so the choice
        # can be exercised without editing this file -- which is how the
        # strict/permissive comparison had to be run the first time (two
        # branches, manually diffed). An unknown value raises rather than
        # silently falling back, so a typo cannot run one policy while the
        # report claims the other.
        try:
            from metaphysica.simulations.core.variants import resolve
            require_operator = resolve("render_policy") == "strict"
        except ImportError:
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


# ═══════════════════════════════════════════════════════════════════════════
# Is a PARAMETER's eml_description offerable as an EML option?
# ═══════════════════════════════════════════════════════════════════════════
#
# Pages/parameters.html attaches a "Normal | EML" pill to every parameter
# whose eml_description is non-empty, and shows the field's raw text under
# the EML tab. Non-empty was the only test, so the pill was offered for 36
# parameters that have no EML expression to show:
#
#   * 18 whose eml_description is English prose -- toggling to EML showed
#     the same sentence as Normal, relabelled as the framework's formal
#     notation. That is worse than no option: it presents prose AS EML.
#   * 10 that read eml_scalar(N_pass) and the like -- a bare tally with no
#     operator. Identical in kind to the lone-symbol renders the strict
#     render_policy already withholds (see REQUIRE_OPERATOR): a picture of
#     one symbol depicts no relation.
#   * 8 that call operators the installed eml-math does not define
#     (ops.quadratic over a metric signature, ops.corrcoef over two data
#     arrays, ops.integrate over a grid, ops.argmin_mu, plus a Python
#     comprehension summing an indexed family).
#
# The operator surface is READ FROM THE INSTALLED LIBRARY rather than
# listed here. A hardcoded list would keep suppressing an expression after
# eml-math grew the operator it needs, and would need editing in lockstep
# with a package this module does not own.

#: Names the evaluator binds itself (EMLEvaluator._namespace). Anything else
#: spelled ``eml_*`` is a constructor the DSL does not have.
_EML_CONSTRUCTORS = frozenset({"eml_scalar", "eml_pi", "eml_vec"})

_EML_PREFIX = "EML: "


def eml_operator_surface() -> frozenset:
    """Operator names the INSTALLED eml-math actually provides.

    Empty frozenset if eml-math cannot be imported, which makes the
    unknown-operator test skip rather than suppress everything -- the same
    fail-open choice ``_serialise_tree`` makes for the operator count. A
    missing dependency must not silently withhold every EML option.
    """
    try:
        import eml_math.operators as _ops
    except Exception:
        return frozenset()
    return frozenset(n for n in dir(_ops) if not n.startswith("_"))


def classify_eml_description(desc: str, *, operators=None) -> Tuple[bool, str, str]:
    """Return ``(offerable, reason, category)`` for one eml_description.

    Deliberately a STATIC check on the source text. Whether the expression
    also *agrees* with the registered value is a different question, and it
    is the cross-check's to answer -- an expression that depicts a real
    relation is worth showing even when one of its operands is missing from
    the registry, and suppressing on disagreement would hide the very
    discrepancies the cross-check exists to surface.

    Categories: ``ok``, ``prose``, ``malformed``, ``no_relation``,
    ``not_expressible``.
    """
    import ast

    if operators is None:
        operators = eml_operator_surface()

    text = (desc or "").strip()
    if not text:
        return False, "no eml_description", "prose"

    if not text.startswith(_EML_PREFIX):
        return False, (
            "eml_description holds prose, not an EML expression -- there is "
            "nothing to show under an EML tab that is not already shown "
            "under Normal"
        ), "prose"

    try:
        from eml_math.evaluator import EMLEvaluator
        body = EMLEvaluator._parse(text)
    except Exception as exc:
        return False, f"eml_description is not a parseable expression: {exc}", "malformed"

    try:
        parsed = ast.parse(body, mode="eval")
    except SyntaxError as exc:
        return False, (
            f"declared 'EML:' but the body is not a valid expression: {exc}"
        ), "malformed"

    unknown: set = set()
    comprehension = False
    n_ops = 0
    for node in ast.walk(parsed):
        if isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.SetComp,
                             ast.DictComp)):
            comprehension = True
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id == "ops"):
            n_ops += 1
            if operators and func.attr not in operators:
                unknown.add(f"ops.{func.attr}")
        elif isinstance(func, ast.Name) and func.id.startswith("eml_"):
            if func.id not in _EML_CONSTRUCTORS:
                unknown.add(func.id)

    if unknown:
        return False, (
            f"requires {', '.join(sorted(unknown))}, which eml-math does not "
            f"provide -- the quantity lives in a domain the scalar tension "
            f"algebra has no type for"
        ), "not_expressible"

    if comprehension:
        return False, (
            "expression sums over an indexed family (Python comprehension); "
            "the scalar algebra has no indexed-family or reduction type"
        ), "not_expressible"

    if n_ops == 0:
        return False, (
            "expression contains no operator -- a bare symbol or tally "
            "depicts no relation, the same defect the strict render_policy "
            "withholds for lone-symbol diagrams"
        ), "no_relation"

    return True, REASON_OK, "ok"
