"""neutrino_algebraic.run_eml caught every exception and returned run(),
so a broken EML path scored AGREE in the cross-check. Only ImportError may
fall back."""
import pytest


class _Registry:
    def get_param(self, path):
        # Fixture values from the path readers of the path in force, not typed.
        from metaphysica.simulations.core.active_path import topology
        from metaphysica.simulations.core.canonical_values import canon
        topo = topology()
        return {"topology.elder_kads": topo.b3, "topology.mephorash_chi": topo.chi_eff,
                "topology.n_gen": topo.n_gen,
                "geometry.alpha_leak": canon()["alpha_leak"]["value"]}.get(path)

    def has_param(self, path):
        return False

    def set_param(self, *a, **k):
        pass


def test_eml_error_surfaces(monkeypatch):
    pytest.importorskip("eml_math")
    from metaphysica.simulations.core import eml_integration
    from metaphysica.simulations.PM.algebra.neutrino_algebraic import (
        NeutrinoAlgebraicSimulation,
    )

    def broken(*a, **k):
        raise RuntimeError("broken EML op")

    monkeypatch.setattr(eml_integration, "eml_sqrt", broken)
    with pytest.raises(RuntimeError, match="broken EML op"):
        NeutrinoAlgebraicSimulation().run_eml(_Registry())
