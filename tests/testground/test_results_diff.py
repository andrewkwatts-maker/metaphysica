"""RFC 6902 diff and apply: round trips, escaping, arrays, nested add/remove."""
import pytest

from metaphysica.testground.results.diff import (apply_patch, diff, escape,
                                                 unescape)


def roundtrip(a, b):
    ops = diff(a, b)
    assert apply_patch(a, ops) == b
    assert {o["op"] for o in ops} <= {"add", "remove", "replace"}
    return ops


def test_equal_documents_have_no_ops():
    assert diff({"a": [1, {"b": 2}]}, {"a": [1, {"b": 2}]}) == []


def test_pointer_escaping():
    a = {"a/b": {"c~d": 1}}
    b = {"a/b": {"c~d": 2}}
    ops = roundtrip(a, b)
    assert ops == [{"op": "replace", "path": "/a~1b/c~0d", "value": 2}]
    assert unescape(escape("~/x")) == "~/x"


def test_array_length_change_replaces_whole_array():
    ops = roundtrip({"x": [1, 2, 3]}, {"x": [1, 2]})
    assert ops == [{"op": "replace", "path": "/x", "value": [1, 2]}]


def test_array_same_length_is_diffed_per_index():
    ops = roundtrip({"x": [1, {"y": 1}, 3]}, {"x": [1, {"y": 2}, 3]})
    assert [o["path"] for o in ops] == ["/x/1/y"]


def test_nested_adds_and_removes():
    a = {"p": {"q": {"old": 1, "keep": 2}}}
    b = {"p": {"q": {"keep": 2, "new": {"deep": [1]}}}}
    ops = roundtrip(a, b)
    assert {o["op"] for o in ops} == {"add", "remove"}


def test_exact_equality_no_type_coercion():
    assert diff({"v": 1}, {"v": 1.0}) != []
    assert diff({"v": True}, {"v": 1}) != []
    assert diff({"v": 0.1 + 0.2}, {"v": 0.3}) != []
    assert diff({"v": float("nan")}, {"v": float("nan")}) == []


def test_type_change_and_root_replace():
    roundtrip({"v": {"a": 1}}, {"v": [1]})
    roundtrip([1], {"a": 1})


def test_apply_does_not_mutate_and_rejects_bad_ops():
    a = {"x": 1}
    apply_patch(a, [{"op": "replace", "path": "/x", "value": 2}])
    assert a == {"x": 1}
    with pytest.raises(KeyError):
        apply_patch(a, [{"op": "remove", "path": "/missing"}])
    with pytest.raises(KeyError):
        apply_patch(a, [{"op": "move", "path": "/x"}])
