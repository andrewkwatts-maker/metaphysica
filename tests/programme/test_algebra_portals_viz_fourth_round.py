"""L6 algebra-portals-viz round 4: shielding k is fitted without data, rows CALIBRATED, retired."""
from metaphysica.simulations.PM.consciousness import orch_or_pair_shielding as shield


def _defs():
    sim = [v for v in vars(shield).values()
           if isinstance(v, type) and hasattr(v, "get_output_param_definitions")
           and v.__module__ == shield.__name__][0]
    return {d.path: d for d in sim().get_output_param_definitions()}


def test_shielding_rows_with_fitted_k_are_calibrated():
    d = _defs()
    for path in ("consciousness.shielded_tau_ms", "consciousness.shielding_factor"):
        assert d[path].status == "CALIBRATED"


def test_shielding_retired_from_paper():
    assert shield.RETIRED_FROM_PAPER is True


def test_proton_decay_block_reads_b3_from_path():
    from metaphysica.simulations.PM.support import complete_residue_registry as r
    src = open(r.__file__, encoding="utf-8").read()
    assert "b3 = 24\n" not in src
    assert "b3 = active_b3()" in src
    assert "M_Planck = 1.22e19" not in src
