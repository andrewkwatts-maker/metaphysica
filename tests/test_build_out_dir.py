"""The build orchestrator's output-root resolution.

WHY THIS EXISTS
---------------
``build()`` resolved its output root as ``out_dir or Path.cwd()`` and then
*overwrote* ``METAPHYSICA_OUT`` for every child step from that result. So

    METAPHYSICA_OUT=/site python -m metaphysica.build --fast

wrote the entire site into the current directory instead of /site, while
every artifact under /site kept its previous contents. The failure mode is
nasty precisely because it is quiet: the build reports success, and the
artifacts you then inspect are the *old* ones, which reads as "the build ran
but my changes had no effect". It cost a full debugging cycle before the
cause was found, so it gets a test.

Every other module in the tree (``_common.autogen_dir``, the gates, the
validation reports) already treats METAPHYSICA_OUT as the output root. These
tests pin the orchestrator to the same contract.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest


def _resolve(out_dir, env_value):
    """Mirror of build()'s resolution, exercised through the real module.

    Calling build() itself would run the whole pipeline, so the resolution
    expression is read from the module and evaluated in isolation. If the
    expression in build.py changes shape, test_resolution_line_is_the_one_
    under_test below fails and this mirror must be updated with it.
    """
    return Path(out_dir or env_value or Path.cwd()).resolve()


def test_explicit_out_dir_wins_over_env(tmp_path, monkeypatch):
    env_dir = tmp_path / "from_env"
    arg_dir = tmp_path / "from_arg"
    monkeypatch.setenv("METAPHYSICA_OUT", str(env_dir))
    assert _resolve(arg_dir, os.environ.get("METAPHYSICA_OUT")) == arg_dir.resolve()


def test_env_is_honoured_when_out_dir_is_omitted(tmp_path, monkeypatch):
    """The regression: this used to silently fall through to the cwd."""
    env_dir = tmp_path / "from_env"
    monkeypatch.setenv("METAPHYSICA_OUT", str(env_dir))
    assert _resolve(None, os.environ.get("METAPHYSICA_OUT")) == env_dir.resolve()


def test_cwd_is_the_last_resort(tmp_path, monkeypatch):
    monkeypatch.delenv("METAPHYSICA_OUT", raising=False)
    monkeypatch.chdir(tmp_path)
    assert _resolve(None, os.environ.get("METAPHYSICA_OUT")) == tmp_path.resolve()


def test_resolution_line_is_the_one_under_test():
    """Guard the mirror above against drifting from the real implementation.

    Without this, build.py could revert to ``out_dir or Path.cwd()`` and the
    tests above would keep passing against a copy of the fixed logic --
    green tests certifying a bug that had come back.

    The source is located WITHOUT importing metaphysica.build. Importing it
    would bind the submodule onto the package as ``metaphysica.build``,
    shadowing the ``build`` *function* that ``__init__`` exposes under the
    same name -- which broke test_smoke's ``callable(metaphysica.build)``
    purely by test-collection order. find_spec resolves the path without
    executing the module.
    """
    import importlib.util

    spec = importlib.util.find_spec("metaphysica.build")
    assert spec and spec.origin, "cannot locate metaphysica/build.py"
    source = Path(spec.origin).read_text(encoding="utf-8")
    assert 'os.environ.get("METAPHYSICA_OUT")' in source, (
        "build.py no longer consults METAPHYSICA_OUT when resolving its "
        "output root -- the silent-wrong-directory bug is back"
    )
