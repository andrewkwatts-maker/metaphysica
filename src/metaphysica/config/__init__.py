#!/usr/bin/env python3

# ===========================================================================
# TOPOLOGICAL SEED CONSTANTS (v2.2.0 — mystical overlay stripped)
# ===========================================================================
# The 7 canonical topological seeds. Each entry is a plain integer / real
# derived from G2 manifold topology or from a documented experimental
# calibration; no independent physical meaning is attached to their names.
#
#   1.0        watts_constant    - observer unity anchor
#   24         B3                - third Betti number of the G2 manifold (SSoT seed)
#   135        shadow_sector     - visible-sector integer (135 = 288 - 153; see notes)
#   72 / 144   chi_eff / chi_eff_total - per-shadow / total Euler characteristic
#   153        christ_constant   - joint-closure integer (fitted decomposition; not a first-principles derivation)
#   163        sterile_sector    - sterile-sector integer (fitted decomposition)
#   288        roots_total       - 12 x b3 total root count
#
# The prior release carried an additional Hebrew-gematria / Gnostic naming
# overlay for these values. That overlay carries no physical meaning and has
# been extracted to the gitignored file `src/metaphysica/_gnostic_aliases.py`
# for the author's personal use (see `docs/local-overrides.md`).
# ===========================================================================

"""
config.py - Single Source of Truth for Principia Metaphysica Framework

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
Licensed under the MIT License. See LICENSE file for details.

This configuration file contains ALL theoretical values, phenomenological parameters,
and computational settings used throughout the Principia Metaphysica project.

Version: 17.2-ABSOLUTE
Last Updated: January 2026

CHANGELOG v12.5:
- v12.0: Added KKGravitonParameters, FinalNeutrinoMasses
- v12.1: Updated alpha4/alpha5 to NuFIT 6.0 (theta_23 = 45.0°)
- v12.2: Hybrid neutrino suppression (base 39.81 × flux 3.12 = 124.22)
- v12.3: Fixed neutrino mass unit bug (1M× error), delta_m² calculation
- v12.4: CRITICAL FIX - M_Pl standardized to reduced mass (2.435e18 GeV)
  * Fixes 20% inconsistency between PhenomenologyParameters and ModuliParameters
  * All formulas now use M_PLANCK_REDUCED consistently
  * Added dual derivations for Higgs mass and M_GUT
- v12.5: Re(T) constrained from Higgs mass (OPEN PROBLEM — see HiggsMassParameters)
  * Three competing Re(T) values: 1.833 (geometric), 7.086 (baryon asymmetry), 9.865 (Higgs inversion)
  * Inverted formula: Re(T) = (λ₀ - λ_eff) / (κ y_t²) with m_h = 125.10 GeV → 9.865
  * Baryon asymmetry uses Re(T) = 7.086 (calibrated for BBN match)
  * All rigor gaps resolved: Wilson phases, thermal friction, CKM CP, flux unification
- v12.9: Pneuma racetrack vacuum selection (dynamically selected via G2 topology)
- v13.0: Fermion chirality mechanism resolved (n_gen = 24/8 = 3 from spinor saturation)
  * Added FermionChiralityParameters class
  * Generation count: N_flux / spinor_DOF = 24 / 8 = 3
  * Pneuma chiral filter: gamma^5 T_mu coupling
  * Comparison to intersecting branes and flux compactification
- v14.0: Complete gauge sector closure
  * Proton Decay Rate Uncertainty RESOLVED via TCS cycle separation (d/R=0.12, S=2.1)
  * Doublet-Triplet Splitting RESOLVED via TCS discrete torsion on b2=4 cycles
  * All gauge unification critiques now geometrically derived
  * τ_p = 8.15×10^34 years (4.9× Super-K, from simulation output)
- v14.1: Final critique resolution
  * Doublet-Triplet mechanism upgraded to Native TCS Topological Filter
  * Triplets shunted to shadow sector (not just lifted) - no Wilson line tuning
  * Breaking Chain Selection RESOLVED: Pati-Salam geometrically preferred
  * Pati-Salam arises from SO(24,2) → G₂ projection with Pneuma (54_H) alignment
  * Added BreakingChainParameters class with intermediate scale M_PS = 1.2×10^12 GeV
  * FIXES: Consolidated proton decay to single canonical value (8.15e34 years)
  * FIXES: Deprecated ProtonLifetimeParameters (use GeometricProtonDecayParameters)
  * FIXES: Fixed KKGravitonParameters 10^13x bug (now 5.0 TeV from R_c^-1)
  * FIXES: Clarified Higgs mass as phenomenological INPUT (not prediction)
  * FIXES: Consolidated neutrino params to NuFIT 6.0 (2024)
  * FIXES: Fixed HiggsVEVs (V_U was 174 GeV, should be ~245 GeV for tan β=10)
"""

import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

from .version import (
    STERILE_STATUS,
    TRANSPARENCY_LEVEL,
    VERSION,
    VERSION_SHORT,
)

# The FormulasRegistry import must stay the first thing the package pulls in:
# it reaches back into metaphysica.simulations, which imports metaphysica.config
# again. Keeping it first preserves the pre-existing (and pre-existingly
# warned-about) partial-initialisation behaviour exactly.
from .registry import _REGISTRY_AVAILABLE, _ssot_dim

if _REGISTRY_AVAILABLE:
    from .registry import FormulasRegistry, _get_registry

from .formula import (
    AppendixMetadata,
    ContentBlock,
    Formula,
    FormulaCategory,
    FormulaDerivation,
    FormulaDerivationStep,
    FormulaInfoItem,
    FormulaReference,
    FormulaSubComponent,
    FormulaTerm,
    LearningResource,
    ParameterCategory,
    ParameterMetadata,
    SectionMetadata,
)

from .core_formulas import (
    CoreFormulas,
)

from .constants import (
    DimensionalStructure,
    FrameworkStatistics,
    FundamentalConstants,
    SMParameterRegistry,
)

from .settings import (
    ComputationalSettings,
)

from .reference_data import (
    RealWorldData,
)

from .parameters import (
    AnomalyCancellation,
    BreakingChainParameters,
    BridgePhysicsParameters,
    CMBBubbleParameters,
    CycleIntersectionNumbers,
    DoubletTripletSplittingParameters,
    EFTValidityParameters,
    FRTTauParameters,
    FermionChiralityParameters,
    FinalNeutrinoMasses,
    FittedParameters,
    FluxQuantization,
    G2SpinorGeometryParameters,
    GaugeUnificationParameters,
    GeometricProtonDecayParameters,
    GeometricYukawaParameters,
    HiddenVariableParameters,
    HiggsMassParameters,
    HiggsVEVs,
    KKGravitonParameters,
    LandscapeParameters,
    LatticeDispersionParameters,
    MashiachStabilizationParameters,
    MasterActionParameters,
    MirrorSectorParameters,
    ModuliParameters,
    MultiTimeParameters,
    NeutrinoMassMatrix,
    NeutrinoParameters,
    PhenomenologyParameters,
    PneumaRacetrackParameters,
    PneumaVielbeinParameters,
    ProtonLifetimeParameters,
    QuantumFRStabilityParameters,
    RightHandedNeutrinoMasses,
    SeesawParameters,
    SharedDimensionsParameters,
    Sp2RGaugeFixingParameters,
    SubleadingDispersionParameters,
    TCSTopologyParameters,
    ThermalTimeParameters,
    TopologicalCPPhaseParameters,
    TorsionClass,
    TwoTimePhysics,
    V21BridgeParameters,
    V21UnifiedTimePhysics,
    V61Predictions,
    WilsonLinePhases,
    XYGaugeBosonParameters,
)

from .nomenclature import (
    BraneNomenclature,
    G2DirectionNomenclature,
    HebrewPhysicsNomenclature,
    ShadowDimensionNomenclature,
)

from .config_dict import (
    get_config_dict,
)

from .validation import (
    validate_all,
    validate_dimensional_consistency,
    validate_generation_count,
    validate_swampland_constraint,
)


# ==============================================================================
# v14.1 SIMULATION STATUS - DERIVED vs HARDCODED PARAMETERS
# ==============================================================================
"""
PARAMETER DERIVATION STATUS (v14.1 Audit)

CORRECTLY DERIVED (have validated simulations):
- Neutrino masses           → neutrino_mass_matrix_final_v12_7.py (v14.1 FIXED!)
  * Bug was: exp(b3/4π) instead of exp(b3/8π)
  * Now achieves: Solar <10%, Atmospheric <1% vs NuFIT 6.0
- M_GUT (2.118e16 GeV)      → g2_torsion_m_gut_v12_4.py
- Proton decay (8.15e34 yr) → proton_decay_geometric_v13_0.py
- KK graviton (5.0 TeV)     → kk_graviton_mass_v12_fixed.py
- Pneuma VEV                → pneuma_stability_v12_8.py
- CP violation (δ_CP)       → ckm_cp_rigor.py (H₃(G₂,Z) cycle orientations)
- Higgs Yukawa             → higgs_yukawa_rg_v12_4.py

PHENOMENOLOGICAL INPUTS (not predictions):
1. Higgs mass
   - Simulation: higgs_mass_v12_4_moduli_stabilization.py
   - Status: Circular — Higgs inversion gives Re(T)=9.865; baryon asymmetry uses calibrated 7.086
   - The Higgs mass is INPUT to constrain moduli, not a prediction

HARDCODED BUT DERIVABLE (need new simulations):
1. Fermion masses (m_u, m_d, m_e, etc.)
   - Currently: PDG values hardcoded in FermionMassParameters
   - Should: Derive from G₂ cycle intersection Yukawa matrices
   - Simulation needed: fermion_mass_geometric_v15.py

2. CKM matrix elements (V_us, V_cb, V_ub, etc.)
   - Currently: PDG values hardcoded
   - Should: Derive from Yukawa texture + cycle overlaps
   - Simulation needed: ckm_matrix_geometric_v15.py

3. Matter multiplicities (N_5, N_10, N_1)
   - Currently: Assumed from SO(10) decomposition
   - Should: Derive from G₂ index theorem on matter curves
   - Simulation needed: matter_multiplicity_index.py

4. DT splitting proof
   - Currently: Asserted via TCS discrete torsion
   - Should: Explicit index theorem calculation
   - Simulation needed: dt_splitting_proof.py

CORRECTLY HARDCODED (phenomenological inputs):
- M_PLANCK (2.435e18 GeV)   → Measured (defines G)
- Higgs mass (125.10 GeV)   → Measured (constrains Re(T))
- Gauge couplings at M_Z    → Measured (runs to M_GUT)
- PMNS angles               → Measured (NuFIT 6.0)
- Neutrino masses           → Set to match NuFIT 6.0 Δm² values
- Topological invariants    → Fixed by manifold choice (TCS #187)

Note: This is a living document. Update as new simulations are added.
"""
