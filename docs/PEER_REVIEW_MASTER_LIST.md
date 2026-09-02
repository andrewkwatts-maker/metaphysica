# Peer-Review Master Defect Register — Principia Metaphysica v2.2.1

**Compiled:** 2026-08-17 · **Method:** four recompute-verified module audits (geometry/algebra, cosmology, gauge/particle, registry/datasets), one validation-coverage audit, and an eight-section review of the full paper (447-page render + 228-page official PDF). Every numeric claim below was re-derived in Python before listing. ~250 raw findings deduplicated to the register below.

**Verdict in one paragraph:** the computational core is in far better shape than the prose. The registry's arithmetic, the b₃-chain identities, and the new computed validation layer (163 sigma-certificates, 12 live beacons, dead-link zero) hold up. The paper text, however, publishes **multiple incompatible values for at least 20 headline quantities**, contains **derivation displays that do not produce their own stated results** (several off by 10–60 orders of magnitude), asserts **claims its own tables falsify**, and carries **circular derivations presented as predictions**. Most of these are not new physics errors — they are version-fragment accretion plus a prose layer that hand-copies numbers instead of reading the registry. Fix the systemic causes (S-block) and the majority of the C/M items become mechanical.

Status legend: `[x]` fixed this session · `[ ]` open · **DECIDE** = needs the author's canonical-value ruling before code can fix it.

---

> ## Read this before using the tables below (added 2026-09-02)
>
> **This file is history, not the live register.** It records the four-domain
> peer-review cycle of 2026-08-17 and the sweeps that followed. The live
> register is `PrincipiaMetaphysica/docs/OUTSTANDING_ISSUES.md`, and it wins
> on any disagreement.
>
> It is kept in full — including every falsified candidate and withdrawn claim,
> per standing policy — but **several "Suggested canonical" entries in C-1 were
> subsequently ruled the other way.** The ones that matter:
>
> | C-1 row | suggested here | ruled since |
> |---|---|---|
> | Bulk dimension | 27D (24,1,2) | **26D at (24,2)**, ruled 2026-08-31, shadows 13D(12,1) × 2 — with `D_crit = 26` withdrawn, the Bars ghost-freedom appeal withdrawn, and the lattice obstruction (24 − 2 ≡ 6 mod 8) unanswered |
> | Clifford/spinor | Cl(24,1), 2¹² = 4096, non-chiral | **Weyl of Cl(24,2) = 4096** (Dirac 2¹³ = 8192) — chiral, which is what the chirality gates need |
> | w_a | −0.8165 (FITTED ×4 projection) | **−1/√24 = −0.2041**; the −0.8165 branch was retired and is labelled FITTED |
> | S₈ | 0.8030 (growth-ODE) | **0.8207** under the declared friction window; published against *both* anchors — 0.718σ vs Planck, **2.733σ TENSION vs KiDS-1000** |
> | θ₁₃ | "DECIDE which module is canonical" | asin(1/6) = 9.594° **FALSIFIED** (~9σ, kept on the books); headline `particle.theta_13_deg` = 8.669° at **0.805σ PASS**; `geometry.theta_13` = 8.54° is the NuFIT value restated and is deliberately unscored |
> | Σm_ν | 0.0598 (spectral) | **`geometry.sum_m_nu` = 0.0817 eV** canonical — the spectral branch failed its R5 chain audit |
> | n_s | "DECIDE (0.9996 vs 0.964)" | geometric 0.9636 canonical at 0.27σ; `n_s_slow_roll` kept loud as an **8.263σ FAIL** — two internal derivations disagree and both stay visible |
> | Certificate count | "72 gates + 25 named" | gate dashboard now reads **41/43 locked (95.3%), open G12 and G72**; 29 axiomatic, 45 declarative |
>
> Also superseded: C-3's "0.48σ global alignment" finding was right that the
> number was irreproducible, but the replacement is not a smaller σ — the
> global fit is **χ² = 126,749 over 65 scoring rows, p = 0, POOR_FIT** (5,791
> over 60 excluding the five withdrawn candidates). The old "χ² = 0.2304" was a
> `.get(key, 0.23)` default firing on a key the report never contained.
>
> And the load-bearing geometric gap this cycle could only name — *nothing maps
> a bridge index to a G₂ coordinate pair* — is **closed**, on one stated
> assumption. See `PrincipiaMetaphysica/docs/BRIDGE_CHANNEL_ASSIGNMENT.md`.

---

## C — Critical (scientific validity)

### C-1 · Canonical-value conflicts (DECIDE, then template) — the dominant defect class

One quantity, several published values. Each row needs one canonical ruling; prose should then *read* the registry (see S-1), not restate numbers.

| Quantity | Values found in paper/site | Registry value | Suggested canonical |
|---|---|---|---|
| w_a | +0.29, +0.1, −0.204, +0.27, −0.75, −0.8165 | −0.8165 | −0.8165 (FITTED ×4 projection) |
| S₈ | 0.789, 0.80296, 0.831, 0.837 | 0.80296 | 0.8030 (growth-ODE) |
| w₀ | −0.853, −0.9583, −0.980, −1.0 | −0.9583 | −23/24 (retire −0.853 thermal-time text) |
| Re(T) | 1.833, 3.739, 7.086, 9.865, 37.85, 94.07, 174.03 | (several) | one canonical + per-sector conversion table |
| α_leak | 1/√6=0.408, 0.57, 1/(4π)=0.0796, 0.00248 | 0.40825 | 1/√6; rename 0.57 → α_sample (ANSATZ) everywhere |
| τ_p (yr) | 3.9e34, 4.757e34, 4.8e34, 8.15e34, 1.0e34 | 4.757e34 | 4.76e34; Super-K bound: pick 1.6e34 vs 2.4e34 (mode-dependent, say which) |
| m_H prose | 125.08, 125.10, 125.20, 125.25 (±0.17) | — | 125.20 ± 0.11 (PDG 2024) everywhere |
| M_GUT | 6.325e15, 1.8e16, 2.1e16, 2.118e16, 1.24e17 (“≈2e17”) | 6.325e15 | DECIDE: geometric vs RG value; label the other |
| H₀ (pred.) | 70.42, 71.55, 76.34 (+anchors 67.4/73.04) | 71.55 & 76.34 both live | DECIDE: O'Dowd 71.55 vs ricci-flow 76.34 — one is “the” prediction |
| n_s | 0.964, 0.9636, 0.967, 0.9996 | — | DECIDE (0.9996 is 8.3σ; 0.964 is 0.21σ) |
| δ_CP (PMNS) | π/6, π/2, 232.5°, 278.4° | 278.4 (FITTED) | 278.4°; retire π/6 and π/2 as superseded |
| Cabibbo λ | e^{−3/2}=0.22313, e^{−π/2}=0.208, 0.2257 | 0.22313 | e^{−3/2}; 0.2257 is a stale PDG copy, 0.208 a rival ansatz |
| M_KK | 4.5 TeV, 4.72 TeV, 5.0 TeV, 3.4e15, 3.647e15 | — | 4.5 TeV warped form; the e15 values are the (wrong-pairing) ratio form — label separately |
| θ₁₃ | 8.33°, 8.61°, 8.65°, 8.67°, 9.59° (+status fitted vs derived) | 8.647 pred / 9.594 derived | DECIDE which module is canonical; registry already FAILs 9.59 at 4.10σ |
| Λ / ρ_vac | 1.23e-52 m⁻², 5.907e-10, ~1e-50, e^{−3456} | 1.2268e-52 | implemented formula only (drop instanton-display) |
| BR(p→e⁺π⁰) | 25% / 75% inverted vs 64.2% / 35.6% | 0.25 | DECIDE; two pages apart the ratios flip |
| Σm_ν | 0.042–0.060 eV (NO) vs 0.0994 eV (IO) | 0.0598 | present as alternative orderings, never simultaneously |
| Compression ratio | 116:1, 121:1, 131:1, 152:1, 2.3:1 | — | recompute one ratio from the ledger; delete the rest |
| Certificate count | 42, 72, 196 | 72 gates + 25 named | say “72 gates + 25 named certs”; delete 42/196 |
| Residue count | 107 emitted vs 121 vs 125 claimed | 107 | reconcile registry emission with the 125 narrative |
| 288 partition | 135+153 (fitted, SSoT) vs 125+163 (appendices) | 135+153 | DECIDE: two *different* splits are used as if interchangeable |
| 125-node map | 3 incompatible bank/index partitions | — | one map; regenerate the other tables from it |
| Bulk dimension | 25D, 26D, 27D; D=b₃+2 and D=b₃+3 both “forced” | 27 (24,1,2) | 27D(24,1,2); fix the (24,1)=“26D” mislabels (it is 25D) |
| Clifford/spinor | Cl(24,1)→4096 vs Cl(26,1)→4096 (wrong; =8192); 2^12.5 | 4096 | Cl(24,1), 2¹²=4096; delete 2^12.5 and “3×16=64” |
| χ (Euler) | 72 (from h³¹) vs χ_eff=144 | 144 | χ_eff=144; the 72 text imports CY-fourfold language |
| Internal manifold dim | 7D (V₇) vs “8-dimensional” vs “9-dimensional G₂×T²” | 7 | V₇ is 7D; fix stale KK text |

### C-2 · Derivation displays that don't produce their stated result

- [ ] **m_ν seesaw (p316):** 0.57²·246²/10⁴ = **1.97 GeV**, printed as 2×10⁻³ eV — 12 orders. Needs M_s ≈ 10¹⁶ GeV and the honest scale.
- [ ] **R_c chain (p297):** ħc/(Re(T)·ℓ_P) = 1.7e18 GeV, printed as 5 TeV — 15 orders.
- [ ] **c from horizon (p392):** L_horizon/(6t_P) ≈ 1.4e69 m/s. Not salvageable as a derivation of c; delete or reframe.
- [ ] **Λ display (p246/713):** displayed instanton formula gives 8.8e-196; the implemented formula (no instanton factor) gives the quoted 1.23e-52. Section header still claims e^{−2πD} “resolves the 120-order hierarchy”. Show the implemented formula; retire the header claim. *(Cert G56 + code comments already fixed; ch. 5/6 prose remains.)*
- [ ] **λ(μ) running (p407-8):** outputs *increase* toward M_Pl (sign inverted vs the printed one-loop formula); Λ_I has three mutually exclusive values (10^10.5 / 3.7e7 / 2.7e3); β_λ gauge quartic coefficients wrong and g₁²g₂² cross-term missing. The whole R-appendix metastability story needs recomputation.
- [ ] **ζ-function residues (p418-9):** Res(5/2) asserted 0 by Ricci-flatness but output 0.15198; Res(7/2) substitutes χ_eff for Vol(V₇).
- [ ] **M_GUT^eff (p93):** formula gives 1.24e17 (matches output), prose says ≈2e17; a spurious f_inst^{1/4} step contradicts the equation.
- [ ] **m_H bulk (p172):** printed inputs give 548.2 GeV, output says 414.22; and the 8π² normalization step (×4π² over tree) is underived.
- [ ] **w₀ bridge form (p204):** T_ω²/4π = 1/(24π), not 1/24 — off by π.
- [ ] **θ₂₃ (p188):** displayed formula gives 65.61°; printed “45 + 15.86 − 11.1 ≈ 49.75” inserts an undisclosed −11.1°.
- [ ] **D_eff (p200):** (26+10)/2 = 18, printed 13.
- [ ] **Δ(v=2) (p59):** denominator 1.001 not 1.01; and dΔ/dv=0 contradicts the “positive feedback” claim.

### C-3 · Claims falsified by their own numbers

- [ ] **MDL self-test (p73-74):** L(Theory)=32,640 bits ≫ L(Data)=8,000 — the compression argument fails as printed. Reconcile with the 69-bit claim.
- [ ] **τ_p “comfortably above” (p169):** 10³⁴ < 1.6×10³⁴ — prediction sits *below* the quoted bound.
- [ ] **α_sample bound (p53):** 0.57 exceeds its own printed ≤1/√6≈0.41 bound. *(Now labelled ANSATZ in code; prose contradiction remains.)*
- [ ] **“0.48σ global alignment” (pp3, 353-355):** component rows are 6.04σ (Planck) and 2.58σ; χ²=0.2304 is irreproducible from its own table; “24/58 within 1σ” is inconsistent with a 0.48σ mean.
- [ ] **Self-falsifying criterion (p293):** “falsified if w₀ < −0.95” while predicting w₀ = −0.9583.
- [ ] **Untestable testability (p335, p329):** σ_SI = 1.9e-93 cm² called “within DARWIN sensitivity” (≈46 orders below); g_aγγ = 4.8e-16 called “within IAXO” (≈3 orders below; correct statement appears on p331).
- [ ] **Falsification gap (p268/270):** “no excess above **7 TeV** challenges” a **5 TeV** prediction.
- [ ] **Ω_a h² (p327-330):** derived 0.516 overcloses (obs 0.12); companion page computes 0.048 with a different f_a; “100% of DM with θ_i ~ O(1)” coexists with both.

### C-4 · Circularity presented as prediction

- [ ] m_H “independent validation”: effective_scaling ≡ 414.22/125.10 exactly; λ₀ = 0.129 is m_h²/2v² back-computed; “3.92 combined with 1.185 gives 3.31” is a division presented as new information.
- [ ] α_T = 27/10: γ was fitted to produce 2.7; (2π/b₃)·γ = 2.7 is an identity, labelled “DERIVED, zero free parameters, not engineered”.
- [ ] Compton/manifest QED block: bulk ≡ CODATA×(1+ε) then “recovers CODATA exactly” (it doesn't even match exactly — 1.4e-9 off from a stale input). *(Registry layer already relabelled ILLUSTRATIVE; paper prose remains.)*
- [ ] PMNS/CKM ratio: prints prediction 1.54 next to its own output 2.4646, rescued post-hoc as “tribimaximal enhancement”, still labelled PREDICTED.
- [ ] V_ub: printed formula omits |ρ−iη|; “topological_factor 0.58” inconsistent with the 0.331 the output implies.
- [ ] H₀ relaxation: “resolves the tension without free parameters”, but the formula reaches 67.4 only at z≈6.5 (not 1100), the 10.1 scale factor is 73.1/7.24 fitted, and “Ricci flow resolution” replaces a 5σ tension with a new 3.17σ one (76.34 vs SH0ES).
- [ ] η_b: “fully geometric, no calibration” vs the same Re(T)=7.086 labelled “CALIBRATED — tuned to match BBN” on the facing section.

### C-5 · Mathematically false statements

- [ ] dim J₃(O) = 27, not 125 (p89).
- [ ] G₂ has **12** roots (14 is the group dimension); the “14 roots per G₂ → 144 per shadow → 288” chain fails twice (p73).
- [ ] Golay CSS: self-dual C gives [[24,**0**,8]], not [[24,12,8]]; only the X-half of the stabilizers is listed; the worked syndrome is off by one qubit (p426-7).
- [ ] “P†P = I₁₃, lossless” for a rank-≤4 projection that its own card says discards 9 dimensions (p349).
- [ ] Spin(7) holonomy “preserves no spinors” (it preserves exactly one, and is 8-dimensional); associative (3-form) and coassociative (4-form) are swapped, then re-swapped (pp147-149).
- [ ] M_Pl² = M*¹¹·Vol(V₇) is dimensionally wrong (M⁴); standard is M*⁹·Vol (pp120-123).
- [ ] Signature bookkeeping: (24,1) totals 25, labelled “26D” across the descent chain; “24 core + 24 local + 2 = 50 spacelike” double-counts; “(26,1) unified-time” appears once; unified-time “+2” justified two incompatible ways (1+0 and Sp(2,ℝ)).
- [ ] Dirichlet boundary conditions imposed on a closed manifold (p341).
- [ ] “G₂ is the only 7D structure supporting a torsion-free Ricci-flat metric” — false (T⁷, K3×T³,…) (p20).
- [ ] The 6/6 aligned/orthogonal split justified by “eigenvalue ±1 of |det R_⊥|” — an absolute value can't be −1, det of a rotation pair is +1, R_⊥ eigenvalues are ±i (p43).
- [ ] f = M_Pl/12 called **super**-Planckian and “Planck-suppressed” in the same sentence (p255).
- [ ] sin(π/3) stated as 0.5; δ_CP = π/K with K=4 stated as π/6 (pp286, 155).
- [ ] G defined as “the first eigenvalue of the V₇ Laplacian” whose own spectrum starts at λ₁=0 → G=0 (pp393, 415).
- [ ] Racetrack W_np printed with “+” where the minimum requires “−” (p434).
- [ ] Yukawa ladder: printed N-assignments give electron = 473 MeV (needs N≈27); eq. (6.2) then uses N∈{0,1,2} (p273-4). *(Header table in code already fixed; prose remains.)*
- [ ] “125 physical parameters of the Standard Model” — the SM+ν has ~26–28 (pp414, 425).
- [ ] “1/α_GUT = 23.54 matches **NuFIT 6.0**” — NuFIT constrains neutrino oscillations, not gauge couplings; “α_GUT: 1/24 ± 0.5” has uncertainty larger than the value (pp291-292).
- [x] n_gen = χ_eff/(**4**·b₃) printed with a denominator (=96) that contradicts its own “=144/48=3” — the framework's central claim, fixed to 2·b₃ in 5 surfaces.

---

## M — Major (pipeline & data correctness)

### M-1 · Generator value-binding bugs
- [ ] Literal `?` placeholders where substitution failed: “m_h = ? GeV”, “Σm_ν = ? eV”, “— ?π”, “gives ?. This replaces the earlier ? / ?” (pp133, 141-142).
- [ ] Empty `OUTPUTS:` blocks (≥8 cards) and blank INPUTS labels (“= 1 4 4”) — systemic slot-binding fragility (pp125, 129-130, 218, 344-392 passim).
- [ ] Wrong variable wired to output: P_entry shows 2.3000 (=288/125) under a “288/24 = 12” equation; f_damp card outputs eta_baryon; Δλ slot reuses lambda_gut (0.16042); τ card outputs b₃/k_gimel instead of k_gimel/b₃; r_geo provenance string cites b₃/b₂=24/12=2 for a 0.75 value that is (b₃−6)/b₃; α_T card's output is gamma_fitted=10.313.
- [ ] Raw markdown/labels leaking: `**bold**`, an unrendered table (p269), `(eq:compton_bulk)`-style label keys as equation numbers (pp276-279, 390), `\quadN_1` undefined control sequence (p434), `\texttt{}` cells (pp439, 441), Hebrew ק as an undefined summation symbol with “where קis” (p344).

### M-2 · Sigma/uncertainty misstatements (each recomputed)
- [ ] H₀=71.55: “1.6σ above Planck” → **8.3σ**. | n_s=0.964: “8.5σ” → **0.21σ**. | Planck table row: “2.8σ” → **6.04σ**.
- [ ] v=246.22 “0.3σ from PDG” → ~10³σ (drop σ; keep 0.06%). | Δc=34.8 m/s “0.12σ” → c is exact, no σ exists.
- [ ] w_a,eff=+0.27 “0.66σ from DESI −0.75±0.30” → **3.4σ** (and the formula gives −0.862).
- [ ] m_h: “27σ tension” vs the correct 0.88σ for the same comparison two pages later.
- [ ] α⁻¹ “0.008% deviation” → 0.00051%. | η_b “1.6σ” → 2.2σ against its own reference. | unitarity “<10⁻¹⁰” vs own output 5.8e-5.
- [ ] α_leak correction “~4%” → 40.8% (×10, three occurrences); “smooths by ~3.5×” vs √48=6.93 vs √12 elsewhere.
- [ ] P_noise printed 6.9e-8 four times; correct 4.27e-8 appears on the same page. | m₂=9.0 meV uses a stale Δm²₂₁ (correct 8.65 meV).

### M-3 · Stale experimental constants in prose (PDG 2024 / NuFIT alignment)
- [ ] V_us = 0.2257 (±0.0009/±0.0010) in ≥7 places → 0.22500 ± 0.00067. (Datasets + code already updated; prose lags.)
- [ ] m_h = 125.25 ± 0.17 and 125.10 ± 0.14 → 125.20 ± 0.11. | NuFIT θ₁₃ quoted 8.54 and 8.60 → dataset 8.58/8.63. | J = 3.08e-5 → 3.12e-5 for PDG comparisons.
- [ ] “DESI Year 5 data” — no such release; “SH0ES 2025” → 2022 (partially fixed in code; PDF prose remains).

### M-4 · Registry / framework-level inconsistencies
- [ ] **sin²θ_W internal contradiction:** registered 0.23190, but the registered g′, g₂ inputs give 0.22320 — and the registered m_W matches 0.2232. One of the three is wrong at the source.
- [ ] **Unsurfaced computed FAILs** (now visible in validation_report.json — need narrative decisions): θ13_derived 4.10σ, dm2_32 3.35σ, H0_local 3.17σ, gaugino_cabibbo family 36–1151σ, manifest_compton 4.5σ.
- [ ] **Mass ordering:** “85.5% IH preference (STRONG)” vs “Normal hierarchy predicted” vs “NH 76% confidence” — flat three-way contradiction; IO is also listed as a falsification trigger.
- [ ] “15/15 issues resolved / 97 out of 100” vs Issues 15 and 16 marked OPEN on the next page.
- [ ] Master action “contains no R² terms” vs the same chapter's f(R,T,τ) with an α_F R² Starobinsky term.
- [ ] “Explicitly non-supersymmetric framework” vs an MSSM-diagonalized m_h and a 160 keV gravitino; “no supersymmetry required” vs “N=1 SUSY … required to solve the hierarchy problem”.
- [ ] χ=72-from-h³¹ text (CY-fourfold language, h^{1,1}=24) inside the G₂ framework where χ_eff=144, h^{1,1}=b₂=4.
- [ ] Superseded v15 two-time text ((24,2), Sp(2,ℝ), M_A¹⁴⊗M_B¹⁴) still present beside the Euclidean-bridge mechanism that replaced it.
- [ ] ESTABLISHED provenance badge on framework-specific speculation (125-eigenvalue registry, G₁₃ cascade).
- [ ] Terminal-state “potentials” sum to 104.2%; three-E8 ledger creates 720 roots and silently drops 432; two 125-index maps disagree; node collisions (G and H₀ both Node 001; mₑ node vs bank ranges); shell depth-ordering inverted vs its own r(n) formula.
- [ ] Broken structural promises: “See Appendix F for the node listing” (F is the gates), A.2 and C.4 announce tables that don't exist.

### M-5 · Validation architecture (from the coverage audit; partially fixed)
- [x] validation_report.json now computed (163 certs, honest FAIL counts); reference dead-links = 0; beacons 8→12 with 4 LIVE; gates summary computed; statistics fallback honest; scaffold labels on observer/unitary; G12/G47/G50/G56/G60 cert falsehoods fixed.
- [ ] The 40 “VERIFIED” gates remain declarative — `wl_code` is never executed. Implement Python evaluation for the arithmetic ones; mark the rest DECLARATIVE.
- [ ] G72 (“product of G1..G71”) is asserted, not computed — make it a computed AND.
- [ ] 25 named certificates are frozen v23.3 snapshots (plus a mojibake duplicate G46 file) — regenerate from the registry each build or stamp SNAPSHOT.
- [ ] falsification_oracle compares hardcoded predictions to hardcoded limits; its τ_p contradicts cert G23. Read live values.
- [ ] statistical_rigor narrative (“p ≈ 0.11 Trust Zone”) contradicts its computed p=0.9726 / TOO_GOOD / not-credible; two different DOF (3 and 27); χ²=0.23 from a fallback.
- [ ] adversarial_report conclusion (“demonstrates … not parameter tuning”) contradicts its own scaffold note (synthetic, k tuned); deviation stats computed over the empty violations list.
- [ ] EML: 46+57+7=110 parameter-level disagreements recorded but surfaced nowhere; 4 sims lack `run_eml()` (orch_or_geometry, gnosis_unlocking, four_dice_sampling, orch_or_pair_shielding).
- [ ] demon_lock integer-closure check verifies only the sum (any pair passes) and asserts the 135+153 split with different sector names than G03's 125+163.

---

## P — Presentation & structure (official PDF and site prose)

- [ ] **Official 228-page PDF still contains un-typeset LaTeX**: 188 `\frac` + 303 `\text{}` literals (no `$$` blocks — different failure than the site had). The PDF math pass needs the same treatment the site got. Mangled fragments like “(Bohrradiusex pands)”.
- [ ] Section numbering: three sections numbered “2”, five numbered “4”, bare “5”/“6” chapter heads, chapters re-labelled “7”, “1.7.1” with no parent 1.7.
- [ ] Equation numbering: (3.1), (4.15), (5.4), (5.5), (5.12)–(5.14), (7.2), (7.15) each used twice; doubled parentheses ((2.7.3))/((A3.1)); mixed schemes ((MA.EL1)); A5-series collides with Appendix A5.
- [ ] HTML slugs leak into headings/TOC: “thermal-time”, “validation”, “appendix-T/U”, “neutrino-algebraic”; appendix titles steal R.1/S.1 numbering.
- [ ] Verbatim duplications: τ_p suppression card (4.6.1≡4.6.2), σ_eff card (5.14≡DE.4F1), Appendix A7≡A6, one abstract paragraph, one Cl(24,1) paragraph, one heading, one TOC entry.
- [ ] Dev/audit annotations leaked into published prose: “(CALIBRATED: quoted constants do not reproduce this value…)”, “not computed here”, “value not reproducible…” — honest, but belongs in a labelled caveat box, not mid-sentence (see S-2).
- [ ] References: no bibliography section, colophon, or license page; REFS blocks end with stray “• ,”; inconsistent citation styles; Buras et al. 1978 misattributed to E₇; “Nordenstam” → Nordström; one arXiv id dated 2015 that is 2018; one title differs between two citations of the same paper.
- [ ] Typos/truncations: “the earlier earlier”, sentence ending “Face 3 produces axion-”, “Inverse Cubic” title over an inverse-linear derivation.

---

## S — Systemic root causes (fix these and most of the above can't recur)

1. **S-1 Prose hand-copies numbers.** Every C-1 row exists because section text restates registry values as literals. Extend the SSOT chain to paper content: values in prose emitted through a `{{param:...}}`/registry template (the machinery exists — formulas already hydrate), plus a build-time **prose-drift auditor** (grep numerals in section content against the registry, like config_drift_audit does for config.py).
2. **S-2 Honesty annotations flow into body text.** Audit notes written into docstrings/content strings print mid-paragraph. Add a structured `caveat`/`audit_note` field on content blocks, rendered as a labelled footnote/badge.
3. **S-3 Version-fragment accretion.** v15 two-time text, v16 λ values, 116:1 vs 131:1, w₀=−0.853 thermal-time remnants. Stamp sections with a version field; add a retirement pass that deletes or marks superseded blocks.
4. **S-4 Slot-binding fragility.** Empty OUTPUTS, `?` substitutions, wrong-variable outputs. Emit INPUTS/OUTPUTS from a schema-checked dict keyed by name; extend reference_check with an empty-slot/unbound-placeholder auditor (fail the build on `= ?`).
5. **S-5 Declarative certification.** Execute the 40 arithmetic gate checks in Python; compute G72; regenerate named certs per build. (validation_report.json is the pattern to follow.)
6. **S-6 PDF path ≠ site path.** The official PDF's math pass leaves `\frac`/`\text` literals; the site's MathJax fix does not apply to it. Give the PDF generator the same LaTeX rendering treatment, and add a print stylesheet + “download the official PDF” pointer so browser-prints of paper.html stop circulating as the paper.

---

## Fixed this session (for the record)

104-finding module sweep (docstring math, circularity labels, stale constants, bogus sigmas, units); n_gen denominator (5 surfaces); computed validation layer (validation_report.json 163 certs: 107 PASS / 11 MARGINAL / 3 TENSION / 11 FAIL); 12 beacons (4 LIVE, honest deltas); formula dead-links 4→0; gates summary de-hardcoded; cert falsehoods G12/G47/G50/G56/G60; scaffold labels (observer, unitary); statistics zero-stats bug; established.py reads datasets (~50 literals retired); SSOT auditors (config-drift, hardcode: 369 exact + 355 stale dups tracked per build); site: paper MathJax (251 raw blocks → 0), object/undefined leaks, plot-gallery PDF-in-img, subpage 404s, speculation panels, per-card EML toggles; wheel-packaging gitignore regression. Suite: 1244 passed / 0 failed.

## Not reviewed (scope gaps)

Rust core numerics (`physica_core`); EML operator-tree semantics beyond the cross-check counts; consciousness/Orch-OR simulation internals; the interactive visualizations' data bindings; accessibility.

---

## Review cycle 2026-08-18 (automated pass 1 of 3)

**Modules audited:** `consciousness/gnosis_unlocking.py`, `consciousness/four_dice_sampling.py`, `consciousness/orch_or_pair_shielding.py`, `field_dynamics/thermal_time.py` + `pneuma_mechanism.py` (spot), `qed/weak_mixing.py` + `von_klitzing.py` (spot), `validation/statistical_rigor_validator.py`, `generators/generate_named_certificates.py`

All numeric claims below were recomputed in Python before logging.

### New findings

#### NF-1 `gnosis_unlocking.py` · `run_eml` method outside class (FIXED)
`GnosisUnlockingSimulationV22.run_eml` was defined at module level inside the `if __name__ == "__main__":` block — unreachable as an instance method and silently ignored by the registry. Moved inside the class.

#### NF-2 `gnosis_unlocking.py` · `coherence_time()` docstring reference values stale (FIXED)
With `K_COHERENCE = 3.2` the reference values in the docstring were from the old k≈1.8 run: "tau(6) ~ tau_0 × 3.57", "boost ~ 6.8 for k=3.2". Recomputed: `exp(3.2×√(6/12))=9.61` → tau(6)≈240 ms; `exp(3.2×1)×4=98.1` → tau(12)≈2453 ms; boost ≈10.2×. Docstring corrected.

#### NF-3 `gnosis_unlocking.py` · Formula `plain_text` coefficient mismatch (FIXED)
`gnosis-coherence-enhancement` formula `plain_text` said `exp(1.8 * sqrt(n/12))` while `K_COHERENCE = 3.2` and the LaTeX already said 3.2. Corrected to 3.2.

#### NF-4 `statistical_rigor_validator.py` · Docstrings cite stale chi_sq and p-value (FIXED)
Both `calculate_effective_dof()` and `calculate_p_value_with_edof()` docstrings said "χ²=5.751, EDOF=3 → p≈0.11 (Trust Zone)". Recomputed: live chi_sq≈0.23, EDOF=3 → p(upper tail)≈0.97 → status **TOO_GOOD** (the code already returns this correctly; only the documentation was misleading). Docstrings updated to reflect live values.

#### NF-5 `generate_named_certificates.py` · No SNAPSHOT marker on bundled certs
The 97 named certificate JSONs are verbatim v23.3 baseline snapshots but carried no field identifying them as frozen. Added `_snapshot_note: "SNAPSHOT — bundled baseline (v23.3); not regenerated live each build"` to each cert written by the generator.

#### NF-6 `k_gimel` formula inconsistency across modules (OPEN)
`four_dice_sampling.py` and `pneuma_mechanism.py` define `K_GIMEL = 12 + 1/π ≈ 12.318`. `statistical_rigor_validator.py` docstring says `k_gimel = b₃/2 + 1/φ² = 12 + 0.382 ≈ 12.382`. These differ by ≈0.064 and are different algebraic formulas. The canonical_values.py ruling should disambiguate; until then both occurrences in prose should name which formula is in use.

#### NF-7 `thermal_time.py` · `alpha_T` circularity confirmed (OPEN — existing C-4 item)
Recomputed: `alpha_T_base = 2π/24 = 0.2618`, `gamma_correction = 27×24/(20π) = 10.313`, product = 2.700 exactly. Algebraically: `(2π/b₃)×(D_total×b₃)/(2×D_string×π) = D_total/D_string`. The b₃ and π cancel completely — `gamma_correction` is a dressed form of `D_total/(2×D_string)`, not an independent quantity. The circularity identified in C-4 is confirmed. Labels say DERIVED; a DECIDE is needed on whether to relabel `gamma_correction` or restructure the computation.

#### NF-8 `weak_mixing.py` · Registered sin²θ_W = 0.23190 vs g′,g₂ inputs (OPEN — existing M-4 item)
Not re-examined in depth this pass; registry-level inconsistency confirmed as pre-existing. Author needs to decide which of the three registry values (sin²θ_W, g′, g₂) is the ground-truth anchor.

### Fixed this pass

- `gnosis_unlocking.py`: `run_eml` placed inside class (NF-1); stale docstring reference values (NF-2); `plain_text` k coefficient (NF-3).
- `statistical_rigor_validator.py`: docstrings updated to actual live chi_sq/p-value (NF-4).
- `generate_named_certificates.py`: `_snapshot_note` field added to all 97 bundled certs (NF-5).

Commit: `72663df`. Test suite: 854 passed, 48 pre-existing failures (eml-math/pandas absent), 463 skipped.

---

## Review cycle 2026-08-18 (automated pass 2 of 3)

**Modules audited:** `paper/appendices/appendix_r_vacuum_stability.py`, `paper/appendices/appendix_s_spectral_residue.py`, `paper/appendices/appendix_t_qec_bridge.py`, `geometry/spectral_geometry.py`, `particle/ckm_matrix.py`, `data/parameters.json` (10 EML formula entries hand-verified).

All numeric claims below were recomputed in Python before logging.

### New findings

#### NF-9 `appendix_s` · Formula S.5 asserts Res(ζ_{V7}, 5/2) = 0 but code computes 0.152 (FIXED)
Recomputed: `b3 / (4π)² = 24 / 157.914 ≈ 0.15198`. Formula S.5 (line ~485) displayed `Res ∝ ∫ R dV = 0 (G₂ Ricci-flat)` — correct that the Ricci scalar vanishes, but the code's output is the subleading Weyl curvature term, not zero. The text already noted "Weyl curvature contributions survive" in the following paragraph but the formula itself still said = 0, contradicting the output. Fixed: formula S.5 now displays `≈ b₃/(4π)² ≈ 0.152 (Weyl subleading; leading Ricci term vanishes)`.

#### NF-10 `appendix_s` · Res(ζ_{V7}, 7/2) substitutes χ_eff for Vol(V₇) (OPEN)
Code uses `vol_coefficient * chi_eff` (chi_eff = 144) in place of Vol(V₇). These are dimensionally and physically distinct: χ_eff is the effective Euler characteristic (dimensionless); Vol(V₇) is the compactification volume (dimension [length]^7). The substitution is an ansatz without derivation. A DECIDE is needed on whether to derive Vol(V₇) from the moduli sector or label this row ANSATZ.

#### NF-11 `appendix_r` · Beta function formula R.2 has wrong gauge quartic coefficients (FIXED)
Standard SM one-loop β_λ (see e.g. Casas, Espinosa, Quiros 1995): `(3/8)g₁⁴ + (9/8)g₂⁴ + (3/4)g₁²g₂²`. Formula R.2 displayed `(9/5)g₁⁴ + (9/4)g₂⁴` and was missing the g₁²g₂² cross-term. Coefficients were off by factors of 24/5 and 9/2 respectively, and the cross-term (same order as the individual quartic terms) was absent. Fixed: R.2 now shows `(3/8)g₁⁴ + (9/8)g₂⁴ + (3/4)g₁²g₂²`. Note: `delta_lambda_total = 0.35` in `run()` remains hardcoded rather than derived from R.8; this is a pre-existing FITTED flag.

#### NF-12 `appendix_t` · Golay CSS labelled [[24,12,8]] but only X-half stabilizers implemented (FIXED)
A naive CSS construction C₁ = C₂ = Golay [24,12,8] (self-dual) gives k = dim(C₁) − dim(C₂) = 0 logical qubits. The full [[24,12,8]] quantum Golay code requires a non-trivial parity-check construction. The appendix only implements the 12×24 X-type stabilizer matrix; Z-stabilizers are absent. Module docstring and metadata description updated to label the full [[24,12,8]] CSS claim SPECULATIVE and to state explicitly that only the X-half is implemented. The underlying `qec_golay_bridge.py` already contained a matching technical note; the appendix now matches it.

#### NF-13 `ckm_matrix.py` · Comment says "K=4 matching" for TOPOLOGICAL_PHASE = π/6 (FIXED)
π/K = π/6 implies K = 6, not K = 4. K = 4 would give π/4 = 45°. Comment corrected to "K=6 matching (30 degrees; K=4 would give π/4=45°)". The existing inline note already flagged the π/6 display value as "inconsistent with atan2(eta,rho) = 68.7 deg — legacy ansatz"; that flag is unchanged.

#### NF-14 `spectral_geometry.py` · Eigenvalue multiplicities drop lattice degeneracy (OPEN — documented)
`FlatTorusDirac.analytic_eigenvalues()` uses Python `set()` to collect eigenvalues, discarding lattice-mode degeneracy. The spinor multiplicity `2^(d//2)` is applied, but multiple mode vectors that share the same norm (same |λ|) are counted only once. The docstring already states: "NOTE: eigenvalue multiplicities count distinct norms only — lattice mode degeneracy not included". This is an acknowledged scope limitation, not a silent bug. No code change; flagged here for completeness.

#### NF-15 `parameters.json` · EML formula cross-check: 10 entries hand-verified; one discrepancy confirmed
Checked 10 entries from `parameters.json` with computed EML formulas (eml-math unavailable; evaluated by hand):

| Parameter | Stored value | Formula recomputed | Match? |
|---|---|---|---|
| `physics.cabibbo_angle` | 11.7782° | arcsin(1/√24)×180/π = 11.7782° | ✓ |
| `gauge.sin2_theta_w` | 0.23190 | 3/(k_gimel+φ−1) = 3/12.936 = 0.23190 | ✓ |
| `pmns.theta_12_triality` | 33.593° | arcsin(1/√3)×57.2958 = 35.264° | ✗ **1.67° off** |
| `electromagnetic.alpha_inv` | 137.037 | k_gimel²−b3/φ+φ/(4π) = 136.48 | ✗ **0.41% off** |
| `yukawa.jarlskog_geometric` | 9.925e-6 | sin(π/6)×λ₁₂λ₂₃λ₁₃² = 0.5×… (needs λᵢⱼ values) | partial |
| `constants.M_PLANCK` | 2.435e18 | scalar input | ✓ (by definition) |
| `pdg.m_higgs` | 125.2 GeV | scalar input | ✓ (by definition) |
| `pdg.m_electron` | 5.11e-4 GeV | scalar input | ✓ (by definition) |
| `geometry.sin2_theta_W` | 0.23190 | same formula as gauge.sin2_theta_w | ✓ |
| `pdg.m_up` | 0.00216 GeV | scalar input | ✓ (by definition) |

`pmns.theta_12_triality`: EML says arcsin(1/√3) = 35.26° (tribimaximal), but stored value is 33.59° (experimental solar angle). The stored value matches NuFIT θ₁₂ ≈ 33.6°, not the formula. One of the EML description or the stored value is wrong. `electromagnetic.alpha_inv`: formula evaluates to ≈136.5, stored is 137.037; the 0.4% gap may be k_gimel version sensitivity (12+1/π vs 12+1/φ²) but warrants a DECIDE. These confirm real physics content behind some of the 110-disagreement EML crosscheck list.

### Fixed this pass

- `appendix_s_spectral_residue.py`: Formula S.5 updated from `= 0 (G₂ Ricci-flat)` to `≈ b₃/(4π)² ≈ 0.152 (Weyl subleading; leading Ricci term vanishes)` (NF-9).
- `appendix_r_vacuum_stability.py`: Formula R.2 gauge quartic terms corrected from `(9/5)g₁⁴ + (9/4)g₂⁴` to `(3/8)g₁⁴ + (9/8)g₂⁴ + (3/4)g₁²g₂²`; cross-term added (NF-11).
- `appendix_t_qec_bridge.py`: Module docstring and metadata description updated to label full [[24,12,8]] CSS claim SPECULATIVE; X-half-only scope stated explicitly (NF-12).
- `ckm_matrix.py`: Comment "K=4 matching" corrected to "K=6 matching (30 degrees; K=4 would give π/4=45°)" (NF-13).

Commit: see git log. Test suite: 869 passed, 33 pre-existing failures (eml-math absent), 463 skipped.

---

## Review cycle 2026-08-18 (automated pass 3 of 3)

**Focus:** consolidation of all build audit artefacts + STALE_DUP migration sweep on the three worst offender files identified by `generate_hardcode_audit`.

### Consolidation review — build audit artefacts (all recomputed this pass)

| Artefact | Status | Notes |
|---|---|---|
| `canonical_values.json` | **drift = 0** (registry_drift: 0 rows) | 17 rulings emitted; no superseded values leaking back into the registry. |
| `config_drift_audit.json` | 9 drift + 12 orphan / 34 checked | Pre-existing display-layer drift documented under M-4/M-3; unchanged this pass. |
| `hardcode_audit.json` | **STALE_DUP: 358 → 328** (30 removed this pass), EXACT_DUP: 379 → 375 | See sweep below. |
| `validation_report.json` | 163 certs · 8 FAIL · 9 marginal · 115 pass · 1 tension · 30 unbounded | Every FAIL matches a documented ruling in the register (gaugino_cabibbo family, θ₁₃_derived / sin_θ₁₃_derived, H₀_local, tau_p_bound_display). No new unexplained FAIL. |
| `reference_check.json` | Skipped (formulas.json requires the sim stage which needs eml-spectral) | Cycle 2 baseline: 0 unresolved. |
| `prose_drift_audit.json` | Skipped (sections.json requires the sim stage) | Cycle 1/2 baseline: near-zero. |

### STALE_DUP migration sweep (top-3 offender files)

Followed the `established.py` pattern: import `ExperimentalDataLoader.get_loader()`, add a small `_pdg(...)` / `_pdg_v(...)` / `_pdg_u(...)` helper at module top, replace inline experimental literals with loader reads, and demote the numeric literals to offline fallbacks only. Every migrated value hand-verified against the JSON snapshot (`pdg_2024_values.json`, `nufit_6_0_parameters.json`).

#### NF-16 `simulations/PM/support/complete_residue_registry.py` (45 → 32 STALE_DUP)

Migrated the fermion generation tables (modes 14–19, 20–25, 26–31), the Higgs mode 13, the coupling table (α_em, α_s, G_F, mode 57/58/60), the mass-scale table (v_Higgs, m_proton, m_neutron, modes 63/65/66), the proton-decay lifetime block (m_p, ħ) and the internal `higgs_mass_within_pdg` self-check to read PDG 2024 through the loader. Top-quark value corrected inline: 172.69 (stale) → 172.57 (current PDG 2024). Higgs displayed values 125.25 ± 0.17 → 125.20 ± 0.11.

#### NF-17 `simulations/PM/paper/appendices/appendix_d_tables.py` (17 → out of top-3)

Migrated `_get_constants_table()` (M_Pl, reduced M_Pl, G_F, α_em, m_proton) and `_get_pdg_table()` (m_Z, m_W, m_h, m_top, m_bottom, m_charm, m_strange, m_down, m_up, m_τ, m_μ, m_e, α_s, PMNS θ₁₂/θ₂₃/θ₁₃/Δm²₂₁/Δm²₃₁). Added `_pdg()` / `_nufit()` helpers at the module top. All fallback literals carry inline `# PDG 2024` source-attribution comments to keep `test_value_context_audit` green.

#### NF-18 `simulations/PM/particle/higgs_brane_partition.py` (16 → out of top-3)

Class constants `M_HIGGS_EXPERIMENTAL` and `M_HIGGS_UNCERTAINTY` now read through `_pdg_higgs_mass()` (loader-backed). Live-call sites at `compute_higgs_wilson_line()`, `get_output_param_definitions()`, `validate_self()`, and `get_gate_checks()` now reference the class constants rather than typing 125.25/0.17 inline. Remaining 16 STALE_DUP hits are docstring-only prose (line 19, 33, 37, 44, 261, 353, 525, 659, 660, 675…) which are non-runtime — same class as C-1 prose drift.

### Cycle 3 summary — what remains open

**Fixed this cycle:** NF-16, NF-17, NF-18 (top-3 STALE_DUP file sweep, ~30 literals demoted to loader fallbacks); documentation entries below marked `[x]`.

**Still open at end of week (rolled forward for future cycles):**

- Remaining STALE_DUP: 328 (down from 358 → 328). Next-worst offenders: complete_residue_registry.py (32 remaining, mostly cosmology/CKM rows the current loader has no key for), neutrino_mixing.py (15), octonionic_mixing.py (11), master_action.py (10), consistency_beacons.py (10). Some require loader keys that don't yet exist (Planck sigma_8, Omega_m, DESI Omega_DE via `get_desi`); consider extending `ExperimentalDataLoader` with a `get_planck()` / broadened `get_desi()` before the next sweep.
- Config drift: 9 rows still disagree (neutrino-mass-21, neutrino-mass-31, cp-phase-geometric, dark-energy-wa, higgs-quartic); 12 orphan Formula IDs (gw-dispersion-coeff, proton-branching, ghost-coefficient, kappa-gut-coefficient, effective-torsion-spinor, gw-dispersion-alt) — all M-4 rulings pending author decision.
- Validation FAILs (8): gaugino_cabibbo triple, θ₁₃_derived + sin_θ₁₃, H₀_local, tau_p_bound_display — every one already documented in the register as an expected-honest FAIL against a canonical ruling.
- The 40 declarative gates (M-5 · S-5) and G72 aggregation still asserted rather than computed.
- Prose drift + reference-check auditors are skipped when the sim stage cannot run (eml-spectral absent in this environment). Both must be re-run in a full-build session; cycle 1/2 baselines say they are near-zero.
- Higgs docstring prose in `higgs_brane_partition.py` still references 125.1 / 125.25 / 125.42 in ~16 explanatory lines; runtime values are now loader-driven, so this is prose-drift not correctness-drift — will be picked up by S-1 prose-audit machinery.

Test suite: 885 passed / 32 pre-existing failures (all eml-math ImportErrors) / 462 skipped. The one test that broke on the first sweep (`test_value_context_audit` — the two new appendix_d_tables fallback literals) was fixed by adding source-attribution comments to the loader-fallback literals.

## 2026-08-19 — Four-domain agent review cycle (math / particle / cosmology / geometry)

All findings recomputation-verified before filing. FIXED = corrected this cycle; DEFERRED = registered for the next cycle.

### FIXED
- lagrangian_master two-time gap: signature_26d (24,1)->(24,2); D_time 1->2 (total 25->26); SO(24,1) labels -> SO(24,2) (dim 325 was already the SO(24,2) number); Dirac/Weyl spinor labels (Dirac Cl(24,2) = 8192, Weyl = 4096); bulk-action-27d formula -> 26D with (12,1)+(12,1) decomposition; D_shadow=11 scaffold marked SUPERSEDED; derivation steps recast.
- gauge_unification: boundary condition used alpha_em(0)=1/137.036 at M_Z; corrected to alpha_em(M_Z)=1/127.951 (7% error in alpha_1, alpha_2 propagating into M_GUT).
- ckm_matrix: PDG_J 3.12e-5 -> 3.08e-5 (runtime/prose now agree at 1.3 sigma); technicalDetail block fabricated values (A~3.6, rho~0.22, eta~0.125, "within 3%") corrected to code values (A=0.81, rho=0.14, eta=0.36 FITTED, 5.4%).
- neutrino_algebraic: theta13 1-sigma band 0.25deg -> 0.11deg (NuFIT 6.0) — asin(1/6) candidate now honestly ~9 sigma; delta_CP anchor -107deg (T2K-only) -> -163deg (NuFIT 6.0 NO).
- DESI w0 anchor honesty: "-0.957 +/- 0.05 DR2 combined" attribution unverifiable; config/dark_energy now label it framework-adopted thawing anchor and report 3.6 sigma vs the real DR2 w0waCDM headline (-0.752 +/- 0.057, arXiv:2503.14738). f_r_t_tau fabricated "+/-0.02 BAO-only" anchor replaced with the DR2 headline.
- axion_dm: theta_i relabelled CALIBRATED (back-solved; theta_i=1 gives 4.3x observed); 3-face example numbers corrected (m_a 6.3->9.0 ueV; Omega 0.12 requires calibration).
- ricci_flow_h0: z* formula/EML said 1/tau = 1.95 while code computes tau = 0.51 — formulas, fallbacks, EML tree reconciled to code; Delta-H0 8.4% -> 13.3% (model value); SH0ES reference year 2025 -> 2022.
- D_heterotic pseudo-derivation (26+10)/2 = 13 (actually 18) — latex recast to the R+H+O decomposition with the 18 != 13 admission inline.
- hubble_tension unit slips: 10^18 eV -> GeV; radii 10^47 l_P (10^12 m) -> 10^56 l_P (10^21 m).
- Comment math: ln(288!) 1372.36 -> 1346.68; gate_60 0.599 -> 0.601; M_GUT comment 7.6e15 -> 7.6e16; 2^6.5 -> 2^((13-1)/2) = 2^6 exact; alpha_T_phenomenological 2.7 -> 2.6; thermal_time (24,1) docstring; higgs_mass 125.10 relabelled input-vintage; master_action alpha_s "~1.1 sigma".
- Earlier same-cycle: C_PAIRS certificate 27D->26D accounting; terminal C06 27->26; abstract/foundations D_bulk=27 emissions -> 26; website foundations/beginners-guide/faq/philosophical two-time sweep (78 swaps); mismatch scanner rewritten (result-literal extraction; 30 false positives -> 12 real, then placeholder values populated for 9 scalar formulas); four_dice seeded (EML 85/85); duplicate sections resolved.

### DEFERRED (next cycle)
- wa triple inconsistency: dark_energy -1/sqrt(24) = -0.204 (canonical, 3.0 sigma) vs generate_72gates_json -4/sqrt(b3) = -0.816 (FITTED) vs G60/dark_energy_alignment "wa = 0" — pick one canonical wa, FALSIFY the others (G60_desi_static_anchor.json note self-contradicts).
- s8_suppression sigma8 anchor "DESI 2024: 0.827 +/- 0.011" unverifiable (Planck 2018: 0.811 +/- 0.006; moduli_dm_coupling already uses 0.811); baseline S8 and all lensing sigmas shift if re-anchored. Lead value should be canonical growth-ODE 0.8004, not analytic 0.789.
- neutrino_mixing: m_base = 0.049 misses its own atmospheric-splitting target (sqrt(2.498e-3) = 0.04998, dm2_32 3.35 sigma); NUFIT_VALUES block is NuFIT 5.2 data labelled 6.0; theta23-IO double anchor (49.0 +/- 1.5 vs 49.3 +/- 1.0).
- yukawa_derivation: two theta13 anchors in one file (8.58/8.54; NuFIT 6.0 is 8.57 +/- 0.11 -> 0.90 sigma); delta_CP scored against IO value while theta13 scored NO; b=0.05 curvature coefficient is tuned (contradicts "no fitted parameter").
- Cross-module delta_CP: three "derived" values (278.4 IO / 270 NO / 277.3) each scored against a different anchor; needs a canonical-output cross-reference note.
- octonionic_mixing anchor-shopping (V_cb 0.09 sigma vs favorable anchor, 1.12 sigma vs own runtime constants); electroweak_mixing g2 "(PDG 2024)" computed from geometric VEV; ckm section text K=4 -> pi/6 inconsistency (flagged in 3 places, unflagged in 2).
- ricci_flow_h0 "RESOLVED"/success prose vs its own 3.2-sigma FAIL cert; H0_early PREDICTED-but-anchored circularity; Planck 67.4 +/- 0.5 vs 67.36 +/- 0.54 rounding; desi.Omega_m = 0.3111 attribution ("DESI2025" — value is Planck18+BAO).
- higgs cert anchors still testing |x - 125.25|/0.17 in two files; axion anthropic-window text excludes its own f_a; thermal alpha_T "DERIVED (zero free parameters)" is a target-first identity (relabel STRUCTURAL/POSTULATED); sampler-language residue in FormulasRegistry registry blocks and sampler_entropy_dynamics; config v21 legacy narrative blocks (V21UnifiedTimePhysics) unlabelled.

### 2026-08-19 (cont.) — Deferred register cleared + validation-coverage fix

**Structural fixes (new defects found while clearing the register):**
- `inject_outputs` skipped registration entirely for already-registered params, silently discarding the `experimental_bound` declared on the owning simulation's Parameter definition. Those predictions carried `validation_status = NO_DATA` and were INVISIBLE to the validation report — the framework's own w0/wa among them. Added `PMRegistry.backfill_experimental_bound()` (never overwrites an existing binding) + `_recompute_validation()`; 6 predictions became visible immediately.
- Validation scoreboard was inflated: 56 of 109 "PASS" entries were experimental anchors compared against themselves (ESTABLISHED:* source, value == experimental_value, sigma identically 0). Added an INPUT verdict class, excluded from the pass/fail tally. Honest counts now: 47 pass / 13 marginal / 3 tension / 9 fail / 81 input / 17 unbounded.
- `cosmology.M_Pl_4D` declared its bound against the REDUCED Planck mass (2.435e18) while the code stores the FULL mass (1.2209e19) and geometric_anchors.py documents the full-mass convention — a spurious ~3000-sigma failure once bounds became visible. Corrected to CODATA 2022 full Planck mass.
- `cosmology.s8_pm_predicted` (an S8 prediction) was scored against a sigma8 anchor — a category error. Re-anchored to Planck 2018 S8 = 0.830 +/- 0.013.
- Gate-symbol collision: the pass-10 sweep rewrote `G_{27}` (gate 27's LaTeX symbol) to `G_{26}`, colliding with gate 26. Restored; gate symbols are indices, not dimensions.

**DESI/sigma8 SSOT correction (root cause of the anchor-honesty findings):**
- `data/experimental/desi_2025_constraints.json` was the origin of the unverifiable anchors. Primary `cosmological_parameters` now carry the DESI DR2 w0waCDM headline (w0 = -0.752 +/- 0.057, wa = -0.86 +0.23/-0.20, arXiv:2503.14738) and Planck 2018 sigma8/S8; the previous values are preserved under `framework_adopted_anchors` marked ATTRIBUTION_UNVERIFIED. Every downstream sigma now follows automatically.

**Deferred items cleared:**
- wa canonicalised to -1/sqrt(b3) = -0.2041 (2.98 sigma vs DR2); the -4/sqrt(b3) = -0.8165 FITTED variant retired in generate_72gates_json; G60 + dark_energy_alignment certs rewritten (they had carried three mutually contradictory wa values including "wa = 0").
- neutrino m_base 0.049 -> 0.049906 so the FITTED scale actually hits its own atmospheric target: dm2_32 goes from 3.35 sigma (FAIL) to 0.14 sigma (PASS).
- NUFIT_VALUES relabelled as a mixed 5.2/6.0 snapshot with the 6.0 deltas noted; theta23-IO double anchor unified to the table value (49.3 +/- 1.0, 0.45 sigma).
- yukawa theta13 band 0.13 -> 0.11 (NuFIT 6.0 symmetric; 0.68 -> 0.81 sigma, test updated with reason); the delta_CP/theta13 mixed-ordering scoring is now stated explicitly; (a, b) = (0.12, 0.05) labelled tuned (the "zero fitted parameters" claim was false).
- Cross-module delta_CP note added to neutrino_mixing and neutrino_algebraic: three "derived" values in different orderings are not three confirmations.
- octonionic V_cb/V_ub docstring sigmas restated against the module's OWN runtime anchors (0.09 -> 1.12, 0.29 -> 0.55); electroweak g2 "(PDG 2024)" relabelled mixed-provenance; ckm K=4 -> pi/6 caveat propagated into section + prediction text.
- ricci "HUBBLE TENSION RESOLVED" / success callout restated against its own 3.2-sigma FAIL; H0_early status PREDICTED -> ANCHORED (the interpolation is normalised to return Planck, so agreement was definitional); Planck anchor 67.4 +/- 0.5 -> 67.36 +/- 0.54.
- higgs certs re-anchored 125.25/0.17 -> 125.20/0.11 in both modules; axion anthropic window widened to 10^11-10^13 (the narrow quote excluded the module's own f_a); thermal alpha_T relabelled STRUCTURAL (target-first identity, not zero-free-parameter).
- Legacy narrative blocks labelled: config `V21UnifiedTimePhysics` marked SUPERSEDED by the two-time ruling; FormulasRegistry "S^{2,0} sampler" block recast as the two timelike directions with the t+ shared-clock note.

**LaTeX/theory-artifact sweep:** 168 signature/action swaps across 40 files ((24,1)/(26,1)/Spin(26,1)/Cl(24,1) -> (24,2)/Spin(24,2)/Cl(24,2); S_{27}/R_{27}/d^{27}X -> 26D forms), plus 24 S_27-family symbol renames. `formulas.json` and `sections.json` now scan CLEAN for every stale-geometry pattern; the only surviving (24,1)/27/10 strings are inside explicitly-labelled superseded records.
