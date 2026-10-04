"""Ranking is confined to the D-019 comparator modules (governance test).

D-019: "Only the comparator module may rank." In the test ground, the words
rank / ranked / best / winner / recommend / recommended may appear in CODE
(identifiers, attributes, imports, string literals -- not docstrings or
comments) only in:

    assessment/comparator.py, assessment/tiebreak.py, assessment/recommend.py,
    assessment/report.py, cli.py, graph/build.py

The engine's legacy modules switch_search, fork_implications and
preferred_path stay non-ranking: they still return NO_SELECTION_MADE and do not
import the comparator.

The scanner is itself tested on snippets so a scanner that finds nothing
cannot pass silently.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Iterator, List, Set, Tuple

_SRC = Path(__file__).resolve().parents[2] / "src" / "metaphysica"
_PKG = _SRC / "testground"
_CORE = _SRC / "simulations" / "core"

BANNED = frozenset({"rank", "ranked", "best", "winner", "recommend",
                    "recommended"})
ALLOWED = frozenset({
    "assessment/comparator.py",
    "assessment/tiebreak.py",
    "assessment/recommend.py",
    "assessment/report.py",
    "cli.py",
    "graph/build.py",
})
NON_RANKING_ENGINE = ("switch_search.py", "fork_implications.py",
                      "preferred_path.py")
RANKING_MODULES = ("metaphysica.testground.assessment.comparator",
                   "metaphysica.testground.assessment.tiebreak",
                   "metaphysica.testground.assessment.recommend")


def _docstring_ids(tree: ast.AST) -> Set[int]:
    """id() of every docstring Constant node."""
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                ids.add(id(first.value))
    return ids


def _texts(tree: ast.AST) -> Iterator[Tuple[str, int]]:
    """Every identifier and non-docstring string in the code, with a line."""
    skip = _docstring_ids(tree)
    for node in ast.walk(tree):
        line = getattr(node, "lineno", 0)
        if isinstance(node, ast.Name):
            yield node.id, line
        elif isinstance(node, ast.Attribute):
            yield node.attr, line
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                               ast.ClassDef)):
            yield node.name, line
        elif isinstance(node, ast.arg):
            yield node.arg, line
        elif isinstance(node, ast.keyword) and node.arg:
            yield node.arg, line
        elif isinstance(node, ast.alias):
            yield node.name, line
            if node.asname:
                yield node.asname, line
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module, line
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            for name in node.names:
                yield name, line
        elif (isinstance(node, ast.Constant) and isinstance(node.value, str)
              and id(node) not in skip):
            yield node.value, line


def _words(text: str) -> List[str]:
    """Split identifiers and prose into lower-case words (snake, camel)."""
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    return [w.lower() for w in re.findall(r"[A-Za-z]+", spaced)]


def banned_words(source: str) -> List[Tuple[str, int]]:
    """(word, line) for every banned word in the code of ``source``."""
    tree = ast.parse(source)
    return sorted({(w, line) for text, line in _texts(tree)
                   for w in _words(text) if w in BANNED})


def _relative(path: Path) -> str:
    return path.relative_to(_PKG).as_posix()


def test_ranking_words_appear_only_in_the_comparator_modules():
    offenders = []
    for path in sorted(_PKG.rglob("*.py")):
        if _relative(path) in ALLOWED:
            continue
        hits = banned_words(path.read_text(encoding="utf-8"))
        offenders += ["%s:%d %s" % (_relative(path), line, word)
                      for word, line in hits]
    assert not offenders, offenders


def test_the_comparator_modules_exist_and_do_rank():
    """The allowance is used where it is granted (and only there)."""
    for rel in ("assessment/comparator.py", "assessment/recommend.py"):
        assert banned_words((_PKG / rel).read_text(encoding="utf-8")), rel


def test_the_scanner_flags_ranking_in_code():
    """Falsifiability: each code form is caught."""
    snippets = {
        "def rank(xs):\n    return xs\n": "rank",
        "x = 'best'\n": "best",
        "RECOMMEND_CHANGE = 1\n": "recommend",
        "y = obj.winner\n": "winner",
        "from m import rank\n": "rank",
        "def f(ranked):\n    return ranked\n": "ranked",
        "f(recommended=True)\n": "recommended",
        "class BestPath:\n    pass\n": "best",
        "z = f'{a} is best'\n": "best",
    }
    for source, word in snippets.items():
        assert word in {w for w, _ in banned_words(source)}, source


def test_the_scanner_ignores_docstrings_and_comments():
    source = ('"""The best path is ranked here."""\n'
              "# rank the winner\n"
              "def f():\n"
              '    """Recommend nothing."""\n'
              "    return 1  # best\n")
    assert banned_words(source) == []


def _constants(path: Path) -> Set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def _imports(path: Path) -> Set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
            out.update("%s.%s" % (node.module, a.name) for a in node.names)
        elif isinstance(node, ast.Import):
            out.update(a.name for a in node.names)
    return out


def test_the_legacy_engine_modules_stay_non_ranking():
    """switch_search, fork_implications, preferred_path: NO_SELECTION_MADE."""
    for name in NON_RANKING_ENGINE:
        path = _CORE / name
        assert "NO_SELECTION_MADE" in _constants(path), name
        assert not any(i.startswith(RANKING_MODULES)
                       for i in _imports(path)), name
