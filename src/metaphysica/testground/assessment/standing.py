"""Standing failures: checks that fail in EVERY assessed configuration.

D-019 amendment (c): a check failing everywhere cannot tell configurations
apart, so it is excluded from the comparison and DISCLOSED in the report --
never silently dropped.

What a "check" is
=================
Only the check criteria -- validity and consistency -- carry checks. Closure
and elegance signals are measures (sizes, counts of formulas): a value shared
by every configuration is not a failure, so they never stand.

* An itemized measurement lists its failing items in ``detail["failures"]``;
  each item is the check ``"<signal>:<item>"``.
* A measurement without an item list is one check, ``"<signal>"``, failing
  when its count is positive. It is standing only when it fails with the SAME
  count in every assessed configuration, so excluding it removes no
  difference between them.

Only configurations that were actually measured take part (a configuration
with no measurement at all was not run). With fewer than two assessed
configurations nothing is standing -- one configuration has nothing to be
compared against, so excluding its failures would only hide them.

Target facts (assessment config) are never standing: they are what every
configuration must reproduce.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import (Any, Dict, FrozenSet, Iterable, List, Mapping, Optional,
                    Sequence, Union)

from metaphysica.testground.assessment.score import (CONSISTENCY, CRITERIA,
                                                     VALIDITY)
from metaphysica.testground.signals.model import Measurement, Signal

__all__ = [
    "CHECK_CRITERIA",
    "MIN_CONFIGURATIONS",
    "by_criterion",
    "item_ids",
    "failing_checks",
    "standing_failures",
    "effective_count",
    "live_failures",
]

#: The criteria whose signals are pass/fail checks.
CHECK_CRITERIA = (VALIDITY, CONSISTENCY)
#: Fewer assessed configurations than this and nothing is standing.
MIN_CONFIGURATIONS = 2

SignalLookup = Union[Sequence[Signal], Mapping[str, str], None]


def _criterion_lookup(signals: SignalLookup) -> Dict[str, str]:
    """signal id -> criterion, from Signal objects or a plain mapping."""
    if signals is None:
        return {}
    if isinstance(signals, Mapping):
        return dict(signals)
    return {s.id: s.criterion for s in signals}


def by_criterion(measurements: Any,
                 signals: SignalLookup = None) -> Dict[str, List[Measurement]]:
    """Group measurements by criterion.

    Accepts a mapping ``criterion -> measurements``, or an iterable of
    ``(Signal, Measurement)`` pairs, or of bare Measurements whose criterion
    is looked up in ``signals`` (Signal objects or ``{signal id: criterion}``).
    """
    out: Dict[str, List[Measurement]] = {c: [] for c in CRITERIA}
    if isinstance(measurements, Mapping):
        unknown = sorted(set(measurements) - set(CRITERIA))
        if unknown:
            raise ValueError("measurements keyed by unknown criteria: %s"
                             % ", ".join(map(str, unknown)))
        for criterion, ms in measurements.items():
            out[criterion].extend(ms)
        return out
    lookup = _criterion_lookup(signals)
    for item in measurements:
        if isinstance(item, tuple):
            signal, m = item
            out[signal.criterion].append(m)
            continue
        if item.signal not in lookup:
            raise ValueError("no criterion known for signal %r; pass the "
                             "theory's signals" % item.signal)
        out[lookup[item.signal]].append(item)
    return out


def item_ids(m: Measurement) -> Optional[List[str]]:
    """The itemized failure ids of ``m`` ("signal:item"), or None."""
    items = m.detail.get("failures") if isinstance(m.detail, dict) else None
    if not isinstance(items, (list, tuple)) or not items:
        return None
    return ["%s:%s" % (m.signal, item) for item in items]


def failing_checks(m: Measurement) -> FrozenSet[str]:
    """Every check ``m`` reports as failing (empty unless MEASURED)."""
    if not m.measured:
        return frozenset()
    items = item_ids(m)
    if items is not None:
        return frozenset(items)
    if m.count is not None and m.count > 0:
        return frozenset({m.signal})
    return frozenset()


def _checks(grouped: Mapping[str, List[Measurement]]) -> List[Measurement]:
    return [m for c in CHECK_CRITERIA for m in grouped.get(c, ())]


def _whole_signal_counts(ms: Iterable[Measurement]) -> Dict[str, int]:
    return {m.signal: m.count for m in ms
            if m.measured and item_ids(m) is None and m.count}


def standing_failures(measurements: Mapping[str, Any],
                      signals: SignalLookup = None,
                      min_configurations: int = MIN_CONFIGURATIONS
                      ) -> FrozenSet[str]:
    """Check ids failing in every assessed configuration.

    ``measurements`` maps a configuration digest to its measurements in any
    form `by_criterion` accepts.
    """
    grouped = {d: by_criterion(ms, signals) for d, ms in measurements.items()}
    assessed = {d: _checks(g) for d, g in grouped.items()
                if any(g.values())}
    if len(assessed) < max(min_configurations, 1):
        return frozenset()
    per_cfg = [frozenset().union(*(failing_checks(m) for m in ms))
               for ms in assessed.values()]
    common = frozenset.intersection(*per_cfg)
    whole = [_whole_signal_counts(ms) for ms in assessed.values()]
    varying = {s for s in common
               if s in whole[0] and len({w.get(s) for w in whole}) > 1}
    return frozenset(common - varying)


def effective_count(m: Measurement, standing: FrozenSet[str]) -> Optional[int]:
    """``m.count`` with its standing failures excluded (None if no count)."""
    if m.count is None:
        return None
    items = item_ids(m)
    if items is None:
        return 0 if m.signal in standing else m.count
    excluded = sum(1 for i in items if i in standing)
    return max(m.count - excluded, 0)


def live_failures(m: Measurement, standing: FrozenSet[str]) -> List[str]:
    """Failing checks of ``m`` that are not standing, sorted."""
    return sorted(failing_checks(m) - standing)
