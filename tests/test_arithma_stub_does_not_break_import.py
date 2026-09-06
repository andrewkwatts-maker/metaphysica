"""A non-functional arithma must degrade, not break the package.

WHAT THIS CAUGHT
----------------
CI went from green to four collection errors with this, on every module that
touches the triple-track:

    src/metaphysica/simulations/PM/particle/neutrino_mixing.py:181
        return _A.Expression.number(float(v))
    AttributeError: 'NoneType' object has no attribute 'number'

and then, downstream of it:

    ImportError: cannot import name 'simulations' from 'metaphysica'

Fifty-three modules guard the backend as `try: import arithma as _A / except
ImportError: _A = None`. That catches a MISSING package. It does not catch a
package that imports and does not work -- and arithma's own fallback binds
`Expression` to None when its compiled extension fails to load, so
`import arithma` succeeds and every use of it explodes.

It was made reachable by declaring arithma a hard dependency, which caused CI
to install exactly such a build. arithma is now an extra, because every call
site is written to degrade without it.

The same blind spot had already been visible in the artifacts:
`arithma_available: true` alongside 422 formulas none of which carried an
arithma tree. Importable is not usable, and only one of those is worth
reporting.
"""
from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]

_STUB = '''
__version__ = "0.0.0-stub"
Expression = None
Integer = None
Variable = None
'''


def _run_with_stub(body: str, tmp_path) -> subprocess.CompletedProcess:
    """Run *body* in a subprocess where `import arithma` yields a stub."""
    stub_dir = tmp_path / "stub" / "arithma"
    stub_dir.mkdir(parents=True)
    (stub_dir / "__init__.py").write_text(_STUB, encoding="utf-8")
    script = tmp_path / "probe.py"
    script.write_text(textwrap.dedent(body), encoding="utf-8")
    env = {
        "PYTHONPATH": str(tmp_path / "stub"),
        "PYTHONIOENCODING": "utf-8",
        "PATH": "/usr/bin:/bin",
        "SYSTEMROOT": "C:\\\\Windows",
    }
    return subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, cwd=str(_ROOT), env=env, timeout=300,
    )


def test_the_backend_reports_a_stub_as_unusable(tmp_path):
    result = _run_with_stub(
        """
        from metaphysica.simulations.core.arithma_backend import (
            ARITHMA, ARITHMA_UNAVAILABLE_REASON,
        )
        assert ARITHMA is None, "a stub arithma was reported as usable"
        assert ARITHMA_UNAVAILABLE_REASON, "no reason was recorded"
        print("OK", ARITHMA_UNAVAILABLE_REASON[:60])
        """,
        tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_the_simulations_package_still_imports_under_a_stub(tmp_path):
    """This is the exact CI failure: the package became unimportable."""
    result = _run_with_stub(
        """
        import metaphysica.simulations  # noqa: F401
        print("OK")
        """,
        tmp_path,
    )
    assert result.returncode == 0, (
        "metaphysica.simulations cannot be imported when arithma is a stub. "
        "That is the failure this test exists for -- an optional backend "
        "must degrade, not take the package down:\n"
        + result.stdout + result.stderr
    )


def test_neutrino_mixing_imports_under_a_stub(tmp_path):
    """The module whose import-time assert crashed first."""
    result = _run_with_stub(
        """
        from metaphysica.simulations.PM.particle import neutrino_mixing  # noqa: F401
        print("OK")
        """,
        tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_arithma_is_not_a_hard_dependency():
    """Declaring it is what let a stub reach the import path."""
    text = (_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    head, _, tail = text.partition("[project.optional-dependencies]")
    assert "arithma" not in head.split("dependencies = [")[-1].split("]")[0], (
        "arithma is back in the required dependencies. Every call site is "
        "written to degrade without it, and requiring it made CI install a "
        "build whose extension does not load."
    )
    assert "arithma" in tail, "arithma should still be offered as an extra"
