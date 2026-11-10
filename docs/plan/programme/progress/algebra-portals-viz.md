# algebra-portals-viz (L6) progress, rounds 1 to 5

| id | file:line | state | commit | test |
|---|---|---|---|---|
| sim-algebra-misc-01 | visualizations/figure3_alp_discovery_window.py | fixed: point read from registry rows, plotted where it falls | see git log | test_algebra_portals_viz_first_round::test_figure3_point_from_registry_rows |
| sim-algebra-misc-02 | PM/portals/alp_portals.py | fixed: ALP rows CALIBRATED, photon coupling scored against the 1e-10 stellar bound (FAIL kept) | | ::test_alp_rows_calibrated_and_scored_against_bound |
| sim-algebra-misc-03 | PM/algebra/clifford_unification.py | fixed: boost row removed (it was a rotation), no swallowed exceptions | | ::test_clifford_boost_row_removed_and_no_swallowed_errors |
| sim-algebra-misc-04 | freudenthal_triple, e7_representation, e8x8_splitting | fixed: text/certificates read active b3 via PM/algebra/_active_b3.py | | ::test_text_reads_active_b3 |
| sim-algebra-misc-05, 23 | freudenthal_triple.py | fixed: bulk-match and V_bridge/racetrack text removed | | ::test_freudenthal_text_does_not_match_bulk |
| sim-algebra-misc-13, 16 | PM/support/complete_residue_registry.py | fixed: formula text built from computed m1 and sum, docstring b3 | | ::test_residue_registry_no_swallowed_loader_errors_or_literal_fallbacks |
| sim-algebra-misc-15 | complete_residue_registry.py | fixed: _pdg_v/_pdg_u raise, literal fallbacks and `or 0.0031` style defaults removed | | same |
| sim-algebra-misc-14 | complete_residue_registry.py | partly: v and Dm2 read from loader; M_GUT = 2e16 stays, blocked on register 2.2 ruling | | same |
| sim-algebra-misc-18 | qec_golay_bridge.py | fixed: mapping reads active b3, MISMATCH at b3 = 43 | | ::test_qec_mapping_reads_active_b3 |
| sim-algebra-misc-19 | neutrino_algebraic.py | fixed: chi_eff, n_gen, alpha_leak fallbacks raise; inputs declared. Module-level text constants (_B3 etc.) remain | | ::test_neutrino_algebraic_missing_topology_row_raises |
| sim-algebra-misc-25,26,27,28 | visualizations figure1, brane_diagrams, certificate_dashboard, figure2 | fixed: no typed b3, 26D text, seal and gate text from GATES_CERTIFICATES.json, no invented 1% error | | test_algebra_portals_viz_figures.py |
| sim-algebra-misc-09 (+43 in part) | consciousness/orch_or_pair_shielding.py | fixed: one `shielding_enhancement(n)` feeds value, description, formula, certificate and self-check; k = 2.5 stays labelled FITTED, no fit target | | test_algebra_portals_viz_second_round::test_shielding_one_function_everywhere |
| sim-algebra-misc-20 | algebra/neutrino_algebraic.py | fixed: theta13 and alpha_leak text, sigma and EML text built from `_derived_values()` (path in force); module b3/chi/n_gen constants removed; delta_CP text reads the labelled `_OFF_PATH` object | | ::test_neutrino_text_follows_value_not_one_sixth |
| sim-algebra-misc-21 | algebra/e7_representation.py, e8x8_splitting.py | fixed: algebra.e7_alpha_leak and e8_portal_coupling are ANSATZ normalisation 1/sqrt(6), named as not geometry.alpha_leak, no self-bound | | ::test_e7_normalisation_is_not_the_coupling_in_force |
| sim-algebra-misc-22 | e7_representation.py | fixed: e7_alp_mass_gev kept as a row (rule 5), status ANSATZ, named an inverse-GeV number not a mass | | same |
| sim-algebra-misc-06 | gaugino_condensation.py | refuted as to text: every N1 = 24 sentence already says "at the off-path seed"; statuses fixed under 07 | | |
| sim-algebra-misc-07 | gaugino_condensation.py, e8x8_splitting.py | fixed: W_np_1/2, lambda_eff, T_min, condensate_ratio, e8_hidden_condensate, heterotic proxy now CALIBRATED | | ::test_gaugino_and_e8_condensate_rows_calibrated |
| sim-algebra-misc-29 | algebra/octonions.py | fixed: only ImportError falls back; undeclared fork raises | | ::test_octonion_fork_read_does_not_swallow_errors |
| sim-algebra-misc-30 | algebra/__init__.py | fixed: guard removed | | ::test_algebra_init_has_no_import_guard |
| sim-algebra-misc-35 | clifford_unification.py | fixed: the three self-test rows have status IDENTITY (rows kept) | | ::test_clifford_self_tests_are_identity_rows |
| sim-algebra-misc-36 | leech_lattice.py | fixed: working-out comments and dead loop replaced by a short Conway-Sloane note | | ::test_leech_enumeration_has_no_working_out_left |
| sim-algebra-misc-44 | four_dice_sampling.py | fixed: ANSATZ | | ::test_dice_rows_are_ansatz |
| sim-algebra-misc-11 | field_dynamics/orch_or_geometry.py | blocked: file owned by L4 (quantum_bio.topological_pitch to CALIBRATED with the 2.125 factor shown) | | |
| sim-algebra-misc-12 | simulations/base/established.py | blocked: not in the L6 set (consciousness.coherence_fraction to status INPUT, out of validation) | | |
| sim-algebra-misc-34 | paper/appendices/appendix_clifford_algebra.py | blocked: paper lane (signature_count row to INPUT) | | |
| sim-algebra-misc-08 | docs/claude-context.md | blocked: docs, not in the L6 set | | |
| sim-algebra-misc-31 | PM/portals/alp_portals.py | fixed: the 24 is the named constant G_AGG_DENOMINATOR (value and EML tree); worked numbers stay labelled off-path seed | | test_algebra_portals_viz_third_round::test_alp_denominator_is_a_named_constant |
| sim-algebra-misc-32 | visualizations/ricci_flow_evolution.py | fixed: w0, wa derived from named OFF_PATH_B3, curve label built from the value, still labelled off-path | | ::test_ricci_flow_w_parameters_derived_from_named_seed |
| sim-algebra-misc-33 | goldilocks_plot, stability_heatmap, theory_overview_diagrams | fixed: RETIRED_FROM_PAPER = True, modules and output kept | | ::test_off_path_figures_retired_from_paper |
| sim-algebra-misc-39 | e7_representation.py | fixed: M_Pl from RealWorldData.PLANCK_MASS; the 0.693 literal in clifford_unification no longer exists | | ::test_e7_planck_mass_read_from_dataset |
| sim-algebra-misc-10 | consciousness/gnosis_unlocking.py, orch_or_pair_shielding.py | fixed: gnosis chain (tau_0 INPUT, k fitted) is CALIBRATED and the one chain; Penrose rows labelled separate speculation. quantum_bio row is L4 | | ::test_gnosis_chain_is_calibrated_and_penrose_is_labelled_separate |
| sim-algebra-misc-45 | PM/algebra/shadow_clifford.py | fixed: test builds the 13 64x64 gammas, checks Clifford relations, 64^2 = 4096, quaternionic | | ::test_4096_claim_from_explicit_64x64_gammas |
| sim-algebra-misc-41 | PM/portals/*.py | refuted: all 12 rows have descriptions in code and bounds where a bound exists (cross-section 1e-45 XENONnT); the empty ones are stale generated parameters.json | | |
| sim-algebra-misc-17 | PM/geometry/leech_partition.py | blocked: not in the L6 set (n_gen_leech to RETIRED, b3_leech_identification status) | | |
| sim-algebra-misc-24 | core formulas pneuma-master-action-v23, shadow-action-13d-v23 | blocked: FormulasRegistry/formula data, not in the L6 set | | |
| sim-algebra-misc-40 | freudenthal_triple.py, e7_representation.py | blocked: freudenthal_quartic is read by core/free_set.py, geometry/b3_candidate_sweep.py, tests/test_free_set.py; removing it needs those lanes | | |
| sim-algebra-misc-42 | Constants/ad-hoc, extract_supplementary, section_schema | blocked: no importer, but run_all_simulations.py rglob("*.py") lists the folder in its script index, so rule 5 forbids deleting; needs a ruling | | |
| sim-algebra-misc-43 | consciousness/orch_or_pair_shielding.py | fixed: shielded_tau_ms and shielding_factor CALIBRATED, RETIRED_FROM_PAPER = True, text says no data it was fitted to (rows kept) | | test_algebra_portals_viz_fourth_round::test_shielding_rows_with_fitted_k_are_calibrated |
| sim-algebra-misc-13 (recheck) | support/complete_residue_registry.py | fixed: proton-decay block had `b3 = 24` and M_Planck 1.22e19 typed; now active_b3() and RealWorldData.PLANCK_MASS | | ::test_proton_decay_block_reads_b3_from_path |
| sim-algebra-misc-37 (leech_lattice part) | algebra/leech_lattice.py | partly: split into leech_lattice (499), golay_code (92), leech_decomposition mixin (499); GolayCode re-exported. gaugino_condensation.py (913) and neutrino_algebraic.py (1068) still over the limit | | test_algebra_portals_viz_fifth_round.py |

Round 2 status vocabulary: reused ANSATZ, CALIBRATED; IDENTITY (the validation verdict word) used as a Parameter status for self-test rows: true by construction.

Status vocabulary: reused CALIBRATED and bound_type "upper"; no new status.

## Downstream
tests/test_eml_fallback_is_import_only.py fixture supplied chi_eff, n_gen, alpha_leak (round 1 made them required); edited, subject is my file. test_simulations_do_not_need_plotting fails independent of this lane (matplotlib present).
paper/appendices/appendix_clifford_algebra.py still names algebra.clifford_boost_conservation (removed). Re-run of AutoGenerated needed before figure 3 / dashboard match the new rows.

## Needs other lane
appendix_clifford_algebra.py (paper lane): drop the boost row. M_GUT ruling (register 2.2) for sim-algebra-misc-14.

## Data to confirm
Stellar bound 1e-10 GeV^-1 (module value) versus HB 6.6e-11 quoted in alp_portals section text.

## Next round
Round 5: leech_lattice split done. Left: 14 (M_GUT ruling), 37 (gaugino_condensation, neutrino_algebraic), 38 (portals x3, consciousness x3, complete_residue_registry, proof_completeness: one file per round).
Round 4: 43 and 13 recheck done. Left: 14 (M_GUT ruling), 37/38 file splits (prose to data files; large, one file per round), 16/23-28 appear done.
Done in round 3: 10,31,32,33,39,45 fixed; 41 refuted; 17,24,40,42 blocked. Remaining: 13 (formula text check), 14 (M_GUT ruling), 16, 23-28 recheck, 37/38 file splits (last), 43 (gnosis k = 3.2 now CALIBRATED; RETIRE-FROM-PAPER of shielding k still open), plus any finding numbered above 45.

## Review
Review round on 7af0d85, 25f333e, 6bad1bd, 38a9339. Tests: tests/programme/test_algebra_portals_viz_sixth_round.py (new) plus corrected tests in first_round, second_round, third_round (each subject is my file and asserted the defect).

| defect | action | commit |
|---|---|---|
| clifford_boost_conservation deleted (0.408 vs 0.1) | row restored: output param, Parameter status FALSIFIED, check in run() with 0.408, section row and callout "FAILS", 3 of 4 checks pass. first_round test inverted to assert presence | review-round |
| proton-decay text typed 4.24e39 yr, ~2.5e18 GeV | `proton_decay_values()` computes tau_p, M_GUT_base, M_GUT_eff (b3 via active_b3, chi_eff via registry, M_Pl via dataset); `proton_decay_text()` feeds every formula, parameter and section string; test compares text to run() residues | review-round |
| neutrino text "~12% high", "~4 sigma", "1/sqrt6", `(1/sqrt6)/sqrt6 = 1/6` | `_overshoot(V)` builds "+49%, 38.7 sigma"; formula block, n_gen factor and alpha_leak at the off-path seed built from values; second_round test now rejects "12%", "sqrt6", "~4 sigma" | review-round |
| neutrino re-derives n_gen = b2/4, chi_eff = 48 n_gen, `_OFF_PATH = _derive(24,3,144.0)` | `_derive(topo, alpha_leak)` takes `core.active_path.topology()` (fork readers) and `canonical_values.canon()["alpha_leak"]` (the one function); `_off_path()` reads named seed_24; `_seed_split_note` reads topology | review-round |
| ricci_flow OFF_PATH_B3 = 24 | read from `seed_values("seed_24")`; third_round test compares to that read | review-round |
| RETIRED_FROM_PAPER read by nothing | new `visualizations/_retired.py` (`output_dir_for`, `paper_figures`); the three figure modules write to a `retired` subfolder; orch_or_pair_shielding returns no section and no certificates while flagged (certificate kept as `shielding_certificates()`); test generates the Goldilocks figure and finds it under retired/ and checks all_plots list unchanged | review-round |
| shielding EML tree exp(k sqrt(n)) and category PREDICTED | tree now exp(k sqrt(n/12)) (n/6)^2, category CALIBRATED; test evaluates the tree against `shielding_enhancement` at n = 6 and 12 | review-round |
| octonion fork test passed on base | test monkeypatches `variants.resolve` to raise KeyError and asserts it propagates; the `except ImportError: return self._C_mult` fallback also removed; run against the 355bfd9 source the getter returns without raising, so the test fails there | review-round |

Needs other lane (added): all_plots.py, run_all_simulations.py (still builds OrchORPairShieldingSimulation, harmless now: no section, no certificate), website/Pages/visualization-index.html and js/pm-visualization-manifest.js still list the three retired figures (site lane). e7_representation.py and e8x8_splitting.py text still says alpha_leak = 1/sqrt(6) (not in this review's list; next round).
