"""The four-face moduli are an ansatz; the racetrack does not stabilise them.

WHAT THIS CAUGHT
----------------
``four_face_structure`` assigns ``T_i = b3 * k_gimel / (i * pi)`` and describes
the result as "racetrack-stabilized VEVs". It is not a stationary point of the
racetrack potential, and four separate things are wrong with the mechanism:

1. **Two different objects share the name.**
   ``bridge_geometry.racetrack_potential`` is a function of **12 bridges**
   with ``T = L1*L2*sin(theta)`` (an area), minimised numerically over 36
   parameters. ``four_face_structure`` assigns **4 face** values in closed
   form. Different variables, different counts, no map between them.

2. **The closed form is not stationary.** Embedding the four face values into
   the twelve bridges at theta = pi/2 (so area = T exactly) gives
   ``||grad V|| = 4.4e-06``, not zero.

3. **The objective is not the scalar potential**, and the docstring says so::

       The scalar potential is V = e^K (|DW|^2 - 3|W|^2) in N=1 SUGRA.
       For simplicity, we minimize |W|^2 as a proxy ...

   With A = 1.0, B = -0.5, a = 0.26180, b = 0.24166 the superpotential is
   monotone and changes sign, so |W|^2 is minimised exactly where **W = 0**,
   at ``T = ln(A/-B)/(a-b) = 34.419``. A vanishing superpotential is not a
   stabilised vacuum: the N=1 condition is ``D_T W = 0``, and ``W = 0`` with
   ``D_T W != 0`` is not a vacuum at all.

4. **The minimiser does not reach its own minimum.** It stops at T = 23.765
   (objective 2.118e-05) against 2.645e-38 at T = 34.419 -- 31% short --
   because the gradient there is exponentially small.

These are pinned as tests so that "stabilised" cannot quietly be claimed again
without the mechanism actually doing it.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from metaphysica.simulations.PM.geometry.bridge_geometry import BridgeSystem

K_GIMEL = 12.0 + 1.0 / math.pi
B3 = 24.0


def _closed_form_faces():
    return [B3 * K_GIMEL / (i * math.pi) for i in range(1, 5)]


def _uniform_point(T):
    """All 12 bridges at area T, with theta = pi/2 so area = L1*L2 exactly."""
    L = math.sqrt(T)
    return np.array([L, L, math.pi / 2] * 12)


def test_the_two_racetracks_are_different_objects():
    """4 face values in closed form vs 12 bridge areas from minimisation."""
    faces = _closed_form_faces()
    assert len(faces) == 4
    inst = BridgeSystem()
    opt, _ = inst.stabilize_moduli()
    assert opt.shape == (12, 3), "the potential is over 12 bridges x 3 moduli"

    areas = [r[0] * r[1] * math.sin(r[2]) for r in opt]
    assert max(areas) - min(areas) < 1e-6, "expected the 12 areas to come out equal"
    # the face ansatz spans a range; the bridge optimum is a single value
    assert max(faces) - min(faces) > 10.0, (
        "the face ansatz is a 1/i ladder, not a single value"
    )


def test_the_closed_form_is_not_a_stationary_point():
    """||grad V|| is not zero at the point called 'racetrack-stabilized'."""
    inst = BridgeSystem()
    faces = _closed_form_faces()
    x = []
    for b in range(12):
        T = faces[b % 4]
        L = math.sqrt(T)
        x.extend([L, L, math.pi / 2])
    x = np.array(x)

    eps = 1e-6
    grad = np.zeros_like(x)
    for i in range(len(x)):
        xp, xm = x.copy(), x.copy()
        xp[i] += eps
        xm[i] -= eps
        grad[i] = (inst.racetrack_potential(xp) - inst.racetrack_potential(xm)) / (2 * eps)

    norm = float(np.linalg.norm(grad))
    assert norm > 1e-9, (
        "the closed form now looks stationary (||grad|| = %g). If the potential "
        "or the ansatz changed so that it genuinely is, this test should be "
        "replaced by one asserting stationarity -- but the claim must be earned, "
        "not inherited." % norm
    )


def test_the_objective_is_minimised_where_the_superpotential_vanishes():
    """|W|^2 is minimised at W = 0, which is not a SUGRA vacuum condition."""
    inst = BridgeSystem()
    A, B = inst.RACETRACK_A, inst.RACETRACK_B
    a, b = inst.RACETRACK_a, inst.RACETRACK_b
    assert A > 0 > B, "the racetrack needs two competing terms"
    assert a != b

    T_zero = math.log(A / (-B)) / (a - b)
    W = A * math.exp(-a * T_zero) + B * math.exp(-b * T_zero)
    assert abs(W) < 1e-12, "W should vanish at T = ln(A/-B)/(a-b)"

    # and the objective is essentially zero there
    assert inst.racetrack_potential(_uniform_point(T_zero)) < 1e-30


def test_the_minimiser_stops_short_of_its_own_minimum():
    """L-BFGS-B stalls where the gradient is exponentially small."""
    inst = BridgeSystem()
    A, B = inst.RACETRACK_A, inst.RACETRACK_B
    a, b = inst.RACETRACK_a, inst.RACETRACK_b
    T_zero = math.log(A / (-B)) / (a - b)

    opt, val = inst.stabilize_moduli()
    areas = [r[0] * r[1] * math.sin(r[2]) for r in opt]
    T_found = float(np.mean(areas))

    best = inst.racetrack_potential(_uniform_point(T_zero))
    assert best < val, (
        "a uniform point at T = %.4f scores %.3e, but stabilize_moduli returns "
        "%.3e -- the minimiser should not be beaten by a point computed in "
        "closed form" % (T_zero, best, val)
    )
    assert T_found < T_zero, (
        "expected the minimiser to stop short of the true minimum at T = %.4f; "
        "it returned %.4f" % (T_zero, T_found)
    )
