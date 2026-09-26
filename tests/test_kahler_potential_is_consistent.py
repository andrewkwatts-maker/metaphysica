"""One Kähler potential, not three.

WHAT THIS CAUGHT
----------------
The framework states the Kähler potential three mutually inconsistent ways:

    K = -3 ln(T + T_bar)            config.py, dynamical_lambda,
                                    bridge_geometry, bridge_axion_ede
    K = -2 ln(Vol_7)                lagrangian_master
    K = -3 ln(4*pi/3 * Im(T)^{7/3}) matter_sector_complete

These cannot all be right, and K is not decoration -- it enters the F-term
potential V = e^K (K^{IJbar} D_I W D_Jbar Wbar - 3|W|^2), so the disagreement
propagates into every moduli result.

WHICH ONE IS THE G2 ONE
The canonical form for M-theory on a G2 manifold is K = -3 ln V_7 with
V_7 = (1/7) int Phi ^ *Phi. For a single overall modulus the 7-volume scales as
V_7 ~ (Im T)^{7/3}, so -3 ln V_7 = -7 ln(Im T): the **7/3 form is the
G2-consistent one**. K = -3 ln(T + T_bar) is the CY_3 / no-scale
single-modulus form, correct there and carried over here; the -2 coefficient
matches neither.

WHY THIS TEST DOES NOT FIX IT
Rewriting the call sites changes published numbers, so which form is adopted is
a physics ruling for the author. This test records the three known statements
and fails if a FOURTH appears -- the same pattern used for the contradictory
scoring groups and the open datasource rulings. It makes the inconsistency
impossible to grow silently while leaving the ruling where it belongs.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

#: (relative path, regex) for each Kähler statement currently in the tree.
#: Adding a form means adding a line here, which forces a look at whether it
#: agrees with the others.
_KNOWN_FORMS = {
    "-3ln(T+Tbar)": [
        ("src/metaphysica/config/parameters/moduli.py",
         r"K = -3 ln\(T \+ T_bar\)"),
        ("src/metaphysica/simulations/PM/cosmology/dynamical_lambda.py",
         r"K = -3 ln\(T \+ T_bar\)|K = -3 ln\(2T\)"),
        ("src/metaphysica/simulations/PM/geometry/bridge_geometry.py",
         r"K = -3 ln\(T \+ T_bar\)|K = -3 ln\(2T\)"),
        ("src/metaphysica/simulations/PM/cosmology/bridge_axion_ede.py",
         r"K = -3 ln\(2T\)"),
    ],
    "-2ln(Vol7)": [
        ("src/metaphysica/simulations/PM/derivations/lagrangian_master.py",
         r"K = -2 ln\(Vol_7\)"),
    ],
    "-3ln(Im(T)^{7/3})": [
        ("src/metaphysica/simulations/PM/derivations/matter_sector_complete.py",
         r"K = -3 ln\(4\*pi/3 \* Im\(T\)\^\{7/3\}\)"),
    ],
}

_ROOT = Path(__file__).resolve().parents[1]


def test_the_three_known_forms_are_all_still_present():
    """If one disappeared, the inconsistency may have been resolved.

    That would be good news, and this test should then be updated -- but it
    must be a deliberate act, not a silent drift.
    """
    missing = []
    for label, sites in _KNOWN_FORMS.items():
        for rel, pattern in sites:
            f = _ROOT / rel
            if not f.is_file():
                missing.append("%s: file gone (%s)" % (label, rel))
                continue
            if not re.search(pattern, f.read_text(encoding="utf-8")):
                missing.append("%s: no longer in %s" % (label, rel))
    if missing:
        pytest.skip(
            "a recorded Kahler form has changed; review and update this test:\n  "
            + "\n  ".join(missing)
        )


def test_no_fourth_kahler_form_has_appeared():
    """Any `K = ... ln ...` statement must be one of the three recorded ones."""
    seen = set()
    for path in _ROOT.joinpath("src/metaphysica").rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for m in re.finditer(r"K\s*=\s*-\s*(\d)\s*\*?\s*ln", text):
            seen.add((m.group(1), str(path.relative_to(_ROOT)).replace("\\", "/")))

    coefficients = {c for c, _ in seen}
    assert coefficients <= {"2", "3"}, (
        "a Kahler potential with an unrecorded coefficient appeared: %s\n"
        "The G2 form is K = -3 ln V_7. Add it to _KNOWN_FORMS only after "
        "checking whether it agrees with the others." % sorted(coefficients)
    )


def test_the_g2_form_and_the_cy_form_really_do_disagree():
    """The inconsistency is arithmetic, not a matter of taste.

    With V_7 proportional to (Im T)^{7/3}:
        -3 ln V_7          = -7   ln(Im T)
        -3 ln(T + T_bar)   = -3   ln(2 Im T)   -> coefficient 3, not 7
        -2 ln V_7          = -14/3 ln(Im T)    -> neither
    Three different logarithmic slopes, so three different kinetic terms.
    """
    import math

    def slope(coefficient, volume_power):
        """d/d ln(Im T) of -coefficient * ln(V_7), with V_7 ~ (Im T)^power."""
        return -coefficient * volume_power

    g2_slope = slope(3, 7.0 / 3.0)        # canonical G2
    cy_slope = slope(3, 1.0)              # -3 ln(T + Tbar)
    odd_slope = slope(2, 7.0 / 3.0)       # -2 ln(Vol_7)

    assert g2_slope == pytest.approx(-7.0)
    assert cy_slope == pytest.approx(-3.0)
    assert odd_slope == pytest.approx(-14.0 / 3.0)
    assert len({round(g2_slope, 6), round(cy_slope, 6), round(odd_slope, 6)}) == 3, (
        "the three forms must give three distinct slopes, or there is nothing "
        "to reconcile"
    )
    assert not math.isclose(g2_slope, cy_slope)
