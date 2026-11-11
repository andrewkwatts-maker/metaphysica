"""XB-04: the stale 137dd42 path ranking is no longer published.

The committed data/path_ranking.json predated the wave A ranking contract, so
"Publish the path ranking" raised. It now lives in docs/plan/programme/stale/;
the publish step skips with its logged line, and a present invalid file still
raises.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from metaphysica.generators import generate_path_ranking as gpr
from metaphysica.testground.rank import validate_ranking

REPO = Path(__file__).resolve().parents[2]
STALE = REPO / "docs" / "plan" / "programme" / "stale" / "path_ranking_137dd42.json"


def test_stale_ranking_is_not_in_package_data():
    assert not gpr.SOURCE.exists(), gpr.SOURCE


def test_stale_ranking_is_kept_and_fails_the_contract():
    assert STALE.is_file(), STALE
    problems = validate_ranking(json.loads(STALE.read_text(encoding="utf-8")))
    assert problems


def test_publish_skips_with_logged_line_when_absent(tmp_path, capsys):
    assert not gpr.SOURCE.exists()
    assert gpr.publish(gpr.SOURCE, tmp_path) is False
    assert "absent; skipped" in capsys.readouterr().out
    assert not (tmp_path / "path_ranking.json").exists()


def test_main_exits_zero_when_absent(capsys):
    # Fail early: with the file absent, main() writes nothing anywhere.
    assert not gpr.SOURCE.exists()
    assert gpr.main() == 0
    assert "absent; skipped" in capsys.readouterr().out


def test_present_invalid_file_raises(tmp_path):
    src = tmp_path / "path_ranking.json"
    shutil.copyfile(STALE, src)
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(ValueError, match="does not validate"):
        gpr.publish(src, out)
    assert not (out / "path_ranking.json").exists()
