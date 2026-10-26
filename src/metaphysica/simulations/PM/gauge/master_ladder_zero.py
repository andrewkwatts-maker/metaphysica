"""Lane L3a: zero modes and the nonabelian gauge source on the G2 step of the master ladder.

What the adopted G2 geometry gives is computed (`metaphysica.actions.zero_modes`) and
compared with what PM's actions declare. A mismatch is a failing check, never patched.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Callable, Dict, Mapping, Optional

from metaphysica.actions.correspondence import Correspondence
from metaphysica.actions.model import Action
from metaphysica.actions.spinors import dirac_dim
from metaphysica.actions.zero_modes import zero_modes
from metaphysica.simulations.PM.gauge import master_ladder_steps as S

# The D-028 class (name) whose singular A_(k-1) loci are kept to give nonabelian gauge
# fields. PM declares none today (L3a); set it only when a class is adopted.
GAUGE_SOURCE_CLASS: Optional[str] = None
GAUGE_REF = ("Acharya hep-th/9812205; Atiyah & Witten hep-th/0107177: M-theory on a smooth G2 "
             "gives U(1)^b2 only; nonabelian groups need singular loci kept")


def zero_mode_rule_for(parent: Action, child: Action, n: int = 7
                       ) -> Callable[[Mapping[int, int]], Dict[str, int]]:
    """Betti -> {child field name: components}, from `zero_modes` on the parent's fields.

    A kind the child does not declare keeps the kind name, so it reports as undeclared.
    """
    def rule(betti: Mapping[int, int]) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for kind, count in zero_modes(parent.fields, n, betti, "G2").items():
            fields = [f for f in child.fields
                      if f.kind == kind or (kind == "vector" and f.kind == "form:1")]
            name = fields[0].name if fields else kind
            out[name] = count * (dirac_dim(child.dim) if kind == "spinor" else 1)
        return out
    return rule


def declared_nonabelian(*actions: Action) -> Dict[str, str]:
    """SU(3) or SU(2) content PM declares in the given actions: fields or open terms."""
    out = {}
    for a in actions:
        for f in a.fields:
            if "SU(" in f.name:
                out["%s:%s" % (a.id, f.name)] = f.kind
        for t in a.terms:
            ref = S.OPEN_TERMS.get("%s:%s" % (a.id, t.id), ("", ()))[0]
            if "SU(3)" in ref or "SU(2)" in ref:
                out["%s:%s" % (a.id, t.id)] = ref
    return out


def active_scan() -> Dict[str, object]:
    """D-028 scan of the active Z2^3 with its A1 loci kept singular."""
    from metaphysica.simulations.PM.geometry import orbifold_gauge_scan as o

    lat = o.z7_lattice()
    rec = o.analyse(o.close_group(o.active_generators(lat, o.phi_active())), lat)
    ks = tuple(sorted({r["k"] for r in rec["strata"] if r["kind"] == "A"}))
    kept = o.betti_with_keep(rec["flat_betti"], rec["strata"], keep=ks)
    return {"gauge": rec["gauge"]["text"], "has_su3_su2": rec["gauge"]["has_su3_su2"],
            "b1": sorted({r["b1"] for r in rec["strata"]}), "kept_b2_b3": (kept[2], kept[3]),
            "smooth_b2_b3": (rec["betti"][2], rec["betti"][3])}


def nonabelian_gauge_source(a6: Action, a4: Action, b2: int) -> Correspondence:
    def compute():
        claims = declared_nonabelian(a6, a4)
        scan = active_scan()
        detail = ("smooth G2 gives U(1)^%d only; PM declares SU(3)/SU(2) in %s; source class: %s. "
                  "Active Z2^3 with its 12 A1 loci kept: %s with b1 = %s adjoint chirals "
                  "(non-chiral), has_su3_su2 = %s, kept (b2, b3) = %s. %s"
                  % (b2, sorted(claims) or "nothing", GAUGE_SOURCE_CLASS, scan["gauge"],
                     scan["b1"], scan["has_su3_su2"], scan["kept_b2_b3"], GAUGE_REF))
        holds = not claims or GAUGE_SOURCE_CLASS is not None
        return ("no source" if claims and not holds else "ok"), holds, detail

    return Correspondence("nonabelian_gauge_source", "6D", GAUGE_REF, compute)
