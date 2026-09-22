"""The glued 3-form's GL(7) orbit along the neck, and the wall it crosses.

WHAT WAS MEASURED, 2026-09-22, adopted branch (`all_plus_one`)
=============================================================
Outcome: **DEGENERATE**, and specifically NOT crossover.

  * The glued form never leaves the SPLIT orbit. The orbit label is the
    UNORDERED signature of Hitchin's B, {4,3}, and it is {4,3} at every one of
    the 700 grid points.
  * det B nevertheless CHANGES SIGN. 165 of 700 points carry ordered signature
    (3,4) rather than (4,3) -- an orientation flip inside the one orbit -- so a
    locus with det B = 0 must lie between them, and 36 sign changes in r were
    bracketed.
  * The wall sits where the twisted block's amplitude equals the flat block's:
    t a^2 / r_*^2 -> 1 from below (0.800 at t=1 rising to 1.033 at t=1000), so
    r_* is proportional to sqrt(t), which follows from eta ~ a^2/r^2 and was
    predicted from the form rather than fitted to the scan.
  * Below a critical amplitude the wall is INSIDE the bolt and off the
    manifold. t_crit depends on theta: 2.2247 at the pole, 0.3903 at
    theta = 2pi/3.

Why that distinction is the whole point: classifying on the ORDERED signature
would have reported a crossover to the compact orbit, which would have meant
the two `g2_form_convention` branches differ by region and every holonomy
sentence needs a domain. They do not. What is true is weaker and still new --
the framework now has a locus where phi is not stable and no metric is induced
at all.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from metaphysica.simulations.PM.geometry import glued_orbit_scan as gos

#: One family, a coarse grid. The full scan is ~5 minutes; these reproduce
#: every structural claim above on a grid small enough to run every time.
_RADII = (1.0, 1.2, 2.0, 10.0, 100.0)
_T_VALUES = (0.0, 0.1, 1.0, 10.0)
_THETAS = (math.pi / 4, math.pi / 2)


@pytest.fixture(scope="module")
def records():
    return gos.scan(radii=_RADII, t_values=_T_VALUES, thetas=_THETAS,
                    n_families=1)


# ------------------------------------------------------------------ the form

def test_the_glued_form_is_antisymmetric_at_every_sampled_point():
    """A component array that is not a 3-form makes every orbit label noise."""
    fam = gos._families(1)[0]
    for t in (0.0, 1.0, 10.0):
        phi = gos.glued_three_form(fam, r=1.5, theta=math.pi / 4, t=t)
        assert phi.shape == (7, 7, 7)
        assert np.allclose(phi, -np.transpose(phi, (1, 0, 2)), atol=1e-12)
        assert np.allclose(phi, np.transpose(phi, (1, 2, 0)), atol=1e-12)


def test_t_zero_is_exactly_the_flat_form():
    """The gluing parameter must switch the twisted block OFF at zero.

    If it did not, every t = 0 record would be measuring something other than
    the flat orbifold form and the scan would have no baseline.
    """
    fam = gos._families(1)[0]
    phi0 = gos.glued_three_form(fam, r=1.3, theta=1.0, t=0.0)
    assert np.array_equal(phi0, gos._flat_phi())


def test_the_twisted_block_actually_moves_the_form():
    """A scan over a t that changes nothing would pass forever."""
    fam = gos._families(1)[0]
    phi0 = gos.glued_three_form(fam, r=1.3, theta=1.0, t=0.0)
    phi1 = gos.glued_three_form(fam, r=1.3, theta=1.0, t=1.0)
    assert not np.allclose(phi0, phi1), (
        "t = 1 leaves the component array unchanged, so the twisted block is "
        "not being added and the whole scan is measuring the flat form"
    )


def test_eta_is_read_from_the_eguchi_hanson_module_not_retyped():
    """The components must match `exceptional_two_form` term by term.

    h = a^2 r^-2 gives eta_{r phi} = -2 a^2 cos(theta)/r^3,
    eta_{r psi} = -2 a^2/r^3 and eta_{theta phi} = -a^2 sin(theta)/r^2. Those
    are written here ONCE, as an independent check on the substitution path --
    not as the source the scan reads.
    """
    r, theta, a = 2.0, math.pi / 3, 1.5
    got = gos.eta_components_at(r, theta, a)
    expect = {
        (0, 2): -2 * a ** 2 * math.cos(theta) / r ** 3,
        (0, 3): -2 * a ** 2 / r ** 3,
        (1, 2): -a ** 2 * math.sin(theta) / r ** 2,
    }
    assert set(got) == set(expect)
    for key, value in expect.items():
        assert got[key] == pytest.approx(value, rel=1e-9)


# ------------------------------------------------------- the orbit invariant

def test_the_orbit_label_is_the_unordered_signature():
    """(4,3) and (3,4) are ONE orbit: an orientation-reversing A flips B.

    This is the classification error the module was written to refuse, so it
    gets a direct test rather than only an indirect one through the scan.
    """
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )

    phi = G2DifferentialGeometry()._standard_phi()
    forward = gos.orbit_at(phi)
    # Reflecting one coordinate is an orientation-reversing GL(7,R) element.
    flipped = -np.array(phi)
    reflected = np.einsum("ia,jb,kc,abc->ijk",
                          np.diag([-1.0, 1, 1, 1, 1, 1, 1]),
                          np.diag([-1.0, 1, 1, 1, 1, 1, 1]),
                          np.diag([-1.0, 1, 1, 1, 1, 1, 1]), phi)
    for moved in (flipped, reflected):
        rec = gos.orbit_at(moved)
        assert rec["orbit"] == forward["orbit"], (
            "an orientation-reversing element changed the reported ORBIT; the "
            "classifier is reading the ordered signature"
        )


def test_the_flat_form_sits_in_the_orbit_the_fork_declares():
    """The scan's baseline must agree with `real_form_report`, or it is unmoored."""
    rec = gos.orbit_at(gos._flat_phi())
    assert rec["signature_unordered"] == gos.expected_unordered_signature()
    assert rec["n_negative"] == gos.expected_negative_eigenvalues()


def test_the_expected_signature_is_read_from_the_fork_not_hardcoded():
    """Switching the convention must move the expectation, or no guard is fork-aware."""
    split = gos.expected_unordered_signature("all_plus_one")
    compact = gos.expected_unordered_signature("octonion_derived")
    assert split == (4, 3)
    assert compact == (7, 0)
    assert split != compact, (
        "both branches report the same expected signature, so the seam guard "
        "cannot tell them apart and is not fork-aware"
    )


# --------------------------------------------------------- the measured facts

def test_the_form_never_leaves_the_home_orbit(records):
    """The measured result: no crossover, on the unordered invariant."""
    home = "COMPACT" if gos.expected_unordered_signature() == (7, 0) else "SPLIT"
    labels = {r["orbit"] for r in records}
    assert labels == {home}, (
        "the glued form left the home orbit %s; labels seen were %s. Either the "
        "orbit genuinely drifted -- in which case every holonomy sentence now "
        "needs a DOMAIN -- or the classifier regressed to the ordered "
        "signature." % (home, sorted(labels))
    )


def test_det_B_changes_sign_so_a_degenerate_wall_exists(records):
    """The measured result: an orientation flip inside the orbit, hence a wall.

    The sign change is what proves the wall. A grid can step over det B = 0
    without landing on it, so the threshold detector alone would report nothing.
    """
    signs = {r["det_B_sign"] for r in records}
    assert signs == {1, -1}, (
        "det B does not change sign anywhere on the grid, so the measured "
        "degenerate wall has disappeared. Signs seen: %s" % sorted(signs)
    )
    walls = [d for d in gos.degenerate_records(records)
             if d["detection"] == "det_B sign change in r"]
    assert walls, "sign changes exist but the bracketing detector found none"


def test_the_outcome_is_degenerate_and_not_crossover(records):
    outcome = gos.orbit_outcome(records)
    assert outcome["outcome"] == "DEGENERATE", (
        "the measured outcome was DEGENERATE on 2026-09-22; it is now %r. Each "
        "of the three outcomes means something different for the wording task, "
        "so a change here is a finding and not a test to adjust."
        % outcome["outcome"]
    )
    assert outcome["n_in_other_open_orbit"] == 0, (
        "a crossover to the other open orbit appeared; that would make the two "
        "g2_form_convention branches differ by REGION"
    )
    assert outcome["n_orientation_flipped_within_home_orbit"] > 0


def test_small_t_is_stable_all_the_way_to_the_bolt(records):
    """Below the critical amplitude the wall is off the manifold.

    So the degeneracy is not a claim that the construction is broken: it is a
    claim about an amplitude, and the amplitude has a measured threshold.
    """
    small = [r for r in records if 0.0 < r["t"] <= 0.1]
    assert small, "the grid has no small-t sample to make the statement on"
    assert all(r["det_B_sign"] == small[0]["det_B_sign"] for r in small), (
        "det B already flips at t <= 0.1, so the critical amplitude is smaller "
        "than the measurement recorded"
    )


# ------------------------------------------------------------ the seam guard

def test_the_seam_signature_guard_is_fork_aware_and_failable():
    """Exactly the fork's own negative-eigenvalue count at the seam, below t_crit.

    The guard is placed at t = 0.1, BELOW the measured t_crit (0.774 at
    theta = pi/4), because above it the seam is inside the wall where the
    ordered count legitimately reads 4 rather than 3. A guard placed at t = 1
    would fail against the real geometry, which is a guard that misreads its own
    subject.
    """
    rec = gos.seam_signature(theta=math.pi / 4, t=0.1)
    assert rec["n_negative"] == gos.expected_negative_eigenvalues(), (
        "at the seam r = a with t below the critical amplitude, Hitchin's B "
        "must have exactly the fork's declared negative-eigenvalue count. Got "
        "%d, expected %d, signature %s"
        % (rec["n_negative"], gos.expected_negative_eigenvalues(),
           rec["signature"])
    )
    assert rec["signature_unordered"] == gos.expected_unordered_signature()
    assert not rec["is_degenerate"], (
        "phi is degenerate at the seam below the critical amplitude, so no "
        "metric is induced where the construction needs one"
    )


def test_the_seam_guard_would_fail_if_the_orbit_drifted():
    """The guard must be capable of failing, so feed it a form that drifts.

    A 3-form scaled toward zero in one direction leaves the open orbit; if the
    guard still reported the declared signature it would be inert.
    """
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )

    phi = np.array(G2DifferentialGeometry()._standard_phi(), dtype=float)
    phi[0, :, :] *= 1e-8
    phi[:, 0, :] *= 1e-8
    phi[:, :, 0] *= 1e-8
    rec = gos.orbit_at(phi, det_reference=abs(
        gos.orbit_at(gos._flat_phi())["det_B"]))
    assert rec["orbit"] != "SPLIT" or rec["is_degenerate"], (
        "a form collapsed along one coordinate still reports the home orbit, "
        "so the orbit classifier cannot detect drift at all"
    )


# --------------------------------------------------------------- the scaling

def test_the_wall_scales_as_sqrt_t_as_the_form_predicts():
    """eta ~ a^2/r^2 forces r_* proportional to sqrt(t). Measured, not fitted."""
    report = gos.wall_scaling_report(t_values=(1.0, 10.0, 100.0))
    ratios = report["t_a2_over_r2_at_wall"]
    assert len(ratios) == 3, "a wall was not found at every sampled t"
    for value in ratios:
        assert 0.5 < value < 1.5, (
            "t a^2 / r_*^2 = %.4f at the wall, which is not of order one, so "
            "the wall is not where the twisted and flat blocks balance" % value
        )
    assert ratios == sorted(ratios), (
        "t a^2/r_*^2 must approach its limit monotonically from below as the "
        "subleading a^4/r^4 term in eta dies off"
    )


def test_there_is_a_critical_amplitude_and_it_depends_on_theta():
    """t_crit is a real threshold, not a constant, and the poles differ most."""
    at_pole = gos.critical_amplitude(theta=1e-6)
    at_quarter = gos.critical_amplitude(theta=math.pi / 4)
    assert at_pole["t_crit"] is not None
    assert at_quarter["t_crit"] is not None
    assert at_pole["t_crit"] > at_quarter["t_crit"], (
        "the critical amplitude must be LARGER at the pole, where eta's "
        "cos(theta) component is extremal and the sin(theta) component vanishes"
    )
    assert 0.1 < at_quarter["t_crit"] < 10.0


# ------------------------------------------------------------- the order tags

def test_every_record_carries_its_order_tag(records):
    """Exact and asymptotic are never conflated, at every consumer."""
    for rec in records:
        assert rec["order"] == "leading-order-in-t"
        assert rec["flat_block_identification"] == "asymptotic (ALE)"

    for report in (gos.orbit_outcome(records),
                   gos.seam_signature(t=0.1),
                   gos.critical_amplitude(),
                   gos.wall_scaling_report(t_values=(1.0,))):
        assert report["order"] == "leading-order-in-t"


def test_the_scan_refuses_an_unknown_convention():
    """A silent default on the fork is the defect geometry_narration exists for."""
    with pytest.raises(ValueError, match="unknown g2_form_convention"):
        gos._flat_phi("not_a_branch")


# ------------------------------------------------- the contraction-order fix

def test_the_optimised_hitchin_contraction_preserves_the_orbit_verdict():
    """`optimize=True` reorders the contraction. What must not change is the ORBIT.

    The orbit scan evaluates Hitchin's B at hundreds of grid points and the
    naive contraction forms the full 7^7 intermediate each time (0.156 s per
    call); the optimised order is ~500x faster.

    It is NOT bitwise identical -- measured, the two orders differ by ~1e-13
    absolute on entries of order 400, which is floating-point reassociation at
    machine epsilon. An earlier version of this test asserted bitwise equality
    on the strength of a single phi and failed immediately on a glued one,
    which is the test working.

    So the property pinned here is the one the scan actually depends on: the
    sign of det B and the eigenvalue signs agree under both orders, at every
    sampled point. If that ever stops holding, the speedup has to be
    re-justified rather than silently kept.
    """
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
        _levi_civita_7d,
    )

    eps = _levi_civita_7d()
    fam = gos._families(1)[0]
    samples = [G2DifferentialGeometry()._standard_phi()]
    for t in (0.1, 1.0, 5.0):
        for r in (1.0, 1.5, 3.0):
            samples.append(gos.glued_three_form(fam, r, math.pi / 3, t))

    for phi in samples:
        naive = np.einsum("abcdefg,iab,jcd,efg->ij", eps, phi, phi, phi)
        used = G2DifferentialGeometry(phi=phi).hitchin_bilinear()

        scale = max(1.0, float(np.max(np.abs(naive))))
        assert np.allclose(naive, used, rtol=0, atol=1e-9 * scale), (
            "the two contraction orders differ by more than machine noise: "
            "%g on a scale of %g" % (np.max(np.abs(naive - used)), scale)
        )

        naive_sym = 0.5 * (naive + naive.T)
        used_sym = 0.5 * (used + used.T)
        assert np.sign(np.linalg.det(naive_sym)) == \
               np.sign(np.linalg.det(used_sym)), (
            "the contraction order changed the SIGN of det B, which is the "
            "invariant the degenerate wall is detected by"
        )
        assert np.array_equal(
            np.sign(np.linalg.eigvalsh(naive_sym)),
            np.sign(np.linalg.eigvalsh(used_sym))), (
            "the contraction order changed the eigenvalue signs, so it changed "
            "the reported GL(7,R) orbit"
        )


def test_the_shared_levi_civita_symbol_cannot_be_mutated():
    """It is cached and shared, so a writable copy would corrupt the process."""
    from metaphysica.simulations.PM.geometry.g2_differential import (
        _levi_civita_7d,
    )

    eps = _levi_civita_7d()
    assert eps.flags.writeable is False
    with pytest.raises(ValueError):
        eps[0, 1, 2, 3, 4, 5, 6] = 99.0
    assert _levi_civita_7d() is eps, "the symbol is being rebuilt on every call"


def test_the_wall_exponent_is_one_half_not_merely_of_order_one():
    """The sqrt-t claim, pinned as an EXPONENT rather than an order-one ratio.

    The order-one test above (t a^2/r_*^2 in (0.5, 1.5) over t in [1, 100])
    tolerates any exponent p with |1 - 2p| ln(100) < ln(3) -- roughly
    p in [0.38, 0.62] -- so r_* ~ t^0.47 would pass it while the register
    says sqrt(t). This test fits the LOCAL log-log slope between successive
    sampled decades and pins the convergence that eta ~ a^2/r^2 actually
    forces: slopes approach 1/2 FROM BELOW (the subleading a^4/r^4 term only
    ever lowers the wall), monotonically, and the last measured slope sits
    within a stated margin of 1/2.

    MEASURED 2026-09-22: local slopes 0.49667 (100->300), 0.49867
    (300->1000), 0.49948 (1000->3000); final deviation from 1/2 is 5.2e-4.
    The margin below is 10x that, stated, not tuned.
    """
    ts = (100.0, 300.0, 1000.0, 3000.0)
    report = gos.wall_scaling_report(t_values=ts)
    rs = [w["r_star"] for w in report["walls"]]
    assert len(rs) == len(ts), "a wall was not found at every sampled t"

    slopes = [
        math.log(rs[i] / rs[i - 1]) / math.log(ts[i] / ts[i - 1])
        for i in range(1, len(ts))
    ]

    for slope in slopes:
        assert slope < 0.5, (
            "a local slope reached %.5f >= 1/2: the approach must be from "
            "BELOW, because the subleading a^4/r^4 term in eta only ever "
            "lowers the wall radius" % slope
        )
    assert slopes == sorted(slopes), (
        "local slopes are not monotonically increasing toward 1/2: %s -- the "
        "correction term is not dying off, so the exponent is not 1/2" % slopes
    )
    assert abs(slopes[-1] - 0.5) < 5e-3, (
        "the final local slope is %.5f, more than 5e-3 from 1/2 (measured "
        "deviation 5.2e-4, margin 10x). r_* does not scale as sqrt(t)"
        % slopes[-1]
    )
