"""The toy theory's signals and data rows.

Every LIVE signal is computed in-process, in microseconds, from the
configuration under test (``ctx.selection``) -- never from the environment --
so the screen is faithful by construction. One ARTIFACT signal
(``consistency.screen_replay``, cost FULL) re-reads the full run's
``toy_output.json`` and counts the quantities where the subprocess disagrees
with the in-process screen: the toy's form of kill condition K2.

Signal ids carry their criterion as a prefix (``closure.fitted_inputs``).
Each count is lower-is-better; validity counts are failures, and a failing
validity signal itemizes them (``detail["failures"]``) and states its reason.
``validity.n_light_states`` is a READING (count 0, ``detail["value"]``): the
target fact n_light_states = 3 is pre-registered in ``assessment.yaml``, not
here. Discrete inputs declared by options (``adds_discrete_input``) are
counted by the test ground itself (``assessment.criteria.discrete_inputs``,
signal ``discrete_inputs``), so no toy signal repeats them.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable, Dict, Sequence, Tuple

from metaphysica.testground.signals.model import (
    ARTIFACT,
    FULL,
    LIVE,
    SCREEN,
    Measurement,
    Signal,
    SignalContext,
)
from metaphysica.testground.theory import ScoredRow
from metaphysica.theories.toy import model

__all__ = ["SIGNALS", "ToySignals", "ToyAnchors"]


def _prediction(ctx: SignalContext) -> model.Prediction:
    return model.predict(dict(ctx.selection))


def _tachyon(ctx: SignalContext) -> Measurement:
    m2 = _prediction(ctx)["observables"]["m2"]
    if m2 >= 0:
        return Measurement("validity.tachyon", count=0, detail={"m2": m2})
    why = ("tachyonic light state: m^2 = %.6g < 0 under mass_rule=%s"
           % (m2, dict(ctx.selection).get("mass_rule")))
    return Measurement("validity.tachyon", count=1,
                       detail={"m2": m2, "failures": ["tachyon"]},
                       reasons=(why,))


def _n_light_states(ctx: SignalContext) -> Measurement:
    n = _prediction(ctx)["n_light_states"]
    return Measurement("validity.n_light_states", count=0,
                       detail={"value": n})


def _fitted_inputs(ctx: SignalContext) -> Measurement:
    n = _prediction(ctx)["fitted_inputs"]
    return Measurement("closure.fitted_inputs", count=n,
                       detail={"fitted_inputs": n})


def _identity(name: str) -> Callable[[SignalContext], Measurement]:
    def evaluate(ctx: SignalContext) -> Measurement:
        residual = _prediction(ctx)["identities"][name]
        broken = residual > model.TOLERANCE
        return Measurement("consistency." + name, count=int(broken),
                           detail={"residual": residual},
                           reasons=("%s broken by %.3g" % (name, residual),)
                           if broken else ())
    return evaluate


def _elegance(key: str) -> Callable[[SignalContext], Measurement]:
    def evaluate(ctx: SignalContext) -> Measurement:
        pred = _prediction(ctx)
        return Measurement("elegance." + key, count=pred[key],
                           detail={"formulas": pred["formulas"]})
    return evaluate


def _chi2(rows: Sequence[Dict[str, Any]]) -> float:
    return sum(r["sigma"] ** 2 for r in rows if r.get("sigma") is not None)


def _data(key: str) -> Callable[[SignalContext], Measurement]:
    def evaluate(ctx: SignalContext) -> Measurement:
        rows = _prediction(ctx)["rows"]
        if key == "chi2_milli":
            count = int(round(1000 * _chi2(rows)))
        else:
            verdict = {"n_fail": "FAIL", "n_tension": "TENSION"}[key]
            count = sum(1 for r in rows if r["verdict"] == verdict)
        return Measurement("data." + key, count=count, detail={"rows": rows})
    return evaluate


def _same(a: Any, b: Any) -> bool:
    if isinstance(a, float) and isinstance(b, float):
        return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-15)
    return a == b


def _screen_replay(ctx: SignalContext) -> Measurement:
    path = Path(ctx.root) / model.ARTIFACT
    if not path.is_file():
        return Measurement.unmeasured("consistency.screen_replay",
                                      "no %s in the run root" % model.ARTIFACT)
    full = json.loads(path.read_text(encoding="utf-8"))
    live = _prediction(ctx)
    keys = [("observables", k) for k in live["observables"]] + \
           [("identities", k) for k in live["identities"]]
    differ = ["%s.%s" % k for k in keys
              if not _same(full[k[0]].get(k[1]), live[k[0]][k[1]])]
    return Measurement("consistency.screen_replay", count=len(differ),
                       detail={"differ": differ}, reasons=tuple(differ))


def _live(sid: str, criterion: str, fn: Callable[[SignalContext], Measurement],
          text: str) -> Signal:
    return Signal(sid, criterion, LIVE, SCREEN, fn, text)


SIGNALS: Tuple[Signal, ...] = (
    _live("validity.tachyon", "validity", _tachyon, "m^2 of the light state "
          "is not negative"),
    _live("validity.n_light_states", "validity", _n_light_states,
          "reading of n_light_states (target fact in assessment.yaml)"),
    _live("closure.fitted_inputs", "closure", _fitted_inputs,
          "continuous inputs fitted to data"),
    _live("consistency.ward_identity", "consistency",
          _identity("ward_identity"), "g_heavy + threshold = g0"),
    _live("consistency.lorentz_identity", "consistency",
          _identity("lorentz_identity"), "E^2 = p^2 + m^2"),
    _live("consistency.strong_cp_phase", "consistency",
          _identity("strong_cp_phase"), "a phase no path explains (standing)"),
    _live("elegance.unrooted_formulas", "elegance",
          _elegance("unrooted_formulas"), "formulas not rooted in the seed"),
    _live("elegance.literal_leaves", "elegance", _elegance("literal_leaves"),
          "raw non-integer literals in the formulas"),
    _live("data.n_fail", "data", _data("n_fail"), "rows beyond 3 sigma"),
    _live("data.n_tension", "data", _data("n_tension"), "rows at 2-3 sigma"),
    _live("data.chi2_milli", "data", _data("chi2_milli"),
          "chi^2 over the rows, x1000, rounded"),
    Signal("consistency.screen_replay", "consistency", ARTIFACT, FULL,
           _screen_replay, "the full run reproduces the screen (K2)"),
)


class ToySignals:
    """SignalProvider: the toy's signals."""

    def signals(self) -> Sequence[Signal]:
        return SIGNALS


class ToyAnchors:
    """AnchorProvider: the data rows a full run wrote."""

    def scored_rows(self, root: Path) -> Sequence[ScoredRow]:
        data = json.loads((Path(root) / model.ARTIFACT).read_text(
            encoding="utf-8"))
        return [ScoredRow(r["id"], r["verdict"], r.get("sigma"))
                for r in data["rows"]]
