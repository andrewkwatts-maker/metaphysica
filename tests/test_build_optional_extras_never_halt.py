"""A missing optional extra yields an INCOMPLETE build, never a failed one.

WHY THIS EXISTS
---------------
`build.py` states the rule in a comment next to the gate that enforces it:

    A missing optional extra should yield an incomplete build, never a
    failed one.

and `CLAUDE.md` repeats it as a promise to users:

    build.py skips steps whose extras are missing with a friendly install
    hint instead of failing -- so a slim install never produces a broken
    build.

The rule was enforced by a hand-maintained map, `OPTIONAL_DEPS`, and on
2026-09-22 a step was missing from it. `Build proof-completeness ledger`
imports pandas inside `proof_completeness.build_ledger` and raises an
ImportError that NAMES the `plots` extra -- a well-behaved module doing
exactly the right thing -- but because the step had no row in the map,
nothing caught it and the build HALTED. Every step after it never ran, and
the operator saw "exited with code 1", which reads as a broken build rather
than an incomplete one.

A map is only as good as the thing that checks it is complete. This test is
that thing: it reads the steps' own source for optional-dependency imports
and requires each one to be gated. The defect class is "someone added a step
and forgot the row", so the test has to look at the steps rather than at the
map.

SCOPE, STATED HONESTLY
----------------------
This checks the modules a build step invokes for a top-level or function-level
import of a known optional package. It cannot see a dependency reached through
a deeper call chain, so passing here is not proof that no step can ever halt.
It catches the shape that actually shipped, which is the one worth catching.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from metaphysica.build import OPTIONAL_DEPS, STEPS

#: Packages that live behind an extra, mapped to the extra that supplies them.
#: Taken from `pyproject.toml`'s optional-dependencies, not invented here.
OPTIONAL_PACKAGES = {
    "eml_spectral": "sims",
    "matplotlib": "plots",
    "pandas": "plots",
    "xhtml2pdf": "pdf",
    "playwright": "hq-pdf",
    "pypdf": "hq-pdf",
}

_IMPORT = re.compile(
    r"^\s*(?:import|from)\s+(%s)\b" % "|".join(OPTIONAL_PACKAGES),
    re.MULTILINE,
)


def _module_source(cmd) -> str:
    """The source of the module a build step runs, or '' when not resolvable."""
    if len(cmd) < 3 or cmd[1] != "-m":
        return ""
    parts = cmd[2].split(".")
    root = Path(__file__).resolve().parents[1] / "src"
    path = root.joinpath(*parts).with_suffix(".py")
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _generator_steps():
    """(label, cmd) for every step invoked as `python -m <module>`."""
    return [(label, cmd) for label, cmd, _extra in STEPS
            if len(cmd) >= 3 and cmd[1] == "-m"]


def test_at_least_one_step_is_inspectable():
    """A source-reading test over an empty set would pass forever."""
    steps = _generator_steps()
    assert len(steps) > 10, steps
    assert any(_module_source(cmd) for _label, cmd in steps)


@pytest.mark.parametrize(
    "label,cmd", _generator_steps(), ids=lambda v: v if isinstance(v, str) else "")
def test_step_importing_an_optional_package_is_gated(label, cmd):
    """Any step whose generator imports an optional package needs a row."""
    source = _module_source(cmd)
    if not source:
        pytest.skip("step %r is not a resolvable `-m` module" % label)
    found = sorted(set(_IMPORT.findall(source)))
    if not found:
        return
    assert label in OPTIONAL_DEPS, (
        "build step %r imports optional package(s) %s but has no row in "
        "OPTIONAL_DEPS, so a tree without that extra HALTS the build instead "
        "of skipping the step. Add: %r: (%r, %r)"
        % (label, found, label, OPTIONAL_PACKAGES[found[0]], tuple(found))
    )


def test_the_proof_completeness_step_is_gated_on_plots():
    """The row that was missing, pinned by name.

    Kept as its own test rather than folded into the sweep above, because the
    import that halted the build is inside `proof_completeness.build_ledger`
    rather than in the generator module the step invokes -- so the sweep does
    not see it, and only a named assertion holds this one down.
    """
    assert OPTIONAL_DEPS.get("Build proof-completeness ledger") == (
        "plots", ("pandas",)), (
        "the proof-completeness step lost its OPTIONAL_DEPS row; a tree "
        "without pandas will halt the whole build again"
    )


def test_every_optional_deps_row_names_a_real_step():
    """A row for a step that no longer exists gates nothing."""
    labels = {label for label, _cmd, _extra in STEPS}
    stale = sorted(set(OPTIONAL_DEPS) - labels)
    assert not stale, (
        "OPTIONAL_DEPS rows naming steps that are not in STEPS: %s" % stale)
