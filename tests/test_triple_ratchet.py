"""Ratchet: formulas not triple-checked must be explicit, and may only fall.

A published formula is checked when its ``triple_status`` is OK (Arithma tree,
EML tree and float agree) or RULED_DIVERGENCE (disagreement on record). One
with no number to check says so through ``non_numeric`` (a reason string).
Everything else is unchecked, and the count is pinned: converting a formula
lowers it, and the pin is lowered with it. It never rises.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
from collections import Counter

import pytest

from metaphysica.generators._common import autogen_dir
from metaphysica.simulations.core.arithma_backend import is_usable

#: Without a usable Arithma backend (PyPI arithma 2.0.2 is a stub) every
#: formula is EML_ONLY, so the count measures the install, not the formulas.
pytestmark = pytest.mark.skipif(not is_usable(),
                                reason="arithma backend unusable")

#: MEASURED 2026-10-28 on a fresh build (582 published formulas).
_UNCHECKED_CEILING = 126
_CHECKED = ("OK", "RULED_DIVERGENCE")


def _published():
    path = autogen_dir() / "formulas.json"
    if not path.is_file():
        pytest.skip("formulas.json not built")
    payload = json.loads(path.read_text(encoding="utf-8"))
    formulas = payload.get("formulas", payload)
    return list(formulas.values()) if isinstance(formulas, dict) else formulas


def _unchecked(formulas):
    return sorted(
        f["id"] for f in formulas
        if f.get("triple_status") not in _CHECKED and not f.get("non_numeric")
    )


def test_unchecked_formulas_do_not_grow():
    formulas = _published()
    unchecked = _unchecked(formulas)
    assert len(unchecked) <= _UNCHECKED_CEILING, (
        "%d published formulas are neither triple-checked nor marked "
        "non_numeric, above the pinned ceiling of %d. Give the new formula "
        "arithma + eml + value, or a non_numeric reason. Newest: %s"
        % (len(unchecked), _UNCHECKED_CEILING, unchecked[-6:])
    )


def test_ceiling_is_tight():
    """Lower the pin when formulas are converted; a slack pin hides growth."""
    unchecked = _unchecked(_published())
    assert len(unchecked) >= _UNCHECKED_CEILING, (
        "only %d unchecked formulas remain: lower _UNCHECKED_CEILING from %d"
        % (len(unchecked), _UNCHECKED_CEILING)
    )


def test_non_numeric_formulas_carry_no_value():
    bad = [f["id"] for f in _published()
           if f.get("non_numeric") and f.get("value") is not None]
    assert not bad, "non_numeric formulas with a value: %s" % bad


def test_non_numeric_reasons_are_reported():
    reasons = Counter(f["non_numeric"] for f in _published()
                      if f.get("non_numeric"))
    print("non_numeric reasons:", reasons.most_common(3))
    assert all(len(r.strip()) >= 10 for r in reasons), "reason too short"
