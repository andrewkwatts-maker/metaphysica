"""The summary printed "[FAIL] ... 0 FAILURES detected" when the cause was an
ERROR, and never named the simulation."""
from metaphysica.simulations.core.eml_cross_check import log_cross_check_summary


def test_summary_names_errors(capsys):
    report = {
        "summary": {"total_simulations": 1, "agreed": 0, "failed": 0,
                    "not_implemented": 0, "errors": 1,
                    "global_max_deviation": 0.0, "all_agree": False},
        "simulations": {"sim_x": {"status": "ERROR", "note": "boom"}},
        "failed_params": {},
    }
    log_cross_check_summary(report)
    out = capsys.readouterr().out
    assert "1 ERRORS" in out and "ERROR sim_x: boom" in out
