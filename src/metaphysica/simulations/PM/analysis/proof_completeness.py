"""
proof_completeness.py — ProofLedger + Bayesian uncertainty scan (Sprint 5 #7).
=============================================================================

Centralises the derivation status of every parameter in the FormulasRegistry
and runs a lightweight Bayesian (Gaussian-prior) posterior scan over the
numerical values so the maturity of the 116:1 compression is transparent
to readers and reviewers.

Origin
------
The class skeleton is sourced verbatim from
``H:/Github/EyesOfAzrael/PossibleImprovements.txt`` (search for
``ProofLedger``). This module implements the spec exactly, with one
extension: the ``open_tension`` bucket is wired up via the registry's
``validation_status`` field so cosmology / particle parameters flagged
as TENSION or FAIL by the experimental cross-check land in that bucket
rather than silently passing as ``numerical_agreement``.

Classification rules
--------------------
For each parameter ``p`` with registry entry ``info``:

1. If the parameter name carries one of the recognised **experimental
   anchor prefixes** (``nufit.``, ``pdg.``, ``codata.``, ``desi.``,
   ``planck.`` — optionally with a leading ``parameters.``) AND the
   ``source`` field starts with ``"ESTABLISHED:"``, classify as
   ``"experimental_anchor"``.  These are NuFIT / PDG / CODATA / DESI /
   Planck observational inputs — they are anchors against which the
   theory is checked, not theory fits.

2. Else if the parameter's source simulation is one of the four
   speculative Orch-OR / Gnosis modules tracked in
   :data:`EML_DEFERRED_SIMULATIONS` — or it carries an
   ``eml_deferred=True`` flag on its metadata — classify as
   ``"eml_deferred"``. These are intentionally excluded from the EML
   cross-check (per `TIER_2_3_ROADMAP §T2.2`) and pulled out of the
   ``fully_derived`` / ``fitted`` denominators so the headline metric
   isn't diluted by speculative content.

3. Else if the parameter name matches the **legacy fitted markers**
   (``theta_13_*`` or ``delta_CP_*`` — case-insensitive substring, both
   with-underscore and without-underscore spellings), classify as
   ``"fitted"``.  Sprint 4 derives these geometrically, but the task spec
   explicitly says the ledger surfaces the *divergence* not the closure
   status — i.e. the marker stays a flag for the human reader.

4. Else if ``info.validation_status`` is one of ``{"TENSION", "FAIL"}``
   *and* an experimental value was provided, classify as
   ``"open_tension"``.

5. Else if an EML tree exists for the parameter (either in the legacy
   ``eml_trees.json`` or the v25.0 ``eml_trees_v25.json``), classify as
   ``"fully_derived"``.

6. Otherwise classify as ``"numerical_agreement"``.

Bayesian scan
-------------
For every numeric parameter, draw 1000 samples from a per-parameter
**theory-motivated prior** (see :data:`PRIORS`). The selected prior is
resolved by:

1. First trying a longest-prefix match against the parameter name (with
   any leading ``parameters.`` namespace stripped) — this routes
   experimental anchors to their dataset-specific envelope
   (``pdg.* → σ_rel=0.001``, ``nufit.* → σ_rel=0.014``,
   ``codata.* → σ_rel=1e-9``, ``desi.* → σ_rel=0.05``,
   ``planck.* → σ_rel=0.005``).
2. Else falling back to a status-bucket default keyed on the
   classification result (``fully_derived_default`` for derived theory
   predictions, ``open_tension_default`` for TENSION/FAIL rows,
   ``eml_deferred_default`` for speculative Orch-OR / Gnosis rows).

Each prior carries a ``distribution`` flag — ``"gaussian"`` draws via
:func:`numpy.random.Generator.normal` centred on the registry value with
σ = ``sigma_rel * max(|value|, 1.0)``; ``"log_normal"`` draws via
:func:`numpy.random.Generator.lognormal` with the same σ in log-space
(then offsets back so the posterior mean ≈ the registry value).
``None`` priors (``eml_deferred_default``) skip propagation entirely
and pin the uncertainty to 0.0 — speculative parameters shouldn't move
the headline error budget.

Non-numeric parameters (status strings, dicts) also pin uncertainty at
0.0. The posterior standard deviation is returned per parameter — this
is a proxy for the 1-σ sensitivity of the prediction, NOT a real
Bayesian inference. Sprint T4.3 (TIER_2_3_ROADMAP §T4.3) — Sprint T5
wires this into CI.

Outputs
-------
:meth:`ProofLedger.build_ledger` returns a tuple ``(DataFrame,
uncertainties)`` where the DataFrame has columns ``Parameter | Value |
Status | EML_Tree | Section | Uncertainty | Duplicate_Derivations``
and ``uncertainties`` is a numpy array aligned with the DataFrame row
order. ``Duplicate_Derivations`` is a per-row list of the *other*
registered parameter IDs that derive the same physical observable
(sourced from :data:`metaphysica.simulations.core.observable_groups.OBSERVABLE_GROUPS`
so the ledger and the shadow-derivation auditor stay in lock-step).

:meth:`ProofLedger.derive_proof_ledger` packages the above plus a
status histogram and the per-section grouping into a dict suitable for
serialisation. The orchestrator
:mod:`metaphysica.generators.generate_proof_completeness` writes the
dict out as ``AutoGenerated/proof_completeness_ledger.json`` and renders
the grouped table to ``AutoGenerated/proof_completeness_ledger.md``.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""
from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Tuple

import numpy as np

# pandas is an OPTIONAL extra (`plots`), but this module imported it at module
# level -- so on any install without that extra, importing proof_completeness
# raised ModuleNotFoundError, taking down the nine tests in
# test_proof_completeness_priors.py that CI runs as a GATING step. The gate has
# been erroring rather than gating since the extra was split out.
#
# `from __future__ import annotations` makes the two pd.DataFrame annotations
# below strings, so only the one real construction site needs the import. It is
# deferred into build_ledger() and raises there with a clear instruction.
if TYPE_CHECKING:  # pragma: no cover - typing only
    import pandas as pd

# Sprint 4 EML adapter — exactly the import path the task spec mandates.
from metaphysica.simulations.core.eml_tree_adapter import eml_operator_tree

# Sprint T2 #6 — shared observable-group map; same source the shadow-
# derivation detector consumes, so the ledger's Duplicate_Derivations
# column and the audit_shadow_derivations.py CONFLICT report stay
# semantically in lock-step.
from metaphysica.simulations.core.observable_groups import (
    OBSERVABLE_GROUPS,
    build_param_to_group_index,
)


# ── Classification constants ───────────────────────────────────────────────

#: Status bucket labels used everywhere in this module + the on-disk JSON.
STATUS_FULLY_DERIVED      = "fully_derived"
STATUS_NUMERICAL          = "numerical_agreement"
STATUS_FITTED             = "fitted"
STATUS_OPEN_TENSION       = "open_tension"
STATUS_EXPERIMENTAL_ANCHOR = "experimental_anchor"
STATUS_EML_DEFERRED       = "eml_deferred"

#: Canonical ordering for histograms / markdown.
STATUS_ORDER: Tuple[str, ...] = (
    STATUS_FULLY_DERIVED,
    STATUS_NUMERICAL,
    STATUS_EXPERIMENTAL_ANCHOR,
    STATUS_FITTED,
    STATUS_OPEN_TENSION,
    STATUS_EML_DEFERRED,
)

#: Validation flags that move a parameter into ``open_tension``.
OPEN_TENSION_VALIDATIONS = frozenset({"TENSION", "FAIL"})

#: Simulation IDs whose parameters are intentionally deferred from the EML
#: cross-check (per TIER_2_3_ROADMAP §T2.2). These four Orch-OR / Gnosis
#: modules currently report ``EML NOT_IMPLEMENTED`` and are speculative —
#: tagging them ``eml_deferred`` keeps the ``fully_derived`` denominator
#: clean. A parameter is classified ``eml_deferred`` when its ``source``
#: (or ``metadata.source_simulation``) matches one of these IDs, OR when
#: its ``metadata`` carries an explicit ``eml_deferred=True`` flag.
EML_DEFERRED_SIMULATIONS: frozenset = frozenset({
    "orch_or_geometry_v22_0",
    "gnosis_unlocking_v22_2",
    "four_dice_sampling_v22",
    "orch_or_pair_shielding_v22",
})

#: Prefixes that flag a registry entry as an experimental anchor — i.e.
#: a NuFIT / PDG / CODATA / DESI / Planck observational input rather
#: than a theoretical prediction. The ``parameters.`` lead is optional
#: so both ``nufit.theta_13`` and ``parameters.nufit.theta_13`` are
#: recognised.
EXPERIMENTAL_ANCHOR_PREFIXES: Tuple[str, ...] = (
    "nufit.",
    "pdg.",
    "codata.",
    "desi.",
    "planck.",
)

#: The ``source`` field must carry this prefix for an entry to count as
#: an experimental anchor — guards against a derived parameter that
#: happens to live in a ``pdg.*`` slot but was computed by a simulation.
EXPERIMENTAL_ANCHOR_SOURCE_PREFIX = "ESTABLISHED:"

#: Pre-compiled legacy fitted-marker detector.  Matches case-insensitively
#: against the parameter NAME (so ``nufit.theta_13`` and
#: ``neutrino.delta_CP_pred`` both hit). Underscored / non-underscored
#: spellings are both covered (delta_CP, deltaCP, delta_cp).
_FITTED_PATTERN = re.compile(
    r"(?:theta_?13|delta_?cp)",
    re.IGNORECASE,
)

#: Bayesian scan defaults.
DEFAULT_SIGMA_FRACTION = 0.01     # 1 % Gaussian prior (used when no PRIORS entry matches)
DEFAULT_N_SAMPLES      = 1000     # 1000 posterior draws

# ── Sprint T4.3 — theory-motivated priors ────────────────────────────────────
#
# Replaces the uniform 1 % Gaussian prior with per-parameter-family priors
# resolved by name prefix (for experimental anchors) or classification
# bucket (for theory / open-tension / EML-deferred rows). Per TIER_2_3_ROADMAP
# §T4.3, this is the kickoff implementation — real per-formula error
# propagation via autodiff is task #6 in the same sprint.
#
# Prior entry contract:
#   * ``sigma_rel``: fractional 1-σ width relative to |value|.
#   * ``distribution``: either ``"gaussian"`` (numpy.random.normal) or
#     ``"log_normal"`` (numpy.random.lognormal).
#   * ``None`` entry: skip propagation entirely — uncertainty pinned to 0.
#
# The ``*`` suffix on prefix keys mirrors the experimental-anchor namespace
# (e.g. ``pdg.m_electron`` matches the ``pdg.*`` rule). Defaults are keyed
# on the classification bucket name (``fully_derived_default`` etc.) so the
# resolver can fall through cleanly when no name prefix hits.

#: Theory-motivated priors per parameter family.
PRIORS: Dict[str, Optional[Dict[str, Any]]] = {
    # CODATA / PDG / experimental anchors — tight, asymmetric if dataset
    # has known systematic. Resolved by NAME prefix (longest match wins).
    "pdg.*":    {"sigma_rel": 0.001,  "distribution": "gaussian"},
    "nufit.*":  {"sigma_rel": 0.014,  "distribution": "gaussian"},  # NuFIT 6.0 typical ~1.4 %
    "codata.*": {"sigma_rel": 1e-9,   "distribution": "gaussian"},  # CODATA is essentially exact
    "desi.*":   {"sigma_rel": 0.05,   "distribution": "gaussian"},
    "planck.*": {"sigma_rel": 0.005,  "distribution": "gaussian"},

    # Theory derived — 1 % Gaussian by default. Resolved by STATUS bucket
    # when no name prefix hits.
    "fully_derived_default": {"sigma_rel": 0.01, "distribution": "gaussian"},

    # Open tensions — wider, log-normal (positive-definite, asymmetric).
    "open_tension_default": {"sigma_rel": 0.1, "distribution": "log_normal"},

    # EML deferred — skip propagation. Speculative consciousness sims
    # shouldn't move the headline error budget.
    "eml_deferred_default": None,
}

#: Mapping STATUS_* constant → default-prior key. ``None`` means "no
#: status-specific default registered" → falls through to the legacy
#: ``DEFAULT_SIGMA_FRACTION`` Gaussian.
_STATUS_TO_DEFAULT_KEY: Dict[str, str] = {
    STATUS_FULLY_DERIVED:      "fully_derived_default",
    STATUS_NUMERICAL:          "fully_derived_default",
    STATUS_EXPERIMENTAL_ANCHOR: "fully_derived_default",
    STATUS_FITTED:             "fully_derived_default",
    STATUS_OPEN_TENSION:       "open_tension_default",
    STATUS_EML_DEFERRED:       "eml_deferred_default",
}

#: Sentinel returned by :func:`_resolve_prior` when a parameter should
#: skip uncertainty propagation entirely (e.g. EML-deferred rows).
_SKIP_PRIOR = "__skip__"


def _resolve_prior(
    param: str,
    status: str,
    priors: Optional[Mapping[str, Optional[Mapping[str, Any]]]] = None,
) -> Any:
    """Resolve the prior dict for *param* with classification *status*.

    Resolution order:

    1. **Longest-prefix name match.** Strip a leading ``parameters.``
       namespace, then test each ``"<prefix>.*"`` key in :data:`PRIORS`
       against the parameter name — longest matching prefix wins. This
       routes ``nufit.theta_13`` → ``nufit.*`` even though ``pdg.*``,
       ``desi.*``, etc. are also registered.

    2. **Status-bucket default.** Map the classification *status* to one
       of the ``*_default`` keys via :data:`_STATUS_TO_DEFAULT_KEY` and
       look that up in :data:`PRIORS`.

    3. **Legacy fallback.** When neither path resolves, return ``None``
       so the caller can apply the legacy ``DEFAULT_SIGMA_FRACTION``
       Gaussian — guarantees backward compatibility for parameters that
       slip through the new classification scheme.

    Returns
    -------
    dict | _SKIP_PRIOR | None
        * A prior dict ``{"sigma_rel": ..., "distribution": ...}`` when a
          rule fired and was non-None.
        * The :data:`_SKIP_PRIOR` sentinel when the matched entry was
          explicitly ``None`` (EML-deferred → skip propagation).
        * ``None`` when no rule fired at all → caller falls back to the
          legacy default.
    """
    table = priors if priors is not None else PRIORS

    # 1. Longest-prefix name match.
    name = str(param)
    if name.startswith("parameters."):
        name = name[len("parameters."):]
    best_prefix = ""
    best_entry: Any = None
    best_hit = False
    for key, entry in table.items():
        if not key.endswith(".*"):
            continue
        prefix = key[:-1]  # keep the trailing '.' so "pdg." matches "pdg.foo"
        if name.startswith(prefix) and len(prefix) > len(best_prefix):
            best_prefix = prefix
            best_entry = entry
            best_hit = True
    if best_hit:
        return _SKIP_PRIOR if best_entry is None else best_entry

    # 2. Status-bucket default.
    default_key = _STATUS_TO_DEFAULT_KEY.get(status)
    if default_key is not None and default_key in table:
        entry = table[default_key]
        return _SKIP_PRIOR if entry is None else entry

    # 3. Legacy fallback.
    return None


# ── Helpers ────────────────────────────────────────────────────────────────


def _is_fitted_marker(param: str) -> bool:
    """True iff *param* name carries one of the legacy fitted markers."""
    return bool(_FITTED_PATTERN.search(str(param)))


def _is_experimental_anchor(param: str, info: Mapping[str, Any]) -> bool:
    """True iff *param* is a NuFIT / PDG / CODATA / DESI / Planck anchor.

    An entry counts as an experimental anchor when BOTH conditions hold:

    * The parameter name starts with one of the recognised dotted
      prefixes (``nufit.``, ``pdg.``, ``codata.``, ``desi.``, ``planck.``)
      — optionally with a leading ``parameters.`` namespace.
    * The ``source`` field (top-level or under ``metadata``) starts with
      the ``ESTABLISHED:`` marker.

    Both conditions are required so a derived parameter that happens to
    live under, say, ``pdg.*`` but was actually computed by a simulation
    (``source`` = ``"neutrino_mixing_v17_2"``) is *not* mis-tagged as an
    anchor.
    """
    name = str(param)
    if name.startswith("parameters."):
        name = name[len("parameters."):]
    if not any(name.startswith(p) for p in EXPERIMENTAL_ANCHOR_PREFIXES):
        return False
    if not isinstance(info, Mapping):
        return False
    source = info.get("source")
    if isinstance(source, str) and source.startswith(EXPERIMENTAL_ANCHOR_SOURCE_PREFIX):
        return True
    meta = info.get("metadata")
    if isinstance(meta, Mapping):
        meta_source = meta.get("source")
        if isinstance(meta_source, str) and meta_source.startswith(
            EXPERIMENTAL_ANCHOR_SOURCE_PREFIX
        ):
            return True
    return False


def _is_eml_deferred(info: Mapping[str, Any]) -> bool:
    """True iff the parameter is from an EML-deferred speculative simulation.

    A parameter qualifies when ANY of the following hold:

    * ``info["metadata"]["eml_deferred"]`` is truthy.
    * ``info["eml_deferred"]`` is truthy (top-level flag).
    * The top-level ``source`` field matches one of
      :data:`EML_DEFERRED_SIMULATIONS`.
    * The ``metadata.source_simulation`` field matches one of
      :data:`EML_DEFERRED_SIMULATIONS`.

    This covers both the PMRegistry export shape (``source`` at top level,
    ``source_simulation`` under metadata) and any future opt-in flag a
    simulation may carry on its metadata payload.
    """
    if not isinstance(info, Mapping):
        return False

    # Explicit flag — preferred when a simulation opts in.
    if bool(info.get("eml_deferred")):
        return True
    meta = info.get("metadata")
    if isinstance(meta, Mapping) and bool(meta.get("eml_deferred")):
        return True

    # Hardcoded simulation set — the four Orch-OR / Gnosis modules.
    source = info.get("source")
    if isinstance(source, str) and source in EML_DEFERRED_SIMULATIONS:
        return True
    if isinstance(meta, Mapping):
        sim = meta.get("source_simulation")
        if isinstance(sim, str) and sim in EML_DEFERRED_SIMULATIONS:
            return True

    return False


def _has_eml_tree(info: Mapping[str, Any]) -> bool:
    """True iff a registry entry advertises an EML tree.

    Recognises three shapes:

    * ``info["eml_tree"]`` directly populated (spec form).
    * ``info["eml_description"]`` starting with ``"EML:"`` (legacy form
      used by the FormulasRegistry).
    * ``info["metadata"]["eml_description"]`` starting with ``"EML:"``
      (PMRegistry export shape — eml_description lives under metadata).
    """
    if not isinstance(info, Mapping):
        return False
    tree = info.get("eml_tree")
    if tree not in (None, "", "None"):
        return True
    desc = info.get("eml_description", "") or ""
    if isinstance(desc, str) and desc.strip().startswith("EML:"):
        return True
    meta = info.get("metadata")
    if isinstance(meta, Mapping):
        meta_desc = meta.get("eml_description", "") or ""
        if isinstance(meta_desc, str) and meta_desc.strip().startswith("EML:"):
            return True
    return False


def _validation_status(info: Mapping[str, Any]) -> Optional[str]:
    """Extract the validation_status field if present."""
    if not isinstance(info, Mapping):
        return None
    v = info.get("validation_status")
    if isinstance(v, str) and v:
        return v
    return None


def _coerce_value(info: Mapping[str, Any]) -> Any:
    """Return the registry value for *info*, robust to dict / scalar form."""
    if isinstance(info, Mapping):
        return info.get("value")
    return info


def _to_float_or_none(value: Any) -> Optional[float]:
    """Coerce *value* to float for the Bayesian scan; return None on failure."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        v = float(value)
        return v if math.isfinite(v) else None
    if isinstance(value, str):
        try:
            v = float(value)
        except (TypeError, ValueError):
            return None
        return v if math.isfinite(v) else None
    return None


def _section_of(param: str) -> str:
    """Section = the dotted prefix before the first '.', or '(none)'."""
    s = str(param)
    if "." in s:
        return s.split(".", 1)[0]
    return "(none)"


def _classify(param: str, info: Mapping[str, Any]) -> str:
    """Return one of the six STATUS_* constants for *param*.

    Ordering (from TIER_2_3_ROADMAP §T2.2):

    1. Experimental anchor — wins over the legacy fitted marker so
       ``nufit.theta_13`` lands in the right bucket.
    2. EML-deferred — speculative consciousness sims are pulled out of
       the derived / fitted denominators before the rest of the cascade.
    3. Legacy fitted marker — non-anchor ``theta_13`` / ``delta_CP``
       parameters.
    4. Open tension — ``validation_status`` is ``TENSION`` / ``FAIL`` and
       an ``experimental_value`` is present.
    5. Fully derived — an EML tree exists.
    6. Numerical agreement — default fallback.
    """
    if _is_experimental_anchor(param, info):
        return STATUS_EXPERIMENTAL_ANCHOR
    if _is_eml_deferred(info):
        return STATUS_EML_DEFERRED
    if _is_fitted_marker(param):
        return STATUS_FITTED
    vstat = _validation_status(info)
    has_experiment = info.get("experimental_value") is not None
    if vstat in OPEN_TENSION_VALIDATIONS and has_experiment:
        return STATUS_OPEN_TENSION
    if _has_eml_tree(info):
        return STATUS_FULLY_DERIVED
    return STATUS_NUMERICAL


def _eml_tree_label(info: Mapping[str, Any]) -> str:
    """Return a short string identifying the EML tree (or 'None')."""
    if not isinstance(info, Mapping):
        return "None"
    tree = info.get("eml_tree")
    if isinstance(tree, str) and tree:
        return tree
    desc = info.get("eml_description", "")
    if isinstance(desc, str) and desc.startswith("EML:"):
        return desc
    meta = info.get("metadata")
    if isinstance(meta, Mapping):
        meta_desc = meta.get("eml_description", "")
        if isinstance(meta_desc, str) and meta_desc.startswith("EML:"):
            return meta_desc
    return "None"


def _compute_duplicates_map(
    registry_map: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Tuple[str, ...]]:
    """Compute per-parameter cross-links from :data:`OBSERVABLE_GROUPS`.

    For each parameter that belongs to an observable group, returns the
    *other* group members that are also present in ``registry_map`` with
    a numeric value. The "at least 2 numeric members" gate mirrors the
    shadow-derivation detector's ``INSUFFICIENT_DATA`` rule so the
    ledger's cross-link surface and the audit report stay aligned: a
    group with only one live numeric chain produces no duplications.

    Parameters
    ----------
    registry_map
        ``{param_id: info_dict}`` view of the live registry. Already
        normalised so non-mapping infos are wrapped as ``{"value": ...}``.

    Returns
    -------
    dict
        ``{param_id: (other_param_id_1, other_param_id_2, ...)}`` for
        every parameter that has at least one numeric sibling chain.
        Parameters with no live siblings (or that don't appear in any
        observable group) are absent from the result.
    """
    index = build_param_to_group_index(OBSERVABLE_GROUPS)

    # Per-observable: count how many declared members have a numeric
    # value in the current registry, and remember which.
    group_numeric_members: Dict[str, List[str]] = {}
    for observable, members in OBSERVABLE_GROUPS.items():
        numeric_here: List[str] = []
        for member in members:
            info = registry_map.get(member)
            if info is None:
                continue
            if _to_float_or_none(_coerce_value(info)) is not None:
                numeric_here.append(member)
        group_numeric_members[observable] = numeric_here

    out: Dict[str, Tuple[str, ...]] = {}
    for param_id, (observable, _all_siblings) in index.items():
        numeric = group_numeric_members.get(observable, [])
        if len(numeric) < 2:
            # No duplicated chain in the live registry — leave empty.
            continue
        siblings = tuple(m for m in numeric if m != param_id)
        if siblings:
            out[param_id] = siblings
    return out


def _registry_to_items(registry: Any) -> List[Tuple[str, Mapping[str, Any]]]:
    """Yield ``(param, info)`` pairs from any of the supported registry shapes.

    Supported shapes
    ----------------
    * Plain ``dict`` — used by the source spec.
    * PMRegistry singleton — ``.export_parameters()`` returns the dict shape.
    * FormulasRegistry — looks for ``.registry`` attribute (dict).
    * Any object with ``.items()``.
    """
    if registry is None:
        return []
    if hasattr(registry, "export_parameters") and callable(registry.export_parameters):
        try:
            exported = registry.export_parameters()
            if isinstance(exported, Mapping):
                return list(exported.items())
        except Exception:  # pragma: no cover — defensive
            pass
    if hasattr(registry, "registry") and isinstance(registry.registry, Mapping):
        return list(registry.registry.items())
    if isinstance(registry, Mapping):
        return list(registry.items())
    if hasattr(registry, "items") and callable(registry.items):
        try:
            return list(registry.items())
        except Exception:  # pragma: no cover
            return []
    return []


# ── ProofLedger ─────────────────────────────────────────────────────────────


class ProofLedger:
    """Automated proof-completeness ledger + Gaussian Bayesian scan.

    See module docstring for the classification rules and the Bayesian
    scan semantics.

    Examples
    --------
    >>> ledger = ProofLedger()
    >>> df, unc = ledger.build_ledger({"alpha": {"value": 1/137, "eml_tree": "T"}})
    >>> bool({"Parameter", "Value", "Status", "EML_Tree"} <= set(df.columns))
    True
    >>> len(unc) == len(df)
    True
    """

    def __init__(
        self,
        *,
        sigma_fraction: float = DEFAULT_SIGMA_FRACTION,
        n_samples: int = DEFAULT_N_SAMPLES,
        rng_seed: Optional[int] = None,
    ) -> None:
        if not math.isfinite(float(sigma_fraction)) or sigma_fraction <= 0.0:
            raise ValueError(
                f"sigma_fraction must be a finite positive float, "
                f"got {sigma_fraction!r}"
            )
        if int(n_samples) <= 0:
            raise ValueError(f"n_samples must be positive, got {n_samples!r}")
        self.sigma_fraction = float(sigma_fraction)
        self.n_samples = int(n_samples)
        self._rng = np.random.default_rng(rng_seed)
        # On-disk EML tree — overlay-safe slot in AutoGenerated/eml_trees_v25.json.
        self.ledger_tree = eml_operator_tree("proof_completeness")

    # ── Public API ─────────────────────────────────────────────────────────

    def build_ledger(
        self,
        registry: Any,
    ) -> Tuple[pd.DataFrame, np.ndarray]:
        """Build the classification DataFrame + Bayesian uncertainty array.

        Parameters
        ----------
        registry
            Any of: a plain ``dict[str, dict]``, a PMRegistry instance
            (``.export_parameters()`` is used), or a FormulasRegistry
            instance (``.registry`` attribute is used).

        Returns
        -------
        df, uncertainties
            ``df`` columns: ``Parameter | Value | Status | EML_Tree |
            Section | Uncertainty | Duplicate_Derivations``.
            ``uncertainties`` is a numpy array of the same length as the
            DataFrame, holding the posterior standard deviation per
            parameter (0.0 for non-numeric). ``Duplicate_Derivations``
            lists the other registered parameter IDs that derive the same
            physical observable (via
            :data:`metaphysica.simulations.core.observable_groups.OBSERVABLE_GROUPS`)
            — empty when the row's parameter has no sibling chain.
        """
        items = _registry_to_items(registry)
        registry_map: Dict[str, Mapping[str, Any]] = {
            str(p): (info if isinstance(info, Mapping) else {"value": info})
            for p, info in items
        }

        # Sprint T2 #6 — pre-compute the per-parameter cross-link surface.
        # A row only carries duplicates when the observable group has at
        # least 2 *numeric* members live in the current registry; this
        # mirrors the shadow-derivation detector's
        # "INSUFFICIENT_DATA if <2 numeric members" gate so the ledger
        # and the audit report agree on what counts as a duplication.
        duplicates_map = _compute_duplicates_map(registry_map)

        rows: List[Dict[str, Any]] = []
        for param, info in items:
            info_map = info if isinstance(info, Mapping) else {"value": info}
            status = _classify(param, info_map)
            value = _coerce_value(info_map)
            rows.append({
                "Parameter": str(param),
                "Value": value,
                "Status": status,
                "EML_Tree": _eml_tree_label(info_map),
                "Section": _section_of(param),
                "Duplicate_Derivations": list(duplicates_map.get(str(param), ())),
            })

        try:
            import pandas as pd
        except ImportError as exc:  # pragma: no cover - exercised in CI matrix
            raise ImportError(
                "build_ledger needs pandas, which ships in the optional "
                "'plots' extra. Install with: pip install metaphysica[plots]"
            ) from exc

        df = pd.DataFrame(rows, columns=[
            "Parameter", "Value", "Status", "EML_Tree", "Section",
            "Duplicate_Derivations",
        ])

        uncertainties = self._bayesian_scan(df)
        df["Uncertainty"] = uncertainties

        # Record the ledger build itself as an EML derivation (Sprint 4
        # adapter contract — overlay-safe write into eml_trees_v25.json).
        self.ledger_tree.register_derivation(
            param="ledger_summary",
            formula="full registry audit + Bayesian Gaussian-prior scan (sigma=1%, N=1000)",
            value=int(len(df)),
        )

        return df, uncertainties

    def derive_proof_ledger(self, registry: Any) -> Dict[str, Any]:
        """Run :meth:`build_ledger` and package the results for serialisation.

        The returned dict carries

        * ``status_counts`` — histogram of the four buckets.
        * ``per_section`` — ``{section: {status: count}}`` matrix.
        * ``rows`` — list-of-dicts version of the DataFrame.
        * ``uncertainties`` — list of floats aligned with ``rows``.
        * ``meta`` — Bayesian scan parameters + total counts.
        """
        df, uncertainties = self.build_ledger(registry)

        status_counts = {key: 0 for key in STATUS_ORDER}
        for s in df["Status"].tolist():
            status_counts[s] = status_counts.get(s, 0) + 1

        per_section: Dict[str, Dict[str, int]] = {}
        for _, row in df.iterrows():
            section = row["Section"]
            status = row["Status"]
            bucket = per_section.setdefault(section, {k: 0 for k in STATUS_ORDER})
            bucket[status] = bucket.get(status, 0) + 1

        # JSON-friendly value coercion (numpy → python, NaN → None).
        rows: List[Dict[str, Any]] = []
        for i, (_, row) in enumerate(df.iterrows()):
            v = row["Value"]
            if isinstance(v, (np.floating, np.integer)):
                v = v.item()
            if isinstance(v, float) and not math.isfinite(v):
                v = None
            unc = float(uncertainties[i]) if i < len(uncertainties) else 0.0
            if not math.isfinite(unc):
                unc = 0.0
            duplicates_raw = row.get("Duplicate_Derivations", []) \
                if hasattr(row, "get") else []
            # Pandas Series.get returns the column scalar; coerce to a
            # plain list of strings so the JSON payload is canonical and
            # any numpy-array containers from DataFrame round-trips are
            # flattened.
            if duplicates_raw is None:
                duplicates: List[str] = []
            else:
                try:
                    duplicates = [str(d) for d in list(duplicates_raw)]
                except TypeError:
                    duplicates = []
            rows.append({
                "parameter": str(row["Parameter"]),
                "value": v,
                "status": str(row["Status"]),
                "eml_tree": str(row["EML_Tree"]),
                "section": str(row["Section"]),
                "uncertainty": unc,
                "duplicate_derivations": duplicates,
            })

        # Register the four bucket counts on the EML tree.
        for bucket in STATUS_ORDER:
            self.ledger_tree.register_derivation(
                param=f"status_count_{bucket}",
                formula=f"count of registry params classified as {bucket}",
                value=int(status_counts.get(bucket, 0)),
            )

        return {
            "rows": rows,
            "status_counts": status_counts,
            "per_section": per_section,
            "uncertainties": [r["uncertainty"] for r in rows],
            "meta": {
                "n_parameters": int(len(df)),
                "sigma_fraction": float(self.sigma_fraction),
                "n_samples": int(self.n_samples),
                "classifier_version": "sprint5.task7.v1",
            },
        }

    # ── Internal: theory-motivated Bayesian scan ───────────────────────────

    def _bayesian_scan(self, df: pd.DataFrame) -> np.ndarray:
        """Run a theory-motivated posterior scan over the numeric Values column.

        Replaces the Sprint 5.7 uniform 1 % Gaussian prior with per-parameter
        priors resolved by :func:`_resolve_prior` against :data:`PRIORS`:

        * Experimental anchors (``pdg.*``, ``nufit.*``, ``codata.*``,
          ``desi.*``, ``planck.*``) draw from a tight Gaussian whose σ
          matches the dataset's typical error envelope.
        * Theory-derived rows draw from a 1 % Gaussian.
        * Open-tension rows draw from a 10 % log-normal (positive-definite,
          asymmetric — better for masses / cross-sections).
        * EML-deferred rows skip propagation entirely (σ = 0).

        Each row's draw uses :func:`numpy.random.Generator.normal` or
        :func:`numpy.random.Generator.lognormal` per the prior's
        ``distribution`` flag. Per-row σ = ``sigma_rel * max(|value|, 1.0)``
        so the scan tracks the value's order of magnitude rather than
        flat 0.01 — a value of ``2.43e18`` doesn't get a rounding-error
        noise floor.

        Sprint T4.3 kickoff per TIER_2_3_ROADMAP §T4.3.
        Returns a length-N array of posterior standard deviations.
        """
        n = len(df)
        if n == 0:
            return np.zeros(0, dtype=float)

        values = df["Value"].tolist()
        statuses = df["Status"].tolist() if "Status" in df.columns else [""] * n
        params = df["Parameter"].tolist() if "Parameter" in df.columns else [""] * n

        stds = np.zeros(n, dtype=float)

        for i in range(n):
            fv = _to_float_or_none(values[i])
            if fv is None:
                continue  # non-numeric → σ = 0
            prior = _resolve_prior(params[i], statuses[i])
            if prior is _SKIP_PRIOR:
                continue  # EML-deferred or other explicit skip → σ = 0

            if prior is None:
                # Legacy fallback — flat 1 % Gaussian on |value|.
                sigma_rel = self.sigma_fraction
                distribution = "gaussian"
            else:
                sigma_rel = float(prior.get("sigma_rel", self.sigma_fraction))
                distribution = str(prior.get("distribution", "gaussian"))

            # σ on the absolute scale of the value's magnitude. The
            # max(|v|, 1.0) clamp protects against a value-of-zero entry
            # collapsing the prior to a delta.
            sigma = sigma_rel * max(abs(fv), 1.0)
            if not math.isfinite(sigma) or sigma <= 0.0:
                continue

            if distribution == "log_normal":
                # Draw positive-definite samples whose median equals the
                # registry value: lognormal(mean=ln|v|, sigma=sigma_rel)
                # gives a multiplicative spread; we recentre on |v| to
                # keep the posterior mean ≈ value and copy the sign of v.
                if abs(fv) == 0.0:
                    # Pure-zero log-normal is undefined; degrade to a
                    # Gaussian on the abs scale.
                    draws = self._rng.normal(loc=0.0, scale=sigma,
                                             size=self.n_samples)
                else:
                    mu = math.log(abs(fv))
                    samples_pos = self._rng.lognormal(
                        mean=mu, sigma=sigma_rel, size=self.n_samples
                    )
                    draws = math.copysign(1.0, fv) * samples_pos
            else:
                # Gaussian (default).
                draws = self._rng.normal(loc=fv, scale=sigma,
                                         size=self.n_samples)

            std = float(np.std(draws, ddof=0))
            stds[i] = std if math.isfinite(std) else 0.0

        return stds


# ── Module entry point ─────────────────────────────────────────────────────


def derive_proof_ledger(registry: Any) -> Dict[str, Any]:
    """Module entry point — instantiate a :class:`ProofLedger` and run it.

    Convenience wrapper used by
    :mod:`metaphysica.generators.generate_proof_completeness` so the
    orchestrator can stay agnostic of the class signature.
    """
    return ProofLedger().derive_proof_ledger(registry)


# Alias kept for source-spec compatibility (``generate_proof_ledger`` is
# the verbatim name from PossibleImprovements.txt).
generate_proof_ledger = derive_proof_ledger


__all__ = [
    "ProofLedger",
    "derive_proof_ledger",
    "generate_proof_ledger",
    "STATUS_FULLY_DERIVED",
    "STATUS_NUMERICAL",
    "STATUS_FITTED",
    "STATUS_OPEN_TENSION",
    "STATUS_EXPERIMENTAL_ANCHOR",
    "STATUS_EML_DEFERRED",
    "STATUS_ORDER",
    "EXPERIMENTAL_ANCHOR_PREFIXES",
    "EXPERIMENTAL_ANCHOR_SOURCE_PREFIX",
    "EML_DEFERRED_SIMULATIONS",
    "DEFAULT_SIGMA_FRACTION",
    "DEFAULT_N_SAMPLES",
    "PRIORS",
    "resolve_prior",
]


# Public alias for the prior-resolution helper — tests + downstream
# error-propagation modules call it directly.
resolve_prior = _resolve_prior
