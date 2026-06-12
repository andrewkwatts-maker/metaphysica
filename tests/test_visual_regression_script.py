"""Smoke tests for ``scripts/visual_regression.py``.

The full screenshot pipeline pulls in playwright + chromium and a live HTTP
server, neither of which we want in the default test suite. These tests
verify only that:

* the script module imports without optional deps installed,
* its CLI parser builds and ``--help`` exits cleanly,
* subcommands are wired up.

Real screenshot capture / diff is exercised manually as part of the
v2.1.0-publish flow (see TIER_2_3_ROADMAP §T4.5).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "visual_regression.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("visual_regression", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_file_exists():
    assert SCRIPT_PATH.is_file(), f"Missing: {SCRIPT_PATH}"


def test_script_imports_cleanly():
    """Module must import even when playwright / Pillow are missing."""
    mod = _load_script_module()
    # Public surface
    assert hasattr(mod, "capture")
    assert hasattr(mod, "diff")
    assert hasattr(mod, "main")
    assert callable(mod.capture)
    assert callable(mod.diff)
    assert callable(mod.main)


def test_cli_help_exits_zero(capsys):
    """``--help`` should print usage and exit 0 without touching the optional deps."""
    mod = _load_script_module()
    with pytest.raises(SystemExit) as exc:
        mod.main(["--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "visual_regression" in captured.out
    assert "capture" in captured.out
    assert "diff" in captured.out


def test_capture_subcommand_requires_root_and_out():
    """``capture`` must declare --root and --out as required args."""
    mod = _load_script_module()
    with pytest.raises(SystemExit):
        mod.main(["capture"])  # missing required args -> argparse exits 2


def test_diff_subcommand_requires_baseline_and_candidate():
    mod = _load_script_module()
    with pytest.raises(SystemExit):
        mod.main(["diff"])  # missing required args -> argparse exits 2


def test_missing_mode_errors():
    mod = _load_script_module()
    with pytest.raises(SystemExit):
        mod.main([])  # subparser is required


def test_default_constants_are_sane():
    mod = _load_script_module()
    assert mod.DEFAULT_READY_TIMEOUT_MS >= 1000
    assert mod.DEFAULT_VIEWPORT[0] >= 800
    assert mod.DEFAULT_VIEWPORT[1] >= 600
    assert isinstance(mod.DEFAULT_READY_EVENT, str) and mod.DEFAULT_READY_EVENT


def test_iter_pages_raises_for_missing_root(tmp_path):
    mod = _load_script_module()
    with pytest.raises(FileNotFoundError):
        list(mod._iter_pages(tmp_path))


def test_iter_pages_returns_sorted(tmp_path):
    mod = _load_script_module()
    pages_dir = tmp_path / "Pages"
    pages_dir.mkdir()
    for name in ("zeta.html", "alpha.html", "mu.html"):
        (pages_dir / name).write_text("<html></html>", encoding="utf-8")
    found = [p.name for p in mod._iter_pages(tmp_path)]
    assert found == ["alpha.html", "mu.html", "zeta.html"]


def teardown_module(module):
    # Don't pollute sys.modules for later tests.
    sys.modules.pop("visual_regression", None)
