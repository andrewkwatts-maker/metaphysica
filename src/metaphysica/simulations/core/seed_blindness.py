"""Which published rows CLAIM b_3 but do not move when b_3 moves.

WHY THIS EXISTS
===============
Four seed-blind writers were found one at a time, each by a different
accident: `g2_geometry` emitting literals (found by a fork that could not
propagate), `particle.b3` (found by a provenance guard), `RACETRACK_a`
(found by a re-measurement agent), `cosmology.b3` (found by an ambiguous-
alias guard). Each was a row that claimed to ride on b_3 and did not.

That is four instruments catching four instances of ONE defect class, which
means the class was never being searched for -- only stumbled into. This
module searches for it.

THE EPISTEMIC POINT, which is the real motivation
=================================================
A conclusion drawn from a frozen value is a bug report wearing a physics
result. "The racetrack vacuum does not exist on the adopted path" is a
strong claim; it is only worth anything if the exponents that produced it
actually followed the seed. The same applies to every recorded cost of the
b3_seed adoption -- eta_B at 18 sigma, the axion ceiling breach, the Higgs
divergence. Before any of those can be believed, the rows beneath them must
be shown to MOVE when the seed moves.

This is also the argument for switches over edits: because both branches are
runnable, "did this conclusion come from a bug?" is an experiment rather than
an audit. Run both, diff, and the frozen rows announce themselves.

THE METHOD
==========
Run the SAME registration path under both seeds in separate processes (the
registry is a per-process singleton, so in-process flipping proves nothing),
then classify every row that appears in both:

  MOVED         the value differs between seeds -- it consumes the seed
  FROZEN_CLAIM  the value is IDENTICAL but the row's own text/metadata
                mentions b_3: a suspect, and the defect class above
  STATIC        identical and no b_3 claim -- correct, most rows are this

A FROZEN_CLAIM is not automatically a bug: a row may legitimately mention
b_3 in prose while computing something else (D_space_24, the Leech
dimension, the bc-ghost count -- the disentangled bulk-24s). So the report
NAMES them for a reading rather than asserting a defect, and the ratchet is
on the count: it may fall, never rise.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, List

__all__ = ["rows_under_seed", "classify_rows", "seed_blindness_report"]

_CLAIM_TOKENS = ("b3", "b_3", "elder_kads", "betti")

_HARVEST = r"""
import json, sys

# Run the ACTUAL registration path, then harvest the in-memory registry.
# Reading the built parameters.json instead would be the very defect this
# module hunts: a file on disk does not move when the env var moves, so
# every row would report frozen and the detector would be a constant.
from metaphysica.simulations.run_all_simulations import SimulationRunner

runner = SimulationRunner(verbose=False)
try:
    runner.run_all()
except SystemExit:
    pass                      # exit 72 = non-sterile, expected on-path

out = {}
registry = runner.registry
rows = getattr(registry, "_parameters", None) or {}
for name, row in rows.items():
    payload = row if isinstance(row, dict) else getattr(row, "__dict__", {})
    value = payload.get("value", getattr(row, "value", None))
    rest = json.dumps(
        {k: str(v) for k, v in payload.items() if k != "value"}).lower()
    out[name] = {
        "value": value if isinstance(value, (int, float, str, bool, type(None)))
        else str(value),
        "claims_b3": any(t in rest for t in ("b3", "b_3", "elder_kads", "betti")),
    }
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"))
"""


def rows_under_seed(seed: str) -> Dict[str, Any]:
    """Registered rows as a FRESH process resolves them under `seed`.

    A subprocess, deliberately: FormulasRegistry is a per-process singleton
    built at import, so flipping the env var in-process leaves the already
    resolved values in place and every row would look frozen.
    """
    env = dict(os.environ)
    env["METAPHYSICA_VARIANT_B3_SEED"] = seed
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        target = fh.name
    try:
        proc = subprocess.run(
            [sys.executable, "-c", _HARVEST, target],
            env=env, capture_output=True, text=True, timeout=900)
        if proc.returncode != 0:
            return {"error": (proc.stderr or "")[-400:]}
        with open(target, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {"error": "%s: %s" % (type(exc).__name__, exc)}
    finally:
        try:
            os.unlink(target)
        except OSError:
            pass


def classify_rows(at_24: Dict[str, Any],
                  at_43: Dict[str, Any]) -> Dict[str, List[str]]:
    """MOVED / FROZEN_CLAIM / STATIC over the rows present under both."""
    out: Dict[str, List[str]] = {"MOVED": [], "FROZEN_CLAIM": [],
                                 "STATIC": []}
    for name in sorted(set(at_24) & set(at_43)):
        a, b = at_24[name], at_43[name]
        if not isinstance(a, dict) or not isinstance(b, dict):
            continue
        if a.get("value") != b.get("value"):
            out["MOVED"].append(name)
        elif a.get("claims_b3") or b.get("claims_b3") or any(
                t in name.lower() for t in _CLAIM_TOKENS):
            out["FROZEN_CLAIM"].append(name)
        else:
            out["STATIC"].append(name)
    return out


def seed_blindness_report() -> Dict[str, Any]:
    """The search, run over both seeds in fresh processes."""
    at_24 = rows_under_seed("seed_24")
    at_43 = rows_under_seed("seed_43_joyce")
    if "error" in at_24 or "error" in at_43:
        return {
            "available": False,
            "reason": at_24.get("error") or at_43.get("error"),
            "note": ("the harvest subprocess failed; an UNAVAILABLE report "
                     "is a reportable state, never a pass"),
        }

    classes = classify_rows(at_24, at_43)
    return {
        "available": True,
        "n_rows_compared": sum(len(v) for v in classes.values()),
        "n_moved": len(classes["MOVED"]),
        "n_frozen_claim": len(classes["FROZEN_CLAIM"]),
        "n_static": len(classes["STATIC"]),
        "frozen_claims": classes["FROZEN_CLAIM"],
        "moved": classes["MOVED"],
        "counts": (
            "registered parameter rows, compared between two FRESH "
            "processes resolving seed_24 and seed_43_joyce. FROZEN_CLAIM "
            "means the value did not move while the row's own text claims "
            "b_3 -- a suspect for a reading, not a proven defect: a row may "
            "legitimately say 'b_3' in prose while computing the bulk's 24 "
            "(D_space_24, dim Leech, the bc-ghost count)."
        ),
        "why_it_matters": (
            "a conclusion drawn from a frozen value is a bug report wearing "
            "a physics result. Every recorded cost of the adoption -- the "
            "deleted racetrack vacuum, eta_B at 18 sigma, the axion ceiling "
            "breach -- is only worth its weight if the rows beneath it "
            "actually move with the seed. Switches make that an experiment "
            "rather than an audit."
        ),
    }
