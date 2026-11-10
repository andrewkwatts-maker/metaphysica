# validation-data (L7) progress, rounds 1-5

| id | state | note |
|---|---|---|
| VD-01,03,14,15,26,38 | fixed | one scored row per observable (observables.py, fit_partition.py); tuned rows unscored; three fit numbers from rows |
| VD-07,16,28,29,30 | fixed | gate_summary from registry; counts share chi2 N; stale literals gone |
| VD-21,22,05 | fixed | loader raises on missing error, keeps asymmetric errors; NuFIT flagged source_unverified |
| VD-25 | partly | sigma nulled in report block; source row is in generate_validation_certificates |
| VD-02,13,24 | blocked | other lane owns the file |

| VD-04 | falsification_oracle.py | fixed | round 2 | test_validation_data_oracle.py; ALP prose built from rows, row_status INPUT_ANSATZ, "FALSIFIED" note dropped, CAST 6.6e-11 flag (value to confirm) |
| VD-17,18,20 | falsification_oracle.py | fixed | round 2 | version from registry, nm verdict with units, 1e-4 strength literal removed, b3 = 24 text removed |
| VD-19 | falsification_oracle.py | partly | round 2 | verdicts say benchmark; registry status of geometry.m_KK_central is another lane |
| VD-09 | CERTIFICATES.py C003 | fixed | round 2 | chi_eff = 48 (b2/4) from seed_values; 6*b3 dropped |
| VD-10 | consistency_beacons.py | fixed | round 2 | pure Cl(24,2) check |
| VD-31 | geometric_pipeline.py | fixed | round 2 | observables stage and its tests deleted (tests/test_geometric_pipeline.py edited: asserted the defect) |
| VD-32 | information_bottleneck_distiller.py | fixed | round 2 | DERIVED strings replaced by "retired off-path reading" |
| VD-33 | adversarial_axiom_tester.py | fixed | round 2 | b3 from seed_values(resolve_path()); k_geometric_base 0.9514 stays labelled tuned |
| pipeline-13 | generate_72_certificates.py | fixed | round 2 | registry load raises |
| VD-06,08,11,12 | report rows | blocked | | rows are made by generate_validation_certificates / simulations (not owned) |

| pipeline-12 | generate_72_certificates.py | fixed | round 3 | test_validation_data_gate_certificates.py; registry-tier result text built from the checks, `result_basis` field, G12 0.68 sigma text removed |
| pipeline-14 | generate_72_certificates.py | fixed | round 3 | anchors read via new ExperimentalDataLoader.get_value; only CKM row-1 unitarity stays literal, flagged source_unverified |
| VD-23 | codata_2022.json, pdg_2024_values.json | partly | round 3 | three M_Pl errors flagged source_unverified (values not edited) |
| VD-36 | nine dead modules | fixed | round 3 | deleted after grep (no importer; run_all_simulations globs simulations/v16 only); test_dead_modules_are_gone |
| VD-37 | GATES_CERTIFICATES.json | refuted | round 3 | stamp is VERSION_SHORT from config; only the artifact is old, a rebuild (not allowed here) refreshes it |
| VD-35 | unitary_filter(_legacy) | blocked | round 3 | run_all_simulations.py (not owned) imports unitary_filter_legacy |
| VD-27 | generate_statistics.py | partly | round 3 | write-back to parameters.json extracted, `except Exception` removed (raises); the split of the 1100-line validator and moving the write-back to another generator not done |

| VD-27 | generate_statistics.py | fixed | round 4 | test_validation_data_statistics_writeback.py; write-back is a table (_parameter_rows), generate_statistics split (_collect_sigmas, _build_statistics), every function <= 60 lines; rigor-validator class split still open |
| pipeline-39 | generate_statistics.py | fixed | round 4 | no "72" in EML text or print, totals from the headline tally; declarative MAJORITY_VERIFIED status block removed (it was overwritten by the headline verdict) |
| pipeline-11 | generate_statistics.py | fixed | round 4 | one sigma source chosen in _collect_sigmas, N shared with chi2; no declarative status |
| VD-34 | CERTIFICATES.py | partly | round 4 | test_validation_data_certificate_split.py; 2070 lines split into 7 mixins in PM/validation/certificate_gates/ (gate bodies unchanged); gate functions of 60+ lines (g81 145) not yet shortened |

| VD-34 | certificate_gates/*, CERTIFICATES.py, generate_72_certificates.py | fixed | round 5 | test_validation_data_gate_functions.py; every gate function and the generator's create_certificate, main <= 60 lines (verdict/result helpers, shared honesty constants, table-driven run_all _SECTOR_RUN_ORDER, G72 seal and summary builders); create_certificate output identical for all 72 gates; docstring retirement history trimmed in the gates touched |
| VD-27 | statistical_rigor_validator.py | fixed | round 5 | file is 442 lines, Jacobian/correlation code gone (round 1), rows -> chi2 -> p-value -> report methods separate; no further split needed |

Downstream: tests/test_derivation_chains.py (3 failures) are data/parameters.json vs derivation_chain/parameter_ledger/kill_switch_rows, none owned here; gates 12,19,26,48 now read COMPUTED_FAIL with data-file anchors (sigmas changed: 12 is 22.83, 48 uses DESI DR2 -0.752, 19 and 27 use NuFIT IO); results.py STOCHASTIC refers to removed "/jacobian_analysis"; AutoGenerated/statistical_rigor_report.json lacks scored_rows until rebuilt.
Needs other lane: constraints_count literal (abstract.py, JS loader).
Data to confirm: CKM row-1 unitarity 0.9985+/-0.0007 (no data file); NuFIT IO theta_13 8.63 vs old literal 8.58 (that was the NO value); M_Pl uncertainties; primary row choice for n_s, w_eff, PMNS theta_13 groups; NuFIT 6.0 source; DESI thawing w0 957 source.
Next round: hard_certificate_audit.run_hard_audit (189 lines, simulations/validation/audit), VD-35 via run_all_simulations owner, VD-02,13,24 and VD-06,08,11,12 (rows made outside this lane). Lane is otherwise complete.

## Review
| defect | action | commit | test |
|---|---|---|---|
| critical: falsified gaugino_cabibbo_* and theta13_derived grouped as duplicates | removed from OBSERVABLE_GROUPS; they are scored rows of their own, so all and excluding-falsified differ and withdrawn_rows lists them; live-report duplicate test now allows a shared reference only for FALSIFIED rows | review round | test_falsified_candidates_are_not_grouped_as_duplicates |
| high: constraints_count literal 1 in _build_statistics | key removed from generate_statistics (its meaning, one Higgs constraint, is abstract.py/JS loader, another lane) | review round | test_no_constraints_count_literal_in_statistics |
| high: tally_gates counted unexecuted gates as locked/open | locked/open count executed gates only; unexecuted go to new `not_run` (headline `gates_not_run`, framework_statistics `not_run_count`); test_gate_summary edited (asserted the defect) | review round | test_unexecuted_gates_are_not_run_not_locked |
| high: G79 ImportError fallback returned LOCKED | fallback removed, ImportError raises | review round | test_g79_has_no_import_fallback_that_locks |
| high: `or default` for geometry.elder_kads (24) and sum_m_nu_upper (0.12) | new `_require_param` raises KeyError; used in core, cosmo, lattice; gate test supplies the key | review round | test_gates_have_no_default_for_missing_registry_keys |
| high: VD-21 asymmetric error used only in the anchor helper | dark_energy_thawing scoring (run and parameter definitions) uses ExperimentalValue.uncertainty_toward via loader; only DESI wa is asymmetric (0.23/0.20). Other asymmetric sources (NuFIT rows built in established.py via .uncertainty) still use the mean: VD-21 stays partly | review round | test_asymmetric_error_is_taken_on_the_prediction_side |
| high: ALP status IMMINENT_TEST above CAST bound | status EXCLUDED_BY_CURRENT_BOUND when mass in window and coupling >= CAST; projected status kept as projected_sensitivity_status | review round | test_alp_status_follows_the_current_bound_not_the_projection |
| high: test_edof_is_labelled_ansatz passes on base | kept as a label test; behaviour change tested instead: report summary.status (and headline verdict) now come from the row-count p-value, EDOF verdict is status_edof_ansatz; fails on base (no such key) | review round | test_headline_verdict_is_not_the_edof_ansatz |

Review notes: headline p_value and dof still read the EDOF block (the stale AutoGenerated artifact lacks summary.p_value_n_dof); a rebuild plus switching p_value to summary.p_value_n_dof is next round. Artifacts need a rebuild (not allowed here) for headline verdict, withdrawn rows and not_run to appear.
