"""Fork gates: validation, the fixed point, digest stability, enumeration.

The shared tiny theory has no gated fork and its hand counts are pinned, so
this file builds its own small gated theory on top of it.
"""

from __future__ import annotations

import pytest

from metaphysica.testground.configurations.enumerate import (
    count_configurations,
    enumerate_configurations,
)
from metaphysica.testground.configurations.model import digest_of
from metaphysica.testground.switches.gates import (
    canonical,
    gate_open,
    validate_gates,
)
from metaphysica.testground.switches.model import Fork, VariantOption
from tests.testground.test_2a_support import make_theory


def _opt(id_, **kw):
    return VariantOption(id_, "s", "c", **kw)


def _fork(id_, *opts, gate=()):
    return Fork(id_, "q", "test", list(opts), "OPEN", applies_when=gate)


def gated():
    """mech (m, t) gates betti (b0, b1) gates tail (t0, t1) via betti=b1."""
    return {
        "mech": _fork("mech", _opt("m", adopted=True), _opt("t")),
        "betti": _fork("betti", _opt("b0", adopted=True), _opt("b1"),
                       gate=(("mech", "t"),)),
        "tail": _fork("tail", _opt("t0", adopted=True), _opt("t1"),
                      gate=(("betti", "b1"),)),
    }


def test_validation_refuses_unknown_fork_option_self_and_cycle():
    f = gated()
    validate_gates(f)
    bad = dict(f, betti=_fork("betti", _opt("b0", adopted=True),
                              gate=(("nope", "x"),)))
    with pytest.raises(ValueError, match="unknown fork"):
        validate_gates(bad)
    bad = dict(f, betti=_fork("betti", _opt("b0", adopted=True),
                              gate=(("mech", "zz"),)))
    with pytest.raises(ValueError, match="unknown option"):
        validate_gates(bad)
    bad = dict(f, betti=_fork("betti", _opt("b0", adopted=True),
                              gate=(("betti", "b0"),)))
    with pytest.raises(ValueError, match="itself"):
        validate_gates(bad)
    bad = dict(f, mech=_fork("mech", _opt("m", adopted=True), _opt("t"),
                             gate=(("tail", "t1"),)))
    with pytest.raises(ValueError, match="cycle"):
        validate_gates(bad)


def test_missing_fork_counts_as_its_default():
    f = gated()
    assert not gate_open(f, "betti", {})
    assert gate_open(f, "betti", {"mech": "t"})


def test_canonical_reaches_the_fixed_point_through_a_chain():
    f = gated()
    # tail's gate needs betti=b1, but betti is itself gated off by mech=m.
    assert canonical(f, {"betti": "b1", "tail": "t1"}) == {}
    assert canonical(f, {"mech": "t", "betti": "b1", "tail": "t1"}) == {
        "mech": "t", "betti": "b1", "tail": "t1"}
    assert canonical(f, {"mech": "m", "tail": "t0"}) == {}


def test_canonical_drops_entries_equal_to_the_default():
    assert canonical(gated(), {"mech": "m", "betti": "b0"}) == {}


def test_a_selection_with_no_gated_off_entries_keeps_its_digest():
    sel = {"mech": "t", "betti": "b1", "tail": "t1"}
    assert digest_of(sel) == "%s" % digest_of(dict(sel))
    theory = make_theory(forks=gated(), constraints=[],
                         selection={"mech": "m", "betti": "b0", "tail": "t0"})
    digests = {c.digest for c in
               enumerate_configurations(theory, "archaeology")}
    assert digest_of(sel) in digests
    assert digest_of({"mech": "t", "betti": "b1", "tail": "t1"}) in digests


def test_enumeration_collapses_gated_off_differences():
    theory = make_theory(forks=gated(), constraints=[],
                         selection={"mech": "m", "betti": "b0", "tail": "t0"})
    cfgs = [c.mapping for c in enumerate_configurations(theory, "archaeology")]
    # mech=m: one path; mech=t: betti b0 (tail pinned) + betti b1 x tail 2.
    assert len(cfgs) == 1 + 1 + 2
    assert count_configurations(theory, "archaeology").total == len(cfgs)
    assert all(c["betti"] == "b0" for c in cfgs if c["mech"] == "m")
