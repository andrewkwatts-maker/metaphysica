"""
PMRegistry - Central Parameter, Formula, and Section Registry
===============================================================

Singleton registry for managing all computed parameters, formulas,
and section content in Principia Metaphysica simulations.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import warnings

# Import dependency resolver components
try:
    from metaphysica.simulations.core.dependency_resolver import (
        DependencyGraph,
        DependencyResolver,
        CycleDetectedError,
        MissingComputeFunctionError,
        build_pm_dependency_graph,
        build_seed_values,
    )
    DEPENDENCY_RESOLVER_AVAILABLE = True
except ImportError:
    # Graceful fallback if dependency_resolver not available
    DEPENDENCY_RESOLVER_AVAILABLE = False
    DependencyGraph = None
    DependencyResolver = None


@dataclass
class RegistryEntry:
    """
    Entry in the parameter registry.

    Attributes:
        value: The parameter value (theory prediction or established value)
        source: Source of the value (simulation ID or "ESTABLISHED:SOURCE")
        uncertainty: Optional uncertainty/error on the theory prediction
        status: Status ("ESTABLISHED", "GEOMETRIC", "DERIVED", "PREDICTED", "CALIBRATED")
        timestamp: When the value was set
        metadata: Additional metadata

        # Experimental comparison fields (for validation)
        experimental_value: Experimental measurement for comparison (PDG, NuFIT, DESI, etc.)
        experimental_uncertainty: 1-sigma uncertainty on experimental value
        experimental_source: Citation for experimental value (e.g., "PDG2024", "NuFIT6.0")
        bound_type: Type of comparison ("measured", "upper", "lower", "range")

        # Validation results (computed from theory vs experiment)
        sigma_deviation: Number of sigmas between theory and experiment
            (None for one-sided bounds, where no experimental sigma exists)
        relative_margin: Relative margin (theory-exp)/exp for one-sided
            "lower"/"upper" bounds — NOT a sigma count
        validation_status: "PASS", "MARGINAL", "TENSION", "FAIL", or "NO_DATA"
    """
    value: Any
    source: str
    uncertainty: Optional[float] = None
    status: str = "DERIVED"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Experimental comparison fields
    experimental_value: Optional[float] = None
    experimental_uncertainty: Optional[float] = None
    experimental_source: Optional[str] = None
    bound_type: Optional[str] = None  # "measured", "upper", "lower", "range"

    # Validation results
    sigma_deviation: Optional[float] = None
    relative_margin: Optional[float] = None  # one-sided bounds: (theory-exp)/exp margin
    validation_status: Optional[str] = None  # "PASS", "MARGINAL", "TENSION", "FAIL", "NO_DATA"


@dataclass
class FormulaEntry:
    """
    Entry in the formula registry.

    Attributes:
        formula: The Formula object
        timestamp: When the formula was added
        source: The simulation file that registered this formula
    """
    formula: 'Formula'
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = ""


@dataclass
class SectionEntry:
    """
    Entry in the section registry.

    Attributes:
        content: The SectionContent object
        timestamp: When the section was added
    """
    content: 'SectionContent'
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class PMRegistry:
    """
    Singleton registry for parameters, formulas, and sections.

    This registry serves as the central data store for all simulation
    results, allowing simulations to:
    1. Read input parameters
    2. Write computed parameters
    3. Register formulas and section content
    4. Track provenance and dependencies

    Example Usage:
        registry = PMRegistry.get_instance()

        # Set a parameter
        registry.set_param("gauge.M_GUT", 2.1e16, source="gauge_unification_v16_0")

        # Get a parameter
        M_GUT = registry.get_param("gauge.M_GUT")

        # Check if parameter exists
        if registry.has_param("gauge.ALPHA_GUT"):
            alpha_GUT = registry.get_param("gauge.ALPHA_GUT")

        # Export all data
        params = registry.export_parameters()
        formulas = registry.export_formulas()
        sections = registry.export_sections()
    """

    _instance: Optional['PMRegistry'] = None

    def __new__(cls):
        """Singleton pattern - return existing instance or create new one."""
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._init_registry()
            cls._instance = instance
        return cls._instance

    def _init_registry(self) -> None:
        """Initialize all internal data structures."""
        # Parameter registry: path -> RegistryEntry
        self._parameters: Dict[str, RegistryEntry] = {}

        # Formula registry: formula_id -> FormulaEntry
        self._formulas: Dict[str, FormulaEntry] = {}

        # Section registry: section_id -> SectionEntry
        self._sections: Dict[str, SectionEntry] = {}

        # Provenance tracking: output_path -> [source_simulation_ids]
        self._provenance: Dict[str, List[str]] = {}

        # Mismatch log for debugging
        self._mismatches: List[Dict[str, Any]] = []

        # Dependency resolution system (v20)
        self._dependency_graph: Optional['DependencyGraph'] = None
        self._dependency_resolver: Optional['DependencyResolver'] = None
        self._auto_resolve: bool = False  # Enable auto-resolution on get()
        self._seed_values: Dict[str, Any] = {}  # Base seed values

        # Initialize dependency resolver if available
        if DEPENDENCY_RESOLVER_AVAILABLE:
            self._init_dependency_resolver()

    @classmethod
    def get_instance(cls) -> 'PMRegistry':
        """
        Get the singleton instance of PMRegistry.

        Returns:
            The singleton PMRegistry instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing)."""
        if cls._instance is not None:
            cls._instance._init_registry()

    # -------------------------------------------------------------------------
    # Parameter Management
    # -------------------------------------------------------------------------

    def has_param(self, path: str) -> bool:
        """
        Check if a parameter exists in the registry.

        Args:
            path: Parameter path (e.g., "gauge.M_GUT")

        Returns:
            True if parameter exists, False otherwise
        """
        return path in self._parameters

    def get_param(self, path: str) -> Any:
        """
        Get a parameter value from the registry.

        Args:
            path: Parameter path

        Returns:
            Parameter value

        Raises:
            KeyError: If parameter doesn't exist
        """
        if path not in self._parameters:
            raise KeyError(f"Parameter '{path}' not found in registry")
        return self._parameters[path].value

    def get(self, path: str, default: Any = None, auto_resolve: bool = None) -> Any:
        """
        Get a parameter value with optional default and auto-resolution.

        If auto_resolve is enabled and the parameter is not in the registry,
        attempts to compute it using the dependency resolver.

        Args:
            path: Parameter path
            default: Value to return if parameter doesn't exist
            auto_resolve: Override instance auto_resolve setting

        Returns:
            Parameter value or default if not found
        """
        # Check if parameter exists in registry
        if path in self._parameters:
            return self._parameters[path].value

        # Determine if we should auto-resolve
        should_resolve = auto_resolve if auto_resolve is not None else self._auto_resolve

        # Try auto-resolution if enabled and resolver is available
        if should_resolve and self._dependency_resolver is not None:
            try:
                value = self._resolve_dependency(path)
                if value is not None:
                    return value
            except (KeyError, Exception):
                pass  # Fall through to default handling

        # Return default or raise error
        if default is not None:
            return default
        raise KeyError(f"Parameter '{path}' not found in registry")

    def get_entry(self, path: str) -> Optional[RegistryEntry]:
        """
        Get the full registry entry for a parameter.

        Args:
            path: Parameter path

        Returns:
            RegistryEntry or None if not found
        """
        return self._parameters.get(path)

    def set_param(
        self,
        path: str,
        value: Any,
        source: str,
        uncertainty: Optional[float] = None,
        status: str = "DERIVED",
        metadata: Optional[Dict[str, Any]] = None,
        experimental_value: Optional[float] = None,
        experimental_uncertainty: Optional[float] = None,
        experimental_source: Optional[str] = None,
        bound_type: Optional[str] = None
    ) -> None:
        """
        Set a parameter in the registry.

        Args:
            path: Parameter path (e.g., "gauge.M_GUT")
            value: Parameter value (theory prediction)
            source: Source identifier (simulation ID or "ESTABLISHED:SOURCE")
            uncertainty: Optional uncertainty on theory prediction
            status: Status ("ESTABLISHED", "GEOMETRIC", "DERIVED", "PREDICTED", "CALIBRATED")
            metadata: Optional additional metadata
            experimental_value: Experimental measurement for comparison
            experimental_uncertainty: 1-sigma uncertainty on experimental value
            experimental_source: Citation (e.g., "PDG2024", "NuFIT6.0", "DESI2025")
            bound_type: Type of bound ("measured", "upper", "lower", "range")
        """
        # Check for overwrites and warn if value differs significantly
        if path in self._parameters:
            existing = self._parameters[path]
            # Prevent overwriting ESTABLISHED params
            if existing.status == "ESTABLISHED" and not source.startswith("ESTABLISHED"):
                raise ValueError(f"Cannot override ESTABLISHED param '{path}'")
            self.warn_mismatch(path, value, source)

        # Compute sigma deviation if we have experimental data
        sigma_deviation = None
        relative_margin = None
        validation_status = "NO_DATA"

        if experimental_value is not None and value is not None:
            try:
                theory_val = float(value)
                exp_val = float(experimental_value)

                if bound_type in ("measured", "central_value") and experimental_uncertainty is not None and experimental_uncertainty > 0:
                    # Include theory_uncertainty (from metadata) if available
                    # Total uncertainty: sqrt(exp^2 + theory^2)
                    total_uncertainty = experimental_uncertainty
                    if metadata and isinstance(metadata, dict) and 'theory_uncertainty' in metadata:
                        try:
                            theory_unc = float(metadata['theory_uncertainty'])
                            total_uncertainty = (experimental_uncertainty**2 + theory_unc**2)**0.5
                        except (TypeError, ValueError):
                            pass
                    sigma_deviation = abs(theory_val - exp_val) / total_uncertainty

                    if sigma_deviation < 1.0:
                        validation_status = "PASS"
                    elif sigma_deviation < 2.0:
                        validation_status = "MARGINAL"
                    elif sigma_deviation < 3.0:
                        validation_status = "TENSION"
                    else:
                        validation_status = "FAIL"

                elif bound_type in ("measured", "central_value") and experimental_uncertainty is None:
                    # No uncertainty provided - compute relative error
                    if exp_val != 0:
                        relative_error = abs(theory_val - exp_val) / abs(exp_val)
                        if relative_error < 0.01:  # Within 1%
                            validation_status = "PASS"
                        elif relative_error < 0.05:  # Within 5%
                            validation_status = "MARGINAL"
                        elif relative_error < 0.10:  # Within 10%
                            validation_status = "TENSION"
                        else:
                            validation_status = "FAIL"

                elif bound_type == "lower":
                    # Theory must meet or exceed the lower bound (equality
                    # satisfies it; margin 0 is a pass, e.g. a display echo
                    # of the bound itself). One-sided bounds have no
                    # experimental sigma: store the relative margin
                    # (theory-exp)/exp separately, sigma_deviation = None.
                    if theory_val >= exp_val:
                        validation_status = "PASS"
                        relative_margin = (theory_val - exp_val) / exp_val if exp_val != 0 else None
                    else:
                        validation_status = "FAIL"
                        relative_margin = (exp_val - theory_val) / exp_val if exp_val != 0 else None
                    sigma_deviation = None

                elif bound_type == "upper":
                    # Theory must not exceed the upper bound (equality passes).
                    if theory_val <= exp_val:
                        validation_status = "PASS"
                        relative_margin = (exp_val - theory_val) / exp_val if exp_val != 0 else None
                    else:
                        validation_status = "FAIL"
                        relative_margin = (theory_val - exp_val) / exp_val if exp_val != 0 else None
                    sigma_deviation = None

            except (TypeError, ValueError):
                # Non-numeric values, can't compute sigma
                pass

        entry = RegistryEntry(
            value=value,
            source=source,
            uncertainty=uncertainty,
            status=status,
            metadata=metadata or {},
            experimental_value=experimental_value,
            experimental_uncertainty=experimental_uncertainty,
            experimental_source=experimental_source,
            bound_type=bound_type,
            sigma_deviation=sigma_deviation,
            relative_margin=relative_margin,
            validation_status=validation_status
        )

        self._parameters[path] = entry

        # Track provenance
        if path not in self._provenance:
            self._provenance[path] = []
        self._provenance[path].append(source)

        # Invalidate dependent cached values if using dependency resolver
        if self._dependency_resolver is not None:
            self._dependency_resolver.invalidate(path)

    def patch_eml_description(self, path: str, eml_description: str) -> None:
        """Patch eml_description into an already-registered parameter's metadata."""
        if path in self._parameters and eml_description:
            entry = self._parameters[path]
            if entry.metadata is None:
                entry.metadata = {}
            if not entry.metadata.get('eml_description'):
                entry.metadata['eml_description'] = eml_description

    def backfill_experimental_bound(
        self,
        path: str,
        experimental_value: Optional[float],
        experimental_uncertainty: Optional[float] = None,
        experimental_source: Optional[str] = None,
        bound_type: Optional[str] = None,
    ) -> bool:
        """Attach a declared experimental bound to an already-registered param.

        2026-08 audit fix: ``inject_outputs`` skips re-registration when a
        parameter was already written by an earlier simulation, which
        silently discarded the ``experimental_bound`` declared on the
        owning simulation's Parameter definition. Those predictions then
        carried ``validation_status = NO_DATA`` and were invisible to the
        validation report — the framework's own flagship w0 prediction
        among them. This backfills the bound (never overwriting an
        existing one) and recomputes the verdict.

        Returns True when a bound was attached.
        """
        if path not in self._parameters or experimental_value is None:
            return False
        entry = self._parameters[path]
        if entry.experimental_value is not None:
            return False  # first binding wins; do not overwrite

        entry.experimental_value = experimental_value
        entry.experimental_uncertainty = experimental_uncertainty
        entry.experimental_source = experimental_source
        entry.bound_type = bound_type or "central_value"
        self._recompute_validation(path)
        return True

    def _recompute_validation(self, path: str) -> None:
        """Recompute sigma/verdict for an entry after a bound is attached."""
        entry = self._parameters.get(path)
        if entry is None or entry.experimental_value is None:
            return
        try:
            theory = float(entry.value)
            exp = float(entry.experimental_value)
        except (TypeError, ValueError):
            return

        unc = entry.experimental_uncertainty
        bound = (entry.bound_type or "central_value").lower()

        if bound in ("measured", "central_value") and unc:
            total = float(unc)
            theory_unc = (entry.metadata or {}).get("theory_uncertainty")
            if theory_unc:
                try:
                    total = (float(unc) ** 2 + float(theory_unc) ** 2) ** 0.5
                except (TypeError, ValueError):
                    pass
            sigma = abs(theory - exp) / total
            entry.sigma_deviation = sigma
            if sigma < 1.0:
                entry.validation_status = "PASS"
            elif sigma < 2.0:
                entry.validation_status = "MARGINAL"
            elif sigma < 3.0:
                entry.validation_status = "TENSION"
            else:
                entry.validation_status = "FAIL"
        elif bound == "lower":
            ok = theory >= exp
            entry.validation_status = "PASS" if ok else "FAIL"
            entry.relative_margin = (theory - exp) / exp if exp else None
            entry.sigma_deviation = None
        elif bound == "upper":
            ok = theory <= exp
            entry.validation_status = "PASS" if ok else "FAIL"
            entry.relative_margin = (exp - theory) / exp if exp else None
            entry.sigma_deviation = None

    def update(
        self,
        values: Dict[str, Any],
        *,
        source: str = "v25.0",
        status: str = "DERIVED",
        path_prefix: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Bulk-update the registry from a dict.

        Convenience helper used by the v25.0 Sprint 4 module wiring
        (yukawa_derivation, re_t_sector, vacuum_selection, strong_cp_axion,
        baryogenesis, soft_susy_breaking).  Each key in *values* is registered
        as ``"<path_prefix><key>"`` via :meth:`set_param` with the supplied
        *source* / *status*.

        Non-numeric values (strings, dicts, lists) are stored verbatim — useful
        for status strings like ``"strong CP solved dynamically"``.

        Args:
            values:      Dict of {param_name: value} to register.
            source:      Provenance source string (default "v25.0").
            status:      Status label (default "DERIVED").
            path_prefix: Optional dotted prefix prepended to every key.
            metadata:    Shared metadata dict copied onto every entry.
        """
        if not values:
            return
        shared_meta = dict(metadata) if metadata else {}
        for key, val in values.items():
            full_path = f"{path_prefix}{key}" if path_prefix else key
            try:
                self.set_param(
                    path=full_path,
                    value=val,
                    source=source,
                    status=status,
                    metadata=dict(shared_meta),
                )
            except Exception as exc:  # pragma: no cover - defensive
                warnings.warn(f"PMRegistry.update: could not set {full_path!r}: {exc}")

    # -------------------------------------------------------------------------
    # v25.0 Sprint 4 module wiring (Sprint 4 task #8)
    # -------------------------------------------------------------------------

    def load_v25_modules(self, *, verbose: bool = False) -> Dict[str, Any]:
        """
        Defensively load and register the v25.0 Sprint 4 physics modules.

        Imports and calls each of the six new entry points behind a try/except
        so the build never breaks when a module hasn't landed yet:

            * particle.yukawa_derivation.get_geometric_pmns
            * geometry.re_t_sector.close_vev_gap
            * cosmology.vacuum_selection.prune_landscape
            * particle.strong_cp_axion.solve_strong_cp
            * cosmology.baryogenesis.get_baryogenesis
            * susy.soft_susy_breaking.get_soft_susy_terms

        Each result dict is funnelled through :meth:`update` so all v25.0
        params land in the registry with consistent provenance.

        Args:
            verbose: If True, print a short report per module.

        Returns:
            Dict mapping module name -> the result dict (or {"error": ...}).
        """
        results: Dict[str, Any] = {}

        def _try(module_label: str, importer, prefix: str):
            try:
                result = importer()
            except Exception as exc:  # noqa: BLE001 - we want to swallow everything
                if verbose:
                    print(f"  [SKIP] {module_label}: {exc.__class__.__name__}: {exc}")
                results[module_label] = {"error": f"{exc.__class__.__name__}: {exc}"}
                return
            if not isinstance(result, dict):
                if verbose:
                    print(f"  [SKIP] {module_label}: returned non-dict ({type(result).__name__})")
                results[module_label] = {"error": "non-dict return"}
                return
            self.update(
                values=result,
                source=f"v25.0:{module_label}",
                status="DERIVED",
                path_prefix=prefix,
                metadata={"v25_0_sprint4": True, "module": module_label},
            )
            results[module_label] = result
            if verbose:
                keys = ", ".join(sorted(result.keys()))
                print(f"  [OK]   {module_label}: {keys}")

        if verbose:
            print("\n[INITIALIZATION] Loading v25.0 Sprint 4 modules")
            print("-" * 80)

        # Sprint 4 #2 — Yukawa / PMNS angles
        def _yukawa():
            from metaphysica.simulations.PM.particle.yukawa_derivation import (  # type: ignore
                get_geometric_pmns,
            )
            return get_geometric_pmns()

        # Sprint 4 #3 — Re(T) stabilization
        def _ret():
            from metaphysica.simulations.PM.geometry.re_t_sector import (  # type: ignore
                close_vev_gap,
            )
            return close_vev_gap()

        # Sprint 4 #4 — Landscape pruning
        def _vacua():
            from metaphysica.simulations.PM.cosmology.vacuum_selection import (  # type: ignore
                prune_landscape,
            )
            return prune_landscape()

        # Sprint 4 #5 — Strong CP / axion
        def _strong_cp():
            from metaphysica.simulations.PM.particle.strong_cp_axion import (  # type: ignore
                solve_strong_cp,
            )
            return solve_strong_cp()

        # Sprint 4 #6 — Baryogenesis
        def _baryo():
            from metaphysica.simulations.PM.cosmology.baryogenesis import (  # type: ignore
                get_baryogenesis,
            )
            return get_baryogenesis()

        # Sprint 4 #7 — Soft SUSY breaking
        def _susy():
            from metaphysica.simulations.PM.susy.soft_susy_breaking import (  # type: ignore
                get_soft_susy_terms,
            )
            return get_soft_susy_terms()

        _try("yukawa_derivation",  _yukawa,    prefix="particle.")
        _try("re_t_sector",         _ret,       prefix="geometry.")
        _try("vacuum_selection",    _vacua,     prefix="cosmology.")
        _try("strong_cp_axion",     _strong_cp, prefix="particle.")
        _try("baryogenesis",        _baryo,     prefix="cosmology.")
        _try("soft_susy_breaking",  _susy,      prefix="susy.")

        return results

    # -------------------------------------------------------------------------
    # v26.0 Sprint 5 module wiring (Sprint 5 task #9)
    # -------------------------------------------------------------------------

    def load_v26_modules(self, *, verbose: bool = False) -> Dict[str, Any]:
        """
        Defensively load and register the v26.0 Sprint 5 physics modules.

        Mirrors :meth:`load_v25_modules` but targets the six new
        falsifiability-strengthening modules from PossibleImprovements.txt:

            * cosmology.mirror_dm_relic.derive_mirror_dm_relic
            * cosmology.inflation.derive_inflation_observables
            * particle.axion_photon_coupling.derive_g_a_gamma_gamma
            * particle.higgs_sector.derive_higgs_sector
            * cosmology.cosmological_tensions.resolve_tensions
            * particle.neutrino_sector.derive_neutrino_sector

        Each result dict is funnelled through :meth:`update` so all v26.0
        params land in the registry with consistent provenance.  Every import
        and call is wrapped in a try/except so a missing or half-built module
        skips cleanly without breaking the build.

        Args:
            verbose: If True, print a short report per module.

        Returns:
            Dict mapping module name -> the result dict (or {"error": ...}).
        """
        results: Dict[str, Any] = {}

        def _try(module_label: str, importer, prefix: str):
            try:
                result = importer()
            except Exception as exc:  # noqa: BLE001 - defensive: swallow everything
                if verbose:
                    print(f"  [SKIP] {module_label}: {exc.__class__.__name__}: {exc}")
                results[module_label] = {"error": f"{exc.__class__.__name__}: {exc}"}
                return
            if not isinstance(result, dict):
                if verbose:
                    print(f"  [SKIP] {module_label}: returned non-dict ({type(result).__name__})")
                results[module_label] = {"error": "non-dict return"}
                return
            # The legacy ``"status"`` key is kept in the result dict each
            # ``derive_*`` returns (for human display / backwards
            # compatibility), but every v26.0 module now also exposes a
            # per-module ``<module>_status`` variant — that is what should
            # land in the registry.  Dropping the generic ``"status"`` key
            # here prevents the ``cosmology.status`` / ``particle.status``
            # collisions that otherwise trigger UserWarnings on load.
            values_for_registry = {
                k: v for k, v in result.items() if k != "status"
            }
            self.update(
                values=values_for_registry,
                source=f"v26.0:{module_label}",
                status="DERIVED",
                path_prefix=prefix,
                metadata={"v26_0_sprint5": True, "module": module_label},
            )
            results[module_label] = result
            if verbose:
                keys = ", ".join(sorted(result.keys()))
                print(f"  [OK]   {module_label}: {keys}")

        if verbose:
            print("\n[INITIALIZATION] Loading v26.0 Sprint 5 modules")
            print("-" * 80)

        # Sprint 5 #1 — Mirror DM relic abundance
        def _mirror_dm():
            from metaphysica.simulations.PM.cosmology.mirror_dm_relic import (  # type: ignore
                derive_mirror_dm_relic,
            )
            return derive_mirror_dm_relic()

        # Sprint 5 #2 — Inflation observables (n_s, r)
        def _inflation():
            from metaphysica.simulations.PM.cosmology.inflation import (  # type: ignore
                derive_inflation_observables,
            )
            return derive_inflation_observables()

        # Sprint 5 #3 — Axion-photon coupling g_aγγ
        def _axion_photon():
            from metaphysica.simulations.PM.particle.axion_photon_coupling import (  # type: ignore
                derive_g_a_gamma_gamma,
            )
            return derive_g_a_gamma_gamma()

        # Sprint 5 #4 — Higgs sector (m_h, v_EW)
        def _higgs():
            from metaphysica.simulations.PM.particle.higgs_sector import (  # type: ignore
                derive_higgs_sector,
            )
            return derive_higgs_sector()

        # Sprint 5 #5 — Cosmological tensions (H0, S8)
        def _tensions():
            from metaphysica.simulations.PM.cosmology.cosmological_tensions import (  # type: ignore
                resolve_tensions,
            )
            return resolve_tensions()

        # Sprint 5 #6 — Neutrino sector refinement (Σm_ν)
        def _neutrino():
            from metaphysica.simulations.PM.particle.neutrino_sector import (  # type: ignore
                derive_neutrino_sector,
            )
            return derive_neutrino_sector()

        _try("mirror_dm_relic",        _mirror_dm,    prefix="cosmology.")
        _try("inflation",              _inflation,    prefix="cosmology.")
        _try("axion_photon_coupling",  _axion_photon, prefix="particle.")
        _try("higgs_sector",           _higgs,        prefix="particle.")
        _try("cosmological_tensions",  _tensions,     prefix="cosmology.")
        _try("neutrino_sector",        _neutrino,     prefix="particle.")

        return results

    def load_v25_v26_modules(self, *, verbose: bool = False) -> Dict[str, Any]:
        """
        Convenience wrapper that loads both v25.0 and v26.0 module suites.

        Returns a merged dict keyed by ``"v25_0"`` and ``"v26_0"`` containing
        the per-module result maps from :meth:`load_v25_modules` and
        :meth:`load_v26_modules` respectively.
        """
        return {
            "v25_0": self.load_v25_modules(verbose=verbose),
            "v26_0": self.load_v26_modules(verbose=verbose),
        }

    # -------------------------------------------------------------------------
    # v27.0 Sprint T6 module wiring (Sprint T6 Tier 3 architectural kickoffs)
    # -------------------------------------------------------------------------

    def load_v27_modules(self, *, verbose: bool = False) -> Dict[str, Any]:
        """
        Defensively load and register the v27.0 Sprint T6 physics modules.

        Mirrors :meth:`load_v25_modules` / :meth:`load_v26_modules` but targets
        the Sprint T6 Tier 3 architectural kickoffs:

            * particle.lhc_predictions.get_lhc_predictions  (Sprint T6 #4, T3.7)

        Each result dict is funnelled through :meth:`update` so all v27.0
        params land in the registry with consistent provenance.  Every import
        and call is wrapped in a try/except so a missing or half-built module
        skips cleanly without breaking the build.

        Args:
            verbose: If True, print a short report per module.

        Returns:
            Dict mapping module name -> the result dict (or {"error": ...}).
        """
        results: Dict[str, Any] = {}

        def _try(module_label: str, importer, prefix: str):
            try:
                result = importer()
            except Exception as exc:  # noqa: BLE001 - defensive: swallow everything
                if verbose:
                    print(f"  [SKIP] {module_label}: {exc.__class__.__name__}: {exc}")
                results[module_label] = {"error": f"{exc.__class__.__name__}: {exc}"}
                return
            if not isinstance(result, dict):
                if verbose:
                    print(f"  [SKIP] {module_label}: returned non-dict ({type(result).__name__})")
                results[module_label] = {"error": "non-dict return"}
                return
            values_for_registry = {
                k: v for k, v in result.items() if k != "status"
            }
            self.update(
                values=values_for_registry,
                source=f"v27.0:{module_label}",
                status="PREDICTED",
                path_prefix=prefix,
                metadata={"v27_0_sprint_t6": True, "module": module_label},
            )
            results[module_label] = result
            if verbose:
                keys = ", ".join(sorted(result.keys()))
                print(f"  [OK]   {module_label}: {keys}")

        if verbose:
            print("\n[INITIALIZATION] Loading v27.0 Sprint T6 modules")
            print("-" * 80)

        # Sprint T6 #4 (Tier 3 T3.7) -- LHC / HL-LHC SUSY spectrum predictions
        def _lhc():
            from metaphysica.simulations.PM.particle.lhc_predictions import (  # type: ignore
                get_lhc_predictions,
            )
            return get_lhc_predictions()

        _try("lhc_predictions", _lhc, prefix="particle.")

        return results

    # -------------------------------------------------------------------------
    # Dependency Resolution (v20)
    # -------------------------------------------------------------------------

    def _init_dependency_resolver(self) -> None:
        """
        Initialize the dependency resolver with the PM dependency graph.

        Called automatically during registry initialization if the
        dependency_resolver module is available.
        """
        if not DEPENDENCY_RESOLVER_AVAILABLE:
            warnings.warn("Dependency resolver not available - auto-resolution disabled")
            return

        try:
            self._dependency_graph = build_pm_dependency_graph()
            self._dependency_resolver = DependencyResolver(self._dependency_graph)
            self._seed_values = build_seed_values()
        except Exception as e:
            warnings.warn(f"Failed to initialize dependency resolver: {e}")
            self._dependency_graph = None
            self._dependency_resolver = None

    def enable_auto_resolve(self, enabled: bool = True) -> None:
        """
        Enable or disable automatic dependency resolution on get().

        When enabled, calling get() for a parameter not in the registry
        will attempt to compute it using the dependency resolver.

        Args:
            enabled: True to enable, False to disable
        """
        self._auto_resolve = enabled

    def is_auto_resolve_enabled(self) -> bool:
        """Check if auto-resolution is enabled."""
        return self._auto_resolve

    def set_seed_values(self, seeds: Dict[str, Any]) -> None:
        """
        Set base seed values for dependency resolution.

        These values are used as the Level 0 inputs when computing
        derived parameters.

        Args:
            seeds: Dictionary mapping seed parameter paths to values
        """
        self._seed_values.update(seeds)
        # Invalidate resolver cache when seeds change
        if self._dependency_resolver is not None:
            self._dependency_resolver.clear_cache()

    def get_seed_values(self) -> Dict[str, Any]:
        """Get the current seed values."""
        return dict(self._seed_values)

    def register_dependency(
        self,
        param: str,
        depends_on: List[str] = None,
        compute_fn: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a parameter dependency in the dependency graph.

        This allows simulations to define how their output parameters
        depend on input parameters, enabling automatic resolution.

        Args:
            param: Parameter path (e.g., "cosmology.H0_geometric")
            depends_on: List of parameter paths this parameter depends on
            compute_fn: Function to compute this parameter.
                       Signature: fn(dep_values: Dict[str, Any]) -> Any
            metadata: Optional metadata (level, description, etc.)

        Raises:
            RuntimeError: If dependency resolver not available
            CycleDetectedError: If adding this parameter creates a cycle

        Example:
            registry.register_dependency(
                "cosmology.H0_geometric",
                depends_on=["geometry.k_gimel", "seeds.mephorash_chi"],
                compute_fn=lambda deps: 71.55 * (deps["geometry.k_gimel"] * deps["seeds.mephorash_chi"]) ** 0.1
            )
        """
        if self._dependency_graph is None:
            raise RuntimeError("Dependency resolver not available")

        self._dependency_graph.register(
            param=param,
            depends_on=depends_on or [],
            compute_fn=compute_fn,
            metadata=metadata
        )

    def unregister_dependency(self, param: str) -> None:
        """
        Remove a parameter from the dependency graph.

        Args:
            param: Parameter path to remove
        """
        if self._dependency_graph is not None:
            self._dependency_graph.unregister(param)

    def resolve(self, param: str, store_result: bool = True) -> Any:
        """
        Resolve a parameter using the dependency graph.

        This computes the parameter value by first resolving all its
        dependencies, then applying its compute function.

        Args:
            param: Parameter path to resolve
            store_result: If True, store the resolved value in the registry

        Returns:
            Resolved parameter value

        Raises:
            RuntimeError: If dependency resolver not available
            KeyError: If parameter not in dependency graph
            CycleDetectedError: If circular dependency detected
            MissingComputeFunctionError: If no compute function defined
        """
        if self._dependency_resolver is None:
            raise RuntimeError("Dependency resolver not available")

        value = self._dependency_resolver.resolve(param, self._seed_values)

        if store_result:
            self.set_param(
                path=param,
                value=value,
                source="dependency_resolver",
                status="DERIVED",
                metadata={'resolved': True}
            )

        return value

    def _resolve_dependency(self, path: str) -> Any:
        """
        Internal method to resolve a dependency.

        Called by get() when auto_resolve is enabled.

        Args:
            path: Parameter path to resolve

        Returns:
            Resolved value or None if resolution fails
        """
        if self._dependency_resolver is None:
            return None

        if not self._dependency_graph.has_param(path):
            return None

        try:
            value = self._dependency_resolver.resolve(path, self._seed_values)
            # Store in registry for future access
            self.set_param(
                path=path,
                value=value,
                source="auto_resolved",
                status="DERIVED",
                metadata={'auto_resolved': True}
            )
            return value
        except Exception:
            return None

    def resolve_all(self, params: List[str], store_results: bool = True) -> Dict[str, Any]:
        """
        Resolve multiple parameters at once.

        Args:
            params: List of parameter paths to resolve
            store_results: If True, store resolved values in registry

        Returns:
            Dictionary mapping parameter paths to resolved values
        """
        if self._dependency_resolver is None:
            raise RuntimeError("Dependency resolver not available")

        results = self._dependency_resolver.resolve_all(params, self._seed_values)

        if store_results:
            for param, value in results.items():
                self.set_param(
                    path=param,
                    value=value,
                    source="dependency_resolver",
                    status="DERIVED",
                    metadata={'resolved': True}
                )

        return results

    def get_dependency_graph(self) -> Optional['DependencyGraph']:
        """
        Get the dependency graph instance.

        Returns:
            DependencyGraph instance or None if not available
        """
        return self._dependency_graph

    def get_dependency_resolver(self) -> Optional['DependencyResolver']:
        """
        Get the dependency resolver instance.

        Returns:
            DependencyResolver instance or None if not available
        """
        return self._dependency_resolver

    def get_computation_order(self, param: str) -> List[str]:
        """
        Get the order in which parameters must be computed for a target.

        Args:
            param: Target parameter path

        Returns:
            List of parameters in computation order, ending with target
        """
        if self._dependency_graph is None:
            return [param]
        return self._dependency_graph.get_computation_order(param)

    def get_dependency_level(self, param: str) -> int:
        """
        Get the dependency level of a parameter.

        Level 0: Seeds (no dependencies)
        Level 1: Direct derivations from seeds
        Level 2+: Higher-order derivations

        Args:
            param: Parameter path

        Returns:
            Integer level (0 = seed)
        """
        if self._dependency_graph is None:
            return 0
        return self._dependency_graph.get_level(param)

    def invalidate_cache(self, param: str = None) -> None:
        """
        Invalidate cached values in the dependency resolver.

        If param is specified, invalidates that parameter and all dependents.
        If param is None, clears the entire cache.

        Args:
            param: Optional parameter path to invalidate
        """
        if self._dependency_resolver is None:
            return

        if param is None:
            self._dependency_resolver.clear_cache()
        else:
            self._dependency_resolver.invalidate(param)

    def get_resolver_stats(self) -> Dict[str, Any]:
        """
        Get statistics about dependency resolution.

        Returns:
            Dictionary with cache stats and computation log
        """
        if self._dependency_resolver is None:
            return {'available': False}

        return {
            'available': True,
            'auto_resolve_enabled': self._auto_resolve,
            'cache_stats': self._dependency_resolver.get_cache_stats(),
            'registered_params': len(self._dependency_graph._dependencies) if self._dependency_graph else 0,
        }

    # -------------------------------------------------------------------------
    # Formula Management
    # -------------------------------------------------------------------------

    def add_formula(
        self,
        formula: 'Formula' = None,
        source: str = "",
        *,
        arithma: Any = None,
        eml: Any = None,
        value: Optional[float] = None,
        env: Optional[Dict[str, float]] = None,
        triple_rel: Optional[float] = None,
        triple_abs: Optional[float] = None,
    ) -> None:
        """
        Add a formula to the registry with optional triple-track cross-check.

        Phase E.2 extension: when both a symbolic view (arithma or eml) and
        a ``value`` are present, ``triple_validator.triple_assert`` runs at
        registration time and halts the build on disagreement.

        Args:
            formula: Formula instance to add
            source: Source simulation file identifier
            arithma: Optional arithma.Expression for symbolic cross-check.
            eml: Optional eml_math.EMLPoint for universal-math cross-check.
            value: Optional canonical float for cross-check.
            env: Variable bindings used when evaluating symbolic views.
            triple_rel: Relative tolerance override.
            triple_abs: Absolute tolerance override.
        """
        if formula is None:
            raise ValueError("add_formula: formula argument is required")

        # Merge kwarg overrides into the Formula record.
        if arithma is not None:
            formula.arithma = arithma
        if eml is not None:
            formula.eml = eml
        if value is not None:
            formula.value = value
        if env is not None:
            formula.triple_env = dict(env)
        if triple_rel is not None:
            formula.triple_rel = triple_rel
        if triple_abs is not None:
            formula.triple_abs = triple_abs

        # Triple-track classification + cross-check.
        has_arithma = getattr(formula, "arithma", None) is not None
        has_eml = getattr(formula, "eml", None) is not None
        has_value = getattr(formula, "value", None) is not None

        if has_value and (has_arithma or has_eml):
            try:
                from metaphysica.simulations.core.triple_validator import (
                    triple_assert,
                )
                triple_assert(
                    formula.arithma,
                    formula.eml,
                    float(formula.value),
                    env=formula.triple_env or {},
                    rel=formula.triple_rel,
                    abs_=formula.triple_abs,
                    name=formula.id,
                )
            except ImportError:
                pass

            if has_arithma and has_eml:
                formula.triple_status = "OK"
            elif has_arithma:
                formula.triple_status = "ARITHMA_ONLY"
            else:
                formula.triple_status = "EML_ONLY"
        elif has_value:
            formula.triple_status = "FLOAT_ONLY"
        else:
            formula.triple_status = ""

        # Cache symbolic-side rendered representations once.
        if has_arithma and not formula.arithma_latex:
            try:
                formula.arithma_latex = formula.arithma.to_latex()
            except Exception:
                formula.arithma_latex = ""

        # Capture arithma.to_compact() when available. Sprint 3.1 adds
        # to_compact/from_compact to the Arithma wheel; until that lands
        # (or in dev envs where the wheel isn't built) we degrade gracefully
        # to ``None`` rather than failing registration.
        if has_arithma and formula.arithma_compact is None:
            try:
                if hasattr(formula.arithma, "to_compact"):
                    formula.arithma_compact = formula.arithma.to_compact()
                else:
                    formula.arithma_compact = None
            except Exception:
                formula.arithma_compact = None

        if has_eml and formula.eml_tree_compact is None:
            compact_obj = None
            for method in ("to_compact", "as_compact", "compact"):
                fn = getattr(formula.eml, method, None)
                if callable(fn):
                    try:
                        compact_obj = fn()
                        break
                    except Exception:
                        compact_obj = None
            if compact_obj is None:
                try:
                    compact_obj = repr(formula.eml)
                except Exception:
                    compact_obj = ""
            formula.eml_tree_compact = compact_obj

        if formula.id in self._formulas:
            warnings.warn(f"Overwriting formula {formula.id}")

        self._formulas[formula.id] = FormulaEntry(formula=formula, source=source)

    def get_formula(self, formula_id: str) -> Optional['Formula']:
        """
        Get a formula by ID.

        Args:
            formula_id: Formula ID (e.g., "proton-lifetime")

        Returns:
            Formula instance or None if not found
        """
        entry = self._formulas.get(formula_id)
        return entry.formula if entry else None

    def has_formula(self, formula_id: str) -> bool:
        """
        Check if a formula exists.

        Args:
            formula_id: Formula ID

        Returns:
            True if formula exists, False otherwise
        """
        return formula_id in self._formulas

    # -------------------------------------------------------------------------
    # Section Management
    # -------------------------------------------------------------------------

    def add_section_content(
        self,
        section_id: str,
        content: 'SectionContent'
    ) -> None:
        """
        Add section content to the registry.

        Args:
            section_id: Section identifier (e.g., "2", "4", "5")
            content: SectionContent instance

        Note:
            For appendices (where appendix=True), the subsection_id is used
            as the storage key to allow multiple appendices. The section_id
            indicates which section the appendix relates to.
        """
        # Use subsection_id as key for appendices (e.g., "A", "B", "C"...)
        key = section_id
        if content.appendix and content.subsection_id:
            key = content.subsection_id

        if key in self._sections:
            existing = self._sections[key].content
            # Only warn if content actually differs (not during normal re-registration)
            if (existing.title != content.title or
                existing.abstract != content.abstract or
                existing.content_blocks != content.content_blocks):
                warnings.warn(f"Overwriting section {key} with different content")

        self._sections[key] = SectionEntry(content=content)

    def get_section(self, section_id: str) -> Optional['SectionContent']:
        """
        Get section content by ID.

        Args:
            section_id: Section identifier

        Returns:
            SectionContent instance or None if not found
        """
        entry = self._sections.get(section_id)
        return entry.content if entry else None

    def has_section(self, section_id: str) -> bool:
        """
        Check if a section exists.

        Args:
            section_id: Section identifier

        Returns:
            True if section exists, False otherwise
        """
        return section_id in self._sections

    # -------------------------------------------------------------------------
    # Export Methods
    # -------------------------------------------------------------------------

    def export_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Export all parameters as a dictionary with full experimental validation data.

        Returns:
            Dictionary mapping parameter paths to their full entries including:
            - value: Theory prediction or established value
            - source: Source simulation or ESTABLISHED:* citation
            - uncertainty: Uncertainty on theory prediction
            - status: Parameter status (ESTABLISHED, GEOMETRIC, DERIVED, etc.)
            - experimental_value: Experimental measurement for comparison
            - experimental_uncertainty: 1-sigma uncertainty on experiment
            - experimental_source: Citation for experimental value
            - bound_type: Type of bound (measured, upper, lower, range)
            - sigma_deviation: Number of sigmas between theory and experiment
              (None for one-sided bounds)
            - relative_margin: Relative margin (theory-exp)/exp for one-sided bounds
            - validation_status: PASS, MARGINAL, TENSION, FAIL, or NO_DATA
            - units: Units string from entry metadata (if any)
        """
        result = {}
        for path, entry in self._parameters.items():
            # eml_description is stored in ParameterEntry.metadata if set by simulation
            eml_desc = (entry.metadata or {}).get('eml_description', '')

            result[path] = {
                'value': entry.value,
                'source': entry.source,
                'uncertainty': entry.uncertainty,
                'status': entry.status,
                'timestamp': entry.timestamp,
                'metadata': entry.metadata,
                # Experimental comparison fields
                'experimental_value': entry.experimental_value,
                'experimental_uncertainty': entry.experimental_uncertainty,
                'experimental_source': entry.experimental_source,
                'bound_type': entry.bound_type,
                # Validation results
                'sigma_deviation': entry.sigma_deviation,
                'relative_margin': getattr(entry, 'relative_margin', None),
                'validation_status': entry.validation_status,
                # EML Mirror Phase description
                'eml_description': eml_desc,
                # Units live in metadata; surface them for datasheet consumers
                'units': (entry.metadata or {}).get('units'),
            }
        return result

    def export_formulas(self) -> Dict[str, Dict[str, Any]]:
        """
        Export all formulas as a dictionary.

        Returns:
            Dictionary mapping formula IDs to formula data
        """
        result = {}
        for formula_id, entry in self._formulas.items():
            f = entry.formula
            # Generate title from description if not set
            title = getattr(f, 'title', None)
            if not title and f.description:
                title = f.description.split('.')[0].strip()[:80]

            # Enrich derivation with source if missing
            derivation = f.derivation
            if derivation is None:
                derivation = {}
            if isinstance(derivation, dict) and not derivation.get('source') and entry.source:
                derivation = dict(derivation)
                derivation['source'] = entry.source

            result[formula_id] = {
                'id': f.id,
                'label': f.label,
                'latex': f.latex,
                'plain_text': f.plain_text,
                'category': f.category,
                'description': f.description,
                'title': title,
                'input_params': f.input_params or f.inputParams,
                'output_params': f.output_params or f.outputParams,
                'derivation': derivation,
                'terms': f.terms,
                'eml_latex': getattr(f, 'eml_latex', ''),
                'eml_tree_str': getattr(f, 'eml_tree_str', ''),
                'eml_description': getattr(f, 'eml_description', ''),
                # Triple-track fields (Phase E.2 + Sprint 3.2)
                'arithma_latex': getattr(f, 'arithma_latex', ''),
                'arithma_compact': getattr(f, 'arithma_compact', None),
                'eml_tree_compact': getattr(f, 'eml_tree_compact', None),
                'triple_status': getattr(f, 'triple_status', ''),
                'value': getattr(f, 'value', None),
                # Formula.references exists in the schema but was never
                # populated by any simulation, which is why all 230
                # bibliography entries were orphans -- defined, cited by
                # nothing. Explicit per-formula ids are carried through here;
                # the module-level fallback is applied downstream, where the
                # reference list is actually in scope (see
                # run_all_simulations._attach_module_references).
                'references': list(getattr(f, 'references', None) or []),
                'source_simulation': entry.source,
                'timestamp': entry.timestamp,
            }
        return result

    def export_sections(self) -> Dict[str, Dict[str, Any]]:
        """
        Export all sections as a dictionary.

        Returns:
            Dictionary mapping section IDs to section data
        """
        result = {}
        for section_id, entry in self._sections.items():
            s = entry.content
            # Build content_blocks with all fields
            content_blocks = []
            for block in s.content_blocks:
                block_data = {
                    'type': block.type,
                    'content': block.content,
                }
                if block.formula_id:
                    block_data['formula_id'] = block.formula_id
                if block.label:
                    block_data['label'] = block.label
                    block_data['equationNumber'] = block.label
                if block.level:
                    block_data['level'] = block.level
                if block.items:
                    block_data['items'] = block.items
                if block.headers:
                    block_data['headers'] = block.headers
                if block.rows:
                    block_data['rows'] = block.rows
                content_blocks.append(block_data)

            # Use 'id' as expected by website renderer (not 'section_id')
            # Determine order based on appendix flag
            # v24.2: Special section ordering for non-numeric section_ids
            SPECIAL_SECTION_ORDER = {
                "validation": 8,     # After Discussion (7), before Appendices
                "thermal-time": 1.5, # After Foundations (1), before Methodology (2)
            }

            if s.appendix and s.subsection_id:
                # Appendices come after main sections (100+)
                # Handle subsection_id formats like "R" or "R.1"
                appendix_letter = s.subsection_id[0].upper()
                order = 100 + ord(appendix_letter) - ord('A')
            elif s.section_id and s.section_id[0].isdigit():
                order = int(s.section_id.split('.')[0])
            elif s.section_id in SPECIAL_SECTION_ORDER:
                order = SPECIAL_SECTION_ORDER[s.section_id]
            else:
                order = 99

            result[section_id] = {
                'id': s.section_id,
                'appendix': s.appendix,  # Boolean: render at end of paper
                'subsection_id': s.subsection_id,  # Appendix letter (A, B, C...)
                'type': 'appendix' if s.appendix else 'section',  # For renderer compatibility
                'section_type': s.section_type or ('appendix' if s.appendix else 'section'),
                'title': s.title,
                'shortTitle': s.title,
                'order': order,
                'abstract': s.abstract,
                'contentBlocks': content_blocks,  # camelCase for website compatibility
                'content_blocks': content_blocks,  # snake_case for Python compatibility
                'formulaRefs': s.formula_refs,
                'paramRefs': s.param_refs,
                'formula_refs': s.formula_refs,
                'param_refs': s.param_refs,
                'timestamp': entry.timestamp,
            }
        return result

    def export_provenance(self) -> Dict[str, List[str]]:
        """
        Export provenance tracking.

        Returns:
            Dictionary mapping output paths to source simulation IDs
        """
        return dict(self._provenance)

    # -------------------------------------------------------------------------
    # Mismatch Tracking
    # -------------------------------------------------------------------------

    def warn_mismatch(self, path: str, new_value: Any, new_source: str) -> None:
        """
        Warn if setting a parameter that already exists with a different value.

        Args:
            path: Parameter path
            new_value: New value being set
            new_source: Source of new value
        """
        if path not in self._parameters:
            return

        old_entry = self._parameters[path]
        old_value = old_entry.value

        # Check for significant differences (handle floats with tolerance)
        try:
            if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
                if old_value != 0:
                    rel_diff = abs(new_value - old_value) / abs(old_value)
                    if rel_diff > 0.01:  # 1% tolerance
                        self._log_mismatch(path, old_value, old_entry.source, new_value, new_source)
            elif old_value != new_value:
                self._log_mismatch(path, old_value, old_entry.source, new_value, new_source)
        except Exception:
            # If comparison fails, log it
            if old_value != new_value:
                self._log_mismatch(path, old_value, old_entry.source, new_value, new_source)

    def _log_mismatch(
        self,
        path: str,
        old_value: Any,
        old_source: str,
        new_value: Any,
        new_source: str
    ) -> None:
        """
        Log a parameter mismatch.

        Args:
            path: Parameter path
            old_value: Previous value
            old_source: Source of previous value
            new_value: New value
            new_source: Source of new value
        """
        mismatch = {
            'path': path,
            'old_value': old_value,
            'old_source': old_source,
            'new_value': new_value,
            'new_source': new_source,
            'timestamp': datetime.now().isoformat(),
        }

        self._mismatches.append(mismatch)

        warnings.warn(
            f"Parameter mismatch for '{path}':\n"
            f"  Old: {old_value} (from {old_source})\n"
            f"  New: {new_value} (from {new_source})"
        )

    def get_mismatches(self) -> List[Dict[str, Any]]:
        """
        Get all logged mismatches.

        Returns:
            List of mismatch records
        """
        return list(self._mismatches)

    def validate_all(self) -> List[str]:
        """
        Return list of validation issues.

        Returns:
            List of issue descriptions
        """
        issues = []
        for path, entry in self._parameters.items():
            if entry.status == "DERIVED" and not self._provenance.get(path):
                issues.append(f"{path}: DERIVED but no source simulation")
        return issues

    # -------------------------------------------------------------------------
    # Accuracy Validation (Sigma Deviation Computation)
    # -------------------------------------------------------------------------

    def compute_sigma_deviation(
        self,
        predicted_value: float,
        experimental_path: str
    ) -> Dict[str, Any]:
        """
        Compute sigma deviation between predicted and experimental values.

        Args:
            predicted_value: The theory prediction
            experimental_path: Path to experimental value (e.g., "desi.w0")

        Returns:
            Dictionary with deviation analysis:
            {
                'predicted': float,
                'experimental': float,
                'uncertainty': float,
                'sigma': float,
                'status': str,  # 'EXCELLENT'/'GOOD'/'ACCEPTABLE'/'TENSION'
                'source': str
            }
        """
        if not self.has_param(experimental_path):
            return {
                'predicted': predicted_value,
                'experimental': None,
                'uncertainty': None,
                'sigma': None,
                'status': 'MISSING_DATA',
                'source': None
            }

        entry = self.get_entry(experimental_path)
        exp_value = entry.value
        uncertainty = entry.uncertainty or 0.0

        if uncertainty == 0:
            # No uncertainty available
            sigma = None
            status = 'NO_UNCERTAINTY'
        else:
            sigma = abs(predicted_value - exp_value) / uncertainty
            if sigma < 1.0:
                status = 'EXCELLENT'
            elif sigma < 2.0:
                status = 'GOOD'
            elif sigma < 3.0:
                status = 'ACCEPTABLE'
            else:
                status = 'TENSION'

        return {
            'predicted': predicted_value,
            'experimental': exp_value,
            'uncertainty': uncertainty,
            'sigma': sigma,
            'status': status,
            'source': entry.source
        }

    def validate_prediction(
        self,
        prediction_path: str,
        experimental_path: str,
        metadata_key: str = 'validation'
    ) -> Dict[str, Any]:
        """
        Validate a prediction against experimental data and store result.

        Args:
            prediction_path: Path to predicted parameter
            experimental_path: Path to experimental parameter
            metadata_key: Key to store validation result in metadata

        Returns:
            Validation result dictionary
        """
        if not self.has_param(prediction_path):
            raise KeyError(f"Prediction '{prediction_path}' not in registry")

        pred_entry = self.get_entry(prediction_path)
        result = self.compute_sigma_deviation(pred_entry.value, experimental_path)

        # Store validation in metadata
        pred_entry.metadata[metadata_key] = result

        return result

    def get_accuracy_report(self) -> Dict[str, Any]:
        """
        Generate accuracy report for all predictions with validation data.

        Returns:
            Dictionary with accuracy statistics and details
        """
        report = {
            'excellent': [],  # < 1σ
            'good': [],       # 1-2σ
            'acceptable': [], # 2-3σ
            'tension': [],    # > 3σ
            'unvalidated': [],
            'summary': {}
        }

        for path, entry in self._parameters.items():
            if entry.status in ('DERIVED', 'PREDICTED'):
                validation = entry.metadata.get('validation')
                if validation:
                    status = validation.get('status', 'UNKNOWN')
                    item = {
                        'path': path,
                        'predicted': validation.get('predicted'),
                        'experimental': validation.get('experimental'),
                        'sigma': validation.get('sigma'),
                        'source': validation.get('source')
                    }
                    if status == 'EXCELLENT':
                        report['excellent'].append(item)
                    elif status == 'GOOD':
                        report['good'].append(item)
                    elif status == 'ACCEPTABLE':
                        report['acceptable'].append(item)
                    elif status == 'TENSION':
                        report['tension'].append(item)
                else:
                    report['unvalidated'].append(path)

        # Compute summary
        total = (len(report['excellent']) + len(report['good']) +
                 len(report['acceptable']) + len(report['tension']))
        report['summary'] = {
            'total_validated': total,
            'excellent_count': len(report['excellent']),
            'good_count': len(report['good']),
            'acceptable_count': len(report['acceptable']),
            'tension_count': len(report['tension']),
            'unvalidated_count': len(report['unvalidated'])
        }

        return report
