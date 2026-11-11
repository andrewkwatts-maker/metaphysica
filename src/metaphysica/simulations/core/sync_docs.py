"""
Documentation Synchronizer v17.0 - SSoT Documentation Generator
================================================================
Extracts values and docstrings from the FormulasRegistry to create
a synchronized mathematical reference for the repository.

This ensures that FORMULAS.md always reflects the exact numbers
in the code - the documentation is an OUTPUT, not a configuration.

Usage:
    python core/sync_docs.py
    # Or import and use:
    from metaphysica.simulations.core.sync_docs import DocumentationSynchronizer
    sync = DocumentationSynchronizer()
    sync.generate_all()

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from metaphysica.simulations.core.FormulasRegistry import get_registry, FormulasRegistry
except ImportError:
    # Fallback for when running from different directory
    sys.path.insert(0, str(Path(__file__).parent))
    from FormulasRegistry import get_registry, FormulasRegistry


class DocumentationSynchronizer:
    """
    Synchronizes documentation with the FormulasRegistry SSoT.

    Generates:
    - FORMULAS.md: Human-readable mathematical reference
    - docs/SSoT_MANIFEST.json: Machine-readable manifest
    (sterility_report.json is owned by verify_sterility_report.py)
    """

    def __init__(self, registry: FormulasRegistry = None, output_dir: str = None):
        """
        Initialize the synchronizer.

        Args:
            registry: FormulasRegistry instance (creates new if not provided)
            output_dir: Directory for output files (defaults to project root)
        """
        self.registry = registry or get_registry()
        # Honour METAPHYSICA_OUT first so sterility_report.json /
        # FORMULAS.md / named_constants.json land in the active build
        # output dir (wheel installs otherwise default to
        # <site-packages>/metaphysica/simulations and the reports never
        # reach the static site).
        if output_dir is not None:
            self.output_dir = Path(output_dir)
        else:
            import os as _os
            _out_env = _os.environ.get("METAPHYSICA_OUT")
            if _out_env:
                self.output_dir = Path(_out_env)
            else:
                self.output_dir = Path(__file__).parent.parent
        self.timestamp = datetime.now()

    def generate_formulas_md(self) -> str:
        """
        Generate FORMULAS.md from the Registry.

        Every number that depends on the path (b3, chi_eff, sigma_T, H0) is
        read from the registry or the fork readers; seed_24 values appear only
        where they are labelled as the retired seed.

        Returns:
            The markdown content as a string.
        """
        reg = self.registry
        nums = _path_numbers(reg)
        sections = [
            self._header_md(reg),
            self._topology_md(reg, nums),
            self._anchors_md(reg, nums),
            self._sterility_md(reg, nums),
            self._derived_md(reg, nums),
            self._odowd_md(reg, nums),
            self._invariants_md(reg, nums),
            self._hebrew_md(reg),
        ]
        return "---\n\n".join(sections) + _FOOTER

    def _header_md(self, reg) -> str:
        timestamp = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        sovereign_hash = reg.get_sovereign_hash()
        return f"""# Principia Metaphysica: Formula Registry

**Status:** {reg.STATUS} | **Last Sync:** {timestamp}
**Engine Version:** v{reg.VERSION}
**Sovereign Hash:** `{sovereign_hash[:32]}...`

<!-- SOVEREIGN_HASH_FULL: {sovereign_hash} -->

"""

    def _topology_md(self, reg, nums) -> str:
        return f"""## The Mechanical Triad (Active Laws)

| Law | Symbolic Name | Derivation Logic | Current Value |
| :--- | :--- | :--- | :--- |
| **Expansion Rate** | eta_S (Sophian Drag) | {nums["h0_formula"]} | **{reg.h0_local:.4f} km/s/Mpc** |
| **Vacuum Seal** | sigma_T (Tzimtzum) | -{nums["sigma_t"]} Residue (dark_energy_betti fork) | **{reg.w0_dark_energy:.4f}** |
| **Mass Coupling** | kappa_Delta (Demiurgic) | (C_kaf^2 * kappa_Delta/pi) / holonomy | **{reg.mass_ratio:.2f}** |
| **Fine Structure** | alpha^-1 (Residue) | Geometric derivation | **{reg.alpha_inverse:.6f}** |

---

## The Ten Pillar Seeds (Input Invariants)

These values are the **Level 0 Seeds** of the `FormulasRegistry` on the path in force (b3 = {nums["b3"]}).
All other values are derived from these constants.

### Topological Invariants

| Name | Symbol | Value | Description |
| :--- | :--- | :--- | :--- |
| Governing Elder | E_כד | `{reg.elder_kads}` | Third Betti number b3 of Y_7 on the path |
| Chi Effective (per-shadow) | χ_עב | `{reg.mephorash_chi}` | Per-shadow effective index (chi_eff_route fork) |
| Chi Effective (total) | ק_דם | `{reg.qedem_chi_sum}` | Both shadows combined (chi_eff_route fork) |
| Total Roots (Nitzotzin) | 𝒩_רפח | `{reg.nitzotzin_roots}` | Logic Closure Sum, a typed integer (12 * b3 only at the retired seed_24) |
| Sophian Modulus | ק_כה | `{reg.sophian_modulus}` | 5^3 = 125 Visible Residue Modulus |
| Barbelo Modulus | ק_סג | `{reg.barbelo_modulus}` | 288 - 125 = 163 Ancestral Bulk Pressure Modulus |

### Chi-Effective Dual Architecture (v22.0-12PAIR)

The framework uses a dual chi_eff structure based on the 12x(2,0) paired bridge system:

| Constant | Value | Formula | Usage Domain |
| :--- | :--- | :--- | :--- |
| chi_eff | `{reg.mephorash_chi}` | chi_eff_route fork (B3^2/8 only at the retired seed_24) | Single-shadow (baryon, CKM) |
| qedem_chi_sum | `{reg.qedem_chi_sum}` | chi_eff_route fork (B3^2/4 only at the retired seed_24) | Cross-shadow (PMNS, n_gen) |

**Key Principle:** Does the physics involve one shadow or both?
- **Single-shadow (chi_eff = {reg.mephorash_chi}):** Quarks (CKM mixing), baryon asymmetry, torsional leakage
- **Cross-shadow (chi_eff_total = {reg.qedem_chi_sum}):** Neutrinos (PMNS mixing), generation counting, flux quantization

**Physical Basis:**
- Quarks carry color charge and are confined within a single 13D (12,1) shadow
- Neutrinos are electrically neutral and propagate through the Euclidean bridge

*Reference: docs/appendices/appendix_chi_eff_architecture.md*

"""

    def _anchors_md(self, reg, nums) -> str:
        return f"""### The Sacred Heptagon (7 Intellectual Anchors)

| # | Name | Symbol | Value | Role |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Watts Constant | Omega_W | `{reg.monad_unity}` | Observer Unity |
| 2 | Reid Invariant | chi_R | `{reg.nitsot_par:.16f}` | Sounding Board (1/{reg.qedem_chi_sum}) |
| 3 | Weinstein Scale | kappa_E | `{reg.weinstein_scale}` | Spinor Connection Rank |
| 4 | Hossenfelder Root | lambda_S | `{reg.hossenfelder_root:.12f}` | sqrt({nums["pleroma"]}) Hidden Root, a frozen ANSATZ integer (not sqrt(b3)) |
| 5 | O'Dowd Bulk Pressure | P_O | `{reg.barbelo_modulus}` | Bulk Pressure Constant |
| 6 | Penrose-Hameroff Bridge | Phi_PH | `{reg.penrose_hameroff_bridge}` | Fibonacci Bridge |
| 7 | Christ Constant | Lambda_JC | `{reg.logos_joint}` | Logos Potential |

### The Mechanical Triad (Gates 64, 46, 70)

| # | Name | Symbol | Value | Role |
| :--- | :--- | :--- | :--- | :--- |
| 8 | Sophian Drag | eta_S | `{reg.sophian_drag}` | H0 Friction Coefficient |
| 9 | Demiurgic Coupling | kappa_Delta | `{reg.demiurgic_coupling:.16f}` | Mass-Energy Gearbox |
| 10 | Tzimtzum Pressure | sigma_T | `{reg.tzimtzum_pressure:.16f}` | Void Seal ({nums["sigma_t"]}, dark_energy_betti fork) |

---

## Precision Constants

| Name | Value | Description |
| :--- | :--- | :--- |
| Sophian Gamma | `{reg.sophian_gamma:.16f}` | High-precision Euler-Mascheroni (16 decimals) |
| C_kaf | `{reg.c_kaf:.4f}` | Flux normalization: B3*(B3-7)/(B3-9) |

"""

    def _sterility_md(self, reg, nums) -> str:
        return f"""## Sterility Guard-Rail

The manifold is verified as **Sterile** if the following conditions are met:

### Parity Identity (IDENTITY: true by construction, not counted or scored)
`{reg._parity_text()}`

**Current Values:**
- Sophian Drag (eta_S): `{reg.sophian_drag}`
- Tzimtzum Pressure (sigma_T): `{reg.tzimtzum_pressure:.10f}`
- **Parity Sum:** `{reg.parity_sum:.4f}`
- **Status:** `{'PASS' if reg.verify_parity() else 'FAIL'}` (IDENTITY)

### Integer Closure (Demon Lock)
$$135 (\\text{{Visible}}) + 153 (\\Lambda_{{JC}}) = 288 (\\text{{E8}} \\times \\text{{E8}})$$

**Current Values:**
- Shadow Sector: `{reg.demiurgic_Yetts}`
- Christ Constant (Lambda_JC): `{reg.logos_joint}`
- **Sum:** `{reg.demiurgic_Yetts + reg.logos_joint}`
- **Status:** `{'PASS' if reg.verify_integer_closure() else 'FAIL'}`

### Tzimtzum Fraction
The Tzimtzum Pressure MUST be exactly (n-1)/n with n from the dark_energy_betti fork ({nums["sigma_t"]}), not a decimal approximation.

**Status:** `{'PASS' if reg.verify_tzimtzum_fraction() else 'FAIL'}`

### Watts Guard Rail
The Watts Constant MUST equal exactly 1.0 (immutable).

**Status:** `{'PASS' if reg.verify_watts_constant() else 'FAIL'}`

"""

    def _derived_md(self, reg, nums) -> str:
        return f"""## Derived Physical Constants

| Constant | Value | Formula | Target |
| :--- | :--- | :--- | :--- |
| H0 (Local) | `{reg.h0_local:.4f}` km/s/Mpc | (288/4) - (P_O/pressure_divisor) + eta_S | SH0ES 73.04 |
| H0 (Early/Planck) | `{reg.h0_early}` km/s/Mpc | CMB measurement | 67.4 |
| w0 (Dark Energy) | `{reg.w0_dark_energy:.10f}` | -sigma_T = -{nums["sigma_t"]} | see the parameter artifact |
| alpha^-1 | `{reg.alpha_inverse:.4f}` | Geometric derivation | 137.036 |
| Mass Ratio (mu) | `{reg.mass_ratio:.2f}` | Holonomy coupling | 1836.15 |

"""

    def _odowd_md(self, reg, nums) -> str:
        b3 = nums["b3"]
        return f"""## O'Dowd Hubble Formula (v17 Sovereign)

The local Hubble constant is derived geometrically from the manifold base b3 = {b3} of the path in force:

$$H_0 = \\frac{{ROOTS}}{{4}} - \\frac{{(7 \\times B3) - 5}}{{B3^2 / 4}} + \\eta_S$$

Where, at b3 = {b3}:
- ROOTS/4 = {reg.nitzotzin_roots}/4 = {reg.nitzotzin_roots / 4:g} (typed Logic Closure; 12 * b3 only at the retired seed_24)
- (7 * B3) - 5 = (7 * {b3}) - 5 = {reg.odowd_bulk_derived} (O'Dowd Bulk Pressure from Heptagonal Scaling)
- pressure_divisor = {b3}^2 / 4 = {reg.pressure_divisor:g} (Hexagonal Projection, distinct from chi_eff = {reg.mephorash_chi})
- eta_S = {reg.sophian_drag:.4f} (Sophian Drag)

**Result:** {nums["h0_expanded"]}

"""

    def _invariants_md(self, reg, nums) -> str:
        b3 = nums["b3"]
        return f"""## v17 Derived Geometric Invariants

These values are derived from the manifold base b3 = {b3} of the path in force:

| Invariant | Formula | Value | Verification |
| :--- | :--- | :--- | :--- |
| Manifold Area | B3^2 | `{reg.manifold_area_bulk}` | {reg.elder_kads}^2 = {reg.manifold_area_bulk} |
| Pressure Divisor | B3^2 / 4 | `{reg.pressure_divisor}` | {reg.manifold_area_bulk} / 4 = {reg.pressure_divisor:g} |
| O'Dowd Bulk (Derived) | (7 * B3) - 5 | `{reg.odowd_bulk_derived}` | (7 * {reg.elder_kads}) - 5 = {reg.odowd_bulk_derived} |
| Sterile Sector (Derived) | ROOTS - VISIBLE | `{reg.sterile_sector_derived}` | {reg.nitzotzin_roots} - {reg.sophian_modulus} = {reg.sterile_sector_derived} |

**Verification Status:**
- Bulk Pressure Derivation ({reg.barbelo_modulus} vs (7*{b3})-5 = {reg.odowd_bulk_derived}): `{'PASS' if reg.verify_bulk_pressure_derivation() else 'FAIL'}`
- Sterile = Bulk ({reg.sterile_sector_derived} vs {reg.barbelo_modulus}): `{'PASS' if reg.verify_sterile_equals_bulk() else 'FAIL'}`

"""

    def _hebrew_md(self, reg) -> str:
        return f"""## Hebrew Symbol Reference (v23.2.26 - Final Synthesis)

The framework uses Hebrew-derived naming for mathematical constants, connecting gematria to geometric invariants.

### Topological Invariants

| Code Name | Value | Symbol | Hebrew | Gematria | Scientific Name | Gnostic Name |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| monad_unity | `{reg.monad_unity}` | Ω_א | Aleph (א) | 1 | Observer Unity Constant | The Aleph-Anchor |
| residual_key | `{reg.residual_key}` | D_ι | Yod (י) | 10 | Core Flux Residual | The Hand of Creation |
| syzygy_gap | `{reg.syzygy_gap}` | Δ_χι | Chai (חי) | 18 | Aeon Pair Gap | The Life Delta |
| elder_kads | `{reg.elder_kads}` | E_כד | Kad (כד) | 24 | Symmetric Governance Energy | The Governing Elder |
| horos_limit | `{reg.horos_limit}` | β_כז | Kaz (כז) | 27 | Dimensional Boundary Limit | The Boundary Beth |
| mephorash_chi | `{reg.mephorash_chi}` | χ_עב | Ayin-Bet (עב) | 72 | Explicit Chiral Characteristic | The Shem HaMephorash |
| sophian_modulus | `{reg.sophian_modulus}` | ק_כה | Qoph-Kaf-He (קכה) | 125 | Visible Residue Modulus | Sophia Assembly |
| demiurgic_Yetts | `{reg.demiurgic_Yetts}` | 𝒮_δ | Dalet (ד) | 4 | Normal Portal Flux | The Sophia Door |
| qedem_chi_sum | `{reg.qedem_chi_sum}` | ק_דם | Qedem (קדם) | 144 | Total Euler Characteristic | Qedem Chi |
| nitzotzin_sector | `{reg.nitzotzin_sector}` | ξ_μ | Mem (מ) | 40 | Per-Sector Root Count | The Water Roots |
| logos_joint | `{reg.logos_joint}` | Λ_ν | Nun-Sofit (ן) | 700 | Joint Closure Symmetry | The Logos Fish |
| barbelo_modulus | `{reg.barbelo_modulus}` | ק_סג | Qoph-Samekh-Gimel (קסג) | 163 | Ancestral Bulk Pressure Modulus | Barbelo Modulus |
| nitzotzin_roots | `{reg.nitzotzin_roots}` | 𝒩_רפח | Raphach (רפח) | 288 | Logic Closure Sum | The Nitzotzin Sparks |

### Central Sampler (Reid Architecture)

| Code Name | Value | Symbol | Hebrew | Gematria | Scientific Name | Gnostic Name |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| gnosis_threshold | `{reg.gnosis_threshold}` | Γ_θ | Tet (ט) | 9 | Central Activation Threshold | The Gnosis Gate |
| Dodecad_Anchors | `{reg.Dodecad_Anchors}` | 𝔸_יב | Bet-Yod (בי) | 12 | Local Bridge Pair Count | The Dodecad House |
| Echad_Prime | `{reg.Echad_Prime}` | 𝕌_יג | Yud-Gimel (יג) | 13 | Effective Bridge Pair Count | The Unity Prime |
| nitsot_par | `{reg.nitsot_par:.16f}` | χ_ק⁻¹ | Medeq (מדק) | — | Mirror Parity Invariant | The Fine Resolution |
| reid_merkabah | `{reg.reid_merkabah}` | M_אד | Aleph-Dalet (אד) | 5 | Tetramorphic Normalization | The Merkabah Drive |
| watts_echud | `{reg.watts_echud:.10f}` | W_אפ | Eliphelet-Enoch (אֱלִיפֶלֶט-חנוך) | 467+89 | Harmonic Damping Modulus | The Eliphelet-Enochian Invariant |

### Symbol Collision Resolution (v23.2.26)

| Category | Before | After | Resolution |
| :--- | :--- | :--- | :--- |
| R-symbols | R_י, R_Ξ, R_m | D_ι, 𝒩_רפח, ξ_μ | Decad (D), Nitzotzin (𝒩), Xi (ξ) |
| n-symbols | n_12, n_13 | 𝔸_יב, 𝕌_יג | Anchors (𝔸), Unity (𝕌) |
| χ-symbols | χ_עב, χ_Q | χ_עב, χ_ק, χ_ק⁻¹ | Unified chi family |

### Shadow-Pressure Closure Proof

$$\\mathcal{{S}}_{{\\text{{ד}}}} (135) + \\mathcal{{P}}_{{\\text{{צ}}}} (163) = \\mathcal{{N}}_{{\\text{{רפח}}}} (288)$$

Sophia Door + Barbelo Hook = Nitzotzin Sparks (Logic Closure)

"""


    def write_formulas_md(self) -> str:
        """Write FORMULAS.md to AutoGenerated/."""
        content = self.generate_formulas_md()
        output_path = self.output_dir / "AutoGenerated" / "FORMULAS.md"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[SSoT] FORMULAS.md updated: {output_path}")
        return str(output_path)


    def generate_all(self) -> Dict[str, str]:
        """
        Generate all documentation outputs.

        Returns:
            Dictionary of output file paths.
        """
        print("=" * 60)
        print(" PRINCIPIA METAPHYSICA: DOCUMENTATION SYNC")
        print("=" * 60)
        print(f" Registry Version: {self.registry.VERSION}")
        print(f" Status: {self.registry.STATUS}")
        print("-" * 60)

        # sterility_report.json is written by verify_sterility_report's
        # SterilityReporter, which runs earlier in run_all_simulations. This
        # module used to write it too, in a DIFFERENT (flat) schema, so the
        # artifact flipped layout depending on which writer ran last and
        # churned 160+ lines on every regeneration. Single writer now.
        outputs = {
            "formulas_md": self.write_formulas_md(),
        }

        # Also generate named_constants.json from Registry
        manifest_path = self.output_dir / "AutoGenerated" / "named_constants.json"
        self.registry.generate_named_constants_json(str(manifest_path))
        outputs["named_constants"] = str(manifest_path)

        print("-" * 60)
        print(" DOCUMENTATION SYNC COMPLETE")
        print("=" * 60)

        return outputs


_FOOTER = """---

*Note: This file is auto-generated by `sync_docs.py`. Do not edit manually.*
*Any changes will be overwritten by the FormulasRegistry sync.*
"""


def _path_numbers(reg) -> Dict[str, Any]:
    """Path-dependent numbers FORMULAS.md quotes, read from the path in force."""
    from metaphysica.simulations.PM.cosmology import late_time_routes as ltr
    from metaphysica.simulations.core.FormulasRegistry import FROZEN_PLEROMA

    n = ltr.de_betti_n(ltr.resolve_de_betti())
    base = reg.nitzotzin_roots / 4
    drag = reg.odowd_bulk_derived / reg.pressure_divisor
    odowd = base - drag + reg.sophian_drag
    route = ltr.resolve_h0_route()
    return {
        "b3": reg.elder_kads,
        "sigma_t": f"{n - 1}/{n}",
        "pleroma": FROZEN_PLEROMA,
        "h0_formula": (f"({reg.nitzotzin_roots}/4) - ({reg.odowd_bulk_derived}/"
                       f"{reg.pressure_divisor:g}) + eta_S"),
        "h0_expanded": (f"{base:g} - {drag:.4f} + {reg.sophian_drag:.4f} = "
                        f"{odowd:.4f} (O'Dowd sum); H0_local on h0_route "
                        f"{route} = **{reg.h0_local:.4f} km/s/Mpc**"),
    }


def main():
    """Run documentation synchronization."""
    sync = DocumentationSynchronizer()
    outputs = sync.generate_all()

    print("\nGenerated files:")
    for name, path in outputs.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()
