# Programme: audit, generalise, close, solve, test, cut (2026-11-11)

Owner request (two messages, one programme): review the whole engine and site for inconsistency,
fluff and repetition; validate and improve the simulations; generalise them (SOLID) with every
geometric path switchable and evaluable; close the geometric model and solve the master action;
find falsifiability and compare against data; cut the paper to its core concepts, concise and
academic; make sure the backend generates params, sections, paper and website data correctly.
Standing rule: units, formulas, comments and descriptions match the active path everywhere.

Branch: `site-review` (not pushed). Nothing is pushed, merged or published without the owner.

## Rules for every lane
- At most 3 agents at once. Each lane owns its files; `git add <paths>`, never `-A`; no push.
- Commits: owner as author and committer, no AI attribution.
- Numbers come from the registry or artifacts, never literals. Path-dependent values are read
  through `simulations.core.variants.resolve` or the registry.
- Falsified candidates and withdrawn claims are kept (ledger), never deleted.
- A test per fix; functions of 60 lines or fewer; fail early.
- Outcome stop: after the acceptance test passes or 15 edits, commit, write progress, stop.

## Phases
| # | Phase | Output | State |
|---|-------|--------|-------|
| P1 | Audit (14 read-only lanes, verified) | `audit/<lane>.md`, `AUDIT_SUMMARY.md` | running (wf_9190d4ca-a7f) |
| P2 | Fix lanes from the audit | commits, a test per fix | waiting on P1 |
| P3 | SOLID split; every fork option evaluable | `PATHS.md`, sweep artifacts | waiting on P2 |
| P4 | Close the geometry; solve the master action | `ACTION_SOLUTION.md`, ladder checks | design in progress |
| P5 | Falsifiability and data comparison | `FALSIFIABILITY.md`, paper section 6 table | waiting on P4 |
| P6 | Core paper; generators verified; local rebuild; handoff | `core_paper.json`, `HANDOFF.md` | last |

## Known before the audit
- Chi2 headline 2.24e9 over 63 rows is not a units bug: `electromagnetic.alpha_inv` and
  `geometry.alpha_inverse` are one quantity scored twice, each at 33,457 sigma on the seed-43
  path. Fix: score it once; the Facts in `docs/claude-context.md` and the CHANGELOG still carry
  the retired seed-24 numbers (126,749 over 65; theta_13 0.805 sigma) and must be re-stated.
- `cosmology.speed_of_light_derived` (1.79e8 against 299,792,458) is a UNIT_CHECK row at 402,385 sigma.
- Neutrino ordering: the 0.0605 eV sum implies normal ordering; `neutrino.ordering` says INVERTED.
- Ladder today: 9 open terms, 3 failing checks (`nonabelian_gauge_source`, `owner_item_6`,
  `zero_modes:scalar`); established checks 29 reproduced, 0 failing, 16 blocked.
- Paper: 96 sections, 90,369 words; the 14 core sections are 27,424 words.

## P4 design note (planner)
"Solve" means, for S_26 = Int sqrt|G| [(M_*^24/2) R + Psi-bar i Gamma D Psi]: field equations,
a vacuum that satisfies them, the linearised spectrum on that vacuum, and the 4D effective
action, each as a ladder check that can fail. Expected honest outcome, to be confirmed by code:
vacuum = Ricci-flat product with the holonomy-G2 Y_7 (Psi = 0); massless 4D content = graviton,
b3 moduli scalars with no potential, no non-abelian gauge fields (a compact holonomy-G2
manifold has no continuous isometries, and the action has no form field), non-chiral fermions.
Where the solution does not reach a tabulated Standard Model number, the paper says so and the
number is labelled an ansatz over the topology, not a consequence of the action.
