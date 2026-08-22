"""Tests for the sparse differential-form kernel.

These are written against a specific hazard. The thing being tested is largely
"is this zero", and the module this one replaces -- g2_differential.compute_d_phi
-- returns np.zeros(...) unconditionally. So `assert d(d(w)) == 0` passes there
while verifying nothing whatsoever.

Every zero-assertion below is therefore PAIRED with a non-vacuity assertion
proving the input was non-trivial, and the sign convention carries an explicit
mutation test. The first draft of the graded-commutativity check was itself
vacuous (overlapping indices made both sides empty, so they "agreed"), which is
why the disjoint-index construction is spelled out rather than incidental.
"""
from __future__ import annotations

from itertools import combinations

import pytest
import sympy as sp

from metaphysica.simulations.PM.geometry.exterior_algebra import (
    Form,
    FormBudgetError,
    MAX_DENSE_ENTRIES,
    MAX_SPARSE_COMPONENTS,
    component_count,
    exterior_d,
    form_from_dense,
    guard_form_size,
    guard_wedge_cost,
    integrate_top,
    levi_civita_7d,
    to_dense,
    top_coefficient,
    wedge,
)


# ── size guards ──────────────────────────────────────────────────────────────


def test_component_counts_match_binomials():
    assert component_count(7, 3) == 35
    assert component_count(13, 4) == 715
    assert component_count(28, 7) == 1_184_040
    assert component_count(13, 13) == 1
    assert component_count(7, 9) == 0  # degree above dimension


def test_dense_guard_refuses_the_100gb_form():
    """A dense 7-form in 28D is 100.5 GB -- the 158 GB incident's class."""
    with pytest.raises(FormBudgetError, match="GB"):
        guard_form_size(28, 7, dense=True)


def test_dense_guard_refuses_the_13d_levi_civita():
    """13^13 x 8 bytes = 2.2 PiB. This must never be allocated."""
    with pytest.raises(FormBudgetError):
        guard_form_size(13, 13, dense=True)


def test_sparse_guard_refuses_middle_degree_blowup():
    """C(28,14) = 40,116,600 -- invisible in the low-degree counts."""
    with pytest.raises(FormBudgetError, match="independent components"):
        guard_form_size(28, 14, dense=False)


def test_guards_permit_everything_the_physics_needs():
    """The cases actually used must pass with headroom."""
    assert guard_form_size(13, 4, dense=True) == 13 ** 4     # 0.22 MB
    assert guard_form_size(28, 4, dense=True) == 28 ** 4     # 4.69 MB
    assert guard_form_size(7, 7, dense=True) == 7 ** 7       # 6.3 MB
    assert guard_form_size(13, 4) == 715
    assert guard_form_size(28, 7) == 1_184_040               # sparse is fine


def test_wedge_cost_guard_is_about_time_not_memory():
    """20,475^2 = 4.19e8 iterations would present as a hang, not a crash."""
    with pytest.raises(FormBudgetError, match="hang"):
        guard_wedge_cost(20_475, 20_475)
    assert guard_wedge_cost(1000, 1000) == 1_000_000


# ── wedge algebra ────────────────────────────────────────────────────────────


def test_graded_commutativity_odd_times_odd_flips_sign():
    """a^b = (-1)^(pq) b^a, with p=q=3 so the sign genuinely flips.

    Indices are DISJOINT on purpose: an earlier version of this test used
    overlapping indices, both sides came out empty, and it "passed" vacuously.
    """
    a = Form.from_terms(7, 3, [((0, 1, 2), 2.0)])
    b = Form.from_terms(7, 3, [((3, 4, 5), 1.5)])
    ab, ba = wedge(a, b), wedge(b, a)

    assert len(ab) == 1, "vacuous: a^b must be non-empty for this to mean anything"
    assert ab.components[(0, 1, 2, 3, 4, 5)] == pytest.approx(3.0)
    assert ba.components[(0, 1, 2, 3, 4, 5)] == pytest.approx(-3.0)


def test_graded_commutativity_even_times_odd_does_not_flip():
    a = Form.from_terms(7, 2, [((0, 1), 1.0)])
    b = Form.from_terms(7, 3, [((2, 3, 4), 1.0)])
    ab, ba = wedge(a, b), wedge(b, a)
    assert len(ab) == 1
    assert ab.components == ba.components


def test_wedge_is_associative():
    f1 = Form.from_terms(7, 1, [((0,), 2.0)])
    f2 = Form.from_terms(7, 2, [((1, 2), 3.0)])
    f3 = Form.from_terms(7, 2, [((3, 4), 5.0)])
    left = wedge(wedge(f1, f2), f3)
    right = wedge(f1, wedge(f2, f3))
    assert len(left) == 1
    assert left.components == right.components
    assert list(left.components.values())[0] == pytest.approx(30.0)


def test_repeated_index_annihilates():
    """dx^i ^ dx^i = 0."""
    c = Form.from_terms(7, 2, [((0, 1), 1.0)])
    assert wedge(c, c).is_zero()


def test_wedge_above_dimension_vanishes():
    a = Form.from_terms(7, 4, [((0, 1, 2, 3), 1.0)])
    b = Form.from_terms(7, 4, [((0, 1, 2, 4), 1.0)])
    assert wedge(a, b).is_zero()


def test_zero_form_fast_path_matches_general_path():
    """The 0-form shortcut must agree with ordinary scalar multiplication."""
    s = Form.scalar(7, 3.0)
    f = Form.from_terms(7, 2, [((0, 1), 2.0), ((2, 3), -1.0)])
    left, right = wedge(s, f), wedge(f, s)
    assert left.components == {(0, 1): 6.0, (2, 3): -3.0}
    assert right.components == left.components


def test_from_terms_canonicalises_unsorted_indices():
    """(1,0) must become -(0,1), not an invalid key."""
    f = Form.from_terms(7, 2, [((1, 0), 1.0)])
    assert f.components == {(0, 1): -1.0}


def test_constructor_rejects_non_canonical_keys():
    """Direct construction must not silently accept an unsorted multi-index."""
    with pytest.raises(ValueError, match="strictly increasing"):
        Form(dim=7, degree=2, components={(1, 0): 1.0})


# ── exterior derivative ──────────────────────────────────────────────────────


def _c3_with_external_dependence(n: int, coords):
    """A 3-form whose coefficients depend on coordinates OUTSIDE their index.

    Necessary for a meaningful d: a coefficient depending only on the
    coordinates already in its own multi-index differentiates to zero, which
    would make d^2 = 0 vacuous. Uses 24 components to match elder_kads.
    """
    keys = list(combinations(range(n), 3))[:24]
    terms = []
    for i, k in enumerate(keys):
        outside = [a for a in range(n) if a not in k]
        terms.append(
            (k, sp.Integer(i + 1) * coords[outside[0]] * coords[outside[1]]
                + coords[outside[2]] ** 2)
        )
    return Form.from_terms(n, 3, terms)


def test_d_squared_is_zero_and_is_not_vacuous():
    """d(dC_3) = 0 structurally, with dC_3 demonstrably non-empty.

    The second assertion is the whole point: the first one alone passes
    against g2_differential.compute_d_phi(), which returns np.zeros(...)
    unconditionally.
    """
    n = 13
    x = sp.symbols("x0:13")
    c3 = _c3_with_external_dependence(n, x)
    g4 = exterior_d(c3, x)

    assert len(g4) > 0, "vacuous: dC_3 is empty, so d^2 = 0 would prove nothing"
    assert len(g4) == 46
    assert exterior_d(g4, x).is_zero()


def test_wrong_sign_convention_breaks_d_squared():
    """Mutation test: with the alternating sign forced to +1, d^2 != 0.

    Demonstrates the gate can fail -- required by the house rule from the
    'physics invariants were decorative' correction.
    """
    n = 13
    x = sp.symbols("x0:13")
    c3 = _c3_with_external_dependence(n, x)

    def broken_d(form):
        out = {}
        for idx, val in form.components.items():
            for axis in range(form.dim):
                if axis in idx:
                    continue
                key = tuple(sorted((axis,) + idx))
                term = sp.diff(val, x[axis])  # sign dropped
                if term == 0:
                    continue
                out[key] = sp.expand(out.get(key, 0) + term)
        return Form(form.dim, form.degree + 1,
                    {k: v for k, v in out.items() if v != 0})

    assert not broken_d(broken_d(c3)).is_zero()


def test_exterior_d_refuses_float_coefficients():
    """Floats are refused rather than silently returning zeros.

    A flat-chart float form really does have d = 0, but returning that zero is
    indistinguishable from a broken derivative -- which is exactly how
    compute_d_phi() has been passing its tests.
    """
    f = Form.from_terms(7, 2, [((0, 1), 1.0)])
    with pytest.raises(TypeError, match="sympy"):
        exterior_d(f, sp.symbols("y0:7"))


def test_leibniz_rule():
    """d(a^b) = da^b + (-1)^p a^db."""
    n = 5
    x = sp.symbols("y0:5")
    a = Form.from_terms(n, 1, [((0,), x[2] ** 2), ((1,), x[3])])
    b = Form.from_terms(n, 1, [((2,), x[0] * x[4]), ((3,), x[1])])

    lhs = exterior_d(wedge(a, b), x)
    rhs_terms = wedge(exterior_d(a, x), b)
    second = wedge(a, exterior_d(b, x))
    combined = dict(rhs_terms.components)
    for k, v in second.components.items():
        combined[k] = sp.expand(combined.get(k, 0) + ((-1) ** a.degree) * v)
    combined = {k: v for k, v in combined.items() if sp.simplify(v) != 0}

    assert len(lhs) > 0, "vacuous: d(a^b) is empty"
    assert set(lhs.components) == set(combined)
    for k in lhs.components:
        assert sp.simplify(lhs.components[k] - combined[k]) == 0


# ── top forms, density, reuse ────────────────────────────────────────────────


def test_top_coefficient_and_integration():
    f = Form.from_terms(3, 3, [((0, 1, 2), 7.0)])
    assert top_coefficient(f) == pytest.approx(7.0)
    assert integrate_top(f, volume=2.0) == pytest.approx(14.0)


def test_top_coefficient_rejects_non_top_form():
    with pytest.raises(ValueError, match="not a top form"):
        top_coefficient(Form.from_terms(7, 3, [((0, 1, 2), 1.0)]))


def test_levi_civita_7d_is_shared_and_readonly():
    """One 6.59 MB copy process-wide; shared, so it must not be writeable."""
    a, b = levi_civita_7d(), levi_civita_7d()
    assert a is b, "must be cached -- it costs 0.36 s and 6.59 MB per build"
    assert not a.flags.writeable
    assert a.shape == (7,) * 7


def test_dense_roundtrip_preserves_components():
    f = Form.from_terms(5, 2, [((0, 1), 2.0), ((2, 3), -3.0)])
    assert form_from_dense(to_dense(f), 2).components == f.components


def test_dense_roundtrip_is_antisymmetric():
    f = Form.from_terms(5, 2, [((0, 1), 2.0)])
    arr = to_dense(f)
    assert arr[0, 1] == pytest.approx(2.0)
    assert arr[1, 0] == pytest.approx(-2.0)


def test_module_does_not_overclaim_topology():
    """Integration here is coefficient x volume, not a topological invariant.

    Flat R^n has trivial holonomy and no non-trivial cycles. Asserting the
    scope text keeps a future reader (or a future edit) from quietly promoting
    a number into an invariant.
    """
    import metaphysica.simulations.PM.geometry.exterior_algebra as ea

    doc = ea.__doc__ or ""
    assert "NOT ESTABLISHED" in doc
    assert "not compute a" in doc or "does not compute" in doc
    assert "compact G2 manifold" in doc
