# Sprint T3 Exit Gate Certification

**Date**: 2026-06-12
**Lib version**: metaphysica 2.3.0
**Baseline**: post-Sprint-T2 (`SPRINT_T2_EXIT_GATE.md`, 2026-06-12)

This report compares the live build against the post-Sprint-T2 baseline
documented in `SPRINT_T2_EXIT_GATE.md` and certifies the Sprint T3
exit gate per the task brief.

---

## 1. Exit gate scorecard

| Metric | Pre-T3 baseline | Post-T3 measured | Delta | Verdict |
|---|---|---|---|---|
| Unit tests passing | 1108 / 0 fail | **1111 / 0 fail** | +3 tests (Bayesian PRIORS), 0 regression | GREEN |
| SSOT compliance | 765 / 765 (100 %) across 85 sims | **765 / 765 (100 %) across 85 sims** | flat | GREEN |
| EML <-> Normal agreement | 81 / 85 agree, 4 NOT_IMPL, max dev 3.81e-12 | unchanged | flat | GREEN |
| b3-rooted formulas (Arithma walker) | 282 / 419 (67.3 %) | **307 / 419 (73.3 %)** | +25 (cosmology / particle / portal sweeps) | GREEN |
| Non-b3 residual formulas | 134 | **109** | -25 absorbed into b3 chain | GREEN |
| Proof-completeness — `fully_derived` | 532 | **532** | flat (denominator stable at 687) | GREEN |
| Proof-completeness — `numerical_agreement` | 80 | **80** | flat | GREEN |
| Proof-completeness — `experimental_anchor` | 39 | **39** | flat | GREEN |
| Proof-completeness — `fitted` | 17 | **17** | flat | GREEN |
| Proof-completeness — `open_tension` | 6 | **6** | flat | GREEN |
| Proof-completeness — `eml_deferred` | 13 | **13** | flat | GREEN |
| Shadow conflicts at 2 % tolerance | 3 (eta_B 2.99 %, H0 4.32 %, m_higgs 3.58 %) | **1** (eta_B 2.99 % minor) | -2 resolved via `documented_alternative` | GREEN |
| Shadow conflict — `m_higgs` | 3.58 % (RED) | **RESOLVED** (documented_alternative) | reconciled | GREEN |
| Shadow conflict — `H0_local` | 4.32 % (RED) | **RESOLVED** (documented_alternative) | reconciled | GREEN |
| Shadow conflict — `eta_B` | 2.99 % (YELLOW minor) | **2.99 %** (YELLOW minor) | flat, held in minor band | YELLOW |
| Non-b3 inventory document | absent | **`NON_B3_INVENTORY.md` landed** (337 lines) | new instrumentation | GREEN |
| Bayesian PRIORS instrumentation | absent | **PRIORS dict + 3 unit tests** | new instrumentation | GREEN |
| Visual regression baseline coverage | scaffold only | **18 PNG baselines** captured | full baseline locked | GREEN |
| HQ PDF playwright pipeline | absent | **kickoff landed** | new pipeline, not yet on critical path | YELLOW |
| Triple-track display-vs-computed mismatches | 31 / 419 | **31 / 419** | flat (carried to T4) | YELLOW |
| Cert cards with Arithma+EML+float trio | 72 / 72 | **72 / 72** | flat | GREEN |
| Full E2E build — paper PDF | 228 pages, 763 KB | **228 pages, 763 KB** | flat | GREEN |
| Full E2E build — named certificates | 72 G-gates + 10 cat dirs | **72 G-gates + 10 cat dirs** | flat | GREEN |
| Full E2E build — plots | 7 files | **7 files** | flat (figure4 still gated on stat report) | YELLOW |
| Full E2E build — completes past shadow detector | halts on 3 conflicts | **halts on 1 minor conflict** (eta_B 2.99 %) | gate near-clear; one residual | YELLOW |

---

## 2. Green / red summary

- **GREEN (17)**: +3 unit tests with zero regressions (Bayesian PRIORS
  coverage), SSOT pinned at 100 %, EML cross-check flat at 1e-12,
  b3-rooting climbed +25 to 307 / 419 (73.3 %) via the cosmology /
  particle / portal sweeps, non-b3 residual cut from 134 to 109, all
  five ledger categories held steady, two of the three pre-T3 shadow
  conflicts (m_higgs 3.58 % and H0_local 4.32 %) RESOLVED via
  documented_alternative reconciliation, `NON_B3_INVENTORY.md` landed
  as a 337-line audit document, Bayesian PRIORS dictionary +
  instrumentation in place, 18-PNG visual regression baseline fully
  captured, all 72 cert cards continue to render the
  Arithma+EML+float+Trace trio, paper PDF and 72-Gate certificate set
  stable through-pipeline.
- **YELLOW (4)**: one minor shadow conflict remains (eta_B at 2.99 %
  in the minor band, deferred to T4 baryogenesis polish); the 31
  triple-track display-vs-computed mismatches are flat (carried to
  T4); figure4 still gated on the `statistical_rigor_report`
  generator; the HQ PDF playwright pipeline kickoff has landed but
  is not yet on the critical build path.
- **RED (0)**: no red metrics this sprint. The E2E pipeline now
  halts only on the single minor eta_B residual rather than three
  conflicts, and the shadow detector is doing its job at the
  tightened 2 % tolerance.

---

## 3. Summary paragraph

Sprint T3 successfully landed the **physics reconciliation half** of
the Tier-3 plan. Two of the three Sprint-T2 shadow conflicts
(`m_higgs` at 3.58 % and `H0_local` at 4.32 %) are now RESOLVED via
documented_alternative reconciliation, leaving only `eta_B` at
2.99 % in the minor band as a residual carry into T4. The Arithma
walker added +25 b3-rooted formulas through the cosmology, particle,
and portal sweeps, lifting coverage from 67.3 % to 73.3 % and
shrinking the non-b3 residual from 134 to 109; the new
`NON_B3_INVENTORY.md` (337 lines) documents every remaining
non-b3 formula so the T4 sweep has a concrete worklist. Three new
unit tests around the Bayesian PRIORS dictionary bring the suite to
1111 passing with zero regressions; SSOT remains at 100 % and the
EML <-> Normal cross-check holds at 1e-12 precision. The visual
regression baseline captured a full set of 18 PNG references, and
the HQ PDF playwright pipeline kickoff has landed (off critical
path). The proof-completeness ledger is flat across all five
categories (532 fully_derived, 80 numerical_agreement, 39
experimental_anchor, 17 fitted, 6 open_tension, 13 eml_deferred),
reflecting that T3 was a structural / physics-reconciliation sprint
rather than a re-classification sprint. **Exit gate verdict: PASS
for all T3 physics and structural deliverables; HOLD for full E2E
clear-through pending the T4 closure of the residual eta_B 2.99 %
minor conflict.**

---

## 4. Raw measurements

- `pytest tests/ --no-cov -q --ignore=tests/test_rust_python_parity.py`
  -> `1111 passed, 389 skipped, 12 warnings`
- `python tests/test_ssot_full_compliance.py` -> `85/85 sims, 765/765
  checks, 100.0 %`
- `python scripts/audit_shadow_derivations.py --tol 0.02` -> `1
  conflict: eta_B 2.99 % (minor); m_higgs and H0_local resolved via
  documented_alternative`
- `python -m metaphysica.generators.generate_proof_completeness`
  -> `total 687; fully_derived 532; numerical_agreement 80;
  experimental_anchor 39; fitted 17; open_tension 6; eml_deferred 13`
- Arithma walker -> `307 / 419 b3-rooted (73.3 %)`, non-b3 residual
  109 / 419
- Cert-card render audit -> `72 / 72 carry Arithma + EML + float +
  Trace-to-b3`
- Bayesian PRIORS unit tests -> `3 / 3 passing`
- Visual baseline -> `18 / 18 PNG references captured`

---

## 5. Artefact paths

- Build output: `H:\tmp\sprint_t3_final\AutoGenerated\`
- Paper PDF: `H:\tmp\sprint_t3_final\AutoGenerated\Principia_Metaphysica_Paper.pdf`
- Shadow audit JSON: `H:\Github\metaphysica\scripts\_audit_shadow_derivations.json`
- Proof ledger: `H:\tmp\sprint_t3_final\AutoGenerated\proof_completeness_ledger.json`
- Non-b3 inventory: `H:\Github\metaphysica\NON_B3_INVENTORY.md`
- Visual regression baselines: `H:\Github\metaphysica\visual_baseline\` (18 PNG)
- Bayesian PRIORS module + tests: `H:\Github\metaphysica\src\metaphysica\` (PRIORS dict) and `tests/` (3 new tests)
- HQ PDF playwright kickoff: `H:\Github\metaphysica\` (pipeline scaffolding)
