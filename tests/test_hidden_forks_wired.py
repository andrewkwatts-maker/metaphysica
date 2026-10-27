"""H2: hidden chi_eff / n_gen choices read their fork (H07, H08, H12, H26).

Each case runs in a fresh interpreter so the registry singleton and the class
constants see the selection from the environment, as a variant build would.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

SRC = str(Path(__file__).resolve().parents[1] / "src")

PROBE = r"""
import json
from metaphysica.simulations.core.FormulasRegistry import get_registry
from metaphysica.simulations.PM.cosmology.dynamical_lambda import (
    DynamicalLambdaRelaxation as D)
from metaphysica.simulations.PM.algebra.gaugino_condensation import (
    _resolved_n_gen)
r = get_registry()
print(json.dumps({"total": r.chi_eff_total, "sector": r.chi_eff,
                  "chi": D.CHI_EFF, "nb": D.N_BRIDGES, "ngen": _resolved_n_gen()}))
"""


def _probe(**env_extra):
    env = dict(os.environ, PYTHONPATH=SRC, **env_extra)
    out = subprocess.run([sys.executable, "-c", PROBE], env=env, check=True,
                         capture_output=True, text=True).stdout
    return json.loads(out.strip().splitlines()[-1])


def test_default_values_unchanged():
    got = _probe()
    assert (got["total"], got["sector"], got["chi"], got["nb"], got["ngen"]) \
        == (144, 72, 144, 12, 3)


def test_chi_eff_follows_route_h07_h08_h12():
    got = _probe(METAPHYSICA_VARIANT_CHI_EFF_ROUTE="seed_dependent")
    assert got["total"] != 144 and got["sector"] != 72     # H07
    assert got["chi"] == got["total"]                      # H12
    assert got["nb"] == round(got["total"] / 12.0) != 12


def test_constant_route_keeps_144():
    got = _probe(METAPHYSICA_VARIANT_CHI_EFF_ROUTE="constant_144")
    assert got["total"] == 144


def test_n_gen_follows_source_h26():
    got = _probe(METAPHYSICA_VARIANT_N_GEN_SOURCE="b3_over_dim_O")
    assert got["ngen"] != 3
