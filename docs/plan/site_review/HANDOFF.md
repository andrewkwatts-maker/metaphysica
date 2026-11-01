# Handoff: site review (2026-11-01)

Start: `docs/plan/SITE_REVIEW_2026-11-01.md`, `BRIEFS.md` (this folder), `docs/plan/MASTER_ACTION_SELECTION_2026-11-01.md`, `git log --oneline main..site-review`.

## State
- Branch `site-review` in the main checkout (no worktrees), not pushed. main = origin/main.
- Phase 1 done: R1/R2/R3 findings in this folder (77 rows).
- F3 paths: landed, 11b7913 (9 Playwright and 3 JS tests pass).
- F1 stale content: told to checkpoint (over the turn cap); its progress goes in `F1_PROGRESS.md`. Hand any rest to a fresh executor with a narrow brief.
- F4 EML: running. Scope: withhold policy covering formulas, `pm-eml-offer.js`, formulas.html tiles and optgroup, generic `pm-eml-diagram.js`, `MASTER_ACTION_DIAGRAM_ID` (default `pneuma-master-action-v23` until F5).
- F5 master action and path: running. It waits for F1 and F4 to commit before editing `config/core_formulas.py` and the diagram constant.
- Owner decision made by the planner on request: minimal action (gravity plus Weyl spinor), main path with action forks none/weyl/24/mostly_plus_mtw, one neutrino sum of 0.0605 eV, Re(T) check aligned with D-015. See the selection doc.
- Chi2 headline: validator 126,749 over 65 rows; the other definitions get scope labels (F2).

## F1 checkpoint (4f7be9d, f210314, e6855ef)
Partly done; the rest is listed in `F1_PROGRESS.md`. Give it to a fresh executor as F1b with one target per item. Open items:
- bridge-channel footer links: the generator is not in the engine (the page is built-only). Find its writer or drop the page.
- "125 constants" and the remaining v24.2 strings in the paper.
- The `abstract.py` registry literals (`compression_ratio=131`, `validation.*`).
- The scope wording for "3030.1 over 4 dof".
- Tests for the conclusions lookup, the mismatches skip and the plots loader.
- Screenshots.

**Blocker before publishing: the headline chi2.** `headline_stats.py` binds to the artifacts: chi2 ≈ 2.24e9 over 63 rows, 36/42 gates locked. CHANGELOG [2.4.0] says 126,749 over 65 and 41/43. A chi2 of 2.2e9 means at least one row is off by about 47,000 sigma, which is almost certainly a units or uncertainty bug. Find the dominating rows in `statistical_rigor_report.json` (an Opus or planner task), fix the cause with a test, then reconcile the CHANGELOG. Do not publish the site with the 2.2e9 headline.

## F4 landed (c19b83e)
198 formulas withheld (89 `*_leaf`, 33 with no operator, 4 AST reprs, 72 gate formulas sharing one placeholder). `pm-eml-offer.js`, `pm-eml-diagram.js`, stat tiles and the optgroup are in. Open items:
- `eml_param_crosscheck.write_offer_policy` rewrites `eml_offer_policy.json` and drops the `formulas` section if it runs after `generate_eml_trees.py`. Merge, or fix the build order, with a test.
- The hand-written EML cards on index, foundations and parameters are not on `isOffered` (add `data-eml-id`; F2).
- The gate placeholder is hard-coded at `appendix_f_72gates.py:1858`; remove it at the source.
- `certificates.html` `getEMLCodeForGate` static text (F2).
- The 7 `eml_latex`-only formulas lost their pill. Accept, or give them trees.

## F5 landed (39259e1, 0274f13; PrincipiaMetaphysica 65ee733 = D-029, not pushed)
`none` is adopted. `master-action-26d` is in `master_action.py` with a tree, and the core_formulas entry is a plain Formula. `MASTER_ACTION_DIAGRAM_ID` now points at it. Neutrino: one claim, 0.0605 eV. The Re(T) check applies D-015. Path `4f53cda18c2baa0c` now evaluates as consistent, with 9 open terms and the 3 known failing checks. Tests are in `tests/test_master_action_selection.py`. Open items:
- **Owner ruling needed: neutrino ordering.** The 0.0605 eV arithmetic gives normal ordering, but `neutrino.ordering` is registered as INVERTED, where the floor is about 0.10 eV. Under inverted ordering, 0.0605 is impossible. Either the ordering row is wrong, or the selection doc's neutrino choice is. Do not publish until it is ruled.
- `path_ranking.json` is stale: it still shows rank 3 and `consistent: False`. Regenerate it with `python -m metaphysica.testground rank` over the sweep run directories.
- The two intermediate neutrino rows still say DERIVED until a rebuild.
- The full suite had 26 failures before F5's last fixes. F5 fixed its own failures and 3 others. The rest were not from this lane: `test_derivation_chains` (3), `test_duplicate_statements`, `test_formula_lint`, `test_output_dir_binding` (2), `test_prose_lint`, `test_published_formula_coverage`, `test_rust_python_parity` (2), `test_superseded_surfaces`, `test_tex_renders` (3). `test_eml_math_floor_is_met` is fixed by f104065. Run the full suite next and triage each against main.
- Push PrincipiaMetaphysica 65ee733 together with the site regen.

## Watch
- `tests/test_derivation_chains.py` fails on its own with 3 failures (kill-switch rows). Find which commit on `site-review` caused it (F1's `4f7be9d` is the likely one); fix it before merging.
- `test_action_forks.py::test_adopted_option_of_each_fork_is_the_ladder_today` fails while F5 changes `adopted.py`; F5 should update it.
- Full `pytest tests/` failed one test during F3: `tests/test_derivation_chains.py::test_real_chains_match_declared_formulas`, probably from F4's uncommitted `generate_eml_trees.py`. Recheck after F4 lands.
- CI run 41266065464 on 3f239e9 failed on one stale guard (it required a git install of eml-math, but 2.4.0 is on PyPI). Fixed by 827fbfe on main (pushed) and f104065 on `site-review`; its CI run 41270345785 is green. Main is now 06d9671 (the finished salvage report was dropped).
- Doc tidy-up: `docs/` holds 12 audit and reference reports. Fold any that are finished into one archive once nothing cites them; `CONSOLIDATION_2026-10-31.md` is still cited by the site review plan.
- The local server on :8000 serves `../PrincipiaMetaphysica`; lanes copy templates into it for previews (uncommitted there; the final rebuild overwrites them).

## Next
1. When F1, F4 and F5 have landed: run the full `pytest tests/` (in the background, read the tail), then launch F2 (brief in `BRIEFS.md`, wave 2).
2. After F2: merge `site-review` into main, push, and delete the branch. Check CI. Rebuild the site from the local engine (`python -m metaphysica.build --out ../PrincipiaMetaphysica`, about 10 min, in the background). Commit it in PrincipiaMetaphysica as "Regen from <sha>: site review" with `--no-verify`, push, and confirm the Pages deploy.
3. Tick the progress list in `SITE_REVIEW_2026-11-01.md`.
4. Owner question open: the personal email shown in plain text on the index and paper pages.
