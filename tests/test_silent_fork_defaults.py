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


# ---------------------------------------------------------------------------
# THE SWEEP ABOVE COULD NOT SEE THE REGISTRY'S OWN READERS
# ---------------------------------------------------------------------------
# `_FORK_READING_MODULES` never listed `simulations/core/variants.py`, and
# listing it would not have helped: the detector's shape signature is "a
# function that calls resolve()", while a fork's `read_adopted` reader does
# the opposite -- it reads the SOURCE module directly so the declaration can
# be checked against live state. So the readers were invisible to the sweep
# written to protect them, and on 2026-09-26 one of them was found carrying
# the defect in triplicate: `_dark_energy_betti_adopted` returned the literal
# "b3_24" from a bare `except Exception`, from a `w0 is None` guard, and from
# a `.get(n, "b3_24")` default -- and "b3_24" is also the option that fork
# DECLARES adopted, so every failure path confirmed the declaration. The
# ordinary path was a failure path, because `cosmology.w0_derived` is absent
# from the registry until a sim run fills it.
#
# This detector has the reader's shape: a `*_adopted` function that hands
# back a string literal when it cannot measure.

_VARIANTS_REL = "simulations/core/variants.py"


def _literal_fallbacks_in_readers(source: str):
    """(function, lineno, literal) for each reader that can return a literal
    option id without measuring anything."""
    tree = ast.parse(source)
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.endswith("_adopted"):
            continue
        for inner in ast.walk(node):
            # shape 1: an except handler that returns a string literal
            if isinstance(inner, ast.ExceptHandler):
                for stmt in ast.walk(inner):
                    if (isinstance(stmt, ast.Return)
                            and isinstance(stmt.value, ast.Constant)
                            and isinstance(stmt.value.value, str)):
                        offenders.append(
                            (node.name, stmt.lineno, stmt.value.value))
            # shape 2: dict.get(key, "literal") -- the silent default that
            # CLAUDE.md records as having published a whole statistics report
            if (isinstance(inner, ast.Call)
                    and getattr(inner.func, "attr", "") == "get"
                    and len(inner.args) == 2
                    and isinstance(inner.args[1], ast.Constant)
                    and isinstance(inner.args[1].value, str)):
                offenders.append(
                    (node.name, inner.lineno, inner.args[1].value))
    return offenders


def test_no_fork_reader_hands_back_a_literal_when_it_cannot_measure():
    """A reader that cannot see must raise, never name an option.

    Naming one is worse than raising: `describe()` compares the reader's
    answer to the declaration and publishes "no drift", so a reader that
    returns the declared default when blind publishes a verified state it
    never verified.
    """
    path = _SRC / _VARIANTS_REL
    assert path.is_file(), "%s is the fork registry; it must exist" % _VARIANTS_REL
    offenders = _literal_fallbacks_in_readers(path.read_text(encoding="utf-8"))
    assert not offenders, (
        "%s: fork reader(s) return a literal option id without measuring, at "
        "%s. Raise SourceUnmeasurable instead -- 'cannot tell' is not 'the "
        "declaration is correct'." % (_VARIANTS_REL, offenders)
    )


def test_the_reader_detector_can_actually_fire():
    """Both shapes, or the test above is an empty walk that always passes."""
    except_shape = (
        "def _x_adopted():\n"
        "    try:\n"
        "        return measure()\n"
        "    except Exception:\n"
        "        return 'b3_24'\n"
    )
    get_shape = (
        "def _y_adopted():\n"
        "    n = measure()\n"
        "    return {24: 'b3_24'}.get(n, 'b3_24')\n"
    )
    for label, source in (("except", except_shape), ("get", get_shape)):
        found = _literal_fallbacks_in_readers(source)
        assert found, (
            "the detector missed the %s shape it was written for" % label
        )


def test_every_fork_reader_is_covered_by_the_detector():
    """The detector is only worth its name if it walks every live reader.

    Counts the readers it inspects against the readers the registry actually
    wires up, so a reader added under a different naming convention fails
    here rather than escaping the sweep the way these ones did.
    """
    from metaphysica.simulations.core import variants

    wired = {
        fork.read_adopted.__name__
        for fork in variants.FORKS.values()
        if fork.read_adopted is not None
    }
    assert wired, "no fork wires up a reader; the guard would be inert"
    uncovered = {name for name in wired if not name.endswith("_adopted")}
    assert not uncovered, (
        "reader(s) %s are wired into FORKS but do not end in '_adopted', so "
        "the detector above walks past them" % sorted(uncovered)
    )
