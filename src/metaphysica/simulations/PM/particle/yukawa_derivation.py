#!/usr/bin/env python3
"""
Geometric Yukawa ansatz — the T4 / 24-cell route to the PMNS angles
===================================================================

STATUS ON THE ADOPTED MODEL (read first)
----------------------------------------
Flavour is OPEN (D-011). The internal space Y₇ -- Joyce's resolution of
T⁷/(ℤ/2)³, (b₂, b₃) = (12, 43) -- supplies no chiral sector: its singular
loci are disjoint, so it has no codimension-7 points, and a flavour
structure cannot be derived before a chiral sector exists. This module is
therefore a MODEL CONSTRUCT: a T₄ / 24-cell ansatz whose closed forms were
calibrated at the off-path seed b₃ = 24 (retired, and unreachable by
Joyce's construction).

Which b₃ the formulas consume is decided by the ``flavour_seed_coupling``
fork, read by :func:`resolve_flavour_b3`:

* ``follow_seed`` (ADOPTED) -- the live seed's b₃ (43). θ₁₃ moves to
  4.8351° (measured), far from NuFIT 6.0: the agreement quoted below was
  a property of the calibration and does not survive on the adopted seed.
* ``calibrated_24`` -- :data:`DEFAULT_B3`, the calibration constant 24,
  admitted to be a fit rather than a topological count. It stays runnable
  for costing; ``tests/test_yukawa_derivation.py`` is its regression
  contract.

Every value quoted below at b₃ = 24 describes that calibration at the
off-path seed, not the adopted model.

PHYSICS SUMMARY (the ansatz)
----------------------------
The binary tetrahedral group T₄ is the symmetry group of the 24-cell
(the regular 4-polytope with 24 octahedral cells). The ansatz projects
the 12 paired (2,0) bridges of M^{26}(24,2) onto the 24-cell's vertex
set via the G₂ spinor bundle, and takes the overlap integrals between
the three lepton-doublet generations and the neutrino mass-eigenstate
basis to be governed by:

* An amplitude  sqrt(2/3)  from the 2-out-of-3 vertex-orbit symmetry of
  T₄ on the 24-cell (Frampton-Petcov 2005; Kobayashi-Tanimoto 2018).

* A distortion parameter

      η = √2 · sin(π / b₃)

  where ``sin(π/b₃)`` is read as the half-angle of one T₄ vertex orbit
  around the central rotation axis of the 24-cell, and the ``√2`` factor
  as the octahedral unit-cell diagonal (each of the 24-cell's 24
  octahedral cells has unit edges and √2 diagonals). That reading counts
  the 24-cell's cells as b₃, so it holds only at the off-path seed
  b₃ = 24, where η = 0.184592…. It is not parameter-free: the δ_CP
  coefficients below are tuned, and 24 is the calibration point.

The PMNS angles are then:

    θ₁₃ = arcsin(sqrt(2/3) · η)                          [rad]
    δ_CP = (3π/2) · (1 − a·η·ξ + b·ξ²)  with a=0.12, b=0.05   [rad]

where ξ = cos(π / b₃) is the second b₃-dependent parameter (roadmap item
T2.4 of TIER_2_3_ROADMAP). It is the algebraic conjugate of η: while
η = √2·sin(π/b₃) carries the T₄ vertex-orbit *half-angle sine* (the
cell-diagonal-weighted overlap amplitude), ξ = cos(π/b₃) carries the
*half-angle cosine* — i.e. the in-plane projection of the same orbit onto
the bridge-pair axis. Together (η/√2, ξ) form the unit-circle pair
sin²(π/b₃)+cos²(π/b₃)=1, so ξ is closed-form in b₃ and traces through
``b3_leaf()`` exactly like η.

THE CALIBRATION AT THE OFF-PATH SEED b₃ = 24
---------------------------------------------
The first version shipped η = 0.037 as a literal (from
PossibleImprovements.txt §1). That produced θ₁₃ ≈ 1.73° (~62σ from
NuFIT 6.0 IO 8.63° ± 0.11). The closed form replaced it:

    η = √2 · sin(π / b₃)
    sin θ₁₃ = √(2/3) · √2 · sin(π/b₃) = (2/√3) · sin(π/b₃)

Calibrated at the off-path seed b₃ = 24:

    η = √2 · sin(π/24)   = 0.184592…
    ξ = cos(π/24)        = 0.991445…
    η · ξ                = 0.183013…   ( = sin(π/12)/√2 )
    ξ²                   = 0.982963…   ( = (1+cos(π/12))/2 )
    θ₁₃ = 8.6686° (NuFIT 6.0 NO 8.58 ± 0.11 → 0.81σ, within 1σ)
    δ_CP = 1.5408 π  (compared against the INVERTED-ordering best fit
           1.54π ± 0.17π → 0.005σ; the θ₁₃ anchor above is NORMAL
           ordering, so the two angles are NOT scored in a single
           ordering - against the NO best fit (~1.18π) this δ_CP is
           >2σ)

θ_13 and δ_CP each land within 1σ of their respective anchors, but in
DIFFERENT mass orderings (θ_13: NO; δ_CP: IO) - they are not a joint
single-ordering fit. Nor is the calibration parameter-free: its inputs
are the off-path seed b₃ = 24 and the two coefficients (a, b) =
(0.12, 0.05), TUNED to the δ_CP target -- the 0.12 is the inherited T₄
bridge-pair handedness-flip weight, the 0.05 the ξ² coefficient that
fixes the δ_CP curvature. At the adopted b₃ the same formulas give
θ₁₃ = 4.8351° (measured), and the documented_divergence block reports
the b₃ actually consumed.

GEOMETRIC READING OF η = √2 · sin(π / b₃)
------------------------------------------
1. ``sin(π / b₃)``: the 24-cell has 24 octahedral cells arranged with
   discrete rotational symmetry. Writing that cell count as b₃, the
   smallest angular separation between adjacent T₄ vertex orbits
   projected onto the bridge-pair plane is 2π/b₃, hence the *half-angle*
   is π/b₃, and its sine is taken as the overlap-integral kernel. The
   count belongs to the 24-cell, so the identification with b₃ held only
   at the off-path seed b₃ = 24; at the adopted b₃ the formula no longer
   describes the 24-cell.
2. ``√2``: Each of the 24-cell's 24 octahedral cells has unit-length
   edges; the diagonal connecting opposite vertices through the cell
   centre has length √2 in the unit metric. The ansatz uses it as the
   amplitude weight of the bridge-pair diagonal in the (2,0)+(2,0)
   sampler-projection inner product.

The combined factor √2 · sin(π/b₃) is the ansatz's "diagonal-weighted
vertex-orbit half-angle" of the T₄/24-cell symmetry group.

DEPENDENCY CHAIN (b₃ as the flavour fork resolves it)
-----------------------------------------------------
* η = √2 · sin(π / b₃)  — closed-form in b₃
* ξ = cos(π / b₃)       — sister parameter, closed-form in b₃
* sqrt(2/3) — T₄ orbit-decomposition amplitude
* y_e hierarchy = sqrt(2/3) · exp(−b₃ / 24); the 24 in the denominator
  is a constant calibrated at the off-path seed b₃ = 24, where the
  exponent is −1

Every EML tree leaf in this module routes through :func:`b3_leaf` (the
flavour fork's b₃ leaf), so the website's b₃ tracer reaches the b₃ the
flavour sector actually consumed as a genuine EMLPoint, not just as a
string match in a formula text.

PUBLIC API
----------
* :class:`GeometricYukawaT4` — derivation object parameterised by
  ``b3`` (default :data:`DEFAULT_B3`, the calibration constant) and
  ``eta_distortion`` (default ``None``: η = √2 · sin(π/b₃)).
* :meth:`GeometricYukawaT4.derive_pmns_angles` — returns the dict
  ``{"theta_13_deg", "delta_CP_rad", "y_e_hierarchy",
  "documented_divergence", ...}``.
* :func:`get_geometric_pmns` — module entry-point used by
  ``simulations/run_all_simulations.py``; it consumes
  :func:`resolve_flavour_b3`.
* :func:`resolve_flavour_b3` — the flavour_seed_coupling fork's b₃.

REFERENCES
----------
* PossibleImprovements.txt §1 (the original mandate, ``H:/Github/EyesOfAzrael/``)
* Frampton, Petcov "Sterile-active mixing" Phys.Lett.B (2005)
* Kobayashi, Tanimoto "T₄ / 24-cell PMNS textures" arXiv:1812.01505

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

# v25.0 EML adapter (Sprint 4 #1 — landed at
# ``simulations/core/eml_math.py``). Provides ``eml_operator_tree`` plus
# the canonical operator factories re-exported from ``eml_integration``.
try:
    from metaphysica.simulations.core.eml_tree_adapter import (
        EML_AVAILABLE,
        flavour_b3_leaf as b3_leaf,  # flavour fork decides which b3 (2026-09-22)
        eml_add,
        eml_compute,
        eml_div,
        eml_exp,
        eml_mul,
        eml_neg,
        eml_pi,
        eml_scalar,
        eml_sin,
        eml_sqrt,
        eml_sub,
        eml_operator_tree,
    )
    # arcsin lives on the eml_integration surface (not re-exported by
    # eml_math); import it directly so the EML tree can carry the actual
    # arcsin node rather than a numeric collapse. Same for eml_cos, used
    # by the Sprint T5 #1 sister-parameter ξ = cos(π / b₃).
    from metaphysica.simulations.core.eml_integration import (
        eml_arcsin,
        eml_cos,
    )
except ImportError:  # pragma: no cover — defensive fallback for early-Sprint envs
    EML_AVAILABLE = False

    class eml_operator_tree:  # type: ignore[no-redef]
        """Minimal fallback when ``eml_math`` adapter isn't on disk yet.

        Mirrors the Sprint 4 #1 contract so the Sprint 4 #2 PMNS module
        is independently testable. Replaced by the real adapter at
        import-time once Sprint 4 #1 is merged.
        """

        def __init__(self, name: str) -> None:
            self.name = name

        def register_derivation(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
            return {}

        def get_tree(self) -> Dict[str, Any]:  # pragma: no cover
            return {}


# Triple-track helpers (Arithma + EML + float). Use the canonical shared
# module ``triple_helpers`` for the Arithma façade and the eml helpers.
from metaphysica.simulations.core.triple_helpers import (
    _arithma_num,
    _arithma_add,
    _arithma_sub,
    _arithma_mul,
    _arithma_div,
    _arithma_pow,
    _arithma_neg,
    triple_kwargs,
)

# Formula dataclass — the canonical SSoT-registered triple-tracked formula.
from metaphysica.simulations.base import Formula


# ── Module constants ────────────────────────────────────────────────────────

#: The flavour ansatz's CALIBRATION CONSTANT: the b₃ its closed forms were
#: calibrated at, the off-path seed b₃ = 24 (retired; unreachable by
#: Joyce's construction). It is not the adopted b₃. The ``calibrated_24``
#: branch of ``flavour_seed_coupling`` returns it from
#: :func:`resolve_flavour_b3`; the adopted ``follow_seed`` branch ignores it
#: and consumes the live seed. It stays the constructor default of
#: :class:`GeometricYukawaT4` so the calibrated branch remains reproducible.
DEFAULT_B3: int = 24


def _eta_from_b3(b3: int) -> float:
    """Closed-form η from b₃ (the ansatz's distortion parameter).

    η = √2 · sin(π / b₃)

    At the off-path seed b₃ = 24, where the ansatz was calibrated, this
    evaluates to 0.184592… and lands θ₁₃ = arcsin(√(2/3)·η) at 8.669°,
    i.e. 0.81σ from the NuFIT 6.0 NO best fit (8.58° ± 0.11, symmetric
    1σ bound). At the adopted b₃ it gives θ₁₃ = 4.8351° (measured), so
    that agreement belongs to the calibration. See the module docstring
    for the ansatz's reading of the √2 (24-cell octahedral diagonal) and
    sin(π/b₃) (T₄ vertex-orbit half-angle).
    """
    return math.sqrt(2.0) * math.sin(math.pi / float(b3))


def _xi_from_b3(b3: int) -> float:
    """Closed-form ξ from b₃ (the T2.4 sister parameter).

    ξ = cos(π / b₃)

    Geometric reading: ξ is the algebraic conjugate of η on the
    T₄/24-cell orbit. While η = √2·sin(π/b₃) is the cell-diagonal-
    weighted *half-angle sine* (the off-axis overlap amplitude), ξ =
    cos(π/b₃) is the half-angle *cosine* — the in-plane projection of
    the same vertex orbit onto the bridge-pair principal axis. The
    pair (η/√2, ξ) satisfies sin²+cos²=1, so ξ adds no free parameter
    of its own: it is closed-form in b₃ and routes through
    ``b3_leaf()`` exactly like η. (The δ_CP coefficients that multiply
    it are tuned; see the module docstring.)

    At the off-path calibration seed b₃ = 24 this evaluates to
    cos(π/24) = 0.991445…
    """
    return math.cos(math.pi / float(b3))


def _eta_is_geometric_default(eta: float, b3: int) -> bool:
    """Return True iff ``eta`` matches the canonical √2·sin(π/b₃) value.

    Used by the structural-EML tree builder to decide whether to root
    the η subtree in :func:`b3_leaf` (the canonical SSoT path) or in a
    bare scalar (the override path used by sensitivity scans / tests).
    """
    return math.isclose(eta, _eta_from_b3(b3), rel_tol=1e-12, abs_tol=1e-15)


def _xi_is_geometric_default(xi: float, b3: int) -> bool:
    """Return True iff ``xi`` matches the canonical cos(π/b₃) value.

    Mirrors :func:`_eta_is_geometric_default` for the Sprint T5 #1
    sister parameter ξ = cos(π/b₃). Drives the structural-EML tree
    builder's choice between the b3_leaf-rooted ξ subtree and a bare
    scalar (the override path).
    """
    return math.isclose(xi, _xi_from_b3(b3), rel_tol=1e-12, abs_tol=1e-15)


#: T₄/24-cell distortion parameter η = √2 · sin(π / b₃), evaluated at the
#: calibration constant :data:`DEFAULT_B3` (the off-path seed b₃ = 24).
#: Closed-form in b₃; it replaced an earlier literal η = 0.037.
DEFAULT_ETA: float = _eta_from_b3(DEFAULT_B3)

#: Sister parameter ξ = cos(π / b₃) (TIER_2_3_ROADMAP T2.4), evaluated at
#: the calibration constant :data:`DEFAULT_B3`. Algebraic conjugate of η
#: on the T₄/24-cell orbit; routes through ``b3_leaf()`` exactly like η.
#: At the off-path calibration seed b₃ = 24, ξ = 0.991445…
DEFAULT_XI: float = _xi_from_b3(DEFAULT_B3)

#: Amplitude from the T₄ vertex-orbit decomposition on the 24-cell. The
#: 2-out-of-3 generation overlap leaves this exact factor in the ansatz.
T4_ORBIT_AMPLITUDE: float = math.sqrt(2.0 / 3.0)

#: δ_CP polynomial coefficient ``a`` in (3π/2)·(1 − a·η·ξ + b·ξ²). The
#: 0.12 value is inherited from the earlier (3π/2)(1−0.12·η) form; the
#: ansatz reads it as the T₄ phase-shift induced by the bridge-pair
#: handedness flip. Multiplying by ξ couples that phase to the
#: half-angle cosine projection.
DELTA_CP_ETA_COEF: float = 0.12

#: δ_CP polynomial coefficient ``b`` in (3π/2)·(1 − a·η·ξ + b·ξ²). TUNED:
#: 0.05 is fixed by the requirement that δ_CP land within 1σ of NuFIT 6.0
#: 1.54π while the η·ξ term contributes the inherited handedness-flip
#: correction -- it lifts δ_CP from 1.467π to 1.541π (target 1.54π) at the
#: off-path calibration seed b₃ = 24.
DELTA_CP_XI2_COEF: float = 0.05

#: NuFIT 6.0 anchor values used for the documented-divergence report.
#: These are NOT inputs to the derivation — they are the experimental
#: targets the geometric formula is benchmarked against. The σ for θ_13
#: uses the NuFIT 6.0 symmetric 1σ bound of 0.11 (an earlier 0.13
#: asymmetric-upper copy understated the deviation; the 8.54° quoted
#: in some older notes was a pre-release central value - the dataset
#: NO best fit is 8.58°). For
#: δ_CP the 1σ window is ~0.17π (asymmetric in NuFIT 6.0; the value
#: here is the symmetric proxy used for the documented-divergence
#: σ-deviation report).
NUFIT_THETA_13_DEG: float = 8.58
NUFIT_THETA_13_SIGMA: float = 0.11  # NuFIT 6.0 symmetric 1sigma (2026-08: was a 0.13 asymmetric-upper copy)
NUFIT_DELTA_CP_RAD: float = 1.54 * math.pi      # NuFIT 6.0 best fit ≈ 1.54 π
NUFIT_DELTA_CP_SIGMA_PI: float = 0.17           # NuFIT 6.0 1σ width in units of π


# ── Derivation class ────────────────────────────────────────────────────────


class GeometricYukawaT4:
    """T₄ / 24-cell ansatz for the PMNS angles θ₁₃ and δ_CP.

    A model construct, calibrated at the off-path seed b₃ = 24 (flavour
    is OPEN on the adopted model; see the module docstring). The
    amplitude ``sqrt(2/3)`` comes from the T₄ orbit decomposition on the
    24-cell, the distortion ``η = √2 · sin(π / b₃)`` is closed-form in
    b₃, and the sister parameter ``ξ = cos(π / b₃)`` is the algebraic
    conjugate of η on the same T₄/24-cell orbit. Both η and ξ route
    through ``b3_leaf()``. The δ_CP coefficients (0.12, 0.05) are tuned,
    so the construction is not parameter-free.

    Parameters
    ----------
    b3:
        The b₃ the ansatz consumes. Default :data:`DEFAULT_B3`, the
        calibration constant 24 (the off-path seed);
        :func:`get_geometric_pmns` passes :func:`resolve_flavour_b3`
        instead, which is the live seed's b₃ on the adopted branch.
    eta_distortion:
        T₄/24-cell distortion parameter. When omitted (the canonical
        case) ``η`` is computed from ``b₃`` via :func:`_eta_from_b3`
        (= √2 · sin(π/b₃) ≈ 0.184592 at the off-path calibration seed
        b₃ = 24). Callers may still override with a literal float for
        sensitivity scans or cross-validation hooks.
    xi_distortion:
        Sister T₄/24-cell distortion parameter. When omitted (the
        canonical case) ``ξ`` is computed from ``b₃`` via
        :func:`_xi_from_b3` (= cos(π/b₃) ≈ 0.991445 at the off-path
        calibration seed b₃ = 24). Callers may override for
        sensitivity scans.

    Examples
    --------
    >>> result = GeometricYukawaT4().derive_pmns_angles()
    >>> 'theta_13_deg' in result
    True
    >>> 'delta_CP_rad' in result
    True
    >>> 'y_e_hierarchy' in result
    True
    """

    __slots__ = ("b3", "eta", "xi", "_eml_tree", "_eml_handles", "_last_result")

    def __init__(
        self,
        b3: int = DEFAULT_B3,
        eta_distortion: Optional[float] = None,
        xi_distortion: Optional[float] = None,
    ) -> None:
        if int(b3) <= 0:
            raise ValueError(f"b3 must be positive, got {b3!r}")
        self.b3: int = int(b3)
        # Canonical path: η is the closed-form geometric expression
        # √2 · sin(π / b₃). Callers may still override with a literal
        # float (used by ``test_custom_eta_produces_consistent_theta_13``
        # and any sensitivity scan).
        if eta_distortion is None:
            self.eta: float = _eta_from_b3(self.b3)
        else:
            if not math.isfinite(float(eta_distortion)):
                raise ValueError(
                    f"eta_distortion must be finite, got {eta_distortion!r}"
                )
            self.eta = float(eta_distortion)
        # Sprint T5 #1 sister parameter: ξ = cos(π/b₃). Canonical path
        # mirrors η; override is supported symmetrically.
        if xi_distortion is None:
            self.xi: float = _xi_from_b3(self.b3)
        else:
            if not math.isfinite(float(xi_distortion)):
                raise ValueError(
                    f"xi_distortion must be finite, got {xi_distortion!r}"
                )
            self.xi = float(xi_distortion)
        # On-disk EML derivation registry (Sprint 4 #1 adapter).
        self._eml_tree = eml_operator_tree("T4_24cell_projection")
        # Cache of the structural EML tree nodes (built on derive call).
        self._eml_handles: Dict[str, Any] = {}
        self._last_result: Optional[Dict[str, Any]] = None

    # ── Core derivation ────────────────────────────────────────────────

    def derive_pmns_angles(self) -> Dict[str, Any]:
        """Evaluate θ₁₃, δ_CP and the y_e hierarchy from the T₄/24-cell ansatz.

        Returns
        -------
        dict
            ``{"theta_13_deg": float, "theta_13_rad": float,
            "delta_CP_rad": float, "delta_CP_pi_units": float,
            "y_e_hierarchy": float, "eta_distortion": float, "b3": int,
            "documented_divergence": {...}}``.

            ``documented_divergence`` carries the NuFIT 6.0 anchor
            comparison at the b₃ this instance consumed, so downstream
            validation can flag the ansatz as passing or in tension
            *without* silently fudging η to mask the gap. On the adopted
            seed it reports the divergence.
        """
        # ── Float pipeline (canonical numerical values) ──────────────
        amplitude = T4_ORBIT_AMPLITUDE  # sqrt(2/3) — pure topology
        sin_theta_13 = amplitude * self.eta
        # Guard the arcsin domain (|x| ≤ 1). With η < 1.225 the product
        # stays well inside; defensive clamp for any future extension.
        sin_theta_13 = max(-1.0, min(1.0, sin_theta_13))
        theta_13_rad = math.asin(sin_theta_13)
        theta_13_deg = math.degrees(theta_13_rad)

        # T2.4 form: δ_CP = (3π/2) · (1 − a·η·ξ + b·ξ²) with the sister
        # parameter ξ = cos(π/b₃) providing the second knob. The η·ξ term
        # inherits the handedness-flip weight (a = 0.12); the ξ² term
        # (b = 0.05, tuned) lifts δ_CP from 1.467π to 1.541π -- into the
        # NuFIT 6.0 1σ window at the off-path calibration seed b₃ = 24.
        delta_cp_rad = (3.0 * math.pi / 2.0) * (
            1.0
            - DELTA_CP_ETA_COEF * self.eta * self.xi
            + DELTA_CP_XI2_COEF * self.xi * self.xi
        )
        delta_cp_pi_units = delta_cp_rad / math.pi

        # y_e hierarchy = sqrt(2/3) · exp(−b₃ / 24). The 24 in the
        # denominator is a constant calibrated at the off-path seed
        # b₃ = 24, where this is sqrt(2/3) · exp(−1) ≈ 0.300.
        y_e_hierarchy = amplitude * math.exp(-self.b3 / 24.0)

        # ── EML tree registration (Sprint 4 #1 contract) ─────────────
        # The on-disk JSON entry gets a b3_traceback flag because the
        # formula text mentions ``b3`` / ``24`` (auto-detected by
        # _formula_has_b3_traceback in the adapter).
        self._eml_tree.register_derivation(
            param="theta_13_deg",
            formula="arcsin(sqrt(2/3) * sqrt(2) * sin(pi/b3)) * 180/pi  | b3-rooted",
            value=theta_13_deg,
        )
        self._eml_tree.register_derivation(
            param="theta_13_rad",
            formula="arcsin(sqrt(2/3) * sqrt(2) * sin(pi/b3))  | b3-rooted",
            value=theta_13_rad,
        )
        self._eml_tree.register_derivation(
            param="delta_CP_rad",
            formula=(
                "(3*pi/2) * (1 - 0.12 * sqrt(2)*sin(pi/b3) * cos(pi/b3) "
                "+ 0.05 * cos(pi/b3)^2)  | T4 phase, eta + xi sister, b3-rooted"
            ),
            value=delta_cp_rad,
        )
        self._eml_tree.register_derivation(
            param="xi_distortion",
            formula="cos(pi / b3)  | T4 vertex-orbit half-angle cosine, b3-rooted",
            value=self.xi,
        )
        self._eml_tree.register_derivation(
            param="y_e_hierarchy",
            formula="sqrt(2/3) * exp(-b3 / 24)  | T4 orbit amplitude · b3 ratio",
            value=y_e_hierarchy,
        )

        # ── Structural EML tree (b₃ leaf as a real EMLPoint) ─────────
        eml_theta_13_value: Optional[float] = None
        eml_delta_cp_value: Optional[float] = None
        eml_y_e_value: Optional[float] = None
        if EML_AVAILABLE:
            try:
                (
                    eml_theta_13_value,
                    eml_delta_cp_value,
                    eml_y_e_value,
                ) = self._build_structural_tree()
            except Exception:  # pragma: no cover — EML soft-fail
                pass

        # ── Documented divergence vs NuFIT 6.0 ───────────────────────
        theta_13_sigma_deviation = abs(
            theta_13_deg - NUFIT_THETA_13_DEG
        ) / NUFIT_THETA_13_SIGMA
        delta_cp_pi_offset = abs(
            delta_cp_pi_units - (NUFIT_DELTA_CP_RAD / math.pi)
        )
        delta_cp_sigma_deviation = delta_cp_pi_offset / NUFIT_DELTA_CP_SIGMA_PI
        divergence = {
            "nufit_theta_13_deg": NUFIT_THETA_13_DEG,
            "nufit_theta_13_sigma": NUFIT_THETA_13_SIGMA,
            "theta_13_sigma_deviation": float(theta_13_sigma_deviation),
            "theta_13_within_1sigma": bool(theta_13_sigma_deviation < 1.0),
            "nufit_delta_CP_rad": NUFIT_DELTA_CP_RAD,
            "nufit_delta_CP_pi_units": NUFIT_DELTA_CP_RAD / math.pi,
            "nufit_delta_CP_sigma_pi": NUFIT_DELTA_CP_SIGMA_PI,
            "delta_CP_pi_offset": float(delta_cp_pi_offset),
            "delta_CP_sigma_deviation": float(delta_cp_sigma_deviation),
            "delta_CP_within_1sigma": bool(delta_cp_sigma_deviation < 1.0),
            "note": (
                "Flavour ansatz (flavour is OPEN on the adopted model), "
                "TIER_2_3_ROADMAP T2.4 two-parameter form: "
                "δ_CP = (3π/2)(1 − 0.12·η·ξ + 0.05·ξ²), with "
                "η = √2·sin(π/b₃) and the sister parameter ξ = cos(π/b₃), "
                "the algebraic conjugate of η on the T₄/24-cell vertex "
                "orbit; ξ traces through b3_leaf() exactly like η. "
                "Calibrated at the off-path seed b₃ = 24: θ₁₃ = 8.669° "
                "(NuFIT 6.0 NO 8.58 ± 0.11 → 0.81σ) and δ_CP = 1.541π "
                "(IO best fit 1.54π ± 0.17π → 0.005σ) -- each within 1σ "
                "of its own anchor, but in DIFFERENT mass orderings, with "
                "(a, b) = (0.12, 0.05) tuned to the δ_CP target. The σ "
                "fields of this block score the b₃ this run consumed "
                "(%d, giving θ₁₃ = %.4f°); on the adopted seed the "
                "calibration's agreement does not survive (fork "
                "flavour_seed_coupling)." % (self.b3, theta_13_deg)
            ),
        }

        self._last_result = {
            "theta_13_deg": float(theta_13_deg),
            "theta_13_rad": float(theta_13_rad),
            "delta_CP_rad": float(delta_cp_rad),
            "delta_CP_pi_units": float(delta_cp_pi_units),
            "y_e_hierarchy": float(y_e_hierarchy),
            "eta_distortion": float(self.eta),
            "xi_distortion": float(self.xi),
            "b3": int(self.b3),
            "eml_theta_13_rad": eml_theta_13_value,
            "eml_delta_CP_rad": eml_delta_cp_value,
            "eml_y_e_hierarchy": eml_y_e_value,
            "documented_divergence": divergence,
            "classification": "GEOMETRIC_T4_24CELL",
        }
        return self._last_result

    # ── Structural EML tree (b₃ leaf as a real node) ───────────────────

    def _build_structural_tree(self) -> tuple:
        """Build the EML operator trees rooted at :func:`b3_leaf`.

        Returns
        -------
        tuple
            ``(theta_13_rad_value, delta_CP_rad_value, y_e_hierarchy_value)``
            — the numerically evaluated tensions of the structural trees.

            These cross-check the float-pipeline values: any disagreement
            between the structural tree's ``eml_compute(...)`` and the
            ``math.*`` pipeline would indicate an EML operator bug.
        """
        # b₃ leaf — the traceback root. It is the flavour fork's leaf
        # (flavour_b3_leaf -> resolve_flavour_b3): the live seed's b₃ on
        # the adopted follow_seed branch, DEFAULT_B3 on calibrated_24.
        b3_pt = b3_leaf()

        # T₄ orbit amplitude: sqrt(2/3)
        two = eml_scalar(2.0)
        three = eml_scalar(3.0)
        amp_tree = eml_sqrt(eml_div(two, three))

        # η = √2 · sin(π / b₃) — closed-form, b₃-rooted (Sprint 6 #1).
        # When ``self.eta`` was set via a non-default override (sensitivity
        # scan), we still build the structural tree on the b₃ leaf so the
        # b₃ tracer hits a real EMLPoint; the cross-check value will then
        # differ from the override (that's the intended audit signal).
        eta_tree = eml_mul(
            eml_sqrt(two), eml_sin(eml_div(eml_pi(), b3_pt))
        )
        # eta_pt: the scalar pin used by the float pipeline; downstream
        # arcsin/CP-phase trees consume eta_tree for geometric provenance,
        # but the Formula.value leg is still self.eta (which is _eta_from_b3
        # in the canonical path, and the override otherwise).
        eta_pt = eta_tree if _eta_is_geometric_default(self.eta, self.b3) else eml_scalar(self.eta)

        # θ₁₃ = arcsin(sqrt(2/3) · η)
        sin_arg = eml_mul(amp_tree, eta_pt)
        theta_13_tree = eml_arcsin(sin_arg)

        # ξ = cos(π / b₃) — Sprint T5 #1 sister parameter, b₃-rooted via
        # the same b3_leaf used for η. ξ is the algebraic conjugate of
        # η/√2 on the T₄/24-cell vertex orbit.
        xi_tree = eml_cos(eml_div(eml_pi(), b3_pt))
        xi_pt = xi_tree if _xi_is_geometric_default(self.xi, self.b3) else eml_scalar(self.xi)

        # δ_CP = (3π/2) · (1 − a·η·ξ + b·ξ²)   [Sprint T5 #1 form]
        three_pi_half = eml_div(eml_mul(eml_scalar(3.0), eml_pi()), two)
        eta_xi = eml_mul(eta_pt, xi_pt)
        coef_eta_xi = eml_mul(eml_scalar(DELTA_CP_ETA_COEF), eta_xi)
        xi_squared = eml_mul(xi_pt, xi_pt)
        coef_xi2 = eml_mul(eml_scalar(DELTA_CP_XI2_COEF), xi_squared)
        bracket = eml_add(eml_sub(eml_scalar(1.0), coef_eta_xi), coef_xi2)
        delta_cp_tree = eml_mul(three_pi_half, bracket)

        # y_e hierarchy = sqrt(2/3) · exp(−b₃ / 24)
        # b₃/24 with b₃ as a *real* labelled leaf so the b₃ trace walker
        # actually lands on the SSoT node.
        b3_over_24 = eml_div(b3_pt, eml_scalar(24.0))
        y_e_tree = eml_mul(amp_tree, eml_exp(eml_neg(b3_over_24)))

        # Cache for downstream consumers (b₃ tracer, formula widget).
        self._eml_handles = {
            "b3_leaf": b3_pt,
            "eta_distortion": eta_pt,
            "xi_distortion": xi_pt,
            "theta_13_rad_tree": theta_13_tree,
            "delta_CP_rad_tree": delta_cp_tree,
            "y_e_hierarchy_tree": y_e_tree,
            "amplitude_tree": amp_tree,
        }

        return (
            float(eml_compute(theta_13_tree)),
            float(eml_compute(delta_cp_tree)),
            float(eml_compute(y_e_tree)),
        )

    # ── Accessors ──────────────────────────────────────────────────────

    @property
    def eml_handles(self) -> Dict[str, Any]:
        """Return the cached structural EML tree handles.

        Populated by :meth:`derive_pmns_angles` (via
        :meth:`_build_structural_tree`). Keys: ``b3_leaf``,
        ``eta_distortion``, ``xi_distortion``, ``theta_13_rad_tree``,
        ``delta_CP_rad_tree``, ``y_e_hierarchy_tree``, ``amplitude_tree``.
        """
        return dict(self._eml_handles)

    @property
    def last_result(self) -> Optional[Dict[str, Any]]:
        """Return the dict produced by the most recent
        :meth:`derive_pmns_angles` call (or ``None`` if never called)."""
        return self._last_result

    # ── Triple-tracked formula publication ─────────────────────────────

    def get_formulas(self) -> List[Formula]:
        """Return the triple-tracked Formula registrations for this module.

        Each formula carries:
        * ``arithma`` — Arithma Expression (or stub) cross-check leg
        * ``eml`` — EMLPoint structural tree leg
        * ``value`` — canonical Python float leg

        The :func:`triple_assert` validator in
        :mod:`metaphysica.simulations.core.triple_validator` runs on
        every formula at registration time and halts the build on
        disagreement between the three legs.
        """
        # Ensure we have current results + structural EML handles.
        if self._last_result is None:
            self.derive_pmns_angles()

        theta_13_rad = self._last_result["theta_13_rad"]
        delta_cp_rad = self._last_result["delta_CP_rad"]
        y_e_hier = self._last_result["y_e_hierarchy"]

        # Structural EML legs (fall back to scalar leaves if EML absent).
        if self._eml_handles:
            eml_theta_13 = self._eml_handles["theta_13_rad_tree"]
            eml_delta_cp = self._eml_handles["delta_CP_rad_tree"]
            eml_y_e = self._eml_handles["y_e_hierarchy_tree"]
        else:  # pragma: no cover — EML unavailable
            eml_theta_13 = eml_scalar(theta_13_rad) if EML_AVAILABLE else None
            eml_delta_cp = eml_scalar(delta_cp_rad) if EML_AVAILABLE else None
            eml_y_e = eml_scalar(y_e_hier) if EML_AVAILABLE else None

        # Arithma legs — symbolic AST when the Rust wheel is loaded,
        # stub carrying the float otherwise. The stub still classifies
        # the formula as TRIPLE in audit_formulas.
        eta_a = _arithma_num(self.eta)
        xi_a = _arithma_num(self.xi)
        amp_a = _arithma_num(T4_ORBIT_AMPLITUDE)
        coef_a = _arithma_num(DELTA_CP_ETA_COEF)
        coef_xi2_a = _arithma_num(DELTA_CP_XI2_COEF)
        pi_a = _arithma_num(math.pi)
        # θ₁₃ as a number leg (arcsin not exposed on the Arithma stub
        # façade; the structural EML tree carries the symbolic arcsin).
        arithma_theta_13 = _arithma_num(theta_13_rad)
        # δ_CP = (3π/2) · (1 − 0.12·η·ξ + 0.05·ξ²)   [Sprint T5 #1]
        three_pi_half_a = _arithma_div(
            _arithma_mul(_arithma_num(3.0), pi_a), _arithma_num(2.0)
        )
        eta_xi_a = _arithma_mul(eta_a, xi_a)
        coef_eta_xi_a = _arithma_mul(coef_a, eta_xi_a)
        xi_sq_a = _arithma_mul(xi_a, xi_a)
        coef_xi_sq_a = _arithma_mul(coef_xi2_a, xi_sq_a)
        bracket_a = _arithma_add(
            _arithma_sub(_arithma_num(1.0), coef_eta_xi_a),
            coef_xi_sq_a,
        )
        arithma_delta_cp = _arithma_mul(three_pi_half_a, bracket_a)
        # y_e = sqrt(2/3) · exp(−b₃/24) — as a number leg (exp/neg/div
        # via Arithma stubs reduce to the float result via .evaluate()).
        arithma_y_e = _arithma_num(y_e_hier)

        return [
            Formula(
                id="pmns-theta-13-geometric",
                label="(5.4.1)",
                latex=(
                    r"\theta_{13} = \arcsin\!\Bigl(\sqrt{2/3}\,"
                    r"\sqrt{2}\,\sin(\pi / b_3)\Bigr)"
                ),
                plain_text="theta_13 = arcsin(sqrt(2/3) * sqrt(2) * sin(pi/b3))",
                category="GEOMETRIC",
                description=(
                    "PMNS reactor mixing angle from a T₄ / 24-cell spinor-"
                    "overlap ansatz -- a model construct, since flavour is "
                    "OPEN on the adopted model (Y₇ supplies no chiral "
                    "sector). Amplitude sqrt(2/3) is the T₄ orbit "
                    "decomposition factor; eta = sqrt(2)*sin(pi/b3) is the "
                    "closed-form distortion: sqrt(2) is the 24-cell "
                    "octahedral diagonal, sin(pi/b3) the T₄ vertex-orbit "
                    "half-angle. Calibrated at the off-path seed b₃ = 24; "
                    "at the adopted b₃ the NuFIT agreement does not "
                    "survive (fork flavour_seed_coupling)."
                ),
                eml_tree_str=(
                    "ops.arcsin(ops.mul(ops.sqrt(ops.div(2, 3)), "
                    "ops.mul(ops.sqrt(2), ops.sin(ops.div(pi, b3)))))"
                ),
                eml_description=(
                    "theta_13 = arcsin(sqrt(2/3) * sqrt(2) * sin(pi/b3)), "
                    "with b3 resolved by the flavour_seed_coupling fork: "
                    "the live seed's b3 on the adopted follow_seed branch, "
                    "the calibration constant 24 (the off-path seed) on "
                    "calibrated_24. Every b3 leaf traces to b3_leaf()."
                ),
                arithma=arithma_theta_13,
                eml=eml_theta_13,
                value=float(theta_13_rad),
                triple_env={"b3": 24.0, "eta": self.eta, "xi": self.xi},
                triple_rel=1e-9,
            ),
            Formula(
                id="pmns-delta-cp-geometric",
                label="(5.4.2)",
                latex=(
                    r"\delta_{CP} = \frac{3\pi}{2}\,"
                    r"\Bigl(1 - 0.12\,\eta\,\xi + 0.05\,\xi^{2}\Bigr),"
                    r"\;\eta = \sqrt{2}\,\sin(\pi/b_3),"
                    r"\;\xi = \cos(\pi/b_3)"
                ),
                plain_text=(
                    "delta_CP = (3*pi/2) * (1 - 0.12 * eta * xi + 0.05 * xi^2)"
                    "  with eta = sqrt(2)*sin(pi/b3), xi = cos(pi/b3)"
                ),
                category="GEOMETRIC",
                description=(
                    "PMNS Dirac CP phase from the T₄ bridge-pair "
                    "handedness-flip ansatz with the sister parameter ξ = "
                    "cos(π/b₃) (a model construct; flavour is OPEN on the "
                    "adopted model). (3π/2) is the maximal-CP-violation "
                    "reference; the −0.12·η·ξ term carries the inherited "
                    "handedness-flip weight, coupled to the half-angle "
                    "cosine projection ξ; the +0.05·ξ² term is the "
                    "ξ-curvature correction. Both coefficients were tuned "
                    "so δ_CP lands in the NuFIT 6.0 1σ window (≈ 1.541π vs "
                    "the IO best fit 1.54π) at the off-path seed b₃ = 24, "
                    "so the form is calibrated, not parameter-free. Both "
                    "η and ξ trace through b3_leaf()."
                ),
                eml_tree_str=(
                    "ops.mul(ops.div(ops.mul(3, pi), 2), "
                    "ops.add(ops.sub(1, ops.mul(0.12, ops.mul("
                    "ops.mul(ops.sqrt(2), ops.sin(ops.div(pi, b3))), "
                    "ops.cos(ops.div(pi, b3))))), "
                    "ops.mul(0.05, ops.pow(ops.cos(ops.div(pi, b3)), 2))))"
                ),
                eml_description=(
                    "delta_CP = (3*pi/2) * (1 - 0.12*eta*xi + 0.05*xi^2): "
                    "the two-parameter form with sister ξ = cos(π/b₃). "
                    "Both η and ξ read b₃ via b3_leaf(), which the "
                    "flavour_seed_coupling fork resolves (the live seed on "
                    "the adopted branch; the calibration constant 24, the "
                    "off-path seed, on calibrated_24)."
                ),
                arithma=arithma_delta_cp,
                eml=eml_delta_cp,
                value=float(delta_cp_rad),
                triple_env={"b3": 24.0, "eta": self.eta, "xi": self.xi},
                triple_rel=1e-9,
            ),
            Formula(
                id="yukawa-e-hierarchy-geometric",
                label="(5.4.3)",
                latex=(
                    r"y_e = \sqrt{2/3}\,\exp\!\bigl(-b_3 / 24\bigr)"
                ),
                plain_text="y_e_hierarchy = sqrt(2/3) * exp(-b_3 / 24)",
                category="GEOMETRIC",
                description=(
                    "Electron-Yukawa hierarchy seed of the T₄ ansatz: the "
                    "orbit amplitude times the b₃/24 exponential damping "
                    "(a model construct; flavour is OPEN on the adopted "
                    "model). The 24 in the denominator is a constant "
                    "calibrated at the off-path seed b₃ = 24, where this "
                    "evaluates to sqrt(2/3) / e."
                ),
                eml_tree_str=(
                    "ops.mul(ops.sqrt(ops.div(2, 3)), "
                    "ops.exp(ops.neg(ops.div(b3, 24))))"
                ),
                eml_description=(
                    "y_e = sqrt(2/3) * exp(-b3/24): the T4 amplitude "
                    "factor weighted by the b3 damping. The b3 leaf is a "
                    "real EMLPoint via b3_leaf(), resolved by the "
                    "flavour_seed_coupling fork; the 24 is the off-path "
                    "calibration constant."
                ),
                arithma=arithma_y_e,
                eml=eml_y_e,
                value=float(y_e_hier),
                triple_env={"b3": 24.0, "eta": self.eta, "xi": self.xi},
                triple_rel=1e-9,
            ),
        ]


# ── Module entry point ──────────────────────────────────────────────────────


def get_geometric_pmns() -> Dict[str, Any]:
    """Module entry point used by ``simulations/run_all_simulations.py``.

    Returns the dict produced by
    :meth:`GeometricYukawaT4.derive_pmns_angles` at
    ``b3 = resolve_flavour_b3()``, with ``eta_distortion = None``
    (η = √2·sin(π/b₃)) and ``xi_distortion = None`` (ξ = cos(π/b₃)). The
    dict carries ``theta_13_deg``, ``delta_CP_rad``, ``y_e_hierarchy``,
    the structural EML cross-checks, and the ``documented_divergence``
    block against NuFIT 6.0. Flavour is OPEN on the adopted model; this is
    an ansatz calibrated at the off-path seed b₃ = 24.

    FLAVOUR SEED COUPLING (fork, 2026-09-22): the formula TEXT claims b_3
    ("theta_13 = arcsin(sqrt(2/3) * sqrt(2) * sin(pi/b3))"), so under the
    b3_seed adoption the entry point resolves which b_3 the flavour sector
    actually consumes:

      follow_seed (adopted)  b_3 from the live seed. On seed_43_joyce this
                             gives theta_13 = 4.8351 deg (measured) -- far
                             off NuFIT -- which is the honest state of a
                             24-calibrated ansatz whose formula claims a
                             topological origin. The divergence publishes.
      calibrated_24          the calibration as it was: the off-path seed
                             b_3 = 24 in the flavour formulas regardless of
                             the seed, i.e. the 24 is admitted to be a
                             CALIBRATED constant wearing b_3's name.
                             Runnable for costing.

    The calibrated_24 branch, and only it, reproduces the original
    agreement: ``documented_divergence.theta_13_within_1sigma`` AND
    ``documented_divergence.delta_CP_within_1sigma`` are BOTH ``True``
    there (θ₁₃ = 8.6686°, 0.805σ from NuFIT 6.0 8.58 ± 0.11; δ_CP =
    1.541π, 0.005σ from the IO best fit 1.54π ± 0.17π). That is a
    calibrated ansatz compared with a measurement, not a derivation.
    ``particle.theta_13_deg`` is a different object from
    ``geometry.theta_13`` = 8.54, which is a hardcoded restatement of a
    pre-release NuFIT central value (status MEASURED). The older
    "0.99 sigma from 8.54 +- 0.13" figure used both a superseded central
    value and a superseded asymmetric-upper sigma; it is withdrawn.
    """
    return GeometricYukawaT4(b3=resolve_flavour_b3()).derive_pmns_angles()


def resolve_flavour_b3() -> int:
    """Which b_3 the flavour sector consumes, per the flavour_seed_coupling fork."""
    import os

    branch = os.environ.get("METAPHYSICA_VARIANT_FLAVOUR_SEED_COUPLING", "")
    if branch not in ("follow_seed", "calibrated_24"):
        try:
            from metaphysica.simulations.core.variants import resolve

            branch = resolve("flavour_seed_coupling")
        except Exception:                  # import cycle only
            branch = "follow_seed"
    if branch == "calibrated_24":
        return DEFAULT_B3
    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path,
        seed_values,
    )

    return seed_values(resolve_path())[0]


__all__ = [
    "GeometricYukawaT4",
    "get_geometric_pmns",
    "resolve_flavour_b3",
    "DEFAULT_B3",
    "DEFAULT_ETA",
    "DEFAULT_XI",
    "T4_ORBIT_AMPLITUDE",
    "DELTA_CP_ETA_COEF",
    "DELTA_CP_XI2_COEF",
    "NUFIT_THETA_13_DEG",
    "NUFIT_THETA_13_SIGMA",
    "NUFIT_DELTA_CP_RAD",
    "NUFIT_DELTA_CP_SIGMA_PI",
]
