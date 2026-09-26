# Salvage analysis: `origin/continue/gates-and-rulings` and `origin/eml-render-strict`

Read-only survey, 2026-09-26. No source file was modified and no git write command
was run to produce it.

| | |
|---|---|
| `origin/continue/gates-and-rulings` | tip `fdcc6bb`, last commit 2026-08-25, 114 commits not in `main` |
| `origin/eml-render-strict` | tip `502dd2c`, last commit 2026-08-29, 116 commits not in `main` |
| shared root | `7a0cc08` |
| `main` root | `fedfec8` (2026-09-14) |
| `git merge-base origin/main origin/<either>` | returns nothing (exit 1) for both |

The two branches are not independent of each other: they share 111 commits and
diverge at `7f7aaff`. `gates-and-rulings` adds 3 commits after that point
(`ca23497`, `83c067e`, `fdcc6bb`); `eml-render-strict` adds 5 (`660642c`,
`bdd0c03`, `3baeb0a`, `6bd33a8`, `502dd2c`). 119 distinct commits in total.

## Verdict

**One thing is worth rescuing, and it is not a physics fix.** `main`'s root
commit `fedfec8` is a whole-tree snapshot taken on 2026-09-14 — after both
branch tips — and it demonstrably carries the content of *both* divergent lines
(`502dd2c`'s `REQUIRE_OPERATOR`, `83c067e`'s ruling doc, `3baeb0a`'s registry
statuses, `6bd33a8`'s `write_report`, `660642c`'s `SEMANTIC_EVALUATORS`, and
`ca23497`'s bundled-`parameters.json` fallback are all present). Of the 47
BUG_FIX commits on the two branches, 46 are already in `main` by content, which
was checked per commit rather than assumed. The single exception is `4894809`
(2026-05-03), "strip Firebase from website (and remove leaked Web SDK config)",
and it is missing because it was undone **on the branch itself** — `1dbfa20`
(v2.1.0) re-added all nine files, this time including a `firebase-config.js`
holding hardcoded project credentials, so the branch tip and `main` both carry
them. That cluster is ~3,700 lines of dead code, unreferenced by any page, and
`copy_static` publishes it to every built site. Two smaller items are worth
noting even though neither is a rescue in the strict sense: `654939e`'s β_λ
correction was applied to only one of two sites that share a formula id, and the
stale one is still in the current tree; and `36a2400`'s no-LLM-attribution rule
has residue its own sweep did not cover. Everything else on these branches is
either already in `main`, superseded by better work in `main`, or squarely
b₃ = 24-era and must not come back.

## Classification of all 119 commits

| Class | Count |
|---|---|
| BUG_FIX | 47 |
| FEATURE | 37 |
| DOCS | 15 |
| CHORE (release / version bump / housekeeping) | 14 |
| REFACTOR | 3 |
| SUPERSEDED | 1 (`949725f` "Betti survey: b3 = 24 IS realizable") |
| GENERATED_ARTIFACT | 1 (`bdd0c03` regenerated certificates) |
| root commit | 1 (`7a0cc08`) |

Every one of the 14 CHORE commits is a version bump superseded by `main`'s
2.3.1. The 37 FEATURE commits were checked for headline content, not
line-by-line; the ones that carry real machinery (`8328e93` `PhysicsConfig`,
`660642c` semantic tier, `6bd33a8` `topological_flux.json`, `d790db6`
`tests/test_no_silently_dead_imports.py`, `502dd2c` `REQUIRE_OPERATOR`) were
each confirmed present in `main`.

## How "already in main" was established

Ancestry is useless here, so every verdict below rests on content.

1. **Per-commit line presence.** For each BUG_FIX commit, the added lines of its
   `.py` / `.js` / `.yml` / `.toml` hunks were extracted, filtered to lines of
   40+ characters that are not comment-only, deduplicated, and looked up in a
   corpus built from `git grep -h '' origin/main -- '*.py' '*.js' '*.yml'
   '*.toml' '*.html' '*.md' '*.json'`. 30 of the 47 commits scored 84–100%;
   the four outliers were opened by hand (see below); the remaining 13 changed
   only config, data or documentation and were checked individually against the
   working tree.
2. **Deletion regression test.** `git log --diff-filter=D --name-only` over both
   branches yields 46 paths the branches deleted. Intersected with
   `git ls-tree -r --name-only origin/main`, exactly **eight** of those paths are
   still in `main` — and all eight are the Firebase / auth-guard cluster. This
   is the complete set of cleanups `main` does not have.
3. **Outliers opened by hand.** `95362a7` (0%) is one enormous
   `resolution_evidence` JSON string; it is present verbatim in
   `src/metaphysica/simulations/core/canonical_values.py:257`, with `cdc47b5`'s
   later REFINEMENT paragraph appended, which is why the byte match failed.
   `ca23497` (56%) used per-gate imports that `660642c` replaced with the
   `SEMANTIC_EVALUATORS` dict; `main` has the later form. `6a19fe1` (57%): the
   unmatched lines are repeated `status="FITTED"` markers plus a b₃/8 = 3 ANSATZ
   note whose substance survives in `fermion_generations.py` (now labelled
   "UNRULED route; the ruled route is b_2/4"). `2fc7768` (69%): the gate
   execution tiers, prose-drift guard and config alignment are all in `main`;
   the unmatched lines are a LaTeX→Unicode table added to
   `generate_pdf_paper.py`, which is absent from the **branch tip too** — it was
   removed later on the branch, so there is nothing to rescue.

## Every BUG_FIX commit

Branch column: `both` = in the 111 shared commits; `eml` = `eml-render-strict` only.

| sha | branch | subject | what it fixed | verdict | if missing |
|---|---|---|---|---|---|
| `4894809` | both | strip Firebase from website (and remove leaked Web SDK config) | deleted 8 unreferenced Firebase/auth-guard/template-engine modules and the dead `typeof firebase` branch in `simulation-stats.js` | **STILL_MISSING** | **STILL_VALID** — pure hygiene, no physics content, nothing in it depends on b₃. Undone on the branch by `1dbfa20`; see rescue item 1 |
| `3baeb0a` | eml | Apply the seven ratified rulings: honest values replace convenient ones | FALSIFIED status on `neutrino.theta13_derived`, export whitelist that laundered FALSIFIED back to DERIVED, friction through the growth ODE, G12 COMPUTED_FAIL, two-sided `ckm.unitarity_row1` | ALREADY_IN_MAIN (96% line match; `_friction_ode_factor`, `unitarity_row1`, `gate_G32_wz_gut_ratio` all present) | — |
| `3452264` | both | Shadow auditor: 0 conflicts was a curation artifact | auditor reported clean because its input was curated | ALREADY_IN_MAIN (92%; `scripts/audit_shadow_derivations.py`, `tests/test_shadow_no_conflicts.py`) | — |
| `4d36609` | both | Restore `.[dev,sims]` in CI; one sterility writer; pin claim-miss ratios | duplicate sterility writers, unpinned ratios | ALREADY_IN_MAIN (97%; `ci.yml` installs `.[dev,sims]`) | — |
| `90efbf8` | both | Sync rust crate version to 2.3.0 | crate/package version drift | ALREADY_IN_MAIN — all four locations read 2.3.1 | — |
| `8a1987e` | both | Shadow auditor: skip when there is nothing to audit, rather than exit 2 | empty input read as failure | ALREADY_IN_MAIN (100%) | — |
| `572de97` | both | Revert CI to `.[dev]`: the sims extra is unsatisfiable from PyPI | CI could not install | NOT_APPLICABLE — reverted on the branch by `4d36609`; `main` carries the later `.[dev,sims]` state | — |
| `9a66e48` | both | Fix CI build: a skipped optional producer must not fail its consumers | skipped step failed downstream steps | ALREADY_IN_MAIN (100%) | — |
| `1124118` | both | a gating test has been erroring, not gating, since pandas was split out | module-level `import pandas` in `proof_completeness.py` broke a GATING test into 8 collection errors | ALREADY_IN_MAIN — import deferred into `build_ledger()` at line 132; pandas in the `dev` extra with the original comment verbatim | — |
| `674a945` | both | eml-math floor cannot exceed what PyPI serves | unsatisfiable version floor | ALREADY_IN_MAIN — floor now `eml-math>=2.4.0` | — |
| `8328e93` | both | Optional EML must not break the physics; add PhysicsConfig SSOT view | missing optional extra killed 33 pure-arithmetic tests; two modules used EML as a calculator rather than a cross-check | ALREADY_IN_MAIN (100%) — `AbsentEMLNode` at `eml_integration.py:483`, `simulations/core/physics_config.py` present | — |
| `4b1879d` | both | Physics invariants were decorative: 10 tests could not fail | 17 tests ended in `return <verdict>` with no assert, so gauge/Lorentz/SU(3)/parity invariance was never checked; θ was bounded to 174° so obtuse (ghost) bridges were permitted | ALREADY_IN_MAIN (100%) — `tests/test_physics_invariants.py` asserts; `bridge_geometry.py:368` bounds θ at π/2 with the reason inline at 369–370 | — |
| `d4b2b0f` | both | Fix CI collection: optional deps must not break imports | six modules hard-required eml-math at import time | ALREADY_IN_MAIN (100%) | — |
| `95362a7` | both | Correction: the lattice gives 14+14, not 13+13+2 | retracted a false lattice-derivation claim | ALREADY_IN_MAIN — verbatim in `canonical_values.py:257` with `cdc47b5`'s refinement appended | — |
| `b81f4dd` | both | Evidential audit: IDENTITY verdicts, dual sigmas, theta13 NOT_PREDICTED | verdict/sigma bookkeeping | ALREADY_IN_MAIN (98%) | — |
| `c2f79d3` | both | Deferred register cleared + validation-coverage fix + two-time LaTeX sweep | coverage gap, stale LaTeX | ALREADY_IN_MAIN (85%; remainder is prose `main` rewrote) | — |
| `b653a7f` | both | Peer-review cycle: four-domain audit fixes | math/particle/cosmology/geometry defects | ALREADY_IN_MAIN (96%) | — |
| `e0636ff` | both | Backlog burn-down: prose-drift to zero, EML 85/85, validation-fail fixes | drift and failing validations | ALREADY_IN_MAIN (85%) | — |
| `9197faa` | both | higgs_brane_partition: source m_h anchor from ExperimentalDataLoader | hardcoded anchor | ALREADY_IN_MAIN (100%) | — |
| `fb9807a` | both | complete_residue_registry: pull fermion + coupling values via loader | hardcoded values | ALREADY_IN_MAIN (100%) | — |
| `b3dd8e4` | both | appendix_d_tables: read PDG/NuFIT via ExperimentalDataLoader | hardcoded values | ALREADY_IN_MAIN (100%) | — |
| `654939e` | both | Fix appendix formula errors: beta function, spectral residue, Golay CSS label, CKM comment | wrong SM one-loop β_λ gauge terms; Res(ζ_V7, 5/2); unlabelled [[24,12,8]] claim; K=4 → K=6 comment | ALREADY_IN_MAIN (100% of its lines) **but applied to only one of two sites** — see rescue item 2 | — |
| `111f009` | both | move run_eml into GnosisUnlockingSimulationV22 class; fix stale docstrings | method defined outside its class | ALREADY_IN_MAIN (100%) — `gnosis_unlocking.py:1254` | — |
| `7d45e79` | both | Third-pass prose corrections: 124 falsehood patches at authoring source | false claims in generated prose | ALREADY_IN_MAIN (84%; remainder rewritten in `main`) | — |
| `26aa202` | both | Falsification oracle reads live registry; filter blank param chips | oracle read a stale snapshot | ALREADY_IN_MAIN (100%) | — |
| `2fc7768` | both | Second review pass: executed gates, prose-drift guard, PDF math, config alignment | gates asserted rather than executed; no drift guard | ALREADY_IN_MAIN (69%) — gates, guard and config alignment present; the PDF LaTeX→Unicode table is in neither tree | — |
| `df35b9f` | both | Fix n_gen denominator, plot-gallery PDFs, and subpage JSON paths | five surfaces printed `n_gen = chi_eff/(4*b3) = 144/48`, which evaluates to 1.5; manifest fed `.pdf` into `<img src>`; `./AutoGenerated/` 404s on subpages | ALREADY_IN_MAIN (95%) — denominator reads `2*b3` in `abstract.py`/`foundations.py`; `renderable`/`preview_file` in the manifest generator; `site-config.js` root-relative with the reason at lines 74–76 | — |
| `ac50e5b` | both | Physics audit: 104-finding consistency sweep | derivation-chain inconsistencies | ALREADY_IN_MAIN (89%) | — |
| `99d3874` | both | Fix metaphysica.build clobbered by its own submodule import | lazy submodule import rebound the module over the public `build` callable, breaking the API for the rest of the process | ALREADY_IN_MAIN — `__init__.py:102` rebinds, `_build_wrapper` at 115, comment verbatim | — |
| `6a19fe1` | both | particle: PDG 2024 constant drift fixes and label corrections | stale constants, mislabelled derivation statuses | ALREADY_IN_MAIN (57% line match; substance present — `m_h = 125.20 ± 0.11` and the ANSATZ/NUMEROLOGY labels are in `higgs_mass.py` and `fermion_generations.py`) | — |
| `102a601` | both | gauge/su3: alpha_s to PDG 2024, label as ANSATZ | stale α_s | ALREADY_IN_MAIN (100%) | — |
| `cc06afa` | both | gauge: M_W to PDG 2024 (80.3692 ± 0.0133) | stale M_W | ALREADY_IN_MAIN (85%) — `validate_param_references.py:97` reads 80.3692 | — |
| `8caf106` | both | Update physics constants to CODATA 2022 and PDG 2024 | stale constants across the board | ALREADY_IN_MAIN (84%) | — |
| `d3d02de` | both | Label validator scaffolding and fix G51-G55 derivation status | gates mislabelled as derived | ALREADY_IN_MAIN (95%) — 97 certificate JSONs including G51/G55 | — |
| `1500dac` | both | Fix per-card toggle bugs: paper.html handles `<EML>`/`<Normal>` | toggle ignored the tags | ALREADY_IN_MAIN (100%) | — |
| `703cd31` | both | Silence known 404s: bundle 4 placeholder JSONs + fix lightbox close | console 404s, lightbox would not close | ALREADY_IN_MAIN — all four placeholder JSONs bundled; lightbox handling in `pm-plots-loader.js` | — |
| `e41865b` | both | Fix `js/js/math-mode.js` 404 + MathJax skipHtmlClasses warning | doubled path segment | ALREADY_IN_MAIN — zero `js/js/` and zero `skipHtmlClasses` hits in the tree | — |
| `ea2b5e9` | both | Fix PyPI publish: only workflow.yml does Trusted Publishing | two workflows both claimed the trusted publisher | ALREADY_IN_MAIN — `workflow.yml` is the only file referencing the publish action | — |
| `0ee0ce3` | both | Fix 4 production site bugs: parameters, simulations, EML switcher | broken pages | ALREADY_IN_MAIN (100%) | — |
| `035bca6` | both | Fix ReferenceError: treeData is not defined on formulas.html | undefined `treeData` left by a pre-compact-schema refactor threw whenever a formula had a tree but no LaTeX | ALREADY_IN_MAIN — `formulas.html:2408` uses `purePm \|\| flowPm` with `inflateCompactTree`, comment preserved | — |
| `a11eb89` | both | Release audit: nav, mismatches path, viz-index plot gallery | broken nav and paths | ALREADY_IN_MAIN — `mismatches.html`, `visualization-index.html` present and patched | — |
| `ae41e49` | both | remove UTF-8 BOM from pyproject.toml | BOM broke pip's TOML parser | ALREADY_IN_MAIN — no BOM on the current file | — |
| `ebc6998` | both | switch build backend to maturin; CI to Rust+cibuildwheel | wheels could not build | ALREADY_IN_MAIN (100%) — `build-backend = "maturin"` | — |
| `2e31c94` | both | remove arithmos_core path dep | path dependency broke PyPI builds | ALREADY_IN_MAIN — no `arithmos` reference in `pyproject.toml` | — |
| `61fdbb6` | both | fix version assertion for v2.0.0-alpha.0 | crate/package assertion mismatch | ALREADY_IN_MAIN — the assertion is in `rust/physica_core/src/lib.rs` and reads 2.3.1 | — |
| `55fa8da` | both | skip optional-dep tests cleanly on slim installs | tests failed instead of skipping | ALREADY_IN_MAIN (100%) | — |
| `4099b9b` | both | skip test_unity collection when matplotlib not installed | collection error on slim installs | ALREADY_IN_MAIN — `tests/test_unity.py:23` uses `pytest.importorskip` | — |

**Totals: 46 ALREADY_IN_MAIN (one of which, `572de97`, is NOT_APPLICABLE because
the branch itself reverted it), 1 STILL_MISSING.**

## Rescue list

Three items, in priority order. Item 1 is a rescue in the strict sense. Items 2
and 3 are not — they are defects in the current tree that this survey turned up
while verifying a branch commit, which is worth more than a padded list. All
three are physics-neutral: none of them touches b₂, b₃, χ_eff, the bulk
signature, a gate verdict or a test's strictness.

### 1. Remove the dead Firebase / auth-guard cluster and the credentials it carries (P1)

**Why.** Nine files under `src/metaphysica/website/js/` implement a Firebase
auth/analytics/Firestore integration that nothing uses. Verified: `grep -rln
"firebase\|auth-guard"` across `src/metaphysica/website/Pages/` and
`src/metaphysica/website/*.html` returns **zero** hits, and no JS outside the
cluster imports any of them — they only import each other. One of them,
`firebase-config.js`, hardcodes a Firebase Web SDK config block: an `apiKey`,
`authDomain`, `projectId` (`principia-metaphysica`), `storageBucket`,
`messagingSenderId`, `appId` and `measurementId`. The values are in that file;
they are not reproduced here.

This is shipped, not merely committed. `pyproject.toml` sets
`[tool.maturin] python-source = "src"`, so the whole package directory goes into
the wheel, and `src/metaphysica/website/__init__.py` lists `"js"` in `_BUNDLED`
and copies it with `shutil.copytree`, so **every `metaphysica.build()` publishes
`/js/firebase-config.js` to the static site**.

**History.** `4894809` (2026-05-03) deleted eight of these files and gave the
reasoning in full: the Firebase Web `apiKey` is a documented public client
identifier and security comes from Firestore rules, but baking
project-specific identifiers into a published wheel is bad hygiene regardless,
and it recommended rotating the values in the Firebase Console as
defence-in-depth. `1dbfa20` ("v2.1.0: triple-track validation + Tier 1-3 theory
closures") then re-added all nine as a bulk `A` of the website tree —
`firebase-config.js` for the first time; `git ls-tree 4894809~1` confirms it was
untracked before that. `git log -S` on the key string in `origin/main` returns
only `fedfec8`, the root snapshot, so it was never added to `main` deliberately.

**What to change.**

- Delete these nine files from `src/metaphysica/website/js/`:
  `auth-guard.js`, `auth-guard-ENHANCED.js`, `firebase-analytics.js`,
  `firebase-auth.js`, `firebase-config.js`, `firebase-data.js`,
  `firebase-page-loader.js`, `firebase-references.js`, `pm-template-engine.js`
  (~3,700 lines).
- Before deleting, re-run the reference check so the removal is evidenced rather
  than trusted:
  `grep -rn "firebase\|auth-guard\|pm-template-engine" src/metaphysica/website/`
  should afterwards return hits only in `src/metaphysica/website/CONTRACTS.md`,
  which lists these files as consumers of `AutoGenerated/*.json` in its
  producer/consumer table — those two table rows need the stale consumers struck
  out in the same change.
- `simulation-stats.js` needs nothing: `4894809`'s other half, the unreachable
  `typeof firebase !== 'undefined'` branch, is already absent from `main`.
- Rotate the Firebase project's Web SDK values in the Firebase Console, and
  check the Firestore security rules, treating the published values as exposed
  since 2026-05 (`1dbfa20`). Deleting the file does not un-publish what any
  previously built site served.
- `4894809` also checked that `data-speculation`-style CSS provisions with no
  emitter were not left behind as traps; the analogous check here is that no CSS
  or HTML selector depends on an auth-guard class. Nothing in the tree does.

### 2. Finish `654939e`'s β_λ correction at its second site (P2)

**Why.** `654939e` ruled that formula R.2's gauge quartic terms are
`(3/8)g₁⁴ + (9/8)g₂⁴ + (3/4)g₁²g₂²`, not `(9/5)g₁⁴ + (9/4)g₂⁴` — the SM one-loop
cross-term was missing. Its diffstat touched `appendix_r_vacuum_stability.py` by
one line. But the file carries the id `quartic-beta-function-v19` **twice**:

- `src/metaphysica/simulations/PM/paper/appendices/appendix_r_vacuum_stability.py:494`
  — the section block's `content=`, **corrected**;
- the same file, line 889 — the `Formula(...)` object's `latex=`, still
  `\frac{9}{5}g_1^4 + \frac{9}{4}g_2^4` **and** `\frac{9}{5}g_1^2` inside the
  `λ(...)` bracket.

So one formula id resolves to two different renderings, and the uncorrected one
is on the `Formula` object whose `latex` field is what downstream consumers read
(`generators/eml_render_validity.py:255` reads `latex`;
`generate_arithma_dependency_walker.py:168` falls back to it). The branch tip has
the identical defect — `git show origin/eml-render-strict:<that file> | grep -n
"beta_\\lambda = "` shows the same split at its lines 490 and 876 — so this is
not a regression in `main`, it is a fix that was applied to the display copy and
missed the registry copy.

**What to change.** In
`src/metaphysica/simulations/PM/paper/appendices/appendix_r_vacuum_stability.py`,
line 889, replace the `Formula.latex` gauge terms with the ruled form so the two
sites agree:

```
\beta_\lambda = \frac{1}{16\pi^2}\left[ 24\lambda^2 - 6y_t^4
  + \frac{3}{8}g_1^4 + \frac{9}{8}g_2^4 + \frac{3}{4}g_1^2 g_2^2
  + \lambda(12y_t^2 - \frac{9}{5}g_1^2 - 9g_2^2) \right]
```

Keep the `λ(...)` bracket as it stands unless it is separately ruled on —
`654939e` corrected only the quartic terms, and its ruling should not be widened
here. Add a test that the two occurrences of `quartic-beta-function-v19` in this
file carry the same gauge terms, so the pair cannot drift apart again; that is a
new assertion, not a relaxation of an existing one.

Note the `24λ²` coefficient in this formula is annotated in the source as
`= b3` ("the leading coefficient = b3") and exposes a `b3_leaf` in its
`eml_tree_str`. That annotation is b₃ = 24-era numerology and is **not** part of
this change — 24 is the correct SM coefficient on its own terms. Flagging it so
it is not silently carried as evidence for anything.

### 3. Clear the local-path residue `36a2400` did not cover (P3)

**Why.** `36a2400` established the rule that shipped source carries no LLM/AI
attribution, and swept 15 modules plus `RELEASE.md` and two bundled
`AutoGenerated` assets. Its scope was the "ASSERTION ASSESSMENT" /
"INDEPENDENT ASSESSMENT" docstring headers. Six lines in four files still bake
local agent-workspace and developer-machine paths into published docstrings, in
both `main` and the branch tip:

- `src/metaphysica/simulations/PM/geometry/re_t_sector.py:86` — a
  `C:\Users\Andrew\.claude\plans\...` plan reference
- `src/metaphysica/simulations/PM/cosmology/inflation.py:108` — the same path,
  plus an `H:\Github\...\PossibleImprovements.txt` source spec below it
- `src/metaphysica/simulations/visualizations/plot_wz_evolution.py` and
  `src/metaphysica/generators/generate_pdf_paper.py` — same pattern

**What to change.** Replace each with a neutral in-repo reference, the way
`36a2400` did: name the sprint and row (e.g. "Sprint 4 task #3 — non-perturbative
Re(T) stabilization") and drop the path. A machine-local path in a PyPI wheel is
dead information to every reader anyway. Find them all with
`grep -rn 'C:\\\\Users\|H:\\\\Github' src/metaphysica/ --include=*.py`.

This is documentation wording only. It says nothing about `re_t_adoption`, which
is OPEN.

## Deliberately not rescued

Nothing here is discarded silently; each is listed with the reason.

**Everything b₃ = 24-era.** These branches end 2026-08-25 / 2026-08-29 and
predate the 2026-09-22 ruling that adopted (b₂, b₃) = (12, 43). Their physics
work is written against b₃ = 24 throughout. Not rescued, individually:

- `df35b9f`'s n_gen display fix. The *idea* — a printed formula must evaluate to
  its own stated result — is permanently valid and is the kind of defect worth
  hunting again. The *code* is stale: it settles `n_gen = chi_eff/(2*b3) =
  144/48 = 3`, and `main` has already moved past it. `fermion_generations.py:601`
  now labels that route "UNRULED route; the ruled route is b_2/4". Re-asserting
  `chi_eff/(2*b3)` would undo that. χ_eff is OPEN; this report does not rule on
  it. Current-model equivalent: keep `main`'s ruled/unruled labelling and check
  the *arithmetic self-consistency* of whatever denominator the ruled route
  states, which is the transferable part of the fix.
- `949725f` "Betti survey: b3 = 24 IS realizable — the seed survives". Wholly
  superseded; the seed did not survive.
- `95362a7` / `cdc47b5` / `57235b5` / `9fe44c0` / `d7290ad` / `f649f01`, the
  (26,2)-vs-(24,2) lattice and spinor argumentation. All of it is already in
  `main` verbatim in `canonical_values.py` as recorded resolution evidence,
  which is the right place for it: `CANON["bulk"]` is 26D at (24,2), ruled
  2026-08-31, with the lattice obstruction (24 − 2 ≡ 6 mod 8) unanswered and the
  TCS obstruction (b₂ + b₃ must be odd) independent and still open. Nothing to
  move; nothing to re-argue here.
- `0fb9a1e` / `36484fb` two-time adoption, `225a7da` 42-channel selection rule,
  `2c6da17` / `d609191` RP gate, `6ac56ba` Cl(12,1): all FEATURE work already in
  `main`.

**The ~28 `.bak` files.** `main` tracks zero (`git ls-tree -r origin/main | grep
-c '\.bak$'` → 0); the branch tip tracks 23. Untracked editor backups; the
correct state is `main`'s.

**The three `src/metaphysica/website/AutoGenerated/*.md` generated reports and
`bdd0c03`'s regenerated certificates.** Build output, regenerated by
`metaphysica-build`, and stale at that. `334c2aa` and `d6c9825` on these very
branches were themselves commits to stop tracking regenerated output; rescuing
generated artifacts would work against their own direction.

**`docs/archive/*` sprint exit gates and roadmaps, and
`docs/RULINGS_ASSESSMENT.md`.** Spent planning documents. The one that still
matters, the 2026-08-25 rulings assessment, is already in `main` at
`docs/history/RULINGS_ASSESSMENT_2026-08-25.md`. The live register remains
`PrincipiaMetaphysica/docs/OUTSTANDING_ISSUES.md`.

**The four `src/metaphysica/simulations/tests/*.md` test-suite documents.** They
describe suites as they stood in August. `main`'s `tests/` tree has 147 files the
branch does not have; the descriptions would be wrong on arrival.

**`2fc7768`'s LaTeX→Unicode table for PDF math.** Absent from the branch tip as
well as from `main` — removed on the branch after the commit that added it, and
`main`'s `generate_pdf_paper.py` escapes raw LaTeX into a `.latex` block
instead. There is no version of this to rescue.

**`ca23497`'s per-gate import form.** Superseded by `660642c`'s
`SEMANTIC_EVALUATORS` dict, which is what `main` has at
`generate_72_certificates.py:518`. Its one durable idea — fall back to the
bundled `data/parameters.json` when the build-output copy is absent — is also
already in `main`.

**All 14 version-bump commits** (`84a2fbf`, `9fec57f`, `ec5fc39`, `68f3a21`,
`2db52d9`, `072de4f`, `5298af4`, `842216f`, `d779eb8` and the release commits).
Superseded by 2.3.1, which is in sync across all four locations:
`pyproject.toml:7`, `rust/physica_core/Cargo.toml:3`,
`src/metaphysica/__init__.py:59` and the version assertion in
`rust/physica_core/src/lib.rs`.

**`d1b3ef1`'s header cleanup** is in `main` and needs no action —
`pm-header.js:16` and `143` carry the dated removal notes, `pm-common.css:1028`
the CSS note, and `pm-header.js:286` still clears the persisted
`pm-speculation` override. `js/math-mode.js` survives in both trees as an
unimported module; since the branch tip has it too, it is not a regression and
is out of scope here.

## Reproducing this

```bash
git merge-base origin/main origin/continue/gates-and-rulings   # exit 1
git merge-base origin/main origin/eml-render-strict            # exit 1
git log --oneline origin/eml-render-strict..origin/continue/gates-and-rulings
git log --oneline origin/continue/gates-and-rulings..origin/eml-render-strict

# the complete set of branch cleanups main lacks
git log --diff-filter=D --name-only --pretty=format:"" origin/eml-render-strict \
  | grep -v '^$' | sort -u > /tmp/deleted
git ls-tree -r --name-only origin/main | sort > /tmp/main
comm -12 /tmp/deleted /tmp/main          # -> the 8 Firebase / auth-guard paths

# the leak entered git at 1dbfa20, and reached main only via the root snapshot
git log --oneline --diff-filter=A origin/eml-render-strict \
  -- src/metaphysica/website/js/firebase-config.js
git log --oneline -S'<the apiKey string>' origin/main     # -> fedfec8 only

# nothing references the cluster
grep -rln "firebase\|auth-guard" src/metaphysica/website/Pages/ src/metaphysica/website/*.html
```
