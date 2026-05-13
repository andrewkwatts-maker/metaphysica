# Changelog

All notable changes to `metaphysica` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] — 2026-05-10

EML / Arithmos / metaphysica / periodica synchronised v1.4.0 cut. Adds an
**optional Rust acceleration core** mirroring eml-math's two-tier
pattern, plus an opt-in Arithmos symbolic-substrate bridge for engine
consumers. The pure-Python install path is unchanged.

### Added

- **`physica_core` Rust crate** at `rust/physica_core/` (cdylib + lib)
  housing the performance-critical pieces of the simulation engine:
  - `constants.rs` — `Constant{name, value, units, uncertainty, status,
    derivation_chain}`, `FormulasRegistry` with the Ten Pillar Seeds
    (`b3=24`, `chi_eff=72`, `n_gen=3`, `roots_total=288`,
    `visible_sector=125`, `sterile_sector=163`, golden ratio φ,
    Euler-Mascheroni γ, `JC_CONSTANT=153`, `LOGIC_CLOSURE=288`).
  - `quarks.rs` / `ckm.rs` — quark predictions + CKM matrix +
    unitarity check.
  - `gates.rs` — `gate_28_iterative` (explicit state stack, never
    recursive) so deep manifold logic doesn't risk stack overflow.
  - `simulations.rs` / `g2_manifold.rs` / `validation.rs` — temporal
    sync (RK4), G2 geometry primitives, CMB / isotropic-flow
    validators.
  - `pyfacade.rs` — PyO3 wrapper exposing `PyFormulasRegistry` to
    Python under `metaphysica._physica_core`.
  - `arithmos_bridge.rs` — gated `with-arithmos` opt-in for Arithmos
    symbolic-derivation tree carriers.
- **`[rust]` extra in pyproject** — `pip install metaphysica[rust]`
  pulls in maturin and triggers the Rust build path. Without the
  extra the slim install remains pure Python.
- **`_HAS_RUST` runtime guard** in `src/metaphysica/__init__.py` —
  flips to `True` when the maturin-built extension is available, so
  callers can detect and prefer the Rust path.
- **`[tool.maturin]` section** in `pyproject.toml` —
  `manifest-path = "rust/physica_core/Cargo.toml"`,
  `module-name = "metaphysica._physica_core"`,
  `features = ["python"]`. Maturin is loaded only when the active
  build backend is maturin (i.e. when the `[rust]` extra is enabled);
  the default setuptools build ignores it.

### Changed

- `__version__` bumped from `1.0.0` → `1.4.0` so the package version
  matches `pyproject.toml`'s `[project] version` and the family-wide
  v1.4.0 cut.

### Notes

- Existing 281 Python files are untouched. The Rust core is strictly
  additive — every Python codepath still works identically when
  `_HAS_RUST` is `False`.
- The Rust crate exposes a contract surface (`Constant`, `Quark
  Prediction`, `CKMMatrix`, `TemporalState`); the algorithm bodies
  populate as the hot-paths port (Yukawa φ-scaling, gate_28
  iterative, RK4 temporal sync). v1.4.0 ships the public types +
  PyO3 facade so downstream tooling can target the surface today
  even where individual functions still return placeholder values.

## [1.3.1] — 2026-05-03

PyPI re-publish. PyPI rejects re-upload of the 1.3.0 distributions (file-
name reuse policy) after the 1.3.0 wheel was already on PyPI. Cutting a
1.3.1 patch so the GitHub-release-triggered Trusted Publishing workflow
has fresh artefacts to upload. No functional changes; identical source
to 1.3.0.

## [1.3.0] — 2026-05-03

EML stack version sync. metaphysica, eml-math, and eml-spectral now share
the same major.minor.patch line.

### Changed
- Bumped `eml-math` dependency to `>=1.3.0` (datasheet `Get()` API,
  136 named math constants, abstracted render pipeline).
- Bumped optional `eml-spectral` dependency to `>=1.3.0` (Rust
  acceleration, C API, full algebra/lattice/heterotic catalogue).

### Added
- GitHub Actions CI workflow (`ci.yml`) — Python 3.11 / 3.12 / 3.13 matrix,
  installs `eml-math` from the v1.3.0 git tag during the pre-PyPI
  release window.
- GitHub Actions PyPI publish workflow (`workflow.yml`) — fires on
  release publication, builds wheel + sdist, publishes via Trusted
  Publishing (OIDC, environment `pypi`).

## [1.0.0] — 2026-05-03

First stable release.

### Added
- Public **`Get(name)` JSON-datasheet API** — returns a JSON-shaped
  dict for any of 12 quarks (6 SM + 6 anti) or ~35 curated physics
  constants. Schema is a strict superset of periodica's
  `data/active/quarks/*.json` plus a `pm_prediction` block carrying
  the metaphysica-derived value, the EML expression, and CKM couplings.
- **`list_quarks()` / `list_constants()`** for discovering names accepted
  by `Get()`. Quark names are case-insensitive (`"Up"`, `"u"`,
  `"Up Quark"`, `"AntiUp"` all resolve correctly).
- **`as_json=True`** option on `Get()` for shell-friendly output.
- **Bundled JSON snapshots** shipped inside the wheel
  (`metaphysica/data/quarks/`, `metaphysica/data/constants/`,
  `metaphysica/data/parameters.json`) so `Get()` is a fast file load
  with no simulation runtime cost.
- **`metaphysica-datasheets`** CLI entry point — refreshes the bundled
  snapshots after touching the underlying theory.
- New `Generate quark + constant datasheets` step in the
  `metaphysica.build` pipeline, runs automatically.
- **`py.typed`** marker (PEP 561) for downstream type checkers.
- **`CLAUDE.md`** in-repo guidance file.

### Changed
- **License: MIT → Apache-2.0** (matches the `LICENSE` file shipped
  since project inception; previous `pyproject.toml` was incorrect).
- **Slim base install.** `pip install metaphysica` now pulls only
  numpy / scipy / sympy / mpmath / eml-math (was: also pandas, matplotlib,
  xhtml2pdf, eml-spectral). Heavy / build-only deps are extras:
  - `[sims]` — eml-spectral (advanced algebras for the sim engine)
  - `[plots]` — matplotlib, pandas (plot regeneration)
  - `[pdf]` — xhtml2pdf (PDF paper export)
  - `[full]` — all of the above
- `metaphysica.build` now **skips steps whose extras are missing** with
  a friendly install hint instead of failing.
- User-visible labels: `72-gate ...` → `gate ...` / `Gates ...` across
  build steps, JSON titles, website headings, and prose. Gate
  identifiers (`G1`..`G72`) and count notation (`X/72`) are unchanged.

### Removed
- Stale CLI entry points `pm-verify` and `pm-certificates` (referenced
  modules that no longer exist post-v25 migration).

### Fixed
- 3 silently-skipped tests are now active (test paths corrected after
  the v25 migration). Test suite now reports 655 passed, 0 skipped.
- `_from_snapshot()` in the constant-datasheet builder now reads
  `parameters.json` from the bundled wheel data dir first, falling
  back to the build-time `<out_dir>/AutoGenerated/` copy. Previously
  it only worked from a cwd containing `AutoGenerated/parameters.json`.

## [0.1.0] — pre-release

Initial migration of the simulation engine, generators, and website
templates from the `PrincipiaMetaphysica` repo into the `metaphysica`
PyPI package layout. See `PrincipiaMetaphysica/CLAUDE.md` "What
changed in v25" for the migration details.
