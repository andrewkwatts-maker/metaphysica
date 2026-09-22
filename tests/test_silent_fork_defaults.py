"""A fork read that fails must say so. The narration may not invent a branch.

THE DEFECT THIS FILE GUARDS
===========================
`geometry_narration._resolve` caught bare `Exception` and returned a hardcoded
fallback. `variants.resolve` raises KeyError for a fork that is not declared
and ValueError for an option that does not exist, so both were swallowed: a
renamed or deleted fork would have left the module narrating `all_plus_one`
while its own docstring promised a live read. A silent default, in the module
written to abolish silent defaults.

Three more instances of the same shape were found by an AST sweep on
2026-09-22 and narrowed the same way:

    b3_path.n_gen_report        the n_gen_source override -- the block whose
                                whole purpose is to make the inconsistent
                                combination reachable
    preferred_path._invalidate_caches   a stale cache surviving a switch flip
                                is what that function exists to prevent
    free_set._param_candidates  (introduced the same day and caught by the
                                same sweep)

WHAT IS STILL TOLERATED, AND WHY
================================
ImportError only. `variants` can import a module that imports it back, and
during that window a fallback is the only option. It is recorded in
`fork_reads_degraded()` and surfaced by `narrate()`, so a degraded read is
visible rather than indistinguishable from a live one.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from metaphysica.simulations.PM.geometry import geometry_narration as gn

_SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "metaphysica"

#: Modules whose fork reads must not be papered over. Each one resolves a fork
#: and each one had, or could acquire, the swallowing shape.
_FORK_READING_MODULES = (
    "simulations/PM/geometry/geometry_narration.py",
    "simulations/PM/geometry/b3_path.py",
    "simulations/core/preferred_path.py",
    "simulations/core/free_set.py",
    "simulations/PM/geometry/glued_orbit_scan.py",
)


def test_an_undeclared_fork_is_not_papered_over():
    """The load-bearing one: a missing fork must raise, not narrate a default."""
    with pytest.raises(KeyError):
        gn._resolve("a_fork_that_does_not_exist", "all_plus_one")


def test_an_unknown_option_is_not_papered_over(monkeypatch):
    """An environment naming a branch that does not exist must also raise."""
    monkeypatch.setenv("METAPHYSICA_VARIANT_G2_FORM_CONVENTION",
                       "not_a_real_branch")
    with pytest.raises(ValueError):
        gn._resolve("g2_form_convention", "all_plus_one")


def test_the_healthy_path_reports_no_degradation():
    """With the registry reachable, nothing may be flagged as fallen back."""
    gn.narrate()
    assert gn.fork_reads_degraded() == {}, (
        "a fork read fell back during an ordinary narration: %s"
        % gn.fork_reads_degraded()
    )


def test_narrate_carries_whether_every_read_was_live():
    report = gn.narrate()
    assert report["all_reads_were_live"] is True
    assert report["fork_reads_degraded"] == {}
    assert "WARNING" not in report["note"]


def test_a_degraded_read_is_visible_rather_than_silent(monkeypatch):
    """Force the one tolerated failure -- an ImportError -- and check it shows.

    Without this the ImportError branch would be untested, and an untested
    fallback is how the original defect survived. The import is broken by
    removing `variants` from sys.modules and blocking its re-import, which is
    what an import cycle looks like from inside `_resolve`.
    """
    import builtins
    import sys

    real_import = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name == "metaphysica.simulations.core.variants":
            raise ImportError("simulated import cycle")
        return real_import(name, *args, **kwargs)

    monkeypatch.delitem(sys.modules, "metaphysica.simulations.core.variants",
                        raising=False)
    monkeypatch.setattr(builtins, "__import__", blocked)

    gn._FALLBACKS_USED.clear()
    branch = gn._resolve("g2_form_convention", "all_plus_one")
    assert branch == "all_plus_one", "the tolerated fallback must still work"
    assert "g2_form_convention" in gn.fork_reads_degraded(), (
        "the fallback fired but was not recorded, so a degraded read is "
        "indistinguishable from a live one"
    )
    assert "import" in gn.fork_reads_degraded()["g2_form_convention"]


def test_the_degraded_flag_clears_on_the_next_live_read():
    """A stale warning is its own defect: it would cry wolf on every later run."""
    gn._FALLBACKS_USED.clear()
    gn._FALLBACKS_USED["g2_form_convention"] = "simulated"
    gn._resolve("g2_form_convention", "all_plus_one")
    assert gn.fork_reads_degraded() == {}, (
        "a successful live read did not clear the degraded marker"
    )


@pytest.mark.parametrize("relpath", _FORK_READING_MODULES)
def test_no_fork_reading_module_swallows_a_bare_exception(relpath):
    """AST, not grep: `except Exception: <fallback>` around a resolve() call.

    Flags any handler catching Exception or BaseException inside a function
    whose body also calls `resolve`. That is the precise shape -- a broad
    handler guarding a fork read -- and it is what four modules were carrying.
    """
    path = _SRC / relpath
    if not path.is_file():
        pytest.skip("%s not present" % relpath)

    tree = ast.parse(path.read_text(encoding="utf-8"))
    offenders = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        calls_resolve = any(
            isinstance(n, ast.Call)
            and getattr(n.func, "attr", getattr(n.func, "id", "")) == "resolve"
            for n in ast.walk(node))
        if not calls_resolve:
            continue
        for inner in ast.walk(node):
            if not isinstance(inner, ast.ExceptHandler):
                continue
            broad = inner.type is None or (
                isinstance(inner.type, ast.Name)
                and inner.type.id in ("Exception", "BaseException"))
            if broad:
                offenders.append((node.name, inner.lineno))

    assert not offenders, (
        "%s guards a fork read with a broad exception handler at %s. "
        "variants.resolve raises KeyError for an undeclared fork and "
        "ValueError for an unknown option; swallowing either narrates a "
        "default while claiming to read the live fork. Catch ImportError only."
        % (relpath, offenders)
    )


def test_the_ast_check_can_actually_fire():
    """A checker that cannot flag anything is the defect it hunts.

    Feed it the shape it is looking for and require a hit, so the parametrised
    test above is known to be doing work rather than passing on an empty walk.
    """
    source = (
        "def narrate():\n"
        "    try:\n"
        "        return resolve('g2_form_convention')\n"
        "    except Exception:\n"
        "        return 'all_plus_one'\n"
    )
    tree = ast.parse(source)
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        calls_resolve = any(
            isinstance(n, ast.Call)
            and getattr(n.func, "attr", getattr(n.func, "id", "")) == "resolve"
            for n in ast.walk(node))
        if not calls_resolve:
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.ExceptHandler) and (
                    inner.type is None
                    or (isinstance(inner.type, ast.Name)
                        and inner.type.id in ("Exception", "BaseException"))):
                offenders.append((node.name, inner.lineno))
    assert offenders, (
        "the detector did not flag the exact defect shape it was written for"
    )
