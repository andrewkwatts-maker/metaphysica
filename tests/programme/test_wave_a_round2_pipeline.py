"""Wave A round 2, pipeline: checks of simulations/run_all_simulations.py.

XB-11: the one-line note that names the build steps which write the
validation statistics is printed only when ``--quiet`` is not given.
Review D: the text of the note is the module constant
VALIDATION_STATISTICS_NOTE, printed by name, so the guard costs main() no
line; main() is no longer than it was before the guard.

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
NOTE_CONSTANT = "VALIDATION_STATISTICS_NOTE"
# Measured 2026-11-11 with ast on run_all_simulations.py: main() spans 426
# lines after the note moved to the module constant (429 before the XB-11
# guard at 19153d8~1, 430 with the guard at 19153d8).
MAIN_LINES = 426


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
    """True for a ``print(...)`` of the note: its literal text or the constant."""
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
        return False
    if node.func.id != "print":
        return False
    return any(_holds_note(part) for part in ast.walk(node))


def _holds_note(part: ast.AST) -> bool:
    """True for a string literal holding the note or the name of its constant."""
    if isinstance(part, ast.Name):
        return part.id == NOTE_CONSTANT
    return (
        isinstance(part, ast.Constant)
        and isinstance(part.value, str)
        and STATISTICS_NOTE in part.value
    )


def _runner_tree() -> ast.Module:
    return ast.parse(RUNNER.read_text(encoding="utf-8"))


def _main(tree: ast.Module) -> ast.FunctionDef:
    return next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
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
    found = list(_note_prints(_runner_tree()))
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


def test_review_d_detector_reads_a_print_of_the_constant():
    """print(VALIDATION_STATISTICS_NOTE) is a print of the note, guarded or not."""
    bare = ast.parse(f"print({NOTE_CONSTANT})")
    guarded = ast.parse(f"if not args.quiet:\n    print({NOTE_CONSTANT})")
    other = ast.parse("print(SOME_OTHER_NOTE)")
    assert [g for _, g in _note_prints(bare)] == [False]
    assert [g for _, g in _note_prints(guarded)] == [True]
    assert list(_note_prints(other)) == []


def test_review_d_note_text_is_a_module_constant():
    """The constant is assigned once at module level and holds the whole note."""
    values = [
        node.value for node in _runner_tree().body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == NOTE_CONSTANT for t in node.targets)
    ]
    assert len(values) == 1, f"{NOTE_CONSTANT} is assigned {len(values)} times at module level"
    text = ast.literal_eval(values[0])
    assert text.startswith(STATISTICS_NOTE)
    assert "'Build validation statistics' (--pre-rigor)" in text
    assert "'Refresh validation statistics from this build's rigor report'" in text


def test_review_d_main_prints_the_constant_and_did_not_grow():
    """main() prints the note by name, in one guarded print, and is 426 lines."""
    main = _main(_runner_tree())
    literals = [
        node.lineno for node in ast.walk(main)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and STATISTICS_NOTE in node.value
    ]
    assert literals == [], f"main() still types the note text at line(s) {literals}"
    assert [g for _, g in _note_prints(main)] == [True]
    assert main.end_lineno - main.lineno + 1 == MAIN_LINES
