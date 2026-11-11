# build-fresh (XB) progress

## Close-out

| id | what was done | commit | test |
|---|---|---|---|
| XB-01 | `canonical_values`: H0 computed at access by `dependency_resolver._h0_local` (FormulasRegistry.calculate_h0_local), NOT_EVALUABLE off the path in force, form text built from the registry; tau_p read only from the output directory's artifact, NOT_EVALUABLE with no artifact, raises on missing seed or tau_p rows; `get(symbol)` builds that entry only | (this commit) | `tests/programme/test_build_fresh_canon.py` |

## Existing tests edited
- `tests/programme/test_path_core_review.py::test_artifact_seed_rows_missing_raise`: asserted
  that H0 reads the artifact seed rows (the defect XB-01 removes); now asserts the same raise on
  tau_p, the artifact-backed entry, with an artifact in a temporary output directory.

## Downstream
- `tests/test_de_plane_gate.py`: 5 failures (wa/w0 plane chi2 values). It reads only `B3` from
  `canonical_values`, which XB-01 does not change; not caused by XB.
