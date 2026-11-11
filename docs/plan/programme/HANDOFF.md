Next step: start P7 and finish the wave A close-out, three agents at most in total.
1. P7 lanes (read-only, two agents): `Workflow({scriptPath: "docs/plan/programme/workflows/p7_history_lanes.js", args: {chains: [["site-2025-11","site-2025-12a","site-2025-12b","site-2026-01a","site-2026-01b","site-2026-02_06","site-2026-07_11","site-decisions"],["engine-2026-03_08","engine-2026-09","engine-2026-10","engine-2026-11","engine-pre-rewrite","engine-docs","site-issues","code-catalogue"]]}})`.
   Check first that the scratch history repositories exist (`HISTORY_REVIEW.md`, Sources); rebuild them if not.
2. Wave A (one agent): the items under "Wave A, what is left" below, in order.
3. When the P7 lanes are done: commit `docs/plan/programme/ideas/`, then run
   `docs/plan/programme/workflows/p7_history_merge.js` (one agent at a time), commit `IDEAS_LEDGER.md`.

# Handoff, 2026-11-11

Plan: `PROGRAMME_2026-11-11.md` (phases P1 to P11). Rules: its "Rules for every lane", and
`FIX_BRIEFS.md` rules 1 to 12. Briefs are one target each; executors read narrowly.

## State
- Branch `site-review`; `main` = `origin/main` = b820864, CI red there. The cause (statistics
  step needs the rigor report; CANON bootstrap on an empty output directory) is fixed on
  `site-review` (XB-01 0348545, XB-02 bc63bb4).
- Fresh-clone fast build (`--keep-going`): 26 failed steps at 205b1f4, 4 at f860be6, 2 at 8aebd1f
  ("Publish the path ranking" = XB-04, "Parameter ledger" = XB-07). The render gate passes in the
  clone once `npm ci` has run in `tools/texcheck`; CI skips that gate (wave C item).
- Uncommitted in the tree and not mine to commit: `simulations/base/established.py`,
  `simulations/core/FormulasRegistry.py` (present since the session start; ask the owner).
- Owner rulings 2026-11-11 (D-030), in code from wave B: `action_bulk_spinor` default
  `weyl_holomorphic` (old `weyl` kept, off); fork `residual_space` default `flat_t2`; fork
  `neutrino_ordering` with `unruled` in force; Standard Model numbers are an ansatz layer.
- Holds: no site publish with the 2.2e9 chi2 headline or before the neutrino ordering is ruled;
  no version bump.

## Wave A, what is left
1. Results of the two close-out workflows (see "Workflow results" below).
2. Rebuild in a clean clone until the fast build has no failed step (`WAVE_A_CLOSEOUT.md`, Gate).
3. XV validation-data close-out (XV-01 to XV-16 without XV-08) and XB-06, one target per brief,
   then an adversarial check.
4. Full pytest in the clean clone, in the background (70 to 86 minutes); triage by lane; one fix
   round; final fresh build and pytest.
5. Merge `site-review` into `main`, push, look at CI once, delete `site-review`, remove the clone.
6. Update the P2 row of the programme; refine the wave B briefs in `FIX_BRIEFS.md` from the
   "Later waves" table of `WAVE_A_CLOSEOUT.md` and the three rulings.

## After that
Wave B (L2 geometry, L3 cosmology, L4 gauge-action with P4b, then L5 particle), wave C (L8 paper
cut, L9 pipeline, L10 website with P10 reader levels), wave D (size splits, P5 data check, path
ranking sweep), then P8 model space, P9 a build per path with the site switcher, P11 findings paper.

## For the owner (not blocking)
- The eight decisions in `WAVE_A_CLOSEOUT.md`, "Owner decisions".
- Sibling repositories: Arithma 14 behind and 1 ahead; EML-Spectral and periodica-app one
  unpushed commit each; `claude/sheets` branch and the `periodica-sheets` worktree.

## Scratch (session-bound, rebuildable)
`C:/Users/Andrew/AppData/Local/Temp/claude/5c9ec1ed0a1c70e1/b8e64ed1-91e9-4f2c-85ca-5fe89f0d5611/scratchpad`:
`pmv/` clean clone for the CI replica (needs the `.pyd` copied in and `npm ci` in
`tools/texcheck`), `pmv_build1.log` to `pmv_build3.log`, `hist/site_old.git` and
`hist/engine_old.git` for P7.

## Workflow results
Not in yet when this was written: lane close-outs (actions-generic, algebra-portals-viz,
path-core) and the XB tail (XB-03 done 2eb361f; XB-04, XB-07, then verify and repair).
