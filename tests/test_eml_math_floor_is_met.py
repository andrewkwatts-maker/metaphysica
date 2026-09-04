"""The installed eml-math must satisfy the floor pyproject declares.

WHY THIS EXISTS
---------------
CI went red on every Python in the matrix, failing in about 21 seconds --
too fast to be a test failure. The cause was dependency resolution:
``pyproject.toml`` pins ``eml-math>=2.4.0`` while the latest version on PyPI
is 2.3.0, so ``pip install .[dev,sims]`` could not resolve at all.

The pin is CORRECT and must not be relaxed. The three commits after 2.3.0
add bare-name context resolution, variadic ``mul``/``add`` with a tolerated
annotated expression tail, and ``eml_vec`` resolving like a bare name. The
EML cross-check's agreeing rows depend on all three; pyproject's own comment
records that against 2.3 the operators raise ``AttributeError`` and every
affected parameter is scored unevaluable. Dropping the floor to a published
version would not fix anything -- it would break the thing the floor exists
to protect, and it would do so QUIETLY, as a drift in the unevaluable count
rather than as an error.

Locally the requirement is met because ``eml_math`` resolves to the source
checkout at 2.4.0, which shadows the older wheel from PyPI. CI has no such
checkout, so it now installs eml-math from its public git repository before
installing this package; pip then sees the requirement already satisfied.
That keeps the PUBLISHED metadata honest -- pyproject still states what the
code actually needs -- while letting the matrix run.

This test guards the divergence between the two environments: if the floor
is ever raised past what is actually installed, it fails loudly here instead
of showing up as a mysterious drop in EML agreement.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]


def _declared_floor() -> str | None:
    text = (_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'"eml-math>=([0-9][^"]*)"', text)
    return match.group(1) if match else None


def _as_tuple(version: str):
    parts = []
    for chunk in version.split("."):
        digits = "".join(c for c in chunk if c.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def test_pyproject_declares_a_floor():
    floor = _declared_floor()
    assert floor, "the eml-math pin has disappeared from pyproject.toml"


def test_the_installed_eml_math_meets_the_floor():
    """A shortfall degrades silently into unevaluable rows, not an error."""
    floor = _declared_floor()
    if floor is None:
        pytest.skip("no eml-math pin found")
    try:
        import eml_math
    except ImportError:
        pytest.skip("eml-math is not installed in this environment")

    installed = getattr(eml_math, "__version__", None)
    assert installed, "eml_math exposes no __version__ to check against"
    assert _as_tuple(installed) >= _as_tuple(floor), (
        f"pyproject requires eml-math>={floor} but {installed} is installed. "
        f"The operators added after 2.3.0 raise AttributeError on older "
        f"versions, and every affected parameter is then scored UNEVALUABLE "
        f"rather than raising -- so this shows up as a drift in the EML "
        f"counts, not as a failure. Install the newer eml-math; do not "
        f"lower the floor."
    )


def test_the_features_the_floor_exists_for_actually_work():
    """Check the capability, not the version string.

    A version number can be bumped without the features landing, so this
    evaluates each of the additions the floor was raised for. An earlier
    draft asserted ``hasattr(eml_math.ops, ...)``; there is no top-level
    ``ops`` module -- the operators live inside expression strings handed to
    EMLEvaluator -- so that test skipped on ImportError and checked nothing.
    """
    try:
        from eml_math.evaluator import EMLEvaluator
    except ImportError:
        pytest.skip("eml-math is not installed in this environment")

    evaluator = EMLEvaluator({"b3": 24.0})
    cases = {
        # variadic mul/add (3015502)
        "EML: ops.mul(eml_scalar(2.0), eml_scalar(3.0), eml_scalar(4.0))": 24.0,
        # evaluation context exposed as bare names (4a4d759)
        "EML: ops.add(b3, eml_scalar(1.0))": 25.0,
        # eml_vec resolves like a bare name (a4c4781)
        "EML: ops.add(eml_vec('b3'), eml_scalar(1.0))": 25.0,
        # an annotated tail after the expression is tolerated (3015502)
        "EML: ops.add(b3, eml_scalar(1.0)) — trailing description": 25.0,
        # operators named in the pyproject comment
        "EML: ops.log10(eml_scalar(100.0))": 2.0,
    }
    for expression, expected in cases.items():
        try:
            result = evaluator.eval(expression)
        except Exception as exc:  # noqa: BLE001 - any failure is the finding
            pytest.fail(
                f"{type(exc).__name__} on {expression!r}: {exc}. The floor "
                f"was raised to 2.4.0 for exactly this; on an older "
                f"eml-math every expression using it is scored UNEVALUABLE "
                f"rather than raising, so the damage is silent."
            )
        assert result == pytest.approx(expected), (
            f"{expression!r} gave {result}, expected {expected}"
        )


def test_ci_installs_eml_math_from_source_while_the_floor_is_unpublished():
    """The workflow must not silently go back to a PyPI-only install.

    If it does, and the floor still exceeds the newest published version,
    every job in the matrix fails at dependency resolution before a single
    test runs.
    """
    workflow = _ROOT / ".github" / "workflows" / "ci.yml"
    if not workflow.is_file():
        pytest.skip("no CI workflow present")
    text = workflow.read_text(encoding="utf-8")
    assert "EML-Math.git" in text, (
        "ci.yml no longer installs eml-math from source. That is correct "
        "ONLY once the pinned version is published to PyPI -- otherwise the "
        "whole matrix fails to resolve dependencies in ~20 seconds."
    )
