"""L7 validation-data close-out XV-01: the scored w_a row uses the loaded DESI error.

Review round: the certificate and validate_self score w_a with the same
loaded anchor as the row, the w0 rows read the w0 comparison CANON
registers, and get_output_param_definitions is 60 lines or fewer.
"""
import inspect

import pytest

from metaphysica.simulations.PM.cosmology.dark_energy import (
    DarkEnergyV16, MetadataBuilder, _REG, wa_from_b3)
from metaphysica.simulations.core.canonical_values import CANON
from metaphysica.simulations.data.experimental_data_loader import get_loader


def _row(path):
    rows = DarkEnergyV16().get_output_param_definitions()
    return next(r for r in rows if r.path == path)


def _wa_row():
    return _row("cosmology.wa_derived")


def _pred():
    return wa_from_b3(_REG.elder_kads)[0]


def test_wa_row_uncertainty_is_desi_error_toward_prediction():
    row = _wa_row()
    desi_wa = get_loader().get_desi("wa")
    assert row.experimental_bound == desi_wa.value
    assert row.uncertainty == desi_wa.uncertainty_toward(_pred())
    assert desi_wa.uncertainty_plus is not None  # DESI w_a is asymmetric


def test_wa_row_text_quotes_the_scored_sigma():
    row = _wa_row()
    assert (f"scored with the error on the side of the prediction, "
            f"{row.uncertainty}") in row.description
    assert "0.22" not in row.description


def test_certificate_scores_wa_like_the_row():
    row = _wa_row()
    cert = next(c for c in DarkEnergyV16().get_certificates()
                if c["id"] == "CERT_WA_DESI_EVOLUTION")
    dev = MetadataBuilder.compute_sigma(_pred(), row.experimental_bound,
                                        row.uncertainty)
    assert float(cert["wolfram_result"]) == pytest.approx(dev, abs=1e-4)
    assert f"/ {row.uncertainty}" in cert["condition"]
    assert "0.22" not in cert["assertion"]


def test_validate_self_scores_wa_like_the_row():
    row = _wa_row()
    check = next(c for c in DarkEnergyV16().validate_self()["checks"]
                 if c["name"].startswith("wa deviation"))
    dev = MetadataBuilder.compute_sigma(_pred(), row.experimental_bound,
                                        row.uncertainty)
    assert check["confidence_interval"]["sigma"] == pytest.approx(dev, rel=1e-12)
    assert check["confidence_interval"]["upper"] == pytest.approx(
        row.experimental_bound + 3 * row.uncertainty, rel=1e-12)


def test_w0_rows_read_the_canon_comparison():
    comparison = CANON["w0"]["comparison"]
    row = _row("cosmology.w0_derived")
    assert row.experimental_bound == comparison["exp"]
    assert row.uncertainty == comparison["unc"]


def test_no_typed_wa_anchor_in_the_class():
    src = inspect.getsource(DarkEnergyV16)
    assert "-0.86 +/- 0.22" not in src
    assert "desi_wa_sigma = 0.22" not in src


def test_output_param_definitions_is_60_lines_or_fewer():
    for fn in (DarkEnergyV16.get_output_param_definitions,
               DarkEnergyV16.get_certificates, DarkEnergyV16.validate_self):
        assert len(inspect.getsource(fn).splitlines()) <= 60, fn.__name__
