# Triple-Track Inventory

**Date**: 2026-06-12  
**Total formulas**: 419  
**Triple-tracked (Arithma + EML + non-zero value)**: 0  
**EML + value only (Arithma stub)**: 106  
**Sentinel-valued (value == 0)**: 63  

## Track coverage

| Track | Count | Coverage |
|---|---:|---:|
| Arithma (latex or compact) | 0 | 0.0% |
| EML (any) | 417 | 99.5% |
| Non-zero numeric value | 106 | 25.3% |

## b₃-rootedness (from dependency_chains.json)

- b₃-rooted: **307** / 419
- Ambiguous: 3
- Non-b₃-rooted: 109
- Degraded walks: 9
- Arithma available at walk time: False

## By sector

| Sector | Total | Triple | EML+value | Sentinel | b₃-rooted |
|---|---:|---:|---:|---:|---:|
| paper | 188 | 0 | 28 | 35 | 133 |
| cosmology | 62 | 0 | 0 | 0 | 55 |
| particle | 40 | 0 | 40 | 0 | 34 |
| geometry | 26 | 0 | 16 | 2 | 22 |
| gauge | 23 | 0 | 1 | 22 | 10 |
| algebra | 16 | 0 | 0 | 0 | 14 |
| derivations | 15 | 0 | 0 | 0 | 2 |
| field_dynamics | 14 | 0 | 10 | 4 | 7 |
| qed | 11 | 0 | 0 | 0 | 11 |
| portals | 11 | 0 | 11 | 0 | 11 |
| support | 7 | 0 | 0 | 0 | 4 |
| consciousness | 4 | 0 | 0 | 0 | 2 |
| validation | 2 | 0 | 0 | 0 | 2 |
| **TOTAL** | **419** | **0** | **106** | **63** | **307** |

## Marquee formulas (13 b₃-rooted derivations)

For each marquee derivation: the formula ID found in `formulas.json`, the Arithma LaTeX (if any), the EML compact tree truncated to 120 chars, computed value, observed comparison, and b₃-rootedness chain depth.

### w0

- **ID**: `w0-derivation`  (label (3.1))
- **Category**: `DERIVED` · **triple_status**: `EML_ONLY`
- **Source simulation**: `results_v16_2`
- **Arithma**: _stub (empty)_
- **EML compact tree (120)**: `_SubNode(_NegNode(EMLPoint(0.0, 1.0)), _NegNode(EMLPoint(_NegNode(EMLPoint(_LitNode(1.0), EMLPoint(EMLPoint(_LitNode(1.…`
- **Computed value**: `-0.9583333333333334`
- **Observed parameter** (`cosmology.w0_derived`): value=`-0.9583333333333334` σ=`0.010341497880650344` status=`fully_derived`
- **b₃-rooted**: yes · depth=2 · path: `w0-derivation -> b3_leaf`

### w_a

- **ID**: `wa-nonlinear-correction`  (label (DE.4F3))
- **Category**: `DERIVED` · **triple_status**: `(unset)`
- **Source simulation**: `dark_energy_thawing_v16_2`
- **Arithma**: _stub (empty)_
- **EML compact tree (120)**: `ops.mul(wa, ops.add(eml_scalar(1.0), ops.mul(alpha_leak, eps_NL)))`
- **Computed value**: _none_
- **Observed parameter** (`cosmology.w_a_thawing`): value=`0.009369692847857367` σ=`0.010422432245119668` status=`fully_derived`
- **b₃-rooted**: yes · depth=2 · path: `wa-nonlinear-correction -> b3_leaf`

### n_s

- **Formula ID**: _no matching formula in `formulas.json`_
- **Parameter target**: `cosmology.n_s_pred`
- **Observed parameter row**: status=`fully_derived` value=`0.9636384168229182` σ=`0.010217437752278293`

### eta_B

- **ID**: `baryon-asymmetry-cycle-v18`  (label (6.8))
- **Category**: `DERIVED` · **triple_status**: `(unset)`
- **Source simulation**: `baryon_asymmetry_v18`
- **Arithma**: _stub (empty)_
- **EML compact tree (120)**: `ops.mul(ops.div(J_jarlskog, N_eff), ops.mul(delta_b3, ops.mul(ops.div(b3, chi_eff), ops.mul(ops.sin(delta_cp), ops.exp(…`
- **Computed value**: _none_
- **Observed parameter** (`cosmology.eta_baryon_geometric`): value=`6.185164569435048e-10` σ=`0.01033916279544254` status=`fully_derived`
- **b₃-rooted**: yes · depth=2 · path: `baryon-asymmetry-cycle-v18 -> b3_leaf`

### m_h

- **ID**: `higgs-mass`  (label (4.4.1))
- **Category**: `DERIVED` · **triple_status**: `EML_ONLY`
- **Source simulation**: `higgs_mass_v16_0`
- **Arithma**: _stub (empty)_
- **EML compact tree (120)**: `EMLPoint(4.829113417472866, 1.0)`
- **Computed value**: `125.1`
- **Observed parameter** (`higgs.m_higgs_pred`): value=`120.6228111675565` σ=`1.2153012946347994` status=`fully_derived`
- **b₃-rooted**: yes · depth=2 · path: `higgs-mass -> b3_leaf`

### alpha_inv

- **ID**: `alpha-inverse-geometric`  (label (3.1) Fine Structure Constant)
- **Category**: `GEOMETRIC` · **triple_status**: `EML_ONLY`
- **Source simulation**: `alpha_rigor_v16_1`
- **Arithma**: _stub (empty)_
- **EML compact tree (120)**: `_SubNode(_SubNode(EMLPoint(EMLPoint(_SubNode(EMLPoint(_LitNode(1.0), EMLPoint(EMLPoint(_LitNode(1.0), EMLPoint(0.693147…`
- **Computed value**: `137.03670177575597`
- **Observed parameter** (`constants.alpha_inverse_pred`): value=`137.03670177575597` σ=`1.3468610968245325` status=`fully_derived`
- **b₃-rooted**: yes · depth=2 · path: `alpha-inverse-geometric -> b3_leaf`

### n_gen

- **ID**: `generation-number`  (label (4.2.1))
- **Category**: `DERIVED` · **triple_status**: `EML_ONLY`
- **Source simulation**: `fermion_generations_v16_0`
- **Arithma**: _stub (empty)_
- **EML compact tree (120)**: `EMLPoint(_SubNode(EMLPoint(_LitNode(1.0), EMLPoint(EMLPoint(_LitNode(1.0), EMLPoint(_SubNode(EMLPoint(_LitNode(1.0), EM…`
- **Computed value**: `3.0`
- **Observed parameter** (`topology.n_gen`): value=`3` σ=`0.028678716312534262` status=`fully_derived`
- **b₃-rooted**: yes · depth=2 · path: `generation-number -> b3_leaf`

### g_a_gamma

- **ID**: `axion-portal-photon-coupling-v23`  (label (7.5))
- **Category**: `PREDICTED` · **triple_status**: `(unset)`
- **Source simulation**: `axion_dm_v18`
- **Arithma**: _stub (empty)_
- **EML compact tree (120)**: `ops.mul(ops.mul(g_agg, ops.div(alpha_em, eml_pi())), E_over_N)`
- **Computed value**: _none_
- **Observed parameter** (`axion.g_a_gamma_pred`): _not in ledger_
- **b₃-rooted**: yes · depth=3 · path: `axion-portal-photon-coupling-v23 -> axion-decay-constant-v18 -> b3_leaf` · via axion.f_a

### ReT_stabilized

- **ID**: `racetrack-potential`  (label (4.4.3))
- **Category**: `ESTABLISHED` · **triple_status**: `EML_ONLY`
- **Source simulation**: `higgs_mass_v16_0`
- **Arithma**: _stub (empty)_
- **EML compact tree (120)**: `EMLPoint(0.6059539688575679, 1.0)`
- **Computed value**: `1.833`
- **Observed parameter** (`moduli.re_t_attractor`): value=`1.833` σ=`0.0180698695021988` status=`fully_derived`
- **b₃-rooted**: yes · depth=2 · path: `racetrack-potential -> b3_leaf`

### sigma_m_refined

- **Formula ID**: _no matching formula in `formulas.json`_
- **Parameter target**: `field_dynamics.sigma_m_refined`
- **Observed parameter row**: _not present in ledger_

### theta_QCD

- **ID**: `c37cp-strong-cp-lock`  (label (Z.3))
- **Category**: `DERIVED` · **triple_status**: `EML_ONLY`
- **Source simulation**: `appendix_z_terminal_ledger_v24_2`
- **Arithma**: _stub (empty)_
- **EML compact tree (120)**: `EMLPoint(-1e+300, 1.0)`
- **Computed value**: `0.0`
- **Observed parameter** (`physics.theta_qcd`): value=`0.0` σ=`0.010115034805322103` status=`fully_derived`
- **b₃-rooted**: no · depth=1 · path: `c37cp-strong-cp-lock`

### dynamically_selected

- **ID**: `moduli-damping-v18`  (label (6.10))
- **Category**: `DERIVED` · **triple_status**: `(unset)`
- **Source simulation**: `baryon_asymmetry_v18`
- **Arithma**: _stub (empty)_
- **EML compact tree (120)**: `ops.exp(ops.neg(Re_T))`
- **Computed value**: _none_
- **Observed parameter** (`cosmology.dynamically_selected`): value=`2.0470466728037693e+24` σ=`2.112742449739149e+22` status=`numerical_agreement`
- **b₃-rooted**: yes · depth=2 · path: `moduli-damping-v18 -> b3_leaf`

### Omega_mirror

- **ID**: `axion-3face-relic-density-v23`  (label (7.6))
- **Category**: `PREDICTED` · **triple_status**: `(unset)`
- **Source simulation**: `axion_dm_v18`
- **Arithma**: _stub (empty)_
- **EML compact tree (120)**: `ops.mul(ops.mul(ops.mul(eml_scalar(3.0), ops.pow(alpha_leak, eml_scalar(2.0))), ops.mul(eml_scalar(0.12), ops.pow(ops.d…`
- **Computed value**: _none_
- **Observed parameter** (`cosmology.omega_mirror_h2`): value=`9.618304682770812e-05` σ=`0.010088341500452779` status=`numerical_agreement`
- **b₃-rooted**: yes · depth=3 · path: `axion-3face-relic-density-v23 -> alpha-leak-coupling -> b3_leaf` · via geometry.alpha_leak

---

## Definitions used in this inventory

- **Arithma present** ⇔ `arithma_latex` non-empty *or* `arithma_compact` non-null.
- **EML present** ⇔ any of `eml_latex`, `eml_tree_str`, `eml_tree_compact` non-empty.
- **Non-zero numeric value** ⇔ `value` is finite and ≠ 0 (the sentinel).
- **Triple-tracked** ⇔ Arithma ∧ EML ∧ non-zero value.
- **EML + value only** ⇔ ¬Arithma ∧ EML ∧ non-zero value.
- **Sentinel-valued** ⇔ `value == 0` (placeholder pending derivation).

## Source files

- Formulas: `H:/Github/metaphysica/AutoGenerated/formulas.json` (version 24.2, count 419)
- Ledger: `H:/Github/metaphysica/AutoGenerated/proof_completeness_ledger.json` (rows 681, sprint Sprint 5 task #7)
- Dependency chains: `H:/Github/PrincipiaMetaphysica/AutoGenerated/dependency_chains.json`
- Audit: `H:/Github/metaphysica/scripts/_audit_formulas.json`

