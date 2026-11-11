"""validation-data close-out XV-06: status wording built from the recorded status.

The oracle's ALP comment no longer names the retired 27D (M27) bulk, and the
distiller's integrity conclusion and overfitting text are worded from the MDL
status the analysis records (FAILS_AS_TALLIED) instead of claiming
"VERIFIED" and "the OPPOSITE of overfitting".
"""
import inspect

import pytest

from metaphysica.simulations.PM.validation import (
    falsification_oracle as fo,
    information_bottleneck_distiller as ibd,
)


@pytest.fixture(scope="module")
def report():
    return ibd.InformationBottleneckDistiller().generate_report()


def test_oracle_alp_comment_names_no_retired_27d_bulk():
    src = inspect.getsource(fo.FalsificationOracle._load_predictions)
    assert "M27" not in src
    assert "M₂₇" not in src


def test_distiller_docstring_names_no_m27_bulk():
    assert "M₂₇ bulk phase space" not in ibd.__doc__


def test_integrity_conclusion_is_built_from_the_mdl_status(report):
    integrity = report["results"]["code_theoretical_integrity"]
    status = integrity["mdl_principle"]["mdl_status"]
    conclusion = integrity["overall_conclusion"]
    assert "Integrity VERIFIED" not in conclusion
    assert status in conclusion
    assert "NOT VERIFIED" in conclusion


def test_integrity_conclusion_rejects_a_missing_status():
    with pytest.raises(ValueError):
        ibd.integrity_conclusion("")


def test_interpretation_drops_the_overfitting_claims(report):
    status = report["results"]["code_theoretical_integrity"]["mdl_principle"]["mdl_status"]
    text = report["interpretation"]
    for key in ("key_insight", "mdl_justification", "peer_review_response"):
        assert "OPPOSITE of overfitting" not in text[key]
        assert "proves the framework is not overfitting" not in text[key]
        assert "M₂₇" not in text[key]
        assert status in text[key], key


def test_interpretation_quotes_the_computed_bits(report):
    comp = report["results"]["compression_ratio_analysis"]
    text = report["interpretation"]
    assert str(comp["first_use_total_bits"]) in text["mdl_justification"]
    assert str(comp["without_theory_bits"]) in text["mdl_justification"]
    assert f"{comp['first_use_ratio']:.2f}:1" in text["key_insight"]
