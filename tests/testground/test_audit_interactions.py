"""audit.interactions: footprints, interaction sets, prediction, non_additive."""
import pytest

from metaphysica.testground.audit import footprints, interaction_sets, non_additive, predict

BASE = {"x": 1, "y": 1}
A = {"x": 2, "y": 1}
B = {"x": 1, "y": 3}
S2 = {("fa", "a"): A, ("fb", "b"): B}
SEL2 = {"fa": "a", "fb": "b"}


def test_independent_options_combine():
    assert non_additive(BASE, S2, SEL2, {"x": 2, "y": 3}) == []


def test_a_value_neither_option_gives_is_flagged():
    assert non_additive(BASE, S2, SEL2, {"x": 5, "y": 3}) == ["x"]


def test_a_joint_that_drops_both_changes_is_flagged():
    assert non_additive(BASE, S2, SEL2, {"x": 1, "y": 1}) == ["x", "y"]


def test_both_options_move_a_row_and_the_joint_takes_neither():
    singles = {("fa", "a"): {"x": 2}, ("fb", "b"): {"x": 3}}
    assert non_additive(BASE, singles, SEL2, {"x": 2.5}) == ["x"]


def test_a_row_only_the_joint_has_is_flagged():
    assert non_additive(BASE, S2, SEL2, {"x": 2, "y": 3, "z": 0}) == ["z"]


def test_predict_precedence_and_baseline():
    singles = {("fa", "a"): {"x": 2, "y": 1}, ("fb", "b"): {"x": 3, "y": 9}}
    p = predict(BASE, singles, SEL2)
    assert p == {"x": frozenset({2, 3}), "y": frozenset({9})}
    assert predict(BASE, singles, {"fa": "a"})["y"] == frozenset({1})
    assert predict(BASE, singles, {"fa": "nope"}) == {"x": frozenset({1}), "y": frozenset({1})}


def test_predict_freezes_unhashable_values():
    assert predict({"v": [1, 2]}, {}, {}) == {"v": frozenset({(1, 2)})}


def test_three_way_interaction_that_pairs_alone_do_not_flag():
    # Three options all move r. A pair allows only its own two values, so value 3
    # is flagged for (a, b) but accepted for the triple: the third mover is only
    # visible when the whole selection is predicted.
    base = {"r": 0}
    singles = {("a", "1"): {"r": 1}, ("b", "1"): {"r": 2}, ("c", "1"): {"r": 3}}
    sel = {"a": "1", "b": "1", "c": "1"}
    assert predict(base, singles, sel)["r"] == frozenset({1, 2, 3})
    pair = {"a": "1", "b": "1"}
    assert predict(base, singles, pair)["r"] == frozenset({1, 2})
    assert non_additive(base, singles, pair, {"r": 3}) == ["r"]
    assert non_additive(base, singles, sel, {"r": 3}) == []
    assert non_additive(base, singles, sel, {"r": 4}) == ["r"]


def test_interaction_sets_pairs_and_triples_are_sorted_and_cross_fork():
    fp = footprints(BASE, {("a", "1"): {"x": 2, "y": 1}, ("a", "2"): {"x": 3, "y": 1},
                           ("b", "1"): {"x": 5, "y": 1}, ("c", "1"): {"x": 7, "y": 1},
                           ("d", "1"): {"x": 1, "y": 4}})
    sets = interaction_sets(fp)
    assert (("a", "1"), ("a", "2")) not in sets
    assert sets[0] == (("a", "1"), ("b", "1"))
    assert (("a", "1"), ("b", "1"), ("c", "1")) in sets
    assert all(len({o[0] for o in s}) == len(s) for s in sets)
    assert not any(("d", "1") in s for s in sets)
    assert sets == interaction_sets(fp)
    assert all(len(s) == 2 for s in interaction_sets(fp, k_max=2))


def test_compatible_filters_sets():
    fp = {("a", "1"): frozenset("x"), ("b", "1"): frozenset("x")}
    assert interaction_sets(fp, compatible=lambda sel: False) == []


def test_limit_and_k_max_errors():
    fp = {(f, "1"): frozenset("x") for f in "abcde"}
    with pytest.raises(ValueError, match="exceed limit 3"):
        interaction_sets(fp, limit=3)
    for k in (1, 5):
        with pytest.raises(AssertionError):
            interaction_sets(fp, k_max=k)
