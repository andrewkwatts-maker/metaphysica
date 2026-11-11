"""validation-data close-out XV-06: status wording built from the recorded status.

The oracle's ALP comment no longer names the retired 27D (M27) bulk, and the
distiller's integrity conclusion and overfitting text are worded from the MDL
status the analysis records (FAILS_AS_TALLIED) instead of claiming
"VERIFIED" and "the OPPOSITE of overfitting".
"""
import inspect
import json

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


# Review round: the status, the flags and every report string follow the
# MDL status computed from the tally.

def _stub(seed=40, code=3000, raw_per=32, n=50):
    raw = raw_per * n
    return {"with_theory_data_bits": seed, "theory_code_bits": code,
            "first_use_total_bits": seed + code, "without_theory_bits": raw,
            "data_compression_ratio": raw / seed, "first_use_ratio": raw / (seed + code),
            "status": ibd.seed_accounting_status(raw / seed)}


def test_report_json_has_no_overclaim(report):
    text = json.dumps(report, ensure_ascii=False)
    for phrase in ("M₂₇", "proves PM satisfies MDL", "MDL encoding", "achieves MDL",
                   "MDL achieved", "via MDL", "32,640"):
        assert phrase not in text, phrase


def test_status_and_flag_follow_the_mdl_status(report):
    res = report["results"]
    status = res["mdl_status"]
    assert status == res["code_theoretical_integrity"]["mdl_principle"]["mdl_status"]
    assert status == res["compression_ratio_analysis"]["mdl_status"]
    assert res["mdl_satisfied"] is ibd.mdl_holds(status)
    assert status in res["overall_status"]
    if status.startswith(ibd.MDL_FAILS):
        assert res["mdl_satisfied"] is False
        assert "MDL SATISFIED" not in json.dumps(report, ensure_ascii=False)


def test_mdl_status_is_computed_from_the_tally(report):
    comp = report["results"]["compression_ratio_analysis"]
    assert comp["first_use_total_bits"] > comp["without_theory_bits"]
    assert ibd.mdl_status_from_tally(comp).startswith(ibd.MDL_FAILS)
    assert ibd.mdl_status_from_tally(_stub(code=3000)).startswith(ibd.MDL_FAILS)
    assert "40-bit seed" in ibd.mdl_status_from_tally(_stub(code=3000))
    assert ibd.mdl_status_from_tally(_stub(code=500)) == ibd.MDL_HOLDS


def test_mdl_principle_quotes_the_computed_tally(report):
    comp = report["results"]["compression_ratio_analysis"]
    text = report["results"]["code_theoretical_integrity"]["mdl_principle"]["application_to_pm"]
    assert str(comp["first_use_total_bits"]) in text
    assert str(comp["without_theory_bits"]) in text
    stub = ibd.mdl_principle(_stub(code=500), 50)
    assert stub["mdl_status"] == ibd.MDL_HOLDS
    assert "540 bits" in stub["application_to_pm"] and "32 bits" in stub["application_to_pm"]


def test_integrity_conclusion_holds_branch_and_unknown_status():
    text = ibd.integrity_conclusion(ibd.MDL_HOLDS)
    assert "SUPPORTED AS TALLIED" in text and "NOT VERIFIED" not in text
    assert ibd.overall_status(ibd.MDL_HOLDS).startswith("MDL HOLDS AS TALLIED")
    with pytest.raises(ValueError):
        ibd.integrity_conclusion("SOMETHING_ELSE")
    with pytest.raises(ValueError):
        ibd.mdl_holds("SOMETHING_ELSE")


def test_interpretation_is_built_from_the_stub_bit_counts():
    for code in (3000, 500):
        stub = _stub(code=code)
        text = ibd.mdl_interpretation(stub, ibd.mdl_status_from_tally(stub), 50)
        joined = " ".join(text.values())
        assert "69-bit" not in joined and "64 bits each" not in joined
        assert "32 bits each" in joined and "40-bit seed" in joined
