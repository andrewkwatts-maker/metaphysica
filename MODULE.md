# metaphysica

> **Crate:** `physica_core` &nbsp;|&nbsp; **Engine plugin:** `pt-physica`
> **Upstream repo:** EXISTS (live)

Engine bridge to metaphysica exposing derived physics constants, quark masses, CKM couplings, a simulation tick and an atomic binding-energy/emission translator.

---

## Design

A thin bridge exposing derived physics constants, quark masses and CKM couplings, a per-frame simulation tick and an atomic binding-energy / emission translator - each with a hard-coded fallback so the engine builds green without the submodule.

The cleanest module of the twelve: best test density (24.6 per kLOC), leanest dependency set, no GPU, no Plugin entanglement. The work is **subtractive** - push physics upstream - rather than architectural.

Physics currently living engine-side that belongs in `physica_core`: the full SEMF binding-energy implementation with its five coefficients, the Rydberg emission model, the 15-entry fallback constants table, and the PDG-2024 quark masses and CKM magnitudes. The engine should not own physics numbers.

Same latent build break as periodica: `physica_core/with-arithmos` was deleted upstream in 2.1+. Also, every non-fallback path is a stub - `tick()` advances only a frame id - and the `with-physica-core` code paths have zero test coverage, which is exactly where a stale-submodule break would hide.

## Responsibilities

- Constants lookup with upstream-first/fallback routing and dirty-flag caching
- Quark registry: PDG-2024 masses, CKM magnitudes, datasheet shaping
- Frame-tick driver returning a physics update struct
- Atomic bridge: SEMF binding energy and Rydberg emission wavelengths
- DI seams via constant-source and quark-source traits

### Explicitly not this module's job

- Engine constant caching, dirty flags and hot reload - those stay in `pt-physica`
- `PTExpression`-typed returns (engine-side adapters)

## Dependencies

**Upstream crates**
- Arithma (optional)

**Engine plugins** *(these disappear once extraction completes)*
- pt-themelios (1 ref)
- pt-arithmos (1 ref)
- pt-eml-bridge DEAD - 0 refs

**External crates**
- serde
- serde_json
- once_cell
- parking_lot
- thiserror

## Current state

| | |
|---|---|
| Rust LOC | 1,262 |
| Tests | 31 |
| GPU-coupled files | 0 |
| Extractable | ~35% belongs upstream |
| PyPI | Already on PyPI |
| Extraction risk | **Low** |

**Verdict.** Cleanest module of the twelve: best test density (24.6/kLOC), leanest deps, no GPU, no Plugin entanglement. The work is subtractive - push physics upstream - rather than architectural.

## Blockers

- Same latent build break as pt-periodica: physica_core/with-arithmos was deleted upstream in 2.1+
- Vendored v2.0.0-alpha.0 vs live v2.3.1; three new upstream modules unexposed (cosmology, e8, rg_running)
- Every non-fallback path is a stub: tick() returns a default with only the frame id advancing; register_in_arithmos registers nothing
- len() double-counts constants present in both upstream and fallback
- Zero test coverage of the with-physica-core paths - exactly where a stale-submodule break would hide

## Work items

1. Update the submodule to 2.3.1 and delete the dead feature edge
2. Add CI that builds with --features with-physica-core
3. Move the SEMF implementation and Rydberg model upstream
4. Move the fallback constant/quark tables upstream as a no-default-features data module
5. Wire tick() to the real temporal simulator
6. Fix len() double-counting; drop the unused dep
7. Expose the new e8 module - pt-periodica's E8/Leech lattice kinds want it

---

## Naming

Greek words, written in Latin letters. No Greek script in code, docs or reports.
See [INDEX.md 1b](../GitReview/extraction/INDEX.md#1b-naming-convention----keep-the-greek).

## References

- Master plan: `H:\Github\GitReview\extraction\INDEX.md`
- Per-module report: `H:\Github\GitReview\extraction\modules.html`
- Source of truth today: `h:\DaedalusSVN\PlayTowEngine\PlayTowEngine\plugins\pt-physica`

*Generated 2026-09-03. Do not hand-copy code into this folder; follow the procedure
in INDEX.md so the rename and test migration stay verifiable.*
