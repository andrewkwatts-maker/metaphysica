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
