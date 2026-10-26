"""The superseded scanner's context-word list must not grow.

A sentence escapes the scan when it contains a word from ``_RETIRED``. Adding a
word to that list is therefore the cheapest way to make stale wording pass, so
the pattern is pinned by hash. A deliberate change must update the hash here in
the same commit and say why in the commit message.
"""
import hashlib

from metaphysica.generators import superseded_scan

PINNED_SHA256 = "bba72cc358b83ce7e34f786a4d5b8e546fe7466e38832770e25afebd40cd951b"


def test_retired_pattern_is_unchanged():
    got = hashlib.sha256(superseded_scan._RETIRED.pattern.encode()).hexdigest()
    assert got == PINNED_SHA256, "superseded_scan._RETIRED changed; see this test's docstring"
