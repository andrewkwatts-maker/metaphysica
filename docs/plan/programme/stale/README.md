# Stale artifacts (kept, not published)

- `path_ranking_137dd42.json`: the path ranking committed in 137dd42 as
  `src/metaphysica/data/path_ranking.json`. It fails the wave A ranking contract (`verdict`,
  `unranked`, `not_evaluated`, `option_effects`) and its scores predate the wave A scoring
  fixes, so the build's "Publish the path ranking" step no longer sees it and skips. A fresh
  ranking comes from `python -m metaphysica.testground rank` over a sweep (wave D, P3).
