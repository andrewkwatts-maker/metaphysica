# Wave A close-out (2026-11-11)

Wave A (workflow wf_47affa26-c1a, base 355bfd9, head 205b1f4) handled 149 items in four lanes:
path-core 55, validation-data 43, actions-generic 6, algebra-portals-viz 45. Each lane was
reviewed against its brief and repaired once. This file lists what is still open, who takes it
in the close-out, what moves to a later wave, and what the owner must decide.

## Gate
`main` merges when a fresh clone passes what CI runs, in CI's order:
`python -m metaphysica.build --fast --out .` and then `pytest tests/`. CI on `main` was green at
06d9671 and is red at b820864 (run 42883161957): the build halts at "Build validation
statistics". The planner runs both commands in a clone outside the repo; lanes never run a
build or the full suite (rule 8 of `FIX_BRIEFS.md`).

## Rules for a close-out executor
The twelve rules of `FIX_BRIEFS.md` bind. Differences:
- Your work list is your lane's section below. Each item has an id; nothing else is in scope.
- Your owned files are the lane's set in `FIX_BRIEFS.md` plus the files your section grants.
- Progress goes under a "Close-out" heading in `docs/plan/programme/progress/<lane>.md`, same
  table columns, real commit hashes.
- An item marked "wave D" or "owner" is recorded, not worked.
- An existing test that asserted a defect may be edited; every such edit is listed in progress
  with its reason.

## XB build-fresh (planner-driven, runs before XV)
Fresh build at 205b1f4: a clone with an empty output directory, `python -m metaphysica.build
--fast --out . --keep-going`, 401 s, 26 failed steps. Four causes; the other failures follow from
the first (no `parameters.json`, no `formulas.json`).

Owned for XB only: `simulations/core/canonical_values.py`, `generators/generate_statistics.py`,
`generators/headline_stats.py`, `simulations/PM/validation/statistical_rigor_validator.py`,
`generators/generate_path_ranking.py`, `data/path_ranking.json`, `build.py` (the statistics and
path-ranking steps only), and the tests of those files. A fix that needs another file is
reported as blocked with the file and the reason; it is not edited.
The executor never runs a build. The planner rebuilds in the clone after each commit and passes
back the tracebacks of the steps that still fail.

| id | sev | where | what to do |
|---|---|---|---|
| XB-01 | critical | `core/canonical_values.py` `_h0_entry`, `_tau_p_entry`, `_not_evaluable`, `canon`, `get` | `canon()` builds every entry, and the H0 and tau_p entries read the parameter artifact, so every reader of CANON raises `KeyError: 'topology.elder_kads is not in the parameter artifact'` on an empty output directory: "Run candidate closure gate" (`candidate_closure_gate.py:210`), "Run all simulations" (the step that writes the artifact), "Emit canonical-value rulings", and nine source checks in "Report executable forks". Fix: (a) H0 is computed at access by the one function that computes `cosmology.H0_local`, `FormulasRegistry().h0_local` (wrapped by `dependency_resolver._h0_local(b3)`, which raises off the path in force): no second formula, no artifact read. A topology that is not the path in force gives NOT_EVALUABLE with that reason. (b) tau_p stays artifact-backed. No artifact in the output directory gives a NOT_EVALUABLE entry (value None, note "no parameter artifact in the output directory"); an artifact that exists but lacks the seed rows or the tau_p row still raises. (c) `get(symbol)` builds that symbol only. Tests: with `METAPHYSICA_OUT` pointing at an empty temporary directory, `canon()` returns, H0 equals `FormulasRegistry().h0_local`, tau_p is NOT_EVALUABLE; with an artifact that lacks the row, tau_p raises. |
| XB-02 | critical | `generators/generate_statistics.py`, `generators/headline_stats.py`, `build.py:194,373` | The first "Build validation statistics" pass runs before the rigor validator and needs the rigor report: this is the failure that turned CI red on `main` (`headline_stats: missing artifact statistical_rigor_report.json`). Fix: an explicit first pass (`generate_statistics --pre-rigor`, named in the build step): gate counts only, it never reads a rigor report even when one is present, and the fit keys carry `NOT_AVAILABLE`. The second pass (no flag) requires this build's rigor report and raises without it. With XV-08: one named sigma source, no four-source fallback, a failed load raises. First list the steps between the two passes that read `framework_statistics` and confirm none of them needs a fit key; if one does, report it instead of guessing. Tests: both passes on a temporary directory, with and without the report. |
| XB-03 | high | `statistical_rigor_validator.py` `calculate_p_value_with_edof` (near 342), `generate_report` | `ZeroDivisionError` when there are no scored rows. Fail early with a message that names the missing input. Test it. |
| XB-04 | high | `data/path_ranking.json`, `generate_path_ranking.py` | The committed ranking is from 137dd42: it fails the contract wave A added (`verdict`, `unranked`, `not_evaluated`, `option_effects`) and its scores predate the wave A scoring fixes. A sweep is not run in wave A. `git mv` the file to `docs/plan/programme/stale/path_ranking_137dd42.json` (kept, not published); the publish step then skips with its logged line. Update any test that pins the committed file, listing each edit with its reason. Regeneration by `python -m metaphysica.testground` is a wave D item (P3 sweep artifacts). |
| XB-05 | - | "Report executable forks" | Exit 1 with "9 fork(s) could not be checked against their source": the source readers import `CANON`, so this follows XB-01. Confirm after XB-01 from the planner's rebuild; no edit expected. |

## XV validation-data
Granted: `src/metaphysica/simulations/PM/cosmology/dark_energy.py` (the wa rows near 1276-1295
only). Runs after XB is green: XB edits `generate_statistics.py`, `headline_stats.py` and
`statistical_rigor_validator.py` first, and XV-08 is done there.
| id | sev | where | what to do |
|---|---|---|---|
| XV-01 | high | `PM/cosmology/dark_energy.py:1276-1295` | VD-21: the scored row is `cosmology.wa_derived` with a typed 0.22. Score it with `get_desi('wa').uncertainty_toward(pred)`; test the scored row's uncertainty; correct line 7 of the progress file. |
| XV-02 | medium | `generators/headline_stats.py:78-82` `_fit` | p_value from `summary.p_value_n_dof`, dof from the row count n, so the published p-value matches the verdict. A missing key raises. |
| XV-03 | medium | `validation/statistical_rigor_validator.py:391` | `summary.status` and the headline p-value come from the plain chi-squared over the scored N; EDOF stays as a labelled side figure, never the verdict. |
| XV-04 | medium | same file, 168, 180, 230, 265-272, 343 | Docstrings match the code: no "chi_sq~0.23 TOO_GOOD", no reference to deleted functions. |
| XV-05 | medium | `calculate_p_value_with_edof` (92 lines), `falsification_oracle.evaluate_risk_profile` (175) | Split to 60 lines or fewer. `generate_72_certificates.py` (984 lines) and `hard_certificate_audit.run_hard_audit` (189): wave D, record. |
| XV-06 | medium | `falsification_oracle.py:106`, `information_bottleneck_distiller.py:15,630,703` | "M27 topology", "Code-Theoretical Integrity VERIFIED", "OPPOSITE of overfitting": replace with wording built from the registry status. |
| XV-07 | medium | `falsification_oracle.py:193-198,261,468,479` | 2025 BabyIAXO dates listed as upcoming: label them unconfirmed with `source_unverified`, add to "Data to confirm". |
| XV-08 | medium | `generators/generate_statistics.py:62-70,329-349` | One named sigma source; a missing file or a failed load raises. Done together with XB-01. |
| XV-09 | medium | `certificate_gates/core.py:55-130` | C003 and C002 take expected values from the path helpers; docstrings derive their numbers. |
| XV-10 | medium | commit a08c652 | List in progress every existing test whose assertions were removed or edited, with the reason; restore any assertion that did not assert a defect. |
| XV-11 | low | `statistical_rigor_validator._adapt_validation_rows` | Used only by tests: use it in production or remove it with its tests. |
| XV-12 | low | `headline_stats.gate_summary` | The formula text is built from the computed counts. |
| XV-13 | low | `adversarial_axiom_tester.py:217`, `generate_72_certificates.py:48,766` | Stale comments (energy 2.0 per bridge, 288-root manifold, typed G12 numbers). |
| XV-14 | low | `tests/programme` test_c003, `beacon_two_time_bulk_accounting` | test_c003 varies b2 through `forced()`; the beacon gets an input that can fail. |
| XV-15 | low | `results.py` STOCHASTIC | Refers to the removed `/jacobian_analysis` key. |

## XG actions-generic (runs first in the algebra slot)
| id | sev | where | what to do |
|---|---|---|---|
| XG-01 | medium | `actions/field_equations.py:11-12,135-160` | `vacuum_potential` flags only potential terms with 0 or 1 scalar factors (those spoil phi = 0); the docstring says so. Passing control m^2 phi^2, failing control a linear term. |
| XG-02 | low | `actions/zero_modes.py:26,578` | Document SU2 as accepted by `chiral_index` only; name `chiral_index` in the module docstring; build the message from `K3_DIM`. |
| XG-03 | low | `actions/spinors.py:66-70` | Docstring: the check assumes the hermitian form at one time and ignores holomorphic masses; P4b replaces it. |
| XG-04 | low | `actions/field_equations.py:68,72` | Use `model.HERMITIAN`, not the literal. |
| XG-05 | low | progress file | Row P4a-3 commit is 74ce43c; note that the `slow` marker is not deselected and that the tests live in `tests/actions/`. |

## XA algebra-portals-viz
| id | sev | where | what to do |
|---|---|---|---|
| XA-01 | medium | `PM/support/complete_residue_registry.py:1726` | Section 2.3 types "~2x10^17 GeV"; the computed M_GUT_eff is 9.27e16. Use `pt['eff']`; add the typed form to the strings the proton-text test rejects. |
| XA-02 | medium | `PM/algebra/clifford_unification.py:224` | The FALSIFIED row's description types "Computed 0.408": build it from `run()`. Test it. |
| XA-03 | low | `clifford_unification.py:267` | A TAB plus "exttt{" where `\texttt{` lost its backslash. Test that the row starts with `\texttt`. |
| XA-04 | low | `visualizations/_retired.py`, `stability_heatmap.html` | `paper_figures` is called by no builder: call it where the plot list and the index are built (inside `visualizations/**`), with a test that fails without the call. Move the tracked stale `stability_heatmap.html` and its data file beside the retired figures; do not delete them. |
| XA-05 | medium | `PM/algebra/gaugino_condensation.py` formula A4.3 | Category FALSIFIED, as its description and the sibling formula say. One status per claim. |
| XA-06 | medium | `clifford_unification.get_section_content` | Typed g2_inv, rot_err, checks_passed, all_pass: feed the section from `run()`; test that a changed run value changes the text. |
| XA-07 | medium | `complete_residue_registry.py:1267-1268,1333,565` | Dm2 terms and the M_Pl text and row from the loader and `RealWorldData.PLANCK_MASS`. |
| XA-08 | medium | `PM/algebra/qec_golay_bridge.py` | b3 and the classification text from computed values (the computed class is MISMATCH); RETIRE-FROM-PAPER as rule 5 defines it. |
| XA-09 | medium | `visualizations/figure1_m27_decomposition.py` | Read b3 from the registry for the label; fix "24D G2 Core"; rename to `figure1_m26_decomposition.py` with `git mv` when no file outside the lane imports it, else record the importer. |
| XA-10 | medium | `PM/portals/alp_portals.py` | Planner ruling: a calibrated row is not scored in chi2. The photon coupling stays compared with the stellar bound in a bound check that reports FAIL (the failing number stays visible). One bound, read from the data loader, in both the value and the section text; flag it `source_unverified` for P5. |
| XA-11 | low | `complete_residue_registry.get_formulas` | Two statements sit above the docstring: move them below it. |
| XA-12 | low | `tests/test_eml_fallback_is_import_only.py` | Fixture values from the path readers, not typed. |
| XA-13 | low | progress file | IDENTITY is the accepted status for a row true by construction (rule 4; path-core uses it for the qed rows). Correct the "no new status" note; the review-round commit is f23f5d7. |
| XA-14 | low | `tests/programme` | Add a 196,560 minimal-vector count test; mark misc-45 as a verification test in progress. |
| XA-15 | low | `PM/algebra/neutrino_algebraic.py` | Module-level `_B3 = 24` and theta13 9.59 degrees constants: read the path, or label them off-path as the delta_CP text does. |
| XA-16 | - | oversize functions | Wave D: the prose functions that grew (neutrino `get_formulas`, `get_section_content`; residue `get_formulas`; figure 2; alp `run`) and the moved functions in `leech_decomposition.py`. Do not grow them: new logic goes in helpers. |

## XP path-core
Granted: `src/metaphysica/theories/pm/ranking.py` (`_consistent` only),
`tests/test_frozen_seed_literals.py`, `docs/FROZEN_SEED_LITERALS.md`.
Not yours in the close-out (XB owns them): `core/canonical_values.py`,
`generators/generate_path_ranking.py`, `data/path_ranking.json`, `testground/`. XP-06 is worked
last.
| id | sev | where | what to do |
|---|---|---|---|
| XP-01 | medium | `core/demon_lock_guard.py:209-226` | `verify_tzimtzum_fraction` expects a typed 23/24: read sigma_T from the `dark_energy_betti` fork as `verify_parity` does. |
| XP-02 | medium | `core/FormulasRegistry.py:79,1399` | `FROZEN_PLEROMA = 24` behind lambda_S has no status: give the lambda_S row the registry status for a frozen ansatz input and move the misplaced comment. No new fork until the owner rules (see Owner decisions). |
| XP-03 | medium | `config/parameters/fitted.py:119-156` | T_topological -1.0 and T_OMEGA -0.875 are TCS #187 results while `geometry.py` computes -1.568: label them with the `tcs187_only` pattern of 205b1f4; list live consumers under "Needs other lane". |
| XP-04 | low | `demon_lock_guard.py:300`, `base/registry.py:1102` | Docstrings quote 71.55: no seed-24 value in either. |
| XP-05 | low | `FormulasRegistry.py:324,333,1286`, module docstring, `__init__`, symbol-map comments | Comments quote 576/4 = 144, 72/24 = 3 and b3 = 24 (rest of core-paths-12): path-generic, or labelled seed_24. |
| XP-06 | low | `core/switch_search.py:638` | `search()` is 83 lines: split the ERRORED handling into a helper. |
| XP-07 | low | `verify_parity` | An identity: keep it out of every preflight count and score; test the count. |
| XP-08 | high | `theories/pm/ranking.py` `_consistent` | Swallows every error: map the ERRORED state to missing and let anything else raise. Test both. |
| XP-09 | high | four audit tests | Run each in the foreground, one command per file: `tests/test_frozen_seed_literals.py`, `test_sterility_audit.py`, `test_value_context_audit.py`, `test_seed_blindness.py`. A failure caused by a wave A fix: for the frozen-seed test record each changed literal in `docs/FROZEN_SEED_LITERALS.md` first, as that test's own rules require, then repin; for the others fix the cause when it is in your files, else record it. |
| XP-10 | medium | `base/established.py`, `FormulasRegistry` formula data, config | Findings other lanes could not reach: sim-algebra-misc-12, sim-algebra-misc-24, VD-19 (status of `geometry.m_KK_central`), `topology.orientation_sum`. Read each audit row and handle it. |
| XP-11 | medium | `config/constants.py`, `K_MATCHING` | The #187 Hodge numbers (4/0/68) and the TCS-only `K_MATCHING = 4` still feed the live registry: label with `tcs187_only`; list the live consumers (`g2_geometry.py`, `ckm_matrix.py`, `proton_decay.py`, `appendix_c_derivations.py`) under "Needs other lane". |
| XP-12 | low | `FormulasRegistry.generate_named_constants_json`, `core/sync_docs.py` | Seed-24 text in the named-constants output: built from the path. |
| XP-13 | low | progress file | Commit columns: R5 acebadd, R6 7808641, R7 205b1f4. |

## Later waves (recorded, not worked now)
| item | goes to |
|---|---|
| core-paths-17 (four action fork readers), sim-algebra-misc-11 (`field_dynamics/orch_or_geometry.py`) | L4, wave B |
| core-paths-28 (`topology.critical_dim` in `PM/geometry/modular_invariance.py`), sim-algebra-misc-17 (`leech_partition.py`), VD-02 (`geometric_anchors.py`), sim-algebra-misc-40 (`algebra.freudenthal_quartic` readers) | L2, wave B |
| sim-particle-23 (`PM/qed/_triple_track.py`), `PM/particle/higgs_mass.py:1489,1495` (B3 now reads 43), `PM/qed/compton_wavelength.py` (old CODATA value), NuFIT rows that use the mean | L5, wave B |
| sim-algebra-misc-34 (`appendix_clifford_algebra.py` names a removed row), `constraints_count` in `abstract.py` | L8, wave C |
| core-paths-42 and the `path_ranking.json` sweep, VD-06/08/11/12/24/25 (rows from `generate_validation_certificates`), VD-35 (`run_all_simulations.py` imports `unitary_filter_legacy`), the `run_all_simulations` except-wrap, sim-algebra-misc-42 (`Constants/ad-hoc`), `tests/test_derivation_chains.py` (3) | L9, wave C |
| `constraints_count` in the JS loader | L10, wave C |
| sim-algebra-misc-08 (`docs/claude-context.md` Facts) | planner, after the rebuild |
| core-paths-19/31/36/37, sim-algebra-misc-37/38, XA-16, the XV-05 leftovers | wave D size splits |

## Owner decisions (open, none blocks the close-out)
1. CANON claim rows: 0.0994 eV, 2.118e16 GeV and 4.5 TeV are typed and match no artifact row
   (nearest: `neutrino.sum_masses` 0.1020 DIAGNOSTIC, `gauge.M_GUT` 6.32e15,
   `geometry.m_KK_central` 5.0). Which row is the claim?
2. GUT scale (register 2.2): `M_GUT = 2e16` stays typed in the algebra lane until ruled.
3. Gate G53 (1/24): is the 24 b3 or the 24 space dimensions?
4. lambda_S = sqrt(24): stays frozen, or follows b3?
5. `BULK_PLANCK_POWER`: delete, or keep (a test pins it)?
6. Compton wavelength: accept the CODATA 2022 value 2.42631023538e-12 m everywhere?
7. Gates COSMO-013/014/015 and TOPO-023 hard-code b3 = 24 and are labelled off-path: retire them
   or re-derive them on the path?
8. `b3_clusters` adoption is marked stale at every Joyce seed: withdraw it?
