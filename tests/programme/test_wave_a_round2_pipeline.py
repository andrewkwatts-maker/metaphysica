"""Wave A round 2, pipeline: checks of simulations/run_all_simulations.py.

XB-11: the one-line note that names the build steps which write the
validation statistics is printed only when ``--quiet`` is not given.

The runner is read as source, never imported or run: importing it loads
every simulation and running it writes the build output.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterator, Tuple

RUNNER = (
    Path(__file__).resolve().parents[2]
    / "src" / "metaphysica" / "simulations" / "run_all_simulations.py"
)
STATISTICS_NOTE = "Validation statistics are written by the build steps"


def _is_not_args_quiet(test: ast.expr) -> bool:
    """True for the expression ``not args.quiet``."""
    if not (isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not)):
        return False
    operand = test.operand
    return (
        isinstance(operand, ast.Attribute)
        and operand.attr == "quiet"
        and isinstance(operand.value, ast.Name)
        and operand.value.id == "args"
    )


def _is_note_print(node: ast.AST) -> bool:
    """True for a ``print(...)`` call whose literal text holds the note."""
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
        return False
    if node.func.id != "print":
        return False
    return any(
        isinstance(part, ast.Constant)
        and isinstance(part.value, str)
        and STATISTICS_NOTE in part.value
        for part in ast.walk(node)
    )


def _note_prints(node: ast.AST, guarded: bool = False) -> Iterator[Tuple[int, bool]]:
    """Yield (line, guarded) for each print of the note under ``node``.

    A print is guarded when it sits in the body of an ``if not args.quiet:``;
    the ``else`` branch of that ``if`` runs with ``--quiet`` and is not.
    """
    if isinstance(node, ast.If):
        inner = guarded or _is_not_args_quiet(node.test)
        for child in node.body:
            yield from _note_prints(child, inner)
        for child in node.orelse:
            yield from _note_prints(child, guarded)
        return
    if _is_note_print(node):
        yield node.lineno, guarded
        return
    for child in ast.iter_child_nodes(node):
        yield from _note_prints(child, guarded)


def test_xb11_statistics_note_respects_quiet():
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    found = list(_note_prints(tree))
    assert found, "the runner no longer prints the validation statistics note"
    unguarded = [line for line, guarded in found if not guarded]
    assert unguarded == [], (
        f"run_all_simulations.py prints the statistics note with --quiet "
        f"(no 'if not args.quiet:' around line(s) {unguarded})"
    )


def test_xb11_guard_detector_tells_the_two_cases_apart():
    """The detector itself: an unguarded print and an else branch both count."""
    bare = ast.parse(f"print({STATISTICS_NOTE!r})")
    guarded = ast.parse(f"if not args.quiet:\n    print({STATISTICS_NOTE!r})")
    in_else = ast.parse(
        f"if not args.quiet:\n    pass\nelse:\n    print({STATISTICS_NOTE!r})"
    )
    assert [g for _, g in _note_prints(bare)] == [False]
    assert [g for _, g in _note_prints(guarded)] == [True]
    assert [g for _, g in _note_prints(in_else)] == [False]
