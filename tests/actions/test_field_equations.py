"""Field equations per field and vacuum checks, each with a failing control."""

from __future__ import annotations

from fractions import Fraction

import pytest
import sympy as sp

from metaphysica.actions.field_equations import Factor, field_equations, vacuum_checks
from metaphysica.actions.model import INPUT, OPEN, Action, Check, Coefficient, Field, ModelError, Term
from metaphysica.actions.surfaces import flat_torus, sphere

ONE = Coefficient("one", Fraction(0), INPUT, "p")


def _action(sig, bilinear=None, extra=()):
    D = sum(sig)
    g = Field("G", "metric", 1, Fraction(0))
    psi = Field("Psi", "spinor", 2 ** (D // 2 - 1), Fraction(D - 1, 2), "weyl")
    grav = Term("R", Coefficient("M_star_%d" % (D - 2), Fraction(D - 2), INPUT, "p"), ("R",))
    kin = Term("kin", ONE, ("Psi", "Psi", "d"), bilinear=bilinear)
    return Action("a", D, sig, (g, psi), (grav, kin) + tuple(extra))


def test_equations_of_the_two_time_action():
    eq = field_equations(_action((24, 2), "holomorphic"))
    assert eq["G"] == (r"2\,\mathrm{M\_star\_24}\left(R_{MN} - \tfrac{1}{2} G_{MN} R\right)"
                       r" = T_{MN}[\Psi]")
    assert eq["Psi"] == r"\Gamma^{M} D_{M} \Psi = 0"


def test_vanishing_kinetic_term_gives_no_equation():
    """Control: the hermitian Weyl kinetic term is zero at (24, 2)."""
    assert field_equations(_action((3, 1)))["Psi"] == r"\Gamma^{M} D_{M} \Psi = 0"
    with pytest.raises(ValueError, match="zero"):
        field_equations(_action((24, 2)))


def test_uncovered_term_raises():
    mass = Term("mass", Coefficient("m", Fraction(1), INPUT, "p"), ("Psi", "Psi"))
    with pytest.raises(ValueError, match="mass"):
        field_equations(_action((3, 1), extra=(mass,)))


def _flat(n, prefix):
    coords = sp.symbols("%s0:%d" % (prefix, n))
    return Factor("R%d" % n, n, sp.diag(-1, *([1] * (n - 1))), coords)


def test_flat_vacuum_passes():
    t2 = flat_torus()
    got = vacuum_checks(_action((5, 1)), [_flat(4, "x"), Factor("T2", 2, t2[0], tuple(t2[1]))])
    assert all(c.holds for c in got) and len(got) == 4


def test_sphere_factor_fails():
    s2 = sphere()
    got = vacuum_checks(_action((5, 1)), [_flat(4, "x"), Factor("S2", 2, s2[0], tuple(s2[1]))])
    bad = [c for c in got if not c.holds]
    assert [c.id for c in bad] == ["vacuum_ricci_flat:a:S2"]
    assert bad[0].measured == "2/r**2"


def test_certificate_background_and_potential():
    cert = Check("g2_closure", "torsion 0", True, True, "certificate")
    good = vacuum_checks(_action((9, 1)), [_flat(3, "x"), Factor("Y7", 7, certificate=cert)])
    assert all(c.holds for c in good)
    lam = Term("V", Coefficient("c_V", Fraction(10), OPEN), (), open=True)
    bad = vacuum_checks(_action((9, 1), extra=(lam,)), [_flat(3, "x"),
                        Factor("Y7", 7, certificate=cert)], {"Psi": 1})
    assert sorted(c.id for c in bad if not c.holds) == ["vacuum_matter:a:Psi",
                                                        "vacuum_potential:a"]


def test_bad_factors_raise():
    with pytest.raises(ModelError):
        vacuum_checks(_action((5, 1)), [_flat(4, "x")])
    with pytest.raises(ModelError):
        Factor("X", 2)
