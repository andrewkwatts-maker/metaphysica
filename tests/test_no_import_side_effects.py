"""Ratchet: importing an engine module must not touch the importer's process.

Three modules replaced sys.stdout at import; the old wrapper was then
collected and closed the importer's stream ("I/O operation on closed file").
plot_wz_evolution drew and saved two figures at import, to a hard-coded
path outside the repo. Module-level code may define, not act.
"""
from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "metaphysica"


def _top_level(tree: ast.Module):
    """Statements that run at import (not under `if __name__ == ...`)."""
    for node in tree.body:
        if isinstance(node, ast.If) and "__name__" in ast.unparse(node.test):
            continue
        yield node


def _offences(node) -> list[str]:
    bad = []
    for sub in ast.walk(node):
        if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        if isinstance(sub, ast.Assign) and any(
                ast.unparse(t) in ("sys.stdout", "sys.stderr") for t in sub.targets):
            bad.append("replaces " + ast.unparse(sub.targets[0]))
        if isinstance(sub, ast.Call) and ast.unparse(sub.func).endswith(".savefig"):
            bad.append("calls savefig")
    return bad


def test_no_module_acts_at_import():
    bad = []
    for path in sorted(SRC.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in _top_level(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            for what in _offences(node):
                bad.append("%s:%d %s" % (path.relative_to(SRC), node.lineno, what))
    assert not bad, bad
