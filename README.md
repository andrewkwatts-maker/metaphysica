# metaphysica

[![PyPI](https://img.shields.io/pypi/v/metaphysica.svg)](https://pypi.org/project/metaphysica/)
[![Python](https://img.shields.io/pypi/pyversions/metaphysica.svg)](https://pypi.org/project/metaphysica/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

G2-manifold-derived theoretical physics framework: 125+ derived
constants, a uniform `Get()` JSON-datasheet API for quarks + physics
constants, and a bundled static-website generator.

## Installation

```bash
pip install metaphysica            # slim core: numpy / scipy / sympy / mpmath / eml-math
                                   #   → enough for the Get() datasheet API
pip install metaphysica[sims]      # + eml-spectral (advanced algebras for the sim engine)
pip install metaphysica[plots]     # + matplotlib + pandas (plot regeneration)
pip install metaphysica[pdf]       # + xhtml2pdf (PDF paper export)
pip install metaphysica[full]      # everything above (recommended for `metaphysica-build`)
pip install metaphysica[dev]       # + pytest, black, mypy, build, twine
pip install metaphysica[rust]      # + optional Rust acceleration (see below)
```

`metaphysica` ships with `py.typed`, so type checkers see it as fully typed.

### Optional Rust acceleration

`metaphysica` ships an optional Rust core (`rust/physica_core/`) that
mirrors the Python public API behind a `_HAS_RUST` guard. The pure-Python
install path is **always** the default; the Rust extension is strictly
opt-in:

```bash
# Build via maturin (recommended for ad-hoc development):
pip install maturin
maturin develop --features python

# Or via pip extras (uses the [tool.maturin] section in pyproject.toml):
pip install metaphysica[rust]
```

When the extension is built, `metaphysica._physica_core` becomes
importable and `metaphysica._HAS_RUST` flips to `True`; if it is missing
(slim install, unsupported platform, or build skipped) every call
transparently falls back to the pure-Python implementation. The slim
`pip install metaphysica` path is unchanged and never invokes Rust.

## `Get()` — datasheet API

`metaphysica.Get(name)` returns a JSON-shaped datasheet for any quark
or named physics constant. It's the entry point that downstream layers
(periodica, future apps) consume.

```python
import metaphysica

metaphysica.Get('Up')['Mass_MeVc2']                       # 2.16
metaphysica.Get('Top')['pm_prediction']['phi_scaling_N']  # 0
metaphysica.Get('m_planck')['value']                      # 2.435e18
metaphysica.Get('alpha_em')['value']                      # 0.00729735...

metaphysica.list_quarks()                                 # 12 names (6 SM + 6 anti)
metaphysica.list_constants()                              # ~35 curated constants
```

Quark name aliases (case-insensitive):
`"Up"`, `"up"`, `"u"`, `"Up Quark"`, `"AntiUp"`, `"anti-up"`, …

The quark schema is a strict superset of periodica's
`data/active/quarks/*.json` — every periodica field plus a
`pm_prediction` block (Yukawa φ-scaling N, predicted mass, EML
expression, CKM couplings) and a `_provenance` block.

For shell use: `metaphysica.Get('Up', as_json=True)` returns a JSON
string instead of a dict.

### Bundled snapshots

Every entry returned by `Get()` is a pre-generated JSON shipped inside
the wheel (`metaphysica/data/quarks/`, `metaphysica/data/constants/`,
`metaphysica/data/parameters.json`), so calls do **not** re-run the
simulation. To regenerate the snapshots after touching the underlying
theory:

```bash
python -m metaphysica.generators.generate_datasheets
# or, equivalently:
metaphysica-datasheets
```

This step is also wired into `metaphysica.build` so a full website
build refreshes them automatically.

## Build pipeline

```python
from metaphysica import build
build(out_dir='./site')   # full build: sims + JSON + JS + HTML + datasheets + plots + PDF
```

Or from the shell:

```bash
metaphysica-build                   # rebuild into the current directory
metaphysica-build --out ./site      # rebuild into ./site
metaphysica-build --fast            # skip plot regeneration
metaphysica-build --skip-sims       # only refresh downstream generators
metaphysica-build --only "EML"      # run a single step
```

Steps whose optional extras are missing are skipped with a friendly
install hint, so a slim install never produces a broken build.

## Compatibility

- Python 3.9 – 3.13
- OS: Linux, macOS, Windows (pure Python wheel, no native deps in
  the slim install)

## Testing

```bash
pip install metaphysica[full,dev]
pytest                              # 655 tests, ~20s
```

## Stack

The EML stack is layered. Each layer's `Get(name)` returns a JSON
datasheet derived from that layer's theory:

| Layer | Package | `Get()` returns |
|-------|---------|-----------------|
| Maths | [`eml-math`](https://pypi.org/project/eml-math/) | math constants (e, π, φ, …) |
| Physics | `metaphysica` (this package) | quarks + physics constants |
| Materials | `periodica` (future) | element / compound datasheets |

## Related repositories

- [**PrincipiaMetaphysica**](https://github.com/andrewkwatts-maker/PrincipiaMetaphysica)
  — thin static-site host. Calls `metaphysica.build()` to render and
  serve the rendered theory site at
  [metaphysicæ.com](https://www.metaphysicæ.com).
- [**metaphysica-app**](https://github.com/andrewkwatts-maker/metaphysica-app)
  — interactive PC + mobile (APK) GUI on top of `metaphysica`.
  Browse the framework, explore constants, run derivations interactively.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the v1.0.0 release notes.

## License

Apache-2.0 — see [LICENSE](LICENSE).
