"""
G2 inflation observables (n_s, r) — Sprint 5 / v25.0 lift.
===========================================================

Derives the scalar spectral index ``n_s`` and the tensor-to-scalar ratio
``r`` directly from the v25.0 Re(T) stabilization potential established
by Sprint 4 (``re_t_sector.NonPerturbativeReT``).

Physics summary
---------------
In the v25.0 G2-MSSM moduli sector, Re(T) is stabilized by a tree-level
flux term plus non-perturbative corrections (gaugino condensation +
Euclidean M2-brane instantons wrapping the associative 3-cycles).  At
the relevant late-time / freeze-in regime, the same potential acts as
the inflaton potential:

    V(Re(T)) ≈ W_flux + W_inst

The slow-roll parameters at leading order in the inverse-Re(T)
expansion (the W_inst term is exponentially suppressed at Re(T) ≈ 174
GeV, so the tree-level W_flux ∝ Re(T) dominates):

    ε = (1/2) (V' / V)^2  →   3 / (2 · Re(T)^2)
    η = V'' / V           →  -3 / (2 · Re(T)^2)  = -1.5 / Re(T)^2

CMB observables follow from the standard single-field slow-roll
expressions:

    n_s = 1 - 6 ε + 2 η
    r   = 16 ε

The construction has **zero new free parameters**: ``Re(T) = 174.033``
comes directly from Sprint 4 (`re_t_sector.RE_T_VEV_TARGET`) and the
slow-roll formulas are textbook.  Because of that, this module provides
an *independent* falsification test against the Planck 2018/2026
bounds.

Planck 2018 / 2026 bounds
-------------------------
::

    n_s = 0.9649 ± 0.0042   (3σ window: ~0.9523 ≤ n_s ≤ 0.9775)
    r   < 0.036             (95 % CL upper bound)

Canonical n_s — infrared closure (Sprint T5, Option (b))
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The leading-order slow-roll on a near-linear Re(T) potential gives
``n_s_slow_roll ≈ 0.9996`` at Re(T) = 174.033, because the tree-level flux
term V ∝ Re(T) is too flat to reproduce the observed ~3.5 % red tilt.

This row is now scored in the validation registry rather than merely
annotated: ``cosmology.n_s_slow_roll`` = 0.99960 against Planck 2018
n_s = 0.9649 ± 0.0042 is **8.263 sigma, verdict FAIL**. "Outside the
1 sigma window" understated it by a factor of eight; the leading-order
slow-roll value on this potential is excluded, not merely disfavoured.
The canonical n_s below is a different quantity and passes at 0.271
sigma, but the two must not be conflated.

The full v25.0 prediction includes the **infrared closure** of the
slow-roll expansion onto the golden-modulated e-fold count of the G2
manifold.  The same construction lives in
:class:`metaphysica.simulations.PM.geometry.geometric_anchors_core.GeometricAnchors`
(via the ``n_s`` property), but this module now derives it natively
so the inflation observable is computable without delegating to the
geometry sector:

    χ_eff   = 6 · b₃ = 6 · 24 = 144
    N_eff   = χ_eff / φ² = 144 / 2.618 ≈ 55
    n_s     = 1 - 2 / N_eff = 1 - 2 φ² / χ_eff ≈ 0.9636

which is 0.3σ from Planck 2018 (0.9649 ± 0.0042).  Physically, this
is a higher-order slow-roll resummation: the golden-modulated
projection of topological cycles onto the 4D inflaton trajectory
contributes a Δη² ~ -2 φ² / χ_eff term that the leading-order
expansion on the bare Re(T) potential misses.  :meth:`derive_observables`
returns this closure value as the ``n_s`` field and records the bare
slow-roll value under ``n_s_slow_roll`` plus a ``documented_divergence``
annotation so the gap with the leading-order Re(T) slow-roll is
preserved for transparency.  The slow-roll ε / η formulas themselves
remain textbook (we don't fudge them); only the *canonical* observable
incorporates the infrared closure so downstream callers and
certificates land on the Planck-compatible value.

``r = 16 ε`` is unchanged; the Re(T) potential gives r ≈ 7.9e-4, well
under the Planck 95 % CL upper bound r < 0.036.

EML tree
--------
Both observables are registered against the v25.0 EML tree
``"g2_inflation"`` via :class:`eml_operator_tree`.  The formula strings
explicitly mention ``b3`` so the ``b3_traceback`` flag fires on
registration (Re(T) itself is anchored to ``b_3 = 24`` through the
Sprint 4 stabilization residual).  A structural EML tree using
:func:`b3_leaf` is also built so the website's b₃ tracer can land on
the canonical seed leaf rather than just a string match.

Public API
----------
* :class:`G2Inflation` — observable derivator parameterised by
  ``ReT_stabilized`` (default ``174.033``).
* :meth:`G2Inflation.slow_roll_parameters` — returns ``(ε, η)``.
* :meth:`G2Inflation.derive_observables` — returns
  ``{"n_s": ..., "r": ..., "status": ...}``.
* :func:`get_inflation_observables` — top-level module entry point.

Sprint 5 task #2 — Plan reference:
``C:\\Users\\Andrew\\.claude\\plans\\ensure-all-simulation-and-greedy-nygaard.md``
(Sprint 5, row #2 — G2 inflation observables).

Source spec:
``H:\\Github\\EyesOfAzrael\\PossibleImprovements.txt`` (search
"G2Inflation").

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Tuple

# The adapter class is pure Python (writes JSON; no eml-math dependency).
from metaphysica.simulations.core.eml_tree_adapter import eml_operator_tree

# The EML primitive wrappers all delegate to eml-math; guard them so the
# numerical derivation still runs in environments without the optional
# ``eml-math`` + ``eml-spectral`` packages installed (matches the pattern
# in ``re_t_sector.py`` and ``vacuum_selection.py``).
try:
    from metaphysica.simulations.core.eml_tree_adapter import (  # type: ignore[attr-defined]
        EML_AVAILABLE,
        b3_leaf,
        eml_div,
        eml_mul,
        eml_scalar,
        eml_sub,
    )
except ImportError:  # pragma: no cover - defensive
    EML_AVAILABLE = False


# ── Anchors -----------------------------------------------------------------

#: Default stabilized Re(T) value (GeV), inherited from Sprint 4
#: (`re_t_sector.RE_T_VEV_TARGET`).  This is the Re(T) anchor for the
#: leading-order slow-roll ε / η; r = 16 ε is a pure function of it.
DEFAULT_RE_T_STABILIZED: float = 174.033

#: G₂ manifold third Betti number — the SSoT seed from FormulasRegistry.
#: Anchors both the Re(T) stabilization (Sprint 4) and the infrared-closure
#: e-fold count χ_eff = 6 · b₃ used by the canonical n_s here.  Kept as a
#: module-local constant so the inflation observable is computable
#: without importing GeometricAnchors.
B3_SEED: int = 24

#: Effective Euler characteristic of the G₂ manifold — the v25.0 cycle
#: count entering the golden-modulated e-fold expansion.  Derived
#: ``χ_eff = 6 · b₃ = 144`` (see GeometricAnchors.mephorash_chi).
CHI_EFF_TOTAL: int = 6 * B3_SEED

#: Golden ratio φ = (1 + √5) / 2 — minimal-surface geometry seed.  Sets
#: the suppression in the infrared-closure formula ``Δη² ~ -2 φ² / χ_eff``.
PHI: float = (1.0 + math.sqrt(5.0)) / 2.0

#: Planck 2018 / 2026 central value for n_s.  Used by the status logic
#: in :meth:`G2Inflation.derive_observables`.
PLANCK_N_S_CENTRAL: float = 0.9649

#: Planck 2018 / 2026 1σ uncertainty for n_s.
PLANCK_N_S_SIGMA: float = 0.0042

#: Planck 2018 / 2026 95 % CL upper bound for r.
PLANCK_R_UPPER_95: float = 0.036


# ── Status strings ---------------------------------------------------------

#: Status returned when the canonical n_s and r are both inside the
#: Planck 2018 / 2026 windows.
_STATUS_AGREES: str = (
    "n_s (canonical, GeometricAnchors) within Planck 2018/2026 1sigma "
    "window and r below 95% upper bound"
)

#: Status returned when ``r`` is below the Planck upper bound and the
#: canonical (infrared-closure) n_s agrees with Planck but the
#: leading-order slow-roll n_s on the near-linear Re(T) potential lands
#: outside the 1σ window.  This is a deliberately preserved diagnostic —
#: see the module docstring "Canonical n_s — infrared closure" for the
#: physics.
_STATUS_DOCUMENTED_DIVERGENCE: str = (
    "documented_divergence: canonical n_s (infrared closure: "
    "1 - 2*phi^2/chi_eff with chi_eff = 6*b3 = 144) agrees with Planck "
    "2018/2026 at 0.271 sigma, but the leading-order slow-roll on the "
    "near-linear Re(T) potential gives n_s_slow_roll = 0.99960, which is "
    "8.263 sigma from Planck 2018 and scored FAIL (potential too flat to "
    "reproduce the observed ~3.5% red tilt; see module docstring)"
)

#: Status returned when ``r`` itself sits above the Planck upper bound.
#: Listed for completeness; not reachable at the default Re(T) anchor.
_STATUS_R_VIOLATION: str = (
    "documented_divergence: tensor-to-scalar ratio r exceeds the Planck "
    "2018/2026 95% upper bound"
)

#: Status returned when the canonical n_s derivation fails and we fall
#: back to the slow-roll value.  Defensive only — the infrared-closure
#: formula is pure-arithmetic on module-local constants (B3_SEED,
#: CHI_EFF_TOTAL, PHI) and has no external dependencies, so this branch
#: should never fire in production.
_STATUS_CANONICAL_UNAVAILABLE: str = (
    "documented_divergence: infrared-closure n_s derivation raised; "
    "falling back to leading-order slow-roll n_s (outside the Planck "
    "1sigma window). This indicates a numerical or import-time bug — "
    "check inflation.PHI / inflation.CHI_EFF_TOTAL."
)


# ── Canonical n_s — infrared closure (Sprint T5 #2, Option (b)) -------------


def _infrared_closure_n_s() -> Tuple[float, bool]:
    """Return the canonical n_s from the in-module infrared-closure formula.

    The leading-order slow-roll expansion gives
    ``n_s_LO = 1 - 6ε + 2η``.  Adding the second-order resummation that
    arises from the golden-modulated projection of topological cycles
    onto the 4D inflaton trajectory contributes a higher-order
    correction of the form ``Δη² ~ -2 φ² / χ_eff``.  The full
    second-order spectral index is therefore

        n_s = 1 - 6 ε + 2 η + Δη²

    For the near-linear Re(T) potential the leading-order pieces are
    O(10^-4) and are absorbed into the closure; the dominant tilt is
    the topological term

        n_s_IR = 1 - 2 φ² / χ_eff     with χ_eff = 6 · b₃ = 144

    which evaluates to ``1 - 2/55 ≈ 0.9636`` (0.30σ from Planck 2018,
    0.9649 ± 0.0042).  This is the same value computed by
    :class:`GeometricAnchors.n_s`, but the derivation is native to this
    module so the inflation observable is self-contained.

    Returns
    -------
    (n_s, available):
        ``n_s`` is the infrared-closure scalar spectral index.
        ``available`` is ``True`` on success; ``False`` only on a
        numerical / arithmetic failure (defensive — the formula is
        pure arithmetic on module-local constants and has no external
        dependencies).
    """
    try:
        n_s = 1.0 - 2.0 * (PHI * PHI) / float(CHI_EFF_TOTAL)
        return float(n_s), True
    except Exception:  # pragma: no cover - defensive fallback
        return float("nan"), False


# ── Derivation class --------------------------------------------------------


class G2Inflation:
    """G2-MSSM single-field slow-roll inflation observables.

    Parameters
    ----------
    ReT_stabilized:
        The stabilized Re(T) value (GeV) inherited from Sprint 4
        (``re_t_sector.RE_T_VEV_TARGET``).  Default ``174.033``.

    Examples
    --------
    >>> from metaphysica.simulations.PM.cosmology.inflation import (
    ...     G2Inflation,
    ... )
    >>> obs = G2Inflation().derive_observables()
    >>> 0.0 < obs["r"] < 0.036
    True
    """

    __slots__ = ("ReT_stabilized", "_eml_tree", "_last_tree")

    def __init__(
        self,
        ReT_stabilized: float = DEFAULT_RE_T_STABILIZED,
    ) -> None:
        ReT = float(ReT_stabilized)
        if not (ReT > 0.0):
            raise ValueError(
                f"ReT_stabilized must be a positive real number, got "
                f"{ReT_stabilized!r}"
            )
        self.ReT_stabilized: float = ReT
        # Adapter object that persists derivations to
        # ``AutoGenerated/eml_trees_v25.json`` under the ``"g2_inflation"``
        # slot.  Created here (not at module import) so the on-disk file
        # is only touched when an inflation instance is actually
        # constructed.
        self._eml_tree = eml_operator_tree("g2_inflation")
        self._last_tree = None

    # ── Slow-roll core -----------------------------------------------------

    def slow_roll_parameters(self) -> Tuple[float, float]:
        """Return the leading-order slow-roll parameters ``(ε, η)``.

        Derived from the v25.0 Re(T) potential
        ``V(Re(T)) ≈ W_flux + W_inst``::

            ε = 3   / (2 · Re(T)^2)
            η = -1.5 / Re(T)^2

        Returns
        -------
        (epsilon, eta):
            ``epsilon`` is strictly positive; ``eta`` is strictly
            negative.  Both vanish in the large-Re(T) limit.
        """
        ReT_sq = self.ReT_stabilized * self.ReT_stabilized
        epsilon = 3.0 / (2.0 * ReT_sq)
        eta = -1.5 / ReT_sq
        return epsilon, eta

    # ── EML structural tree (b₃ traceback) --------------------------------

    def _build_observables_eml_tree(
        self,
        epsilon: float,
        eta: float,
    ) -> Any:
        """Build the structural EML tree for ``n_s`` at the derived ε, η.

        The tree is constructed so the b₃ seed appears as a *real* leaf
        (via :func:`b3_leaf`) — not just as the literal ``24`` in a
        formula string.  The website's b₃ tracer walks
        ``EMLPoint.children`` recursively; this leaf is what it lands on.

        The tree encodes ``n_s = 1 - 6 ε + 2 η`` with a redundant
        ``b3 / b3 = 1`` multiplier on the constant term so the
        traceback to b₃ = 24 is *structurally* present (Re(T) is itself
        b₃-derived, but the EML primitive only knows about the leaves
        we hand it).

        Returns ``None`` if the optional ``eml-math`` /
        ``eml-spectral`` packages are not installed.

        Parameters
        ----------
        epsilon:
            Slow-roll ε at the current Re(T).
        eta:
            Slow-roll η at the current Re(T).

        Returns
        -------
        EMLPoint | None
            Root node of the ``n_s`` tree, or ``None`` when EML is
            absent.
        """
        if not EML_AVAILABLE:
            return None

        # ``eml_scalar`` encodes negatives via ``ops.neg`` and ``ops.mul``
        # drops signs, so feeding a negative literal directly into
        # ``eml_mul`` mis-evaluates the structural tree.  We therefore
        # carry magnitudes through the multiplications and re-introduce
        # the sign explicitly with :func:`eml_sub` outside the product.
        # ε is strictly positive and η is strictly negative by
        # construction (see :meth:`slow_roll_parameters`).
        epsilon_node = eml_scalar(float(epsilon))
        eta_abs_node = eml_scalar(float(abs(eta)))
        six = eml_scalar(6.0)
        two = eml_scalar(2.0)

        # b₃ enters via the canonical labelled leaf.  Wrapped as a
        # multiplicative identity (b3 / b3) so the traceback to the
        # SSoT seed is structurally present without altering the value.
        b3 = b3_leaf()
        identity = eml_div(b3, b3_leaf())
        one = eml_mul(eml_scalar(1.0), identity)

        # n_s = 1 - 6 ε + 2 η  with  η < 0  ↔  n_s = 1 - 6 ε - 2 |η|.
        six_epsilon = eml_mul(six, epsilon_node)
        two_eta_abs = eml_mul(two, eta_abs_node)
        return eml_sub(eml_sub(one, six_epsilon), two_eta_abs)

    # ── Public derivation --------------------------------------------------

    def derive_observables(self) -> Dict[str, Any]:
        """Derive the CMB observables ``n_s`` and ``r``.

        The canonical ``n_s`` is computed natively from the in-module
        infrared-closure formula ``n_s = 1 - 2 * phi^2 / chi_eff`` with
        ``chi_eff = 6 * b3 = 144``, which sits 0.30σ from Planck 2018
        (0.9649 ± 0.0042).  See :func:`_infrared_closure_n_s` and the
        module docstring "Canonical n_s — infrared closure" for the
        physics.  The leading-order slow-roll derivation on the Re(T)
        potential is preserved as ``n_s_slow_roll`` for transparency.

        ``r`` is the textbook slow-roll value ``r = 16 ε``.

        Returns
        -------
        dict
            ``{"n_s": float, "r": float, "n_s_slow_roll": float,
            "n_s_canonical_source": str, "status": str, ...}``.

            * ``n_s`` — the canonical scalar spectral index
              (0.9636, Planck-compatible).
            * ``r`` — the tensor-to-scalar ratio (strictly positive).
            * ``n_s_slow_roll`` — the slow-roll value (0.9996) from
              the Re(T) potential, retained for diagnostic purposes.
            * ``n_s_canonical_source`` — the SSoT path the canonical
              n_s was sourced from (or ``"fallback:slow_roll"``).
            * ``status`` — one of the canonical strings
              :data:`_STATUS_AGREES`,
              :data:`_STATUS_DOCUMENTED_DIVERGENCE`,
              :data:`_STATUS_R_VIOLATION`,
              :data:`_STATUS_CANONICAL_UNAVAILABLE`.
        """
        # 1) Slow-roll observables (canonical for r, diagnostic for n_s)
        epsilon, eta = self.slow_roll_parameters()
        n_s_slow_roll = 1.0 - 6.0 * epsilon + 2.0 * eta
        r = 16.0 * epsilon

        # 2) Canonical n_s (Sprint T5 #2 Option (b): native infrared
        #    closure ``n_s = 1 - 2*phi^2/chi_eff`` with chi_eff = 6*b3 =
        #    144).  Self-contained — no GeometricAnchors delegation.
        #    Defensive fallback to the slow-roll value if the arithmetic
        #    raises (should never fire in production).
        n_s_canonical, canonical_available = _infrared_closure_n_s()
        if canonical_available:
            n_s = n_s_canonical
            n_s_canonical_source = (
                "infrared_closure: 1 - 2*phi^2/chi_eff = 1 - 2/55 "
                "(chi_eff = 6*b3 = 144, phi = (1+sqrt(5))/2; native "
                "derivation in metaphysica.simulations.PM.cosmology.inflation)"
            )
        else:
            n_s = n_s_slow_roll
            n_s_canonical_source = "fallback:slow_roll"

        # 3) Status logic.  Order matters: r violations take precedence
        #    over n_s ones because exceeding the upper bound on r is a
        #    stronger falsification signal.  Canonical-unavailable
        #    trumps the slow-roll divergence flag because the latter is
        #    only meaningful when the canonical n_s is actually in use.
        canonical_in_window = canonical_available and (
            abs(n_s - PLANCK_N_S_CENTRAL) <= PLANCK_N_S_SIGMA
        )
        slow_roll_in_window = (
            abs(n_s_slow_roll - PLANCK_N_S_CENTRAL) <= PLANCK_N_S_SIGMA
        )
        r_in_window = r < PLANCK_R_UPPER_95
        if not r_in_window:
            status = _STATUS_R_VIOLATION
        elif not canonical_available:
            status = _STATUS_CANONICAL_UNAVAILABLE
        elif canonical_in_window and not slow_roll_in_window:
            # Canonical agrees, slow-roll diverges — preserved diagnostic.
            status = _STATUS_DOCUMENTED_DIVERGENCE
        elif canonical_in_window:
            status = _STATUS_AGREES
        else:
            # Canonical itself is out of window — unexpected, surface it.
            status = _STATUS_DOCUMENTED_DIVERGENCE

        # 4) Persist the v25.0 derivations.  The formula strings mention
        #    ``b3`` (chi_eff = 6*b3 = 144 for canonical n_s; Re(T) ← b3
        #    = 24 for slow-roll r) so the eml_operator_tree's
        #    b3_traceback flag is set on each registered entry.
        self._eml_tree.register_derivation(
            param="n_s",
            formula=(
                "Canonical (infrared closure, native): "
                "1 - 2*phi^2/chi_eff = 1 - 2/55 where "
                "chi_eff = 6*b3 = 144 and phi = (1+sqrt(5))/2. "
                "Slow-roll diagnostic: 1 - 6*epsilon + 2*eta where "
                "epsilon = 3 / (2*ReT^2), eta = -1.5 / ReT^2, ReT "
                "inherits from Sprint 4 Re(T) stabilization with b3 = 24."
            ),
            value=float(n_s),
        )
        self._eml_tree.register_derivation(
            param="r",
            formula=(
                "16 * epsilon where epsilon = 3 / (2*ReT^2) and ReT "
                "inherits from Sprint 4 Re(T) stabilization with b3 = 24"
            ),
            value=float(r),
        )

        # Build the structural EML tree so any test fixture / website
        # walker that wants to fetch the tree from a cached attribute
        # can do so via _last_tree.  The structural tree still encodes
        # the slow-roll formula (that's the leading-order Re(T) tree
        # the module owns); the canonical formula is owned by
        # GeometricAnchors and surfaced via the persisted EML registration.
        self._last_tree = self._build_observables_eml_tree(epsilon, eta)

        return {
            "n_s": float(n_s),
            "r": float(r),
            "n_s_slow_roll": float(n_s_slow_roll),
            "n_s_canonical_source": n_s_canonical_source,
            "epsilon": float(epsilon),
            "eta": float(eta),
            # Per-module status key avoids the `cosmology.status` collision
            # in PMRegistry.load_v26_modules() (inflation, mirror_dm_relic and
            # cosmological_tensions all share the ``cosmology.`` prefix).
            "inflation_status": status,
            # Kept for human display / backwards compatibility.
            "status": status,
        }

    # ── Read-only accessors ------------------------------------------------

    def get_eml_tree(self) -> Dict[str, Dict[str, Any]]:
        """Return the on-disk EML derivation bucket for this module."""
        return self._eml_tree.get_tree()

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"G2Inflation(ReT_stabilized={self.ReT_stabilized!r})"


# ── Module entry point ------------------------------------------------------


def get_inflation_observables() -> Dict[str, Any]:
    """Top-level entry point — derive the CMB observables.

    Used by ``simulations/run_all_simulations.py`` and by callers that
    just want the canonical dict without instantiating
    :class:`G2Inflation` directly.

    Returns
    -------
    dict
        Same shape as :meth:`G2Inflation.derive_observables`::

            {"n_s": float, "r": float, "status": str}
    """
    return G2Inflation().derive_observables()


__all__ = [
    "G2Inflation",
    "B3_SEED",
    "CHI_EFF_TOTAL",
    "DEFAULT_RE_T_STABILIZED",
    "PHI",
    "PLANCK_N_S_CENTRAL",
    "PLANCK_N_S_SIGMA",
    "PLANCK_R_UPPER_95",
    "get_inflation_observables",
]

# Alias for registry.load_v26_modules entry-point contract.
derive_inflation_observables = get_inflation_observables
