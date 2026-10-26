"""The PM chain 26D (24,2) -> 13D (12,1) -> 6D (5,1) -> 4D (3,1) as engine actions.

Step builders for `master_ladder`. Terms follow `master_action_audit.md` section 3;
every undefined term is OPEN with its audit reference, never filled in here.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from fractions import Fraction as Fr
from typing import Dict, Tuple

from metaphysica.actions.model import (
    DERIVED, INPUT, OPEN, Action, Coefficient, Field, Term,
)
from metaphysica.actions.spinors import dirac_dim, weyl_dim

P_MASTER = "metaphysica.simulations.PM.gauge.master_action"
P_LADDER = "metaphysica.simulations.PM.gauge.master_ladder"
AUDIT = "master_action_audit.md"

# term key "<action id>:<term id>" -> (audit reference, owner items blocking it)
OPEN_TERMS: Dict[str, Tuple[str, Tuple[int, ...]]] = {
    "A26:psi_mass": (AUDIT + " s4 (m Psi-bar Psi: no value; vanishes for a Weyl spinor)", (2,)),
    "A26:psi_quartic": (AUDIT + " s4 (lambda (Psi-bar Psi)^2: no value; 0.408 unproven)", (2, 3)),
    "A26:ym": (AUDIT + " s4 (-(1/4g^2) Tr F^2: g map and E8xE8 vs SM unreconciled)", (1, 8)),
    "A26:kT": (AUDIT + " s4 (-K|dT|^2: no value)", (1,)),
    "A26:V": (AUDIT + " s4 (V(T,phi): off-path calibration, moduli OPEN)", (1,)),
    "A26:xi_R_phi2": (AUDIT + " s4 (xi R phi^2: phi dimension 12 vs g_s = e^phi)", (8,)),
    "A26:L_bridge": (AUDIT + " s4 (sum_12 L_bridge: rho_breath, OR^i undefined)", (1,)),
    "A26:L_C": (AUDIT + " s4 (L_C: no definition)", (1,)),
    "A13:V_face": (AUDIT + " s4 (V_face: no definition)", (1,)),
    "A4:L_SM": (AUDIT + " s2 F and J (SU(3)/SU(2) sources OPEN, D-011)", ()),
    "A4:L_portal": (AUDIT + " s2 F (named, not defined)", ()),
    "A4:L_DM": (AUDIT + " s2 F (named, not defined)", ()),
}
UNDEFINED_SYMBOLS: Dict[str, str] = {
    "rho_breath": AUDIT + " s4 (L_bridge row)",
    "OR^i": AUDIT + " s4 (L_bridge row)",
    "V_bridge": AUDIT + " s4 (statements C, D; double counts L_bridge)",
    "V_face": AUDIT + " s4 (statements C, D, F)",
    "V_tor": AUDIT + " s4 (statement D)",
}


# "<action id>:<term id>" -> display form of the summand (the term carries the sign).
TERM_LATEX: Dict[str, str] = {
    "A26:R": r"\frac{M_*^{24}}{2}R",
    "A26:psi_kin": r"\bar\Psi_P\, i\Gamma^M D_M \Psi_P",
    "A26:psi_mass": r"m\,\bar\Psi_P \Psi_P",
    "A26:psi_quartic": r"\lambda\,(\bar\Psi_P \Psi_P)^2",
    "A26:ym": r"\frac{1}{4g^2}\mathrm{Tr}\,F_{MN}F^{MN}",
    "A26:kT": r"K_{T\bar T}\,|\partial T|^2",
    "A26:V": r"V(T,\phi)",
    "A26:xi_R_phi2": r"\xi R\,\phi^2",
    "A26:L_bridge": r"\sum_{i=1}^{12}\mathcal{L}^{i}_{\mathrm{bridge}}",
    "A26:L_C": r"\mathcal{L}_{C}",
    "A13:R": r"\frac{M_{13}^{11}}{2}R_{13}",
    "A13:psi_kin": r"\bar\Psi_P\, i\gamma^m D_m \Psi_P",
    "A13:V_face": r"V_{\mathrm{face}}^{(f)}",
    "A6:R": r"\frac{M_{6}^{4}}{2}R_{6}",
    "A6:psi_kin": r"\bar\Psi_P\, i\gamma^a D_a \Psi_P",
    "A4:R": r"\frac{M_{\mathrm{Pl}}^{2}}{2}R",
    "A4:psi_kin": r"\bar\Psi_P\, i\gamma^\mu D_\mu \Psi_P",
    "A4:L_SM": r"\mathcal{L}_{\mathrm{SM}}",
    "A4:L_portal": r"\mathcal{L}_{\mathrm{portal}}",
    "A4:L_DM": r"\mathcal{L}_{\mathrm{DM}}",
}


def _term(aid, tid, sym, dim, source, provider, factors=(), sign=1, derivs=0):
    coef = Coefficient(sym, Fr(dim), source, provider)
    return Term(tid, coef, tuple(factors), derivs, sign, source == OPEN,
                TERM_LATEX["%s:%s" % (aid, tid)])


def _open(aid, tid, dim, factors=(), sign=1):
    return _term(aid, tid, "c_" + tid, dim, OPEN, None, factors, sign)


def _gravity(aid, sym, dim, source, provider):
    return _term(aid, "R", sym, dim, source, provider, ("R",))


def _kinetic(aid, source, provider):
    return _term(aid, "psi_kin", "c_kin_" + aid, 0, source, provider, ("Psi", "Psi", "d"))


def _spinor(components, dim, chirality=None):
    return Field("Psi", "spinor", components, Fr(dim - 1, 2), chirality)


def action_26(spinor: str, exponent: int, convention: str) -> Action:
    """Audit section 3 canonical statement, one term per summand."""
    weyl = spinor == "weyl"
    psi = _spinor(weyl_dim(26) if weyl else dirac_dim(26), 26, "weyl" if weyl else None)
    fields = (Field("G", "metric", 1, Fr(0)), psi, Field("A", "form:1", 1, Fr(1)),
              Field("T", "scalar", 1, Fr(0)), Field("phi", "scalar", 1, Fr(12)))
    a = "A26"
    terms = [
        _gravity(a, "M_star_24", exponent, INPUT, P_MASTER),
        _kinetic(a, INPUT, P_MASTER),
        _open(a, "ym", 22, ("d", "A", "d", "A"), -1),
        _open(a, "kT", 24, ("d", "T", "d", "T"), -1),
        _open(a, "V", 26, (), -1),
        _open(a, "xi_R_phi2", 0, ("R", "phi", "phi")),
        _open(a, "L_bridge", 26),
        _open(a, "L_C", 26),
    ]
    if not weyl:  # a Weyl field has no mass or quartic term
        terms[2:2] = [_open(a, "psi_mass", 1, ("Psi", "Psi"), -1),
                      _open(a, "psi_quartic", -24, ("Psi",) * 4)]
    return Action(a, 26, (24, 2), fields, tuple(terms), convention)


def _simple(aid, dim, sig, comps, grav_sym, grav_dim, extra, convention):
    fields = (Field("G", "metric", 1, Fr(0)), _spinor(comps, dim))
    terms = (_gravity(aid, grav_sym, grav_dim, DERIVED, P_LADDER),
             _kinetic(aid, DERIVED, P_LADDER)) + extra
    return Action(aid, dim, sig, fields, terms, convention)


def action_13(convention: str) -> Action:
    return _simple("A13", 13, (12, 1), dirac_dim(13), "M13_11", 11,
                   (_open("A13", "V_face", 13),), convention)


def action_6(convention: str) -> Action:
    return _simple("A6", 6, (5, 1), dirac_dim(6), "M6_4", 4, (), convention)


def action_4(convention: str) -> Action:
    extra = tuple(_open("A4", n, 4) for n in ("L_SM", "L_portal", "L_DM"))
    return _simple("A4", 4, (3, 1), dirac_dim(4), "M_Pl_2", 2, extra, convention)
