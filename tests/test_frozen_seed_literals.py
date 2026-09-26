"""Constants whose own comment declares a b_3 formula the literal only satisfies at 24.

WHAT THIS MEASURES, AND WHY IT IS A CLASS AND NOT THREE BUGS
===========================================================
`FormulasRegistry` resolves the live seed correctly -- `self._b3 =
_seed_values(_resolve_b3_path())[0]` -- and several constants ride it, so
`demiurgic_coupling` is b_3/2 + 1/pi = 21.818 and `pressure_divisor` is
b_3^2/4 = 462.25 under the ADOPTED `seed_43_joyce` (author ruling 2026-09-22,
(b_2, b_3) = (12, 43); `simulations/PM/geometry/b3_path.py` is the SSoT for the
active path and carries the accepted costs).

Others did not move. They are FROZEN LITERALS: a number in the source, plus an
adjacent comment or docstring declaring a b_3-dependent derivation for it,
where the number satisfies that derivation only at the ABANDONED seed
b_3 = 24. `LOGIC_CLOSURE = 288  # topological: 12 x b3` is the clearest shape:
12 x 24 = 288 and 12 x 43 = 516, so the comment and the literal on that one
line are now two different claims.

This file does not fix them, and no successor to it should. Whether a given
literal SHOULD move is a physics ruling: a freeze can be load-bearing -- 163
also equals 288 - 125, which carries no b_3 at all, and sigma_T = 23/24 is
pinned by two guards that would record a violation the moment it moved.
`docs/FROZEN_SEED_LITERALS.md` holds the per-row accounting, the consumers and
the guards. What this file does is MEASURE the population from the source text,
so the next one cannot arrive unnoticed.

WHY IT PARSES THE SOURCE INSTEAD OF LISTING THE CONSTANTS
=========================================================
A hand-written list of frozen constants finds exactly the constants someone
already found. Here the declared formula is extracted from the comment or
docstring that annotates each number, normalised to a Python expression,
evaluated at the live seed and at 24, and compared against the number the
framework actually serves -- so a new constant annotated `= 12 * b3` and left
at 288 is reported by the same machinery that reported the first one.

WHY THE ASSERTIONS ARE SET EQUALITIES
=====================================
The inventories below are pinned as exact sets, compared with `==`. A NEW
frozen literal fails this file, and a REPAIRED one fails it too. A count that
can only go one way is not a check -- it is the defect this project keeps
re-learning, so the check that measures the defect must not have it.

THREE POPULATIONS, KEPT APART
=============================
They are different defects and must not be summed:

  FROZEN_LITERAL     a value the framework actually SERVES (a constant
                     assignment, or a live registry reading) satisfies its
                     declared b_3 formula at 24 and not at the live seed.
  PROSE_ONLY_STALE   no live reading carries the declared number; only the
                     comment's worked example does. Stale narration.
  UNDECIDED          the declared formula matches the written value at NEITHER
                     seed. Either the annotation is wrong, or the harvester
                     mis-paired a prose fragment with a number. These cannot
                     be told apart mechanically, so they are pinned as a count
                     with the rows printed on failure, not as a set of claims.

`chi_eff = 144` is measured here like everything else and is NOT to be
repaired: it is forked as `chi_eff_route`, status OPEN/unruled, and
`test_chi_eff_is_reported_and_left_unruled` asserts it stays unruled.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import ast
import io
import math
import re
import tokenize
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest

from metaphysica.simulations.PM.geometry.b3_path import (
    resolve_path as resolve_b3_path,
    seed_values,
)

#: The seed the frozen literals were written at. b3_path labels it unreachable
#: by the Joyce construction: b_3 = 7 (mod 12), and 24 = 0 (mod 12).
ABANDONED_SEED = 24

CORE = (Path(__file__).resolve().parents[1]
        / "src" / "metaphysica" / "simulations" / "core")

#: Modules scanned for declared-derivation constants. `variants.py` is
#: EXCLUDED, and the exclusion is asserted below rather than left implicit: it
#: is the fork registry, so its b_3 expressions describe branches the framework
#: does NOT take, and scoring those against the live seed would report the
#: off-path branch's own honest record (`w_0 = -23/24` under `seed_24`) as a
#: defect.
SKIP_MODULES = frozenset({"variants.py"})

# --------------------------------------------------------------------------
# harvesting the declared formulas out of the source text
# --------------------------------------------------------------------------

#: How b_3 is spelled in these comments: b3, b_3, B3, B_3.
_SEED_TOKEN = re.compile(r"\b[bB]_?3\b")
_MARK = "\x01"

#: `12 x b3` and `24 x 12` write multiplication with a letter x. Only a letter
#: x BETWEEN two arithmetic atoms is an operator; anywhere else it is prose.
_LETTER_TIMES = re.compile(r"(?<=[\d)\x01])\s*[xX×]\s*(?=[\d(\x01])")

#: A maximal run of arithmetic characters, sqrt included. Scored only if it
#: contains the seed marker.
_ARITH_RUN = re.compile(r"(?:sqrt|[0-9.\s+\-*/()\x01])+")

_IDENT = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")

#: A declaration's subject has to be a NAME, not a sentence. Without this the
#: harvester reads "The total logic-closure integer 288 = 12 x b3" as a claim
#: about a variable called `integer`, and then scores it against whatever the
#: registry happens to serve under that name.
_SUBJECT = re.compile(
    r"^[-*•\s]*(?:\d+[.)]\s*)?"                 # bullet or "10. "
    r"(?:(?:FORMULA|GEOMETRIC|GNOSTIC|DERIVED|STATUS|NOTE|USE\s+FOR|KEY"
    r"|Formula|Derived|Note)\s*:\s*)?"               # label prefix
    r"(?P<name>[A-Za-z_][A-Za-z_0-9]*)"
    r"(?:\s*\^\s*-?\d+|_\{[^}]*\})?"                 # alpha^-1, x_{i}
    r"\s*$"
)

_SAFE_EXPR_NAMES = {"b3", "sqrt"}


def _balance(text: str) -> str:
    """Trim a harvested run down to balanced parentheses."""
    out = text
    while out.count("(") > out.count(")"):
        out = out[:out.index("(")] + out[out.index("(") + 1:]
    while out.count(")") > out.count("("):
        out = out[:out.rindex(")")] + out[out.rindex(")") + 1:]
    return out


def _clean_expr(run: str) -> Optional[str]:
    """One arithmetic run, normalised to a Python expression, or None."""
    e = _balance(run.strip()).strip()
    while e and e[-1] in "+-*/ .":
        e = e[:-1].strip()
    while e and e[0] in "*/ .":
        e = e[1:].strip()
    if _MARK not in e:
        return None
    e = re.sub(r"\s+", " ", e.replace(_MARK, "b3")).strip()
    if not e:
        return None
    try:
        tree = ast.parse(e, mode="eval")
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if node.id not in _SAFE_EXPR_NAMES:
                return None
        elif isinstance(node, ast.Call):
            if not (isinstance(node.func, ast.Name)
                    and node.func.id == "sqrt" and len(node.args) == 1):
                return None
        elif isinstance(node, (ast.Attribute, ast.Subscript, ast.Lambda,
                              ast.Compare, ast.BoolOp)):
            return None
    return e


def _mark(text: str) -> str:
    t = _SEED_TOKEN.sub(_MARK, text).replace("^", "**")
    return _LETTER_TIMES.sub("*", t)


_LETTERISH = re.compile(r"[A-Za-z_]")
_OPERATOR = re.compile(r"[+\-*/]")

#: Prose that trails a formula: "b3 - the Betti number", "b3 (flux quantization)".
_TRAILING_PROSE = re.compile(r"\s*(?:[-,(:;]|\bwhere\b|\bwhich\b).*$")


def _is_fragment(marked: str, run: re.Match, expr: str) -> bool:
    """Was this run cut out of a formula the harvester cannot evaluate?

    `kappa_Delta = B3/2 + 1/pi`, `chi_eff_total / (2*b3)` and
    `v_tree = k_gimel x (b3 - 4)` all contain a symbol with no numeric value
    here, so the arithmetic run stops against a letter and what is left is a
    FRAGMENT: it is not the declared formula, and scoring it says nothing
    about the constant.

    The tell is an OPERATOR between the run and an identifier. Prose merely
    abutting the run is not a fragment -- `288: Octonionic/24D structure
    (b3*12)` and `b3 - the Betti number` both stop at a word with no operator
    joining it to the formula, and both are real declarations.
    """
    raw = run.group(0)
    lo = run.start()
    while lo < run.end() and raw[lo - run.start()] in " \t*+-/":
        lo += 1
    hi = run.end()
    while hi > lo and raw[hi - 1 - run.start()] in " \t*+-/":
        hi -= 1
    if _crosses_operator_to_identifier(marked, lo, -1):
        return True
    if (_OPERATOR.search(expr)
            and _crosses_operator_to_identifier(marked, hi - 1, +1)):
        return True
    return False


def _crosses_operator_to_identifier(marked: str, index: int, step: int) -> bool:
    """From `index`, does whitespace-and-operators lead to an identifier?"""
    i = index + step
    crossed = False
    while 0 <= i < len(marked):
        ch = marked[i]
        if ch.isspace():
            pass
        elif ch in "*+-/\u00d7":
            crossed = True
        elif _LETTERISH.match(ch):
            return crossed
        else:
            return False
        i += step
    return False


def _best_expr(text: str) -> Optional[str]:
    """The LONGEST b_3-bearing expression in a piece of text, or None.

    One per piece, deliberately. `chi_eff_total / (2*b3)` yields both `(2*b3)`
    and, from a neighbouring word, a bare `b3`; scoring the fragments as well
    as the whole reports one declaration several times and scores pieces that
    claim nothing.

    A BARE `b3` is a claim -- "N_flux = ... = b3" and `MANIFOLD_BASE = 24  # b3`
    both say the constant IS the seed -- but only when it is what the text
    says, so it is accepted only if the text reduces to `b3` once a trailing
    prose clause is dropped. Without that, `roots_total = b3 * D_shadow_space`
    is read as the claim `roots_total = b3`.
    """
    marked = _mark(text)
    best: Optional[str] = None
    for run in _ARITH_RUN.finditer(marked):
        cleaned = _clean_expr(run.group(0))
        if cleaned is None or _is_fragment(marked, run, cleaned):
            continue
        if cleaned == "b3":
            reduced = _TRAILING_PROSE.sub("", marked.strip()).strip()
            if reduced != _MARK:
                continue
        if best is None or len(cleaned) > len(best):
            best = cleaned
    return best


def _eval_expr(expr: str, b3: int) -> Optional[float]:
    """Evaluate a declared formula. The grammar is restricted by _clean_expr."""
    try:
        return float(eval(  # noqa: S307
            compile(ast.parse(expr, mode="eval"), "<declared>", "eval"),
            {"__builtins__": {}},
            {"b3": b3, "sqrt": math.sqrt},
        ))
    except Exception:
        return None


def _numeric_part(part: str) -> Optional[Tuple[str, float]]:
    """A chain part that is a plain number (or plain arithmetic), b_3-free."""
    marked = _mark(part)
    if _MARK in marked:
        return None
    best: Optional[Tuple[str, float]] = None
    for run in re.finditer(r"[0-9.\s+\-*/()]+", marked):
        raw = _balance(run.group(0).strip()).strip()
        while raw and raw[-1] in "+-*/ .":
            raw = raw[:-1].strip()
        if not raw or not re.search(r"\d", raw):
            continue
        try:
            value = float(eval(  # noqa: S307
                compile(ast.parse(raw, mode="eval"), "<n>", "eval"),
                {"__builtins__": {}}, {}))
        except Exception:
            continue
        if best is None or len(raw) > len(best[0]):
            best = (raw, value)
    return best


def _display_tolerance(raw: str, value: float) -> float:
    """Half a unit in the last decimal place the source actually wrote.

    A comment writing `-0.204` cannot be checked to 1e-9 -- it is a rounded
    display of a full-precision quantity. A comment writing `288` can be.
    """
    if "." in raw:
        decimals = len(raw.rsplit(".", 1)[1])
        return 0.5 * 10.0 ** (-decimals) + 1e-12
    return 1e-9 * max(1.0, abs(value))


def _subject_of(head: str) -> Optional[str]:
    """The name a declaration is about, or None when the head is a sentence."""
    m = _SUBJECT.match(head)
    return m.group("name") if m else None


_CHAIN = re.compile(r"[^=\n]+(?:=[^=\n]+)+")


def _annotated_texts(src: str) -> List[Tuple[int, str]]:
    """Every comment and docstring line in a module, with its line number."""
    texts: List[Tuple[int, str]] = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            texts.append((tok.start[0], tok.string.lstrip("#").strip()))
    for node in ast.walk(ast.parse(src)):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
            continue
        doc = ast.get_docstring(node)
        if not doc:
            continue
        base = node.body[0].lineno
        for i, line in enumerate(doc.splitlines()):
            texts.append((base + i, line.strip()))
    return texts


def _trailing_comments(src: str) -> Dict[int, str]:
    """line number -> the comment on that line."""
    out: Dict[int, str] = {}
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            out[tok.start[0]] = tok.string.lstrip("#").strip()
    return out


def _constant_assignments(src: str) -> List[Tuple[int, str, float]]:
    """(lineno, name, value) for every assignment that folds to a number.

    Anything reading `self._b3` rides the seed by construction and is not a
    frozen literal, so it does not fold and is not collected.
    """
    out: List[Tuple[int, str, float]] = []
    for node in ast.walk(ast.parse(src)):
        if not isinstance(node, ast.Assign):
            continue
        try:
            value = eval(  # noqa: S307 - constant fold in an empty namespace
                compile(ast.Expression(node.value), "<const>", "eval"),
                {"__builtins__": {}}, {})
        except Exception:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                out.append((node.lineno, target.id, float(value)))
            elif (isinstance(target, ast.Attribute)
                  and isinstance(target.value, ast.Name)
                  and target.value.id == "self"):
                out.append((node.lineno, target.attr, float(value)))
    return out


# --------------------------------------------------------------------------
# resolving what a declaration is about, in the LIVE framework
# --------------------------------------------------------------------------

def _live_registry():
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    return FormulasRegistry()


def _numeric_readings(registry) -> Dict[str, float]:
    """Every numeric reading the registry serves, public property or attribute."""
    out: Dict[str, float] = {}
    for name in dir(type(registry)):
        if name.startswith("__"):
            continue
        try:
            value = getattr(registry, name)
        except Exception:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        out[name] = float(value)
    for name, value in vars(registry).items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        out[name] = float(value)
    return out


def _resolve_subject(subject: str,
                     readings: Dict[str, float]) -> Optional[Tuple[str, float]]:
    """A declared name -> the live reading it names, or None."""
    for candidate in (subject, "_" + subject, subject.lower(),
                      "_" + subject.lower(), subject.upper()):
        if candidate in readings:
            return candidate, readings[candidate]
    return None


#: Name parts that say nothing about WHICH quantity a reading is.
_GENERIC_TOKENS = frozenset({"total", "value", "derived", "base", "const",
                             "constant", "sum", "num", "raw"})


def _tokens(name: str) -> set:
    """A reading's name, split into the parts that identify the quantity."""
    parts = re.split(r"[_\W]+|(?<=[a-z0-9])(?=[A-Z])", name.lstrip("-_"))
    return {p.lower() for p in parts
            if len(p) >= 2 and p.lower() not in _GENERIC_TOKENS}


def _holders(value: float, readings: Dict[str, float],
             subject: Optional[str] = None) -> List[str]:
    """Live readings equal to a declared value, or to its negation.

    This is how a declaration written about a name the registry does not
    export reaches the reading that actually serves it, without a hand-written
    alias table: the link is MEASURED, so it keeps working for the next alias
    nobody wrote down.

    A value match alone is not enough, because the small integers are shared
    by unrelated quantities -- 24 is both the abandoned b_3 and the spacelike
    core dimension `D_space_24`, and FormulasRegistry says in as many words
    that those are not the same object. When `subject` is given the match must
    therefore be CORROBORATED by a shared name part, so a declaration about
    `N_flux` is not credited to `D_space_24`.
    """
    out: List[str] = []
    tol = 1e-9 * max(1.0, abs(value))
    wanted = _tokens(subject) if subject else None
    for name, live in sorted(readings.items()):
        if name.startswith("_") and name.lstrip("_") in readings:
            continue
        if abs(live - value) <= tol:
            candidate = name
        elif abs(live + value) <= tol:
            candidate = "-" + name
        else:
            continue
        if wanted is not None and not (wanted & _tokens(name)):
            continue
        out.append(candidate)
    return out


# --------------------------------------------------------------------------
# the scan
# --------------------------------------------------------------------------

FROZEN_LITERAL = "FROZEN_LITERAL"
PROSE_ONLY_STALE = "PROSE_ONLY_STALE"
UNDECIDED = "UNDECIDED"
RIDES_SEED = "RIDES_SEED"

#: How the value a declaration is about was found, most authoritative first.
BY_ASSIGNMENT = "assignment"        # a constant literal on the annotated line
BY_NAME = "live_reading"            # the declared name resolves to a reading
BY_VALUE = "live_holder"            # a reading equals the declared number
BY_PROSE = "declared_value"         # only the comment carries the number


def scan(b3_live: int) -> List[Dict[str, Any]]:
    """Every declared b_3 formula in the core modules, scored at both seeds."""
    readings = _numeric_readings(_live_registry())
    rows: List[Dict[str, Any]] = []
    seen: set = set()

    for path in sorted(CORE.glob("*.py")):
        if path.name in SKIP_MODULES:
            continue
        src = path.read_text(encoding="utf-8")
        trailing = _trailing_comments(src)

        # CHANNEL A -- a constant assignment whose own comment declares a
        # b_3 formula. This is the `LOGIC_CLOSURE = 288  # 12 x b3` shape, and
        # it needs no '=' in the comment because the assignment supplies it.
        for lineno, name, value in _constant_assignments(src):
            expr = _best_expr(trailing.get(lineno, ""))
            if expr is None:
                continue
            _emit(rows, seen, path, lineno, trailing[lineno], name, expr,
                  value, BY_ASSIGNMENT, 1e-9 * max(1.0, abs(value)),
                  b3_live, readings)

        # CHANNEL B -- an '=' chain in a comment or docstring, whose head is a
        # NAME and whose tail carries a b_3 formula.
        for lineno, text in _annotated_texts(src):
            for chain in _CHAIN.finditer(text):
                parts = chain.group(0).split("=")
                if len(parts) < 2:
                    continue
                subject = _subject_of(parts[0])
                if subject is None:
                    continue
                exprs = [e for e in (_best_expr(p) for p in parts[1:]) if e]
                if not exprs:
                    continue
                expr = max(exprs, key=len)
                numeric = [n for n in (_numeric_part(p) for p in parts[1:])
                           if n]
                resolved = _resolve_subject(subject, readings)
                if resolved is not None:
                    origin, name, value = BY_NAME, resolved[0], resolved[1]
                    tol = 1e-9 * max(1.0, abs(value))
                elif numeric:
                    raw, value = numeric[-1]
                    name = subject
                    tol = _display_tolerance(raw, value)
                    origin = (BY_VALUE
                              if _holders(value, readings, subject)
                              else BY_PROSE)
                else:
                    continue
                _emit(rows, seen, path, lineno, text, name, expr, value,
                      origin, tol, b3_live, readings)
    return rows


def _emit(rows, seen, path, lineno, text, name, expr, value, origin, tol,
          b3_live, readings) -> None:
    at_24 = _eval_expr(expr, ABANDONED_SEED)
    at_live = _eval_expr(expr, b3_live)
    if at_24 is None or at_live is None:
        return
    holds_24 = abs(value - at_24) <= tol
    holds_live = abs(value - at_live) <= tol

    if holds_live:
        verdict = RIDES_SEED
    elif not holds_24:
        verdict = UNDECIDED
    elif origin in (BY_ASSIGNMENT, BY_NAME, BY_VALUE):
        verdict = FROZEN_LITERAL
    else:
        verdict = PROSE_ONLY_STALE

    key = (path.name, name, expr, round(value, 9), verdict)
    if key in seen:
        return
    seen.add(key)
    rows.append({
        "module": path.name,
        "lineno": lineno,
        "subject": name,
        "origin": origin,
        "declared_formula": expr,
        "source_text": text,
        "value": value,
        "at_24": at_24,
        "at_live": at_live,
        "holds_at_24": holds_24,
        "holds_at_live": holds_live,
        "verdict": verdict,
        # Reported UNCORROBORATED, deliberately: every reading that happens to
        # equal this value, whether or not its name relates to the subject.
        # The verdict above used the corroborated list; this field is for the
        # reader, and it is what shows that `N_flux = 24` matches
        # `D_space_24` by value while being a different object.
        "live_holders": _holders(value, readings),
    })


def _keys(rows, verdict) -> List[Tuple[str, str, str, float]]:
    return sorted((r["module"], r["subject"], r["declared_formula"],
                   round(r["value"], 6))
                  for r in rows if r["verdict"] == verdict)


# --------------------------------------------------------------------------
# the pinned inventories
# --------------------------------------------------------------------------
#
# MEASURED 2026-09-26 against the ADOPTED seed, b_3 = 43 (`seed_43_joyce`).
# Each entry is (module, subject, declared formula, the value served).
#
# These are SETS, compared with ==. Adding a frozen literal fails this file;
# repairing one fails it too. Do NOT edit an inventory to make the file pass:
# the point of pinning it is that a change in this population is a change the
# author has to look at. `docs/FROZEN_SEED_LITERALS.md` carries the per-row
# accounting, every consumer and the guards that pin each value.

#: A value the framework SERVES satisfies its declared formula at 24, not live.
FROZEN_AT_24: List[Tuple[str, str, str, float]] = [
    # 288 = 12 x b_3. Also 135 + 153, which carries no b_3 -- a dichotomy.
    ("FormulasRegistry.py", "LOGIC_CLOSURE", "12*b3", 288.0),
    ("FormulasRegistry.py", "roots_total", "(b3*12)", 288.0),
    # the chi_eff pair, forked as chi_eff_route and TO BE LEFT UNRULED
    ("FormulasRegistry.py", "chi_eff_shadow", "b3**2/8", 72.0),
    ("FormulasRegistry.py", "chi_eff_total", "b3**2/4", 144.0),
    # 163 = 7*b_3 - 5. Also 288 - 125, which carries no b_3 -- a dichotomy.
    ("FormulasRegistry.py", "sterile_sector", "7*b3 - 5", 163.0),
    ("identify_ghost_literals.py", "sterile_sector", "(7*b3)-5", 163.0),
    # D_bulk - b_3 = 2. b3_path already records this identity as BROKEN on the
    # adopted path (26 - 43 = -17); the registry docstring still asserts it.
    ("FormulasRegistry.py", "D_bulk", "b3 + 2", 26.0),
    # the "Clean Room" independent validator's own seed, hardcoded at 24, so
    # the sterility report cross-checks the live framework against the
    # abandoned seed
    ("verify_sterility_report.py", "MANIFOLD_BASE", "b3", 24.0),
]

#: Only a comment carries the number; no live reading does. Stale narration.
PROSE_STALE_AT_24: List[Tuple[str, str, str, float]] = [
    ("FormulasRegistry.py", "N_flux", "b3", 24.0),
    ("FormulasRegistry.py", "denominator", "b3*10 - 1", 239.0),
    # w_0 = -1 + 1/b_3 = -23/24: the frozen sigma_T reached through the w_0
    # identity. `calculate_w0` returns -self._tzimtzum_pressure, and the
    # literal itself is annotated "sigma_T = 23/24" with no b_3 in it, so the
    # harvester reaches it here and not at the assignment. See
    # test_tzimtzum_pressure_satisfies_its_declared_form_only_at_24.
    ("FormulasRegistry.py", "w0", "-1 + 1/b3", -0.9583),
    ("FormulasRegistry.py", "w_a", "-1/sqrt(b3)", -0.204),
]

#: Matches at neither seed: a wrong annotation, or a mis-paired fragment.
#: Pinned as a COUNT, not a set, because the two cannot be told apart
#: mechanically and pinning the set would pin parser behaviour. The count is
#: compared with ==, so it fails in both directions like the sets do.
UNDECIDED_COUNT = 0


@pytest.fixture(scope="module")
def live_seed() -> int:
    b3, _b2 = seed_values(resolve_b3_path())
    return b3


@pytest.fixture(scope="module")
def rows(live_seed) -> List[Dict[str, Any]]:
    return scan(live_seed)


# ------------------------------------------------------- the detector works

def test_the_adopted_seed_is_not_the_abandoned_one(live_seed):
    """Everything below is vacuous if the live seed is 24.

    If the author rules back to `seed_24` this file stops measuring anything
    and must be re-read rather than left passing emptily.
    """
    assert live_seed != ABANDONED_SEED, (
        "the live seed is 24, so 'holds at 24' and 'holds at the live seed' "
        "are the same question and this file measures nothing"
    )
    assert live_seed == 43, (
        "ADOPTED b3_seed = seed_43_joyce (author ruling 2026-09-22); a "
        "different seed means the inventories below were measured elsewhere"
    )


def test_the_parser_finds_the_shapes_the_source_actually_writes():
    assert _best_expr("topological: 12 x b3") == "12*b3"
    assert _best_expr("chi_eff_shadow = b3^2/8 = 576/8 = 72") == "b3**2/8"
    assert _best_expr("sterile_sector = 163 (= 7*b3 - 5)") == "7*b3 - 5"
    assert _best_expr("w_a = -1/sqrt(b3)") == "-1/sqrt(b3)"
    assert _best_expr("no seed here at all") is None
    # prose must not be swallowed into the expression
    assert _best_expr(
        "The total logic-closure integer 288 = 12 x b3 is topological."
    ) == "12*b3"
    # a bare b3 is a claim only where the text says so
    assert _best_expr("b3 - the Betti number") == "b3"
    assert _best_expr("roots_total = b3 * D_shadow_space = 288") is None


def test_the_parser_refuses_a_fragment_of_a_formula_it_cannot_evaluate():
    """`1/pi` and `chi_eff_total / (...)` leave arithmetic the seed does not
    explain, and scoring the leftover says nothing about the constant."""
    assert _best_expr("n_gen = chi_eff_total / (2*b3) = 144/48") is None
    assert _best_expr("kappa_Delta = B3/2 + 1/pi = 12 + 0.318") is None
    # the source writes this one with a multiplication sign, not a letter x
    assert _best_expr("v_tree = k_gimel \u00d7 (b3 - 4) = 246.37 GeV") is None
    assert _best_expr("alpha^-1 = k_gimel^2 - b3/phi + phi/(4*pi)") is None
    # ... while a formula that IS fully arithmetic survives intact
    assert _best_expr("C_kaf = b3 * (b3 - 7) / (b3 - 9) = 27.2") == (
        "b3 * (b3 - 7) / (b3 - 9)")


def test_the_parser_refuses_a_sentence_as_a_subject():
    """Without this the harvester invents variables called `integer` and `be`."""
    assert _subject_of("  sterile_sector ") == "sterile_sector"
    assert _subject_of("  - roots_total ") == "roots_total"
    assert _subject_of("  FORMULA: eta_S ") == "eta_S"
    assert _subject_of("  10. kappa_Delta ") == "kappa_Delta"
    assert _subject_of("  alpha^-1 ") == "alpha"
    assert _subject_of("The total logic-closure integer 288 ") is None
    assert _subject_of("(which would be 480 ") is None
    assert _subject_of("2. GEOMETRIC: 288 ") is None


def test_the_declared_formulas_are_evaluated_not_pattern_matched():
    assert _eval_expr("12 * b3", 24) == 288
    assert _eval_expr("12 * b3", 43) == 516
    assert _eval_expr("7*b3 - 5", 24) == 163
    assert _eval_expr("7*b3 - 5", 43) == 296
    assert _eval_expr("b3**2/4", 24) == 144.0
    assert _eval_expr("b3**2/4", 43) == pytest.approx(462.25)
    assert _eval_expr("-(b3-1)/b3", 24) == pytest.approx(-23 / 24)
    assert _eval_expr("-(b3-1)/b3", 43) == pytest.approx(-42 / 43)
    # the grammar is closed: no attribute access, no call but sqrt
    assert _clean_expr("b3.real") is None
    assert _clean_expr("len(b3)") is None


def test_the_scan_is_not_empty(rows):
    """A detector that finds nothing is indistinguishable from a broken one."""
    assert len(rows) >= 10, (
        "the harvester stopped finding declared b_3 formulas -- far more "
        "likely the parser broke than that the comments vanished"
    )
    assert any(r["verdict"] == RIDES_SEED for r in rows), (
        "nothing rides the seed, which cannot be true: pressure_divisor and "
        "c_kaf both do"
    )
    assert {r["verdict"] for r in rows} <= {
        FROZEN_LITERAL, PROSE_ONLY_STALE, UNDECIDED, RIDES_SEED}


def test_the_fork_registry_is_deliberately_not_scanned():
    """`variants.py` describes branches the framework does NOT take.

    Scoring its b_3 expressions against the live seed would report the
    off-path branch's own honest record as a frozen literal. The exclusion is
    asserted so it stays a decision rather than becoming an oversight.
    """
    assert "variants.py" in SKIP_MODULES
    assert (CORE / "variants.py").exists(), (
        "the fork registry moved; the exclusion above now hides nothing and "
        "should be re-pointed or dropped"
    )


# --------------------------------------------- the population, pinned as sets

def test_the_frozen_literal_inventory_is_exactly_what_is_pinned(rows):
    """Set equality, so this fails on a new one AND on a repaired one."""
    measured = _keys(rows, FROZEN_LITERAL)
    assert measured == sorted(FROZEN_AT_24), _diff(
        measured, sorted(FROZEN_AT_24), rows, FROZEN_LITERAL)


def test_the_stale_prose_inventory_is_exactly_what_is_pinned(rows):
    measured = _keys(rows, PROSE_ONLY_STALE)
    assert measured == sorted(PROSE_STALE_AT_24), _diff(
        measured, sorted(PROSE_STALE_AT_24), rows, PROSE_ONLY_STALE)


def test_the_undecided_count_is_exactly_what_is_pinned(rows):
    """Declarations true at neither seed. Pinned both ways, as a count."""
    undecided = [r for r in rows if r["verdict"] == UNDECIDED]
    assert len(undecided) == UNDECIDED_COUNT, "\n".join(
        ["UNDECIDED population is %d, pinned at %d."
         % (len(undecided), UNDECIDED_COUNT)]
        + ["  %s:%d  %s = %g, declared %s -> %g at 24, %g live\n      %s"
           % (r["module"], r["lineno"], r["subject"], r["value"],
              r["declared_formula"], r["at_24"], r["at_live"],
              r["source_text"][:100]) for r in undecided]
        + ["A row here is either an annotation that is wrong at both seeds or "
           "a prose fragment the harvester mis-paired. Read it before "
           "repinning."])


def _diff(measured, pinned, rows, verdict) -> str:
    new = [k for k in measured if k not in pinned]
    gone = [k for k in pinned if k not in measured]
    by_key = {(r["module"], r["subject"], r["declared_formula"],
               round(r["value"], 6)): r
              for r in rows if r["verdict"] == verdict}
    lines = ["%s population changed." % verdict]
    for k in new:
        r = by_key[k]
        lines.append(
            "  NEW   %s:%d  %s = %g, declared %s -> %g at b_3=24, %g live"
            % (r["module"], r["lineno"], r["subject"], r["value"],
               r["declared_formula"], r["at_24"], r["at_live"]))
        lines.append("        source: %s" % r["source_text"][:110])
    for k in gone:
        lines.append(
            "  GONE  %s %s (declared %s, value %g) left this population"
            % (k[0], k[1], k[2], k[3]))
    lines.append(
        "A NEW entry is a constant annotated with a b_3 derivation it does "
        "not satisfy at the live seed. A GONE entry means a value or an "
        "annotation moved -- which of the two, and whether the move was an "
        "AUTHOR ruling, belongs in docs/FROZEN_SEED_LITERALS.md and the "
        "outstanding-issues register BEFORE this inventory is repinned.")
    return "\n".join(lines)


# ------------------------------------------- the three named dichotomies

def test_bulk_pressure_satisfies_its_declared_form_only_at_24(live_seed):
    """163 = 7*b_3 - 5 holds at 24 and gives 296 at the live seed.

    The registry already exposes BOTH sides, so the break is visible without
    changing anything: `sterile_sector_derived` is 288 - 125 = 163 and carries
    no b_3, while `odowd_bulk_derived` is 7*b_3 - 5 and follows the seed.
    `BULK_PRESSURE` is the frozen one, and it is frozen at the value the
    b_3-free derivation also gives -- which is exactly why unfreezing it is a
    ruling and not a repair.
    """
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    registry = FormulasRegistry()
    assert FormulasRegistry.BULK_PRESSURE == 163
    assert registry.odowd_bulk_pressure == 163
    assert _eval_expr("7*b3 - 5", ABANDONED_SEED) == 163
    assert _eval_expr("7*b3 - 5", live_seed) == 296
    assert registry.odowd_bulk_derived == 296, (
        "the derived side stopped following the seed"
    )
    assert registry.sterile_sector_derived == 163, (
        "the 288 - 125 side carries no b_3 and must not move"
    )
    assert registry.verify_bulk_pressure_derivation() is False, (
        "the two sides agree again -- one of them moved; that is an author "
        "ruling and the register must say which"
    )


def test_logic_closure_satisfies_its_declared_form_only_at_24(live_seed):
    """288 = 12 x b_3 holds at 24 and gives 516 at the live seed."""
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    registry = FormulasRegistry()
    assert FormulasRegistry.LOGIC_CLOSURE == 288
    assert registry.roots_total == 288
    assert _eval_expr("12 * b3", ABANDONED_SEED) == 288
    assert _eval_expr("12 * b3", live_seed) == 516
    # The value ALSO has a second, b_3-free derivation: 135 + 153. The freeze
    # is therefore not obviously wrong -- it is a dichotomy, and which of the
    # two derivations is structural is the author's ruling.
    assert registry.shadow_sector + registry.christ_constant == 288


def test_tzimtzum_pressure_satisfies_its_declared_form_only_at_24(live_seed):
    """sigma_T = 23/24, while the declared form is (b_3 - 1)/b_3.

    The framework's `dark_energy_betti` ruling puts n = b_3 in w_0 = -(n-1)/n,
    and `b3_path.downstream` computes exactly that -- so the seed-following
    w_0 and the frozen sigma_T disagree at the live seed while
    `calculate_w0` still returns -sigma_T.
    """
    from metaphysica.simulations.PM.geometry.b3_path import downstream
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    registry = FormulasRegistry()
    assert registry.tzimtzum_pressure == pytest.approx(23.0 / 24.0)
    assert registry.w0_dark_energy == pytest.approx(-23.0 / 24.0)
    assert _eval_expr("(b3-1)/b3", ABANDONED_SEED) == pytest.approx(23 / 24)
    assert _eval_expr("(b3-1)/b3", live_seed) == pytest.approx(42 / 43)

    declared = downstream()
    assert declared["w0_formula"] == "-(b_3 - 1)/b_3"
    assert declared["w0"] == pytest.approx(-(live_seed - 1) / live_seed)
    assert abs(declared["w0"] - registry.w0_dark_energy) > 1e-3, (
        "the seed-following w_0 and the frozen sigma_T agree again -- one of "
        "them moved, and which is an author ruling"
    )


def test_chi_eff_is_reported_and_left_unruled():
    """`chi_eff = 144` is forked as `chi_eff_route`, status OPEN/unruled.

    It is measured here like everything else and MUST NOT be repaired by this
    file or any successor. The assertion is that the fork is still unruled, so
    a silent adoption fires this test.
    """
    from metaphysica.simulations.core.variants import FORKS, resolve

    assert "chi_eff_route" in FORKS
    assert resolve("chi_eff_route") == "unruled", (
        "chi_eff_route has been selected; that is the author's ruling, and "
        "this file must be re-read against it rather than updated to match"
    )

    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    registry = FormulasRegistry()
    # The two claimed origins, both live, disagreeing honestly.
    assert registry.chi_eff_total == 144
    assert registry.pressure_divisor == pytest.approx(registry.b3 ** 2 / 4.0), (
        "the b_3^2/4 route stopped riding the seed"
    )
    assert registry.pressure_divisor != registry.chi_eff_total, (
        "the two chi_eff routes agree again; at b_3 = 24 they did, and that "
        "coincidence is what the fork exists to record"
    )


# ------------------------------------------------- what the guards pin

def test_the_parity_guard_is_tautological_and_cannot_fire():
    """`DemonLockGuard.EXPECTED_PARITY_SUM` reads the value it checks.

    It is a property returning `self.registry.parity_sum`, and
    `verify_sterile_parity` compares `self.registry.parity_sum` against it. On
    the registry side that is x == x, so the guard cannot fire whatever eta_S
    or sigma_T become -- only its JSON branch can. This is ASSERTED rather
    than fixed: what the parity invariant should be pinned against on the 43
    path is the author's ruling. What must not happen is that it goes on being
    believed to be a live check.
    """
    from metaphysica.simulations.core.demon_lock_guard import DemonLockGuard

    registry = _live_registry()
    guard = DemonLockGuard(registry=registry)
    assert guard.EXPECTED_PARITY_SUM == registry.parity_sum
    assert guard.verify_sterile_parity() is True

    # Proof it is a tautology and not a coincidence: move the very value the
    # guard exists to guard, and it still passes. The registry here is a
    # scratch instance; nothing is committed.
    registry._tzimtzum_pressure = (registry.b3 - 1) / registry.b3
    assert guard.verify_sterile_parity() is True, (
        "the guard fired, so it is no longer tautological -- good, but "
        "re-read this test and the register together"
    )
    assert guard.violations == []


def test_the_hard_tzimtzum_guards_would_trip_if_the_literal_moved():
    """THREE guards pin sigma_T to 23/24 BY LITERAL, and all three fire.

    This is the load-bearing part of the freeze, and why unfreezing sigma_T is
    not a one-line change. The moment the value stops being exactly 23/24:

      * `demon_lock_guard.verify_tzimtzum_fraction` records
        "TZIMTZUM ERROR: Registry drift detected. Must be 23/24."
      * `demon_lock_guard.verify_w0_seal` records a W0 ERROR, because it pins
        `registry.w0_dark_energy` -- w_0 = -sigma_T -- to -23/24 at 1e-10
      * `FormulasRegistry.verify_tzimtzum_fraction` returns False at 1e-15

    Both guard checks run inside `run_preflight`, so the preflight fails. That
    is the cost of the repair, and it is stated here rather than discovered.
    """
    from metaphysica.simulations.core.demon_lock_guard import DemonLockGuard

    registry = _live_registry()
    assert registry.verify_tzimtzum_fraction() is True
    intact = DemonLockGuard(registry=registry)
    assert intact.verify_tzimtzum_fraction() is True
    assert intact.verify_w0_seal() is True
    assert intact.violations == []

    # The declared (b_3 - 1)/b_3 form, applied to a scratch instance only.
    # Nothing is committed; the assertions are about the GUARDS.
    registry._tzimtzum_pressure = (registry.b3 - 1) / registry.b3
    assert registry.verify_tzimtzum_fraction() is False
    tripped = DemonLockGuard(registry=registry)
    assert tripped.verify_tzimtzum_fraction() is False
    assert tripped.verify_w0_seal() is False
    assert any("TZIMTZUM" in v for v in tripped.violations), (
        "the guard stopped naming the violation, so unfreezing sigma_T would "
        "now be silent"
    )
    assert any("W0 ERROR" in v for v in tripped.violations), (
        "the w_0 seal stopped firing; it is the second of the three pins and "
        "the register must say why it was released"
    )


def test_the_hubble_guard_also_cannot_fire():
    """`verify_hubble_formula` rounds the value it then compares.

    `expected_h0 = round(self.registry.h0_local, 2)` and the comparison is
    `abs(registry.h0_local - expected_h0) > 0.01`, which rounding can never
    reach. Its docstring claims to verify H0 = 71.55; the live H0 is 71.74,
    because eta_S follows the seed. Neither the claim nor the number is
    touched here -- what is recorded is that the check does not test them.
    """
    from metaphysica.simulations.core.demon_lock_guard import DemonLockGuard

    registry = _live_registry()
    guard = DemonLockGuard(registry=registry)
    assert guard.verify_hubble_formula() is True
    assert registry.h0_local != pytest.approx(71.55, abs=0.01), (
        "h0_local is back at the 24-era 71.55; the register must say why"
    )
    # ... and it still passes with an H0 nowhere near the docstring's 71.55
    registry._sophian_drag = 0.0
    assert guard.verify_hubble_formula() is True, (
        "the H0 guard fired, so it is no longer self-referential; re-read "
        "this test"
    )


def test_the_registry_parity_check_is_already_failing_at_the_live_seed():
    """`FormulasRegistry.verify_parity` pins 1.64034 = 163/239 + 23/24.

    eta_S follows the seed to 163/429, so the live parity sum is 1.33829 and
    this check returns False. Nothing else asserts it, so it fails silently
    into `sync_docs` and the sterility report. Recorded here, not repaired:
    what the parity invariant is on the 43 path is a physics ruling.
    """
    registry = _live_registry()
    assert registry.parity_sum == pytest.approx(163 / 429 + 23 / 24)
    assert registry.parity_sum == pytest.approx(1.3382867132867133, rel=1e-12)
    assert registry.verify_parity() is False, (
        "verify_parity passes again -- either its pinned 1.64034 moved or "
        "eta_S / sigma_T did, and the register must say which"
    )
    # ... and it passed at the abandoned seed, which is the whole point.
    assert abs((163 / 239 + 23 / 24) - 1.64034) < 2e-4
