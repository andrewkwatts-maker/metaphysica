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

Round 6 (2026-11-11). N = tests/programme/test_path_core_named_constants_text.py.
FormulasRegistry.FROZEN_PLEROMA = 24 is the frozen integer behind lambda_S.

Round 4 (2026-11-11). F = tests/programme/test_path_core_fallbacks_and_text.py.
tests/testground/test_2c_screen.py edited: three tests asserted the defects of
core-paths-22/23 (settle swallows, unreadable store or missing import-time
option becomes "unknown"); they now assert the raise.
PathValued moved to config/path_valued.py (config/parameters/path_valued.py
re-exports it) so config/constants.py can use it without an import cycle.

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
| sim-geometry-structure-05 | base/registry.py:789 (re_t_sector rows) | fixed: geometry.ReT and VEV_gap_percent registered CALIBRATED with status_reason (ENTRY_POINT_KEY_STATUSES); re_t_sector.py itself is L2 | bc8dc15 | S::test_re_t_rows_are_calibrated_not_derived |
| sim-particle-27 | base/registry.py:740, 864, 1002 | fixed (registry part): one `_register_entry_point`; import/run error, non-dict return and unknown override raise; no {"error"} skip | bc8dc15 | S::test_entry_point_failure_raises_instead_of_skipping |
| sim-particle-01 | core/FormulasRegistry.py:2417-2431 | fixed in part: QED_ROUNDTRIP_IDENTITIES names the ten manifest identities, "Physical Meaning" text replaced by IDENTITY; score already excludes them (validation_report verdict INPUT/IDENTITY for all nine); Parameter status DERIVED in PM/qed/*.py is L5 | bc8dc15 | S::test_qed_manifest_rows_are_declared_identities |
| core-paths-13 | core/FormulasRegistry.py:1145-1149, 1477-1478, 1874-1875 | fixed: literal 43, 144 and n_gen 3 fallbacks removed; no import cycle (eight import orders checked) | bc8dc15 | S::test_registry_has_no_literal_seed_fallbacks |
| core-paths-26 | core/variants/catalogue/g2_forms.py:264, 294 | fixed: b3_clusters summary says retired seed_24; consequence states the 3-cycle reading fails at every Joyce seed (odd b3); option and adoption kept | bc8dc15 | S::test_b3_clusters_is_not_stated_at_the_active_seed |
| core-paths-18 | config/parameters/master_action.py:14-35 | fixed in part: PNEUMA_25D renamed PNEUMA_WEYL_26D (no importer), history prose removed; BULK_PLANCK_POWER kept: the source records it is kept for the owner and tests/test_master_action_is_one_consistent_statement.py pins it | bc8dc15 | S::test_master_action_names_the_weyl_spinor |
| core-paths-21 | core/switch_search.py:589-623 | fixed: row `state` CONSISTENT/INCONSISTENT/ERRORED, `errored_checks`, search `n_errored`; ranking consumer is theories/ (Needs other lane) | abbca46 | F::test_errored_combination_is_apart_from_inconsistent |
| core-paths-20 | core/switch_search.py:213-217, 577-583 | fixed: fork.default() raises; free set returns (None, "UNMEASURED: <exc>") as `free_set_status` | abbca46 | F::test_a_fork_with_no_default_raises, F::test_free_set_failure_is_an_unmeasured_record |
| core-paths-41 | core/switch_search.py:119 | fixed: resolve("action_bulk_sectors") | abbca46 | F::test_re_t_check_reads_the_live_action_selection |
| core-paths-22 | testground/runner/screen.py:117-123; testground/rank.py | fixed: _settle raises; ranking header `n_not_evaluated`/`not_evaluated`, validated | abbca46 | tests/testground/test_2c_screen.py::test_settle_raises_a_failing_invalidation, F::test_ranking_header_lists_rows_not_evaluated |
| core-paths-23 | testground/runner/screen.py:163-176 | fixed: _process_key raises on an unreadable store or an import-time fork with no option | abbca46 | tests/testground/test_2c_screen.py (two tests) |
| core-paths-24 | testground/runner/worker.py:172-175 | fixed: reason and wall_s required | abbca46 | F::test_run_log_without_reason_or_wall_time_raises |
| core-paths-25 | core/preferred_path.py:5 | fixed | abbca46 | F::test_preferred_path_does_not_count_forks_in_prose |
| core-paths-35 | core/eml_integration.py:363-379 | fixed: chi_eff = 48 n_gen (n_gen of the path when omitted), n_gen = chi_eff/48; old n_gen = chi_eff/(4 b3) gave 1.5 | abbca46 | F::test_eml_chi_eff_is_the_k3_reading_of_the_path |
| core-paths-38 | core/dependency_resolver.py:589-599, 731, build_seed_values | fixed: 153/135/163/288 read from FormulasRegistry; descriptions name the source | abbca46 | F::test_resolver_seeds_are_read_from_the_registry |
| core-paths-33 | core/demon_lock_guard.py:168-190, 479 | fixed: RETIRED_FROM_PAPER = ("verify_integer_closure",), labelled IDENTITY; preflight labels built from registry values (H0 71.55, 23/24, 1.6403 were typed) | abbca46 | F::test_integer_closure_is_retired_and_labels_are_computed |
| core-paths-34 | core/identity_ledger.py:97-256 | refuted: `claimed` is the frozen literal by design and identity_report already evaluates every claim at every seed (per_branch computed, status_on_adopted) | - | - |
| core-paths-36 | core/free_variable_ledger.py:974-1020 | fixed (text): anchors read at geometric_anchors.ANCHOR_FIT, the value they are registered at; split is wave D | abbca46 | F::test_free_variable_ledger_names_the_anchor_it_reads |
| core-paths-39 | config/parameters/bridge.py:125-137, verify_signature | fixed: SHADOW_SIGNATURE (12,1) active; (12,0) kept as RETIRED_SHADOW_SIGNATURE_SPATIAL (no importer); verify_signature sums the two shadows | abbca46 | F::test_bridge_states_the_two_13d_shadow_reading |
| core-paths-11 (config/constants.py) | config/constants.py:72-109, config_dict.py:37-39 | fixed: FundamentalConstants PathValued; HODGE_* kept as RETIRED_TCS187_HODGE_*; euler_characteristic, fermion_generations read the path; config_dict exports b2, b3, chi_eff | abbca46 | F::test_fundamental_constants_follow_the_path |
| core-paths-17 | variants/adopted.py action forks | blocked: brief keeps the four action forks for L4 wave B | - | - |
| core-paths-28 | topology.critical_dim | blocked: registered in PM/geometry/modular_invariance.py (L2) | - | - |
| core-paths-05 (tau_p) | core/canonical_values.py | fixed: CANON tau_p_years read from artifact row proton_decay.tau_p_years (raises when absent), PREDICTED against Super-K 2.4e34; 3.9e34/8.15e34/1.0e34 kept as superseded | R5 | P::test_canon_tau_p_is_read_from_the_artifact |
| core-paths-12 (verify_parity) | core/FormulasRegistry.py verify_parity; core/demon_lock_guard.py | fixed: verify_parity is an IDENTITY against parity_sum_on_path (163/(10 b3 - 1) + fork sigma_T); typed 1.64034 gone; guard prose says IDENTITY | R5 | P::test_parity_check_is_an_identity_on_every_seed |
| core-paths-12 (named constants text) | core/FormulasRegistry.py generate_named_constants_json | fixed: verification block, c_kaf, hubble_formula, tzimtzum and w0 formulas computed from the path; checks labelled IDENTITY | R5 | P::test_named_constants_verification_text_is_computed |
| core-paths-11 (nomenclature) | config/nomenclature.py | fixed: BraneNomenclature, HebrewPhysicsNomenclature PathValued; K_GIMEL, C_KAF, C_KAF_APPLICATION, HEBREW_PARAMETERS from FormulasRegistry; 12.31, 27.2 kept as RETIRED_SEED24_* | R5 | P::test_nomenclature_k_gimel_and_c_kaf_follow_the_path |
| core-paths-44 | core/shape_search.py | fixed: main() command line; primitives read active_path.topology and raise on a missing or non-positive primitive | R5 | P::test_shape_search_primitives_read_the_path, P::test_shape_search_missing_primitive_raises, P::test_shape_search_has_a_command_line_entry |
| core-paths-45 | CI guards | refuted: tests/test_seed_blindness.py and test_registry_paths.py already guard it; the src references are prose | - | - |
| core-paths-19, 31, 37 | size splits | blocked: wave D P3 | - | - |
| core-paths-36 (split) | core/free_variable_ledger.py | blocked: wave D | - | - |
| core-paths-42 | joint geometry sweep | blocked: needs a sweep run (--singles, --joint 2) and artifact regeneration (L9); seed_24 is refused by constrained_singles (b2_over_faces) | - | - |
| sim-particle-23 | core/FormulasRegistry.py | blocked: no change needed in the registry; PM/qed/_triple_track.py is L5 | - | - |
| core-paths-12 (named constants, gates) | core/FormulasRegistry.py generate_named_constants_json; G07/G10/G24/G49/G70, z6_pneuma, geometric_ratio, horos_limit, mass_ratio docstrings | fixed: formula text built from b3, chi_eff_total, n_gen of the path; lambda_S = sqrt(FROZEN_PLEROMA) labelled frozen; Phi_PH 13 labelled typed; parity_product labelled IDENTITY | R6 | N::test_named_constants_formula_text_quotes_the_path |
| core-paths-12 (chi_R) | core/FormulasRegistry.py:1386 | fixed: reid_invariant = 1/chi_eff_total (chi_eff_route), was typed 1/144 | R6 | N::test_reid_invariant_reads_chi_eff_total |
| core-paths-26 (b3_origin) | core/variants/catalogue/seed.py:217-310 | fixed: question names derived_joyce_a1 as the adopted answer; the four 24 options' summaries start "seed_24 only:" (dark_energy_betti text was already frozen-n) | R6 | N::test_b3_origin_options_for_24_are_marked_seed_24 |
| core-paths-05 (sum_mnu, M_GUT, MKK) | core/canonical_values.py:304-342 | blocked: no artifact row carries 0.0994, 2.118e16 or 4.5 (nearest: neutrino.sum_masses 0.1020 DIAGNOSTIC, gauge.M_GUT 6.32e15, geometry.m_KK_central 5.0); which row is the claim is an owner/L5 decision | - | - |

## Review
Round 7 (2026-11-11), reviewer defects in the lane's commits. V =
tests/programme/test_path_core_review.py. Edited tests: tests/test_canonical_values.py
test_wa_ruling_minimal_form (pinned the b2 multiplier) and C::test_derived_constants_follow_the_flux
(pinned pi x 12/b3 on the stub path). New statuses: RETIRED (a reading kept as a record, out of the
score; TopologicalCPPhase); NOT_EVALUABLE (no value on this path; same meaning as identity_ledger).

| defect | action | commit | test |
|---|---|---|---|
| canonical_values._wa_entry projection b2 x wa (-1.83, 3.72 sigma); -0.8165 row dropped | fixed: projection = dim(Psi) x wa = 4 wa (registered wa_projection_x4), -0.6100 at 0.48 sigma; seed_24 rows -0.204124 and -0.816497 kept as retired keys | R7 | V::test_wa_projection_is_the_registered_dim_psi_variant |
| fermion.TopologicalCPPhase pi x 12 (seed_24 count) / 43 = 50.23 deg, DERIVED | fixed: ORIENTATION_SUM renamed RETIRED_TCS187_ORIENTATION_SUM (no importer); DELTA_CP_RAD/DEG, MAXIMAL_CP raise NotEvaluable off seed_24 (config/path_valued.tcs187_only), 90 deg on seed_24; STATUS RETIRED; docstring drops the maximal-CP claim | R7 | V::test_retired_cp_phase_is_not_evaluable_off_seed_24 |
| geometry.G2SpinorGeometry T_topological -43/24, T_omega -1.568 exported RESOLVED | fixed: both are the TCS #187 reading from the RETIRED_TCS187 records (-1.0, -0.875 = TorsionClass); export keys T_*_tcs187, torsion_status RETIRED, status ANSATZ (no importer of the old keys) | R7 | V::test_spinor_torsion_is_the_tcs187_reading_and_agrees |
| canonical_values H0 and tau_p answered for any path from the adopted-path artifact | fixed: artifact seed read from topology.elder_kads, topology.b2 (raises when absent); a path with other (b3, b2) gets status NOT_EVALUABLE, value None | R7 | V::test_artifact_entries_are_not_evaluable_on_another_seed, V::test_artifact_seed_rows_missing_raise |
| test_wa_ruling_minimal_form dropped the sigma check, pinned b2 | fixed: comparison.sigma recorded and quoted in the note (2.06 at b3 = 43, asserted), projection tested against 4 wa | R7 | tests/test_canonical_values.py::test_wa_ruling_minimal_form, V::test_wa_tension_on_the_adopted_seed_is_recorded |

Review notes: GeometricAnchors.elder_kads is 24 on the adopted path, so the registered
wa_projection_x4 row reads -0.8165 there (L2). base/established.py registers
topology.orientation_sum = 12 ESTABLISHED, a TCS #187 count used live by
PM/particle/neutrino_mixing.py (next round, with L5).

## Close-out
Round 1 (2026-11-11), WAVE_A_CLOSEOUT.md section XP. X = tests/programme/test_path_core_closeout_<topic>.py.
Commit "this" means the commit that carries the row; the last close-out commit fills the hashes.
Edited test: tests/test_frozen_seed_literals.py (XP-09): FROZEN_AT_24 drops FormulasRegistry
sterile_sector, PROSE_STALE_AT_24 drops denominator, and the parity test is inverted
(test_the_registry_parity_check_is_an_identity_on_the_path); it asserted the pre-12db48f/acebadd
state, and the moves are recorded first in docs/FROZEN_SEED_LITERALS.md "Moves recorded 2026-11-11".

| id | file:line | state | commit | test |
|---|---|---|---|---|
| XP-08 | theories/pm/ranking.py:68-79 `_consistent` | fixed: an ERRORED row is None (missing); every exception and a row without `state` raise | this | X ranking_consistent (5 tests) |
| XP-09 | four audit tests | fixed: test_frozen_seed_literals 3 failures were wave A moves (12db48f text, acebadd verify_parity), recorded in FROZEN_SEED_LITERALS.md then repinned; test_sterility_audit, test_value_context_audit, test_seed_blindness pass unchanged | this | the four files: 18, 11, 3, 6 passed |
| XP-01 | core/demon_lock_guard.py verify_tzimtzum_fraction | fixed: expected (n-1)/n with n from de_betti_n(resolve_de_betti()) (the reader verify_parity uses); violation and formula warning name the fork fraction | this (group 2) | X guard::test_tzimtzum_fraction_reads_the_dark_energy_fork, ::test_tzimtzum_fraction_flags_a_registry_off_the_fork, ::test_tzimtzum_formula_warning_names_the_fork_fraction |
| XP-04 | core/demon_lock_guard.py verify_hubble_formula; base/registry.py register_dependency | fixed: docstring names the formula and h0_local, no 71.55 or 288/4; example uses a ratio with no seed value | this (group 2) | X guard::test_docstrings_do_not_quote_the_seed_24_hubble_value |
| XP-07 | core/demon_lock_guard.py RETIRED_FROM_PAPER, run_preflight; FormulasRegistry.py __main__ | fixed: verify_sterile_parity (the guard's form of the verify_parity identity) joins RETIRED_FROM_PAPER; run_preflight runs identities apart, moves their violations to warnings, and records `tally` (scored_passed, scored_total, identities_not_counted); registry __main__ all_verified drops verify_parity | this (group 2) | X guard::test_parity_identity_is_not_counted_in_the_preflight, ::test_a_broken_parity_identity_does_not_block_the_lock, ::test_registry_main_tally_leaves_verify_parity_out |
| XP-02 | core/FormulasRegistry.py FROZEN_PLEROMA, named constant hossenfelder_root | fixed: FROZEN_PLEROMA_STATUS = "ANSATZ" (no fork; owner decision open); lambda_S entry carries status and status_reason; misplaced _PATH_VALUED_SYMBOLS comment restored | this (group 3) | X registry_rows::test_lambda_s_named_constant_is_an_ansatz |
| XP-10 | base/established.py coherence_fraction, orientation_sum, _register_param | partly fixed: sim-algebra-misc-12 coherence_fraction and orientation_sum (TCS #187 count) are INPUT, registered with no experimental value; sim-algebra-misc-24 blocked (text in PM/gauge/master_action.py L4, formulas.json L9); VD-19 blocked (geometry.m_KK_central status set in PM/geometry/geometric_anchors.py L2) | this (group 3) | X registry_rows::test_typed_inputs_are_not_validated_against_themselves, ::test_orientation_sum_says_it_is_not_derived_on_the_path |
| XP-03 | config/path_valued.py tcs187_only for TorsionClass.T_OMEGA | blocked: raising off seed_24 breaks live consumers on the adopted path (config/parameters/proton_decay.py:45 class body, PM/particle/higgs_mass.py:1501, fitted.py derive_alpha_sum, derive_M_GUT, torsion_enhancement_factor) and the fresh-clone gate; convert consumers first (wave B) | - | - |
| XP-11 | config/path_valued.py retired TCS #187 readers | blocked: same reason; consumers g2_geometry.py, ckm_matrix.py, proton_decay.py, appendix_c_derivations.py | - | - |

Not done this round (tool-call cap): XP-05 (FormulasRegistry seed_24 comments), XP-12 (core/sync_docs.py seed_24 text, parity to reg._parity_text() as IDENTITY), XP-06 (split switch_search.search ERRORED handling), XP-13 (fill "this" commit cells: close-out f860be6, group 2 8ccbfc3, group 3 its hash; R5 acebadd, R6 7808641, R7 205b1f4).

## Downstream
- Close-out: X ranking_consistent, test_frozen_seed_literals, test_sterility_audit, test_value_context_audit, test_seed_blindness pass. None.
- Close-out group 2: X guard, test_demon_lock_guard, test_path_core_fallbacks_and_text, test_dark_energy_betti_gate pass. None.
- Close-out group 3: X registry_rows 4 passed. None run beyond it.
- Round 7: V, C, T, P, tests/test_canonical_values.py: 55 passed. None.
- None: T, tests/test_canonical_values.py, tests/testground, tests/test_dependency_resolver.py: 588 passed, 1 skipped.
- Round 2: R, K, C, T, tests/testground, tests/test_variants.py, tests/test_g2_differential.py: all pass after the rank_effects rename (one D-019 failure before it).
- Round 3: S, T, R, C, K, tests/testground, test_master_action_is_one_consistent_statement, test_variants, test_canonical_values, test_higgs_sector: 657 passed, 1 skipped. None.

- Round 5 (P = tests/programme/test_path_core_parity_and_text.py): P, test_canonical_values, test_formulas_registry_core, test_physics_invariants, test_sterility_audit, test_value_context_audit, test_declarative_strategy_a/b, test_racetrack_is_an_ansatz_not_a_vacuum, tests/testground pass. tests/test_frozen_seed_literals.py fails 3: it pins the removed defects (FormulasRegistry prose sterile_sector/denominator rows GONE; verify_parity no longer fails at the live seed). Its docstring requires docs/FROZEN_SEED_LITERALS.md and the register to record the move before repinning; neither is L1, so not edited.
- Baseline (not L1): tests/test_b3_root_coverage.py 3 fail from AutoGenerated dependency_chains (walker root_seed "b3=24", degraded walks; L9); test_b3_status_versus_the_refutation.py fails because OUTSTANDING_ISSUES.md is now split into docs/issues/.

## Needs other lane
- Owner of docs/FROZEN_SEED_LITERALS.md: record the round-5 moves, then repin tests/test_frozen_seed_literals.py inventories and invert its verify_parity test.
- theories/pm/ranking.py `_consistent`: map switch_search row state ERRORED to None (missing), so ERROR rows leave the ladder tie-break (core-paths-21).
- L9: run_all_simulations.py:1469-1483 still wraps load_v25/v26_modules in `except Exception`; the loaders now raise, the caller hides it.
- L5: PM/qed/*.py (nine kernels) register manifest_* as DERIVED; set the status/verdict from FormulasRegistry.QED_ROUNDTRIP_IDENTITIES. PM/qed/_triple_track.py literal 288/28800 (sim-particle-23) should read the registry.
- L2: moduli_indexing b3_clusters needs a reading at the adopted seed (owner decision on adoption).
- theories/pm/ranking.py:68-72 `_consistent` swallows every exception (owner of theories/ unassigned).
- L9: regenerate src/metaphysica/data/path_ranking.json; publish now refuses it (no verdict, option_effects, unranked).
- L5: PM/particle/higgs_mass.py:1489,1495 registers topology.mephorash_chi / elder_kads from TCSTopologyParameters.CHI_EFF / B3, now the live path (B3 = 43, was 24).
- L2: move the b3_path seed table into core; critical_dim in modular_invariance.py.
- L2: GeometricAnchors.elder_kads = 24 on seed_43_joyce, so wa and wa_projection_x4 rows are the seed_24 numbers.
- L5: neutrino_mixing.py divides topology.orientation_sum (a TCS #187 count, 12) by the live b3 and chi_eff.
- L2/L3: PM/qed/compton_wavelength.py still types CODATA 2018 2.42631023867e-12 labelled 2022.
- L3: dark_energy modules use live b3 while dark_energy_betti adopts frozen n = 24.
- Close-out XP-03/XP-11: L5 and others convert TorsionClass and TCS #187 consumers before tcs187_only can raise. XP-10: L4 master_action.py text and L9 formulas.json (sim-algebra-misc-24); L2 geometric_anchors.py m_KK_central status (VD-19). Register in PrincipiaMetaphysica/docs/issues/ to record the wave A moves. verify_w0_seal still types thawing = -23/24.
- canonical_values importers outside L1: generate_prose_drift_audit.py (all_canonical), tests/test_de_plane_gate.py:35; candidate_closure_gate.py and de_plane_gate.py already import at call time.

## Data to confirm
- CODATA 2022 electron Compton wavelength 2.42631023538(76)e-12 m (was the 2018 value).
- Source rows for CANON sum_mnu, M_GUT and MKK in the parameter artifact (none match today).

## Next round
- FormulasRegistry module docstring, __init__ comments and the HEBREW symbol-map comments still quote b3 = 24 (e.g. lines 114-151, 1183, 1252, 1282, 1329); torsion_gate G53 types 1/24 (24th root): owner to say whether that 24 is b3 or the 24 space dimensions.
- CANON sum_mnu 0.0994, M_GUT 2.118e16, MKK 4.5 still typed: no artifact row found (see Data to confirm).
- Size splits CP-19, 31, 36 (ledger), 37 are wave D P3; core-paths-42 waits on L9.
