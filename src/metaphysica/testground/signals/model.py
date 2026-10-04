"""Signals: the measurements an assessment reads, declared with their binding.

A signal is evaluated against a SignalContext -- the configuration under test,
the root its run wrote to, and the stamp proving the artifacts there belong to
that configuration. A signal that reads an artifact whose stamp does not match
returns UNMEASURED (D-019 kill condition K4), never a stale number.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

__all__ = [
    "LIVE",
    "ARTIFACT",
    "SCREEN",
    "FULL",
    "MEASURED",
    "UNMEASURED",
    "UNEVALUABLE",
    "Measurement",
    "SignalContext",
    "Signal",
]

#: binding: computed in-process from code (LIVE) or read from the run's
#: artifacts (ARTIFACT).
LIVE = "live"
ARTIFACT = "artifact"
#: cost: available from the cheap in-process screen, or only after a full run.
SCREEN = "screen"
FULL = "full"

MEASURED = "MEASURED"
UNMEASURED = "UNMEASURED"        # could not be read (missing / stamp mismatch)
UNEVALUABLE = "UNEVALUABLE"      # read, but the quantity is not defined here


@dataclass(frozen=True)
class Measurement:
    """One signal's reading for one configuration."""

    signal: str
    status: str = MEASURED
    #: The integer count this signal contributes to its criterion (lower is
    #: better). None unless MEASURED.
    count: Optional[int] = None
    #: Free-form detail for the report: which checks failed, the values.
    detail: Dict[str, Any] = field(default_factory=dict)
    reasons: Tuple[str, ...] = ()

    @property
    def measured(self) -> bool:
        return self.status == MEASURED

    @classmethod
    def unmeasured(cls, signal: str, why: str) -> "Measurement":
        return cls(signal=signal, status=UNMEASURED, reasons=(why,))

    @classmethod
    def unevaluable(cls, signal: str, why: str) -> "Measurement":
        return cls(signal=signal, status=UNEVALUABLE, reasons=(why,))


@dataclass(frozen=True)
class SignalContext:
    """Where and for what a signal is evaluated."""

    theory: str
    digest: str
    selection: Tuple[Tuple[str, str], ...]
    #: The isolated root the configuration's run wrote to (None for screen).
    root: Optional[Path] = None
    #: The digest recorded in ``root/configuration.json`` by the runner.
    stamp_digest: Optional[str] = None

    @property
    def stamped(self) -> bool:
        return self.root is not None and self.stamp_digest == self.digest


@dataclass(frozen=True)
class Signal:
    """A named measurement feeding one criterion of the comparator."""

    id: str
    criterion: str                       # see assessment.score.CRITERIA
    binding: str                         # LIVE or ARTIFACT
    cost: str                            # SCREEN or FULL
    evaluate: Callable[[SignalContext], Measurement]
    description: str = ""

    def __call__(self, ctx: SignalContext) -> Measurement:
        if self.binding == ARTIFACT and not ctx.stamped:
            return Measurement.unmeasured(
                self.id, "artifact signal without a matching run stamp")
        try:
            return self.evaluate(ctx)
        except Exception as exc:   # a signal that crashes is UNMEASURED, loudly
            return Measurement.unmeasured(
                self.id, "%s: %s" % (type(exc).__name__, exc))
