# Consolidation to main (2026-10-31 .. 11-01)

Goal: every metaphysica worktree merged into main and closed, main pushed, CI green,
PyPI release published, PrincipiaMetaphysica site rebuilt and pushed.

## State found
- 24 worktrees. 21 already merged into main; rank had uncommitted work; glow (2) and gates (3) unmerged.
- CI red on main since 2026-10-04. PyPI at 2.3.0; tag v2.3.1 never got a Release.
- Site repo 47 commits ahead of origin (last deploy 2026-10-04).

## Done
- [x] Commit rank (137dd42); merge rank, glow, gates into main (conflict: confinement allowlist, kept both).
- [x] CI "Build site": closed_form degrades without a usable arithma (1695203).
- [x] CI tests (b725890): plots extra in CI; fork detector sees table-driven resolve
      (action forks, g2_construction wired); arithma-tree tests skip without a usable backend;
      derivation comments on the 288 = 125 + 163 literals. CI green on 3.11/3.12/3.13.
- [x] All 24 worktrees removed, local branches deleted (none were on origin); main only.
- [x] metaphysica-app: 1 unpushed commit pushed.
- [x] v2.4.0 tagged, GitHub Release, PyPI 2.4.0 published (sdist + mac/linux/windows wheels).
- [x] Site: 47 commits + gates G1 note pushed; GitHub Pages deployed.
- [x] Site regenerated from engine v2.4.0 and pushed (604cc0e): 260 formulas OK (was 206), arithma trees kept.

## Facts worth keeping
- PyPI arithma 2.0.2 is a stub (`Expression = None`); 2.0.4 is excluded by the pin (fixed-point range).
  CI and `pip install metaphysica[full]` therefore run without the arithma leg.
- The site is rebuilt from a local engine checkout (local arithma works), not from the PyPI
  install that build.bat uses; a PyPI-based build would drop the arithma trees.
- Site deploys via GitHub Pages on push to PrincipiaMetaphysica main.

## Left for the owner
- Zenodo upload (RELEASE.md step 10, manual).
- RELEASE.md audit hits that predate this release: 26 hype-word hits (33 at v2.3.0), e.g.
  paper/discussion.py:386 "proof-killer", paper/integrity.py:774 "not tuned";
  proof_completeness_ledger.md lacks "fitted decomposition" wording; PMNS split unverified.
- Remote branch origin/core-paper is fully merged into main; delete it if no longer wanted.
- A working arithma release on PyPI (wide range) would let CI check the arithma leg again.
