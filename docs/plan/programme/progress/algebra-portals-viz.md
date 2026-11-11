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
| sim-algebra-misc-45 | PM/algebra/shadow_clifford.py | verification test (no code defect; XA-14): test builds the 13 64x64 gammas, checks Clifford relations, 64^2 = 4096, quaternionic | | ::test_4096_claim_from_explicit_64x64_gammas |
| sim-algebra-misc-41 | PM/portals/*.py | refuted: all 12 rows have descriptions in code and bounds where a bound exists (cross-section 1e-45 XENONnT); the empty ones are stale generated parameters.json | | |
| sim-algebra-misc-17 | PM/geometry/leech_partition.py | blocked: not in the L6 set (n_gen_leech to RETIRED, b3_leech_identification status) | | |
| sim-algebra-misc-24 | core formulas pneuma-master-action-v23, shadow-action-13d-v23 | blocked: FormulasRegistry/formula data, not in the L6 set | | |
| sim-algebra-misc-40 | freudenthal_triple.py, e7_representation.py | blocked: freudenthal_quartic is read by core/free_set.py, geometry/b3_candidate_sweep.py, tests/test_free_set.py; removing it needs those lanes | | |
| sim-algebra-misc-42 | Constants/ad-hoc, extract_supplementary, section_schema | blocked: no importer, but run_all_simulations.py rglob("*.py") lists the folder in its script index, so rule 5 forbids deleting; needs a ruling | | |
| sim-algebra-misc-43 | consciousness/orch_or_pair_shielding.py | fixed: shielded_tau_ms and shielding_factor CALIBRATED, RETIRED_FROM_PAPER = True, text says no data it was fitted to (rows kept) | | test_algebra_portals_viz_fourth_round::test_shielding_rows_with_fitted_k_are_calibrated |
| sim-algebra-misc-13 (recheck) | support/complete_residue_registry.py | fixed: proton-decay block had `b3 = 24` and M_Planck 1.22e19 typed; now active_b3() and RealWorldData.PLANCK_MASS | | ::test_proton_decay_block_reads_b3_from_path |
| sim-algebra-misc-37 (leech_lattice part) | algebra/leech_lattice.py | partly: split into leech_lattice (499), golay_code (92), leech_decomposition mixin (499); GolayCode re-exported. gaugino_condensation.py (913) and neutrino_algebraic.py (1068) still over the limit | | test_algebra_portals_viz_fifth_round.py |

Round 2 status vocabulary: reused ANSATZ, CALIBRATED; IDENTITY (the validation verdict word) used as a Parameter status for self-test rows: true by construction.

Status vocabulary: reused CALIBRATED and bound_type "upper". IDENTITY is the accepted status for a row true by construction (rule 4; path-core uses it for the qed rows), so the clifford self-test rows use it as an existing status, not a new one (corrected in close-out XA-13).

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
Review round on 7af0d85, 25f333e, 6bad1bd, 38a9339; the review-round commit is f23f5d7. Tests: tests/programme/test_algebra_portals_viz_sixth_round.py (new) plus corrected tests in first_round, second_round, third_round (each subject is my file and asserted the defect).

| defect | action | commit |
|---|---|---|
| clifford_boost_conservation deleted (0.408 vs 0.1) | row restored: output param, Parameter status FALSIFIED, check in run() with 0.408, section row and callout "FAILS", 3 of 4 checks pass. first_round test inverted to assert presence | f23f5d7 |
| proton-decay text typed 4.24e39 yr, ~2.5e18 GeV | `proton_decay_values()` computes tau_p, M_GUT_base, M_GUT_eff (b3 via active_b3, chi_eff via registry, M_Pl via dataset); `proton_decay_text()` feeds every formula, parameter and section string; test compares text to run() residues | f23f5d7 |
| neutrino text "~12% high", "~4 sigma", "1/sqrt6", `(1/sqrt6)/sqrt6 = 1/6` | `_overshoot(V)` builds "+49%, 38.7 sigma"; formula block, n_gen factor and alpha_leak at the off-path seed built from values; second_round test now rejects "12%", "sqrt6", "~4 sigma" | f23f5d7 |
| neutrino re-derives n_gen = b2/4, chi_eff = 48 n_gen, `_OFF_PATH = _derive(24,3,144.0)` | `_derive(topo, alpha_leak)` takes `core.active_path.topology()` (fork readers) and `canonical_values.canon()["alpha_leak"]` (the one function); `_off_path()` reads named seed_24; `_seed_split_note` reads topology | f23f5d7 |
| ricci_flow OFF_PATH_B3 = 24 | read from `seed_values("seed_24")`; third_round test compares to that read | f23f5d7 |
| RETIRED_FROM_PAPER read by nothing | new `visualizations/_retired.py` (`output_dir_for`, `paper_figures`); the three figure modules write to a `retired` subfolder; orch_or_pair_shielding returns no section and no certificates while flagged (certificate kept as `shielding_certificates()`); test generates the Goldilocks figure and finds it under retired/ and checks all_plots list unchanged | f23f5d7 |
| shielding EML tree exp(k sqrt(n)) and category PREDICTED | tree now exp(k sqrt(n/12)) (n/6)^2, category CALIBRATED; test evaluates the tree against `shielding_enhancement` at n = 6 and 12 | f23f5d7 |
| octonion fork test passed on base | test monkeypatches `variants.resolve` to raise KeyError and asserts it propagates; the `except ImportError: return self._C_mult` fallback also removed; run against the 355bfd9 source the getter returns without raising, so the test fails there | f23f5d7 |

Needs other lane (added): all_plots.py, run_all_simulations.py (still builds OrchORPairShieldingSimulation, harmless now: no section, no certificate), website/Pages/visualization-index.html and js/pm-visualization-manifest.js still list the three retired figures (site lane). e7_representation.py and e8x8_splitting.py text still says alpha_leak = 1/sqrt(6) (not in this review's list; next round).

## Close-out
Round 1 (WAVE_A_CLOSEOUT.md, XA). Tests: tests/programme/test_algebra_portals_viz_closeout_*.py.

| id | file:line | state | commit | test |
|---|---|---|---|---|
| XA-01 | PM/support/complete_residue_registry.py (2.3.3) | fixed: GUT scale in the text is `pt['eff']`; "2×10¹⁷" added to the strings the proton-text test rejects | 74b6e25 | test_algebra_portals_viz_closeout_residue_text::test_section_gut_scale_is_the_computed_effective_value |
| XA-07 | complete_residue_registry.py (Dm2 terms, M_Pl term, row 61, lambda_max EML text) | fixed: `_dm2_term` reads NuFIT; M_Pl, b3, chi_eff terms from `proton_decay_text()`; row 61 value and error from `RealWorldData.PLANCK_MASS`; lambda_max EML text built from the value | 74b6e25 | ::test_neutrino_splitting_terms_read_the_loader, ::test_planck_mass_text_and_row_read_the_dataset |
| XA-11 | complete_residue_registry.get_formulas | fixed: docstring first | 74b6e25 | ::test_get_formulas_docstring_is_first |
| XA-02 | PM/algebra/clifford_unification.py:224 | fixed: FALSIFIED description quotes `run()`'s boost error; run docstring and comment name BOOST_BOUND, BOOST_RAPIDITY | e3ec3d5 | test_algebra_portals_viz_closeout_clifford::test_falsified_description_is_built_from_run |
| XA-03 | clifford_unification.py:269 | fixed: TAB + "exttt{" restored to `	exttt{` | e3ec3d5 | ::test_minkowski_row_starts_with_texttt |
| XA-06 | clifford_unification.get_section_content | fixed: g2_inv, rot_err, checks_passed, all_pass already came from `run()` (since f23f5d7); the typed "/4" total now `run()['_checks_total']` | e3ec3d5 | ::test_section_text_follows_a_changed_run |
| XA-05 | PM/algebra/gaugino_condensation.py (A4.3) | fixed: category FALSIFIED, as its description and `algebra.gaugino_cabibbo_proxy` say; its sigma built from the value | 420820f | test_algebra_portals_viz_closeout_gaugino_status.py |
| XA-08 | PM/algebra/qec_golay_bridge.py | fixed: abstract, callout and metadata text read the computed b3 and classification (MISMATCH at b3 = 43); RETIRED_FROM_PAPER = True: no section, no certificates (kept as `paper_section()`, `qec_certificates()`), rows and formulas kept | f0ed6e8 | test_algebra_portals_viz_closeout_qec_retired.py |
| XA-10 | PM/portals/alp_portals.py | partly: one bound `STELLAR_COOLING_BOUND_GEV_INV` in the registered row, the Parameter (was CAST 6.6e-11), the section text (was HB 6.6e-11), certificate and self-check; `stellar_bound_sentence` shows the live value and "bound check FAIL"; row stays CALIBRATED (upper bounds are not in chi2), metadata `source_unverified`. Blocked part: reading the bound from the loader needs an L7 data entry (Needs other lane) | d5c3792 | test_algebra_portals_viz_closeout_alp_bound.py |
| XA-09 | visualizations/figure1_m27_decomposition.py | fixed: label `b_3 = <value>` read from registry row topology.elder_kads (`b3_from_registry`, raises when missing); "24D G2 Core" now "24D Spatial Core", G2 holonomy labelled Y_7's. Not renamed: `src/metaphysica/generators/all_plots.py:27` imports it (outside the lane) | 2d7d955 | test_algebra_portals_viz_closeout_figure1_b3.py |
| XA-13 | this progress file | fixed: IDENTITY note corrected (accepted status, rule 4); review-round rows carry commit f23f5d7 (8 rows) | 29f1373 | none (docs) |
| XA-14 | tests/programme | verification test (no code defect, no code change: it passes on the base code; R2-07): 196,560 = 1104 + 759*2^7 + 24*4096 counted on the Golay object and equal to `kissing_number`; misc-45 marked a verification test too | 29f1373 | test_algebra_portals_viz_closeout_leech_count.py |
| XA-12 | tests/test_eml_fallback_is_import_only.py | fixed: fixture b3, chi_eff, n_gen from `active_path.topology()`, alpha_leak from `canon()` | 29f1373 | the file itself (fixture only, no assertion changed) |
| XA-15 | PM/algebra/neutrino_algebraic.py | refuted: no `_B3 = 24` or 9.59 degree constant at HEAD (removed under misc-20, 38a9339/f23f5d7); the module constants left are NuFIT inputs | | |
| XA-16 | oversize functions | recorded, wave D: not worked; no listed function grew this round (new logic went to `_dm2_term`, `stellar_bound_sentence`, `paper_section`, `b3_from_registry`) | | |
| XA-04 | visualizations/_retired.py, stability_heatmap.html | round 2, partly: stale `stability_heatmap.html` and `stability_heatmap_data.json` moved with `git mv` to `visualizations/retired/` (where `output_dir_for` writes them), not deleted. Blocked part: no plot list or index is built inside visualizations/**; the only one is `generators/all_plots.py:21` `VISUALIZATION_MODULES` (generators lane), which lists none of the three retired modules, so `paper_figures` has no in-lane caller (Needs other lane) | d0576ed | test_algebra_portals_viz_closeout_retired_heatmap.py |

Edited tests: test_algebra_portals_viz_sixth_round.py::test_proton_text_is_built_from_the_computed_values now also rejects "2×10¹⁷" (XA-01 asks for it).

Close-out needs other lane: L7 (validation-data, owns simulations/data/**): add the stellar-cooling g_agg upper bound to a data file with `source_unverified` (1e-10 versus HB 6.6e-11), then alp_portals reads it with `get_loader().get_value(...)` (XA-10 rest).
Rename figure1_m27_decomposition.py to figure1_m26_decomposition.py (XA-09): generators lane edits all_plots.py:27 in the same commit (`git mv` then the import); AutoGenerated indexes regenerate.

Close-out round 2 needs other lane: generators lane (all_plots.py) builds the plot list as `_retired.paper_figures(VISUALIZATION_MODULES)` in `main()`, with a test that a retired module in the list is not run; or the planner grants all_plots.py to this lane.

Close-out next round (round 1 note, XA-04 now partly done): XA-04 (call `paper_figures` where the plot list and index are built inside visualizations/**, test that fails without the call; move stability_heatmap.html and its data file beside the retired figures). gaugino_condensation still types 344.7/37.6/25.6 sigma outside A4.3 (lines ~116, 554, 747, 788, 826, 839); alp section text still says alpha_leak = 1/sqrt(6), chi_eff = 72 unlabelled.

## Close-out review
| defect | file:line | action | commit | test |
|---|---|---|---|---|
| XA-05 test could not detect typed text: the typed 344.7σ equalled the value computed at N1 = 24, so `test_cabibbo_proxy_sigma_is_built_from_the_value` passed on b8cf83e | tests/programme/test_algebra_portals_viz_closeout_gaugino_status.py:17 | fixed: PDG λ_W and its uncertainty read from the loader (`_pdg_lambda_w`, ckm V_us) and the quote built by `_vs_pdg` in A4.3 and A4.4 (A4.4's typed 37.6σ and "cf. PDG 0.22500" too, rule 6); the test patches the PDG input to 0.30000 ± 0.00200 and asserts the description follows it (fails on base: no reader to patch) | 76dff19 | test_algebra_portals_viz_closeout_gaugino_status.py |

Edited tests: test_algebra_portals_viz_closeout_gaugino_status.py, the sigma test replaced (it could not fail on the old code).
