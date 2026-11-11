Next step: collect the running workflows, finish wave A, merge to `main`; agents as needed (owner lifted the cap of 3 on 2026-11-11).
1. Workflows launched and not yet collected when this was written (a result may be lost with the
   session; each can be resumed or rerun from its script):
   - `workflows/wave_a_xv.js`, run wf_86516413-505, args `{base: "5ae9e51", scratch: <scratchpad>}`
     (the first run, wf_ea28d7ae-969, did no work: its agents read the owner's "wrong chat sorry",
     meant for a message about another project, as a withdrawal; the script now says so in its
     context line and runs one small chain as a canary before the fan-out):
     XV-01 to XV-16 and XB-08 to XB-10 in chains, two review lenses per chain, repair, re-check, a
     scribe for `progress/validation-data.md` and `progress/build-fresh.md`. Check with
     `git log --oneline 79cd6ad..HEAD | grep "close-out"`; an item with no commit is rerun.
   - lane close-outs, run wf_db2bff49-97f: actions-generic done, algebra-portals-viz and
     path-core finishing (see `progress/<lane>.md`, heading "Close-out").
   - P7 history lanes, run wf_1b85d461-836 (`workflows/p7_history_lanes.js`, 16 lanes): files land
     in `docs/plan/programme/ideas/` (uncommitted). Missing lanes are rerun with
     `args: {chains: [[<lane>], ...]}` (lane names: `HISTORY_REVIEW.md`). Then commit `ideas/`,
     run `workflows/p7_history_merge.js`, commit `IDEAS_LEDGER.md`.
   - P9 and P10 design panel, run wf_9b3d158a-1ae: proposals and the two designs land in
     `docs/plan/programme/design/` (`P9_PATH_BUILDS.md`, `P10_READER_LEVELS.md`); commit them.
2. Wave A: the items under "Wave A, what is left" below, in order.
3. The end state is a release and a live site: `PROGRAMME_2026-11-11.md`, "Release and publish".

# Handoff, 2026-11-11

Plan: `PROGRAMME_2026-11-11.md` (phases P1 to P12). Rules: its "Rules for every lane", and
`FIX_BRIEFS.md` rules 1 to 12. Briefs are one target each; executors read narrowly.

## State
- Branch `site-review`; `main` = `origin/main` = b820864, CI red there. The cause (statistics
  step needs the rigor report; CANON bootstrap on an empty output directory) is fixed on
  `site-review` (XB-01 0348545, XB-02 bc63bb4).
- Fresh-clone fast build (`--keep-going`): 26 failed steps at 205b1f4, 4 at f860be6, 2 at 8aebd1f
  ("Publish the path ranking", "Parameter ledger"); both are fixed since (XB-04 f09ebed, XB-07
  64000da). A fourth build and a full pytest were started in the clone: `pmv_build4.log` and
  `pmv_pytest1.log` in the scratchpad. The render gate passes in the clone once `npm ci` has run
  in `tools/texcheck`; CI skips that gate (wave C item).
- XB tail (wf_24c2a391-ab1) is done: XB-03 2eb361f, XB-04 f09ebed, XB-07 64000da; review found one
  out-of-scope file, repaired in fcffa04; its medium and low findings are rows XB-08 to XB-13 of
  `WAVE_A_CLOSEOUT.md`. Known and not XB's: `tests/test_free_variable_ledger.py` (2, stale
  `free_variables.json` in the default output directory) and `tests/test_derivation_chains.py`
  (3, baseline).
- Owner rulings 2026-11-11 (D-030), in code from wave B: `action_bulk_spinor` default
  `weyl_holomorphic` (old `weyl` kept, off); fork `residual_space` default `flat_t2`; fork
  `neutrino_ordering` with `unruled` in force; Standard Model numbers are an ansatz layer.
- Release and the live site push are authorised (owner, 2026-11-11) once the five gates of
  "Release and publish" hold. Nothing is released or pushed live yet.

## Wave A, what is left
1. Collect the workflows above; rerun what is missing; deal with every `still_open` and `blocked`.
2. After the path-core lane has finished: XB-06, XB-11, XB-12 (one executor each, then a reviewer).
3. Rebuild in a clean clone until the fast build has no failed step (`WAVE_A_CLOSEOUT.md`, Gate).
4. Full pytest in the clean clone, in the background (70 to 86 minutes); triage by lane; one fix
   round; final fresh build and pytest.
5. Merge `site-review` into `main`, push, look at CI once, delete `site-review`, remove the clone.
6. Update the P2 and P7 rows of the programme; refine the wave B briefs in `FIX_BRIEFS.md` from
   the "Later waves" table of `WAVE_A_CLOSEOUT.md` and the three rulings.

## After that
Wave B (L2 geometry, L3 cosmology, L4 gauge-action with P4b, then L5 particle), wave C (L8 paper
cut, L9 pipeline, L10 website with P10 reader levels), wave D (size splits, P5 data check, path
ranking sweep), release R1 (2.5.0 unless the owner names another), then P8 model space, P9 a
build per path with the site switcher, P11 findings paper, release R2.

## For the owner (not blocking)
- The eight decisions in `WAVE_A_CLOSEOUT.md`, "Owner decisions".
- Sibling repositories: Arithma 14 behind and 1 ahead; EML-Spectral and periodica-app one
  unpushed commit each; `claude/sheets` branch and the `periodica-sheets` worktree.

## Scratch (session-bound, rebuildable)
`C:/Users/Andrew/AppData/Local/Temp/claude/5c9ec1ed0a1c70e1/b8e64ed1-91e9-4f2c-85ca-5fe89f0d5611/scratchpad`:
`pmv/` clean clone for the CI replica (needs the `.pyd` copied in and `npm ci` in
`tools/texcheck`), `pmv_build1.log` to `pmv_build4.log`, `pmv_pytest1.log`, `hist/site_old.git`
and `hist/engine_old.git` for P7 (rebuild: `HISTORY_REVIEW.md`, Sources).
