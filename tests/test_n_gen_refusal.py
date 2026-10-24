"""Incoherent seed / n_gen_source pairings are refused with a reason, never a crash."""
import pytest

from metaphysica.simulations.PM.geometry.b3_path import (
    require_three_generations,
)


@pytest.mark.parametrize("seed", ["seed_7_joyce", "seed_19_joyce",
                                  "seed_31_joyce"])
def test_unreachable_n_gen_is_refused_with_a_reason(seed):
    with pytest.raises(ValueError, match="which is not three"):
        require_three_generations(seed)


def test_adopted_path_gives_three():
    assert require_three_generations() == 3


def test_octonionic_mixing_import_is_refused_not_a_crash(monkeypatch):
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_7_joyce")
    import subprocess
    import sys
    out = subprocess.run(
        [sys.executable, "-c",
         "import metaphysica.simulations.PM.particle.octonionic_mixing"],
        capture_output=True, text=True)
    assert out.returncode != 0
    last = out.stderr.strip().splitlines()[-1]
    assert last.startswith("ValueError:") and "not three" in last
