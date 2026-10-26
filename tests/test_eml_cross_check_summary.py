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


def test_nothing_compared_is_not_agreement():
    """geometric_anchors scored AGREE with 0 values checked: its re-run
    returned {} because the registry already held every output."""
    import pytest
    from types import SimpleNamespace
    from metaphysica.simulations.core import eml_cross_check as x
    if not x.EML_AVAILABLE:
        pytest.skip("eml-math not installed")
    sim = SimpleNamespace(metadata=SimpleNamespace(id="sim_empty"),
                          run_eml=lambda registry: {})
    assert x.check_simulation(sim, None, {}).status == "SKIP"
    assert x.check_simulation(sim, None, {"_meta": 1}).status == "SKIP"
    sim.run_eml = lambda registry: {"a": 1.0}
    assert x.check_simulation(sim, None, {"a": 1.0}).status == "AGREE"


def test_delegating_run_eml_is_not_agreement():
    """102 of 118 run_eml methods were `return self.run(registry)`; they
    scored AGREE by comparing run() with itself."""
    from metaphysica.simulations.core import eml_cross_check as x

    class Meta:
        id = "sim_delegating"

    class Delegating:
        metadata = Meta()

        def run(self, registry):
            return {"a": 1.0}

        def run_eml(self, registry):
            """Docstrings do not count as a body."""
            return self.run(registry)

    class Independent(Delegating):
        def run_eml(self, registry):
            return {"a": 2.0 / 2.0}

    assert x.delegates_to_run(Delegating())
    assert not x.delegates_to_run(Independent())
    if x.EML_AVAILABLE:
        chk = x.check_simulation(Delegating(), None, {"a": 1.0})
        assert chk.status == "DELEGATED"
        assert x.check_simulation(Independent(), None, {"a": 1.0}).status == "AGREE"
    report = x.generate_cross_check_report(
        [x.SimulationCheck("s1", "DELEGATED"), x.SimulationCheck("s2", "AGREE")])
    assert report["summary"]["delegated"] == 1 and report["summary"]["agreed"] == 1
