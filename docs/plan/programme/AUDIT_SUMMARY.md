# Audit summary, 14 lanes (2026-11-11)

Source: docs/plan/programme/audit/*.md. Each lane ends in a Verification section. Id prefixes: GS sim-geometry-structure, PA sim-particle, VD sim-validation-data, WS website, PF paper-front, AA paper-app-a, AB paper-app-b, PB paper-back, CP core-paths, PL pipeline, AG sim-action-gauge, AM sim-algebra-misc, CO sim-cosmology, GC sim-geometry-closure. Suffix `~` = partly confirmed. Suffix `U` = never verified (UNVERIFIED). Active path: b3_seed = seed_43_joyce, (b2,b3) = (12,43), n_gen = 3, adopted action master-action-26d. "Retired seed" = seed_24 (b3 24, chi_eff 144, 288 roots, H0 71.55, k_gimel 12.318).

## 1. Totals

Confirmed, partly and refuted count every finding that has a Verification line, at any severity. Medium and low were not split in the tally. Unverified = medium and low (222 in all) plus 7 cosmology highs (CO-14, 15, 18, 25, 26, 27, 30).

| lane | critical | high | med+low | confirmed | partly | refuted |
|---|---|---|---|---|---|---|
| sim-geometry-structure | 7 | 18 | 18 | 19 | 6 | 0 |
| sim-particle | 7 | 13 | 11 | 12 | 8 | 0 |
| sim-validation-data | 5 | 16 | 17 | 13 | 8 | 0 |
| website | 6 | 11 | 13 | 15 | 2 | 0 |
| paper-front | 4 | 7 | 19 | 10 | 1 | 0 |
| paper-app-a | 3 | 20 | 17 | 17 | 6 | 0 |
| paper-app-b | 7 | 18 | 15 | 20 | 4 | 1 |
| paper-back | 12 | 23 | 16 | 28 | 6 | 1 |
| core-paths | 2 | 18 | 25 | 15 | 5 | 0 |
| pipeline | 4 | 16 | 20 | 17 | 3 | 0 |
| sim-action-gauge | 8 | 22 | 10 | 20 | 9 | 1 |
| sim-algebra-misc | 3 | 25 | 17 | 22 | 6 | 0 |
| sim-cosmology | 9 | 23 | 10 | 19 | 5 | 1 |
| sim-geometry-closure | 1 | 10 | 14 | 8 | 3 | 0 |
| total | 78 | 240 | 222 | 235 | 72 | 4 |

Confirmed critical 62, confirmed high 174 (before cross-lane de-duplication; section 2 merges them into clusters).

## 2. Confirmed and partly confirmed critical and high findings, de-duplicated

Rows merge defects found in several lanes. Refuted ids are listed at the end.

| ids | file:line | defect | fix |
|---|---|---|---|
| CP-05 CP-08 CP-11 CP-12 GC-06 GS-23~ AG-20 CO-09 CO-23 CO-14U CO-18U AM-16 AM-19~ PA-07 PA-08 AB-05 AB-06 AB-09 AB-22 AB-25 AA-22 PL-03 PL-04 PL-30 VD-08 VD-09 VD-10 VD-20 | core/canonical_values.py:40-41; FormulasRegistry.py:653; config/parameters/geometry.py:38-48; dynamical_lambda.py:195; inflation.py:157; gauge_unification.py:1755; generate_pdf_paper.py:282; appendix_r/u/s; GATES_CERTIFICATES G1,G22 | B3=24, CHI_EFF=144, B2=4, h11=24 typed as constants or defaults; geometry.elder_kads 24 sits beside topology.elder_kads 43; gates and beacons test 24/144; PDF cover and compression report print the retired seed | read b3, b2, chi_eff, n_gen through b3_path.seed_values(resolve_path()); delete literals; raise on a missing key |
| GC-01 GC-02 GC-03~ GC-05 GC-04 CP-11 VD-09 | g2_geometry.py:224,255,258,230,264-265 | chi_eff = 144 from off-path TCS h31 = 68 for any seed; K_MATCHING 4 beside b2 12; d_over_R 0.12 gluing literal; k_gimel and c_kaf calibrated at b3 24 and evaluated at 43 | chi_eff = 48 * n_gen; drop K and d/R or register as INPUT; one labelled calibration row |
| GS-01 GS-02 GS-06 GS-18 GS-20 GS-21 GS-22 GS-08 VD-01~ VD-02 | geometric_anchors_core.py:1021,1043-1045,626,283,1101,1061; alpha_rigor.py:744 | Measured values restated and then scored: M_Pl x sqrt(8 pi), mu_pe back-computed from CODATA, G_N x correction, T_CMB, G_F_matched, alpha_inv labelled "not a fitted value", tau_proton literal 1e36 | register INPUT or CALIBRATED, remove the comparison, one alpha_inv row |
| AG-01 AG-02 AG-03 AG-29~ PA-18 | electroweak_mixing.py:99,105-110,122,191; master_action.py:412 | g_2 = 2 M_W/v typed, then m_W = g_2 v/2 published DERIVED; v = 246.37 is the retired calibration (850.9 on b3 43); on-shell sin2 from the masses; three weak angles; v_EW names 174 and 246 | PDG v, M_W, sin2 as labelled INPUT; one scheme table |
| AG-04 AB-08 AB-09 AB-10 | thermal_time.py:291-294; appendix_u:104,150-170 | alpha_T = 2.6 is a target-first identity (26/10), DERIVED, match_sigma scored; b3 24 literal in U | ANSATZ or ledger row; read D_TOTAL from CANON |
| PA-05 PA-06 PA-04 PA-10 PA-11 PA-09~ PA-12 PA-13 | soft_susy_breaking.py:147; higgs_sector.py:137,196; higgs_vev_refined.py:353; higgs_brane_partition; higgs_mass.py; yukawa_derivation.py:238 | W_flux solved to hit m_3/2 = 1 TeV; m_h = 125.08 from tuned delta_rad = 87.5; v_geometric 850.9 GeV unscored; three m_h values; theta_13 4.835 deg (34 sigma) | CALIBRATED or CIRCULAR labels; score the failures; descriptions from values |
| PA-01 PA-20 | FormulasRegistry.py:2417-2431; qed/*.py | Nine qed rows: bulk = CODATA x (1+eps), manifest = bulk/(1+eps), a tautology scored as agreement; Compton value is CODATA 2018 labelled 2022 | remove from paper and score; delete with qed |
| CO-01 CO-03 CO-07 CO-08 CO-19 CO-20 CO-11 CO-21~ CO-02 | cosmological_constant.py:239-261,703; speed_of_light.py; evolution_engine.py; cosmological_tensions.py:158; multi_sector.py:478; attractor_potential.py:131; baryon_asymmetry.py:190 | Lambda from R_H = c/H0 with a typed "circularity removed" flag; c in m/s "derived" (402,385 sigma from invented 300 m/s); H0_early returns its input; H0/S8 "resolved" return the typed baseline; T'/T = 0.57 fitted; V_0 = observed rho_Lambda; eta_B tuned yet DERIVED; formula 5.26 carries exp(-2 pi 26) never computed | CIRCULAR or CALIBRATED or retire; formula text from code |
| CP-27 CO-04 CO-05 CO-06 CO-29 CO-20 AB-18 PB-09 PB-10 AM-32U GS-23~ AA-02 VD-12 | FormulasRegistry.py:1413; dark_energy_thawing.py:455; attractor_potential.py:996; discussion.py:766 | w0 = -23/24 frozen n=24 beside w0 = -42/43; w0_derived passes (0.02 sigma) against an unverified -0.957, fails 3.94 sigma against desi.w0; wa = -4/sqrt(b3) with an unexplained x4; wa quoted as +0.27, -0.75, ~0.1, -0.61, -0.204; paper says "DERIVED via MEP" | one thawing_w0() source; score against desi.w0 only; wa FITTED; delete the MEP claim |
| CP-01 CO-10 CO-12 GS-05 WS-02 PB-31 | baryon_asymmetry.py:157-177; inflation.py:151; re_t_sector.py:128-170; index.html:1255; results.py:474 | re_t_adoption=computed_vacuum silently falls back to 7.086; Re(T) is 7.086, 37.85 or 174.033 "GeV" and printed as "derived" | one dimensionless CALIBRATED Re(T); raise when no minimum |
| CP-04 GC-09 GC-10 CP-15 CP-16 CP-17 CP-26 CP-28 CP-29 CP-03 CP-02~ | g2_closure.py:465-480; g2_differential.py:344,517; variants/adopted.py:12-21,119 | catch-all fork readers return the active-path answer; nine drift guards are literals; 30 of 40 options give identical chi2; ranking has 40 inconsistent rows; critical_dim DERIVED though RETIRED; brane tension "SO(24,1)" | call resolve() directly; measuring readers; output_effect flag; WITHDRAWN status |
| CP-09 GS-09 CO-22 PF-07 PB-16 AG-15 WS-15 AM-05 AM-26 | geometric_anchors_core.py:399; cosmology_intro.py:243; methodology.py:117; integrity.py:106; master_action.py:1260 | 8192 Dirac spinor, "26,1" signature, one shared time, 27D bulk (24+1+2) | 4096 Weyl, (24,2), one time per shadow |
| AG-05 AG-25 CP-10 PA-12 PA-13 GS-04 GS-16 AM-17 | pneuma_mechanism.py:298; chirality.py:243,1168; four_face_structure.py:611; leech_partition.py | n_bridge_pairs = b3//2 = 21; generation_count = b3//8 = 5 PREDICTED; check computes 24.0/8.0; n_bridges 20; n_gen_leech DERIVED though withdrawn | n_gen = b2/4 from the fork; stop registering the b3//k rows |
| CP-30 PL-32 AM-13~ PB-05 PB-23 GS-10 VD-11 WS-04 PA-02 PA-03 PA-17 AM-20 PB-07 | beginners-guide.html:1498; predictions_aggregator.py:546,171; neutrino_sector.py:215; neutrino_mixing.py:821; complete_residue_registry.py:410 | Sums 0.0605, 0.0625, 0.0708, 0.0817, 0.1003, 0.102 coexist; ordering is NO in one module and the literal "INVERTED" in another; 76% "only unique prediction"; delta_CP 1.7 sigma printed as 0.02; theta13 text 9.59 vs value 12.89 | one sum row and one fork-read ordering; text from registry; sigma computed |
| PB-01 PB-02 PB-24 AG-07 AG-08 AG-26 VD-07 VD-08 AA-12 PL-12 PL-13 AM-27 | integrity.py:830-862,653-828; gauge_sector_complete.py:783; master_action.py:387,425; headline_stats.py:34; generate_72_certificates.py:38 | Gates return literal PASS (including open G72); mixing_validated True; alpha_s 0.117 and 3e-6 literals DERIVED; "36 of 42 locked" counts 9 never-executed gates; counts 72/71/42/36/41/43 | gate state from the gate registry; executed vs declarative reported separately |
| AA-01 PF-09~ PF-10 PF-12 PB-03 PB-04 WS-06 WS-07 PL-01 PL-02 VD-03~ | appendix_d_alignment.py:213; integrity.py:294; results.py:229; index.html; statistical_rigor_report.json | chi2 126,748.86 over 65 (retired seed) published as current; two scoreboards in one paragraph; "appropriate fit quality" beside POOR_FIT; 2.24e9 without cause | load_fit_summary(); delete Jacobian and peer_review blocks |
| CP-06 CP-07 AA-03 PB-14 CO-16 CO-17 WS-03 WS-10 | canonical_values.py:79; dependency_resolver.py:70; results.py:786; FormulasRegistry.py:4246; index.html:1308 | H0 71.55 (and 72.95, 76.29, 73.1) in text; live value 71.74, FITTED_COMPOSITE | prose from the computed value; delete cosmology.H0_odowd |
| AM-01 AM-02 AM-22 VD-04 WS-05 PB-34 | figure3_alp_discovery_window.py:60; alp_portals.py:437; falsification_oracle.py:104 | ALP point 3.51 meV, 1e-11 plotted; registry 111 eV, 1.2e-6; rows PREDICTED though the live seed fails the stellar bound; 6 ueV in section 6 | read the registry, CALIBRATED, score g_agg |
| PB-06 PB-08 PB-33 PB-35 AM-14 GS-19 AM-28 | predictions_aggregator.py:584,745,583; fig2 line 71 | tau_p 8.15e34, 3.9e34, 4.757e34; M_GUT 2.118e16, 2.1e16, 2e16, 6.3e15; M_KK 4.5 vs 5.0; 1% fallback sigma | one registry value each; skip rows with no uncertainty |
| PF-01 PF-02 PF-03 PF-04 PF-08 WS-14 AG-17 AG-18 AG-19 AG-16~ AG-09~ AG-30~ AM-23 AM-24~ AM-07 | methodology.py:496,557,227; lagrangian_master formulas; bridge-lagrangian-v22; unitary_filter_legacy | "manifestly ghost-free", compression and Metric Lock claims; live DERIVED/ANSATZ rows for E8xE8 YM, xi R phi^2, bridge, V_face that the adopted action excludes; gaugino rows DERIVED though off-path | SUPERSEDED or ANSATZ; delete passages |
| PA-14~ PA-15~ PA-16 PA-19 AG-12 AG-21 AG-22 AG-23~ AG-28~ AG-06 AG-24 | axion_photon_coupling.py; lhc_predictions.py; gauge_unification.py:1720,1771; matter_sector_complete.py:133; lagrangian_master.py:1554 | typed f_a, theta_QCD = 0, m_1/2 500 vs 21.9 GeV; ALPHA_GUT pulled 15% to b3 by a FITTED weight; catch-all entropy_rate; exp(-1.5) FN fit DERIVED; 189,800 vs 38,025 Riemann components; dof 324 | label INPUT/FITTED; fail early; correct text |
| CO-13~ CO-31~ CO-32~ CO-28~ GS-12 GS-13 GS-14 GS-15 GS-17 GS-24 GS-25 GC-07~ GC-08 GC-11~ | inflation.py:151; s8_suppression.py; hubble_tension.py; geometric_anchors.py:648 | r from the disabled slow-roll route; S8 scored vs Planck not lensing; REFUTED module still imported; "First Principles Derivation" title; D = 26 text; dead Leech block | label routes, retitle, delete block |
| AB-01 AB-02 AB-03 AB-04 AB-12 AB-13 AB-15 AB-16 AB-17 AB-19 AB-23 AB-24 AB-27 AB-30~ | appendix_r:255-329; appendix_t:263; appendix_o:515-575; appendix_s:498 | Vacuum "ABSOLUTELY STABLE" from typed numbers and a mechanism absent from the action; bounce 1e360; [[24,12,8]] has k = 0 as CSS; 27D chain and "consciousness channel" bridges; heat-kernel claims; `or 1.0` hides 0.0 | withdraw, state stability open |
| AA-04 AA-05 AA-06 AA-07~ AA-08 AA-09 AA-10 AA-11 AA-13 AA-14 AA-15 AA-16 AA-17 AA-18 AA-19~ AA-21~ AA-26 AA-29~ AG-27 | appendix_h/g/b/z/k/c; gauge_sector_complete.py:509 | 276+24-12 = 288, 240+48, 125/288 angle, gematria letters, "proof of isotropy", Omega Seal hard-codes, hierarchy "resolved", 125/144 hypercharge | archive; ledger row |
| PB-12 PB-13 PB-15 PB-17 PB-18 PB-19 PB-20 PB-21 PB-22 PB-25 PB-26 PB-27 PB-28 PB-29 PB-30~ PB-32 PF-05 PF-06 | results.py:692; discussion.py:575-789; physics_chain.py:48; predictions_aggregator.py:153-450,2337 | "0.48 sigma geometric coherence"; placeholder "ledger-derived compression ratio (not available in this build)" 7+ times; "All Major Issues Resolved"; D_crit start of chain; three copies of the prediction table; demo main() | one registry-built table; delete blocks |
| AM-04 AM-06 AM-07 AM-08 AM-09 AM-11 AM-12 AM-15 AM-18 AM-21~ AM-25 AM-03~ AM-10~ | freudenthal_triple.py:287; gaugino_condensation.py:681; orch_or_pair_shielding.py:250; complete_residue_registry.py:66; qec_golay_bridge.py:232; figure1:77 | b3=24 in appendix text while rows use 43; three shielding formulas; ESTABLISHED row validated against itself (sigma 0); `_pdg_v` swallows exceptions; boost check fails its test, falls back to 0.0; three alpha_leak values | read topology.elder_kads; one function per quantity |
| VD-05~ VD-13 VD-14~ VD-15 VD-16 VD-17 VD-18 VD-19~ VD-21 | nufit_6_0.json; statistical_rigor_validator.py:560,583; generate_statistics.py:270; falsification_oracle.py:3,333 | NuFIT "6.0" file looks 5.2-era; PM-generated "experimental" H0 70.2; deprecated chi2 5032 block; 5-prediction success rate 40%; "v24.1", "0.0 microns" | re-pull data with checksum; single fit block |
| PL-05 PL-06 PL-07 PL-08 PL-09 PL-10 PL-11 PL-16 PL-17 PL-18 PL-21 PL-26 PL-02 PL-13 | build.py:208,512; datasheets/constant.py:211; src/metaphysica/data/parameters.json; generate_pdf_paper.py:120,326; run_all_simulations.py:2287 | Wheel snapshot (620 rows) beats fresh build (821); PDF renders all 96 sections and ignores core_paper.json; PDF placeholders; six bare `except: pass`; reason null in build_status; parameter_ledger exit 1 on DIAGNOSTIC | build artifact first; PDF takes core manifest; fail the step on unresolved ids |
| WS-01 WS-08 WS-09 WS-11 WS-12 WS-13 WS-16 WS-17 WS-15 | index.html:1241-1325; pm-constants-loader.js:347,371,745; validation-stats.js; certificates.html:1208; falsification.html:99 | hand-typed sigmas and counts, loader default tables (H0 71.55, 288, 163), LEGACY_CERTIFICATES, hero "125 constants", empty path-ranking glow | bind every number to pm-value; no numeric defaults |
| CP-02~ CP-03 | AutoGenerated/path_ranking.json | rank 1 is a validator-policy flip (theory_uncertainty_policy=always, chi2 404,372); 30 of 40 rows share chi2 2,239,161,804.118 | publish "no consistent path", per-option output_effect |

Refuted, dropped: AG-10, CO-24, AB-14, PB-11. Findings 26-43 of GS, 22-38 of VD, 18-30 of WS, 13/14/18-25/31-45 of CP, 14/15/19/20/22-25/27-29/31/33-40 of PL, 29-45 of AM, 31-40 of AG and 21-31 of PA are UNVERIFIED (medium or low).

## 3. Paper

Only the four paper lanes judged sections; no simulation lane did. The lanes' section tables are reproduced; ids that share an action are grouped (words listed per id). Section ids repeat across lanes (6.1-6.9 in paper-back are the qed notes; A6/A7 in paper-app-b are the Clifford appendices); lane prefix disambiguates.

| id | title | words now | action | target | reason |
|---|---|---|---|---|---|
| 0 | Abstract | 209 | KEEP-CORE | 180 | correct; drop repeated scoreboard |
| extended-abstract | Extended abstract | 545 | ARCHIVE | 0 | repeats 0 and 1 |
| 1 | Introduction | 373 | KEEP-CORE | 350 | problem, idea, chain; one scoreboard |
| extended-introduction | Extended introduction | 5,302 | ARCHIVE | 0 | history, related work; Inputs-and-Status table moves to 7, related work 150 words into 1 |
| 1.1 | Foundations of Dimensional Descent | 2,988 | MERGE-INTO 2 | 600 | bulk postulate, E8/Leech split; cut numerology |
| 2.6 | Topologically Anchored Methodology (EDOF=3) | 2,408 | ARCHIVE | 0 | contradicts active path, failed MDL test; retired claims to ledger |
| A | 125-Residue Spectral Registry | 374 | MERGE-INTO scoreboard | 120 | |
| D | Statistical Convergence Logs (rename Fit ledger) | 487 | KEEP-CORE | 250 | fit numbers from artifact |
| F | Gates of Integrity | 314 | MERGE-INTO validation | 120 | one gate count |
| H | 288-Root Basis | 1,064 | LEDGER | 80 | numerology |
| K | Sterile Constant Table | 763 | MERGE-INTO A | 100 | registry table only |
| Z | Terminal Constant Ledger | 204 | MERGE-INTO D | 40 | "zero free parameters" false |
| B C E G I J L (app-a) | S_PR(2) 424, Gauge Reduction 402, Brane Map 277, 42-Certificate/Omega Seal 713, Terminal States 726, Torsion Funnel 469, Omega Unwinding 458 | 3,469 | ARCHIVE | 0 | nothing downstream uses them |
| M N | Tensor Calculus 1,371; Vielbein 1,029 | 2,400 | ARCHIVE | 0 | textbook; cite Carroll, Wald, Nakahara |
| O | Kaluza-Klein Reduction | 1,436 | KEEP-CORE | 300 | 26 = 13+13, 13 = 4+2+7 |
| P | G2 Holonomy | 1,428 | KEEP-CORE | 350 | Joyce Y7, (12,43), finite pi_1 |
| Q | Index Theorem | 1,474 | MERGE-INTO P | 120 | n_gen = b2/4, chirality open |
| R.1 | Vacuum Stability | 1,021 | LEDGER | 60 | typed numbers; stability open |
| S.1 appendix-T A7 | Spectral Residue 1,193; QEC Bridge 320; Clifford appendix 355 | 1,868 | ARCHIVE | 0 | unsupported; Weyl-4096 sentence to action section |
| appendix-U | Gamma correction | 235 | LEDGER | 40 | identity as derivation |
| A6 | Clifford (algebra module) | 257 | CUT | 0 | duplicate of A7 |
| 3.7 | Cosmological Results and Alignment | 2,976 | MERGE-INTO 5.2, retired blocks to LEDGER | 300 | |
| 4 | System Integrity and Verification | 1,809 | ARCHIVE (3 lines into 1) | 120 | hard-coded PASS |
| 6 | Falsifiable Predictions via SME | 5,000 | KEEP-CORE, one falsifiability table | 1,200 | table: ordering, sum m_nu 0.0605, tau_p 4.757e34, KK 5.0 TeV, ALP 3.51 meV, w0/wa, N_eff, GW/CHSH below reach |
| 7 | Discussion, Conclusions | 4,395 | KEEP-CORE, trim | 1,300 | |
| 7.1 7.2 7.3 7.4 7.6 7.7 7.8 | Axion DM 558, Orch-OR 774, DM Portal 531, Sterile Portals 344, Pair Shielding 210, Gnosis 76, 4-Dice 89 | 2,582 | ARCHIVE | 0 | speculation, no test |
| 7.5 | ALP Portal | 575 | MERGE-INTO 6 | 0 | |
| 6.1-6.8 (PB) | Compton 133, Stefan-Boltzmann 135, Hartree 198, Magnetic Flux 153, von Klitzing 169, Avogadro 240, Faraday 219, Molar Gas 101 | 1,348 | ARCHIVE | 0 | qed tautologies (PA-01) |
| 6.9 | Weak Mixing | 137 | MERGE-INTO 3 | 0 | |
| 6.1.1 | Yukawa Textures | 231 | MERGE-INTO 4.2 | 0 | |
| 6.2.1 | Baryon Asymmetry + Jarlskog | 561 | ARCHIVE | 0 | |
| 4.5 | Neutrino Mixing | 1,165 | MERGE-INTO 4.3 | 150 | |
| 4.6 | Proton Decay | 1,295 | MERGE-INTO 6 | 0 | |
| 4.7 4.8 4.9 4.2.1 | CKM/PMNS 500, Mass Ratios 176, Higgs from 4-Brane 270, Geometric Higgs VEV 228 | 1,174 | ARCHIVE | 0 | |
| LEDGER (PB) | retired-claims ledger | n/a | new | 250 | |

Totals (sum of listed rows): words now 51,867 (paper-front 11,825; paper-app-a 6,675; paper-app-b 10,119; paper-back 23,248). Words proposed 6,030 (1,130; 710; 870; 3,320). Rows judged 59; rows with target above 0: 19 (0, 1, 1.1, A, D, F, H, K, Z, O, P, Q, R.1, U, 3.7, 4, 6, 7, 4.5, plus the PB ledger). paper-app-b states about 11,100 words now; its rows sum to 10,119, so about 980 words are in rows the lane did not list. paper-back states about 23,200 and 3,300.

Consolidated repeated statements (state once):

| statement | section ids | lives once in |
|---|---|---|
| Bulk postulate 26D (24,2) = two (12,1) shadows, 13 = 4+2+7 | 0, 1, extended-abstract, extended-introduction, 1.1, 2, O | 2 |
| Y7 Joyce, (b2,b3) = (12,43), n_gen = b2/4 = 3, chi_eff = 48n | 0, 1, extended-*, 1.1, 4.2, P, Q, S.1, R.1 | 2.4 / P |
| Joyce Thm 11.6.1, 10 of 10 hypotheses | 0, 1, extended-*, 2.4 | 2.4 |
| Scoreboard 22/26 and chi2 2.24e9 over 63 (alpha_inv dominates) | 0, 1 (twice), extended-abstract, 7, D | 7 via load_fit_summary |
| Path comparison seed_24 vs seed_43 (36 vs 23 pass) | 1, 2.6, extended-introduction, R.1, T | ledger table |
| Retired claims: D_crit 26, ghost-freedom, w0 = -1+1/b3, racetrack Re(T), b3 = 24, n_gen = b3/8, compression 116:1, Metric Lock | extended-introduction, 1.1, 2.6, P, Q, R.1, S.1, T, U | one ledger table |
| Ghost control open; dark energy open (gradV/V >= 2.673); racetrack impossible | 0, 1, 1.1, 2.6, 5.2, 4.4 | 4.1 / 5.2 / 4.4 |
| EDOF=3 and 125 residues | 2.6 (about 20 times), 1.1, A, S.1 | 7 free-variable ledger |
| Pneuma / chirality proposal; Re(T) calibration of an open modulus | extended-introduction, 1.1, 4.1, 4.4 | 4.1, 4.4 |
| Neutrino ordering and sum; tau_p; M_GUT; M_KK; ALP; wa | 3.7, 4.5, 6, 6.2c, 7, 7.5 | 6 falsifiability table |
| SM gauge structure from geometry; 12 bridge pairs as consciousness channels | O.7, O.9, O.11, P | cut; gauge section |
| Hebrew-letter naming, 125/288/24 ratios | A, B, G, H, I, J, K, Z | cut |
| 42-gate / 72-gate counts, hard-coded PASS | F, G, 4, integrity | 4 lines in 1 |

## 4. Simulation modules

Counts are module rows from each lane's Table A (a row can be a group of modules).

| lane | KEEP | FIX | MERGE | RETIRE-FROM-PAPER | DELETE |
|---|---|---|---|---|---|
| sim-geometry-structure | 14 | 7 | 0 (recommends 1) | 6 | 0 |
| sim-particle | 2 | 14 | 0 | 11 | 1 |
| sim-validation-data | 1 | 10 | 1 | 1 | 10 |
| sim-action-gauge | 2 | 10 | 1 | 2 | 0 |
| sim-algebra-misc | 3 | 13 | 0 | 8 | 2 |
| sim-cosmology | 5 | 14 | 1 | 7 | 1 |
| sim-geometry-closure | 7 | 5 | 0 | 2 | 1 (2 modules) |
| core-paths | about 9 | about 14 | 0 | 1 | 0 |
| pipeline | about 8 | about 15 | 1 | 6 | 1 |
| website (pages and scripts) | rest | 7 | 5 | 5 | 4 groups |

RETIRE-FROM-PAPER (keep module and rows, remove from the paper and score):
- GS: flux_homogeneity, instanton_cycles, leech_equivariance, leech_partition, modular_invariance, sphere_packing (retired b3 identification, no test).
- PA: nine qed modules (avogadro, faraday, molar_gas, von_klitzing, magnetic_flux, stefan_boltzmann, compton_wavelength, hartree_energy, weak_mixing: tautologies); higgs_brane_partition (70.57 GeV vs 125); mass_ratio (computed at b3 24).
- VD: information_bottleneck_distiller.
- AG: su3_qcd_gauge, su2_weak_gauge, u1_hypercharge, non_abelian_kk_gauge, kk_reduction_gr_gauge (textbook forms, flags asserted); orch_or_geometry, sampler_entropy_dynamics (numerology); gauge_sector_complete.y_ratio.
- AM: leech_lattice (24/8 = 3 withdrawn), qec_golay_bridge (needs b3 24), e8x8_splitting and gaugino_condensation (falsified, off-path), orch_or_pair_shielding, gnosis_unlocking, four_dice_sampling (no data), figures goldilocks_plot, stability_heatmap, theory_overview_diagrams, ricci_flow_evolution (retired seed).
- CO: attractor_potential (V_0 = observed rho), vacuum_selection (0.92 chosen), speed_of_light (c exact), hubble_tension (self-declared REFUTED, still imported by late_time_routes._kk_bridge_h0), bridge_axion_ede, cosmological_tensions, axion_dm (provisional).
- GC: orbifold_gauge_scan, flat_form_involution_map.
- CP: demon_lock_guard. PL: generate_compression_report and the scorecard, index, named-constants, plots-manifest, terminology generators.
- WS: foundations (keep clifford, so10-gut, yang-mills), philosophical-implications, consciousness-speculative, visualization-index, mismatches.

MERGE:
- GS: geometric_anchors into geometric_anchors_core (or the reverse), one file.
- VD: unitary_filter_legacy into unitary_filter.
- AG: gauge_sector_complete into gauge/master_action.
- AM: complete_residue_registry neutrino sum into one row.
- CO: baryogenesis into baryon_asymmetry.
- PL: generate_statistics into headline_stats.
- WS: sections.html and appendices.html into paper.html; simulations.html into parameters.html; faq into beginners-guide; theory-diagrams into geometry-to-physics.

DELETE (confirm run_all_simulations.py does not glob the folder first):
- PA: qed/_triple_track (with qed).
- VD: geometric_pipeline; rigor_covariance, cosmology_validation, principia_residue_calculator, final_verification_script, tolerance_sweep (dead); four one-off migration scripts.
- AM: Constants/ad-hoc (5 files, hard-coded H:\Github path); extract_supplementary and section_schema if no importer.
- CO: mirror_dm_detection (no importer).
- GC: conical_point_search, holonomy_wording_audit (tests only; move to tests).
- PL: generate-latex-paper.js.
- WS: geometric-framework redirect, validation-stats.js, legacy theory-constants*.js, 19 unreferenced js/css files. Nav 18 header links to 10.

FIX modules named in several lanes: size standard (24 of 28 cosmology files, master_action 2,499, lagrangian_master 4,204, g2_geometry 3,253, run_all_simulations 3,943 lines) is split compute / formulas / section / gates.

## 5. Path system

Fork evaluability (core-paths 3a, 26 forks; forks with at least one declared-only option). R = runnable on scored output.

| fork | declared-only options | note |
|---|---|---|
| re_t_adoption | computed_vacuum | silent fallback to 7.086 (CP-01) |
| n_gen_source | chi_over_24, chi_eff_over_48 | |
| b3_origin | input_24, arc_flag_stabiliser, d4_root_shell, joyce_twisted_sector | |
| joyce_contribution_table | supplied | no table |
| g2_form_convention | all_plus_one | no chi2 effect |
| metric_construction | hitchin_cubic | adopted reader falls back to quadratic_contraction (CP-15) |
| chi_eff_route | unruled, constant_144, seed_dependent | |
| twisted_norm_convention | orbit_average | |
| lattice_24d | niemeier_e8x3 | |
| g2_construction | fano_tcs | refused and swallowed |
| moduli_indexing | b2_gauge, cy3_shadow | |
| bulk_signature | 26_2, 25_1 | |
| dark_energy_betti | b2_4, ngen_3 | b3_24 option is frozen n=24 |
| face_genericity | all | |
| seed_selection | ruling_only | |
| action_bulk_sectors | undecided, e8xe8_ym, flux_f4, kk_tower | all four action forks OPEN (CP-17) |
| action_bulk_spinor | dirac | |
| h0_route | ricci_flow, kk_bridge | not in sweep |
| b3_seed | seed_24, 7, 19, 31 | not in ranking rows |
| render_policy, theory_uncertainty_policy | n/a | build and validation options, not geometry forks |

Fully runnable on scored output: spectral_index_route, dark_energy_mechanism, flavour_seed_coupling, dark_energy_betti, h0_route (R). 3 partial, 14 or more declared-only. Ranking: 40 rows, all inconsistent; 30 share chi2 2,239,161,804.118; rank 1 is a validator-policy flip (CP-02, CP-03).

Geometric choices that are not forks (core-paths 3b): seed_24 hard-coded; retired TCS #187 literals (h11 4, h31 68); Dirac versus Weyl spinor; shadow signature (12,0) versus (12,1); 6D-to-4D residual integers (a 2D space PM does not declare, AG-13); O'Dowd H0 inputs; Re(T) 7.086; frozen n = 24 for w0; the Z2^3 group.

Path-dependent literals reaching published output (all lanes, de-duplicated):

| literal | where | should read |
|---|---|---|
| B3 24, CHI_EFF 144, B2 4 | canonical_values.py:40-41; FormulasRegistry.py:653 (elder_kads 24); dependency_resolver.py:909 | seed_values(resolve_path()) |
| TCS h11 4, h31 68, K 4, d/R 0.12 | g2_geometry.py:222-260; config/parameters/geometry.py:38-48 | chi_eff = 48 n_gen |
| H0 71.55 = 288/4 - 163/144 + 0.6819; `24*3 - 0.45` | canonical_values.py:79; dependency_resolver.py:70; FormulasRegistry.py:4246 | computed 71.74 |
| w0 -23/24, wa -1/sqrt(24) | FormulasRegistry.py:1413; attractor_potential.py:996; moduli_dm_coupling.py:1327; ricci_flow_evolution.py:136; dark_energy_thawing.py:1404-1900 | thawing_w0() |
| Re(T) 7.086, 37.85, 174.033 | baryon_asymmetry.py:149; inflation.py:154; re_t_sector.py | one CALIBRATED row |
| v 246.37; alpha_s 0.117; sin2 0.22320; k_gimel 12 + 1/pi | electroweak_mixing.py:99-110; master_action.py:387,412 | PDG INPUT |
| h11 24, alpha_T 2.600, entropy_rate -0.0825 | gauge_unification.py:1189,1720,1755 | registry |
| D_TOTAL 26, D_STRING 10, vielbein_rank 26 | thermal_time.py:291; lagrangian_master.py:1414 | CANON |
| 288 = 2 chi_eff; 125/144 | lagrangian_master.py:179; gauge_sector_complete.py:509 | retire |
| int(b3/8), b3//2 | chirality.py:243; pneuma_mechanism.py:298; four_face_structure.py:611 | n_gen = b2/4 |
| b3 24 in section text | freudenthal_triple.py:287; e7_representation.py:331; e8x8_splitting.py:305; gaugino_condensation.py:681; neutrino_algebraic.py:82; complete_residue_registry.py:12; appendix_r/s/u/t | topology.elder_kads |
| 8192, "26,1", "SO(24,1)", 27D | geometric_anchors_core.py:399; cosmology_intro.py:243; methodology.py:117; integrity.py:106 | 4096, (24,2) |
| 3.51 meV, 1e-11; M_GUT 2e16 / 2.12e16; tau_p 3.9e34; 5.0 and 4.5 TeV | figure3:60; complete_residue_registry.py:425; predictions_aggregator.py | registry rows |
| 42/42, 72 gates, 126,748.86/65 | certificate_dashboard.py:280; appendix_f; appendix_d:213; integrity.py:294 | validation artifact |
| 71.55, 288, 163, 30/32/48/58 | pm-constants-loader.js:347-376; index.html:1241-1325; certificates.html:1208 | pm-value bindings |

## 6. Validation

Duplicate rows (VD-01): 9 extra rows in 8 groups, alpha_inv {electromagnetic.alpha_inv, geometry.alpha_inverse}; mu_pe {fermion.mass_ratio_proton_electron, geometry.mu_pe}; w0 {cosmology.w0_thawing, w0_tzimtzum}; w0 {cosmology.w0_derived, geometry.w_zero}; Cabibbo x3 {ckm.V_us, ckm.lambda_wolfenstein, yukawa.epsilon_fn}; PMNS {neutrino.theta_nn_pred, pmns.theta_nn_triality} (3 groups). Statuses: 8 CIRCULAR rows, 2 IDENTITY rows.

Unit check: cosmology.speed_of_light_derived 179,077,057 vs 299,792,458 m/s, sigma 402,384 (c is exact; row to retire, CO-03). Further unit and label errors: entropy_density (CO-26U), Re(T) in GeV (CO-12), geometry.* rows without units (GS-11), e7_alp_mass_gev (AM-22).

chi2: published 2,239,162,102.6 over 63 rows (alpha_inv about 99.99%). After removing duplicates: 1,119,785,455 over 54 rows. Without alpha_inv and the falsified rows: 12,649 over 48 rows. Facts figure 126,749/65 belongs to the retired seed. Fit status POOR_FIT; EDOF = 3 ansatz; 22 PASS / 26 FAIL on the published count; 14 PASS after dedupe; median |sigma| 2.14. Falsified rows contribute about 3.97e5.

Top contributors (chi2): alpha_inv 1.119e9; gaugino_cabibbo_proxy 3.93e5; hypercharge gp 6,547; G_F_matched 3,261; neutrino.theta13_derived 1,500; particle.theta_13_deg 1,159; gaugino_cabibbo_derived 862; gaugino_cabibbo_refined 653; T_CMB 345; eta_baryon 330; sin2_theta_w_geometric 293; sin_theta13_derived 213; V_ub_triality 195; mass_ratio_proton_electron 162; jarlskog_triality 89.8.

Gates: 71 total, 29 axiom, 42 testable, 36 "locked" = 27 executed pass + 9 declarative, 6 open (G12, G19, G22, G27, G50, G72); 71 total, 27 COMPUTED_PASS, 6 COMPUTED_FAIL. The Facts 41/43 and other counts (72, 42/42) are stale. theory_uncertainty_policy is cited_only; setting it to always changes rank 1 (chi2 404,372).

Stale or doubtful experimental values (VD-05, 13, 21; CO-05, 17): NuFIT "6.0" file looks 5.2-era (arXiv 2111.03086, checksum pending); asymmetric errors averaged or one side used; G_N and M_Pl uncertainties differ between PDG and CODATA files; H0_odowd scored against a PM_geometric "experimental" 70.2; T_CMB source label; w0 -0.957 tagged "DESI2025_thawing" (attribution unverified; desi.w0 is -0.752 +/- 0.057); KiDS S8 0.766(20) vs recalled 0.759 (check); Compton value is 2018 labelled 2022; S8 scored against Planck rather than lensing.

Falsified-row sigmas differ between Facts (344.7/37.6/25.6) and validation_report (627.0/29.4/25.6) (AM-08).

## 7. Proposed fix lanes (ten, disjoint files, in dependency order)

| # | name | files owned | finding ids | acceptance test |
|---|---|---|---|---|
| 1 | path-core | simulations/core/{canonical_values,FormulasRegistry,dependency_resolver,variants/*}.py, config/parameters/*, switch_search, testground, path_ranking generator | CP-01..12, 15-17, 26-29, CO-04 (alias), GS-23, GC-06 | grep finds no 24/144/4 literal in core; resolve() raises on unknown fork; ranking has an output_effect flag per option; test that switching b3_seed changes canonical values |
| 2 | geometry | PM/geometry/* (g2_geometry, g2_closure, g2_differential, geometric_anchors*, four_face_structure, re_t_sector, alpha_rigor, bridge_geometry, joyce_contributions, flat_form, conical_point_search, holonomy_wording_audit, closed_geometry/*) | GS-*, GC-*, CP-04 | chi_eff = 48 n_gen at seeds 24 and 43; no catch-all in g2_closure; topology.critical_dim WITHDRAWN; spinor 4096; one alpha_inv row |
| 3 | cosmology | PM/cosmology/* | CO-*, CP-06/07 (prose), VD-12 | one w0 source; Lambda_derived CIRCULAR; speed_of_light rows gone; H0 text equals computed value; Re(T) one row |
| 4 | gauge-action | PM/gauge/*, PM/derivations/*, PM/field_dynamics/*, PM/actions/*, theories/* | AG-*, PA-18 | m_W, m_Z, alpha_s INPUT; ladder drops xi R phi^2; no b3//k count rows; gauge_sector_complete merged |
| 5 | particle-susy-qed | PM/particle/*, PM/susy/*, PM/qed/*, core qed formulas | PA-*, CP-10 | qed removed from score; m_h CIRCULAR; one neutrino ordering and sum; theta_13 text equals value |
| 6 | algebra-portals-viz | PM/algebra/*, PM/portals/*, PM/consciousness/*, PM/support/complete_residue_registry.py, visualizations/*, Constants/* | AM-* | figure3 reads registry; no b3 = 24 in section text; fallbacks removed; ad-hoc deleted |
| 7 | validation-data | statistical_rigor_validator, falsification_oracle, headline_stats, experimental_data_loader, unitary_filter*, certificates and consistency_beacons, data/experimental/*, dead scripts | VD-*, PL-01, PL-02, PL-11 | dedup by observable (54 rows); chi2 text from computed fields; gates split executed/declarative; NuFIT checksum |
| 8 | paper-prose | PM/paper/* (methodology, foundations, core_text, results, discussion, integrity, predictions_aggregator, conclusions, physics_chain), appendix modules, core_manifest | PF-*, AA-*, AB-*, PB-* | 59 rows actioned; core sections 6,030 words or fewer; no retired-seed literal; Section 6 is one registry-built table |
| 9 | pipeline | build.py, generators/*, datasheets/*, run_all_simulations.py, src/metaphysica/data/parameters.json, generate-latex-paper.js | PL-*, CP-05 (build side) | fresh build beats snapshot; PDF renders core manifest; unresolved ids fail the step; no bare `except: pass`; parameter_ledger exit 0 |
| 10 | website | website/index.html, Pages/*, js/*, css/* | WS-* | every number is a pm-value binding; no numeric loader defaults; nav 10 links; 19 unreferenced files removed |

Lane 9 rebuilds after 1-8; lane 10 runs on the rebuilt artifacts. Lane 8 depends on registry values from lanes 2-7.
