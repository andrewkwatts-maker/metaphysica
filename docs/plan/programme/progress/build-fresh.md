# build-fresh (XB) progress

## Close-out

| id | what was done | commit | test |
|---|---|---|---|
| XB-01 | `canonical_values`: H0 computed at access by `dependency_resolver._h0_local` (FormulasRegistry.calculate_h0_local), NOT_EVALUABLE off the path in force, form text built from the registry; tau_p read only from the output directory's artifact, NOT_EVALUABLE with no artifact, raises on missing seed or tau_p rows; `get(symbol)` builds that entry only | 0348545 | `tests/programme/test_build_fresh_canon.py` |
| XB-02 | not started (executor stopped at the context limit); findings below | - | - |

## XB-02 handoff (findings, no code edited yet)
- Steps between the two passes (build.py 194 and 373) that read `framework_statistics`: none by
  name. Generic parameter copiers there (generate_js_constants maps a fixed list without
  statistics; interactive_html, named_constants, validation_certificates, eml_param_crosscheck)
  already tolerate string rows (`status`, `open_gate_ids`). No step needs a fit key.
- Plan: `headline_stats.pre_rigor_headline(certs_path)` (gate counts, fit keys = NOT_AVAILABLE,
  never reads the rigor report); `generate_statistics(pre_rigor=False)` + `--pre-rigor` flag on
  the build.py 194 step; the post pass reads only `statistical_rigor_report.json` scored rows
  (keep the name `_collect_sigmas`, a writeback test greps it), raising when missing or empty;
  `load_json_file` raises; drop the gates/param-cert/parameters sigma extractors.
- Existing tests to edit: `tests/test_statistics_fail_early.py` expects RuntimeError "earlier
  build step failed" from the fallback chain; becomes FileNotFoundError naming the rigor report.
- Needs other lane: `simulations/run_all_simulations.py:3863` calls `generate_statistics()`
  (post pass) before the rigor report exists and swallows the raise as [WARN]; it should call
  the pre-rigor pass or drop the call.

## Existing tests edited
- `tests/programme/test_path_core_review.py::test_artifact_seed_rows_missing_raise`: asserted
  that H0 reads the artifact seed rows (the defect XB-01 removes); now asserts the same raise on
  tau_p, the artifact-backed entry, with an artifact in a temporary output directory.

## Downstream
- `tests/test_de_plane_gate.py`: 5 failures (wa/w0 plane chi2 values). It reads only `B3` from
  `canonical_values`, which XB-01 does not change; not caused by XB.
