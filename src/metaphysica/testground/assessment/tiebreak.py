"""The data tie-break: criterion 5, consulted ONLY inside a group of equals.

D-019 row 5: between configurations equal on criteria 1-4, agreement with data
may order them -- on the rows COMMON to the tied group, with the policy forks
held fixed -- and the result always discloses:

* the trials factor k, the number of configurations the data chose among
  (the group size), and
* that accepting on it adds ONE fitted degree of freedom to the theory.

The data key is (n_FAIL, n_TENSION, chi2_milli), lower is better, where
chi2_milli is round(1000 * sum sigma^2) over the common rows whose sigma is
known in every member (integer keys, score.py). If any member has no data the
tie-break does not run: a group cannot be ordered on a value some members lack.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import (Any, Dict, FrozenSet, List, Mapping, Optional, Sequence,
                    Tuple)

from metaphysica.testground.assessment.score import DATA, ScoreVector
from metaphysica.testground.theory import ScoredRow

__all__ = [
    "CHI2_QUANTUM",
    "DATA_KEY_COMPONENTS",
    "FITTED_DOF_ON_ACCEPT",
    "COMMON_ROWS",
    "PER_CONFIGURATION",
    "NO_DATA",
    "TieBreak",
    "common_row_ids",
    "data_key",
    "order_by_key",
    "tiebreak",
]

#: chi^2 is compared in thousandths, so the key stays integer.
CHI2_QUANTUM = 1000
DATA_KEY_COMPONENTS = ("n_FAIL", "n_TENSION", "chi2_milli")
#: Accepting a configuration on the data tie-break costs one fitted dof.
FITTED_DOF_ON_ACCEPT = 1

# basis of a tie-break
COMMON_ROWS = "common_rows"
PER_CONFIGURATION = "per_configuration"
NO_DATA = "no_data"

DataKey = Tuple[int, ...]


@dataclass(frozen=True)
class TieBreak:
    """The data ordering inside one group of equals, with its disclosure."""

    group: Tuple[str, ...]
    #: data sub-groups, lowest key first; one sub-group = no separation.
    order: Tuple[Tuple[str, ...], ...]
    keys: Dict[str, Optional[DataKey]]
    basis: str
    common_rows: Optional[int] = None
    chi2_rows: Optional[int] = None
    reasons: Tuple[str, ...] = ()

    @property
    def k(self) -> int:
        """The trials factor: how many configurations the data chose among."""
        return len(self.group)

    @property
    def separates(self) -> bool:
        return len(self.order) > 1

    @property
    def leader(self) -> Optional[str]:
        """The single configuration the data puts first, if there is one."""
        if self.separates and len(self.order[0]) == 1:
            return self.order[0][0]
        return None

    @property
    def fitted_dof_on_accept(self) -> int:
        return FITTED_DOF_ON_ACCEPT

    def as_dict(self) -> Dict[str, Any]:
        return {
            "group": list(self.group),
            "order": [list(sub) for sub in self.order],
            "keys": {d: (list(k) if k is not None else None)
                     for d, k in self.keys.items()},
            "key_components": list(DATA_KEY_COMPONENTS),
            "basis": self.basis,
            "common_rows": self.common_rows,
            "chi2_rows": self.chi2_rows,
            "trials_factor_k": self.k,
            "leader": self.leader,
            "fitted_dof_on_accept": self.fitted_dof_on_accept,
            "reasons": list(self.reasons),
        }


def _rows_by_id(rows: Sequence[ScoredRow]) -> Dict[str, ScoredRow]:
    return {r.id: r for r in rows}


def common_row_ids(rows: Mapping[str, Sequence[ScoredRow]]) -> FrozenSet[str]:
    """Row ids present for every configuration."""
    sets = [frozenset(r.id for r in rs) for rs in rows.values()]
    return frozenset.intersection(*sets) if sets else frozenset()


def _chi2_ids(rows: Mapping[str, Sequence[ScoredRow]],
              common: FrozenSet[str]) -> FrozenSet[str]:
    indexed = [_rows_by_id(rs) for rs in rows.values()]
    return frozenset(i for i in common
                     if all(ix[i].sigma is not None for ix in indexed))


def data_key(rows: Sequence[ScoredRow], ids: FrozenSet[str],
             chi2_ids: FrozenSet[str]) -> DataKey:
    """(n_FAIL, n_TENSION, chi2_milli) over the rows ``ids``."""
    by_id = _rows_by_id(rows)
    chosen = [by_id[i] for i in sorted(ids)]
    n_fail = sum(1 for r in chosen if r.verdict.upper() == "FAIL")
    n_tension = sum(1 for r in chosen if r.verdict.upper() == "TENSION")
    chi2 = sum(by_id[i].sigma ** 2 for i in sorted(chi2_ids))
    return (n_fail, n_tension, int(round(CHI2_QUANTUM * chi2)))


def order_by_key(digests: Sequence[str],
                 keys: Mapping[str, DataKey]) -> Tuple[Tuple[str, ...], ...]:
    """Sub-groups of equal keys, lowest first; input order kept inside."""
    distinct = sorted({keys[d] for d in digests})
    return tuple(tuple(d for d in digests if keys[d] == k) for k in distinct)


def _no_data(digests: Tuple[str, ...], why: str,
             keys: Optional[Dict[str, Optional[DataKey]]] = None) -> TieBreak:
    return TieBreak(digests, (digests,), keys or {d: None for d in digests},
                    NO_DATA, reasons=(why,))


def _from_rows(digests: Tuple[str, ...],
               rows: Mapping[str, Sequence[ScoredRow]]) -> TieBreak:
    missing = [d for d in digests if d not in rows]
    if missing:
        return _no_data(digests, "no scored rows for %s" % ", ".join(missing))
    group_rows = {d: rows[d] for d in digests}
    common = common_row_ids(group_rows)
    chi2_ids = _chi2_ids(group_rows, common)
    keys = {d: data_key(group_rows[d], common, chi2_ids) for d in digests}
    return TieBreak(digests, order_by_key(digests, keys), dict(keys),
                    COMMON_ROWS, len(common), len(chi2_ids))


def _from_vectors(group: Sequence[ScoreVector]) -> TieBreak:
    digests = tuple(v.digest for v in group)
    keys = {v.digest: v.score(DATA).key for v in group}
    if any(not v.score(DATA).measured or keys[v.digest] is None
           for v in group):
        return _no_data(digests, "data not measured for every member", keys)
    return TieBreak(digests, order_by_key(digests, keys), dict(keys),
                    PER_CONFIGURATION,
                    reasons=("per-configuration data keys: rows were not "
                             "restricted to the group's common rows",))


def tiebreak(group: Sequence[ScoreVector],
             rows: Optional[Mapping[str, Sequence[ScoredRow]]] = None
             ) -> TieBreak:
    """Order a group of configurations equal on criteria 1-4 by data.

    With ``rows`` (digest -> scored rows) the key uses only the rows common
    to the group; otherwise each vector's own data key is used and the basis
    says so.
    """
    if rows is not None:
        return _from_rows(tuple(v.digest for v in group), rows)
    return _from_vectors(group)
