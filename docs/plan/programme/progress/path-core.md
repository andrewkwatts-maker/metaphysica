# L1 path-core progress

Round 1 (2026-11-11). Test file: tests/programme/test_path_core_topology.py (T).
tests/test_canonical_values.py was edited: its subject canonical_values.py is
owned by this lane and it asserted the defect (B3 == 24, w0 DERIVED, H0 typed).

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
| core-paths-11 | config/parameters/geometry.py:38-48, fitted.py | fixed (PathValued; TCS187 rows retired) | this commit | T::test_config_chirality_reads_the_path |
| core-paths-17 | variants/adopted.py action forks | blocked: brief keeps the four action forks for L4 wave B | - | - |
| core-paths-28 | topology.critical_dim | blocked: registered in PM/geometry/modular_invariance.py (L2) | - | - |

## Downstream
- None: T, tests/test_canonical_values.py, tests/testground, tests/test_dependency_resolver.py: 588 passed, 1 skipped.

## Needs other lane
- L2: move the b3_path seed table into core; critical_dim in modular_invariance.py.
- L2/L3: PM/qed/compton_wavelength.py still types CODATA 2018 2.42631023867e-12 labelled 2022.
- L3: dark_energy modules use live b3 while dark_energy_betti adopts frozen n = 24.
- canonical_values importers outside L1: generate_prose_drift_audit.py (all_canonical), tests/test_de_plane_gate.py:35; candidate_closure_gate.py and de_plane_gate.py already import at call time.

## Data to confirm
- CODATA 2022 electron Compton wavelength 2.42631023538(76)e-12 m (was the 2018 value).

## Next round
- sim-particle-01 (Avogadro qed tautology rows: identity status, unscored); core-paths-02/-03 (ranking, output_effect).
- core-paths-15/-16 (adopted.py metric fallback raises; readers measure or declare).
- config/parameters/geometry.py EFTValidity, G2SpinorGeometry, TCSTopology and fitted.py AnomalyCancellation still type B3 = 24 / CHI_EFF = 144 / N_GENERATIONS = 3.
- FormulasRegistry: CP-13 (`self._b3 = 43` ImportError fallback, `return 144`); verify_parity typed 1.64034 fails at b3 = 43.
- CANON still types tau_p, sum_mnu, M_GUT, MKK; read the artifact.
- Medium/low: CP-18..25, 31, 33..39, 41, 44, 45, sim-particle-23, core-paths-26.
