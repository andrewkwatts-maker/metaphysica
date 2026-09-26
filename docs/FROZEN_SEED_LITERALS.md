# Frozen seed literals — constants annotated with a b_3 derivation they satisfy only at b_3 = 24

Measured 2026-09-26 by `tests/test_frozen_seed_literals.py`, which parses the
declared formula out of the comment or docstring next to each constant,
evaluates it at the live seed and at 24, and compares it against the value the
framework actually serves.

**Nothing in this document has been changed.** Every row is a *dichotomy* whose
resolution is a physics ruling, not a repair. Several freezes are load-bearing:
163 and 288 each have a second derivation that carries no b_3 at all, and
σ_T = 23/24 is pinned by three separate guards that record a violation the
moment it moves. The register
(`PrincipiaMetaphysica/docs/OUTSTANDING_ISSUES.md`) wins over this file.

## The active path

| | |
|---|---|
| Adopted seed | `b3_seed = seed_43_joyce`, author ruling 2026-09-22 |
| (b_2, b_3) | (12, 43), both DERIVED — b_3 = 7 + 3·b_2, 7 flat + 3 per A1 family |
| n_gen | b_2/4 = 3 (`n_gen_source = b2_over_faces`) |
| Abandoned seed | b_3 = 24, kept runnable and LABELLED unreachable (b_3 ≡ 7 mod 12) |
| SSoT for the path | `src/metaphysica/simulations/PM/geometry/b3_path.py` |

`FormulasRegistry` resolves the live seed correctly — `self._b3 =
_seed_values(_resolve_b3_path())[0]` at line 1131 — and constants that ride it
moved: `_demiurgic_coupling` (b_3/2 + 1/π) is 21.818, `pressure_divisor`
(b_3²/4) is 462.25, `manifold_area_bulk` (b_3²) is 1849, `odowd_bulk_derived`
(7·b_3 − 5) is 296, `c_kaf` is 45.529, `_sophian_drag` (163/(10·b_3 − 1)) is
163/429 = 0.37995. The rows below are the ones that did not.

## FROZEN_LITERAL — a value the framework *serves* satisfies its declared formula only at 24

| # | Constant | Literal / served value | Declared formula (quoted from source) | Declared at | @ b_3 = 24 | @ live b_3 = 43 | holds@24 | holds@live | Consumers | Guard pinning it |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `FormulasRegistry.LOGIC_CLOSURE` | `288` (line 174) | `# topological: 12 x b3 (first-principles from G2 topology)` | line 174, trailing comment on the assignment | 288 | 516 | yes | **no** | class constant read by `_sophian_drag`'s sibling `BULK_PRESSURE` path; the value is re-exported as `roots_total` / `logic_closure` / `nitzotzin_roots` (149 refs in 19 files). A second module-level `LOGIC_CLOSURE = 288` exists in `simulations/PM/derivations/cosmology_sector_complete.py:101`. | `verify_integer_closure` (135 + 153 == 288) — b_3-free, so it does **not** pin the 12·b_3 claim |
| 2 | `FormulasRegistry._roots_total` | `288` (line 1179, = 135 + 153) | `- roots_total = 288: Octonionic/24D structure (b3*12), NOT E8xE8 roots (480)` (line 142); also `Logic Closure Total (288 = b3 * 12 = 24 * 12)` (line 1505) and `288 - Octonionic/24D structure total (same as roots_total = b3*12)` (line 3943) | lines 142 / 1505 / 3943 | 288 | 516 | yes | **no** | 149 refs / 19 files, incl. `appendix_h_288_roots.py`, `coupling_unification.py`, `avogadro.py`, `lagrangian_master.py`, H0 = 288/4 − P_O/144 + η_S | `verify_integer_closure`, `is_closure_valid` — both only check 135 + 153 = 288 |
| 3 | `FormulasRegistry._chi_eff` | `72` (line 1157) | `chi_eff_shadow = b3^2/8 = 576/8 = 72` (line 284, repeated at 300) | lines 284 / 300 | 72 | 231.125 | yes | **no** | quark Yukawa / CKM, gate transition, baryon asymmetry, torsional leakage; exported as `chi_eff`, `chi_eff_sector`, `mephorash_chi` | **none.** Forked as `chi_eff_route`, status OPEN / **unruled** |
| 4 | `FormulasRegistry._chi_eff_total` | `144` (line 1158) | `GEOMETRIC: chi_eff_total = 72 + 72 = b3^2/4 = 576/4 = 144` (line 310) | line 310 | 144 | 462.25 | yes | **no** | 131 refs / 19 files: `reid_invariant = 1/144`, `chi_parity_product`, PMNS mixing, `N_flux`, `roots_per_sector`, `pneuma_mechanism`, `CERTIFICATES.py` | **none.** Forked as `chi_eff_route`, status OPEN / **unruled** — *must stay unruled* |
| 5 | `FormulasRegistry.BULK_PRESSURE` = `163` (line 191); `_odowd_bulk_pressure` = `163` (line 1382); `_sterile_sector` = 288 − 125 = `163` (line 1188) | `163` | `- sterile_sector = BULK_PRESSURE = 163 (= 7*b3 - 5)` (line 1397); also `sterile_sector = 163 (shadow gauge degrees of freedom = 7*b3 - 5)` (line 3873) and the `odowd_bulk_derived` docstring `(7 * B3) - 5 = 163` (line 4107) | lines 1397 / 3873 / 4107 | 163 | 296 | yes | **no** | 118 refs / 13 files; `_sophian_drag = BULK_PRESSURE/(10·b_3 − 1)`, H0 O'Dowd formula, `terminal_closure.py`, `root_derivation.py`, `appendix_h_288_roots.py`, `generate_72gates_json.py` | `verify_bulk_pressure_derivation()` compares the two sides and **already returns False** at the live seed (163 vs 296). `tests/test_sterility_audit.py::test_sterile_equals_bulk` pins that break with `assertFalse`. `verify_sterile_equals_bulk()` is False for the same reason |
| 6 | `identify_ghost_literals.GhostLiteralHunter.TARGET_LITERALS` | `163` (line 43), and in the same set `144` (42), `288` (44), `576` (47), `0.9583` (48), `71.55` (46) | `163,      # sterile_sector = (7*B3)-5` | line 43 (module docstring repeats it at line 8) | 163 | 296 | yes | **no** | the ghost-literal hunter itself. Consequence: the hunter hunts the **24-era** values and cannot see the live ones (296, 462.25, 1849, 42/43) | none |
| 7 | `FormulasRegistry._D_ancestral_total` | `26` (line 1206) | `return self._D_ancestral_total  # D_bulk = 26 = b3 + 2 (two-time)` (line 3675) | line 3675 | 26 | 45 | yes | **no** | `D_BULK` in `config.py`, every dimensional-reduction consumer, `horos` / `horos_limit` / `D_total_26` | `b3_path.downstream()` already reports `plus_two_identity_holds = False` with a `plus_two_identity_note` ("BROKEN on this path … Recorded, not dropped"), and `b3_path`'s module docstring states the cost. The registry docstring at 3675 was not updated with it |
| 8 | `verify_sterility_report.IndependentDerivation.MANIFOLD_BASE` | `24` (line 66) | `MANIFOLD_BASE = 24       # b3 - the Betti number` | line 66, trailing comment | 24 | 43 | yes | **no** | `derive_independently()` (line 79) and line 179 — the "Clean Room" validator that exists specifically to avoid the tautology loop. Consequence: the independent cross-check derives 144 / 163 / 576 / 71.55 from b_3 = **24** and then compares them to a registry running at 43, so `pressure_divisor_derivation` and `sterile_derivation` in that report are scored against the abandoned seed | none |

## PROSE_ONLY_STALE — only a comment carries the number

No live reading serves these values; the stale narration is the defect.

| # | Subject | Value written | Declared formula | Declared at | @ 24 | @ 43 | Notes |
|---|---|---|---|---|---|---|---|
| 9 | `N_flux` | `24` | `- N_flux = chi_eff_total/6 = 24 = b3 (flux quantization)` | FormulasRegistry.py:315 | 24 | 43 | Rides row 4: 144/6 = 24 only while `chi_eff_total` is frozen. The registry exports no `N_flux`; the value-match to `D_space_24` is rejected by the detector because the two are different objects, which the registry itself states at lines 1109–1120 |
| 10 | `denominator` (η_S) | `239` | `- denominator = 239 = b3*10 - 1 (decimal b3 scaling minus unity)` | FormulasRegistry.py:3873 (and 1398) | 239 | 429 | The **code** rides the seed (`self._sophian_drag = self.BULK_PRESSURE / (self._b3 * 10 - 1)`, line 1402, = 163/429). Only the worked example says 239. The numerator is frozen (row 5), so η_S is a **hybrid**: half-following the seed |
| 11 | `w0` | `-0.9583` | `w0 = -1 + 1/b3 = -23/24 = -0.9583 (consistent with DESI 2025 BAO-only data)` | FormulasRegistry.py:1316 | −0.958333 | −0.976744 | **This is σ_T surfacing.** See the dedicated section below |
| 12 | `w_a` | `-0.204` | `w_a = -1/sqrt(b3) = -1/sqrt(24) = -0.204 (predicted)` | FormulasRegistry.py:1317 | −0.204124 | −0.152499 | `b3_path.downstream()` computes `wa_thawing = -4/sqrt(b_3)` from the live seed (−0.610); `canonical_values.py` lines 26–27 carry both the −1/√b_3 and −4/√b_3 shapes with their 24-era values |

## σ_T = 23/24 — the third named dichotomy, and the guards that pin it

`self._tzimtzum_pressure = 23.0 / 24.0` (FormulasRegistry.py:1410), annotated
`# 10. Tzimtzum Pressure (sigma_T = 23/24) - Void Seal` and `# MUST use
fraction, NOT decimal!`.

That annotation contains **no b_3**, so the detector cannot reach it from the
assignment. It reaches it through the w_0 identity instead (row 11): the
framework's own `dark_energy_betti` ruling puts n = b_3 in w_0 = −(n−1)/n,
`b3_path.downstream()` publishes `w0_formula = "-(b_3 - 1)/b_3"` and computes
−42/43 = −0.976744 from the live seed, while `FormulasRegistry.calculate_w0`
returns `-self._tzimtzum_pressure` = −0.958333 unchanged. The declared form is
therefore (b_3 − 1)/b_3 → 0.958333 at 24, 0.976744 at 43.

### Exactly what trips if the literal changes

Measured by setting `_tzimtzum_pressure = (b_3 − 1)/b_3 = 42/43` on a scratch
registry:

| Check | Where | Pins by | Result at 23/24 | Result at 42/43 | Message recorded |
|---|---|---|---|---|---|
| `DemonLockGuard.verify_tzimtzum_fraction` | demon_lock_guard.py:197, `expected = 23.0/24.0`, tol 1e-10 | **hard literal** | PASS | **FAIL** | `TZIMTZUM ERROR: Registry drift detected. Must be 23/24.` |
| `DemonLockGuard.verify_w0_seal` | demon_lock_guard.py:319, `expected_w0 = -23.0/24.0`, tol 1e-10 | **hard literal**, via w_0 = −σ_T | PASS | **FAIL** | `W0 ERROR: Registry w0 = -0.9767441860, expected -0.9583333333` |
| `FormulasRegistry.verify_tzimtzum_fraction` | FormulasRegistry.py:4637, `expected = 23.0/24.0`, tol 1e-15 | **hard literal** | PASS | **FAIL** | returns False; surfaced in `get_certificate()` and `sync_docs` |
| `DemonLockGuard.verify_sterile_parity` (`EXPECTED_PARITY_SUM`) | demon_lock_guard.py:104 / 228 | **nothing — tautology** | PASS | PASS | none |

Both `verify_tzimtzum_fraction` and `verify_w0_seal` run inside
`DemonLockGuard.run_preflight()` (lines 475–481), so **the preflight fails** if
σ_T moves. Also pinned outside the guard: `identify_ghost_literals`'
`TARGET_LITERALS` contains `0.9583  # tzimtzum_pressure = 23/24` (line 48, and again in its
value->name map at line 286), and
`DemonLockGuard.IMMUTABLE_PARAMS` (line 72) lists `tzimtzum_pressure` and
`sophian_drag` among the parameters the Demon Lock treats as immutable once
registered.

That is the cost side of unfreezing σ_T. It is stated here so the decision is
taken with it in view; the decision itself is the author's.

### `EXPECTED_PARITY_SUM` does not pin anything

The task brief names `EXPECTED_PARITY_SUM` as the guard pinning σ_T. Measured,
it is not a pin at all:

```python
@property
def EXPECTED_PARITY_SUM(self) -> float:
    """Parity sum target from FormulasRegistry (eta_S + sigma_T)."""
    return self.registry.parity_sum          # demon_lock_guard.py:104-106
```

and `verify_sterile_parity` (lines 228–240) compares `self.registry.parity_sum`
against it. On the registry side that is `x == x`: the check **cannot fire**
whatever η_S or σ_T become. Confirmed by moving σ_T to 42/43 — parity goes from
1.338287 to 1.356698, `EXPECTED_PARITY_SUM` follows it, and the check still
passes. `tests/test_demon_lock_guard.py::test_parity_sum_is_derived` asserts
exactly this tautology (`guard.EXPECTED_PARITY_SUM == guard.registry.parity_sum`),
so the tautology is currently *certified* rather than caught. Only the JSON
branch of `verify_sterile_parity` can fail, and only when
`named_constants.json` is stale relative to the registry.

The same shape appears in `DemonLockGuard.verify_hubble_formula` (line 287):
`expected_h0 = round(self.registry.h0_local, 2)` is then compared to
`self.registry.h0_local` with tolerance 0.01, which rounding can never exceed.
Its label reads `Hubble Formula (H0=71.55)`; the live `h0_local` is **71.7396**,
because η_S followed the seed. Both facts are asserted in
`test_the_hubble_guard_also_cannot_fire`.

### And one guard that is already failing, silently

`FormulasRegistry.verify_parity()` (line 4623) pins `expected = 1.64034`
(= 163/239 + 23/24) at tolerance 0.0002. The live parity sum is
163/429 + 23/24 = **1.3382867**, so it returns **False**. Nothing asserted it
before this pass; the False flows into `get_certificate()["parity_valid"]`
(line 4208), the `sync_docs` FORMULAS.md generator (line 88) and the sterility
report. `test_the_registry_parity_check_is_already_failing_at_the_live_seed`
now pins the failure so it cannot be rediscovered as a surprise.

## Blind spots of the detector — stated, not hidden

* A constant whose annotation contains **no b_3** is invisible to the named
  channel. σ_T (row 11) is only reached through the w_0 identity;
  `BULK_PRESSURE = 163` is only reached through the `sterile_sector`
  declaration; `_hossenfelder_root = math.sqrt(24)` (line 1379, annotated
  `lambda_S = sqrt(24)`) is **not reached at all** and is not in any inventory.
* Formulas mixing b_3 with a symbol the harvester cannot evaluate — π, φ, γ,
  `k_gimel`, `chi_eff` — are rejected as fragments rather than mis-scored. That
  is why `alpha^-1 = k_gimel^2 - b3/phi + phi/(4*pi)`, `v_tree = k_gimel x
  (b3 - 4)` and `eta_S = sterile_sector / (b3 * 10 - 1)` produce no row from
  the formula side.
* `simulations/core/variants.py` is deliberately **not** scanned: it is the
  fork registry, so its b_3 expressions describe branches the framework does
  not take, and scoring them would report the off-path branch's own honest
  record as a defect. The exclusion is asserted by
  `test_the_fork_registry_is_deliberately_not_scanned`.
* The scan covers `simulations/core/` only. The same class almost certainly
  exists under `simulations/PM/`; pointing the detector there is a follow-up,
  not a claim made here.

## Recommended fork structure — a RECOMMENDATION for the author, not a decision

Each dichotomy below is a genuine two-way choice with costs on both sides.
`variants.py` is owned elsewhere and was not touched; these are proposals for
it.

### 1. `bulk_pressure_route` — 163 vs 296

| Option | Claim | Buys | Costs |
|---|---|---|---|
| `sector_split` (163, status quo) | 163 = 288 − 125, carries no b_3 | every published H0 / η_S number unchanged; the 288-closure ledger stays intact | `7·b_3 − 5` becomes a coincidence of the abandoned seed and must be retired as a derivation, not merely left in a comment |
| `heptagonal` (296 = 7·43 − 5) | 163 was always 7·b_3 − 5 | the heptagonal derivation survives the seed | 288 − 125 = 163 breaks, so either `visible_sector` = 125 or `roots_total` = 288 must move; η_S, H0 and the whole Barbelo naming layer move with it |

Recommended default: **`sector_split`** with the heptagonal claim explicitly
labelled WITHDRAWN-AS-DERIVATION, because the break is already measured
(`verify_bulk_pressure_derivation()` is False) and pinned by
`test_sterile_equals_bulk`. The cheaper honest move is to relabel the comment,
not the number — but that relabelling is itself a ruling.

### 2. `logic_closure_route` — 288 vs 516

| Option | Claim | Buys | Costs |
|---|---|---|---|
| `gnostic_split` (288) | 288 = 135 + 153 | 149 references across 19 files unchanged; `verify_integer_closure` keeps working | `12 × b_3` retired as a derivation; the "Octonionic/24D structure" reading of 288 goes with it |
| `betti_times_twelve` (516) | 288 = 12·b_3 | the geometric reading survives | 135 + 153 = 288 breaks; H0 = 288/4 − … moves; `appendix_h_288_roots` is invalidated wholesale |

Recommended default: **`gnostic_split`**, same reasoning as above. Note that
the split itself is documented in-file as *fitted*, not first-principles, so
neither side is a derivation from G2 topology.

### 3. `tzimtzum_route` — 23/24 vs 42/43

| Option | Claim | Buys | Costs |
|---|---|---|---|
| `frozen_23_24` (status quo) | σ_T = 23/24 as a seal in its own right | three guards keep passing; `w0_observed_DESI` agreement stays at ~0.017σ | σ_T is then an INPUT with no b_3 behind it, contradicting `dark_energy_betti`'s n = b_3; the registry's w_0 and `b3_path`'s w_0 stay permanently disagreeing |
| `betti_sealed` (42/43) | σ_T = (b_3 − 1)/b_3 | σ_T becomes derived, and `calculate_w0` agrees with `b3_path.downstream()` | `verify_tzimtzum_fraction` ×2 and `verify_w0_seal` all fail, so `run_preflight` fails until they are re-pinned; w_0 agreement degrades to ~0.94σ against the DESI anchor (the trade `b3_path` already documents) |

Recommended default: **`betti_sealed` as the CONSIDERED option and
`frozen_23_24` as ACTIVE**, so the divergence becomes *reachable and
runnable* — which is what makes the guard coupling checkable at all — without
moving a published number before the author rules. This mirrors what
`n_gen_source` did once the fork was made live.

### 4. `chi_eff_route` — leave alone

Already forked, status **OPEN / unruled**. Rows 3, 4 and 9 all hang off it.
`tests/test_seed_propagates_from_the_root.py` already pins the divergence
(144 from Hodge numbers vs 462.25 from b_3²/4) and
`test_chi_eff_is_reported_and_left_unruled` asserts the fork stays unruled.
**No recommendation is offered and none should be.**

### 5. `plus_two_identity` — 26 = b_3 + 2 (row 7)

Not a live fork: `b3_path` already records it as BROKEN and says so in the
`downstream()` note. The recommendation is documentary only — the registry
docstring at line 3675 should carry the same "BROKEN, recorded not dropped"
wording `b3_path` does. Changing a docstring to match a ruling already made is
not itself a ruling, but it is not in this pass's scope either.

### 6. `clean_room_seed` — row 8, the most consequential

`verify_sterility_report.IndependentDerivation.MANIFOLD_BASE = 24` is the seed
of the validator that exists *specifically* to be independent of the registry.
Frozen at 24, it does not validate the live framework; it validates the
abandoned one. There is no fork to recommend here — the two candidate readings
are "the clean room should follow the adopted seed" and "the clean room is a
fixed historical baseline". The second is defensible only if it is *labelled*
as such, and it currently is not. This is the row worth ruling on first.

## Falsified and withdrawn claims — labelled, not deleted

Per the standing rule, nothing below was removed:

* `7·b_3 − 5 = 163` — false at the live seed (296). Kept, labelled.
* `12 · b_3 = 288` — false at the live seed (516). Kept, labelled.
* `b_3²/4 = 144` and `b_3²/8 = 72` — false at the live seed. Kept, **unruled**.
* `D_bulk − b_3 = 2` — BROKEN (26 − 43 = −17), already recorded in `b3_path`.
* `σ_T = 23/24` as a b_3-derived seal — false at the live seed. Kept, guarded.
* `η_S + σ_T = 1.64034` — false at the live seed (1.3382867).
  `FormulasRegistry.verify_parity()` returns False. Kept, labelled.
* `H0 = 71.55` — the live `h0_local` is 71.7396. Kept, labelled.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
