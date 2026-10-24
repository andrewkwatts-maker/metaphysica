"""Volatile key detection (pointer patterns, ``*`` for indices) and masking."""
from metaphysica.testground.results.volatile import detect, mask


A = {"generated_at": "t1", "v": 1,
     "rows": [{"ts": 1, "x": 5}, {"ts": 2, "x": 6}],
     "meta": {"run": "a", "same": 1}}
B = {"generated_at": "t2", "v": 1,
     "rows": [{"ts": 9, "x": 5}, {"ts": 8, "x": 6}],
     "meta": {"run": "b", "same": 1}}


def test_detect_patterns():
    assert detect(A, B) == {"/generated_at", "/rows/*/ts", "/meta/run"}
    assert detect(A, A) == set()


def test_mask_makes_twins_equal_and_keeps_the_rest():
    pats = detect(A, B)
    assert mask(A, pats) == mask(B, pats)
    assert mask(A, pats) == {"v": 1, "rows": [{"x": 5}, {"x": 6}],
                             "meta": {"same": 1}}
    assert A["generated_at"] == "t1"        # input untouched


def test_added_key_and_differing_array_are_volatile():
    a, b = {"k": 1, "l": [1]}, {"k": 1, "l": [1, 2], "n": 0}
    assert detect(a, b) == {"/n", "/l"}


def test_scalar_array_items_are_nulled():
    pats = detect({"l": [1, 2]}, {"l": [1, 3]})
    assert pats == {"/l/*"}
    assert mask({"l": [1, 2]}, pats) == {"l": [None, None]}


def test_pointer_escaping_in_patterns():
    pats = detect({"a/b": 1}, {"a/b": 2})
    assert pats == {"/a~1b"}
    assert mask({"a/b": 1, "c": 1}, pats) == {"c": 1}
