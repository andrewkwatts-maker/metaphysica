# State review — the switch machinery and the 12/43 path

Reviewed 2026-09-26 against `fb81dfd` (clean tree, branch
`claude/wonderful-noether-z3bjav`). Every number here was measured in this
repository, not carried over from a summary. Where a measurement contradicts
a document, the measurement is quoted and the document is named.

## 1. Where the active path actually stands

`b3_seed = seed_43_joyce` is ADOPTED. `b3_path.resolve_path()` returns it and
`seed_values()` returns `(43, 12)`, both derived: `b_3 = 7 + 3 b_2`, seven flat
plus three per A1 family. `n_gen = b_2/4 = 3`.

The reachable family is generated from the contribution table's own relation
rather than hand-listed, so all four profiles execute and the selection
argument is checkable instead of asserted:

| profile | b_3 | b_2 | n_gen = b_2/4 | status |
|---|---|---|---|---|
| `seed_7_joyce`  |  7 |  0 | 0 | DISABLED — structural refutation |
| `seed_19_joyce` | 19 |  4 | 1 | DISABLED — structural refutation |
| `seed_31_joyce` | 31 |  8 | 2 | DISABLED — structural refutation |
| `seed_43_joyce` | 43 | 12 | 3 | **ACTIVE** |
| `seed_24` (off-family) | 24 | 4 | — | CONSIDERED — the comparison baseline |

Only one profile in the family gives three generations, and the other three
fail by being the wrong *kind* of thing (a generation count is a number of
things) rather than by disagreeing with a measurement.

## 2. The switch machinery — 18 forks, 51 options

### What was there

`VariantOption` carried `adopted: bool` and `priority: int`. That gave a reader
two distinguishable states — adopted, and everything else — while "everything
else" mixed two unrelated things: a rival nobody has ruled out, and a candidate
the framework has already refuted and keeps only because a falsified claim
stays on the books. The distinction lived in a `priority` integer whose meaning
was documented in a comment, and nothing checked that an option labelled
"retained because refuted" was treated as refuted anywhere.

### What it is now

Three declared statuses, one vocabulary, published in the artifact:

- **ACTIVE** — adopted; exactly one per fork; what runs by default.
- **CONSIDERED** — a live rival: runnable, not refuted, a real candidate.
- **DISABLED** — refuted (falsified against data, or structurally impossible)
  and RETAINED, runnable under an explicit override, excluded from default
  sweeps, never deleted.

Measured population: **18 ACTIVE · 30 CONSIDERED · 3 DISABLED** across 18
forks, pinned in `tests/test_option_status.py` in both directions — a new
refuted option fails the pin because the inventory grew, and promoting one back
to CONSIDERED fails it because the inventory shrank.

`DISABLED` means *off the table*, not *not executable*. A refutation nobody can
re-run is folklore, so a disabled option still resolves end to end through
`resolve(fork, option)` or the environment. What it no longer does is consume
sweep budget: `Fork.sweepable_ids()` excludes it, and `combinations_for` gained
`include_refuted=False` for a budget sweep. The default stays `True`, because
that module's central promise is that it reports *every* combination and
dropping a refuted one silently would make the promise false.

New operational surface: `selected_status()`, `off_table_selections()`, and a
CLI that prints each option's status, warns loudly when any fork resolves to a
refuted option, and names the forks whose source could not be checked.

### Consistency is enforced rather than hoped for

`VariantOption.__post_init__` reconciles the three fields once — `status`
defaults from `adopted`, `priority` defaults from `status` — and refuses an
incoherent declaration: an option cannot be adopted and refuted at once, and a
DISABLED option cannot claim a sweep slot ahead of a live rival. On its first
run the validator rejected three existing declarations, which is the finding
rather than an inconvenience: `seed_7/19/31_joyce` already *meant* DISABLED via
`priority=2`, and there had been no word for it.

## 3. Findings this pass

### 3.1 The drift detector that could not detect drift (fixed)

`_dark_energy_betti_adopted` promises in its own docstring to be "measured, not
declared", so that "a silent change to the derivation cannot leave this fork
claiming the wrong one". It could not do that, in three ways at once. It caught
bare `Exception` and returned the literal `"b3_24"`; a `w0` of `None` or `<= -1`
returned the same literal; and an unmapped `n` returned it through a
`.get(n, "b3_24")` default. Since `b3_24` is also the option the fork
**declares** adopted, all three failure paths confirmed the declaration.

And the ordinary path was a failure path: `cosmology.w0_derived` is not in the
registry until a sim run populates it, so in a bare process the `except` branch
fired and nothing was ever measured. Consequences:

- `describe()["forks"]["dark_energy_betti"]["drift"]` was permanently `None` —
  published as "no drift" on runs that had checked nothing.
- `test_defaults_match_the_value_adopted_at_the_source` compared the
  declaration against itself for this fork and passed no matter what the
  sector computed. A test that cannot fail, which this repo treats as a defect.

Fixed: a reader that cannot measure raises `SourceUnmeasurable` instead of
naming an option. `describe()` gained a `source_read` field, so "could not
measure" is now distinguishable from both "agrees" and "drifted" — 6 of 18
forks report a non-live read, 5 because they wire up no reader at all and
`dark_energy_betti` because the registry has no `w0` yet.

### 3.2 The sweep that abolished silent defaults could not see the registry's own readers (fixed)

`test_silent_fork_defaults.py` exists to kill exactly this shape and found
three instances elsewhere on 2026-09-22. It never covered
`simulations/core/variants.py`, and listing it would not have helped: the
detector's shape signature is "a function that calls `resolve()`", while a
`read_adopted` reader does the opposite — it reads the source module directly.
The readers were structurally invisible to the sweep written to protect them.

A second detector with the reader's shape now walks them, and it found a
**second instance on its first run**: `_bulk_signature_adopted` fell through to
`return "24_2"` — again the declared adopted option — both when `CANON["bulk"]`
carried no `form` key and when it carried a signature no option claims. A bulk
rewritten to an undeclared signature (the withdrawn 27D and (24,1) readings
among them) would have reported "no drift". Both readers now raise.

### 3.3 A sector that did not move with the seed, and a fork that could not say so

Two SSoTs disagree about `w_0` on the adopted path:

| source | `w_0` | implied n |
|---|---|---|
| `b3_path.downstream()` — the active-path module | −0.976744 = −42/43 | 43 = live b_3 |
| `FormulasRegistry.tzimtzum_pressure` (literal `23.0/24.0`) | −0.958333 = −23/24 | 24 |
| bundled `data/parameters.json` → `cosmology.w0_derived` | −0.958333 | 24 |

`b3_path` documents −0.976744 at 0.94σ as an **accepted cost** of the ruling.
The published number is the other one. The `dark_energy_betti` fork could
express neither the disagreement nor the live-seed reading, because its option
set — written entirely at b_3 = 24 — had no "n = b_3 on whatever seed is live"
entry, and its adopted option's summary read "n = b3 = 24", which the ruling
made false.

Landed, without ruling anything: the adopted option now says 24 is a **frozen
integer** and no longer b_3; a `b3_live` option carries the live-seed reading
so it can be selected and detected; and the fork's notes record what the
reseeding moved here — including that on the adopted seed `n = b_2` is 12, so
the `b2_4` and `bridges_12` integers now **coincide**, and the mass-scale
argument that settled the 2026-09-06 ruling was computed against b_2 = 4 and
b_3 = 24 throughout. Whether that argument survives the reseeding is the
author's ruling. No published number changed.

### 3.4 Half the decision space is decoration — 7 forks nothing reads

`variants.FORKS` states its own admission criterion at the top of the
declaration: documented-but-not-runnable decisions are *deliberately absent*,
because "declaring them here would imply a switch that does nothing."

Measured: **7 of 18 forks have no pipeline consumer** — no module resolves them
or reads their environment override, so selecting any of their options changes
nothing that runs. Between them they carry **25 of the 51 declared options**.

| inert fork | status | options |
|---|---|---|
| `b3_origin` | OPEN | 5 |
| `chi_eff_route` | OPEN | 3 |
| `g2_construction` | OPEN | 2 |
| `moduli_indexing` | OPEN | 3 |
| `bulk_signature` | RULED | 3 |
| `dark_energy_betti` | RULED | 7 |
| `face_genericity` | RULED | 2 |

`dark_energy_betti` is the sharpest case: status RULED, seven options with full
sigma accounting, a documented ruling — and nothing selects any of them. This
is a harder problem than a stale number, because an inert fork publishes into
`variants.json` identically to a live one, so a reader of the artifact or of
the website cannot tell a decision the engine can execute either way from one
that is merely written down.

Not fixed here — wiring these is a body of work and some of it needs author
rulings. Instead `tests/test_forks_are_wired.py` pins the inert set exactly, in
both directions: a newly inert fork fails it because the set grew, and wiring
one up fails it because the set shrank, so the pin must be edited by whoever
did the wiring.

### 3.5 Nothing has been deleted — verified three ways

The standing rule that a falsified candidate stays on the books has held. A
history audit (`docs/DISCARDED_PATH_COVERAGE.md`, 62 approach rows) found **35
RUNNABLE_LABELLED, 27 DOCUMENTED_ONLY, 0 LOST**, confirmed independently by:
no file under `src/` or `tests/` ever deleted; 23 fork option ids added since
the root commit and none removed; and `git log -S` on every discarded-approach
string still finding it in HEAD.

The two failure modes that exist are both short of deletion: **labelled but not
runnable** (§3.4 above), and **runnable but not labelled** — withdrawn claims
still asserted as live physics. The clearest instance of the latter:
`free_set.py` records `cosmology.wa_thawing = -4/sqrt(b_3)` as RETIRED on the
register, "do not resurrect", while `b3_path.downstream()` and
`b3_candidate_sweep.py` both compute exactly that formula and publish it under
the canonical key — where the sector itself registers a different, live
derivation under the same name. Under measurement separately.

### 3.6 Constants frozen at the abandoned seed

`FormulasRegistry` resolves the live seed correctly and several constants ride
it. Others are literals whose own adjacent comment declares a b_3-dependent
derivation that the literal satisfies only at b_3 = 24:

| constant | literal | declared form | at 24 | at 43 |
|---|---|---|---|---|
| `BULK_PRESSURE` | 163 | `7*b_3 − 5` | 163 | 296 |
| `LOGIC_CLOSURE` | 288 | `12*b_3` | 288 | 516 |
| `tzimtzum_pressure` | 23/24 | `(b_3−1)/b_3` | 0.958333 | 0.976744 |
| `chi_eff` | 144 | `b_3²/4` | 144 | 462.25 |

`chi_eff` is already forked `UNRULED` and must stay so. The other three are
**unforked**, so the dichotomy is invisible where `chi_eff`'s is visible. Note
that `demon_lock_guard` pins `tzimtzum_pressure` through `EXPECTED_PARITY_SUM`,
so the freeze may be load-bearing — whether to unfreeze any of these is the
author's physics ruling, not a cleanup. Under measurement separately.

### 3.7 The minimum input list: 67 rows, and a count that could not name its seed

`free_set.py` answers the question a minimum-parameter claim actually needs —
how many *independent knobs*, not how many registration sites. Measured:

| | |
|---|---|
| ledger rows | 67 |
| bare process (no build) | **39**, and the reduction cannot run at all — `reduction_ran: False` gives 67 |
| reseeded probe at b_3 = 43 | 38 |
| reseeded probe at b_3 = 24 | 37 |

Where the knobs live: `geometry` 21 and `ckm` 14 — together over half of 67.
The `ckm` block is largely arithmetic on three Wolfenstein inputs, and the
`geometry` block is mostly *experimental data wearing a geometric namespace*:
`w0_observed_DESI`, `w0_error_DESI`, `wa_observed_DESI`, `omega_Lambda_Planck`,
`theta_12/13/23`, `dm21/31_squared`. `free_set` already classifies those as
`NOT_A_MODEL_KNOB` — "an error bar cannot be a free parameter of the theory
under any reading" — and the suite already asserts it
(`test_an_error_bar_is_not_a_free_parameter`).

**But every one of those reductions is gated on a prior build.** Each filters
`if k in params`, and `_params()` reads `AutoGenerated/parameters.json`. In a
bare process `not_model_knobs()` returns `{}` despite declaring seven rows with
reasons, every duplicate group resolves empty, and the free set reports 67 with
an error bar counted among the theory's free parameters. CI builds first, which
is why three `test_free_set.py` assertions fail locally and pass there.

Two defects fixed, both of which made the count unauditable:

1. **Unknown provenance was treated as agreement.** Every b_3-arithmetic
   removal verifies against the *artifact's* b_3. The guard
   `removals_resting_on_stale_b3` fired only on `consistent is False`, but the
   bundled snapshot has **no `particle.b3` row at all**, giving
   `consistent is None` — the same path as a verified match. The module's own
   note already said an unknown read is "a reportable state, not a pass".
   `build_free_set` now publishes `count_is_the_live_forks` and a
   `count_caveat`, false for both mismatch and unknown.

2. **The retired formula was being counted as a free parameter.** The removal
   of `cosmology.wa_thawing` sat *inside* an `except ImportError:` branch,
   after its bare `pass`, from `f289f94` until now — so it ran only when an
   import failed. On every ordinary run the row stayed in the free set, and the
   framework counted the RETIRED `-4/sqrt(b_3)` artefact among its own free
   parameters, while the module's docstring listed that removal as one of its
   three verified reductions. It also left the stale-b_3 guard with almost
   nothing to guard, since this is one of only two removals marked `uses_b3`.
   Now dedented and guarded on `b3` like its sibling; the stale-b_3 guard fires
   for the first time, naming both b_3-dependent removals on an off-path
   artifact.

**What is still not measurable:** the adopted path's free-parameter count. The
only available snapshot carries no seed and pre-adoption values, and a reseeded
probe is internally inconsistent by construction — set `particle.b3 = 43` on a
snapshot computed at 24 and `algebra.freudenthal_quartic` correctly goes
`CLAIMED_UNVERIFIED`, because 16(43/27)² cannot reproduce a value from
16(24/27)². That is the shared-artifact trap the module documents, so the 38
above is a probe result and not a verified count. A genuine build at the
adopted seed is the prerequisite, and it moves every published number — which
is why it is flagged here rather than done unilaterally.

### 3.8 w_0 has three DESI anchors, and the sigma depends which you pick

After merging `origin/main` (`0b429d4`), the dark-energy sector DOES now compute
w_0 from the live seed — `w0_from_b3(43)` returns −0.976744 = −42/43 — so the
seed-blindness in §3.3 is fixed in the sector, while
`FormulasRegistry.tzimtzum_pressure` remains the frozen 23/24 and still sets the
`cosmology.w0_derived` bound's `target` field (that field is carried in the
result but not used for the verdict, which scores against `experimental`).

The sharper problem is the anchor. The same prediction scores:

| anchor | value | sigma |
|---|---|---|
| `geometry.w0_observed_DESI` ± `geometry.w0_error_DESI` | −0.958 ± 0.02 | **0.937** |
| `desi.w0` ± `abstract.desi_w0_uncertainty` | −0.957 ± 0.067 | **0.295** |
| `desi.w0_thawing` | −0.957 ± 0.33 | **0.060** |

A sixteen-fold spread in the error bar for one quantity. `established.py`
declares `desi.w0` the **primary** scoring anchor (the DR2 headline), and
`cosmology_sector_complete`, `dark_energy_thawing` and `established` itself all
cite that — but `b3_path` scores against the `geometry.*` pair, which is where
the framework's headline "0.94σ cost of the ruling" comes from.

The direction is the safe one: the tightest anchor makes the adoption look
*worse* than the primary anchor does, so the published cost is pessimistic
rather than flattering, and a test pins that so a flip would fail. But a
prediction whose sigma can be selected is weaker evidence than one whose anchor
is named, so `downstream()` now publishes `w0_sigma_anchor`,
`w0_sigma_anchor_is_primary` and `w0_sigma_vs_primary_anchor` alongside the
number. No number changed. Choosing a single anchor for w_0 is the author's
ruling; declaring which is in force is not.

## 4. Structural debt

Five modules carry most of the size, and `config.py` alone is 8,779 lines:

| module | lines |
|---|---|
| `config.py` | 8,779 |
| `simulations/core/FormulasRegistry.py` | 6,091 |
| `simulations/PM/derivations/lagrangian_master.py` | 3,984 |
| `simulations/run_all_simulations.py` | 3,903 |
| `simulations/PM/geometry/four_face_structure.py` | 2,953 |

408 source modules, 169 test modules. Splitting these into
single-responsibility subsections is queued and deliberately not started in the
same pass as a semantics change to the fork registry.

## 5. Open, and not closed by this review

- Whether any of the three unforked frozen constants should ride the seed —
  **author's ruling**, and `demon_lock_guard` has a stake in one of them.
- `chi_eff` and `re_t_adoption` remain OPEN by standing instruction.
- Whether the `dark_energy_betti` mass-scale argument survives the reseeding,
  given that `n = b_2` and `n = 12` now coincide.
- The `dark_energy_betti` sigma figures are all measured at b_3 = 24 and are
  now labelled as such rather than silently reinterpreted.
- Wiring the 7 inert forks, or moving them out of `FORKS` per that module's
  own admission criterion. `chi_eff_route` stays unruled either way; the
  other six are wiring work, and `dark_energy_betti` is the one whose
  options are fully costed and entirely unselectable.
- `cosmology.wa_thawing`: a formula the register retires as "do not
  resurrect" is computed and published under the canonical key by the
  active-path module, while the sector registers a different live
  derivation under the same name.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
