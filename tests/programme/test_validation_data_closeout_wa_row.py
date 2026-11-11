"""L7 validation-data close-out XV-01: the scored w_a row uses the loaded DESI error."""
from metaphysica.simulations.PM.cosmology.dark_energy import (
    DarkEnergyV16, _REG, wa_from_b3)
from metaphysica.simulations.data.experimental_data_loader import get_loader


def _wa_row():
    rows = DarkEnergyV16().get_output_param_definitions()
    return next(r for r in rows if r.path == "cosmology.wa_derived")


def test_wa_row_uncertainty_is_desi_error_toward_prediction():
    row = _wa_row()
    desi_wa = get_loader().get_desi("wa")
    pred, _ = wa_from_b3(_REG.elder_kads)
    assert row.experimental_bound == desi_wa.value
    assert row.uncertainty == desi_wa.uncertainty_toward(pred)
    assert desi_wa.uncertainty_plus is not None  # DESI w_a is asymmetric


def test_wa_row_text_quotes_the_scored_sigma():
    row = _wa_row()
    assert f"{row.uncertainty}" in row.description
    assert "0.22" not in row.description
