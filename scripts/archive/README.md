# Spent one-off scripts

Migration codemods and sprint-specific tooling that have already run. Kept for
provenance — they document how a rename or migration was actually performed —
but they are not part of any workflow and several would be actively harmful to
re-run against the current tree.

The `_` prefix was the original marker for "internal, one-shot"; this directory
makes that explicit rather than leaving them mixed in with live tooling.

Live scripts stay in `scripts/`:

| Script | Purpose |
|---|---|
| `audit_shadow_derivations.py` | run in CI |
| `audit_formulas.py` | formula-registry audit |
| `audit_output_parity.py` | lib vs site output parity |
| `audit_pm_drift.py` | drift against the site repo |
| `codemod_b3_leaf_inject.py` | b3-provenance injection |
| `migrate_formulas_to_triple.py` | triple-track migration |
| `visual_regression.py` | screenshot diffing against `tests/visual_baselines/` |
| `zenodo_pack.py` | release bundling |
