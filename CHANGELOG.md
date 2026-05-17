# Changelog

All notable changes to `metaphysica` will be documented in this file.

---

## [2.0.1] — 2026-05-17

### Added

- **`metaphysica-app` CLI command** — companion-app launcher installed as a console script
  alongside the library. On first run it locates or clones the
  [metaphysica-app](https://github.com/andrewkwatts-maker/metaphysica-app) KivyMD desktop/Android
  explorer at the matching version tag (`v2.0.1`) and launches it. Developer checkouts are
  detected automatically via sibling-directory search from `__file__`; end-user installs clone
  to `~/.metaphysica-app`.

### Fixed

- **CI:** Removed stale `arithmos_core` path dependency from `rust/physica_core/Cargo.toml`
  which caused all PyPI CI builds to fail at cargo manifest load time.
- **Build backend:** Switched from `setuptools` to `maturin`; CI and publish workflow updated to
  use Rust toolchain + cibuildwheel, matching the eml-math pattern.
- **pyproject.toml:** Removed UTF-8 BOM that caused `tomllib.TOMLDecodeError` on `pip install`.

---

## [2.0.0] — 2026-05-14

### Added

- **`_dispatch.py`** — Runtime dispatch layer. `_HAS_RUST: bool` flag and
  `rust_accelerated(fn_name)` decorator provide transparent routing to the Rust extension with
  silent Python fallback when the extension is absent.

- **Rust fast paths wired into the public API:**
  - `Get(name)` — tries `py_get_constant` Rust path for constant lookups first; falls back to
    pure-Python `FormulasRegistry` when the name is not a constant or Rust is unavailable.
  - `list_quarks()` — dispatches to `py_list_quarks` (sorted `Vec<String>` from
    `QuarkRegistry::known_names()`).
  - `list_constants()` — dispatches to `py_list_constants` (sorted `Vec<String>` from
    `FormulasRegistry::known_names()`).

- **`tests/test_rust_python_parity.py`** — 8 parity tests: `list_quarks`, `list_constants`,
  cross-checked against `KNOWN_QUARKS` / `KNOWN_CONSTANTS`, `Get("b3")` value, CKM unitarity,
  Jarlskog invariant.

### Changed

- Crate version bumped to `2.0.0` to align with the PyPI package version.

---

## [1.4.0] — 2026-05-10

### Added

- **`physica_core` Rust crate** at `rust/physica_core/` (`cdylib + lib`):
  - `constants.rs` — `FormulasRegistry` with the Ten Pillar Seeds (`b3=24`, `chi_eff=72`,
    `n_gen=3`, `roots_total=288`, `visible_sector=125`, `sterile_sector=163`, φ, γ,
    `JC_CONSTANT=153`, `LOGIC_CLOSURE=288`) and all 125 derived constants.
  - `quarks.rs` / `ckm.rs` — φ-scaling Yukawa quark mass predictions + CKM matrix +
    unitarity check (±1e-8).
  - `gates.rs` — `gate_28_iterative`: explicit state-stack implementation, never recursive,
    preventing stack overflow on deep manifold logic.
  - `simulations.rs` — `TemporalSimulator` with RK4 integration.
  - `g2_manifold.rs` — G2 geometry primitives (racetrack radius, Euler χ).
  - `validation.rs` — CMB anisotropy and isotropic-flow validators (±0.5%).
  - `pyfacade.rs` — PyO3 facade exposing `PyFormulasRegistry`, `py_list_quarks`,
    `py_list_constants`, `py_get_constant` under `metaphysica._physica_core`.
  - `arithmos_bridge.rs` — gated behind `with-arithmos` for Arithmos symbolic-derivation
    tree carriers.

- **`[rust]` extra** — `pip install metaphysica[rust]` triggers the maturin build. The default
  slim install remains pure Python; `_HAS_RUST` stays `False`.

- **`_HAS_RUST` runtime guard** in `__init__.py`.

- **`[tool.maturin]` section** in `pyproject.toml`:
  `manifest-path = "rust/physica_core/Cargo.toml"`,
  `module-name = "metaphysica._physica_core"`,
  `features = ["python"]`.

- **49 Rust unit tests** — CMB/CKM/quark parity confirmed at ±1e-8.

### Notes

- All 281 existing Python files are untouched. The Rust core is strictly additive.

---

## [1.3.1] — 2026-05-03

PyPI re-publish. No functional changes; identical source to v1.3.0.
PyPI file-name reuse policy required a version bump after the v1.3.0 distributions were
already present on the index.

---

## [1.3.0] — 2026-05-03

### Changed

- Bumped `eml-math` dependency to `>=1.3.0`.
- Bumped optional `eml-spectral` dependency to `>=1.3.0`.

### Added

- GitHub Actions CI workflow — Python 3.11 / 3.12 / 3.13 matrix.
- GitHub Actions PyPI publish workflow — Trusted Publishing (OIDC).

---

## [1.0.0] — 2026-05-03

### Added

- **`Get(name)` datasheet API** — returns a JSON-shaped dict for any of 12 quarks or ~35
  physics constants. Schema is a superset of periodica's datasheet format with a
  `pm_prediction` block (metaphysica-derived value, EML expression, CKM couplings).
- **`list_quarks()` / `list_constants()`** — case-insensitive name discovery
  (`"Up"`, `"u"`, `"Up Quark"`, `"AntiUp"` all resolve).
- **`as_json=True`** option on `Get()`.
- **Bundled JSON snapshots** in-wheel (`data/quarks/`, `data/constants/`, `data/parameters.json`)
  — `Get()` is a fast file load with no simulation runtime cost.
- **`metaphysica-datasheets`** CLI — refreshes bundled snapshots after theory changes.
- **`metaphysica-build`** CLI — full website rebuild: sims + all generators + bundled site assets.
- **`py.typed`** marker (PEP 561).

### Changed

- **License: MIT → Apache-2.0.**
- **Slim base install** — `pip install metaphysica` pulls only numpy / scipy / sympy / mpmath /
  eml-math. Heavy deps behind extras: `[sims]`, `[plots]`, `[pdf]`, `[full]`.
- Gate labels: `72-gate ...` → `gate ...` across build output, JSON, and website headings.
  Gate identifiers (`G1`..`G72`) and count notation (`X/72`) unchanged.

### Fixed

- 3 silently-skipped tests corrected (test paths fixed post-v25 migration). Suite now 655
  passed, 0 skipped.
- `_from_snapshot()` reads `parameters.json` from the bundled wheel data dir first, falling
  back to the build-time `AutoGenerated/` copy.

### Removed

- Stale CLI entry points `pm-verify` and `pm-certificates`.
