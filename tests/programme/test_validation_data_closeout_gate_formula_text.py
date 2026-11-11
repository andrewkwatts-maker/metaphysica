"""L7 validation-data close-out XV-12: gate_summary's formula text quotes its computed counts."""
from metaphysica.generators import headline_stats as hs


def _certs(spec):
    return [{"gate_id": g, "evaluation_status": e, "verification_status": s}
            for g, e, s in spec]


def _registry():
    return _certs([("1", "COMPUTED_PASS", "VERIFIED"), ("2", "COMPUTED_PASS", "VERIFIED"),
                   ("3", "COMPUTED_FAIL", "VERIFIED"), ("4", None, "VERIFIED"),
                   ("5", None, "PENDING_LOCK"), ("6", None, "NOT_TESTABLE"),
                   ("7", "COMPUTED_PASS", "NOT_TESTABLE"),
                   ("8", "NOT_APPLICABLE", "VERIFIED")])


def test_gate_summary_formula_is_built_from_counts():
    s = hs.gate_summary(_registry())
    t = hs.tally_gates(_registry())
    executed = s["executed_pass"] + s["executed_fail"] - t["executed_axiom"]
    assert s["formula"] == (
        f"testable = total - axiom = {s['total']} - {s['axiom']} = {s['testable']}; "
        f"executed = executed_pass + executed_fail - executed_axiom = "
        f"{s['executed_pass']} + {s['executed_fail']} - {t['executed_axiom']} = {executed}; "
        f"declarative = testable - executed = {s['testable']} - {executed} = "
        f"{s['declarative']}")
    assert s["total"] - s["axiom"] == s["testable"]
    assert s["testable"] - executed == s["declarative"]


def test_gate_formula_follows_a_changed_registry():
    small = hs.gate_summary(_certs([("1", "COMPUTED_PASS", "VERIFIED"),
                                    ("2", None, "NOT_TESTABLE")]))
    assert small["formula"].startswith("testable = total - axiom = 2 - 1 = 1;")
    assert small["formula"].endswith("declarative = testable - executed = 1 - 1 = 0")
