"""README status claims must not contradict the shadow-derivation auditor.

WHY THIS EXISTS
---------------
The README carried a hand-written "candidate resolutions" table claiming the
Higgs sector was "closed" ("derived from b3") while the auditor held a live
m_higgs conflict: the derived 120.62 GeV against the PDG-anchored 125.2, a
3.7% gap. Documentation that contradicts the machine state undermines every
other claim on the page.

The mapping below ties README table keywords to auditor observables. A row
may say whatever it likes about tension or progress, but it may not say
"closed" while its observable sits in the auditor's conflict set.
"""
from __future__ import annotations

import importlib.util
import io
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

#: README table keyword -> shadow-auditor observable name.
_CLAIM_MAP = {
    "Higgs sector": "m_higgs",
    "Inflation observables": "n_s",
}


def _known_conflicts():
    spec = importlib.util.spec_from_file_location(
        "shadow_audit", _ROOT / "scripts" / "audit_shadow_derivations.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.KNOWN_CONFLICTS


def test_no_closed_claim_for_a_conflicted_observable():
    conflicts = _known_conflicts()
    readme = io.open(_ROOT / "README.md", encoding="utf-8").read()
    offenders = []
    for line in readme.splitlines():
        if "| closed |" not in line.replace("**", ""):
            continue
        for keyword, observable in _CLAIM_MAP.items():
            if keyword in line and observable in conflicts:
                offenders.append(f"{keyword} ({observable}): {line.strip()[:80]}")
    assert not offenders, (
        "README claims 'closed' for observables the auditor holds in "
        "conflict:\n  " + "\n  ".join(offenders)
    )


def test_the_check_is_not_vacuous():
    """Either the table is there and the map matches it, or it is gone.

    The README's "candidate resolutions" table was replaced by a pointer to
    OUTSTANDING_ISSUES.md, so the keywords this map guards no longer appear
    and the check above has nothing to range over. That is a legitimate
    state, not a failure -- but it must be DISTINGUISHED from the table
    having been renamed or reworded, which would leave a live claim
    unguarded while the test quietly passed.

    So: if the table is absent, require that no "| closed |" row survives at
    all. If any such row exists, the map must match it. The guard therefore
    stays armed for the table's return instead of being deleted with it.
    """
    readme = io.open(_ROOT / "README.md", encoding="utf-8").read()
    closed_rows = [ln for ln in readme.splitlines()
                   if "| closed |" in ln.replace("**", "").lower()]
    matched = [k for k in _CLAIM_MAP if k in readme]

    if not closed_rows:
        assert not matched, (
            "the README carries the mapped keywords but no '| closed |' "
            "rows; the table has been reworded and _CLAIM_MAP no longer "
            "describes it"
        )
        return

    assert matched, (
        f"the README still has {len(closed_rows)} '| closed |' row(s) but "
        f"none of the mapped keywords {sorted(_CLAIM_MAP)} appear, so "
        f"test_no_closed_claim_for_a_conflicted_observable is checking "
        f"nothing. Update the map to the table's current wording."
    )
