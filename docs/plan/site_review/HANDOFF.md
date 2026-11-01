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

## Watch
- Full `pytest tests/` failed one test during F3: `tests/test_derivation_chains.py::test_real_chains_match_declared_formulas`, probably from F4's uncommitted `generate_eml_trees.py`. Recheck after F4 lands.
- metaphysica CI run 41266065464 (commit 3f239e9, "ci: install eml-math from PyPI") was in progress; check it with `gh run view 41266065464`.
- The local server on :8000 serves `../PrincipiaMetaphysica`; lanes copy templates into it for previews (uncommitted there; the final rebuild overwrites them).

## Next
1. When F1, F4 and F5 have landed: run the full `pytest tests/` (in the background, read the tail), then launch F2 (brief in `BRIEFS.md`, wave 2).
2. After F2: merge `site-review` into main, push, and delete the branch. Check CI. Rebuild the site from the local engine (`python -m metaphysica.build --out ../PrincipiaMetaphysica`, about 10 min, in the background). Commit it in PrincipiaMetaphysica as "Regen from <sha>: site review" with `--no-verify`, push, and confirm the Pages deploy.
3. Tick the progress list in `SITE_REVIEW_2026-11-01.md`.
4. Owner question open: the personal email shown in plain text on the index and paper pages.
