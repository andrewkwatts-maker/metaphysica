# Progress: P4a actions-generic

Items are the deliverable bullets of FIX_BRIEFS.md "P4a actions-generic" (no audit finding
names a file of `src/metaphysica/actions/**`; sim-action-gauge rates the package KEEP).

| id | file:line | state | commit | test |
|---|---|---|---|---|
| P4a-1 spinor_bilinears | actions/spinor_bilinears.py | fixed | f6ad950 | tests/actions/test_spinor_bilinears.py |
| P4a-2 Term.bilinear + check_spinor_bilinears | actions/model.py, spinor_bilinears.py, spinors.py | fixed | f6ad950 | tests/actions/test_spinor_bilinears.py |
| P4a-4 surfaces | actions/surfaces.py | fixed | (this commit) | tests/actions/test_surfaces.py |
| P4a-6 chiral_index | actions/zero_modes.py:115 | fixed | (this commit) | tests/actions/test_chiral_index.py |

Notes:
- `weyl_bilinears` rule equals the oracle at (1,1) (3,1) (5,1) (7,1) (9,1) (2,2) (4,2) (6,2)
  (8,2) (10,2) and (24,2) (marked slow, about 2 s), for both choices of C.
- `check_spinor_bilinears` is not wired into `dimensions.check_action`, so the PM ladder is
  unchanged in this wave; `check_spinor_terms` keeps the one-time rule with a docstring note.
- A `bilinear` of None means the hermitian Psi-bar form.
- `chiral_index` also accepts holonomy "SU2" (K3, index 2) so `chirality_check` has a case
  that holds; flat tori and G2 give 0 and fail it. `zero_modes` itself still takes flat, G2.

## Downstream
None.

## Needs other lane
- P4b: call `check_spinor_bilinears` from the master ladder and set `bilinear="holomorphic"`
  on the A26 kinetic term for the `weyl_holomorphic` option.

## Data to confirm
None.

## Next round
Remaining: field_equations, controls/volume_modulus.
