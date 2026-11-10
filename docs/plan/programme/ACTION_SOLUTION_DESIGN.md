# P4 design: solving the adopted master action (planner, 2026-11-11)

Adopted statement (D-029, `master-action-26d`):
S_26 = Int d^26X sqrt|G| [ (M_*^24/2) R_26 + Psi-bar i Gamma^M D_M Psi ], Psi Weyl of Cl(24,2).

"Solve" = field equations, a vacuum that satisfies them, the massless spectrum on that vacuum,
the 4D effective action, and what each says against observation. Every step is a ladder check
that can fail. Nothing below is tuned; where the solution does not reach a published number the
number is relabelled, not rescued.

## Finding 1 (computed): the spinor term as written is identically zero
With two time directions the Spin(24,2)-invariant Dirac adjoint is Psi-bar = Psi^dag Gamma^0 Gamma^0'.
That product commutes with the chirality operator, so for ONE Weyl spinor:
- Psi-bar Gamma^M D_M Psi = 0 identically (kinetic term vanishes);
- Psi-bar Psi is non-zero (a mass term is allowed).
This is the reverse of the one-time rule the engine states in five places ("m and the quartic
vanish for a Weyl field": `actions/spinors.py:65`, `master_ladder_steps.py:25,111`,
`master_ladder.py:40`, `master_action.py:488,506,542`, `config/core_formulas.py:864`).
Rule: with t times, the Hermitian same-chirality kinetic bilinear exists iff t is odd, the
Hermitian mass bilinear iff t is even.
The non-vanishing covariant kinetic term of one Weyl spinor at (24,2) is the holomorphic one,
(1/2) Psi^T C Gamma^M D_M Psi + h.c.: C Gamma^M restricted to one chirality is non-zero and
symmetric for D = 2 mod 8 (so it survives for anticommuting Psi); Psi^T C Psi vanishes.
Evidence: `evidence/weyl_bilinear.py --full` and `evidence/weyl_holomorphic.py --full`, explicit
8192-dimensional gamma matrices at (24,2); controls (3,1), (9,1), (5,1), (2,2), (4,2), (8,2).
Same result as Bars' two-time field theory, which needs Psi-bar X-slash D-slash Psi for this reason.

Ruling R1 (owner, 2026-11-11; record as D-030: "non-vanishing holomorphic form becomes the
default path; leave the old one as a switch, default off, to revisit if it is needed"): keep the 4096-component Weyl field
(a Fact that must not drift) and write its kinetic term in the non-vanishing form. Fork
`action_bulk_spinor` gains the option `weyl_holomorphic` (adopted); `weyl` stays in the
catalogue with its now-failing check (never deleted); `dirac` stays evaluable (for a Dirac field
the Hermitian kinetic term pairs opposite chiralities and is non-zero). The reasons given on
2026-11-01 for dropping m and lambda were wrong at two times; they stay dropped because they
have no coefficient source (the readmission rule), and the text says that instead.

## Field equations
- Metric: M_*^24 (R_MN - (1/2) G_MN R) = T_MN[Psi].
- Spinor: Gamma^M D_M Psi = 0.
- Vacuum: Psi = 0 and R_MN = 0.

## Vacuum
M_26 = M_13 x M_13' (each (12,1)); M_13 = R^(3,1) x K_2 x Y_7. A product metric is Ricci-flat
iff every factor is. R^(3,1): flat. Y_7: holonomy G2 implies Ricci-flat (Bonan 1966), on the
closed-geometry certificate. K_2: compact, orientable, Ricci-flat forces genus 1 by
Gauss-Bonnet, so K_2 = flat T^2. S^2 fails (R = 2/r^2; it would need a flux or a cosmological
term, and the action has neither).
Ruling R2 (owner, 2026-11-11: "make it a switch and make flat torus the default path"): the
residual space is a fork `residual_space` with options `flat_t2` (adopted: forced
by the field equations), `s2` (evaluated, fails the vacuum check), `undeclared` (the state
until now, kept).

## 26D -> 13D (owner item 6) is not solved by this action
The second factor carries its own time. Evaluated options, fork `second_time`:
- `compact_time`: a field on a timelike circle of radius R has 4D modes with m^2 = -n^2/R^2. Fails (tachyonic tower).
- `noncompact_product`: Vol_13 diverges, so M_13^11 = M_*^24 Vol_13 is infinite. Fails.
- `sp2r_invoked` (adopted, the existing Fact "Sp(2,R) is invoked, not derived"): the action has
  no Sp(2,R) gauge structure, so this is an ASSUMPTION. `owner_item_6` keeps failing and says so.
Consequence, stated wherever the chain is stated: the model is solved from the 13D (12,1) action
down; the 26D lift rests on this assumption.

## Massless spectrum from the 13D action on T^2 x Y_7 (b1 = 0, b2 = 12, b3 = 43 on the active path)
| 13D field | on Y_7 (G2) -> 6D | on flat T^2 -> 4D |
|---|---|---|
| metric | graviton, 0 vectors (b1 = 0), b3 moduli scalars | graviton, 2 vectors (b1(T^2)), 3 + b3 scalars |
| spinor (64) | 1 Dirac spinor (one parallel spinor) | 2 Dirac spinors |
4D content: 1 graviton, U(1)^2, b3 + 3 = 46 real scalars, 2 Dirac fermions. All massless, all
neutral, no potential. Chiral index 0 (odd internal dimension; the T^2 step is flat).
No SU(3), no SU(2), no Yukawa couplings, no Higgs potential.
b2 does not enter: the action has no form field, so the 12 harmonic 2-forms give no vectors.

## 4D effective action
S_4 = Int d^4x sqrt(-g) [ (M_Pl^2/2) R - (M_Pl^2/2) G_ij(s) ds^i ds^j - (1/4) K_ab(s) F^a F^b
      + sum_f psi-bar_f i gamma^mu D_mu psi_f ],  V(s) = 0,
M_Pl^2 = M_13^11 Vol_7 Vol_2 (and M_13^11 = M_*^24 Vol_13 under the item 6 assumption).
G_ij is the L2 metric on the moduli (Y_7: harmonic 3-forms; T^2: area and tau).

## What the solution says against observation
1. Volume modulus. Reducing R on M_4 x (b(x) K_n) gives Brans-Dicke with omega = -1 + 1/n, so
   gamma_PPN = (1 + omega)/(2 + omega) = 1/(n + 1). n = 9: omega = -8/9, gamma = 0.1, for test
   matter minimally coupled to the 4D block of the metric. Cassini: gamma - 1 = (2.1 +- 2.3)e-5.
   Taken as the complete theory, the minimal action is excluded. It needs a modulus potential,
   which is a readmission (definition, coefficient source, check that can fail). Re(T) is already
   a labelled calibration of an OPEN modulus; this is the same gap seen from the action.
2. V = 0: the vacuum is Minkowski. No dark energy, no inflation from this action. The
   quintessence and slow-roll rows are not consequences of it.
3. No Standard Model gauge group, chirality or generations. n_gen = b2/4, the gauge couplings,
   masses and mixings in the registry are an ansatz layer over the topological integers. They are
   tested directly against data (the scoreboard); they are not derived from S_26.
Paper wording follows from this: two layers, named as such. Layer 1, the action and its solution
(this file). Layer 2, the ansatz formulas and their scoreboard, falsified rows included.

## What is settled and what is not (owner question, 2026-11-11)
Settled by proof or explicit computation, so no code fix changes it:
- no non-abelian gauge field from the metric on Y_7 (compact, Ricci-flat, b1 = 0: no Killing vector);
- chiral index 0 (13 is odd: the 64-component shadow spinor reduces to Dirac pairs in 4D);
- b2 counts nothing in this action (no form field), so n_gen = b2/4 has no dynamical carrier;
- no potential, so the moduli are massless.
These are the Kaluza-Klein no-go results (Witten 1981, 1983) met inside this model.
Not settled until the fix waves are done: the score of the ansatz layer (it still mixes
retired-seed numbers, double counts and mislabelled inputs). Not solved by any fix: 26D -> 13D.

## P4c: evaluate what each readmission candidate would give (after the fix waves)
The no-go names the missing ingredients. Each becomes an evaluable option, never an adopted one
without the readmission rule (definition, coefficient source, check that can fail):
- a form field (`action_bulk_sectors=flux_f4`): b2 vectors and b3 axions through `zero_modes`;
- a gauge sector (`e8xe8_ym`) and the KK tower (`kk_tower`);
- the singular limit of Y_7: the 12 in b2 = 12 is the 12 singular T^3 loci of T^7/(Z2)^3 before
  resolution (b3 = 7 + 3 b2). In 11D M-theory such loci carry SU(2) gauge fields and conical
  points carry chiral matter (Acharya 1998; Atiyah and Witten 2001). That is literature about a
  different theory, quoted as a lead: whether the 26D (24,2) action has an analogue is open.
Output: one table per option: vectors, gauge algebra, chiral index, moduli, potential, verdict.

## Code (executors; generic first, PM binding second)
Generic, `src/metaphysica/actions/` (no PM imports):
- `spinor_bilinears.py`: `weyl_bilinears(s, t)` by rule (hermitian/holomorphic x kinetic/mass ->
  "nonzero" | "zero" | "total_derivative"); `explicit_weyl_bilinears(s, t)` from sparse gammas
  (test oracle, the two evidence scripts). `Term` gains `bilinear: Optional[str]`
  ("hermitian" | "holomorphic"). `check_spinor_terms` becomes signature-aware and also checks kinetic terms.
- `field_equations.py`: equations per field as LaTeX and a `vacuum_checks(action, factors)`
  returning Checks: every factor Ricci-flat (explicit metric through `curvature.ricci_scalar`
  where one is given, otherwise a named measured certificate), matter fields zero, no potential term.
- `surfaces.py`: Gauss-Bonnet, `ricci_flat_genus()` -> 1; control: genus 0 fails.
- `controls/volume_modulus.py`: omega(n) from the symbolic reduction (sympy), gamma_PPN(n);
  correspondence n = 1 -> omega = 0 (Kaluza-Klein, Overduin & Wesson 1997); failing control.
- `zero_modes.py` already covers "flat" and "G2"; add `chiral_index(internal_dim, holonomy)`.
PM binding, `simulations/PM/gauge/`:
- `master_ladder_steps.py`: A26 kinetic term carries its bilinear from the fork; A6 declares the
  b3 moduli (fork-read), A4 declares 2 vectors, b3 + 3 scalars, 2 Dirac spinors; comments fixed.
- `master_ladder.py`: `_internals()` reads `residual_space`; new checks `vacuum:*`,
  `spinor_kinetic:A26`, `zero_modes:*` on the T^2 step, `second_time:*`.
- `master_action_solution.py` (new, under 300 lines): registers the field equations, vacuum,
  spectrum counts, omega, gamma_PPN and M_Pl relation as formulas and parameters with status
  DERIVED-FROM-ACTION, and the section text for the paper's action section.
- Fork catalogue: `action_bulk_spinor` (+`weyl_holomorphic`), `residual_space`, `second_time`.
Acceptance: `zero_modes:scalar` passes; failing checks are exactly `nonabelian_gauge_source`,
`owner_item_6`, and the new `ppn_gamma_unstabilised` (a prediction that fails against data, kept);
every option of the three forks evaluates to a verdict; tests cover each rule with a failing control.
