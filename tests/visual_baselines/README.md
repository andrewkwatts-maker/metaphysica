# Visual Regression Baseline

Baseline screenshots captured by `scripts/visual_regression.py` for every
`Pages/*.html` rendered by the metaphysica static site builder. These PNGs
are the reference set the CI visual-regression gate diffs candidate
captures against.

## Provenance

- **Captured:** 2026-06-12 against `h:/Github/PrincipiaMetaphysica`
- **Builder:** `metaphysica` v2.1.0, `metaphysica.build(fast=True)`
- **Browser:** Chromium via Playwright 1.60.0 (Chrome 148)
- **Viewport:** 1280 x 800, `full_page=True` (with viewport-only fallback)
- **Sprint:** T3 task #7 — establishes the baseline produced by T2.7.

The 18 PNGs **are** committed and live in this directory; the earlier note
saying they were staged-but-uncommitted is out of date. They date from
2026-06-12 against metaphysica v2.1.0, so they predate the two-time (24,2)
ruling and every page that renders the bulk signature, the gate dashboard or
the global fit will legitimately differ from them. **Recapture before treating
a diff as a regression** — the commands are under *Regenerating* below.

## File inventory

18 baseline PNGs, one per page under `Pages/`:

| File | Size (bytes) | Capture mode |
|---|---:|---|
| `appendices.png` | 1,622,034 | full-page |
| `beginners-guide.png` | 14,858,803 | full-page |
| `certificates.png` | 4,873,417 | full-page |
| `consciousness-speculative.png` | 1,503,105 | full-page |
| `falsification.png` | 948,078 | full-page |
| `faq.png` | 8,655,125 | full-page |
| `formulas.png` | 441,329 | full-page |
| `foundations.png` | 343,114 | full-page |
| `geometric-framework.png` | 3,045,195 | full-page |
| `mismatches.png` | 708,573 | full-page |
| `paper.png` | 79,741 | viewport-only (fallback) |
| `parameters.png` | 919,926 | full-page |
| `philosophical-implications.png` | 36,566,285 | full-page |
| `references.png` | 4,772,945 | full-page |
| `sections.png` | 2,463,008 | full-page |
| `simulations.png` | 7,065,848 | full-page |
| `theory-diagrams.png` | 2,193,319 | full-page |
| `visualization-index.png` | 2,610,029 | full-page |

### Note on `paper.png`

`paper.html` exceeds Chromium's 16384 px full-page screenshot limit, so the
capture script falls back to a viewport-only screenshot (1280 x 800) for
this page. The fallback path was added to `visual_regression.py` in this
sprint so a failed full-page capture no longer aborts the whole run. When
diffing, the candidate must use the same fallback to stay aligned; this is
automatic because the script tries `full_page=True` first on every page.

## Smoke-diff result (2026-06-12)

Captured a second set under `visual_candidate_smoke/` and diffed:

```
worst page diff: 0.019% (faq)
all 18 pages   : <= 0.019%
fail threshold : 0.5%  -> PASS
```

Non-zero values come from MathJax / chart rendering timing jitter on
pages with heavy async content (`faq`, `paper`, `philosophical-implications`,
`certificates`). All are well below the 0.5% gate.

## Regenerating

```
# fresh build of the live website
METAPHYSICA_OUT=h:/Github/PrincipiaMetaphysica python -c \
  "import metaphysica; metaphysica.build(out_dir='h:/Github/PrincipiaMetaphysica', fast=True)"

# capture baseline
python h:/Github/metaphysica/scripts/visual_regression.py capture \
  --root h:/Github/PrincipiaMetaphysica \
  --out  h:/Github/metaphysica/tests/visual_baselines \
  --port 8077

# verify against a fresh second capture
python h:/Github/metaphysica/scripts/visual_regression.py capture \
  --root h:/Github/PrincipiaMetaphysica \
  --out  h:/Github/metaphysica/visual_candidate_smoke \
  --port 8078
python h:/Github/metaphysica/scripts/visual_regression.py diff \
  --baseline  h:/Github/metaphysica/tests/visual_baselines \
  --candidate h:/Github/metaphysica/visual_candidate_smoke \
  --fail-threshold 0.5
```
