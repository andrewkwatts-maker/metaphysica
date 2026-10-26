"""The PM master action as a checked ladder: 26D -> 13D -> 6D -> 4D.

Builds on `metaphysica.actions` (L1). It decides no physics: owner items stay explicit in
`OWNER_ITEMS`, the ladder runs under the recommended option of each, and any term that
depends on an unresolved item is reported OPEN. Audit: `master_action_audit.md`.

Usage: `python -m metaphysica.simulations.PM.gauge.master_ladder OUT.json`

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Mapping, Optional

from metaphysica.actions.correspondence import Correspondence
from metaphysica.actions.ladder import Ladder, Step
from metaphysica.actions.model import Action
from metaphysica.actions.reduction import InternalSpace, Reduction
from metaphysica.actions.spinors import (
    REF as SPINOR_REF, dirac_dim, majorana_allowed, majorana_weyl_allowed,
    product_spinor_dim, weyl_dim,
)
from metaphysica.simulations.PM.gauge import master_ladder_steps as S

ITEM6_REF = "master_action_audit.md s5.8, s7 item 6"

# audit s7 item number -> (question, options, recommended, reason)
OWNER_ITEMS: Dict[int, tuple] = {
    1: ("Which sectors are in the single bulk action; drop or define L_C, V_bridge, V_face, "
        "V_tor, OR^i, rho_breath?", ("E8xE8 YM", "flux F_4", "KK tower", "none"), None, ""),
    2: ("Weyl vs Dirac bulk spinor", ("weyl", "dirac"), "weyl",
        "matches the 2026-08-31 signature ruling; m and lambda vanish for a Weyl field"),
    3: ("What is value 0.4082 (1/sqrt6) attached to pneuma-master-action-v23?", (), None, ""),
    4: ("Bulk Planck exponent", (23, 24, 25), 24,
        "D - 2 = 24 for D = 26; already the engine convention"),
    5: ("Sign convention", ("mostly_plus_mtw", "mostly_minus"), "mostly_plus_mtw",
        "mostly-plus metric with the MTW Riemann sign, as in the audit"),
    6: ("How the second time enters kk-ansatz-26-13", (), None, ""),
    7: ("Derive or label input: M_* ~ 1e16 GeV and Lambda ~ 1e-52 m^-2", (), None, ""),
    8: ("Map of the bulk g to g_GUT; dilaton dimension", (), None, ""),
    9: ("Should gauge_sector_complete SU(3)/SU(2) drop DERIVED while OPEN (D-011)?",
        (), None, ""),
    10: ("Audit items 15 and 17 (master-action-27d id; lagrangian-13d-effective)", (), None, ""),
    11: ("26 = 13 + 13: 2 x 64 shadow spinors versus the 4096 or 8192 bulk count",
         ("computed",), "computed", "decided by product_spinor_dim(13, 13), see report"),
}
_CONVENTION = {"mostly_plus_mtw": "mostly_plus", "mostly_minus": "mostly_minus"}


def resolve_options(overrides: Optional[Mapping[int, Any]] = None) -> Dict[int, Any]:
    """Recommended value per item (None when unresolved), with overrides applied."""
    opts = {k: v[2] for k, v in OWNER_ITEMS.items()}
    for k, val in (overrides or {}).items():
        if k not in OWNER_ITEMS:
            raise KeyError("unknown owner item %r" % (k,))
        allowed = OWNER_ITEMS[k][1]
        if allowed and val not in allowed:
            raise ValueError("item %d: %r not in options %r" % (k, val, allowed))
        opts[k] = val
    return opts


def item_11() -> Dict[str, Any]:
    """What the product rule says about the 26 = 13 + 13 spinor count."""
    prod = product_spinor_dim(13, 13)
    return {"product_13_13": prod, "naive_64x64": dirac_dim(13) ** 2,
            "dirac_26": dirac_dim(26), "weyl_26": weyl_dim(26),
            "supports": "dirac_8192_and_its_weyl_half_4096" if prod == dirac_dim(26)
            else "neither"}


def _product_check(step: str, parent: Action, child_dim: int, internal_dim: int):
    """The parent's spinor count must equal the product rule of child x internal."""
    field = parent.field("Psi")

    def compute():
        want = product_spinor_dim(child_dim, internal_dim)
        if field.chirality == "weyl":
            want //= 2
        return field.components, field.components == want, "product rule gives %d" % want

    return Correspondence("spinor_product:%s" % step, step, SPINOR_REF, compute)


def _leaf_check(action: Action) -> Correspondence:
    comps = action.field("Psi").components
    return Correspondence("spinor_dirac:%s" % action.id, action.id, SPINOR_REF,
                          lambda: (comps, comps == dirac_dim(action.dim), "Dirac count"))


def _item6_gate() -> Correspondence:
    detail = "26 -> 13 drops a time; no ruling on where it goes (audit s5.8, s7 item 6)"
    return Correspondence("owner_item_6", "A13", ITEM6_REF,
                          lambda: ("unresolved", False, detail))


def _internals() -> List[InternalSpace]:
    from metaphysica.simulations.PM.geometry.b3_path import resolve_path, seed_values

    b3, b2 = seed_values(resolve_path())
    betti = {0: 1, 1: 0, 2: b2, 3: b3}
    return [InternalSpace("bridge", 13, True, None, "Vol_13"),
            InternalSpace("G2_Y7", 7, True, betti, "Vol_7"),
            InternalSpace("KK", 2, False, None, "Vol_2")]  # PM declares no KK space


def build_ladder(opts: Mapping[int, Any]) -> Ladder:
    conv = _CONVENTION[opts[5]]
    a26 = S.action_26(opts[2], int(opts[4]), conv)
    a13, a6, a4 = S.action_13(conv), S.action_6(conv), S.action_4(conv)
    bridge, g2, kk = _internals()
    r13 = Reduction(a26, a13, bridge, {"M13_11": "M_star_24*Vol_13"}, signature_change=True)
    r6 = Reduction(a13, a6, g2, {"M6_4": "M13_11*Vol_7"})
    r4 = Reduction(a6, a4, kk, {"M_Pl_2": "M6_4*Vol_2"})
    return Ladder((
        Step("26D", a26),
        Step("13D", a13, r13, (_product_check("26D", a26, 13, 13), _item6_gate())),
        Step("6D", a6, r6, (_product_check("13D", a13, 6, 7),)),
        Step("4D", a4, r4, (_product_check("6D", a6, 4, 2), _leaf_check(a4))),
    ))


def _open_terms(ladder: Ladder) -> Dict[str, str]:
    out = {}
    for step in ladder.steps:
        for t in step.action.terms:
            if t.open:
                key = "%s:%s" % (step.action.id, t.id)
                out[key] = S.OPEN_TERMS[key][0]
    out.update({"undefined:" + k: v for k, v in S.UNDEFINED_SYMBOLS.items()})
    return out


def _unresolved(opts: Mapping[int, Any], open_terms: Mapping[str, str]) -> Dict[str, list]:
    out: Dict[str, list] = {}
    for key in open_terms:
        for item in S.OPEN_TERMS.get(key, ("", ()))[1]:
            if opts[item] is None:
                out.setdefault(str(item), []).append(key)
    out.setdefault("6", []).append("reduction:26D->13D")
    return {k: sorted(v) for k, v in sorted(out.items())}


def _spinor_counts() -> Dict[str, Any]:
    sigs = {"26D": (24, 2), "13D": (12, 1), "6D": (5, 1), "4D": (3, 1)}
    return {k: {"dirac": dirac_dim(sum(s)),
                "weyl": weyl_dim(sum(s)) if sum(s) % 2 == 0 else None,
                "majorana_allowed": majorana_allowed(*s),
                "majorana_weyl_allowed": majorana_weyl_allowed(*s)}
            for k, s in sigs.items()}


def report(option_overrides: Optional[Mapping[int, Any]] = None) -> Dict[str, Any]:
    """Ladder report plus owner items used, OPEN terms and spinor counts (JSON-ready)."""
    opts = resolve_options(option_overrides)
    ladder = build_ladder(opts)
    rep = ladder.report()
    open_terms = _open_terms(ladder)
    failing = sorted(c["id"] for s in rep["steps"] for c in s["checks"] if not c["holds"])
    return {"ladder": rep,
            "owner_items_used": {str(k): opts[k] for k in (2, 4, 5, 11)},
            "owner_items_unresolved": _unresolved(opts, open_terms),
            "open_terms": open_terms, "failing_checks": failing,
            "counts": {"open_terms": len(open_terms), "failing_checks": len(failing)},
            "spinors": _spinor_counts(), "item_11": item_11()}


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("usage: master_ladder OUT.json", file=sys.stderr)
        return 2
    with open(argv[1], "w", encoding="utf-8") as fh:
        json.dump(report(), fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
