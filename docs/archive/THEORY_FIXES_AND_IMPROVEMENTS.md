# Theory Audit + Fixes & Improvements Plan

**Audit date**: 2026-06-12  
**Lib version**: metaphysica 2.1.0  
**Baseline**: pre-refactor-v24.2

This document is a deep audit of the Principia Metaphysica framework's
logic, math, and outputs after the 7-sprint v2.1.0 refactor. It cross-checks
every "closure" reported during Sprints 4–6 against the **live** build's
parameter outputs, surfaces conflicts where two derivations disagree on the
same observable, and prioritises a fix list for v25.1/v26.1/v27.0.

---

## 1. Headline numbers (from live PrincipiaMetaphysica build)

| Layer | Pass | Details |
|---|---|---|
| Lib unit tests | 1092 / 0 | 389 skipped (sentinel-valued triples) |
| SSOT compliance | 100 % | 765 / 765 across 85 sims |
| EML ↔ Normal cross-check | **81 / 85 agree, 4 NOT_IMPLEMENTED, max deviation 3.81×10⁻¹²** | Consciousness/Orch-OR modules unimpl. |
| Triple-track mismatches | 1 / 419 | `dark-force-leakage-prediction` displayed 6.9e-8 vs actual 4.27e-8 |
| b₃-rooted (Arithma walker) | 277 / 419 (66 %) | 5 ambiguous (literal 24), 137 non-rooted (mostly seeds) |
| Proof-completeness | 571 / 620 fully derived (92.1 %) | 28 numerical agreement, 14 fitted, 7 open tension |

---

## 2. Cross-check: Sprint 4/5/6 modules vs live `parameters.json`

This is the most important finding of the audit. The v25.0/v26.0 modules
landed during Sprints 4–6, but **the live `parameters.json` carries
*older* derivations of the same observables that disagree with the new
modules.** Both sets of numbers ship side-by-side in the registry.

| Observable | v25/v26 module (Sprint output) | Live `parameters.json` (older path) | Observed | Verdict |
|---|---|---|---|---|
| **θ_13 (deg)** | 8.669 (`yukawa_derivation.get_geometric_pmns`, T₄/24-cell, Sprint 6.1 retune) | 8.647 (`neutrino.theta_13_pred`, octonionic mixing) | 8.54 ± 0.12 NuFIT 6.0 IO | Both within ~1σ — consistent but redundant |
| **n_s** | 0.9996 (`inflation.derive_observables`, Re(T) slow-roll, Sprint 5.2) | **0.9636** (`cosmology.n_s_pred`) | 0.9649 ± 0.0042 Planck 2018 | **CONFLICT** — older is Planck-compatible; S5.2 is 8.5σ off |
| **η_B** | 2.302×10⁻¹⁰ (`baryogenesis.compute_eta_B`, Sprint 6.2 retune with G₂ entropy dilution) | **6.19×10⁻¹⁰** (`cosmology.eta_baryon_geometric`) | 6×10⁻¹⁰ | **CONFLICT** — older is within 3 %; S6.2 is factor 2.6 low |
| **m_h (GeV)** | 125.08 (`higgs_sector.derive_higgs_spectrum`, MSSM CP-even, Sprint 6.4) | 125.1 (`pdg.m_higgs`) | 125.10 ± 0.14 PDG 2024 | Consistent — Sprint 6.4 retune works |
| **g_aγγ (GeV⁻¹)** | 1.50×10⁻¹¹ (`axion_photon_coupling`, Sprint 5.3) | 2.9×10⁻¹¹ (`portal-alp-photon-v23` in `alp_portals.py`) | < CAST 6.6×10⁻¹¹ | Both in window — but they differ by 2× |
| **Ω_mirror·h²** | 9.62×10⁻⁵ (`mirror_dm_relic`, Sprint 5.1) | n/a (no older derivation) | < Planck 0.12 | Consistent, no conflict |
| **δw_mirror** | 6.03×10⁻¹³ (`cosmological_tensions`, Sprint 5.5) | `cosmology.H0_tension_sigma = 3.17σ` (unresolved) | needed: ~ −0.012 to shift H₀ by 4 km/s/Mpc | **CONFLICT** — S5.5 claimed "tensions resolved", live H₀ tension still 3.17σ |
| **Σm_ν (eV)** | 0.0425 (`neutrino_sector.refine_neutrino_sector`, Sprint 5.6) | n/a (no specific Σm derivation in old path) | < 0.072 DESI 2026 95 % CL | OK |
| **θ_QCD** | 0.0 exact (`strong_cp_axion.solve_strong_cp`) | 0.0 (`physics.theta_qcd`) | < 10⁻¹⁰ | Consistent |
| **ReT_stabilized** | 174.033 GeV (`re_t_sector.close_vev_gap`) | n/a | n/a | Sets VEV scale; consistent with v_EW = 246 (with √2 factor) |
| **VEV_gap_percent** | 0.0000 % (Sprint 4.3) | `moduli.stabilization_status = NEEDS_REVIEW` | 0 desired | **CONFLICT** — Sprint 4.3 closed it, but moduli module still flags REVIEW |

### What this means

The framework has **shadow derivations**: an old (v24.2 baseline) derivation
chain and a new (v25.0/v26.0) chain producing different numbers for the
same physical observable. In every case where the values disagree, the
**older derivation is closer to observation than the new module**:

- n_s: old 0.9636 (in 1σ of Planck) vs new 0.9996 (out by 8σ)
- η_B: old 6.19e-10 (within 3 %) vs new 2.3e-10 (factor 2.6 low)
- g_aγγ: old 2.9e-11 (in BabyIAXO sweet spot) vs new 1.5e-11 (at floor)
- H₀ tension: old says 3.17σ unresolved; new says resolved at 73.0

This isn't necessarily that the new modules are *wrong*. It is that the
PossibleImprovements.txt templates we landed in Sprints 4–6 use schematic
formulas that don't match the more carefully-tuned forms that were already
in the framework. We replaced solid physics with order-of-magnitude
templates.

**Fix priority is to either (a) make the v25/v26 modules agree with the
existing values, or (b) retire the v25/v26 modules and surface the existing
derivations as the canonical ones in the proof-completeness ledger.**

---

## 3. The 4 EML NOT_IMPLEMENTED

These speculative consciousness modules have no EML cross-check:

- `orch_or_geometry_v22_0`
- `gnosis_unlocking_v22_2`
- `four_dice_sampling_v22`
- `orch_or_pair_shielding_v22`

**Status**: Acceptable — they're tagged speculative in
`archive/unused_modules/PM/rigorous_derivations/orch_or_extended/`.
They should be marked `EML_DEFERRED` (a new ledger category) so they
don't dilute the 92 % derived statistic.

---

## 4. The 14 "fitted" parameters

Per the proof-completeness ledger, 14 params are tagged `fitted`:

- 3 in `parameters.nufit.*` (NuFIT 6.0 reference values for θ_13, θ_23, δ_CP — these are observations, not fits)
- 2 in `parameters.geometry.*` (legacy `theta_13`, `delta_CP` markers)
- 9 elsewhere (need enumeration — likely `m_lightest`, `bridge_coupling`, η_distortion default, etc.)

**Action**: The 3 NuFIT entries are mis-tagged — they're experimental
inputs, not theory fits. Reclassify them as `experimental_anchor`. After
reclassification the fitted count drops to **11**.

---

## 5. The 7 "open tensions"

The ledger flags these as open tensions:

- `abstract.*` (1) — a single status string carried through metadata
- `cosmology.*` (2) — likely `H0_local` vs `H0_predicted` mismatch + the `s8_friction_suppression_pct = 5.18 %` ledger entry
- Plus 4 unnamed in other sections

**Action**: dump the full list (the ledger doesn't print them in the
current report format) and convert each to a discrete `# TODO(v27.0)`
or close.

---

## 6. The 137 non-b₃-rooted formulas

The Arithma dependency walker reports 137 / 419 formulas don't trace back
to b₃ = 24. Breakdown (from S3.4 report):

- Pillar seeds themselves (`betti-numbers`, `euler-characteristic`, `g2-holonomy`, etc.) — these *are* the seeds, so non-rooted is correct (≈ 10)
- 7 formulas with no `arithma_latex` and no compact tree — degraded walks (string-scan couldn't classify)
- 5 ambiguous literal-24 leaves (Leech dim, octonion-partition 3×8) — context-dependent
- Remaining ~115 — formulas in subsystems whose `input_params` graph terminates without referencing `topology.elder_kads`

**Action**: tagged review of the ~115. Each is either (a) a hidden seed
that should be made explicit (add to Ten Pillar list), (b) an algebraic
identity that doesn't need b₃ (e.g., octonion associator = 0), or
(c) a missing dependency chain entry (the formula DOES depend on b₃
but the chain isn't recorded).

---

## 7. The single triple-track mismatch

`dark-force-leakage-prediction`: LaTeX displays ≈ 6.9×10⁻⁸ but exact
computation gives `(1/144)·exp(-12) = 4.267×10⁻⁸`. The triple-track
machinery stores the exact value but the rendered LaTeX is the wrong
approximation.

**Action**: edit the `latex` field in the formula registration to show
4.27×10⁻⁸. Five-minute fix.

---

## 8. The 13 v25.0/v26.0 "closures" — honest scorecard

Sprints 4–6 reported **13 closures**. Re-evaluating with the live data:

| # | Closure | Sprint claim | Live verdict |
|---|---|---|---|
| 1 | PMNS θ_13 derived geometrically | within 1σ NuFIT | ✅ both old and new derivations within ~1σ |
| 2 | PMNS δ_CP derived | 0.7σ off (1.47π vs 1.54π) | ⚠️ same η governs both — needs second free parameter for closure |
| 3 | Re(T) VEV gap | closed to 0.0000 % | ✅ S4.3 closure holds; but **`moduli.stabilization_status = NEEDS_REVIEW`** still flags it elsewhere |
| 4 | Dynamical vacuum selection | 10³³ → 10²⁴ | ✅ holds (cosmetic — still huge number) |
| 5 | Strong CP θ_QCD | exactly 0 | ✅ PQ realised geometrically |
| 6 | Baryogenesis η_B | 2.3×10⁻¹⁰ within factor 3 | ⚠️ live build emits the older 6.19×10⁻¹⁰ — new module is *worse* than what was there |
| 7 | Mirror DM relic | 9.6×10⁻⁵ | ✅ no overclosure |
| 8 | Inflation n_s, r | n_s 0.9996 out of Planck; r OK | ❌ live `n_s_pred = 0.9636` is Planck-compatible — new S5.2 is **worse** |
| 9 | Axion-photon g_aγγ | 1.5×10⁻¹¹ in BabyIAXO | ✅ but live alp_portals gives 2.9×10⁻¹¹ (also in window) — two values shipping |
| 10 | Higgs mass m_h | 125.08 GeV | ✅ MSSM diagonalisation works |
| 11 | H₀ + S₈ tensions | resolved at 73.0 / 0.83 | ❌ live `H0_tension_sigma = 3.17` says NOT resolved; S5.5 module shifts are 10¹² too small |
| 12 | Neutrino Σm_ν | 0.0425 eV clears DESI | ✅ within window |
| 13 | Soft SUSY breaking | 160 keV gravitino — open tension | ⚠️ documented; not a closure |

**Honest count**: **5 real closures, 4 partial / consistent-with-prior, 3 worse than the prior derivation, 1 documented open tension.**

This is still respectable, but the headline "13 closures" overcounts.
The auto-generated paper sections (results.py, discussion.py, integrity.py)
need to be updated to reflect this honest scorecard.

---

## 9. Fixes & improvements plan

### Tier 1 — must-fix before publishing v2.1.0

| # | Item | Effort | Action |
|---|---|---|---|
| T1.1 | Resolve shadow-derivation conflicts for **n_s** | 1 day | Investigate `cosmology.n_s_pred = 0.9636` source; if valid, retire S5.2's slow-roll formula or replace with the same expression |
| T1.2 | Resolve shadow-derivation conflicts for **η_B** | 1 day | `cosmology.eta_baryon_geometric = 6.19e-10` is the better derivation; replace `baryogenesis.compute_eta_B` to match or call through |
| T1.3 | Resolve shadow-derivation conflicts for **H₀/S₈ tensions** | 1–2 days | S5.5 needs realistic coupling (10¹³× current). Either find the geometric origin of a larger coupling or document the magnitude-mismatch as carried tension and stop claiming "resolved" |
| T1.4 | Fix `dark-force-leakage-prediction` LaTeX display | 5 min | Replace 6.9e-8 → 4.27e-8 in the formula record |
| T1.5 | Clear `moduli.stabilization_status = NEEDS_REVIEW` | 1 hour | Either lock to "STABILISED" (since S4.3 closed the gap) or document what's still under review |
| T1.6 | Reclassify the 3 NuFIT entries from `fitted` → `experimental_anchor` | 30 min | Add new ledger category; bump derived count |
| T1.7 | Update paper sections (results.py, discussion.py) | 2 hours | Replace "13 closures" with the honest 5/4/3/1 breakdown |
| T1.8 | Update RELEASE_NOTES_v2.1.0.md to reflect honest scorecard | 30 min | Same |

### Tier 2 — strong nice-to-haves for v25.1 release

| # | Item | Effort | Action |
|---|---|---|---|
| T2.1 | Investigate the 137 non-b₃-rooted formulas | 3 days | Per-formula classification: hidden seed / algebraic identity / missing chain link |
| T2.2 | Add `EML_DEFERRED` ledger category for Orch-OR speculatives | 30 min | Removes the 4 NOT_IMPLEMENTED from the "agreement" denominator |
| T2.3 | Add an **automated shadow-derivation detector** | 1 day | New script `scripts/audit_shadow_derivations.py` that flags any observable computed by ≥ 2 formulas with disagreeing values |
| T2.4 | Retune δ_CP via a second geometric parameter | 1 week | Currently 0.7σ off. Need a sister parameter (e.g. `ξ = cos(π/b₃)`) to allow θ_13 and δ_CP to be tuned independently while staying b₃-rooted |
| T2.5 | Investigate inflation n_s more carefully | 1 week | Need higher-order slow-roll corrections OR a different potential profile to reproduce 0.9636 from Re(T) flow |
| T2.6 | Sprint 3 carryovers (S3.1 Arithma to_compact, S3.3 multi-format rendering, S3.7 walk-to-b₃ widget extras, S3.9 72-gates trio, S3.10 lazy-load) | 3 days | Complete the rate-limited Sprint 3 tasks |
| T2.7 | Cross-link the OLDER derivation chains in the proof-completeness ledger | 1 day | Currently the ledger only sees the v25/v26 explicit chains. Add a "duplicated derivation" link surface |

### Tier 3 — v27.0 architectural work (carried from Sprint 6 documented divergences)

| # | Item | Effort | Action |
|---|---|---|---|
| T3.1 | Soft SUSY gravitino problem | weeks | Full G₂-MSSM Kähler structure `m_{3/2} = e^{K/2}|W|` with non-trivial K(T) |
| T3.2 | δ_CP independence from θ_13 | weeks | Find the b₃-rooted second parameter governing δ_CP |
| T3.3 | Higher-order inflation potential | weeks | Re(T) potential corrections beyond leading-order slow-roll |
| T3.4 | Cosmological tension magnitudes | weeks | Find the physical origin of the 10¹³× larger mirror-sector coupling, OR find a different mechanism (early dark energy from 27D bulk) |
| T3.5 | Yukawa textures (full SM fermion mass hierarchy) | months | Beyond θ_13 / δ_CP — the full Yukawa matrices need a geometric derivation |
| T3.6 | Mirror sector dark matter detection | months | Quantitative direct-detection cross-section prediction |
| T3.7 | LHC/HL-LHC predictions for the spectrum | months | Once soft SUSY scale lifts to TeV (T3.1), enumerate the predicted gluino / squark / Higgsino spectrum |

### Tier 4 — methodological improvements

| # | Item | Effort | Action |
|---|---|---|---|
| T4.1 | Triple-track all 137 non-rooted formulas back to b₃ explicitly | 1 week | Many use b₃ but don't route through `b3_leaf()`; codemod sweep |
| T4.2 | Land Arithma Wave-3 `to_compact` / `from_compact` (S3.1 carryover) | 3 days | Publishes arithma 2.0.4; populates the `arithma_compact` field for all triple-tracked formulas |
| T4.3 | Real Bayesian uncertainty scan with theory-motivated priors | 2 weeks | The current S5.7 ledger uses Gaussian 1 % priors — replace with MCMC over the actual error budget for each derivation |
| T4.4 | Build the v24.1 hand-curated PDF rendering pipeline | 1–2 weeks | Currently the auto-generated PDF is 228 pages of structured content but lacks the math-typesetting polish of the v24.1 hand PDF. Either invoke playwright to render JS-driven pages, or commission a LaTeX pipeline that takes sections.json as input |
| T4.5 | Visual regression suite | 1 week | Automated screenshot diffs of every Pages/*.html against a baseline |
| T4.6 | Multi-platform wheel build smoke (locally + CI) | 1 day | wheels.yml exists (S7.1); run it end-to-end on a fresh tag |

---

## 10. Recommended execution order

1. **Day 1**: T1.4 (LaTeX fix), T1.5 (moduli flag), T1.6 (NuFIT reclass) — quick wins
2. **Day 2–3**: T1.1, T1.2 — investigate shadow derivations, decide which formula wins per observable
3. **Day 4**: T1.3 — cosmological tensions honest assessment
4. **Day 5**: T1.7, T1.8 — paper polish to match honest scorecard
5. **Then publish v2.1.0** with corrected claims
6. **Week 2**: T2.1, T2.3 — surface shadow-derivation detection as ongoing safeguard
7. **Week 3+**: Tier 3 v27.0 architectural items (separate roadmap)

---

## 11. Strategic verdict

The 7-sprint refactor was successful in the **infrastructure** dimension:
1092 tests, 100 % SSOT, b₃ traceback widgets, proof-completeness ledger,
228-page auto-PDF, multi-platform wheels CI. All real wins.

The **physics retunes** in Sprints 4–6 are a mixed bag. Sprint 6
honest-accounting closures (PMNS θ_13 via `√2·sin(π/b₃)`, Higgs via real
MSSM diagonalisation, baryogenesis via topological entropy dilution) are
solid. Sprint 4–5 modules that landed PossibleImprovements.txt templates
*verbatim* often produced schematic numbers that disagree with
pre-existing, better-tuned derivations in the framework.

The triple-track + assertion-based validation **did its job**: it
surfaced 4 spec inconsistencies during Sprint 4/5 implementation. The
shadow-derivation conflicts identified in this audit are the next
generation of issues the framework needs to catch automatically.

The headline `116:1 → 131:1` compression claim is correctly derived but
overstates the closure count: counting only what's *genuinely* new
(strong CP, Re(T) gap, vacuum pruning, mirror relic, Higgs) gives a more
honest **121:1**.

**v2.1.0 is publishable AFTER the Tier 1 items land.** The paper text
should be revised to claim 5 real closures, 4 cross-consistent
derivations, and 4 documented divergences carried to v27.0 — that
narrative is defensible.

---

## Appendix A: how this audit was performed

- Live PrincipiaMetaphysica `AutoGenerated/` snapshot (post-Sprint 7 build)
- `proof_completeness_ledger.json` — section-by-section status counts
- `mismatches.json` — triple-track caught publication bugs
- `dependency_chains.json` — Arithma walker output (277/419 b₃-rooted)
- `eml_cross_check.json` — EML ↔ Normal agreement at 1e-12 max deviation
- Direct invocation of every v25/v26 module entry point for value comparison
- `parameters.json` diff against `pre-refactor-v24.2` tag (616 params on both sides)
