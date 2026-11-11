# Progress: P4a actions-generic

Items are the deliverable bullets of FIX_BRIEFS.md "P4a actions-generic" (no audit finding
names a file of `src/metaphysica/actions/**`; sim-action-gauge rates the package KEEP).

| id | file:line | state | commit | test |
|---|---|---|---|---|
| P4a-1 spinor_bilinears | actions/spinor_bilinears.py | fixed | f6ad950 | tests/actions/test_spinor_bilinears.py |
| P4a-2 Term.bilinear + check_spinor_bilinears | actions/model.py, spinor_bilinears.py, spinors.py | fixed | f6ad950 | tests/actions/test_spinor_bilinears.py |
| P4a-4 surfaces | actions/surfaces.py | fixed | b5169c0 | tests/actions/test_surfaces.py |
| P4a-6 chiral_index | actions/zero_modes.py:115 | fixed | b5169c0 | tests/actions/test_chiral_index.py |
| P4a-5 volume_modulus | actions/controls/volume_modulus.py | fixed | 126c74e | tests/actions/test_volume_modulus.py |
| P4a-3 field_equations + vacuum_checks | actions/field_equations.py | fixed | 74ce43c | tests/actions/test_field_equations.py |

Notes:
- `weyl_bilinears` rule equals the oracle at (1,1) (3,1) (5,1) (7,1) (9,1) (2,2) (4,2) (6,2)
  (8,2) (10,2) and (24,2) (marked slow, about 2 s), for both choices of C.
- `check_spinor_bilinears` is not wired into `dimensions.check_action`, so the PM ladder is
  unchanged in this wave; `check_spinor_terms` keeps the one-time rule with a docstring note.
- A `bilinear` of None means the hermitian Psi-bar form.
- `chiral_index` also accepts holonomy "SU2" (K3, index 2) so `chirality_check` has a case
  that holds; flat tori and G2 give 0 and fail it. `zero_modes` itself still takes flat, G2.
- `volume_modulus`: omega from Euler-Lagrange matching on a minisuperspace (a(t), b(t)) metric,
  checked n = 1..9; gamma_PPN = (1 + omega)/(2 + omega). `ppn_check(name, n, bound)` takes the
  Cassini bound from the caller (P4b reads it from its data loader; no data in this package).
- `field_equations` covers c R plus one kinetic term per field and raises for any other term
  (mass, potential, interaction, open L_bridge/V): call it on the adopted R + kinetic action
  only. A Weyl kinetic term that vanishes in the signature raises. `vacuum_checks` checks
  R_MN = 0 per factor (the design names `ricci_scalar`; the tensor is the field equation and
  the scalar is reported as measured), matter fields zero, no potential term.
- Acceptance: tests/actions 122 passed; tests/test_master_ladder.py 16 passed (ladder unchanged).
- The lane's tests live in `tests/actions/`, not `tests/programme/`. The (24,2) oracle test is
  marked `slow`, but `slow` is not deselected (pyproject `addopts` has no `-m`), so it runs in
  every `pytest tests/`.

## Close-out (WAVE_A_CLOSEOUT.md "XG actions-generic")

| id | file:line | state | commit | test |
|---|---|---|---|---|
| XG-01 vacuum_potential degree | actions/field_equations.py:139 `_spoils_vacuum` | fixed | (this commit) | tests/actions/test_actions_generic_closeout.py |
| XG-02 SU2 scope, K3_DIM message | actions/zero_modes.py:14-17,29-31,74,130,134 | fixed | (this commit) | tests/actions/test_actions_generic_closeout.py |
| XG-03 one-time rule docstring | actions/spinors.py:65 | fixed | (this commit) | tests/actions/test_actions_generic_closeout.py |
| XG-04 HERMITIAN constant | actions/field_equations.py:72 | fixed | (this commit) | tests/actions/test_actions_generic_closeout.py |
| XG-05 progress corrections | this file | fixed | (this commit) | none (doc) |

- XG-01: a potential term (scalar factors only, no derivative) fails `vacuum_potential` iff it
  has 0 or 1 factors; m^2 phi^2 and phi^4 pass. XG-02: line 578 of the brief does not exist
  (file is 152 lines); the literal messages were at 71, 127 and 138, now built from G2_DIM, K3_DIM.
- No existing test was edited. tests/actions: closeout 5, field_equations 7, spinors 15,
  chiral_index 8, zero_modes 4 passed.

## Downstream
None.

## Needs other lane
- P4b: call `check_spinor_bilinears` from the master ladder and set `bilinear="holomorphic"`
  on the A26 kinetic term for the `weyl_holomorphic` option.

## Data to confirm
None.

## Next round
None: all six deliverables and XG-01..05 are done. P4b binds them in `simulations/PM/gauge/`.
