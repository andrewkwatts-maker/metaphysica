"""A plotting dependency must not decide whether a simulation runs.

WHY THIS EXISTS
===============
matplotlib is the ``[plots]`` extra. CI installs ``.[dev,sims]``. Three
simulation modules under ``PM/consciousness`` imported it at module top level,
so on every CI run the import raised, ``run_all_simulations`` swallowed it, and
three simulations were silently absent along with four formulas:

    four-dice-branch-count          four_dice_sampling
    gnosis-coherence-enhancement    gnosis_unlocking
    gnosis-unlocking-probability    gnosis_unlocking
    pair-shielding-enhancement      orch_or_pair_shielding

That is exactly the gap between the 569 formulas the author's build produced
and the 565 CI produced, and it is why ``test_arithma_b3_coverage_never_regresses``
asserted ``565 >= 569`` and failed for six days. The coverage never regressed;
an optional dependency was silently deleting content.

This is the third appearance of one defect shape in this repository: nine
simulations that had never run because their import sat under an
``except ImportError``; a stub arithma that imported and could not compute;
and now a figure library gating a physics module.

WHAT IS ASSERTED
================
Every module under ``simulations/PM`` must import with matplotlib unavailable,
and no module outside ``simulations/visualizations`` may import it at top
level. Both checks are made to FAIL on a perturbation, because a guard that
cannot fire is the thing this file exists to prevent.
"""

from __future__ import annotations

import ast
import builtins
import importlib
import pathlib
import sys

import pytest

_SIM_ROOT = (pathlib.Path(__file__).resolve().parents[1] / "src" / "metaphysica"
             / "simulations")

#: Where drawing IS the purpose, so a top-level import is correct.
_PLOTTING_PACKAGE = "visualizations"

#: The four formulas that vanished, named so a regression is legible rather
#: than a count that moved.
FORMULAS_THAT_VANISHED = (
    "four-dice-branch-count",
    "gnosis-coherence-enhancement",
    "gnosis-unlocking-probability",
    "pair-shielding-enhancement",
)


def _top_level_matplotlib_importers():
    """Modules importing matplotlib at module scope, outside visualizations."""
    offenders = []
    for path in sorted(_SIM_ROOT.rglob("*.py")):
        if _PLOTTING_PACKAGE in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:                    # not ours to judge here
            continue
        for node in tree.body:                 # module scope ONLY, not nested
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            if any(n.split(".")[0] == "matplotlib" for n in names):
                offenders.append(str(path.relative_to(_SIM_ROOT)))
                break
    return offenders


def test_no_simulation_imports_matplotlib_at_module_scope():
    offenders = _top_level_matplotlib_importers()
    assert offenders == [], (
        "These modules import matplotlib at module scope, so they disappear "
        "from any install without the [plots] extra -- CI included -- taking "
        "their formulas with them: %s. Import it inside the function that "
        "draws, via simulations.core.optional_plotting." % ", ".join(offenders)
    )


def test_the_scan_detects_a_top_level_import(tmp_path, monkeypatch):
    """The load-bearing half: a scanner that cannot find one finds nothing."""
    planted = _SIM_ROOT / "PM" / "_planted_offender_for_this_test.py"
    planted.write_text("import matplotlib.pyplot as plt\n", encoding="utf-8")
    try:
        offenders = _top_level_matplotlib_importers()
        assert any("_planted_offender" in o for o in offenders), (
            "the scan did not notice a module importing matplotlib at module "
            "scope, so its clean report above means nothing"
        )
    finally:
        planted.unlink()


@pytest.mark.parametrize("module_name", [
    "metaphysica.simulations.PM.consciousness.four_dice_sampling",
    "metaphysica.simulations.PM.consciousness.gnosis_unlocking",
    "metaphysica.simulations.PM.consciousness.orch_or_pair_shielding",
])
def test_the_three_modules_import_with_matplotlib_unavailable(module_name,
                                                              monkeypatch):
    """Import them with matplotlib forced absent, as CI has it."""
    real_import = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name.split(".")[0] == "matplotlib":
            raise ImportError("matplotlib blocked by this test")
        return real_import(name, *args, **kwargs)

    for loaded in [m for m in sys.modules if m.startswith("matplotlib")]:
        monkeypatch.delitem(sys.modules, loaded, raising=False)
    monkeypatch.delitem(sys.modules, module_name, raising=False)
    monkeypatch.setattr(builtins, "__import__", blocked)

    module = importlib.import_module(module_name)
    assert module is not None


def test_the_import_block_is_real(monkeypatch):
    """If the block above does not block, the three tests prove nothing."""
    real_import = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name.split(".")[0] == "matplotlib":
            raise ImportError("matplotlib blocked by this test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    with pytest.raises(ImportError):
        importlib.import_module("matplotlib.pyplot")


def test_optional_plotting_names_the_extra_rather_than_raising_bare():
    from metaphysica.simulations.core import optional_plotting

    assert "[plots]" in optional_plotting._HINT
    # available() must answer about the real environment, not a constant.
    assert optional_plotting.available() is (
        importlib.util.find_spec("matplotlib") is not None)
