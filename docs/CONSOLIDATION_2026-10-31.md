# Consolidation to main (2026-10-31)

Goal: every metaphysica worktree merged into main and closed, main pushed, CI green,
PyPI release published, PrincipiaMetaphysica site rebuilt and pushed.

## State found
- 24 worktrees. 21 already merged into main; rank had uncommitted work; glow (2) and gates (3) unmerged.
- CI red on main since 2026-10-04 (step "Build site"). PyPI at 2.3.0; tag v2.3.1 has no Release.
- Site repo 47 commits ahead of origin (last push 2026-10-04).

## Steps
- [x] Commit rank (137dd42); merge rank, glow, gates into main (conflict: confinement allowlist, kept both).
- [ ] Reproduce and fix CI "Build site" failure.
- [ ] Full pytest; push main; CI green.
- [ ] Remove worktrees and local branches (none exist on origin).
- [ ] Version bump + GitHub Release -> PyPI (needs `gh auth login`).
- [ ] Site: build.bat against new PyPI version, commit, push.
