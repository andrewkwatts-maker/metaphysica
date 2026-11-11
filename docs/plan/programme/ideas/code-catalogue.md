# Lane code-catalogue (P7 history and ideas review)

Sources: the fork report (`python -m metaphysica.simulations.core.variants`, run 2026-11-11 with
`METAPHYSICA_OUT` in scratch; 26 forks, 8 not checkable against source), the catalogue files under
`src/metaphysica/simulations/core/variants/catalogue/` (paths below shortened to `cat/<file>`),
the falsified and withdrawn ledgers in code, the 61 deleted simulation files, and the two
`_retired` leftovers folders. `cv` = `src/metaphysica/simulations/core/canonical_values.py`.
First-seen dates of a fork are the first commit that added its id to `core/variants`.

## 1. Era summary (the model as the code states it on 2026-11-11)

- Bulk 26D at (24,2), "24 space, 2 times, one per shadow" (cat/g2_forms.py:336); ruled 2026-08-31 (cv:466).
- Two 13D (12,1) shadows, each with its own time, 13 = 4 + 7 (V7) + 2 (T2) (cv:475); no shared time (`config/parameters/bridge.py:131`).
- Internal space Y_7 = Joyce resolution of T^7/(Z2)^3 (`config/constants.py:78`); TCS #187 kept as RETIRED record (constants.py:76-80).
- Seed derived: b2 = A1 family count = 12, b3 = 7 + 3 b2 = 43 (cat/seed.py:95, 249); seed_24 (b3 = 24, b2 = 4) retired 2026-09-22.
- chi_eff = 2 x sum chi(K3) = 48 n (k3_reading, cat/g2_metric.py:150), 144 total / 72 per shadow (cv:475); n_gen = b2/4 = 3 (cat/seed.py:156).

## 2. Model timeline (as recorded in code)

| date | commit or file:line | old -> new | reason as recorded |
|------|---------------------|------------|--------------------|
| 2025-11-22 | cat/seed.py:187 (source 48ec267c) | n_gen = chi/2 -> chi/24 | "corrected from chi/2 to chi/24 for 8D manifolds" |
| v12.3 | config/parameters/shared_dimensions.py:112-113 | D_eff = 12.576, w0 = -(D_eff-1)/(D_eff+1) = -0.853 | none (legacy constants still in file) |
| v12.3 era | config/constants.py:65-69, shared_dimensions.py:120-123 | 1 observable (5,1) brane + 3 shadow (3,1) branes, RS warped | none; still declared, labels updated to (24,2) prose at pneuma_mechanism.py:943-972 |
| 2025-12-31 | cat/cosmology.py:157 (source 5755a1e0) | w0 = -11/13 (MEP, D=12) -> thawing quintessence -1 + 1/b3 | "w0 = -0.846, 1.76 sigma vs DESI 2025; replaced 2025-12-31" |
| 2026-01-10 | cat/cosmology.py:51 (source 0b984a37) | n_s = 1 - 2/b3 -> golden_modulated | "11.48 sigma off; replaced 2026-01-10" |
| v22 | config/parameters/bridge.py:133-135 | spatial-only (12,0) shadows over a shared time fiber -> per-shadow time | "RETIRED reading (v22) ... Kept on the books; nothing reads it." |
| 2026-08-19 | cv:475, cv:497-504 | 27D (24,1,2) sampler pair -> 26D (24,2), one time per shadow | "required both b3+2 and b3+3 as 'forced', shadows summed to 25 != 27" |
| 2026-08-20 | cv:467-469 | challenge to (24,2); (26,2) 28D recommended; TCS obstruction found | "the adopted signature is the one that fails" (lattice p - q mod 8) |
| 2026-08-25 | PM/algebra/neutrino_algebraic.py:38 | theta13 derived -> FALSIFIED | "R1 ruling 2026-08-25: about 39 sigma on the adopted path" |
| 2026-08-31 | cv:466; dca1fc1 (bulk_signature fork) | (24,2) kept as option (c); D_bulk = D_crit = 26 withdrawn | "the challenge below is NOT answered by this ruling" |
| undated | constants.py:76-80; config/nomenclature.py:456 | TCS #187 (CHNP 2015, h11 = 4) -> Joyce T^7/(Z2)^3 | "RETIRED reading ... kept as a record" |
| 2026-09-06 | cat/cosmology.py:295, 355 | dark-energy n: b2 = 4 ruled out, n = 24 kept | "RULED OUT 2026-09-06, on physics, despite being the BEST FIT BY A LARGE MARGIN" |
| 2026-09-06 | cat/g2_forms.py:377-380 | "Crowley-Nordstrom forces b2 + b3 odd" -> corrected | "is not what the literature says" |
| 2026-09-22 | cat/seed.py:95, 347; 8434d4a | seed_24 -> seed_43_joyce, (b2,b3) = (12,43) | "both derived from the A1 family count" |
| 2026-09-22 | cv:471-474 | D_crit = 26 = b3 + 2 withdrawn; b3, chi_eff follow forks | "SUPERSEDED IN PART (signature ruling 2026-08-31 and seed ruling 2026-09-22)" |
| 2026-09-26 | cat/cosmology.py:248 | dark_energy_betti b3_24 read "n = b3 = 24" -> frozen constant | "which the b3_seed ruling made false" |
| 2026-10-01 | cat/cosmology.py:176, 229 (D-015) | Re(T) computed vacuum demoted; calibrated Re(T) | "Re(T) is an OPEN modulus" |
| 2026-10-25 | core/ruled_divergences.py:69 | w0-derivation divergence retired | "(3.1) now reads the adopted b3, tracks agree" |
| 2026-11-01 | config/core_formulas.py:843; cat/action.py:58 | master-action-27d id -> master-action-26d; bulk sectors = none | "canonical since 2026-11-01; the id master-action-27d is retired" |

## 3. Ideas

Fork options: `today` is `fork:option`. Status in the report: A active, C considered, D disabled.

| id | idea | kind | first seen | last seen | fate | reason recorded | reason type | today |
|----|------|------|-----------|-----------|------|-----------------|-------------|-------|
| CC-01 | n_s = 1 - 2 phi^2/chi_eff (A) | cosmology | d9c2fb1 2026-10-25 | live | in-force | cat/cosmology.py:40 adopted | ruling | spectral_index_route:golden_modulated |
| CC-02 | n_s = 1 - 2/b3 (D) | cosmology | 0b984a37 | live | falsified | "11.48 sigma off; replaced 2026-01-10" cat/cosmology.py:51 | data (Planck n_s) | spectral_index_route:one_minus_2_over_b3 |
| CC-03 | Re(T) slow roll, n_s = 0.9996 (D) | cosmology | catalogue | live | falsified | "FALSIFIED at 8.3 sigma vs Planck 2018" cat/cosmology.py:63; cv:457 | data (Planck 2018) | spectral_index_route:re_t_slow_roll |
| CC-04 | H0 = 288/4 - 163/144 + eta_S (A) | cosmology | d9c2fb1 | live | in-force | "three fitted inputs" cat/cosmology.py:92 | ruling | h0_route:odowd_composite |
| CC-05 | H0 via G2 Ricci flow, 76.34 (D) | cosmology | ricci_flow_h0.py | live | falsified | "3.17 sigma from SH0ES (76.34) ... fitted angle" cat/cosmology.py:103; cv:268 | data (SH0ES) | h0_route:ricci_flow |
| CC-06 | KK-bridge early dark energy shifts H0 (D) | cosmology | hubble_tension.py | live | refuted-by-argument | "lightest KK mass ~5e28 eV vs ~1e-28 eV needed, ~57 orders off" cat/cosmology.py:115 | computed-number (hubble_tension.HubbleTensionEDE.run) | h0_route:kk_bridge |
| CC-07 | sterile extraction H0 = 70.42 | cosmology | cv:269 | cv:269 | superseded | "sterile extraction (2.5 sigma SH0ES, 6.0 Planck)" | data (SH0ES, Planck) | no option |
| CC-08 | w0 = -1 + 1/b3 thawing quintessence (A) | cosmology | d9c2fb1 | live | in-force | cat/cosmology.py:146 | ruling | dark_energy_mechanism:thawing_quintessence |
| CC-09 | w0 = -(D-1)/(D+1) = -11/13, max entropy production (D) | cosmology | 5755a1e0 | live | falsified | "w0 = -0.846, 1.76 sigma vs DESI 2025; replaced 2025-12-31" cat/cosmology.py:157 | data (DESI 2025) | dark_energy_mechanism:mep_11_13 |
| CC-10 | D_eff = 12.576 shadow-weighted, w0 = -0.853 | cosmology | v12.3 | shared_dimensions.py:112 | superseded | none | none | prose only (constant in file) |
| CC-11 | thermal-time alpha_T = 4.5 w0 = -0.8528 | time | cv:80 | cv:80 | retired | "retired pre-DESI candidate" | none | no option |
| CC-12 | Re(T) BBN-calibrated (A) | cosmology | 2bbe4a4 2026-09-14 | live | in-force | "Re(T) is an OPEN modulus" cat/cosmology.py:176 (D-015) | ruling | re_t_adoption:calibrated |
| CC-13 | Re(T) as solved vacuum of declared potential (D) | cosmology | 2bbe4a4 | live | retired | "DEMOTED 2026-10-01 (D-015)"; "eta_b match ... is destroyed" cat/cosmology.py:216-229 | computed-number (baryon_asymmetry._resolve_re_t) | re_t_adoption:computed_vacuum |
| CC-14 | b3 = 24, b2 = 4 seed as input (C) | topology-number | 8434d4a 2026-09-15 | live | superseded | "b_3 = 24 is an INPUT with no geometric home left" cat/seed.py:48 | ruling (2026-09-22) | b3_seed:seed_24 |
| CC-15 | (b3,b2) = (7,0) orbifold limit (D) | topology-number | 8434d4a | live | refuted-by-argument | "n_gen = b_2/4 = 0 ... a STRUCTURAL refutation" cat/seed.py:63 | argument | b3_seed:seed_7_joyce |
| CC-16 | (b3,b2) = (19,4) (D) | topology-number | 8434d4a | live | refuted-by-argument | "n_gen = b_2/4 = 1. One generation, refuted structurally." cat/seed.py:74 | argument | b3_seed:seed_19_joyce |
| CC-17 | (b3,b2) = (31,8) (D) | topology-number | 8434d4a | live | refuted-by-argument | "n_gen = b_2/4 = 2. Two generations, refuted structurally." cat/seed.py:85 | argument | b3_seed:seed_31_joyce |
| CC-18 | (b3,b2) = (43,12) derived (A) | topology-number | 8434d4a | live | in-force | "both derived from the A1 family count" cat/seed.py:95 | ruling | b3_seed:seed_43_joyce |
| CC-19 | n_gen = b3/8, 8 = dim O (C) | generations | 8434d4a | live | superseded | "incompatible with every Joyce-reachable value -- 7, 19, 31 and 43 are all odd" cat/seed.py:139; core/identity_ledger.py:225 "REFUTED ROUTE" | argument | n_gen_source:b3_over_dim_O |
| CC-20 | n_gen = b2/4, 4 = derived faces (A) | generations | 8434d4a | live | in-force | cat/seed.py:156 | ruling | n_gen_source:b2_over_faces |
| CC-21 | n_gen = chi_eff/24 per sector (D) | generations | 48ec267c 2025-11-22 | live | superseded | "kept as the sector-level formula in v20.1" cat/seed.py:187 | ruling | n_gen_source:chi_over_24 |
| CC-22 | n_gen = chi_eff_total/48 (C) | generations | 3ba5848 | live | unknown | "fails on the whole Joyce family on both chi_eff branches" cat/seed.py:200 | computed-number (catalogue 3ba5848) | n_gen_source:chi_eff_over_48 |
| CC-23 | n_gen = chi/24, F-theory D3 on CY4 | generations | config/core_formulas.py:179 | same | unknown | none (reference text only) | none | prose only |
| CC-24 | b3 derived: b2 = A1 count, b3 = 7 + 3 b2 (A) | topology-number | 2bbe4a4 2026-09-14 | live | in-force | cat/seed.py:249 | ruling | b3_origin:derived_joyce_a1 |
| CC-25 | b3 = 24 as stated input (C) | topology-number | 2bbe4a4 | live | unknown | "BUYS: honesty. The seed is registered INPUT" cat/seed.py:263 | argument | b3_origin:input_24 |
| CC-26 | 24 = Fano arc flag stabiliser, 12 flags x 2 (C) | topology-number | 2bbe4a4 | live | unknown | "a fully derived orbit-stabiliser identity" cat/seed.py:276 | argument | b3_origin:arc_flag_stabiliser |
| CC-27 | 24 = D4 root count, rank x Coxeter (C) | lattice | 2bbe4a4 | live | unknown | "the count is FORCED rather than matched" cat/seed.py:290 | argument | b3_origin:d4_root_shell |
| CC-28 | 24 = 7 flat + Joyce twisted sector (C) | internal | 2bbe4a4 | live | unknown | "the only candidate that would produce actual 3-cycles" cat/seed.py:307 | computed-number (half_shift_enumeration, 458,752 assignments) | b3_origin:joyce_twisted_sector |
| CC-29 | parity refutation of b3 = 24 over 14,336 shifts | topology-number | half_shift_enumeration.py:3 | same | withdrawn | "INCOMPLETE COVERAGE" (one of three reasons) PM/geometry/half_shift_enumeration.py:9 | computed-number (half_shift_enumeration) | no option |
| CC-30 | cited Joyce resolution contribution table (C) | internal | 2bbe4a4 | live | never-implemented | "no table supplied; Betti statements stay conditional" cat/g2_forms.py:43 | none | joyce_contribution_table:supplied |
| CC-31 | phi signs from the octonion product (A) | internal | 32f6948 2026-09-13 | live | in-force | cat/g2_forms.py:138 | ruling | g2_form_convention:octonion_derived |
| CC-32 | all (+1) on the seven Fano triples, split G2* (C) | internal | 32f6948 | live | superseded | "the split form G2*, kept switchable" cat/g2_forms.py:119 | ruling | g2_form_convention:all_plus_one |
| CC-33 | flavour consumes live b3 (A) / keeps 24 calibrated (C) | particle | f289f94 2026-09-23 | live | in-force / superseded | "the 24 must be ADMITTED to be a calibrated constant" cat/flavour.py:49 | argument | flavour_seed_coupling:follow_seed, :calibrated_24 |
| CC-34 | metric from phi by quadratic contraction (A) | internal | e0ccf89 2026-09-21 | live | in-force | "the status quo" cat/g2_metric.py:64 | none | metric_construction:quadratic_contraction |
| CC-35 | Hitchin cubic metric on the 3-form (C) | internal | e0ccf89 | live | unknown | "exhibits signature (4,3) on the adopted split branch" cat/g2_metric.py:79 | computed-number (g2_metric) | metric_construction:hitchin_cubic |
| CC-36 | chi_eff = 48 n from K3 involutions (A) | topology-number | ea482be 2026-09-22 | live | in-force | "(D-009)" cat/g2_metric.py:150 | ruling | chi_eff_route:k3_reading |
| CC-37 | chi_eff unruled (C) | topology-number | ea482be | live | superseded | "the honest state and it is what the code actually does" cat/g2_metric.py:169 | ruling | chi_eff_route:unruled |
| CC-38 | chi_eff = 144 constant (C) | topology-number | ea482be | live | superseded | "chi_eff carries NO topological content" cat/g2_metric.py:183 | argument | chi_eff_route:constant_144 |
| CC-39 | chi_eff = f(b3): b3^2/4 or 6 b3 (D) | topology-number | ea482be | live | refuted-by-argument | "n_gen = chi_eff/48 is then NON-INTEGER at every Joyce-reachable profile" cat/g2_metric.py:198 | argument | chi_eff_route:seed_dependent |
| CC-40 | twisted representative = orbit sum (A) / orbit average (C) | internal | 0bb4e38 2026-09-21 | live | in-force / unknown | "the representative is no longer the push-f[orward]" cat/g2_metric.py:273 | argument | twisted_norm_convention:orbit_sum, :orbit_average |
| CC-41 | Leech lattice Lambda_24 (A) | lattice | 6cb0d2c 2026-09-08 | live | in-force | "rootless, minimum norm 4, kissing 196560" cat/algebra.py:35 | none | lattice_24d:leech |
| CC-42 | Niemeier E8^3, three E8 blocks (C) | lattice | 6cb0d2c | live | unknown | "the block structure the model actually uses" cat/algebra.py:55 | argument | lattice_24d:niemeier_e8x3 |
| CC-43 | Joyce orbifold resolution (A) | internal | 6cb0d2c | live | in-force | cat/g2_forms.py:198 | ruling | g2_construction:joyce_orbifold |
| CC-44 | TCS of Fano pairs (C); TCS #187 h11 = 4 retired | internal | 6cb0d2c; constants.py:76 | live | retired | "Kovalev ... realizes 71 <= b3(M) <= 155" cat/g2_forms.py:217; cv:469 | argument (literature) | g2_construction:fano_tcs |
| CC-45 | four T_i = four b3 clusters of 6 (A) | identity | 6cb0d2c | live | in-force | "read as 3-cycles only on the retired seed_24" cat/g2_forms.py:263 | none | moduli_indexing:b3_clusters |
| CC-46 | four T_i = U(1) gauge kinetic functions (C) | gauge | 6cb0d2c | live | unknown | "T_i cannot enter W at all, so the four-face racetrack is abandoned" cat/g2_forms.py:295 | argument | moduli_indexing:b2_gauge |
| CC-47 | four T_i = CY3 Kahler moduli before S^1 to G2 (C) | internal | 6cb0d2c | live | unknown | "the four faces then belong to the 6D shadow" cat/g2_forms.py:313 | argument | moduli_indexing:cy3_shadow |
| CC-48 | G2 or CY3 x S^1/Z2 internal space | internal | config/constants.py:53 | same | unknown | none (comment only) | none | prose only |
| CC-49 | 26D (24,2), two times, one per shadow (A) | bulk | dca1fc1 2026-09-01 | live | in-force | "Shadows stay 13D(12,1)... nothing migrates" cat/g2_forms.py:336 | ruling (2026-08-31) | bulk_signature:24_2 |
| CC-50 | 28D (26,2), shadows 13+13+2 or two 14D(13,1) (C) | bulk | dca1fc1; cv:468 | live | superseded | "14 - 7 = 7 breaks the descent" cat/g2_forms.py:352-361 | argument | bulk_signature:26_2 |
| CC-51 | 26D (25,1), one time, bosonic string (C) | bulk | dca1fc1 | live | superseded | "Abandons two-time entirely" cat/g2_forms.py:365 | argument | bulk_signature:25_1 |
| CC-52 | 27D (24,1,2) sampler pair, shared time + (0,2) | bulk | cv:498 | 2026-08-19 | retired | "shadows summed to 25 != 27, spinor was non-chiral" cv:500-503 | argument | no option |
| CC-53 | 25D (24,1) labelled as bulk | bulk | cv:505 | cv:505 | retired | "(24,1) physics-core dimension mislabelled as a bulk" | argument | no option |
| CC-54 | (12,0) spatial shadows over a shared time fiber | shadows | bridge.py:133 (v22) | same | retired | "Kept on the books; nothing reads it." | none | prose only (RETIRED_SHADOW_SIGNATURE_SPATIAL) |
| CC-55 | 1 observable (5,1) + 3 shadow (3,1) branes, RS warp | shadows | constants.py:65-69 | live constants | unknown | none | none | prose only (N_SHADOW_BRANES = 3) |
| CC-56 | w0 = -(n-1)/n, n = 24 frozen (A) | cosmology | 26338ae 2026-09-06 | live | in-force | "a constant rather than a topological read" cat/cosmology.py:248 | ruling | dark_energy_betti:b3_24 |
| CC-57 | n = live b3 = 43, w0 = -42/43 (C) | cosmology | 26338ae | live | unknown | "from 0.017 sigma to 0.94 sigma" cat/cosmology.py:270 | data (DESI) | dark_energy_betti:b3_live |
| CC-58 | n = b2 = h11 = 4, w0 = -3/4 (C) | cosmology | 26338ae | live | refuted-by-argument | "RULED OUT 2026-09-06, on physics, despite being the BEST FIT" cat/cosmology.py:295 | ruling + argument | dark_energy_betti:b2_4 |
| CC-59 | n = 3 E8 blocks = generations (C) | cosmology | 26338ae | live | unknown | "thawing band ... CONTAINS the DR2 central wa" cat/cosmology.py:321 | data (DESI DR2) | dark_energy_betti:ngen_3 |
| CC-60 | n = chi_eff/b3 = 6 (C) | cosmology | 26338ae | live | unknown | "1.43 sigma on w0" cat/cosmology.py:332 | data (DESI) | dark_energy_betti:chi_over_b3_6 |
| CC-61 | n = 12 bridges (C) | cosmology | 26338ae | live | unknown | "no better than the adopted option in any respect" cat/cosmology.py:342 | data (DESI) | dark_energy_betti:bridges_12 |
| CC-62 | n = dim O = 8 (C) | cosmology | 26338ae | live | unknown | "recorded, not advocated" cat/cosmology.py:349 | data (DESI) | dark_energy_betti:octonion_8 |
| CC-63 | four face labels generic (A) / any 4-subset (C) | identity | f8e34f2 2026-08-31 | live | in-force / unknown | "all 35 candidates remain" cat/policy.py:143 | none | face_genericity:generic, :all |
| CC-64 | (12,43) selected by one bridge = one A1 (A) / by ruling only (C) | identity | a75aa13 2026-10-04 | live | in-force / unknown | "nothing in the geometry picks (12, 43)" cat/seed.py:363 | argument | seed_selection:wa1_correspondence, :ruling_only |
| CC-65 | bulk action sectors: none (A); E8xE8 YM, flux F4, KK tower, undecided (C) | action | 792a07f 2026-10-27 | live | in-force / unknown | "Adopted 2026-11-01" cat/action.py:58 | ruling | action_bulk_sectors:none, :e8xe8_ym, :flux_f4, :kk_tower, :undecided |
| CC-66 | Weyl 4096 (A) / Dirac 8192 (C) bulk spinor | action | 792a07f | live | in-force / unknown | "the 26 = 13 + 13 product rule then holds without a Weyl halving" cat/action.py:70 | argument | action_bulk_spinor:weyl, :dirac |
| CC-67 | Planck exponent D-2 = 24 (A) / 23, 25 (C) | action | 792a07f | live | in-force / refuted-by-argument | "the dimension check on the R term fails" cat/action.py:83-85 | argument | action_planck_exponent:exponent_24, :exponent_23, :exponent_25 |
| CC-68 | mostly-plus MTW (A) / mostly-minus (C) | action | 792a07f | live | in-force / unknown | "the weak-field sign check reports FAILS (found by E1)" cat/action.py:96 | computed-number (weak-field sign check) | action_sign_convention:mostly_plus_mtw, :mostly_minus |
| CC-69 | wa = x dim(Psi) = 4 projection | cosmology | cv:128 | cv:128 | superseded | "post-DESI graft -> kept as RETRODICTED variant" | data (DESI) | prose only (cosmology.wa_projection_x4) |
| CC-70 | wa from thermal alpha_T (+0.27) / attractor (+0.1) | cosmology | cv:130-131 | same | falsified | "wrong sign vs data" | data | no option |
| CC-71 | theta13: sin = lambda_C/sqrt(2), quark-lepton complementarity | particle | cv:378 | same | falsified | "FALSIFIED at 5.3 sigma" | data (NuFIT) | no option |
| CC-72 | theta13 = asin(1/6) zero-variable candidate | particle | cv:376 | neutrino_algebraic.py:596 | falsified | "FALSIFIED at 8.8 sigma (IO) / 9.3 sigma (NO)" | data (NuFIT 6.0) | prose only (neutrino_algebraic) |
| CC-73 | theta13 derived on adopted path | particle | neutrino_algebraic.py:38 | same | falsified | "R1 ruling 2026-08-25: about 39 sigma on the adopted path" | data (NuFIT 6.0) | no option |
| CC-74 | delta_CP = -2 pi chi_eff/b3^2 "inside 1 sigma" claim | particle | neutrino_algebraic.py:460 | same | withdrawn | "region' claim is withdrawn" | data (NuFIT 6.0) | no option |
| CC-75 | Cabibbo lambda = exp(-pi/2) zero-variable candidate | particle | cv:388 | gaugino_condensation.py:588 | falsified | "FALSIFIED at 25.5 sigma" | data (PDG) | prose only |
| CC-76 | Wolfenstein lambda from racetrack minimum; epsilon proxy | particle | gaugino_condensation.py:562, 657 | same | falsified | status="FALSIFIED" (no reason quoted in record) | none | prose only |
| CC-77 | sin2 theta_W geometric spectral 0.23190 | gauge | cv:408 | same | superseded | "geometric spectral candidate -> gauge.sin2_theta_w_geometric" | none | prose only |
| CC-78 | alpha^-1 geometric, match only at b3 = 24 | identity | core/ruled_divergences.py:77 | same | falsified | "the formula's match to its anchor existed only at b_3 = 24" ruled_divergences.py:50 | ruling | no option |
| CC-79 | Minkowski boost conservation check | other | clifford_unification.py:222 | same | falsified | status="FALSIFIED"; no ops exist in eml-math (clifford_unification.py:214-219) | none | prose only |
| CC-80 | "Global sigma alignment <= 0.48" | other | appendix_d_alignment.py:487 | same | withdrawn | "The quantity was never computed." | computed-number (statistical_rigor_report chi^2) | no option |
| CC-81 | fermion packing from 288 roots, 125 nodes over 3 generations | generations | a8dd95a^ shell_saturation.py:3-8 (v16.2) | deleted a8dd95a 2026-10-26 | retired | "Remove 26 unreferenced modules" (a8dd95a subject) | none | no option |
| CC-82 | "Demon Lock": 42-parameter stack moves as one unit | other | a8dd95a^ recursive_symmetry_gatekeeper.py:4-7 | deleted a8dd95a | retired | "Remove 26 unreferenced modules" | none | no option |
| CC-83 | 24-cycle in 3 x 8 cells = 3 generations (triality) | generations | a8dd95a^ octonionic_triality.py:10 | deleted a8dd95a | refuted-by-argument | "8 divides no reachable b3 (every b3 on Joyce's family is odd)" | argument | n_gen_source:b3_over_dim_O |
| CC-84 | w ~ -23/24 with Ricci-flow relaxation; H0 71.55 (v17.2) | cosmology | 4c14f1a^ cosmology_validation.py:5-7 | deleted 4c14f1a 2026-11-11 | retired | "nine dead modules removed" (4c14f1a subject) | none | h0_route:ricci_flow (related) |
| CC-85 | TCS "pure locked predictions" residue calculator, seed_24 | internal | 4c14f1a^ principia_residue_calculator.py:9 | deleted 4c14f1a | retired | "OFF-PATH (b3_seed = seed_24)" | ruling | b3_seed:seed_24 (related) |

Policy forks (`render_policy`, `theory_uncertainty_policy`) are publication policy, not ideas:
strict / cited_only active, permissive, always, experimental_only considered (cat/policy.py:29-86).
Other ledgers read: `cv` holds a `superseded` map per value (cv:79-548; rounding and binding
drift entries there are not ideas); `core/identity_ledger.py` reports HOLDS/BROKEN per branch and
keeps seed_24 runnable (identity_ledger.py:38-41); `core/ruled_divergences.py:49-77` labels
b3-consumer and chi_eff-coupled formulas.

Deleted simulation files (61, `git log --diff-filter=D`): 23 `.bak` codemod backups (eb3dfed),
4 test READMEs (8886470), the old `variants.py` split into the package (f34164b), 24 unreferenced
modules (a8dd95a: 14 visualisations, 7 validation/audit scripts, hebrew_naming, csv_loader,
shell_saturation) and 9 dead validation modules (4c14f1a). Only CC-81 to CC-85 carried a model
statement; the rest are tooling.

## 4. Owner's candidates

| # | candidate | status | reference |
|---|-----------|--------|-----------|
| 1 | three shadows | seen | config/constants.py:65-69 (N_BRANES = 4, N_SHADOW_BRANES = 3); shared_dimensions.py:120-123 (Y_SHADOW_1..3, RS warp); pneuma_mechanism.py:967 ("Third Shadow 3-Brane", prose now says 13D(12,1)). No fork option. |
| 2 | shadows in pairs / different dimension or make-up | seen | cv:468 (13 + 13 + 2 partition of (26,2)); cat/g2_forms.py:360-361 (two 14D(13,1) shadows); constants.py:67-68 ((5,1) observable vs (3,1) shadow branes); bridge.py:133 ((12,0) shadows) |
| 3 | two times, one bulk + one for shadows | seen (partial) | cv:500-501: 27D (24,1,2) "one shared time + (0,2) spacelike sampler dims" (one shared time, not a shadow time); bridge.py:133-135 shared time fiber. Exact split not seen. |
| 4 | three times | not seen | no "three times", (24,3) or (23,3) in src (search 2026-11-11) |
| 5 | 26D (24,2), two 13D (12,1) shadows | seen, in force | bulk_signature:24_2 cat/g2_forms.py:336; cv:466, 475 |
| 6 | 27D (24,1,2) and other bulks | seen | 27D retired cv:497-504; 28D (26,2) and 26D (25,1) options cat/g2_forms.py:352, 365; 25D (24,1) cv:505; 14D(13,1) shadows g2_forms.py:361; 11D sugra on G2 as a control actions/controls/g2_zero_modes.py:1. 13D/12D/10D only as shadow or string reference (D_string = 10 at config/parameters/cosmology.py:135). |
| 7 | other internal spaces | seen | TCS: g2_construction:fano_tcs, TCS #187 retired constants.py:76-80; Joyce T^7/(Z2)^3 in force; CY3 x S^1/Z2 constants.py:53; CY3 shadow moduli_indexing:cy3_shadow; CY4 F-theory core_formulas.py:179; Leech and Niemeier E8^3 lattice_24d; Fano/octonion: g2_form_convention, b3_origin:arc_flag_stabiliser; D4/Spin(7)/Spin(8) b3_origin:d4_root_shell; Spin(7) manifold as internal space not seen. |

## 5. Gaps

- `H:/Github/_retired/metaphysica-leftovers-2026-10-04`: not opened. Its contents are generated
  output (AutoGenerated 350 files, built Pages/foundations html, js, css, images, two JSON reports
  under src/AutoGenerated) plus three Windows cache .db files; the rules forbid opening generated
  output. Image names only: heterogeneous-brane-structure.svg, generation-count-consistency.svg.
- `H:/Github/_retired/PrincipiaMetaphysica-leftovers-2026-10-04`: only `.claude/settings.local.json`
  and `.github/workflows/validate.yml`; tooling, not opened.
- Deleted modules: only headers read (a8dd95a^, 4c14f1a^); bodies not read. The 14 visualisation
  and validation scripts were classed as tooling from their names and headers.
- Option `consequence` texts read to about 300 characters; `notes` of each fork read only for
  bulk_signature. `restored_from` commits (2c246586, 0b984a37, 5755a1e0, 48ec267c, 3ba5848) were
  not opened; they are cited as the catalogue records them.
- `first seen` for fork options is the fork's first commit in `core/variants`; earlier history
  of each idea belongs to the history lanes.
- `adopted.py`, `selection.py`, the testground switches and `falsification_oracle.py`
  (conditional FALSIFIED verdicts on fifth force, ALP) not read beyond the grep lines cited.
- The fork report warned that `src/metaphysica/simulations/AutoGenerated` exists as a real
  directory; the report itself was written to scratch and the tree is unchanged.
