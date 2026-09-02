# Assessment: Two Times, One Per Shadow — 26D (24,2) vs the Canonical 27D (24,1,2)

**Date:** 2026-08-18 · **Status:** ADOPTED 2026-08-19, **RULED 2026-08-31**
(`CANON["bulk"]`; `variants.json` fork `bulk_signature`, status RULED,
selected `24_2`). This file is kept as the record of *how the case was argued*.
**Two of the arguments below did not survive and are marked; read the
"Costs on the final ruling" section at the foot before quoting anything here.**
**Question:** would giving each 13D shadow its own time dimension — bulk signature (24,2) — improve the framework?
**Method:** the same constraint-board used for the canonical-value rulings (minimal spare variables; every claim recomputed), plus the mechanism proposed in arXiv:2606.12457 (Pettini, "Quantum Entanglement Beyond Kinematics: A Dynamical Hypothesis in (3,2)-Dimensional Spacetime").

---

## Verdict in one paragraph

On the framework's own elegance criterion, the two-time structure **scores strictly better than the current canonical bulk**: it removes two inserted structures (the (0,2) sampler pair and the D_crit-vs-D_bulk terminological split), resolves four audit-documented contradictions outright, and *upgrades* the Pneuma spinor story (4096 becomes the chiral Weyl spinor of Cl(24,2) instead of the non-chiral odd-dimension spinor of Cl(24,1)). The costs are real but bounded: a large-but-guarded text migration (the SSOT drift auditors exist for exactly this), and the obligation to implement — or honestly label as STRUCTURAL — the Sp(2,ℝ) constraint that controls the second time's ghost degrees of freedom. Recommendation: **adopt, pending the author's ruling**, with the migration path below.

## The arithmetic (recomputed)

| Quantity | Current: 27D (24,1,2) | Two-time: 26D (24,2) |
|---|---|---|
| Bulk dimension | 27 = b₃ + 3 ("forced") | **26 = b₃ + 2 ("forced")** ~~— same as D_crit~~ (D_crit claim WITHDRAWN, see foot) |
| Critical-dim argument | separate object (26 ≠ 27), needs a terminological split | ~~identical to the bulk — one argument, not two~~ **WITHDRAWN**: the two-time critical dimension is 27–28, at (25,2)/(26,2) |
| Shadow accounting | 12+12 space + 1 shared time = 25 ≠ 27 → needs +2 sampler pair | **(12,1) + (12,1) = 26 = bulk exactly; each shadow is literally half the bulk, time included (26/2 = 13)** |
| Pneuma spinor 4096 | Cl(24,1), odd D → 2¹² = 4096, **no chirality** (Weyl doesn't exist in odd D) | Cl(24,2), even D → Dirac 2¹³ = 8192, **Weyl = 4096 — the Pneuma spinor becomes chiral**, matching the chirality gates (G20, G66) that currently sit on a non-chiral spinor |
| Reality conditions | Majorana available | (s−t) mod 8 = 6: Majorana yes, Weyl yes, Majorana-Weyl no — state honestly |
| Per-shadow bookkeeping | 13 = 4 + 7 + 2 (canonical ruling) | **unchanged** — each (12,1) shadow reduces exactly as ruled |
| Z₂ shadow swap | swaps space content only (time is shared) | **swaps everything including time — full shadow symmetry** |

## What it resolves (audit register items)

1. **C-1 bulk-dimension row** (25D/26D/27D chaos; b₃+2 and b₃+3 both "forced") — dissolved: one dimension, one derivation.
2. ~~**The "+2 justified two incompatible ways" finding** (1+0 counting vs Sp(2,ℝ)) — the Sp(2,ℝ) justification becomes the *correct* one: this is exactly Bars' two-time physics, which requires signature (d,2) and uses Sp(2,ℝ) gauge symmetry to remove the ghost degrees of freedom of the second time. Bars' gauge-fixed 1T sectors are literally called **"shadows"** in that literature — the framework's own vocabulary.~~ **WITHDRAWN** (see foot): Sp(2,ℝ) gauging gives *one* 24D shadow, not two 13D ones, so the framework's shadows do not inherit the ghost-freedom theorem, and the "+2" still carries three inconsistent readings.
3. **The superseded-v15 contradiction** (two-time text coexisting with the Euclidean-bridge mechanism) — the v15 (24,2)/Sp(2,ℝ) text stops being a fossil and becomes the structure; the "Euclidean bridge" recasts as propagation in the *other shadow's time* (see Pettini alignment below).
4. **The non-chiral-spinor tension** — chirality is load-bearing (chiral orthogonality gates, one preserved G₂ spinor), yet the current Cl(24,1) construction cannot produce a Weyl spinor. Under (24,2) the 4096 count *is* the chiral half.

## Alignment with arXiv:2606.12457

Pettini's mechanism, in the framework's terms:
- An extra **temporal** dimension carries a massless bulk field sourced by preparation/measurement events, producing equal-time correlations between separated branes **causally** (null geodesics in the extra time), with no controllable superluminal signaling.
- His key argument: an extra **spatial** dimension cannot mediate such correlations without opening superluminal shortcuts. The framework's current inter-shadow correlator — the (2,0) **spacelike** sampler pair / Euclidean bridges — is exactly the construction this argument indicts.
- Under the two-time structure, inter-shadow correlations (the sampler machinery, the Orch-OR two-layer story, four-dice sampling) travel through the second time: causally clean, and the Z₂ warped-product setup he uses matches the shadow swap.
- **Borrowable falsifiable prediction:** Pettini's cross-pair correlations between independent Bell pairs — a concrete experimental discriminator the framework currently lacks in this sector.

## Costs (stated fully)

1. **Ghost/unitarity obligation.** Two times are only viable with the Sp(2,ℝ) constraint actually imposed (Bars) — otherwise CTCs/ghosts. The framework must either implement the constraint analysis or label the sector STRUCTURAL (the honesty convention applies; an asserted "ghost-free" would be flagged by our own audit).
2. **Migration blast radius.** "27D", "M²⁷(24,1,2)", "∫d²⁷X", and "Cl(24,1) → 4096" appear across the paper, site, and registry. Mitigation: this is exactly what the SSOT machinery was built for — one canonical ruling change, then the prose-drift auditor enumerates every stale "27" context (add `27`-context rules the way 0.57/0.2257 were handled).
3. **Sampler-narrative recast.** S^(2,0) sampler data fields and four-dice sampling must be rewritten as extra-time dynamics. Pettini's paper is a ready template (bulk field sourced by events, brane-projected).
4. **Emergent shared time needed.** Observers experience one time; under 2T our shadow's t is a gauge slice (Bars), and the "unified time" of the current story becomes emergent — which finally gives the retired thermal-time/KMS machinery a legitimate job (thermal average over the two shadow times) instead of a fossil.

## Migration path (if adopted)

1. Add `bulk` ruling v2 to `canonical_values.py`: 26D (24,2), shadows (12,1)×2, spinor "Weyl of Cl(24,2) = 4096", with the old 27D entry moved to `superseded` ("sampler-pair formulation").
2. Extend the prose-drift auditor with context rules for `27D`/`(24,1,2)`/`Cl(24,1)` (flag-unless-annotated, as for 0.2257).
3. Recast master-action displays (∫d²⁶X), the descent-chain text, and the sampler sections; resurrect + label the Sp(2,ℝ) constraint section (STRUCTURAL until derived).
4. Add a beacon: `dim_bulk == b3 + 2 == 2 × dim_shadow` (live, trivially checkable, locks the accounting forever).
5. Cite Pettini (2026) for the extra-time correlation mechanism and adopt the cross-pair Bell test as a falsification entry.

## Recommendation

Adopt Option B. It is the rare change that *deletes* postulates: two inserted structures go away, four register contradictions close, the spinor derivation strengthens, and the framework gains a falsifiable prediction. The decision is the author's — this document is the assessment requested, and nothing in the canonical table has been changed by it.


---

## Costs on the final ruling (added 2026-09-02) — two arguments above are withdrawn

The recommendation was adopted, and the geometry is now 26D at (24,2) with
13D(12,1) shadows. But a literature pass on 2026-08-20 challenged the bulk on
three independent grounds, and the ruling that followed on 2026-08-31 chose
option (c) — *keep (24,2), and pay for it*. What that costs is recorded in
`CANON["bulk"]["ruling"]`, and two of the table rows above are among the
casualties. They stay on the page, struck rather than deleted, because a
withdrawn argument is a record.

**~~"26 = b₃ + 2, the same as D_crit — one argument, not two"~~ — WITHDRAWN.**
Bars & Kounnas (hep-th/9705205) give the *two-time* bosonic critical dimension
as **27 or 28**, at (25,2)/(26,2): a second time *raises* it. D_crit = 26
belongs to the one-time string at (25,1), where 26 = 24 transverse + a
**lightcone pair** (one space, one time) — not two times. "D_bulk = D_crit"
and "signature (24,2)" were claims from two different theories, and the
coincidence the table above treats as the headline elegance win is not one.

**~~"this is exactly Bars' two-time physics, which uses Sp(2,ℝ) to remove the
ghosts"~~ — the ghost-freedom appeal is WITHDRAWN.** Sp(2,ℝ) gauging removes
exactly two dimensions, taking (24,2) → **one 24D shadow of signature (23,1)**,
not two 13D(12,1) shadows. Bars' shadows are different gauge-fixings of the
*same* bulk, not halves of it, so the framework's shadows do not inherit his
ghost-freedom theorem. Cost 1 in the list above ("implement the constraint or
label it STRUCTURAL") was therefore the right instinct and remains live:
Sp(2,ℝ) is **invoked, not derived**, and nothing derives it from b₃ = 24.

**Unanswered, and the ruling accepts that it is unanswered.** An even
unimodular lattice of signature (p,q) exists iff p − q ≡ 0 (mod 8). For
**(24,2), 22 ≡ 6**, so no even self-dual lattice exists in this signature and
there is no modular-invariant lattice compactification there. Both rejected
alternatives pass — (25,1) → 24 ≡ 0 (the Lorentzian Leech construction the
bosonic string actually uses) and (26,2) → 24 ≡ 0. The framework must answer
this independently; it has not.

**Also withdrawn from the "+2" narrative.** The `+2` carried three inconsistent
readings across the framework's own formulas (lightcone pair / two-time +
bridge / 2 × Sp(2,ℝ)); at most one can be right. And
`beacon.two_time_bulk_accounting` is integer-exact *by construction* — it tests
bookkeeping, not physics, so it cannot adjudicate any of this.

### What survives

- The **shadow accounting** — (12,1) + (12,1) = 26 = bulk exactly, each shadow
  literally half the bulk including its time, with the per-shadow 13 = 4 + 7 + 2
  descent unchanged and nothing migrating.
- The **spinor upgrade** — Cl(24,2) is even-dimensional, so Weyl exists and the
  4096 count *is* the chiral half, which the chirality gates need and which
  Cl(24,1) could not supply. Reality: (s − t) mod 8 = 6, so Majorana yes, Weyl
  yes, Majorana–Weyl no — state it that way.
- The **Z₂ shadow swap** exchanging everything including time.
- The **dissolution of the 25D/26D/27D chaos** into one dimension with one
  derivation.

### Independent of this ruling, and still open

The **TCS obstruction**: Crowley–Nordström force b₂ + b₃ odd for a twisted
connected sum, and the claimed (b₂, b₃) = (4, 24) sums to 28. b₃ = 24 itself
survives (Joyce 1996 has (7, 24)); what fails is the pairing with b₂ = 4. This
has nothing to do with the bulk signature and is not touched by choosing (24,2).
Note that `n_faces = 4` no longer *depends* on b₂ = 4 — it is forced by the
rainbow-labelling enumeration, see `PrincipiaMetaphysica/docs/BRIDGE_CHANNEL_ASSIGNMENT.md` —
which weakens the coupling between the two problems without dissolving the
obstruction.
