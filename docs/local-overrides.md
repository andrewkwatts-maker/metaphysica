# Local overrides

Some pieces of the `metaphysica` framework are deliberately **not
committed to git** and **not shipped in the PyPI wheel**. They live only
on the author's local checkout and can be re-created by anyone who
wants that same overlay locally.

## `src/metaphysica/_gnostic_aliases.py`

A metadata overlay carrying the author's personal
Hebrew-gematria / mystical naming for the framework's topological seeds
(e.g. calling `b3 = 24` "The Governing Elder"). These names carry **no
independent physical meaning** and were removed from the published
source in v2.2.0 as part of the honesty polish.

The file is listed in `.gitignore` and is excluded from the wheel bundle
via maturin's default `.gitignore` respect. Nothing in the published
library depends on it — the wheel is fully self-contained.

### To recreate locally

Drop a file at `src/metaphysica/_gnostic_aliases.py` with:

```python
"""Local mystical / gematria alias overlay — gitignored, not shipped."""

GNOSTIC_METADATA = {
    "elder_kads":    {"gnostic_name": "The Governing Elder", "gematria": 24,  "hebrew": "Kad"},
    "mephorash_chi": {"gnostic_name": "The Shem HaMephorash",  "gematria": 72,  "hebrew": "Ayin-Bet"},
    "logos_joint":   {"gnostic_name": "The Logos Fish",         "gematria": 153, "hebrew": "Nun-Sofit"},
    # ... etc.  See the git history of FormulasRegistry.py pre-v2.2.0 for
    # the full mapping, or open a private issue with @andrewkwatts-maker.
}

__all__ = ["GNOSTIC_METADATA"]
```

Then in your personal notebooks:

```python
from metaphysica._gnostic_aliases import GNOSTIC_METADATA
print(GNOSTIC_METADATA["elder_kads"]["gnostic_name"])  # "The Governing Elder"
```

If the file is missing, no functionality of the published library is
affected — the wheel is fully self-contained.

## Why this pattern?

The mystical / gematria overlay was originally part of the framework's
narrative documentation. It was extracted from the committed source in
v2.2.0 because:

1. The names carry no physical meaning and could confuse readers into
   thinking they represent independent physics claims.
2. Peer reviewers and independent researchers should encounter the
   framework as clean geometric data without a religious/mystical
   overlay.
3. The author still wants access to the overlay for personal use, so
   it lives locally and is regenerated from the git history if lost.

This mirrors the way many research codebases keep author-specific
scratch data (unreleased datasets, private benchmarks) outside the
public release tree.
