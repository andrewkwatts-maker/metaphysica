"""Every optional-import guard must name a symbol that actually exists.

WHY THIS EXISTS
---------------
run_all_simulations.py imports LagrangianMasterDerivationV19 from
PM/derivations/lagrangian_master.py. No such name exists -- the class is
LagrangianMasterDerivation, with no alias. The ImportError is swallowed by a
try/except that sets LAGRANGIAN_MASTER_V19_AVAILABLE = False, so the module is
silently skipped and NONE of its 3,939 lines run. It has been dead in the
pipeline while continuing to look wired.

The `try: import ... except ImportError: X_AVAILABLE = False` idiom is correct
and necessary for genuinely optional dependencies. What it cannot distinguish
is "this optional extra is not installed" from "this name is misspelled". This
test draws that line: a guard may fail because a THIRD-PARTY package is absent,
but never because a first-party symbol does not exist.

Deliberately not asserted here: whether lagrangian_master SHOULD be revived.
That is an author ruling -- it carries ~1,400 lines of Formula literals that
would enter the paper. This test only makes the deadness loud.
"""
from __future__ import annotations

import ast
import importlib
import io
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
_TARGETS = [
    _SRC / "metaphysica" / "simulations" / "run_all_simulations.py",
    _SRC / "metaphysica" / "simulations" / "__init__.py",
    _SRC / "metaphysica" / "simulations" / "base" / "registry.py",
]

#: Third-party extras that may legitimately be absent. A guard failing because
#: one of these is missing is the idiom working as intended.
_OPTIONAL_THIRD_PARTY = {
    "eml_math", "eml_spectral", "arithma", "matplotlib", "pandas",
    "scipy", "sympy", "reportlab", "PIL", "seaborn", "networkx",
}


def _guarded_first_party_imports(path: Path):
    """Yield (module, name) for first-party symbols imported inside a guard."""
    tree = ast.parse(io.open(path, encoding="utf-8").read())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        handles_import_error = any(
            (isinstance(h.type, ast.Name) and h.type.id in
             {"ImportError", "ModuleNotFoundError", "Exception"})
            or (isinstance(h.type, ast.Tuple) and any(
                isinstance(e, ast.Name) and e.id in
                {"ImportError", "ModuleNotFoundError", "Exception"}
                for e in h.type.elts))
            for h in node.handlers
        )
        if not handles_import_error:
            continue
        for sub in ast.walk(node):
            if not isinstance(sub, ast.ImportFrom) or not sub.module:
                continue
            root = sub.module.split(".")[0]
            if root in _OPTIONAL_THIRD_PARTY:
                continue
            if not sub.module.startswith("metaphysica"):
                continue
            for alias in sub.names:
                yield sub.module, alias.name


def _collect_dead():
    dead = []
    for path in _TARGETS:
        if not path.exists():
            continue
        for module_name, symbol in _guarded_first_party_imports(path):
            try:
                module = importlib.import_module(module_name)
            except ImportError as exc:
                missing = getattr(exc, "name", "") or ""
                if missing.split(".")[0] in _OPTIONAL_THIRD_PARTY:
                    continue  # a real optional extra; the guard is doing its job
                dead.append((path.name, module_name, symbol,
                             f"module import failed: {exc}"))
                continue
            if not hasattr(module, symbol):
                dead.append((path.name, module_name, symbol,
                             "module imports fine but has no such name"))
    return dead


#: Known-dead guarded imports, recorded 2026-08-22. Every one is a `V19`
#: suffix that does not exist -- a systematic rename dropped the suffix from
#: the class definitions and silently broke all nine imports at once, taking
#: 16,763 lines out of the pipeline while they continued to look wired:
#:
#:     lagrangian_master          3,938   LagrangianMasterDerivation
#:     gauge_sector_complete      2,020   GaugeSectorCompleteDerivations
#:     matter_sector_complete     1,921   MatterSectorCompleteDerivations
#:     cosmology_sector_complete  1,630   CosmologySectorCompleteDerivations
#:     appendix_m_tensor_calc     1,532   AppendixMTensorCalculus
#:     appendix_n_vielbein        1,563   AppendixNVielbein
#:     appendix_o_kk_reduction    1,333   AppendixOKKReduction
#:     appendix_p_g2_holonomy     1,324   AppendixPG2Holonomy
#:     appendix_q_index_theorem   1,502   AppendixQIndexTheorem
#:
#: This list is a RATCHET, not an acceptance. Reviving them is an author
#: ruling: they carry roughly 1,400 lines of Formula literals that would enter
#: the paper the moment the imports resolve, so switching them on is a physics
#: decision rather than a typo fix. Until that ruling, the debt is recorded
#: here and cannot grow -- an 11th dead import fails this test.
_KNOWN_DEAD = {
    ("metaphysica.simulations.PM.derivations.lagrangian_master",
     "LagrangianMasterDerivationV19"),
    ("metaphysica.simulations.PM.derivations.gauge_sector_complete",
     "GaugeSectorCompleteV19"),
    ("metaphysica.simulations.PM.derivations.matter_sector_complete",
     "MatterSectorCompleteV19"),
    ("metaphysica.simulations.PM.derivations.cosmology_sector_complete",
     "CosmologySectorCompleteV19"),
    ("metaphysica.simulations.PM.paper.appendices.appendix_m_tensor_calc",
     "AppendixMTensorCalcV19"),
    ("metaphysica.simulations.PM.paper.appendices.appendix_n_vielbein",
     "AppendixNVielbeinV19"),
    ("metaphysica.simulations.PM.paper.appendices.appendix_o_kk_reduction",
     "AppendixOKKReductionV19"),
    ("metaphysica.simulations.PM.paper.appendices.appendix_p_g2_holonomy",
     "AppendixPG2HolonomyV19"),
    ("metaphysica.simulations.PM.paper.appendices.appendix_q_index_theorem",
     "AppendixQIndexTheoremV19"),
    ("metaphysica.generators.validation.gemini_peer_review",
     "run_post_simulation_review"),
}


def test_no_new_silently_dead_imports():
    """A guard must not hide a typo.

    Fails on any dead guarded import that is not already in the recorded
    baseline, so this class of defect cannot grow.
    """
    dead = _collect_dead()
    new = [d for d in dead if (d[1], d[2]) not in _KNOWN_DEAD]
    if new:
        lines = [
            f"  {where}: from {mod} import {sym}  ->  {why}"
            for where, mod, sym, why in new
        ]
        pytest.fail(
            "NEW guarded imports name first-party symbols that do not exist. "
            "These fail silently and the module never runs:\n" + "\n".join(lines)
            + "\n\nFix the name, or add it to _KNOWN_DEAD with a reason."
        )


def test_known_dead_list_has_no_stale_entries():
    """If a dead import gets fixed, it must leave the baseline.

    Stops the ratchet from silently accumulating entries that no longer
    describe reality -- the same rot the list exists to prevent.
    """
    dead_keys = {(mod, sym) for _, mod, sym, _ in _collect_dead()}
    stale = _KNOWN_DEAD - dead_keys
    assert not stale, (
        "these are recorded as dead but now resolve; remove them from "
        f"_KNOWN_DEAD: {sorted(stale)}"
    )


def test_the_audit_can_actually_fail(tmp_path):
    """Mutation check: a deliberately dead guard must be detected.

    Without this, a scanner that silently matched nothing would pass forever.
    """
    fake = tmp_path / "fake_module.py"
    fake.write_text(
        "try:\n"
        "    from metaphysica.simulations.core.physics_config import NoSuchName\n"
        "    OK = True\n"
        "except ImportError:\n"
        "    OK = False\n",
        encoding="utf-8",
    )
    found = list(_guarded_first_party_imports(fake))
    assert ("metaphysica.simulations.core.physics_config", "NoSuchName") in found

    module = importlib.import_module("metaphysica.simulations.core.physics_config")
    assert not hasattr(module, "NoSuchName"), (
        "the scanner would not have flagged this"
    )


def test_scanner_ignores_optional_third_party_guards():
    """Guards around genuinely optional extras must NOT be flagged.

    This is the false-positive direction: eml_math/eml_spectral are optional
    by design, and a guard that catches their absence is correct.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "opt.py"
        p.write_text(
            "try:\n"
            "    from eml_spectral import EMLPair\n"
            "    OK = True\n"
            "except ImportError:\n"
            "    OK = False\n",
            encoding="utf-8",
        )
        assert list(_guarded_first_party_imports(p)) == []
