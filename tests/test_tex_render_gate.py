"""The build's render-gate step: skip only without the checker, fail early otherwise."""
from __future__ import annotations

import pytest

from metaphysica.generators import tex_render_gate as gate


def test_no_checker_is_a_skip(tmp_path):
    assert gate.main(tmp_path, tmp_path / "absent") == 0


def test_missing_node_or_modules_names_the_fix(tmp_path):
    assert "node" in gate.checker_problem(tmp_path, None)
    assert "npm ci" in gate.checker_problem(tmp_path, "node")
    (tmp_path / "node_modules" / "mathjax-full").mkdir(parents=True)
    assert gate.checker_problem(tmp_path, "node") is None


def test_missing_inputs_fail(tmp_path):
    with pytest.raises(FileNotFoundError, match="formulas.json"):
        gate.inputs(tmp_path)
