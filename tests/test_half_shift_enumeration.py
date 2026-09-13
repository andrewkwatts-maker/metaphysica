"""The corrected half-shift moduli space, and the withdrawal it enforces.

The previous version of this file asserted a parity refutation of b_3 = 24.
That refutation is WITHDRAWN — its enumeration covered 1/32 of the moduli
space, its additivity premise failed on the stratum it did cover, and its
component action carried a labelling defect. These tests pin the corrected
state: the full moduli space, the non-removability of relative shifts (the
mathematical fact that voids the old reduction), Joyce's admissibility
condition, and the corrected group action — plus a guard that the module
never again claims the refutation.
"""

from __future__ import annotations

import itertools
import random

import pytest

from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
    act_on_component,
    assignments,
    elements,
    fixed_coords,
    fixed_sets_disjoint,
    flip_profile,
    generating_triples,
    is_singular,
    moved_coords,
    relative_slots,
    status_report,
    survey,
    survey_assignment,
)
from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
    _compose,
    _group,
    _non_identity,
)


@pytest.fixture(scope="module")
def group():
    return _group()


@pytest.fixture(scope="module")
def triple(group):
    return generating_triples(group)[0]


@pytest.fixture(scope="module")
def gens(group, triple):
    nz = _non_identity(group)
    return [nz[i] for i in triple]


# ------------------------------------------------------- the moduli space


def test_there_are_28_generating_triples(group):
    assert len(generating_triples(group)) == 28


def test_the_flip_profile_is_the_triangle_structure(gens):
    """1 coordinate flipped by all three, 3 by two, 3 by one."""
    prof = flip_profile(gens)
    counts = sorted(len(v) for v in prof.values())
    assert counts == [1, 1, 1, 2, 2, 2, 3]


def test_five_relative_bits_per_triple(gens):
    """2 on the triply-flipped coordinate + 1 on each doubly-flipped one.

    These are exactly the strata the withdrawn enumeration missed.
    """
    assert len(relative_slots(gens)) == 5


def test_the_full_space_is_16384_per_triple_and_the_old_was_512(group, triple):
    full = sum(1 for _ in assignments(triple, group, include_relative=True))
    old = sum(1 for _ in assignments(triple, group, include_relative=False))
    assert full == 8 ** 3 * 2 ** 5 == 16384
    assert old == 8 ** 3 == 512
    assert full == 32 * old


# ------------------------- the fact that voids the withdrawn reduction


def test_relative_flipped_shifts_are_not_removable_by_conjugation(gens):
    """Conjugation moves every flipper's shift by the same -2t, so the
    DIFFERENCE on a shared flipped coordinate is invariant. A difference of
    1/2 therefore survives every translation — checked by exhausting t in
    quarter steps, which covers all values of -2t mod 1."""
    g1, g2 = gens[0], gens[1]
    shared = [a for a in range(7) if g1[a] < 0 and g2[a] < 0]
    assert shared, "a generating pair always shares flipped coordinates"
    a = shared[0]
    s1, s2 = 0.0, 0.5
    for t4 in range(4):
        t = t4 / 4.0
        n1 = (s1 - 2 * t) % 1.0
        n2 = (s2 - 2 * t) % 1.0
        assert not (n1 == 0.0 and n2 == 0.0), (
            "a translation removed a relative shift of 1/2; the withdrawal "
            "rationale would be wrong"
        )


def test_a_joyce_style_assignment_is_valid_and_outside_the_old_stratum(
        group, triple, gens):
    """A relative shift on a shared flipped coordinate gives a genuine
    (Z/2)^3 whose singular sets are disjoint — the structure Joyce's examples
    use — and no fixed-line-only assignment can express it."""
    g1, g2 = gens[0], gens[1]
    shared = [a for a in range(7) if g1[a] < 0 and g2[a] < 0]
    sv = [[0] * 7 for _ in range(3)]
    sv[1][shared[0]] = 1                     # 1/2 on a coordinate g2 FLIPS
    svecs = tuple(tuple(r) for r in sv)

    # outside the old stratum: support is not inside fixed(g2)
    assert shared[0] not in fixed_coords(g2)

    els = elements(gens, svecs)
    # every element is an involution
    for e, s in els.values():
        ee, ss = _compose(e, s, e, s)
        assert ee == tuple([1] * 7) and ss == tuple([0] * 7)

    # g1 and g2 are both singular and their fixed sets are DISJOINT
    e1 = els[(1, 0, 0)]
    e2 = els[(0, 1, 0)]
    assert is_singular(e1) and is_singular(e2)
    assert fixed_sets_disjoint(e1, e2)


def test_in_the_old_stratum_pure_flip_pairs_always_intersect(gens):
    """The additivity premise of the withdrawn argument could not hold on
    what it covered: two pure sign flips share fixed points."""
    e1 = (tuple(gens[0]), tuple([0] * 7))
    e2 = (tuple(gens[1]), tuple([0] * 7))
    assert not fixed_sets_disjoint(e1, e2)


# ------------------------------------------------- the corrected action


def test_the_component_action_is_functorial(group, gens):
    """act(d1 . d2) == act(d1) . act(d2) — the property the old labelling
    defect broke for elements carrying their own flipped shifts."""
    rng = random.Random(0)
    checked = 0
    while checked < 100:
        svecs = tuple(tuple(rng.randint(0, 1) for _ in range(7))
                      for _ in range(3))
        els = elements(gens, svecs)
        singular = [el for b, el in els.items()
                    if b != (0, 0, 0) and is_singular(el)]
        if not singular:
            continue
        sigma = singular[0]
        moved = moved_coords(sigma[0])
        comp = dict(zip(moved, [rng.randint(0, 1) for _ in moved]))
        d1 = rng.choice(list(els.values()))
        d2 = rng.choice(list(els.values()))
        d12 = _compose(*d1, *d2)
        lhs = act_on_component(d12, sigma, comp)
        rhs = act_on_component(d1, sigma, dict(act_on_component(d2, sigma, comp)))
        assert lhs == rhs
        checked += 1


def test_the_sigma_twist_matters(gens):
    """With a flipped-coordinate shift on sigma, the corrected action differs
    from the withdrawn formula — so the old family counts were wrong where it
    applied, and this cannot regress silently."""
    g1 = gens[0]
    moved = moved_coords(g1)
    a = moved[0]
    ss = [0] * 7
    ss[a] = 1                                  # sigma carries a flipped shift
    sigma = (tuple(g1), tuple(ss))
    delta = (tuple(gens[1]), tuple([0] * 7))
    if delta[0][a] < 0:
        comp = dict.fromkeys(moved, 0)
        with_twist = dict(act_on_component(delta, sigma, comp))[a]
        without = dict(act_on_component(delta, (sigma[0], tuple([0] * 7)),
                                        comp))[a]
        assert with_twist != without


# ------------------------------------------------------ the survey layer


def test_the_canonical_joyce_structure_exists(group, triple):
    """3 singular elements, pairwise disjoint, 12 plain-T3 families — the
    family structure of Joyce's first example. The withdrawn enumeration
    could never produce it; the corrected one must."""
    result = survey(include_relative=True, group=group, triples=[triple])
    assert result["joyce_structure_assignments"] > 0
    assert 12 in result["admissible_family_counts"]


def test_admissibility_is_not_vacuous(group, triple, gens):
    """Both verdicts occur, so the filter genuinely discriminates."""
    seen = set()
    for svecs in assignments(triple, group, include_relative=True):
        rec = survey_assignment(triple, svecs, group)
        if rec["n_singular"] >= 2:
            seen.add(rec["admissible"])
        if seen == {True, False}:
            break
    assert seen == {True, False}


# ---------------------------------------------------------- the withdrawal


def test_the_module_declares_the_withdrawal():
    report = status_report()
    assert report["b3_24_status"] == "UNDETERMINED"
    assert "WITHDRAWN" not in report["b3_24_status"]
    assert "1/32" in report["withdrawn"]
    assert report["moduli_space_size"] == 458752
    assert report["withdrawn_stratum_size"] == 14336


def test_no_refutation_is_claimed_anywhere_in_the_module():
    """The word may appear only in the withdrawal narrative, never as a live
    verdict; and the old verdict key must be gone."""
    import metaphysica.simulations.PM.geometry.half_shift_enumeration as m

    assert not hasattr(m, "refutation_report"), (
        "the withdrawn API returned; the register must rule before any "
        "refutation is republished"
    )
    report = status_report()
    assert "REFUTED" not in str(report.get("b3_24_status"))


def test_betti_statements_stay_conditional():
    report = status_report()
    assert "Not asserted" in report["conditional_gate"]
    assert "calibration" in report["conditional_gate"]
    assert report["flat_contribution"] == 7
    assert "at least 6" in report["unconditional_bound"]
