"""Shared scaffolding for the Arithma (S3.4) and EML (S3.5) dependency walkers.

Both walkers traverse a per-formula symbolic representation, identify the
leaves that carry the third Betti number b₃ of the seed path IN FORCE, and
emit a JSON file with the same top-level shape so the website's b₃-tracer
widget and the audit script can consume them interchangeably::

    {
      "version":             "1.1",
      "kind":                "arithma" | "eml",
      "root_seed":           "b3=43",          # the LIVE seed, read per walk
      "seed":                {"path": "seed_43_joyce", "b3": 43, "b2": 12},
      "total_formulas":      <int>,
      "b3_rooted_count":     <int>,
      "ambiguous_count":     <int>,
      "non_b3_rooted_count": <int>,            # the three PARTITION the total
      "chains": {
        "<formula-id>": {
          "depth":                 <int>,
          "leaves":                <int>,   # EML walker only
          "b3_leaf_count":         <int>,   # LABELLED b3 leaves
          "raw_seed_leaves_count": <int>,   # bare scalars equal to the live b3
          "b3_rooted":             <bool>,
          "ambiguous":             <bool>,  # EML walker only
          "path":                  [...],   # formula-id chain (Arithma)
          "via":                   [...],   # intermediate param names (Arithma)
          "paths":                 [...],   # all b₃ leaf paths (EML)
          "degraded_walk":         <bool>,
        }, ...
      }
    }

WHY THE SEED IS READ, NEVER WRITTEN
===================================
This module used to carry ``B3_VALUE = 24.0`` and both walkers stamped
``root_seed: "b3=24"`` on their output. The b3_seed fork was ADOPTED at
``seed_43_joyce`` on 2026-09-22, so from that day the walkers were measuring
provenance against the off-path seed: a bare ``eml_scalar(24.0)`` -- the
Leech dimension, D_space_24, a frozen seed_24 literal -- was counted as the
seed, and the header said so. The value is now resolved per walk from
:func:`metaphysica.simulations.PM.geometry.b3_path.seed_values`, the single
source of truth for the active path, and the walk records which path it
measured against. ``B3_VALUE`` survives as a LIVE module attribute for
callers that imported it.

WHY LABELS DECIDE AND VALUES ONLY FLAG
======================================
A leaf is b3-rooted when it NAMES b3: ``b3_leaf()`` (eml_integration's
canonical leaf, which wraps the live seed), ``flavour_b3_leaf()`` (the flavour
sector's fork-aware leaf), ``b3`` / ``b_3`` / ``elder_kads`` /
``topology.elder_kads``. A name does not change when the seed does.

A bare scalar equal to the live b3 is only AMBIGUOUS: the number cannot say
whether it was read from the seed or merely coincides with it (43 is also
7 + 3 x 12, computed UPSTREAM of the seed by the closed-geometry certificate).
Ambiguous leaves are counted and kept apart; they never make a chain rooted.

``b3_leaf()`` used to be invisible: the tree parser emits it as a childless
compound node labelled ``b3_leaf``, which matched neither the scalar rule nor
the label set, so of the 89 formulas whose parsed tree calls ``b3_leaf()``, 88
were reported NOT rooted in b3 (the 89th only through a raw 24) -- while the
string-scan fallback, which tested the substring ``"b3"``, did see them. The
same formula therefore flipped verdict depending on which representation
happened to be on disk. Every representation now goes through the one rule
set below.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

B3_TOLERANCE: float = 1e-6

#: Calls that ARE a b₃ leaf in a formula tree. ``b3_leaf()`` wraps the live
#: seed (FormulasRegistry.elder_kads); ``flavour_b3_leaf()`` is the flavour
#: sector's leaf, resolved through the flavour_seed_coupling fork. The parser
#: emits either as a childless node labelled with the function name.
B3_LEAF_FUNCTIONS: frozenset[str] = frozenset({"b3_leaf", "flavour_b3_leaf"})

#: Labels recognised as direct b₃ references in any tree or tree string.
B3_LABEL_TOKENS: frozenset[str] = frozenset({
    "b3", "b_3", "B3", "\\beta_3",
    "topology.elder_kads", "elder_kads",
}) | B3_LEAF_FUNCTIONS

#: Compact-tree kinds that hold a bare number: EML ``#`` (eml_scalar) and
#: ``C`` (a literal constant such as the 24 in ``ops.div(b3, 24)``); arithma
#: ``num``.
NUMERIC_KINDS: frozenset[str] = frozenset({"#", "C", "num"})


# ── The live seed ────────────────────────────────────────────────────────────

def live_seed() -> Tuple[int, int, str]:
    """``(b3, b2, path)`` of the seed path in force for this process.

    Resolved on every call (the b3_seed fork honours
    ``METAPHYSICA_VARIANT_B3_SEED``), so a walk run under the seed_24 override
    measures against 24 and says so, and the adopted walk measures against 43.
    """
    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path,
        seed_values,
    )

    path = resolve_path()
    b3, b2 = seed_values(path)
    return int(b3), int(b2), str(path)


def live_b3() -> int:
    """The live b₃ (43 on the adopted ``seed_43_joyce`` path)."""
    return live_seed()[0]


def seed_header(seed: Optional[Tuple[int, int, str]] = None) -> Dict[str, Any]:
    """The ``root_seed`` / ``seed`` envelope fields for one walk."""
    b3, b2, path = seed if seed is not None else live_seed()
    return {
        "root_seed": f"b3={b3}",
        "seed": {"path": path, "b3": b3, "b2": b2},
    }


def __getattr__(name: str):
    # B3_VALUE was a frozen 24.0. It stays importable, but is now LIVE.
    if name == "B3_VALUE":
        return float(live_b3())
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ── Leaf rules (one set, every representation) ──────────────────────────────

def is_b3_scalar(text: Any, b3: Optional[float] = None) -> bool:
    """True if *text* parses to ±*b3* (default: the live b₃).

    The sign is ignored because a string scan cannot tell ``-43`` from
    ``x - 43`` while the parser folds the former into one leaf; both readings
    must agree. A match is AMBIGUOUS evidence only -- see the module docstring.
    """
    if text is None:
        return False
    try:
        value = float(str(text).strip())
    except (TypeError, ValueError):
        return False
    target = float(live_b3() if b3 is None else b3)
    return abs(abs(value) - abs(target)) < B3_TOLERANCE


def is_b3_label(text: Any) -> bool:
    """True if *text* names b₃ (case-sensitive).

    A trailing ``()`` and a leading ``-`` are ignored: the parser labels
    ``-b3`` as one leaf ``"-b3"``, and it still names b₃.
    """
    if not text:
        return False
    s = str(text).strip().lstrip("-").strip()
    if s.endswith("()"):
        s = s[:-2]
    return s in B3_LABEL_TOKENS


# ── String fallback: the same rules over the text the parser would read ─────

#: Separators after which an EML string carries prose, not expression. Same
#: list as eml_math's ``EMLEvaluator._parse``.
_PROSE_TAILS = (" — ", " – ", " -- ")
_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*")
_NUMBER_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)(?![\w.])")
_QUOTED_RE = re.compile(r"'[^'\n]*'|\"[^\"\n]*\"")


def expression_text(text: Optional[str]) -> str:
    """The part of an EML string a tree parser would read.

    Drops the ``EML:`` prefix, everything after a prose separator, and ``#``
    comments, so a fallback scan sees what the parser sees and never counts
    a ``b3`` that only occurs in a comment or in narration.
    """
    s = (text or "").strip()
    if s.startswith("EML:"):
        s = s[len("EML:"):]
    for sep in _PROSE_TAILS:
        if sep in s:
            s = s.split(sep, 1)[0]
    return "\n".join(line.split("#", 1)[0] for line in s.splitlines()).strip()


def seed_numbers_in(text: Optional[str], b3: Optional[float] = None) -> List[str]:
    """Number tokens in *text* (not part of an identifier) equal to ±b₃."""
    if not text:
        return []
    target = live_b3() if b3 is None else b3
    return [n for n in _NUMBER_RE.findall(text) if is_b3_scalar(n, target)]


def scan_expression(text: Optional[str],
                    b3: Optional[float] = None) -> Tuple[List[str], List[str]]:
    """``(label_hits, seed_scalar_hits)`` in an EML expression string.

    Identifier-bounded, so ``b3`` inside ``b3_over_2pi`` or ``delta_b3`` is
    not a hit -- exactly as those parse to their own leaf labels.
    """
    expr = expression_text(text)
    if not expr:
        return [], []
    target = live_b3() if b3 is None else b3
    labels: List[str] = []
    for quoted in _QUOTED_RE.findall(expr):        # eml_vec('topology.elder_kads')
        if is_b3_label(quoted[1:-1]):
            labels.append(quoted[1:-1])
    bare = _QUOTED_RE.sub(" ", expr)
    for ident in _IDENT_RE.findall(bare):
        if is_b3_label(ident):
            labels.append(ident)
    return labels, seed_numbers_in(bare, target)


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


# ── Where each formula's tree string comes from in the source ────────────────
#
# A tree string written as f"ops.mul(eml_scalar({b3 // 2}), ...)" carries the
# NUMBER the expression evaluated to at registration time, not a leaf. The
# walker cannot see a provenance that is not in the string, so such trees are
# found in the source, attributed to formula ids, and REPORTED -- the count is
# the thing to ratchet down by replacing interpolation with labelled leaves.
#
# The same scan finds formula ids registered by MORE THAN ONE simulation. The
# registry keeps the last registration, so when the competing tree strings
# disagree about b3, the published verdict depends on which simulation ran
# (or imported) last -- a registration-order dependence the walk inherits and
# cannot repair, only report.

#: Formula fields a tree is parsed from (eml_tree_str first; an
#: ``EML:``-prefixed eml_description when the tree string is empty).
TREE_FIELDS: Tuple[str, ...] = ("eml_tree_str", "eml_description")

_FMT_PERCENT_RE = re.compile(
    r"%(?:\([^)]*\))?[-#0 +]*(?:\d+|\*)?(?:\.(?:\d+|\*))?[diouxXeEfFgGcrsa%]")
_FMT_BRACE_RE = re.compile(r"\{[^{}]*\}")
_B3_NAME_RE = re.compile(r"(?:^|_)b_?3(?:$|_)|elder_kads")


def _how_built(node: ast.AST) -> Optional[str]:
    """None for a plain string literal, else how the string is computed."""
    if isinstance(node, ast.Constant):
        return None if isinstance(node.value, str) else "computed"
    if isinstance(node, ast.JoinedStr):
        if any(isinstance(v, ast.FormattedValue) for v in node.values):
            return "f-string"
        return None
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Mod):
            return "%-format"
        if isinstance(node.op, ast.Add):
            return _how_built(node.left) or _how_built(node.right)
        return "computed"
    if isinstance(node, ast.IfExp):
        return _how_built(node.body) or _how_built(node.orelse)
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "format"):
        return ".format"
    return "computed"


def _template(node: ast.AST) -> Tuple[List[str], List[ast.AST]]:
    """(literal fragments in order, interpolated sub-expressions)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value], []
    if isinstance(node, ast.JoinedStr):
        frags, exprs = [], []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                frags.append(v.value)
            elif isinstance(v, ast.FormattedValue):
                exprs.append(v.value)
        return frags, exprs
    if (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod)
            and isinstance(node.left, ast.Constant)
            and isinstance(node.left.value, str)):
        return _FMT_PERCENT_RE.split(node.left.value), [node.right]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        lf, le = _template(node.left)
        rf, re_ = _template(node.right)
        return lf + rf, le + re_
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "format"
            and isinstance(node.func.value, ast.Constant)
            and isinstance(node.func.value.value, str)):
        return (_FMT_BRACE_RE.split(node.func.value.value),
                list(node.args) + [k.value for k in node.keywords])
    return [], [node]


def _names_b3(exprs: Iterable[ast.AST]) -> bool:
    """True if an interpolated expression names b3 (``b3 // 2``, ``_b3_seed``,
    ``reg.elder_kads``) -- provenance the rendered string no longer carries."""
    for e in exprs:
        for sub in ast.walk(e):
            name = (sub.id if isinstance(sub, ast.Name)
                    else sub.attr if isinstance(sub, ast.Attribute) else None)
            if name is None:
                continue
            bare = name.lstrip("_")
            if is_b3_label(bare) or _B3_NAME_RE.search(bare):
                return True
    return False


def _const_str(node: Optional[ast.AST]) -> Optional[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def formula_tree_sites(root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """One record per ``*Formula(...)`` call under *root*.

    *root* defaults to the package's ``simulations/`` tree -- the code that
    registers what formulas.json publishes. Each record:

      ``file``, ``line``  the call
      ``formula_id``      its constant ``id=``, or None when computed
      ``simulations``     constant ids of ``SimulationMetadata(...)`` in the
                          same file, to attribute a call whose id is computed
      ``field``           the keyword the tree is parsed from, mirroring the
                          tree generator: a non-empty ``eml_tree_str``, else an
                          ``EML:`` ``eml_description``; None if neither
      ``how``             None for a plain literal (implicit concatenation of
                          literals included), else ``f-string``, ``%-format``,
                          ``.format`` or ``computed``
      ``fragments``       the literal pieces of that string, in order
      ``names_b3``        an interpolated expression names b3

    Sorted by file and line, so every report built from it is stable.
    """
    root = (Path(root) if root is not None
            else Path(__file__).resolve().parents[1] / "simulations")
    sites: List[Dict[str, Any]] = []
    for path in sorted(root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, SyntaxError, ValueError):
            continue
        calls, sims = [], set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fname = (getattr(node.func, "id", None)
                     or getattr(node.func, "attr", None) or "")
            kws = {k.arg: k.value for k in node.keywords if k.arg}
            if fname == "SimulationMetadata" and _const_str(kws.get("id")):
                sims.add(_const_str(kws["id"]))
            elif fname.endswith("Formula") and "id" in kws:
                calls.append((node, kws))
        for node, kws in calls:
            field = None
            for name in TREE_FIELDS:
                value = kws.get(name)
                if value is None:
                    continue
                how = _how_built(value)
                if how is None:
                    text = "".join(_template(value)[0])
                    usable = (text.strip() if name == "eml_tree_str"
                              else text.strip().startswith("EML:"))
                    if not usable:
                        continue
                field = name
                break
            record: Dict[str, Any] = {
                "file": path.relative_to(root).as_posix(),
                "line": node.lineno,
                "formula_id": _const_str(kws.get("id")),
                "simulations": sorted(sims),
                "field": field,
                "how": None,
                "fragments": [],
                "names_b3": False,
            }
            if field is not None:
                value = kws[field]
                frags, exprs = _template(value)
                record["how"] = _how_built(value)
                record["fragments"] = [f for f in frags if f.strip()]
                record["names_b3"] = _names_b3(exprs)
            sites.append(record)
    sites.sort(key=lambda s: (s["file"], s["line"]))
    return sites


def site_verdict(site: Dict[str, Any], b3: Optional[float] = None) -> str:
    """rooted / ambiguous / not_rooted / no_tree for one registration site,
    judged from the literal text it would publish (fragments, for a computed
    string -- so a b3 that is only interpolated does not count)."""
    if site.get("field") is None:
        return "no_tree"
    labels, scalars = scan_expression(" ".join(site.get("fragments") or []), b3)
    return "rooted" if labels else ("ambiguous" if scalars else "not_rooted")


def matches_template(text: Optional[str], fragments: Iterable[str]) -> bool:
    """True if every literal fragment occurs in *text*, in order."""
    if not text:
        return False
    pos = 0
    for frag in fragments:
        i = text.find(frag, pos)
        if i < 0:
            return False
        pos = i + len(frag)
    return True


__all__ = [
    "B3_VALUE",
    "B3_TOLERANCE",
    "B3_LEAF_FUNCTIONS",
    "B3_LABEL_TOKENS",
    "NUMERIC_KINDS",
    "TREE_FIELDS",
    "live_seed",
    "live_b3",
    "seed_header",
    "is_b3_scalar",
    "is_b3_label",
    "expression_text",
    "seed_numbers_in",
    "scan_expression",
    "truncate_paths",
    "formula_tree_sites",
    "site_verdict",
    "matches_template",
]
