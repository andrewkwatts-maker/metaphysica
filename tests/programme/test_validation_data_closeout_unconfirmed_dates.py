"""validation-data close-out XV-07: the BabyIAXO 2025 first-results year is
labelled unconfirmed.

The oracle used to list BabyIAXO as "Commissioning phase" with first results
in 2025 and the kill-switch text as "BabyIAXO (2025)", a year now past with no
cited source. Each place that quotes the year now carries
``source_unverified`` or says the year is unconfirmed, and the quoted years
are read from the limits table.
"""
import pytest

from metaphysica.simulations.PM.validation import falsification_oracle as fo


@pytest.fixture(scope="module")
def oracle():
    """Oracle with the real limits and timeline tables (no registry read)."""
    o = fo.FalsificationOracle.__new__(fo.FalsificationOracle)
    o.exclusion_thresholds = o._load_experimental_limits()
    o.experimental_timeline = o._load_timeline()
    return o


def test_limits_entry_carries_source_unverified(oracle):
    entry = oracle.exclusion_thresholds["BabyIAXO_2025"]
    assert entry.get("source_unverified")
    assert "unconfirmed" in entry["status"]
    assert "Commissioning" not in entry["status"]


def test_timeline_entry_carries_source_unverified(oracle):
    rows = [r for r in oracle.experimental_timeline if r["experiment"] == "BabyIAXO"]
    assert len(rows) == 1
    assert rows[0].get("source_unverified")
    assert "unconfirmed" in rows[0]["test"]


def test_kill_switch_text_says_unconfirmed(oracle):
    year = oracle.exclusion_thresholds["BabyIAXO_2025"]["first_results_expected"]
    iaxo = oracle.exclusion_thresholds["IAXO_2028"]["first_results_expected"]
    exp = oracle._get_primary_experiment("ALP_Principia_Metric")
    span = oracle._get_test_timeline("ALP_Principia_Metric")
    for text in (exp, span):
        assert "unconfirmed" in text
        assert str(year) in text and str(iaxo) in text
    assert "BabyIAXO (2025) /" not in exp


def test_missing_planned_year_raises(oracle):
    o = fo.FalsificationOracle.__new__(fo.FalsificationOracle)
    o.exclusion_thresholds = {"IAXO_2028": oracle.exclusion_thresholds["IAXO_2028"]}
    with pytest.raises(KeyError):
        o._get_primary_experiment("ALP_Principia_Metric")


def test_timeline_years_are_read_from_the_limits_table(oracle):
    limits = oracle.exclusion_thresholds
    keys = {"BabyIAXO": "BabyIAXO_2025", "ALPS-II": "ALPS_II_2026",
            "Hyper-K": "Hyper_K_2027", "IAXO": "IAXO_2028",
            "DUNE": "DUNE_2028", "HL-LHC": "HL_LHC_2029"}
    for row in oracle.experimental_timeline:
        assert row["year"] == limits[keys[row["experiment"]]]["first_results_expected"]


def test_timeline_follows_a_changed_planned_year(oracle):
    o = fo.FalsificationOracle.__new__(fo.FalsificationOracle)
    o.exclusion_thresholds = {k: dict(v) for k, v in oracle.exclusion_thresholds.items()}
    o.exclusion_thresholds["BabyIAXO_2025"]["first_results_expected"] = 2031
    o.exclusion_thresholds["IAXO_2028"]["first_results_expected"] = 2034
    years = {r["experiment"]: r["year"] for r in o._load_timeline()}
    assert (years["BabyIAXO"], years["IAXO"]) == o._alp_planned_years() == (2031, 2034)


def test_alps_ii_status_is_labelled_unconfirmed(oracle):
    entry = oracle.exclusion_thresholds["ALPS_II_2026"]
    assert entry.get("source_unverified")
    rows = [r for r in oracle.experimental_timeline if r["experiment"] == "ALPS-II"]
    assert len(rows) == 1 and rows[0].get("source_unverified")
