# Discarded-path coverage audit

**Question asked.** The project's standing rule is that a falsified, withdrawn or
superseded candidate **stays on the books — runnable and labelled — and is never
deleted**. This document tests that rule against the repository: for every
abandoned / withdrawn / superseded / falsified approach, geometry, seed or
derivation route recoverable from the git history and from the tree, does it
survive **today** as a runnable labelled option, or has it been lost?

**Nothing was edited to produce this report.** It is read-only: `git log`,
`git show`, `git diff` and file reads only. No ruling is made here — in
particular `chi_eff_route` and `re_t_adoption` are OPEN and stay open, and this
document does not prefer any of their options.

## What was searched, and the limits of what git can show

- `git log --oneline --all | wc -l` → **50 commits**, on two refs
  (`main` and the current working branch). HEAD is `fb81dfd` (2026-09-23).
- The **root commit is `fedfec8` (2026-09-14)** and it imports the entire tree in
  one go — 971 files, 419,674 insertions. So **every ruling before 2026-09-14
  has no git record in this repository at all**: the 2026-08-19 and 2026-08-31
  bulk rulings, the 2026-09-06 `dark_energy_betti` ruling, the 2026-09-07 Leech
  generator falsification, the 2026-09-08 `lattice_24d` / `g2_construction` /
  `moduli_indexing` forks and the 2026-09-13 `g2_form_convention` fork are all
  visible **only in-tree**, through `CANON[...]["superseded"]`, the fork `notes`
  and `docs/history/`. For those rows the "when/why discarded" column cites the
  in-tree ruling date and the file that carries it, not a commit that does not
  exist.
- Commit messages were searched for `withdraw`, `abandon`, `retire`, `discard`,
  `supersede`, `stale`, `off-path`, `deprecate`, `falsif`, `DO NOT RESURRECT`,
  `no longer`, `removed`, `deleted`; diffs were searched with `git log -S` for
  every approach string named below.
- **Deletion check.** `git log --all --diff-filter=D --name-only` shows that in
  the whole history **no file under `src/` or `tests/` has ever been deleted** —
  the only deletions are three stray Windows cache `.db` files in `90a6e9d`.
  Deleted *functions* number three across 50 commits (`git log -U0` for removed
  `def`/`class` lines): `get_certificates` (`74b0563`), `_check` (`2dfd477`) and
  `_validate_g2_holonomy` (`bfff33e`) — the last is discussed in the table.
- **Fork-option deletion check.** Diffing the option ids in
  `simulations/core/variants.py` between the root commit `fedfec8` and today
  (`comm -23`) returns **nothing in the root that is not still present**:
  23 option ids have been added since the root, none removed.
- `git log -S` on every approach string in the brief — `M^27`, `27D`,
  `(24,1,2)`, `unified time`, `D_crit = 26`, `(7, 24)`, `b_2 = 7`,
  `1/sqrt(b_3)`, `sin2_2theta`, `extra-twisted`, `Kovalev`, `Crowley`,
  `MiniMOG`, `Coxeter-Todd`, `6.Suz`, `chi_eff = 6`, `b_3^2/4`, `37.8527`,
  `196560` — returns the string still present in HEAD in every case.

### Snapshot the verdicts were measured against

`variants.py` was **being modified by another process during this audit**: the
working tree is dirty (`git status`: ` M src/metaphysica/simulations/core/variants.py`,
+146/−7 against `fb81dfd`), the file grew from 94,438 to 104,782 bytes mid-audit,
and a new `dark_energy_betti.b3_live` option dated 2026-09-26 appeared between
two reads. All fork counts below are measured against one snapshot:

- `variants.py` md5 `947b794c7367aa3eac82b8a7468012e5`
- **18 forks, 51 options: 18 ACTIVE, 30 CONSIDERED, 3 DISABLED**
- The `ACTIVE` / `CONSIDERED` / `DISABLED` option-status vocabulary is part of
  the *uncommitted* change; at `fb81dfd` the only distinction was `adopted` plus
  a `priority` integer. The three DISABLED options today are
  `b3_seed.seed_7_joyce`, `b3_seed.seed_19_joyce`, `b3_seed.seed_31_joyce`.

### Which forks can actually execute their options

`grep -rn 'resolve("<fork>")'` over `src/` (excluding `variants.py` itself):

| wiring | forks |
|---|---|
| read by the physics/generator pipeline (11) | `b3_seed`, `n_gen_source`, `g2_form_convention`, `metric_construction`, `joyce_contribution_table`, `twisted_norm_convention`, `flavour_seed_coupling`, `lattice_24d`, `re_t_adoption`, `render_policy`, `theory_uncertainty_policy` |
| read **only** by the audit harness (2) | `b3_origin` (`core/switch_search.py` only), `chi_eff_route` (`core/fork_implications.py` only) |
| **no consumer at all — inert (5)** | `bulk_signature`, `dark_energy_betti`, `g2_construction`, `moduli_indexing`, `face_genericity` |

That table drives most of the `DOCUMENTED_ONLY` verdicts below: **13 options
across those five inert forks are declared, costed and labelled, but selecting
one executes nothing.** `tests/test_variants.py` checks that each fork declares
one adopted option, offers a real choice, states a consequence and matches its
source — it does **not** check that any code reads the fork.

## Verdict vocabulary used

- **RUNNABLE_LABELLED** — the approach itself can be executed today and produce
  its own numbers (a fork option with a live consumer, a published row that is
  recomputed every build, or a function that reproduces the old result), and it
  carries a label saying it is withdrawn / falsified / off-path.
- **DOCUMENTED_ONLY** — described in prose, a `superseded` entry, a fork note or
  a quarantined document, possibly with a live check that it *fails*, but the
  approach cannot be run to produce its own outputs.
- **LOST** — not present anywhere. A rule violation.

## The table

| approach | what it claimed | when/why discarded (commit + date) | represented today? | where (fork id + option id, or file) | verdict |
|---|---|---|---|---|---|
| **27D bulk, `M^27(24,1,2)` sampler-pair** | bulk is 27-dimensional: one shared time plus a (0,2) spacelike "sampler" pair | two-time ruling 2026-08-19, pre-git; retired because it "required both b3+2 and b3+3 as 'forced', shadows summed to 25 != 27, spinor was non-chiral" (`CANON["bulk"]["superseded"]["27"]`, in tree since root `fedfec8` 2026-09-14) | yes, as a superseded entry plus two executable stale-token scanners | `core/canonical_values.py` `CANON["bulk"]["superseded"]["27"]`; `generators/generate_prose_drift_audit.py` `_MIGRATION_TOKENS` (`27D`, `M^27`, `M²⁷`, `(24,1,2)`, `d²⁷X`, `Cl(24,1)`, `27/10`); `generators/generate_terminology_audit.py` `DEPRECATED_PATTERNS`. **Not** an option of `bulk_signature` | DOCUMENTED_ONLY |
| **25D / "(24,1) unified time"** | the (24,1) physics core read as the bulk, with one unified time | same 2026-08-19 ruling: "(24,1) physics-core dimension mislabelled as a bulk" (`CANON["bulk"]["superseded"]["25"]`) | yes, superseded entry + `25D` and `unified time` deprecated patterns; `FormulasRegistry` keeps it as gate G10's `legacy_description` ("Anchors 24D manifold to G(24,1) unified time (v21)") | `core/canonical_values.py`; `generators/generate_terminology_audit.py:42,45`; `core/FormulasRegistry.py:5132`. Note `bulk_signature.25_1` is a *different* claim (26D at (25,1)) | DOCUMENTED_ONLY |
| **`D_bulk = D_crit = 26`** | the bulk dimension *is* the critical dimension | **WITHDRAWN** 2026-08-31 signature ruling: the two-time critical dimension is 27–28 (Bars & Kounnas hep-th/9705205), 26 is the one-time value at (25,1) (`CANON["bulk"]["ruling"]`) | withdrawal recorded; the `+2` identity it rested on is runnable and labelled BROKEN — but the withdrawn claim is **still asserted unlabelled** in five live modules | withdrawal: `CANON["bulk"]["ruling"]`, `PM/geometry/modular_invariance.py:699`; runnable identity: `core/identity_ledger.py` `d_bulk_is_b3_plus_two`, `PM/geometry/b3_path.py` `plus_two_identity_holds`, `core/ruled_divergences.py` `"critical-dimension"`. Unlabelled assertions: `PM/derivations/lagrangian_master.py:124`, `PM/geometry/modular_invariance.py:606,778,851`, `PM/validation/consistency_beacons.py:436,457`, `PM/cosmology/cosmological_constant.py:527` | DOCUMENTED_ONLY |
| **Bars `Sp(2,R)` ghost-freedom appeal** | the second time is ghost-controlled by Bars' Sp(2,R) gauging | **WITHDRAWN** 2026-08-31: "Sp(2,R) gauging removes two dimensions and yields ONE 24D shadow of signature (23,1), not two 13D(12,1) shadows", and "unitary_report.json is a self-declared scaffold that cannot fail" (`CANON["bulk"]["ruling"]`) | withdrawal recorded in CANON only; the appeal itself **still runs unlabelled** and is imported by the build | withdrawal: `CANON["bulk"]["ruling"]`. Live unlabelled: `simulations/validation/unitary_filter_legacy.py` (header "For PM's v21 (24,1) signature theory with Euclidean bridge", `c = 24 + 2 - 26 = 0`, Bars 2006 in References, `DIM_BRIDGE = 2`), mirrored in `PM/validation/unitary_filter.py`; imported at `simulations/run_all_simulations.py:349` | DOCUMENTED_ONLY |
| **The two retired readings of the `+2`** | "two-time (1) + Euclidean bridge (1)"; "2 × Sp(2,R)" | 2026-08-31 ruling: under (24,2) "the only self-consistent reading is 'one time per shadow'; the other two should be retired wherever they appear" | both readings are enumerated in the CANON challenge text; the Euclidean-bridge reading is still **live and unlabelled** in the filter above | `CANON["bulk"]["challenge"]`; live text at `simulations/validation/unitary_filter_legacy.py:15,17,136,175,508,586,644,825` | DOCUMENTED_ONLY |
| **28D at (26,2)** — the four-agent review's recommendation | passes the lattice test (24 ≡ 0 mod 8), matches the Bars–Kounnas critical dimension, admits Majorana–Weyl | not adopted at the 2026-08-31 ruling (option (b) recommended, option (c) taken) | declared as an option with its full cost list, but the fork has **no consumer**, so selecting it changes nothing | `variants.py` `bulk_signature.26_2` (CONSIDERED) | DOCUMENTED_ONLY |
| **26D at (25,1), one time** | the standard bosonic reading, Lorentzian Leech `II_25,1`, passes mod-8 | not adopted 2026-08-31; "abandons two-time entirely" | as above — declared, inert | `variants.py` `bulk_signature.25_1` (CONSIDERED) | DOCUMENTED_ONLY |
| **"`II_26,2 = Leech + U + U` derives the 13+13+2 partition"** | the lattice *forces* two 13D(12,1) shadows plus a 2D shared sector | **RETRACTED** in-tree (CANON `resolution_evidence`, CORRECTION and REFINEMENT 2026-08-20): U has signature (1,1) and cannot be split, so the lattice gives two rank-14 (13,1) pieces; "what is retracted is only the DERIVATION claim" | recorded verbatim, including the trade-off it leaves open | `CANON["bulk"]["resolution_evidence"]` | DOCUMENTED_ONLY |
| **Complex-Leech / Eisenstein `Z[omega]` rank-12 split** | the 12+12 split of Leech comes from the rank-12 Eisenstein Leech lattice | in-tree 2026-08-20 Leech survey: omega is fixed-point-free so `Leech^omega = 0`; "that lead is dead as stated". Replaced by the Höhn–Mason fixed-point sublattice orbits | recorded, with the surviving route (orbit 4, Coxeter–Todd `K_12`) named | `CANON["bulk"]["resolution_evidence"]`; `PM/geometry/leech_partition.py` | DOCUMENTED_ONLY |
| **The 4×3 grouping of the 24 (MiniMOG)** | 4 faces × 3 blocks as a structure on the 24 coordinates | in-tree 2026-08-20: "4 x 3 IS NOT A STRUCTURE ON 24" — MiniMOG serves `M_12` and the ternary Golay code; `M_24` is 5-transitive so no partition is invariant | recorded with the corroborating 12×2 / 6×4 / 3×8 division-algebra argument | `CANON["bulk"]["resolution_evidence"]` | DOCUMENTED_ONLY |
| **Twisted connected sum of Fano pairs (the manifold construction)** | the G2 manifold is a TCS; `b_3 = 24` comes from it | excluded in-tree: `fano_tcs` exhibits 71 ≤ b_3 ≤ 155, so 24 is far below the floor; "The framework should drop the TCS framing" (`CANON["bulk"]["ruling"]`); provenance corrected in `74b0563` (2026-09-15) and `b3_path.narration()` | the option is declared but `g2_construction` has **no consumer**, and there is no TCS module anywhere in `PM/geometry/` | `variants.py` `g2_construction.fano_tcs` (CONSIDERED, inert); correction generated at `PM/geometry/b3_path.py` `narration()` → `provenance_correction`; `PM/geometry/g2_geometry.py:170` | DOCUMENTED_ONLY |
| **"TCS #187" as a catalogue entry** | a named TCS example supplying the framework's topology | in-tree: "'TCS #187' appears in no published enumeration - no TCS catalogue uses serial numbers", and the repo attributed it to CHNP in one place and Joyce in another (`CANON["bulk"]["tcs_obstruction"]`) | its Hodge numbers are **kept and evaluated** so chi_eff route A can be shown type-incorrect | `PM/geometry/chi_eff_routes.py` `_TCS_HODGE = {"h11": 4, "h21": 0, "h31": 68}` and `ROUTES["tcs_hodge"]`; `PM/geometry/g2_geometry.py:178-181` (`self.tcs_id = 187`) | RUNNABLE_LABELLED |
| **"TCS forces `b_2 + b_3` odd"** | a parity theorem excluding (4,24) | **WITHDRAWN** in-tree: relation (2.17) makes the parity depend on the building blocks, "There is no universal parity constraint"; the Crowley–Nordström `nu` is a Z/48 invariant equal to 24 for every TCS and says nothing about parity | recorded twice — in the fork option text and in the CANON note | `variants.py` `g2_construction.fano_tcs` consequence (`WITHDRAWN: ...`); `CANON["bulk"]["notes"]` (CORRECTED 2026-09-06) | DOCUMENTED_ONLY |
| **The `b_2 = 7` proposal, and the pair (7,24)** | keep `b_3 = 24` and move `b_2` to 7 (Joyce 1996), built on the parity claim | dropped with the parity claim ("the b2 = 7 proposal built on one is dropped"); then computed UNREACHABLE by the derived table in `adf0081` (2026-09-14) | not selectable as a seed; but a **live boolean** recomputes its unreachability each run | `PM/geometry/derived_contribution_table.py:198`, keys `pair_7_24_reachable` (lines 537, 588); `variants.py:1385` | DOCUMENTED_ONLY |
| **Joyce (4,24) as the realised pair** | (4,24) lies inside Joyce's 252 (b2,b3) pairs, so the manifold exists | `adf0081` (2026-09-14) computed "(4, 24) UNREACHABLE ... cannot be realised by this construction under the derived table"; `d45b799` (2026-09-15) SETTLED b_3 ≡ 7 (mod 12) | the pair is runnable as the `seed_24` path (b_2 = 4, b_3 = 24) and the unreachability is recomputed — **but `g2_construction.joyce_orbifold` is still the ACTIVE option and its text still argues (4,24) is inside the ranges** | runnable: `variants.py` `b3_seed.seed_24`, `PM/geometry/b3_path.py` `PATHS["seed_24"]`; refutation: `derived_contribution_table.py:48,198`; stale claim: `variants.py` `g2_construction.joyce_orbifold` (ACTIVE) | RUNNABLE_LABELLED |
| **`b_3 = 24` as an INPUT with its origin open** | the status quo seed; `b_2 = 4` from a previously FITTED `h^{1,1}` | superseded by the author ruling in `bf60005` (2026-09-22): adopted path is `seed_43_joyce` | fully runnable via `METAPHYSICA_VARIANT_B3_SEED=seed_24`, labelled `reachable_by_joyce: False`, and the whole seed-24 identity column is kept | `variants.py` `b3_seed.seed_24` (CONSIDERED, prio 0) and `b3_origin.input_24`; `PM/geometry/b3_path.py` `PATHS["seed_24"]`; `core/identity_ledger.py` (12 identities hold on seed_24 alone); `core/seed_blindness.py` | RUNNABLE_LABELLED |
| **(15,24) via the (0,16) profile** | `b_3 = 24` IS reachable, uniquely at (b_2,b_3) = (15,24) | claimed in `adf0081` (2026-09-14), **WITHDRAWN one commit later in `300f66f` (2026-09-15)**: the (0,16) profile's 16 components have transverse group order 8, so the A1 / Eguchi–Hanson model was applied outside its domain | the verdict, its reason and the census that killed it are all executable and tested; `b3_verdict()` returns `WITHDRAWN_A1_MODEL_MISAPPLIED` and refuses to publish a reachability boolean | `PM/geometry/derived_contribution_table.py:85-118, 388, 438-440, 553-570` (`b3_verdict`), `transverse_group_census()` in `intersection_tensor.py` / `eguchi_hanson.py`; `tests/test_derived_contribution_table.py`. **Not** selectable as a seed | RUNNABLE_LABELLED |
| **The A1 / epsilon-dichotomy contribution table outside its domain** | `T^3 x C^2/{+-1}` Eguchi–Hanson contributions apply to every admissible family | `300f66f` (2026-09-15): measured 43,664 components at transverse order 2, 4,688 at order 4, 16 at order 8; only the order-2 rows are A1 | the census is live and tested, and the test fails if every component ever turns out to be A1 (so the withdrawal itself stays falsifiable) | `PM/geometry/derived_contribution_table.py`, `kummer_transverse.py`, `eguchi_hanson.py` | RUNNABLE_LABELLED |
| **Joyce profiles `b_3 = 7` / `19` / `31`** | reachable, fully derived alternatives to (12,43) | refuted **structurally** (n_gen = b_2/4 gives 0, 1, 2) as the family was enumerated — `d45b799` (2026-09-15), made executable in `f289f94` (2026-09-23) | all three run end to end; `PATHS` is *generated* from `b_3 = 7 + 3 n_T3` rather than hand-listed, and the selection argument is now a check rather than a restatement | `variants.py` `b3_seed.seed_7_joyce` / `seed_19_joyce` / `seed_31_joyce` (**DISABLED**); `PM/geometry/b3_path.py` `_joyce_family()`, `compare_paths()` | RUNNABLE_LABELLED |
| **The earlier half-shift parity refutation of `b_3 = 24`** | a parity theorem over 14,336 shift assignments refuted `b_3 = 24` for Joyce (Z/2)^3 | **WITHDRAWN** in-tree for incomplete coverage (shifts on multiply-flipped coordinates are not removable by conjugation) | the withdrawn 512-per-triple stratum is reproducible by an explicit flag, "kept only so the old numbers remain checkable" | `PM/geometry/half_shift_enumeration.py:3-11, 151-156` (`include_relative=False`) | RUNNABLE_LABELLED |
| **`n_gen = b_3 / 8` (the 8 being dim O)** | three generations from the octonions | abandoned by the `n_gen_source` ruling in `bf60005` (2026-09-22): 8 divides no Joyce-reachable `b_3` (all odd), so it is an integer nowhere on the family | runnable three ways, all labelled ABANDONED/REFUTED | `variants.py` `n_gen_source.b3_over_dim_O` (CONSIDERED); `PM/geometry/b3_path.py` `n_gen_report()` (explicit override makes the inconsistent state reachable and therefore checkable); `core/identity_ledger.py` `n_gen_from_b3_over_eight`; `core/switch_search.py:233-294` ("ABANDONED route") | RUNNABLE_LABELLED |
| **`n_gen = chi_eff / 48`** | three generations from the effective Euler characteristic | shown in `3ba5848` (2026-09-22) to fail on the whole Joyce family on **both** chi_eff branches: non-integer at every profile on the seed-dependent branch, and 3 even at `n_T3 = 0` on the constant branch | fully executable and costed per branch per profile; **no ruling is made** — `chi_eff_route` stays OPEN and `chi_eff_claim()` still returns the dichotomy | `PM/geometry/chi_eff_branches.py` (`N_GEN_DIVISOR = 48`, `branch_cost_table`, `route_c_is_the_b3_over_8_route`); `variants.py` `chi_eff_route` | RUNNABLE_LABELLED |
| **`chi_eff = 6 b_3` as an independent generation route** | a third, independent derivation of `n_gen = 3` | `3ba5848` / `chi_eff_branches`: `6 b_3 / 48 = b_3 / 8` **identically**, so it is not independent — it inherits the `b3_over_dim_O` refutation wholesale | the identity is checked symbolically, not sampled | `PM/geometry/chi_eff_branches.py` `route_c_is_the_b3_over_8_route()`; `PM/geometry/chi_eff_routes.py` `ROUTES["six_b3"]` | RUNNABLE_LABELLED |
| **"Three agreeing derivations of `chi_eff = 144` are corroboration"** | routes A (TCS Hodge), B (`b_3^2/4`) and C (`6 b_3`) independently give 144 | refuted in-tree: B and C intersect at exactly one point and it is 24, so their agreement "is the DEFINITION of their unique crossing point"; 144 is hit by ~8 of 320 simple expressions; route A is a Calabi-Yau-threefold Euler characteristic and a type error on a Joyce orbifold | all three routes are evaluated across the reachable family with the crossing solved rather than sampled | `PM/geometry/chi_eff_routes.py` (`ROUTES`, `CLAIMED_CHI_EFF`, crossing solver); `PM/geometry/g2_geometry.py:198-205` exposes both claimed origins | RUNNABLE_LABELLED |
| **`n_gen = chi_eff/(4*b3)`** | a further generation-count notation | flagged as suspect notation requiring verification | policed by the terminology audit's deprecated-pattern list; no module computes it | `generators/generate_terminology_audit.py:47` | DOCUMENTED_ONLY |
| **`b_3 = 24` from an arc-flag stabiliser (12 flags × 2)** | 24 as the order of a Fano arc flag stabiliser | kept but labelled NUMERICAL by the 2026-09-14 `b3_origin` ruling: "it is a subgroup ORDER, not a count of 3-cycles or harmonic 3-forms, so it does not clear the A4 bar" | computed, and the A4 bar is enforced as a consistency check in the switch search | `variants.py` `b3_origin.arc_flag_stabiliser`; `PM/geometry/arc_flag_structure.py`; `core/switch_search.py` A4-bar check | RUNNABLE_LABELLED |
| **`b_3 = 24` from the D4 root shell** | 24 = rank × Coxeter number for D4, forced | same ruling, labelled NUMERICAL: the directions live in a 4-dimensional Cartan space while `b_3` counts 3-forms on a 7-manifold | computed, labelled, and the 12+12 split's Weyl-chamber cost is stated | `variants.py` `b3_origin.d4_root_shell`; `PM/geometry/d4_root_shell.py` | RUNNABLE_LABELLED |
| **`b_3 = 24` from a Joyce twisted sector (7 flat + 17 twisted)** | the only candidate origin that would produce actual 3-cycles | left INERT by the 2026-09-14 ruling: converting families to Betti numbers needs a cited contribution table, and "Selecting it without the table asserts what it cannot compute" | runnable, and the switch search *fails* it as VACUOUS when it is selected without a table — the uncertainty is itself a switch | `variants.py` `b3_origin.joyce_twisted_sector`, `joyce_contribution_table.absent/supplied`; `PM/geometry/joyce_contributions.py`, `half_shift_enumeration.py`; `core/switch_search.py:409-429` | RUNNABLE_LABELLED |
| **`d_ijk`: a triple intersection form on `H^3`** | a cubic metric-free invariant on the 3-forms, "blocked pending a harmonic basis" | refuted in `8e80d5f` (2026-09-21): total degree 9 on a 7-manifold, so identically zero for every input; also `3 + 3 = 6 != 7`, so no topological bilinear on `H^3` alone | the whole multilinear enumeration is recomputed and brute-force recounted in the tests, and it VANISHES rather than disappears when a Betti number is zero | `PM/geometry/multilinear_degree_audit.py`; `PM/geometry/intersection_tensor.py` (the 12×12×43 replacement, `4a5cc68` 2026-09-21) | RUNNABLE_LABELLED |
| **The 24×24 lattice Gram matrix as the model's metric-free form** | the framework's 24 coordinates carry a lattice whose Gram matrix is the intersection form | retired in `8e80d5f` / `4a5cc68` (2026-09-21) for the 12×12×43 integer tensor; the lattice swap had already been measured to move no published number | both lattices remain constructed and verified against their defining properties, and the replacement tensor is computed alongside | `variants.py` `lattice_24d.leech` / `niemeier_e8x3`; `PM/algebra/leech_lattice.py`; `PM/geometry/intersection_tensor.py` | RUNNABLE_LABELLED |
| **"The Leech lattice decomposes into three E8 copies"** | `cross_e8`: 24 = 3 × 8 as a decomposition, each block an octonion carrying a Fano plane | mutually exclusive with Lambda_24 (rootless), fork opened 2026-09-08: "the framework has been assuming both at once" | both lattices runnable and verified (det, evenness, 720 = 3 × 240 roots vs kissing 196560 counted from the Golay code) | `variants.py` `lattice_24d.niemeier_e8x3` (CONSIDERED); `PM/algebra/leech_lattice.py:607` (`_lattice_choice`) | RUNNABLE_LABELLED |
| **The pre-2026-09-07 Leech generator** | Construction A generator used for every generator-derived quantity in the module | FALSIFIED 2026-09-07: `det(Gram) = 7,144,929` (not 1) and 12 basis rows of norm 2 — "Not the Leech lattice" | kept **only as a note string**; there is no `_generator_matrix_pre_2026_09_07`, so the old numbers cannot be reproduced | `PM/algebra/leech_lattice.py:544-567` (`_FALSIFIED_GENERATOR_NOTE`) | DOCUMENTED_ONLY |
| **"phi is not a G2 form" (dim ann = 6 vs 14)** | the all-(+1) phi has a 6-dimensional annihilator in so(7) where g2 needs 14, so it is not a G2 form | refined and partly superseded in `25681cb` (2026-09-21): `Lambda^3(R^7)` has two open GL(7,R) orbits and **both** have 14-dimensional stabilisers, so "dim 14 vs 6" is not the invariant it was read as; the discriminator is the signature of Hitchin's B — (7,0) compact vs (4,3) split | both the old measurement and the refined one are computed, and the superseded reading is named as superseded in the successor fork's notes | `variants.py` `g2_form_convention` notes (old reading) and `metric_construction` notes (refinement); `PM/geometry/g2_differential.py`, `glued_orbit_scan.py` | RUNNABLE_LABELLED |
| **The quadratic contraction called "Hitchin's formula"** | `phi_iab phi_jab / 6` is Hitchin's construction of the metric | corrected in `e0ccf89` / `25681cb` (2026-09-21): Hitchin's construction is CUBIC; the quadratic form returns `1.0 * I_7` for both phis, so every "unique compatible Riemannian metric" claim made through it was unfalsifiable | the mislabelling is recorded and **both** constructions are runnable — the switch exists "so neither path is discarded" (`e0ccf89`) | `variants.py` `metric_construction.quadratic_contraction` (ACTIVE) / `hitchin_cubic` (CONSIDERED); `PM/geometry/g2_differential.py:495` | RUNNABLE_LABELLED |
| **`b_2,flat = 0` "DERIVED in joyce_orbifold"** | a citation to a computation that did not exist | `2888ead` (2026-09-21): "The value was right and the provenance was false, which is the worse of the two failures"; replaced by the character-theoretic derivation over the 7 non-trivial characters of (Z/2)^3 | the false citation is recorded in the commit; the replacement derivation settles b_1, b_2 and b_3 at once and is computed | `PM/geometry/derived_contribution_table.py` (`FLAT_B2`), `joyce_orbifold.py` | DOCUMENTED_ONLY |
| **`w0 = -(n-1)/n` with `n = b_2 = 4`** | the best fit of every candidate: 0.04 sigma on w0, 0.25–0.74 sigma in 2D | **RULED OUT on physics 2026-09-06** despite the fit: `b_2` counts Kähler moduli, whose mass the framework's own racetrack fixes at 24.6 TeV against the 3.5e-32 eV a rolling field needs — a ratio of 7.1e44, published as `geometry.kahler_over_quintessence_mass` | declared with the full sigma accounting and the computed mass ratio — but `dark_energy_betti` has **no consumer**, so the option cannot be executed | `variants.py` `dark_energy_betti.b2_4` (CONSIDERED, inert); the mass ratio itself is computed in `PM/cosmology/dark_energy_thawing.py` | DOCUMENTED_ONLY |
| **`w0 = -(n-1)/n` with `n = 3`, `6`, `12`, `8`** | the E8-block, `chi/b_3`, bridge-count and octonion readings of the dark-energy integer | recorded, not advocated, at the 2026-09-06 ruling; `n = 3` is the only option whose thawing band contains the DR2 central `wa` | four declared options with their sigmas — same inert fork | `variants.py` `dark_energy_betti.ngen_3` / `chi_over_b3_6` / `bridges_12` / `octonion_8` | DOCUMENTED_ONLY |
| **`w0 = -0.8528` from the thermal-time `alpha_T = 4.5` mechanism** | a pre-DESI dark-energy equation of state from the thermal mechanism | retired pre-DESI (`CANON["w0"]["superseded"]["-0.8528"]`, "retired pre-DESI candidate") | the retirement is recorded; the value survives as an **unlabelled default argument** in a plot script that nothing imports | `core/canonical_values.py`; unlabelled at `simulations/visualizations/plot_wz_evolution.py:22` (`def w_PM(z, w0=-0.8528, ...)`) | DOCUMENTED_ONLY |
| **`wa = -4/sqrt(b_3)`** | the post-DESI `wa` graft | **RETIRED on the register with "do not resurrect"** | still **computed every call** under the key `wa_thawing` in two geometry modules, while the registry row `cosmology.wa_thawing` carries the canonical `-1/sqrt(b_3)`; labelled only in `free_set` | label: `core/free_set.py:168-171, 211-214`; unlabelled computation: `PM/geometry/b3_path.py:276`, `PM/geometry/b3_candidate_sweep.py:185`; canonical row: `PM/cosmology/dark_energy_thawing.py:350` | RUNNABLE_LABELLED |
| **`wa = +0.1` (attractor) and `wa = +0.27` (thermal)** | sub-leading CPL parameters of the wrong sign | superseded: "DESI prefers wa < 0, so the positive-wa discriminator failed" | recorded in CANON and inline in the appendix prose, each occurrence marked SUPERSEDED | `CANON["wa"]["superseded"]`; `PM/cosmology/attractor_potential.py:754-773` | DOCUMENTED_ONLY |
| **`n_s = 0.9996` from the Re(T) slow-roll variant** | a zero-parameter spectral index | FALSIFIED at 8.3 sigma vs Planck 2018 (`CANON["n_s"]["superseded"]`) | published and rescored every build as `cosmology.n_s_slow_roll` (8.263 sigma FAIL) | `core/canonical_values.py`; `PM/cosmology/inflation.py`; `core/observable_groups.py` | RUNNABLE_LABELLED |
| **`H0 = 76.34` (Ricci-flow variant) and `H0 = 70.42` (sterile extraction)** | two topology-first Hubble candidates | superseded; "no zero-var candidate survives" (`CANON["H0_km_s_Mpc"]`) | the Ricci-flow variant is still computed and published as `cosmology.H0_ricci_variant` | `PM/cosmology/ricci_flow_h0.py`; `core/canonical_values.py`; `core/observable_groups.py` | RUNNABLE_LABELLED |
| **`sin^2(theta_W) = 0.23190` geometric spectral candidate** | the Weinberg angle from spectral geometry | superseded on a scheme ruling; reverts to 17.1 sigma FAIL without an uncited theory buffer (`theory_uncertainty_policy` = `cited_only`) | published as `gauge.sin2_theta_w_geometric` and rescored under all three uncertainty policies each build | `PM/gauge/master_action.py`; `generators/generate_validation_certificates.py`; `variants.py` `theory_uncertainty_policy` | RUNNABLE_LABELLED |
| **The racetrack vacuum at `Re(T) = 37.8527`** | the unique SUSY AdS minimum of the declared N=1 potential, so `Re(T)` is an OUTPUT | deleted by the `b3_seed` adoption (`bf60005`, 2026-09-22): the mechanism IS the exponent ordering `a > b`, and at `b_3 = 43` `a = 2pi/43 < b = 2pi/26`, giving zero stationary points — "Not a relocated minimum, a deleted one" | fully runnable on `seed_24`; the absence on the adopted branch is pinned by tests, and the solver was proven innocent by an ordering-restored control at `Re(T) = 10.2085` | `PM/cosmology/racetrack_vacuum.py:23-45`; `tests/test_racetrack_vacuum.py`, `tests/test_re_t_is_unbound_on_the_adopted_path.py`; cross-check row `(24, 26)` in `racetrack_pairs.py` | RUNNABLE_LABELLED |
| **"Try other exponents" — the 28 derived-integer pairs** | some other pair of derived integers restores the ordering and the vacuum | enumerated and costed in `1199762` (2026-09-22); the structural result is negative: **every** pair that restores the ordering gives an AdS minimum, so nothing on the derived menu uplifts to dS | fully runnable, ordered by pair name, trials factor 56 published as a first-class field, `verdict` a constant, nothing adopted | `PM/cosmology/racetrack_pairs.py` (`DERIVED_INTEGER_MENU`, `enumerate_pairs`) | RUNNABLE_LABELLED |
| **`neutrino.theta13_derived = asin(1/6)`** | `sin(theta_13) = alpha_leak/sqrt(2 n_gen) = 1/6`, zero free parameters | FALSIFIED by the R1 ruling 2026-08-25, ~9 sigma from NuFIT 6.0 | a live published row with `status="FALSIFIED"`, recomputed every build, with its own EML tree and its 9.594 deg value intact | `PM/algebra/neutrino_algebraic.py:32-36, 423-451`; `core/observable_groups.py`; `parameters.json` `neutrino.theta13_derived = 9.594...` | RUNNABLE_LABELLED |
| **`sin(theta_13) = lambda_C/sqrt(2)` (quark–lepton complementarity)** | `theta_13 = 9.155 deg` from the Cabibbo angle | FALSIFIED at 5.3 sigma (`CANON["theta13_deg"]["superseded"]["9.155"]`) | recorded **only** as a superseded entry; no module computes it | `core/canonical_values.py` only | DOCUMENTED_ONLY |
| **`algebra.gaugino_cabibbo_{proxy,derived,refined}`** | the Cabibbo angle from an N1=24/N2=23 hidden-E8 racetrack, zero free parameters | FALSIFIED 2026-09 at 344.7 / 37.6 / 25.6 sigma vs PDG `lambda_W`; between them they carry 95.4% of the global chi-squared | all three rows live, published, labelled FALSIFIED, derivations intact ("Retained with its derivation intact") | `PM/algebra/gaugino_condensation.py:33-41, 327-338, 380-387, 513-518`; `parameters.json` (all three present) | RUNNABLE_LABELLED |
| **`lambda_cabibbo = exp(-pi/2)`** | the zero-variable Cabibbo candidate | FALSIFIED at 25.5 sigma (`CANON["lambda_cabibbo"]["superseded"]["0.20788"]`) | the same number is the live `algebra.gaugino_cabibbo_refined = 0.20787957...`, computed as `exp(-2 pi * 6/24)` and labelled FALSIFIED | `core/canonical_values.py:146-149`; `PM/algebra/gaugino_condensation.py:142-143, 513-518` | RUNNABLE_LABELLED |
| **`sin^2(2 theta) = 1/b_3` (torsion-geometry sterile mixing)** | active–sterile mixing from torsion geometry, `1/24 ~ 0.0417` | excluded by the IceCube/MINOS+ 2024 bound of 0.01 by ~4.2x; "SUPERSEDED CLAIM, kept on record per falsification policy" | recorded **only** inside the superseding row's description string; nothing computes `1/b_3` as a mixing angle, and the cited `SCALE_DISAGREEMENTS.md` is not in this repository | `PM/portals/sterile_neutrino_portals.py:848-851` | DOCUMENTED_ONLY |
| **The v25 flavour ansatz calibrated at `b_3 = 24`** | `theta_13 = arcsin(sqrt(2/3) sqrt(2) sin(pi/b3))` as a topological derivation, 0.8 sigma vs NuFIT | the last seed-blind writer; ruled in `bf60005`/`1199762` (2026-09-22): a formula claiming `b_3` must consume `b_3`, and the 0.8 sigma agreement "is exposed as a property of the off-path calibration" (8.6686 deg at 24 vs 4.8351 deg at 43) | both branches runnable and regression-pinned; the calibrated branch must "ADMIT to be a calibrated constant, not b_3" | `variants.py` `flavour_seed_coupling.follow_seed` / `calibrated_24`; `PM/particle/yukawa_derivation.py:862-867` | RUNNABLE_LABELLED |
| **The twelve externally proposed closed-form "closures"** | closed forms eliminating the remaining calibration inputs (Weinberg angle, PMNS angles, Lambda, H0, g-2, a Majorana phase, soft-SUSY scale, baryogenesis prefactor) | evaluated and mostly falsified before integration, 2026-08 review: the Weinberg formula gives 0.365 not 0.2312, the theta_13 formula 0.31 deg not 8.618, the Golay Lambda expression 1.17e-6 against a claimed 1.17e-120 | all fourteen candidate ids are evaluated from SSOT inputs every build with a recorded verdict, "so the same dead end is never explored twice" | `PM/validation/candidate_closure_gate.py` (`candidate_id` rows, `FALSIFIED` / `ILL_FORMED` / `NEAR_MISS_NOTED` / …) | RUNNABLE_LABELLED |
| **Exact-but-worthless formula hits** | `theta_23 = aut_fano*n_fano/arc_stab = 49`; `ckm.delta_cp = 24 pi/144 = pi/6` | disqualified in `5114cc8` (2026-09-14): tolerance cannot filter an exact match; 49 is the NuFIT central value in **degrees** and the match evaporates in radians | the three disqualification classes (EXPERIMENTAL, UNIT_DEPENDENT, …) run before any expression is generated, and the trials factor is reported with every result | `core/shape_search.py` (`disqualify()`, `primitives()`); `ff7ddc4` / `5114cc8` | RUNNABLE_LABELLED |
| **"24 = b_3" in the bc-ghost, Leech-dimension and `eta^(-24)` claims** | the 24 in three string-theoretic claims is the third Betti number | `bf60005` (2026-09-22): each actually counts the bulk's 24 spacelike core; all three claims survive, rewired to `D_space_24`, "with the old identification recorded per branch as data" | the correction is labelled at the site and the conflation is named | `PM/geometry/modular_invariance.py:186-198, 540`; `PM/paper/foundations.py:793`; `simulations/validation/unitary_filter_legacy.py:324-331` | RUNNABLE_LABELLED |
| **`alpha-inverse-geometric` agreement** | a geometric derivation of the fine-structure constant that agreed at `b_3 = 24` | falsified-by-ruling in `bf60005` (2026-09-22): moves to 449.6 on the adopted seed "and stays LABELLED" | kept in the ruled-divergence ledger under an explicit `_FALSIFIED_BY_RULING` reason, and the gate is two-directional (a row that heals must leave, or the test fails) | `core/ruled_divergences.py` (`alpha-inverse-geometric`, `alpha-inverse-anchor`, `unity-seal-anchor`); `PM/geometry/alpha_rigor.py` | RUNNABLE_LABELLED |
| **`T_i` as `b_2` gauge kinetic functions / as CY3 Kähler moduli** | the four racetrack moduli are U(1) gauge kinetic functions, or CY3 Kähler moduli before the S^1 reduction | not adopted at the 2026-09-08 `moduli_indexing` fork; adopting `b2_gauge` "RE-OPENS ROUTE 1" (the quintessence closure that rests on the racetrack existing) | declared with the Route 1 consequence spelled out — but `moduli_indexing` has **no consumer** | `variants.py` `moduli_indexing.b2_gauge` / `cy3_shadow` (CONSIDERED, inert); `PM/geometry/four_face_structure.py` | DOCUMENTED_ONLY |
| **Route 1: Kähler moduli as the quintessence field** | the rolling dark-energy field is one of the four Kähler moduli | closed by the racetrack giving `m_T = 2 k_gimel m_3/2 ~ 24.6 TeV` against `b_3 H0 ~ 3.5e-32 eV`, a ratio of 7.1e44 | the closure is computed (`geometry.kahler_over_quintessence_mass`) and the premise it depends on is named; but the option that would re-open it is inert | `variants.py` `moduli_indexing.b2_gauge` consequence; `PM/cosmology/dark_energy_thawing.py` | DOCUMENTED_ONLY |
| **All 35 face-assignment candidates (`face_genericity = all`)** | any 4-subset of the seven Fano points may label the faces | superseded 2026-09-01 when genericity became DERIVED from the global-labelling premise: the 28 line-containing sets admit zero labellings, each of the 7 arcs admits 18 | the 3^7 enumeration and the 28/7 orbit split are computed in `topological_terms.block_labelling_analysis`, but `face_genericity` itself has **no consumer** | `variants.py` `face_genericity.all` (CONSIDERED, inert); `PM/gauge/topological_terms.py` | DOCUMENTED_ONLY |
| **Permissive EML render policy** | any clean render may be offered as a formula's diagram | ruled `strict`, decided by running both branches (two git branches, manually diffed) | wired: flipping the fork changes which formulas are offered (ten more under `permissive`, "every one of them a truncation") | `variants.py` `render_policy.permissive`; `generators/eml_render_validity.py:197` | RUNNABLE_LABELLED |
| **"Fold theory uncertainty in regardless of provenance"** | the behaviour before the fork existed: uncited theory buffers may change a verdict | generalised away by the R6 ruling; five load-bearing rows revert (e.g. `sin2_theta_w_geometric` 0.68 -> 17.1 sigma) | wired, and all three verdicts are exported per row so the comparison needs no rebuild | `variants.py` `theory_uncertainty_policy.always` / `experimental_only`; `generators/generate_validation_certificates.py:158` | RUNNABLE_LABELLED |
| **`RULINGS_ASSESSMENT` (2026-08-25) scoring method** | score each theory branch on an "Accuracy vs data" axis 1–5 and recommend a winner | quarantined in `1f7935e` (2026-09-20): the method conflicts with the anti-tuning guard, its central premise (`b_3 = 24` derived) is refuted, and its numbers are stale. "The questions survive; the scoring does not" | preserved verbatim under a SUPERSEDED header in the quarantine directory, with a test asserting each occupant declares itself superseded and that no production module reads it | `docs/history/RULINGS_ASSESSMENT_2026-08-25.md` | DOCUMENTED_ONLY |
| **`G_GEOMETRY_HOLONOMY` literal-PASS gate** | "G2 holonomy validated (parallel spinor + Ricci-flat + torsion-free)", result PASS | `_validate_g2_holonomy` **deleted** in `bfff33e` (2026-09-22): it was `all()` over three literals and could not fail, publishing a PASS for a claim that is false on the adopted branch | the claim survives, generated from `geometry_narration` so it follows `g2_form_convention`, with each condition reporting MEASURED or PLACEHOLDER (all three are placeholders and say why). The deleted code was a fake-pass check, not an approach | `PM/geometry/geometry_narration.py`; `bfff33e` | DOCUMENTED_ONLY |

### Counts

| verdict | rows |
|---|---|
| RUNNABLE_LABELLED | 35 |
| DOCUMENTED_ONLY | 27 |
| **LOST** | **0** |

### LOST list

**Empty.** No discarded approach traced in this audit has been deleted from the
repository. Three independent checks agree: no `src/` or `tests/` file has ever
been removed; no fork option id present at the root commit is absent today; and
`git log -S` on every approach string named in the brief finds it still in HEAD.
The standing rule has not been violated by deletion.

What the audit found instead is **two failure modes short of deletion**, both of
which the rule's wording ("runnable *and* labelled") does cover:

1. **Labelled but not runnable** — 13 options across the five forks with no
   consumer (`bulk_signature`, `dark_energy_betti`, `g2_construction`,
   `moduli_indexing`, `face_genericity`). `dark_energy_betti` is the sharpest
   case: it is RULED, it carries seven options with full sigma accounting and a
   computed mass ratio behind the ruling, and **not one of them can be
   selected**. Nothing in `tests/test_variants.py` would notice.
2. **Runnable but not labelled** — withdrawn claims still asserted as live
   physics: `D_bulk = D_crit = 26` in five modules, the Bars Sp(2,R)
   ghost-freedom appeal and the "two-time + Euclidean bridge" `+2` reading
   throughout `unitary_filter_legacy.py` (which `run_all_simulations.py`
   imports), the retired `-4/sqrt(b_3)` computed under the live row's own name
   `wa_thawing`, and `g2_construction.joyce_orbifold` still ACTIVE while
   arguing for a pair (4,24) that the same tree computes as unreachable.

## Approaches that should become DISABLED options, in priority order

`DISABLED` is already defined in `variants.py` as "Refuted … and RETAINED
ANYWAY, runnable and labelled … DISABLED means 'not on the table', NOT 'not
executable'", with `sweepable_ids()` excluding it from default sweeps only.
That is exactly the slot these belong in. Each row gives the fork (existing id,
or a new fork proposed) and the **exact evidence string already in the tree**
that labels it — no new evidence is invented here, and no OPEN ruling is
pre-empted (nothing below touches `chi_eff_route` or `re_t_adoption`).

1. **`dark_energy_betti.b2_4` → DISABLED** (existing fork). It is the one option
   in the registry explicitly ruled out on physics while being the best fit, so
   leaving it CONSIDERED means a capped sweep spends budget on a candidate the
   framework has rejected. Evidence string, already in the option's
   `consequence`: `"RULED OUT 2026-09-06, on physics, despite being the BEST FIT
   BY A LARGE MARGIN"`. Prerequisite, and it is the more important half: **wire
   the fork** — `dark_energy_betti` has no `resolve()` consumer, so today the
   label is the only thing the option has.
2. **`n_gen_source.b3_over_dim_O` → DISABLED** (existing fork). Structurally
   refuted across the entire reachable family, not merely unadopted. Evidence
   string, already present in three places:
   `"ABANDONED route (not n_gen_source)"` (`core/switch_search.py:289`),
   `"REFUTED ROUTE, kept runnable and labelled"`
   (`core/identity_ledger.py`, `n_gen_from_b3_over_eight`), and the option's own
   `"it requires 8 to divide b_3, so it is incompatible with every
   Joyce-reachable value"`. It is already fully runnable — this is a relabel
   only.
3. **`g2_construction.fano_tcs` → DISABLED** (existing fork), *and* the fork's
   ACTIVE option corrected. Evidence string, already in the option:
   `"b3 = 24 sits far outside what anyone has realised … he realizes 71 <= b3(M)
   <= 155"`. The blocking problem is that `g2_construction.joyce_orbifold` is
   ACTIVE and still argues `(4, 24)` is inside Joyce's ranges, which
   `derived_contribution_table.py:198` computes as `"(4, 24) and (7, 24):
   UNREACHABLE"` on the adopted path. Both options are stale in opposite
   directions; the fork also has no consumer.
4. **New option `b3_seed.seed_15_24_a1_misapplied` → DISABLED.** The withdrawn
   `(b_2, b_3) = (15, 24)` result is the most thoroughly documented discarded
   seed in the repository (`300f66f`, 2026-09-15) and the only one whose
   verdict function exists (`b3_verdict()`), yet it is the one seed that cannot
   be pushed through the pipeline. Adding it as a DISABLED path in
   `b3_path.PATHS` (hand-declared and labelled, exactly as `seed_24` is) would
   let the downstream consequences of the withdrawn pair be measured rather than
   argued. Evidence string, already in the tree:
   `"status": "WITHDRAWN_A1_MODEL_MISAPPLIED"` with
   `"why_withdrawn": "the (0,16) profile's components have transverse group
   order 8, …"` (`derived_contribution_table.py:566-570`).
5. **New option `b3_seed.seed_7_24_joyce_b2_seven` → DISABLED.** The `b_2 = 7`
   proposal, and the pair `(7, 24)`, are the nearest-realizable alternative the
   register named and then dropped; today only a boolean about them is computed.
   Evidence strings, both already in the tree: `"WITHDRAWN: the claim that TCS
   forces b2 + b3 odd … the b2 = 7 proposal built on one is dropped"`
   (`variants.py`, `g2_construction.fano_tcs`) and
   `"(4, 24) and (7, 24): UNREACHABLE"`
   (`derived_contribution_table.py:198`).
6. **`bulk_signature.26_2` and `bulk_signature.25_1` → keep CONSIDERED, but wire
   the fork.** Neither is refuted — both pass the mod-8 test the adopted option
   fails — so DISABLED would be wrong. The defect is that the fork is inert:
   the ruling's three accepted costs are recorded as prose in
   `CANON["bulk"]["ruling"]` and nothing can run the alternatives. Evidence
   string for the adopted option's costs, already present:
   `"withdraws 'D_bulk = D_crit = 26' … withdraws the Bars appeal for
   ghost-freedom … leaves the lattice obstruction unanswered (24 - 2 = 6 mod
   8)"`.
7. **New fork `bulk_formulation`, with `sampler_pair_27d` → DISABLED.** The 27D
   `M^27(24,1,2)` formulation is a *different* claim from any option
   `bulk_signature` offers (one shared time plus a (0,2) spacelike sampler
   pair), and it is the oldest discarded geometry in the project. It is
   currently policed only as a string token. Evidence string, already in the
   tree verbatim: `"M^27(24,1,2) sampler-pair formulation (one shared time +
   (0,2) spacelike sampler dims). Retired: required both b3+2 and b3+3 as
   'forced', shadows summed to 25 != 27, spinor was non-chiral, and spacelike
   correlator bridges carry the superluminal-shortcut hazard (Pettini)."`
   (`CANON["bulk"]["superseded"]["27"]`). A second DISABLED option
   `physics_core_24_1` would carry
   `"(24,1) physics-core dimension mislabelled as a bulk"`.
8. **New fork `ghost_control`, with `bars_sp2r_appeal` → DISABLED.** This is the
   highest-value labelling fix in the report, because the withdrawn appeal is
   not merely undocumented — it *runs*, inside a module the build imports, and
   asserts `c = 24 + 2 - 26 = 0` for a "v21 (24,1) signature theory with
   Euclidean bridge". Making it a DISABLED option would let
   `unitary_filter_legacy` state which branch its central-charge arithmetic
   belongs to. Evidence string, already in the tree: `"The appeal to Bars for
   ghost-freedom is withdrawn: Sp(2,R) gauging removes two dimensions and yields
   ONE 24D shadow of signature (23,1), not two 13D(12,1) shadows, so the
   framework's shadows do not inherit his theorem. Ghost control of the second
   time is now an OPEN problem with no computed backing"`
   (`CANON["bulk"]["ruling"]`).
9. **New fork `plus_two_reading`, with `euclidean_bridge` and `two_sp2r` →
   DISABLED.** The ruling ordered two of the three `+2` readings retired
   "wherever they appear" and one of them is still the live text of the unitary
   filter. Evidence string, already in the tree: `"the '+2' must now carry ONE
   reading. Three are currently in use across the formulas: a lightcone pair,
   'two-time plus Euclidean bridge', and '2 Sp(2,R)'. Under (c) with two
   physical times the only self-consistent reading is 'one time per shadow'; the
   other two should be retired wherever they appear."`
10. **New fork `sterile_mixing_route`, with `torsion_one_over_b3` → DISABLED.**
    `sin^2(2 theta) = 1/b_3` is named in the project's own falsified list but
    exists only inside a description string, so the excluded value is never
    computed and the exclusion is never re-checked against the bound. Evidence
    string, already in the tree: `"SUPERSEDED CLAIM, kept on record per
    falsification policy (SCALE_DISAGREEMENTS.md §4): sin²(2θ) = 1/b₃ = 1/24 ≈
    0.0417 (torsion geometry) exceeds the IceCube/MINOS+ 2024 upper bound of
    0.01 by ~4.2× and is excluded by data."`
    (`PM/portals/sterile_neutrino_portals.py:848-851`).
11. **New fork `theta13_route`, with `qlc_lambda_c_over_root_two` → DISABLED.**
    The quark–lepton-complementarity candidate is the only falsified `theta_13`
    route with no runnable row — its zero-parameter sibling `asin(1/6)` has one.
    Evidence string, already in the tree: `"sin(theta13) = lambda_C/sqrt(2),
    quark-lepton complementarity — FALSIFIED at 5.3 sigma"`
    (`CANON["theta13_deg"]["superseded"]["9.155"]`).
12. **New fork `leech_generator`, with `pre_2026_09_07` → DISABLED.** The
    falsified generator is retained as prose only, so the numbers it produced
    for "every generator-derived quantity in the module" cannot be reproduced.
    Evidence string, already in the tree: `"pre-2026-09-07 generator:
    det(Gram)=7144929 (not 1) and 12 rows of norm 2 (Lambda_24 has none). Not
    the Leech lattice."` (`PM/algebra/leech_lattice.py`,
    `_FALSIFIED_GENERATOR_NOTE`).
13. **`moduli_indexing.b2_gauge` / `cy3_shadow` and `face_genericity.all` →
    keep CONSIDERED, wire the forks.** None is refuted; `b2_gauge` is the option
    that would re-open Route 1, which is a live question, not a closed one. The
    defect is inertness, not the label.

### Two fixes that are not option relabels

- **Name the retired `wa` formula where it runs.** `b3_path.downstream()` and
  `b3_candidate_sweep` both publish `-4/sqrt(b_3)` under the key `wa_thawing`,
  which is the registry name of the canonical `-1/sqrt(b_3)` row. `free_set.py`
  already carries the correct label —
  `"-4/sqrt(b_3) -- the RETIRED formula's legacy artefact; removal records no
  independent content, not a revival"` — and the register's own words are
  `"do not resurrect"`. The two geometry modules should carry the same label, or
  a different key.
- **Add a test that every fork has a live consumer.** Five of eighteen forks
  have none, and two more are read only by the audit harness. `test_variants.py`
  checks that a fork's default matches its source but never that anything reads
  the fork, so an option can be declared, costed, labelled and still be
  unexecutable — which is the failure mode the whole registry exists to prevent.
  The check is cheap: for each fork id, assert that `resolve("<id>")` appears
  somewhere under `src/` outside `variants.py`, with an explicit allow-list for
  any fork deliberately left declaration-only.

---

*Audit method: read-only. `git log`/`git show`/`git diff` plus file reads; no
source file was modified and no git command that writes was run. All fork counts
are against `variants.py` md5 `947b794c7367aa3eac82b8a7468012e5`, taken while
the file was being modified by another process — re-measure before acting on the
counts.*
