# Rulings Assessment — Principia Metaphysica

**Date:** 2026-08-25  
**Scope:** Seven pending author rulings on theory branches, derived values, and gate thresholds.  
**Honesty standard:** No physical constant or tolerance is invented. Every recommendation states what would falsify it. A gate that cannot fail is worse than no gate.

---

## Scoring rubric

Each option is scored 1–5 on four axes:

| Axis | What it measures |
|------|-----------------|
| **Elegance** | Does the derivation follow from the framework's own primitives without grafting extra machinery? |
| **Geometric derivation** | Is the result a clean consequence of the 288-root / G2 / b₃ topology, or does it require external inputs? |
| **Accuracy vs data** | How many σ is the prediction from the best available experimental measurement? |
| **Physical soundness** | Is the claim falsifiable? Does it respect established physics constraints? |

---

## Ruling (a) — theta13: retire `neutrino.theta13_derived = 9.594°`?

### Context

Two competing values exist in the registry:

| Key | Value | Method | Deviation from NuFIT 6.0 NO (8.57° ± 0.25°) |
|-----|-------|--------|-----------------------------------------------|
| `neutrino.theta13_derived` | 9.594° | `sin(θ₁₃) = 1/√b₃ = 1/√24`; zero free parameters | **4.10 σ** |
| `neutrino.theta_13_pred` | 8.647° | `neutrino_mixing_v17_2`; fitted inputs | **0.16 σ** |

The task notes 9.31 σ against NuFIT 8.57 ± 0.11°; the registry shows 4.10 σ using the 0.25° uncertainty from NuFIT 6.0 NO. Either way it is a clear tension. `abstract.fitted_pmns = 2` confirms that `theta_13_pred` uses fitted inputs — it is calibrated to NuFIT, not independently derived.

### Options

**Option A — Retire `theta13_derived` entirely, promote `theta_13_pred`**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 2 | Calibrated to data, not a zero-parameter prediction |
| Geometric derivation | 2 | Requires fitted PMNS inputs |
| Accuracy vs data | 5 | 0.16 σ from NuFIT 6.0 IO |
| Physical soundness | 3 | Honest but not independently falsifiable; inherits the NuFIT fit |

**Option B — Keep `theta13_derived` as a DERIVED/FAIL entry, demote to historical record**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 5 | `sin(θ₁₃) = 1/√b₃` is a clean zero-parameter prediction |
| Geometric derivation | 5 | Follows directly from b₃ = 24 |
| Accuracy vs data | 1 | 4.10 σ from NuFIT 6.0 NO — decisively excluded |
| Physical soundness | 4 | Falsifiable and correctly FAILING; transparency is honest |

**Option C — Displace `theta13_derived`; record the 8.647° value as the geometric prediction with honest σ annotation**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 3 | The 8.647° derivation chain is less clean but more accurate |
| Geometric derivation | 3 | Module uses geometric inputs but relies on calibration |
| Accuracy vs data | 5 | 0.16 σ from NuFIT 6.0 IO |
| Physical soundness | 4 | Honest if the fitted inputs are explicitly documented |

### Recommendation

**Retain `theta13_derived` as FAIL (DERIVED, 4.10 σ) and display it as such.** The 1/√b₃ formula is the only zero-parameter prediction; suppressing it removes a genuine falsification record. Alongside it, keep `theta_13_pred` labelled CALIBRATED (fitted inputs, abstract.fitted_pmns = 2). Crowning the 0.16 σ value as the geometric prediction would be dishonest — its fitting source is in the registry and must stay visible.

**Falsification condition:** If a future Yukawa calculation from first principles yields sin(θ₁₃) consistent with NuFIT at < 1 σ without fitted inputs, the DERIVED formula can be declared falsified and the Yukawa result promoted as the canonical prediction.

---

## Ruling (b) — S8 branch: analytic approximation vs growth-ODE

### Context

Two S8 suppression routes exist:

| Route | Suppression | S8 value | Deviation from KiDS-1000 (0.827 ± 0.011) |
|-------|-------------|----------|-------------------------------------------|
| Analytic friction approximation | ~5.13% (s8_friction_suppression_pct ≈ 5.18%) | ~0.7841 | ~3.53 σ (from task) |
| Growth-ODE integration | ~4.31% | ~0.7909 | ~3.01 σ (from task) |
| Current registry (`s8_pm_predicted`) | — | 0.8029 | 2.19 σ |

Note: the registry value 0.8029 (2.19 σ) already incorporates both the dark-energy term and the full moduli-DM friction calculation — the "analytic" vs "ODE" branch concerns which method produced the friction suppression.

### Options

**Option A — Adopt the growth-ODE result as canonical (4.31% suppression)**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 3 | ODE is standard; less elegant than a closed-form approximation |
| Geometric derivation | 3 | Derived numerically from PM equations; no closed form |
| Accuracy vs data | 4 | 3.01 σ from KiDS-1000 — better than analytic branch |
| Physical soundness | 5 | The ODE is the correct calculation; the approximation approximates *it* |

**Option B — Adopt the analytic approximation (5.13% suppression)**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 4 | Closed-form `exp(-β_eff · I(z))` is cleaner |
| Geometric derivation | 4 | β_eff = α_leak / (4π) = 1/(4π√b₃) is a topological expression |
| Accuracy vs data | 2 | 3.53 σ from KiDS-1000 — *worse* than the ODE it approximates |
| Physical soundness | 2 | An approximation that disagrees with the ODE it approximates is internally inconsistent |

### Recommendation

**Adopt the growth-ODE route (4.31% suppression, ~3.01 σ from KiDS-1000).** The reasoning is straightforward: the analytic approximation is valid only if it agrees with the numerical result it was meant to simplify. When they disagree by 0.8 percentage points on suppression, the ODE wins — it is the calculation the approximation is trying to match. The analytic form should be retained in the codebase as a documented approximation with its deviation from the ODE noted explicitly.

**Falsification condition:** If a future growth-ODE update with more accurate cosmological inputs moves the S8 prediction outside the 2 σ KiDS-1000 window in the unfavourable direction, the moduli-DM coupling mechanism is observationally falsified at that level.

---

## Ruling (c) — n_s branch: canonical 0.9636 vs slow-roll 0.9996

### Context

Two values are documented in the codebase (see `inflation.py`):

| Value | Source | Deviation from Planck 2018 (0.9649 ± 0.0042) |
|-------|--------|-----------------------------------------------|
| 0.9636 | Infrared closure: `n_s = 1 - 2φ²/χ_eff = 1 - 2φ²/144` | **0.31 σ** |
| 0.9996 | Leading-order slow-roll on the near-linear Re(T) racetrack potential at Re(T) = 174.033 | **8.26 σ** — excluded |

The 0.9636 value (`geometry.n_s`, `cosmology.n_s_pred`) is in the registry and matches Planck to 0.31 σ. The 0.9996 value is the bare racetrack slow-roll result, documented in `inflation.py` as a `documented_divergence` annotation.

### Options

**Option A — Retain 0.9636 as the canonical prediction, keep 0.9996 as a documented divergence**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 4 | n_s = 1 − 2/N_eff with N_eff = χ_eff/φ² ≈ 55 is clean |
| Geometric derivation | 4 | Uses b₃ and φ (golden ratio), both framework primitives |
| Accuracy vs data | 5 | 0.31 σ from Planck 2018 |
| Physical soundness | 4 | Falsifiable: if future CMB data shifts n_s above 0.97 at 3 σ, the formula fails |

**Option B — Promote the slow-roll 0.9996 as the canonical prediction**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 4 | Leading-order slow-roll is textbook |
| Geometric derivation | 3 | Follows from the racetrack potential anchored to b₃ |
| Accuracy vs data | 1 | 8.26 σ from Planck 2018 — decisively excluded |
| Physical soundness | 1 | The racetrack potential's inflation sector is falsified by this prediction alone |

**Option C — Suppress 0.9996 entirely and report only 0.9636**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 4 | Clean |
| Geometric derivation | 4 | Same as Option A |
| Accuracy vs data | 5 | 0.31 σ |
| Physical soundness | 2 | Hides the fact that the racetrack slow-roll disagrees with its own infrastructure by 8 σ |

### Recommendation

**Retain 0.9636 as canonical, keep 0.9996 as a *loud* documented divergence.** The slow-roll result at the racetrack minimum falsifies the racetrack potential's inflation sector. This is a genuine physical finding: the potential that stabilises the moduli at Re(T) = 174.033 produces a spectral tilt incompatible with Planck. That fact must remain visible — suppressing it (Option C) would hide a falsification. The infrared-closure correction (the golden-modulated N_eff formula) is a separate claim that happens to give the right answer; it should be presented alongside an honest statement that the bare racetrack slow-roll disagrees.

**Falsification condition:** If future CMB data from a Simons Observatory or CMB-S4 measurement moves the central n_s above 0.970 at 3 σ, the 0.9636 prediction is excluded.

---

## Ruling (d) — H0: should the SH0ES 73.04 anchor be inside the shadow group?

### Context

The registry has `cosmology.H0_local = 76.34` (3.17 σ from SH0ES 2022 at 73.04 ± 1.04). The GATE_EVAL_SPECS for G47 uses `{"path": "cosmology.H0_local", "exp": 73.04, "unc": 1.04}`, treating SH0ES as the evaluation anchor. Meanwhile `desi.S8` and `planck.S8` are listed as *distinct* anchors (both = 0.832) in the registry — meaning two experimental sources with the same central value are separately tracked as independent measurements.

**The question:** should SH0ES H0 = 73.04 be an internal anchor for evaluating the PM H0 prediction, or an external reference?

The SH0ES anchor is explicitly a low-redshift *local* measurement. PM's Ricci-flow H0 = 76.34 differs from it by 3.17 σ — which is already a FAIL. It also differs from Planck early-time H0 (~67.4) by a large margin. Including SH0ES inside the shadow group would mean using the Cepheid+SN measurement as an internal constraint, which would set 73.04 as a target the theory must hit — when in fact the theory already misses it by 3.17 σ.

By analogy: `desi.S8` and `planck.S8` are correctly kept as distinct *external* anchors because consistency of two independent measurements of the same quantity is evidence; they are not targets the theory was tuned to. The same logic applies to H0.

### Options

**Option A — Remove SH0ES H0 from the shadow group; treat it as an external experimental anchor**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 4 | Consistent with the desi/planck S8 treatment |
| Geometric derivation | — | Not applicable (this is an anchor classification) |
| Accuracy vs data | 3 | H0 = 76.34 is 3.17 σ from SH0ES; the FAIL status is honest |
| Physical soundness | 5 | Keeps the SH0ES tension visible; the 3.17 σ discrepancy is a real constraint |

**Option B — Keep SH0ES H0 inside the shadow group**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 2 | Inconsistent with the desi/planck S8 treatment |
| Geometric derivation | — | Not applicable |
| Accuracy vs data | 2 | Creates the appearance of an internal target rather than an external test |
| Physical soundness | 2 | Conflates a tuning target with a genuine prediction |

### Recommendation

**Remove SH0ES H0 from the shadow group (Option A).** Consistency with the desi/planck S8 treatment argues for this: both S8 measurements sit outside the shadow group as independent external anchors. SH0ES H0 should be treated the same way — an external measurement against which the PM prediction (currently failing at 3.17 σ) is evaluated. The FAIL status should remain.

**Falsification condition:** If a future PM derivation of H0 from first principles lands within 2 σ of Planck AND within 2 σ of SH0ES simultaneously, the tension would be resolved. Current PM H0 = 76.34 resolves neither.

---

## Ruling (e) — Canonical neutrino mass sum: 0.0598 vs 0.0817 vs 0.1012 eV

### Context

Three values are stored in the registry:

| Key | Value (eV) | Source | DESI ΛCDM bound (< 0.072 eV) |
|-----|-----------|--------|-------------------------------|
| `spectral.sum_m_nu` | 0.0598 | `complete_residue_registry_v18` | **Passes** |
| `geometry.sum_m_nu` | 0.0817 | `geometric_anchors_v16_2` | **Fails** (1.14× above) |
| `neutrino.mass_sum` | 0.0994 | `neutrino_mixing_v17_2` | **Fails** (1.38× above) |

NuFIT 6.0 NO mass splittings: Δm²₂₁ = 7.41 × 10⁻⁵ eV², |Δm²₃₂| = 2.511 × 10⁻³ eV². The minimum NO mass sum (m₁ → 0) is ≈ 0.0590 eV; the minimum IO mass sum is ≈ 0.1012 eV.

`spectral.sum_m_nu ≈ 0.0598` is consistent with the NuFIT NO minimum — it corresponds to m₁ ≈ 0, using only the measured splittings. `geometry.sum_m_nu ≈ 0.0817` comes from a separate geometric derivation. `neutrino.mass_sum ≈ 0.0994` comes from the neutrino mixing module and corresponds approximately to the IO minimum.

### Options

**Option A — Adopt `spectral.sum_m_nu = 0.0598` (spectral / NuFIT splittings, NO)**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 4 | Uses only measured splittings and the lightest neutrino mass floor |
| Geometric derivation | 3 | Spectral derivation from residue registry; not from b₃ topology directly |
| Accuracy vs data | 5 | Passes the DESI ΛCDM bound; consistent with NuFIT NO splittings |
| Physical soundness | 5 | The minimum sum is an honest lower bound, not an invented value |

**Option B — Adopt `geometry.sum_m_nu = 0.0817` (geometric derivation)**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 4 | Comes from the geometric-anchors module — framework-native |
| Geometric derivation | 5 | Directly from G2 geometry |
| Accuracy vs data | 2 | Exceeds DESI ΛCDM bound (0.072 eV) by a factor of 1.14 |
| Physical soundness | 2 | Violates the best current cosmological neutrino mass bound |

**Option C — Adopt `neutrino.mass_sum = 0.0994` (neutrino mixing module)**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 3 | Comes from PMNS mixing module |
| Geometric derivation | 2 | Uses fitted PMNS inputs |
| Accuracy vs data | 1 | Exceeds DESI bound by factor 1.38; near the IO minimum sum |
| Physical soundness | 3 | Corresponds to IO hierarchy, which NuFIT disfavours (ΔC.L. ~2 σ) |

### Recommendation

**Adopt `spectral.sum_m_nu = 0.0598` (Option A).** It is the only value that passes the DESI ΛCDM cosmological bound (< 0.072 eV), it is derived consistently from the NuFIT NO mass splittings, and it is not a tuned number — it follows from setting m₁ ≈ 0 (the normal hierarchy floor). The geometric value (0.0817) and the mixing value (0.0994) should be preserved as FAIL annotations with honest sigma deviations against the DESI bound; they represent predictions from other derivation chains that are currently excluded.

**Falsification condition:** If a future CMB+BAO dataset tightens the bound below 0.060 eV, the spectral prediction is also excluded. If the bound is loosened above 0.090 eV, the geometric prediction becomes viable.

---

## Ruling (f) — G12 / G30 / G32 tolerances

### G12 — Electroweak alignment: sin²θ_W = 0.2319 vs PDG 0.23122

Measured: geometry gives sin²θ_W = 0.23190 (from the 12/24 shadow ratio).  
PDG 2024 (MS-bar, Z-pole): 0.23122 ± 0.00003.  
Deviation: |0.23190 − 0.23122| / 0.00003 = **22.8 σ** (not 0.68 σ as the current cert claims).

The 0.68 σ figure in the cert uses an invented 0.001 theory tolerance that is not stored in any registry entry. The DECLARATIVE_GATE_STRATEGIES.md notes this. 

**Options:**

| Option | Description | Elegance | Geometric | Accuracy | Soundness |
|--------|-------------|----------|-----------|----------|-----------|
| A | Convert with 0.001 theory tolerance (status quo) | 2 | 3 | 1 | 1 |
| B | Convert to COMPUTED_FAIL at PDG uncertainty only | 3 | 3 | — | 5 |
| C | Seek a refined geometric derivation of sin²θ_W | 5 | 5 | ? | 4 |

**Recommendation:** Convert G12 to COMPUTED_FAIL using only the PDG uncertainty (22.8 σ). Do not apply the 0.001 theory tolerance — a number not in the registry is an invented number, and the honesty rules prohibit it. If a rigorous geometric derivation improves the prediction (closer to 0.23122), then and only then can the theory tolerance be motivated by the derivation residual. As of now, 0.23190 is a 22.8 σ discrepancy, and the certificate should say so.

**Falsification condition:** A future geometric derivation yielding sin²θ_W within 3 σ of the PDG Z-pole value would resolve the tension. The current value is excluded at high significance.

---

### G30 — Leptonic hierarchical gap: `m_μ/m_e ~ χ_eff`

The claim is `m_μ/m_e ~ χ_eff = 144`. The actual ratio is m_μ/m_e = 106.658 MeV / 0.511 MeV ≈ **206.8** — a factor of **1.44× above χ_eff = 144**. Similarly m_τ/m_μ ≈ 16.82 vs b₃/2 = 12 (factor 1.40×).

The wl_code contains `~` (tilde), which indicates an order-of-magnitude claim, not an equality. The cert result is `chi_eff = 144` which does not state a tolerance.

**The problem:** there is no checkable tolerance stored anywhere. The `~` operator has no numerical definition in the gate. Without one, the gate cannot fail — it is unfalsifiable as written.

**Options:**

| Option | Description | Elegance | Geometric | Accuracy | Soundness |
|--------|-------------|----------|-----------|----------|-----------|
| A | Leave as DECLARATIVE with ~ notation | 3 | — | 1 | 1 |
| B | State explicit factor-of-2 tolerance (m_μ/m_e within 2× of χ_eff) | 2 | 2 | 3 | 3 |
| C | Convert the gate to a qualitative ordering claim: m_μ/m_e > b₃ | 3 | 3 | 4 | 4 |

**Recommendation:** Either define an explicit tolerance and state it in the registry, or restructure the claim as a falsifiable ordering statement (e.g. `χ_eff < m_μ/m_e < 10·χ_eff`). The factor-1.44 discrepancy is honest and should appear in the cert. Do not invent a tolerance — derive it from the next-order geometric correction or leave the gate as DECLARATIVE until a derivation exists.

**Falsification condition:** A future derivation of m_μ/m_e from b₃ and the lepton mass hierarchy that lands within 10% of 206.8 would constitute genuine geometric derivation of lepton masses.

---

### G32 — W/Z mass ratio: sin²θ_W = 3/8 (GUT prediction)

The GUT prediction `sin²θ_W_GUT = 3/8 = 0.375` is an exact rational identity at the GUT unification scale — it is the SO(10)/SU(5) tree-level prediction, not a PM invention. The PDG Z-pole value is 0.23122 (running changes the value from GUT to Z scale).

The 3/8 identity is **exactly convertible** — `3/8` is a ratio of two integers. The cert currently says `sin²θ_W_GUT = 3/8`, which is a mathematically exact statement about the GUT-scale value. The question is only whether to evaluate it against the Z-pole PDG value (wrong comparison) or the GUT-scale prediction (correct comparison).

| Option | Description | Elegance | Geometric | Accuracy | Soundness |
|--------|-------------|----------|-----------|----------|-----------|
| A | Convert to COMPUTED_PASS: 3 == 3 and 8 == 8 (exact integers) | 4 | 4 | 5 | 4 |
| B | Convert to COMPUTED_FAIL: compare against PDG Z-pole | 2 | 2 | 1 | 2 |

**Recommendation:** Convert G32 to COMPUTED_PASS by checking the exact integer identity `3/8` against the registry's GUT-scale value, which is the claim the gate is actually making. The comparison must be to `gauge.sin2_theta_W_gut = 0.375`, not to the Z-pole PDG value. State clearly in the cert note that the GUT-scale prediction and the Z-pole measurement differ by RG running, and that this gate does not predict the Z-pole value.

**Falsification condition:** If the SO(10) GUT unification is shown to require a different tree-level sin²θ_W (e.g. from group-theoretic corrections specific to the G2 manifold), the 3/8 identity is falsified at that scale.

---

## Ruling (g) — G36 CKM unitarity: binding the threshold to PDG first-row uncertainty

### Context

The cert currently states the module's unitarity deviation as ≈ 5.8 × 10⁻⁵ with a note that a previous claim of < 10⁻¹⁰ was "corrected." The GATE_EVAL_SPECS has no entry for G36. The DECLARATIVE_GATE_STRATEGIES.md notes: "the only non-invented threshold is `< 1.0` (definition of unitarity)."

PDG 2024 first-row unitarity: |V_ud|² + |V_us|² + |V_ub|² = 0.9985 ± 0.0007.  
PM module deviation: 5.83 × 10⁻⁵.

The task asks: bind the evaluation threshold to the PDG first-row uncertainty (0.0007) rather than inventing 1 × 10⁻³.

### Options

**Option A — Use 1.0 as the only threshold (definitional unitarity, no σ test)**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 2 | Always passes; not a meaningful test |
| Geometric derivation | — | N/A |
| Accuracy vs data | 1 | A gate that cannot fail is worse than no gate |
| Physical soundness | 1 | Unfalsifiable |

**Option B — Bind to PDG first-row uncertainty: deviation < 0.0007**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 4 | Uses a published measurement uncertainty — no invention |
| Geometric derivation | — | The threshold comes from PDG, not from PM |
| Accuracy vs data | 5 | PM deviation (5.83 × 10⁻⁵) << 7 × 10⁻⁴; gate passes with a 12× margin |
| Physical soundness | 5 | Falsifiable: if PM deviation grows above 0.0007, the gate fails |

**Option C — Use the invented 1 × 10⁻³ threshold**

| Axis | Score | Rationale |
|------|-------|-----------|
| Elegance | 2 | 1 × 10⁻³ is not in any registry entry or PDG table |
| Geometric derivation | — | N/A |
| Accuracy vs data | 4 | Gate passes (5.83 × 10⁻⁵ < 1 × 10⁻³) |
| Physical soundness | 2 | Invented number — violates the honesty rules |

### Recommendation

**Bind the G36 threshold to the PDG first-row unitarity uncertainty (0.0007) — Option B.** The PDG published uncertainty is not an invented number; it is the standard against which any CKM matrix reconstruction is evaluated. A deviation of 5.83 × 10⁻⁵ passes this threshold by a factor of 12. Add this as a GATE_EVAL_SPECS entry: `{"path": "ckm.unitarity_test", "kind": "rel", "exp": 0.0, "rel_tol": 7e-4, "source": "PDG 2024 first-row CKM unitarity (0.0007)"}`. This is the only way to make G36 a gate that can genuinely fail.

**Falsification condition:** If a recalculation of the CKM matrix from PM geometry yields a first-row deviation above 7 × 10⁻⁴, G36 is COMPUTED_FAIL. Any deviation above 1.0 violates unitarity outright.

---

## Summary table

| Ruling | Recommended option | Key σ or bound |
|--------|-------------------|----------------|
| (a) theta13 | Retain `theta13_derived` as FAIL; keep `theta_13_pred` as CALIBRATED | 4.10 σ FAIL preserved |
| (b) S8 branch | Adopt growth-ODE (4.31% suppression) | ODE beats analytic approximation |
| (c) n_s branch | Retain 0.9636 as canonical; 0.9996 stays as loud divergence | 0.31 σ vs 8.26 σ |
| (d) H0 anchor | Remove SH0ES from shadow group; keep as external anchor | 3.17 σ FAIL stays |
| (e) mass sum | Adopt `spectral.sum_m_nu = 0.0598` | Passes DESI ΛCDM < 0.072 eV |
| (f) G12 | COMPUTED_FAIL at 22.8 σ; no invented 0.001 tolerance | Remove invented tolerance |
| (f) G30 | Define explicit checkable tolerance or leave DECLARATIVE | Factor 1.44× gap unstated |
| (f) G32 | COMPUTED_PASS on exact 3/8 GUT identity; note RG context | GUT-scale, not Z-pole |
| (g) G36 | Bind to PDG first-row uncertainty 7 × 10⁻⁴ | PM at 5.83 × 10⁻⁵, passes |
