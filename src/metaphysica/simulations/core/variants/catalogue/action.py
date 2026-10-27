"""Catalogue: the master action's open choices (owner items 1, 2, 4, 5).

Each fork mirrors one `OWNER_ITEMS` entry of `simulations.PM.gauge.master_ladder`;
the adopted option is that table's recommendation, so the default ladder is
unchanged. `master_ladder.report` reads them through `resolve`.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from typing import Dict

from ..model import Fork, VariantOption
from ..adopted import (
    _action_bulk_sectors_adopted,
    _action_bulk_spinor_adopted,
    _action_planck_exponent_adopted,
    _action_sign_convention_adopted,
)

_SRC = "simulations.PM.gauge.master_ladder.OWNER_ITEMS"
_CONSUMER = ("metaphysica.simulations.PM.gauge.master_ladder",)
_AUDIT = "master_action_audit.md s7 item "


def _opt(oid: str, summary: str, consequence: str, adopted: bool = False):
    return VariantOption(id=oid, summary=summary, consequence=consequence,
                         adopted=adopted)


def _fork(fid: str, item: int, question: str, adopted, options, notes: str) -> Fork:
    return Fork(id=fid, question=question, source="%s[%d]" % (_SRC, item),
                status="OPEN", read_adopted=adopted, options=options,
                notes=_AUDIT + "%d. %s" % (item, notes), consumers=_CONSUMER,
                kind="physics", binding="call_time")


_KEPT = ("The bulk terms stay OPEN; only the item's 'unresolved' bookkeeping "
         "changes (no term is defined by choosing it).")

FORKS: Dict[str, Fork] = {
    "action_bulk_sectors": _fork(
        "action_bulk_sectors", 1,
        "Which sectors are in the single 26D bulk action?",
        _action_bulk_sectors_adopted,
        [
            _opt("undecided", "no ruling; every sector term stays OPEN and item 1 "
                 "is reported unresolved",
                 "The ladder as built today: build_ladder ignores item 1 and the "
                 "report lists ym, kT, V, L_bridge, L_C and V_face as blocked by it.",
                 adopted=True),
            _opt("e8xe8_ym", "E8xE8 Yang-Mills is the gauge sector", _KEPT),
            _opt("flux_f4", "the flux F_4 sector", _KEPT),
            _opt("kk_tower", "a KK tower", _KEPT),
            _opt("none", "no extra sectors: drop ym, kT, V, L_bridge, L_C and V_face",
                 "Removes every term item 1 blocks; the bulk action is gravity "
                 "plus the spinor only, so the OPEN count falls and the checks "
                 "that need those terms are no longer asked."),
        ],
        "Drop or define L_C, V_bridge, V_face, V_tor, OR^i, rho_breath."),
    "action_bulk_spinor": _fork(
        "action_bulk_spinor", 2, "Weyl or Dirac bulk spinor?",
        _action_bulk_spinor_adopted,
        [
            _opt("weyl", "a Weyl bulk spinor (4096 components in 26D)",
                 "Matches the 2026-08-31 signature ruling; m and lambda vanish "
                 "for a Weyl field, so psi_mass and psi_quartic are absent.",
                 adopted=True),
            _opt("dirac", "a Dirac bulk spinor (8192 components in 26D)",
                 "Doubles the 26D spinor count and adds the OPEN psi_mass and "
                 "psi_quartic terms; the 26 = 13 + 13 product rule then holds "
                 "without a Weyl halving."),
        ],
        "Weyl vs Dirac bulk spinor."),
    "action_planck_exponent": _fork(
        "action_planck_exponent", 4, "Bulk Planck exponent in M_*^n R",
        _action_planck_exponent_adopted,
        [
            _opt("exponent_24", "n = D - 2 = 24",
                 "The engine convention for D = 26.", adopted=True),
            _opt("exponent_23", "n = 23", "Mass dimension of the gravity "
                 "coefficient is 23, so the dimension check on the R term fails."),
            _opt("exponent_25", "n = 25", "Mass dimension of the gravity "
                 "coefficient is 25, so the dimension check on the R term fails."),
        ],
        "Bulk Planck exponent."),
    "action_sign_convention": _fork(
        "action_sign_convention", 5, "Metric signature and Riemann sign convention",
        _action_sign_convention_adopted,
        [
            _opt("mostly_plus_mtw", "mostly-plus metric with the MTW Riemann sign",
                 "As in the audit; the weak-field Newtonian check holds.",
                 adopted=True),
            _opt("mostly_minus", "mostly-minus metric",
                 "With the audit's Lagrangian signs unchanged, the weak-field "
                 "sign check reports FAILS (found by E1)."),
        ],
        "Sign convention."),
}
