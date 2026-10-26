"""Seeded random sample of full-path selections.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import random
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence

__all__ = ["sample_selections"]


def sample_selections(forks: Sequence[Any], n: int, *, seed: int,
                      canonical: Callable[[Mapping[str, str]], Mapping[str, str]] = dict,
                      compatible: Callable[[Mapping[str, str]], bool] = lambda s: True,
                      statuses: Sequence[str] = ("active", "considered"),
                      max_tries: Optional[int] = None) -> List[Dict[str, str]]:
    """*n* distinct, compatible, non-default selections, uniform per fork, deterministic.

    Dedup is by canonical form, so gated-off forks cannot make two samples differ.
    Raises ValueError with the count found when *n* cannot be reached.
    """
    tries = 100 * n if max_tries is None else max_tries
    pools = []
    for fork in forks:
        ids = [o.id for o in fork.options if o.status in statuses]
        if not ids:
            raise ValueError(f"fork {fork.id!r} has no option with status in {list(statuses)}")
        pools.append((fork.id, ids))
    default = {fork.id: fork.default() for fork in forks}
    rng = random.Random(seed)
    seen = {json.dumps(canonical(default), sort_keys=True)}
    out: List[Dict[str, str]] = []
    for _ in range(tries):
        if len(out) >= n:
            break
        sel = {fid: rng.choice(ids) for fid, ids in pools}
        key = json.dumps(canonical(sel), sort_keys=True)
        if key not in seen and compatible(sel):
            seen.add(key)
            out.append(sel)
    if len(out) < n:
        raise ValueError(f"found {len(out)} of {n} selections in {tries} tries")
    return out
