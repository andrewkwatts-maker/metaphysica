# L1 path-core progress

Round 1 (2026-11-11). Test file: tests/programme/test_path_core_topology.py (T).
tests/test_canonical_values.py was edited: its subject canonical_values.py is
owned by this lane and it asserted the defect (B3 == 24, w0 DERIVED, H0 typed).

Round 2 (2026-11-11). R = tests/programme/test_path_core_fork_readers.py,
K = tests/programme/test_path_core_ranking.py,
C = tests/programme/test_path_core_config_literals.py.
tests/test_variants.py edited: it pinned the unmeasurable set to
{dark_energy_betti}, so it asserted the literal readers of core-paths-16.
resolve() already raised on an unknown fork (KeyError) and unknown option
(ValueError) before round 2; R does not repeat that.

Round 3 (2026-11-11). S = tests/programme/test_path_core_registry_status.py.

| id | file:line | state | commit | test |
|---|---|---|---|---|
| core-paths-05 | core/canonical_values.py (B3/B2/CHI_EFF) | fixed | 12db48f | T::test_topology_and_canonical_names_agree_with_seed_values |
| core-paths-06 | core/canonical_values.py (CANON w0/wa/alpha_leak) | fixed | 12db48f | T::test_frozen_w0_is_an_input_not_a_prediction |
| core-paths-27 | core/canonical_values.py (H0 typed) | fixed | 12db48f | T::test_canon_h0_is_read_from_the_artifact |
| pipeline-30 | generators/generate_canonical_values.py | fixed (main not run) | 12db48f | tests/test_canonical_values.py |
| sim-geometry-closure-06 | core/FormulasRegistry.py:653, dependency_resolver.py:909 | fixed | 12db48f | T::test_hebrew_symbol_values_follow_the_path |
| core-paths-12 | core/FormulasRegistry.py eta_S text | fixed (status FITTED) | 12db48f | T::test_registry_text_has_no_retired_seed_numbers |
| sim-cosmology-04 | core/FormulasRegistry.py tzimtzum 23/24 | fixed (fork reader) | 12db48f | T::test_registry_tzimtzum_follows_the_dark_energy_fork |
| sim-cosmology-16 | core/FormulasRegistry.py calculate_h0_local text | fixed | 12db48f | T::test_registry_text_has_no_retired_seed_numbers |
| sim-particle-20 | core/FormulasRegistry.py CODATA_COMPTON | fixed (2022 value) | 12db48f | T::test_registry_text_has_no_retired_seed_numbers |
| core-paths-07 | core/dependency_resolver.py H0_base | fixed | 12db48f | T::test_dependency_resolver_seeds_and_h0_follow_the_path |
| core-paths-11 | config/parameters/geometry.py:38-48, fitted.py | fixed (PathValued; TCS187 rows retired) | 77af308 | T::test_config_chirality_reads_the_path |
| core-paths-15 | core/variants/adopted.py:119-143 | fixed (raises SourceUnmeasurable with fork, option, reason) | 3f067f8 | R::test_metric_reader_raises_when_no_option_matches |
| core-paths-16 | core/variants/adopted.py:12-21, 51-67 | fixed for re_t_adoption, b3_seed (declared only, raise); the four action readers stay for L4 | 3f067f8 | R::test_self_referential_readers_are_declared_not_measured |
| core-paths-03 | testground/rank.py, new testground/rank_effects.py | fixed (option_effects: scored, unscored, none (baseline: the adopted option), not_evaluable) | 279c246 | K::test_every_option_of_every_fork_has_a_measured_effect |
| core-paths-02 | testground/rank.py; catalogue/policy.py | fixed in part: verdict "no consistent path", policy forks (kind policy) unranked, ties share a rank; joint geometry sweep is core-paths-42 | 279c246 | K::test_policy_forks_do_not_rank_even_when_they_fit_best |
| core-paths-03 (follow-up) | testground/rank_effects.py:24-89 | fixed: RANKED_KIND/unranked_reason renamed PATH_KIND/off_path_reason (D-019 confinement test failed on 279c246) | 5634c97 | tests/testground/test_ranking_is_confined.py |
| core-paths-11 (remainder) | config/parameters/geometry.py EFTValidity, G2SpinorGeometry, TCSTopology; moduli.py Pneuma, Mashiach, QuantumFR; fermion.py TopologicalCPPhase; proton_decay.py DoubletTriplet; fitted.py AnomalyCancellation, TorsionClass.N_FLUX | fixed: PathValued + N_FLUX + class `_PATH_DERIVED` (A/B_COEFF, VEV_PNEUMA, DELTA_CP, MAXIMAL_CP, GS_COUNTERTERM); TCS #187 values kept as RETIRED_TCS187_* | 5634c97 | C::test_config_class_follows_the_path_in_force |
| sim-geometry-structure-05 | base/registry.py:789 (re_t_sector rows) | fixed: geometry.ReT and VEV_gap_percent registered CALIBRATED with status_reason (ENTRY_POINT_KEY_STATUSES); re_t_sector.py itself is L2 | (this commit) | S::test_re_t_rows_are_calibrated_not_derived |
| sim-particle-27 | base/registry.py:740, 864, 1002 | fixed (registry part): one `_register_entry_point`; import/run error, non-dict return and unknown override raise; no {"error"} skip | (this commit) | S::test_entry_point_failure_raises_instead_of_skipping |
| sim-particle-01 | core/FormulasRegistry.py:2417-2431 | fixed in part: QED_ROUNDTRIP_IDENTITIES names the ten manifest identities, "Physical Meaning" text replaced by IDENTITY; score already excludes them (validation_report verdict INPUT/IDENTITY for all nine); Parameter status DERIVED in PM/qed/*.py is L5 | (this commit) | S::test_qed_manifest_rows_are_declared_identities |
| core-paths-13 | core/FormulasRegistry.py:1145-1149, 1477-1478, 1874-1875 | fixed: literal 43, 144 and n_gen 3 fallbacks removed; no import cycle (eight import orders checked) | (this commit) | S::test_registry_has_no_literal_seed_fallbacks |
| core-paths-26 | core/variants/catalogue/g2_forms.py:264, 294 | fixed: b3_clusters summary says retired seed_24; consequence states the 3-cycle reading fails at every Joyce seed (odd b3); option and adoption kept | (this commit) | S::test_b3_clusters_is_not_stated_at_the_active_seed |
| core-paths-18 | config/parameters/master_action.py:14-35 | fixed in part: PNEUMA_25D renamed PNEUMA_WEYL_26D (no importer), history prose removed; BULK_PLANCK_POWER kept: the source records it is kept for the owner and tests/test_master_action_is_one_consistent_statement.py pins it | (this commit) | S::test_master_action_names_the_weyl_spinor |
| core-paths-17 | variants/adopted.py action forks | blocked: brief keeps the four action forks for L4 wave B | - | - |
| core-paths-28 | topology.critical_dim | blocked: registered in PM/geometry/modular_invariance.py (L2) | - | - |

## Downstream
- None: T, tests/test_canonical_values.py, tests/testground, tests/test_dependency_resolver.py: 588 passed, 1 skipped.
- Round 2: R, K, C, T, tests/testground, tests/test_variants.py, tests/test_g2_differential.py: all pass after the rank_effects rename (one D-019 failure before it).
- Round 3: S, T, R, C, K, tests/testground, test_master_action_is_one_consistent_statement, test_variants, test_canonical_values, test_higgs_sector: 657 passed, 1 skipped. None.

## Needs other lane
- L9: run_all_simulations.py:1469-1483 still wraps load_v25/v26_modules in `except Exception`; the loaders now raise, the caller hides it.
- L5: PM/qed/*.py (nine kernels) register manifest_* as DERIVED; set the status/verdict from FormulasRegistry.QED_ROUNDTRIP_IDENTITIES. PM/qed/_triple_track.py literal 288/28800 (sim-particle-23) should read the registry.
- L2: moduli_indexing b3_clusters needs a reading at the adopted seed (owner decision on adoption).
- theories/pm/ranking.py:68-72 `_consistent` swallows every exception (owner of theories/ unassigned).
- L9: regenerate src/metaphysica/data/path_ranking.json; publish now refuses it (no verdict, option_effects, unranked).
- L5: PM/particle/higgs_mass.py:1489,1495 registers topology.mephorash_chi / elder_kads from TCSTopologyParameters.CHI_EFF / B3, now the live path (B3 = 43, was 24).
- L2: move the b3_path seed table into core; critical_dim in modular_invariance.py.
- L2/L3: PM/qed/compton_wavelength.py still types CODATA 2018 2.42631023867e-12 labelled 2022.
- L3: dark_energy modules use live b3 while dark_energy_betti adopts frozen n = 24.
- canonical_values importers outside L1: generate_prose_drift_audit.py (all_canonical), tests/test_de_plane_gate.py:35; candidate_closure_gate.py and de_plane_gate.py already import at call time.

## Data to confirm
- CODATA 2022 electron Compton wavelength 2.42631023538(76)e-12 m (was the 2018 value).

## Next round
- core-paths-21 (switch_search evaluate_combination: ERRORED state apart from inconsistent), 20, 41.
- core-paths-22, 23, 24 (testground runner fallbacks), 25, 35, 38 (text), 33, 34, 36, 39.
- config/constants.py HODGE_H11/H21/H31 = 4/0/68 (#187); master_action.py:387,412 literals (AUDIT_SUMMARY section 5).
- FormulasRegistry verify_parity typed 1.64034; CANON tau_p, sum_mnu, M_GUT, MKK typed.
- Size splits (CP-19, 31, 37) are wave D P3; CP-42 joint sweep, 44, 45 low.
- Baseline failures: tests/test_b3_root_coverage.py (3), test_b3_status_versus_the_refutation.py (1).
