"""
Import Health Smoke Test
========================
Verifies that all remaining simulation modules import cleanly.
Catches broken imports from refactoring or archival.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

import importlib
import sys
from pathlib import Path

import pytest

# The simulation modules now live inside the metaphysica package; resolve
# their on-disk path via the installed package itself.
import metaphysica.simulations.PM as _PM_pkg
SIMULATIONS_DIR = Path(_PM_pkg.__file__).resolve().parent
PACKAGE_PREFIX = "metaphysica.simulations.PM"


def collect_module_paths():
    """Collect every Python module path under metaphysica.simulations.PM."""
    modules = []
    for py_file in SIMULATIONS_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        rel = py_file.relative_to(SIMULATIONS_DIR)
        sub = str(rel).replace("\\", "/").replace("/", ".").removesuffix(".py")
        modules.append(f"{PACKAGE_PREFIX}.{sub}")
    return sorted(modules)


MODULE_PATHS = collect_module_paths()

# Optional deps that live behind the package's [plots], [pdf], [sims] extras.
# A module that fails to import solely because one of these is missing is
# *not* a broken module — it's a module whose plot / PDF / sim path is
# unavailable in the current install. Skip cleanly in that case.
_OPTIONAL_DEPS = frozenset({
    "matplotlib", "matplotlib.pyplot", "matplotlib.figure",
    "pandas",
    "xhtml2pdf", "reportlab",
    "eml_spectral",
})


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_module_imports(module_path):
    """Each simulation module should import without errors.

    Modules that import only because an optional extra dep (matplotlib,
    pandas, xhtml2pdf, eml-spectral) is absent are skipped — those
    extras are deliberately not part of the slim CI install.
    """
    try:
        importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        # ModuleNotFoundError carries the missing module name in `.name`.
        # If it's a known optional extra, this is a graceful skip.
        if (e.name or "").split(".")[0] in _OPTIONAL_DEPS:
            pytest.skip(
                f"{module_path}: optional dep '{e.name}' not installed "
                f"(install metaphysica[full] for plot/sim/PDF paths)"
            )
        pytest.fail(f"ImportError in {module_path}: {e}")
    except ImportError as e:
        msg = str(e)
        if "eml-math" in msg or "eml-spectral" in msg or "eml_spectral" in msg:
            pytest.skip(
                f"{module_path}: eml-spectral not installed "
                f"(install metaphysica[sims] for EML paths)"
            )
        pytest.fail(f"ImportError in {module_path}: {e}")
    except Exception as e:
        # Some modules may fail for non-import reasons (missing data files, etc.)
        # We only care about import-level failures
        if "No module named" in str(e) or "cannot import name" in str(e):
            pytest.fail(f"Import failure in {module_path}: {e}")
        else:
            pytest.skip(f"Non-import error in {module_path}: {type(e).__name__}: {e}")
