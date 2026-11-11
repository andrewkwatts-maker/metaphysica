"""XP-06: switch_search.search() delegates its ERRORED handling to a helper.

search() was 83 lines. The row-state partition (consistent, blocked only by
unevaluable checks, ERRORED) is _state_counts, the standing-versus-switched
split is _standing_and_switched; the report keys and their order are kept.
"""
import inspect

from metaphysica.simulations.core import switch_search as ss

KEY_ORDER = [
    "what_this_reports", "forks_searched", "n_combinations", "capped", "rows",
    "n_internally_consistent", "internally_consistent_digests",
    "n_blocked_only_by_unevaluable_checks",
    "blocked_only_by_unevaluable_digests", "n_errored", "errored_digests",
    "problems_no_combination_fixes", "problems_the_switches_control",
    "n_clean_on_every_switch_controlled_check",
    "clean_on_every_switch_controlled_check_digests",
    "why_those_are_separated", "why_that_second_count_exists", "ordering",
    "closure_would_look_like", "verdict",
]


def _row(digest, state, checks, consistent=False, blocked=False):
    return {"digest": digest, "state": state, "checks": checks,
            "internally_consistent": consistent,
            "blocked_only_by_unevaluable_checks": blocked}


def _stub_rows():
    standing = {"name": "standing", "ok": False}
    return [
        _row("d3", "ERRORED", [standing, {"name": "raised", "ok": False,
                                          "kind": "ERROR"}]),
        _row("d1", "CONSISTENT", [{"name": "raised", "ok": True}],
             consistent=True),
        _row("d2", "BLOCKED", [standing, {"name": "raised", "ok": True}],
             blocked=True),
    ]


def test_search_fits_the_size_rule():
    assert len(inspect.getsource(ss.search).splitlines()) <= 60


def test_state_counts_keep_errored_rows_apart():
    counts = ss._state_counts(_stub_rows())
    assert counts["n_errored"] == 1
    assert counts["errored_digests"] == ["d3"]
    assert counts["internally_consistent_digests"] == ["d1"]
    assert counts["blocked_only_by_unevaluable_digests"] == ["d2"]


def test_search_report_keys_and_errored_rows(monkeypatch):
    rows = _stub_rows()
    monkeypatch.setattr(ss, "combinations_for", lambda ids, cap: rows)
    monkeypatch.setattr(ss, "evaluate_combination", lambda row: row)
    report = ss.search(fork_ids=["f"], cap=64)
    assert list(report) == KEY_ORDER
    assert [r["digest"] for r in report["rows"]] == ["d1", "d2", "d3"]
    assert report["errored_digests"] == ["d3"]
    assert report["problems_no_combination_fixes"] == []
    assert report["problems_the_switches_control"] == ["raised", "standing"]
    assert report["verdict"] == ss.VERDICT
