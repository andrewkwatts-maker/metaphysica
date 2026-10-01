# Wording memo — the adopted model

## RULINGS 2026-10-01 (the author; D-015) — these override anything below

- **Adopt the sensible path on every fork; keep the alternatives switchable**
  so they can be simulated and compared. Off-path options stay runnable.
- **Real form: compact (`octonion_derived`) is ACTIVE**; the split form
  (`all_plus_one`) stays a switchable path. On the active path Y₇ has
  holonomy exactly G₂ (π₁ = 1), so "G₂ holonomy" is now accurate there. Do
  not add holonomy phrases gratuitously (a source-file ratchet counts them),
  and use `holonomy_claim()` where a sentence depends on the real form.
- **χ_eff: the K3 reading is ADOPTED.** χ_eff = 2 × Σ χ(K3) = 48n — the
  Kummer K3 surfaces transverse to the n singular involutions, counted once
  per shadow; 144 at n = 3. Still never "the Euler characteristic of Y₇"
  (that is 0). n_gen = χ_eff/48 = n restates the ruled route b₂/4; it is not
  a second derivation and not an index theorem for chirality (chirality is
  still OPEN).
- **Re(T) is an OPEN modulus**: Y₇ fixes no Re(T) at leading order (CG.6).
  Values computed with the calibrated Re(T) are labelled CALIBRATED.
- **WA-1 is ADOPTED**: each bridge is one resolved A₁ component (one U(1)).
  With π₁ finite only at n = 3 (and, on the compact form, holonomy exactly
  G₂ only there), the bridge↔component correspondence selects
  (b₂, b₃) = (12, 43) without data (CG.8). Its consequence to test: the 12
  U(1) couplings come in 3 quartets.

Status: 2026-10-01. Read this before editing any prose, formula text or
parameter metadata. It states what is TRUE on the active path, how to say it,
and what may not be said. Decisions are in the site repo's
`docs/DECISION_LOG.md` (D-001 … D-014); the closed-geometry certificate is
`src/metaphysica/simulations/PM/geometry/closed_geometry/`.

## 1. Facts on the active path

| topic | say this | source |
|---|---|---|
| internal space | Y₇ = Joyce's resolution of T⁷/Γ, Γ = (ℤ/2)³ = the diagonal stabiliser of φ | CG.1–CG.4 |
| Betti numbers | (b₂, b₃) = (12, 43); sequence (1, 0, 12, 43, 43, 12, 0, 1); b₃ = 7 + 3b₂ = 7 flat + 36 twisted | CG.1 |
| Euler characteristic | χ(Y₇) = 0 (every closed odd-dimensional manifold) | CG.2 |
| fundamental group | π₁(Y₇) = 1 | CG.4 |
| singular set | 12 components, each a flat T³ (b₁ = 3); U(1)¹² on the smooth manifold (SU(2)¹² at the orbifold point); local N = 4 SYM | CG.3, CG.5 |
| generations | n_gen = b₂/4 = 3 = the number of singular involutions n (the ruled route) | b3_path, D-009 |
| χ_eff = 144 | an **effective index**, never "the Euler characteristic of Y₇"; defined by the K3 reading χ_eff = 2Σχ(K3) = 48n (adopted 2026-10-01) | D-009, D-015 |
| chirality | OPEN: the singular loci are disjoint, so Y₇ has no codimension-7 points | D-011 |
| moduli, Re(T) | OPEN: the leading-order flux potential is positive and runs away; no gaugino racetrack exists on Y₇; full holonomy excludes a confining sector in φ's family | CG.5, CG.6, CG.10 |
| dark energy | OPEN: the leading-order flux potential cannot accelerate (|∇V|/V ≥ 5√(2/7) ≈ 2.673 > √2) | CG.11 |
| flavour | OPEN: needs a chiral sector; flavour values are model constructs or fits | D-011 |
| bulk | 26D, signature (24,2) = 24 space + 2 times, one per 13D(12,1) shadow; 12 bridge pairs | ruling 2026-08-31 |
| second time | ghost control is OPEN; Bars' Sp(2,ℝ) ghost-freedom theorem is NOT inherited (withdrawn) | ruling 2026-08-31 |
| 26 | "26 = the critical dimension" is withdrawn (the two-time critical dimension is 27–28) | ruling 2026-08-31 |
| bridges ↔ components | the 12 bridges and 12 components form one 3 × 4 structure on the all-plain members; WA-1 (adopted 2026-10-01) makes it the selection of (12, 43); blocks ↔ involutions is canonical, the matching inside a block is a free choice | CG.8, CG.12, D-015 |

## 2. What is off-path, retired or calibrated

- **b₃ = 24 is the OFF-PATH seed**: retired, and unreachable by Joyce's
  construction from Γ (CG.7). Never assert it as the topology.
- **TCS / "TCS #187" is off-path.** The construction is a Joyce orbifold; b₃ = 43
  is outside every published TCS range (71–155), and "#187" appears in no
  published enumeration. Do not cite CHNP as the construction.
- **n_gen = b₃/8 is abandoned**: 8 divides no reachable b₃ (all odd).
- **The k_ℷ layer** (k_ℷ = b₃/2 + 1/π: α⁻¹, the Higgs vev v, sin²θ_W, T_CMB,
  μ): fits made at the retired seed (D-007). Label CALIBRATED; values unchanged.
- **The racetrack** (a = 2π/24, ε ≈ 0.2257, Re(T) = 7.086, the "VEV gap"):
  calibrated at the off-path seed; no racetrack exists on Y₇.
- **w₀ = −23/24** is frozen at the off-path seed; w₀ = −1 + 1/b₃ has no
  derivation. Never write "consistent with DESI": the DESI DR2 w0waCDM
  headline (BAO+CMB+DESY5, arXiv:2503.14738; parameter `desi.w0`) is
  w₀ = −0.752 ± 0.057, and both −23/24 and −42/43 sit more than 3σ from it.
- **"G₂ holonomy"** is true on the active (compact) path since D-015 and false on
  the split-form switch path. See §4.

## 3. A 24 that is still in the code

Classify by the OBJECT the text says it counts (D-004/D-012), never by the
variable name:

| the 24 counts | write |
|---|---|
| the bulk's space directions, 12 bridge pairs × 2, SO(24), D_space | name the object ("the bulk's 24 space directions"); never call it b₃ |
| a named constant: Leech rank, the 24-cell, χ(K3), the η²⁴ / bc-ghost weight | name the constant |
| nothing named (arithmetic or a fit) | "calibrated at the off-path seed b₃ = 24" |

Never change a value, an EML tree, an arithma expression, a formula id or a
parameter path in a wording pass. Value changes go through a pre-registered
decision.

## 4. How to say it

- Numbers in prose come from live values wherever the text is built in code:
  `from metaphysica.simulations.PM.geometry.geometry_narration import render`,
  then `render("Y_7 has {betti_pair}.")` (registers `plain`, `html`, `latex`;
  keys: b2, b3, n_gen, manifold, construction, structure, betti_pair,
  betti_sequence, b3_split, n_gen_route, chi_eff, chi_y7, off_path_seed,
  calibrated_at_24, bulk). In module-level constants and docstrings, typed
  numbers are acceptable if correct for the adopted seed.
- Holonomy: accurate on the active path, but a source-file ratchet counts the
  phrases, so do not add them to files that have none. Where a sentence depends
  on the real form, use `holonomy_claim()["sentence"]`.
- Status words: DERIVED, CALIBRATED, OPEN, OFF-PATH, RETIRED, UNRULED — use them.
- A retired claim is LABELLED, not silently deleted, where the text records
  history ("formerly …, retired"). In reader-facing prose, state the adopted
  model first and keep the history to one clause.
- Data: never claim a global fit (the registry verdict is POOR_FIT); never
  restate the withdrawn χ² = 0.23 headline; per-row comparisons cite their row.
- Remove version and sprint tags from reader-facing prose ("v24.2",
  "Sprint 2.9", "v25.0+v26.0").
- Plain sentences; one idea each; no hype ("exactly", "naturally", "without
  fine-tuning") unless proved.
- Never invent a constant, tolerance, citation or DOI.

## 5. Process rules for anyone editing

- Edit only the files you own in the current pass.
- Run the tests that import or pin the files you touched
  (`python -m pytest <files> -q -p no:cacheprovider`).
- Do not run git, the build, or anything that sets `METAPHYSICA_OUT`.
- Report what you changed, what you left alone, and why.
