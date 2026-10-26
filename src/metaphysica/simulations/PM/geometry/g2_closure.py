"""Closing the G2 geometry: every hypothesis of Joyce's existence theorem, measured.

WHAT "CLOSED" MEANS (D-023)
===========================
No explicit compact G2 metric is known. Joyce's construction is closed when every
hypothesis of the existence theorem is measured on the adopted seed, each by code
that can fail, and the conclusions then follow by citation:

  * a torsion-free G2 structure exists on the resolution   Joyce 2000, Thm 11.6.1
  * it is Ricci-flat                                       Bonan
  * its holonomy is all of G2                              Joyce 1996 II, Prop 1.1.1
                                                           (Hol = G2 iff pi_1 finite)

Hypotheses (plan: PrincipiaMetaphysica/docs/plan/geometry/2026-10-25-close-g2.md):

  H1  Gamma preserves phi0                          joyce_orbifold.diagonal_stabiliser
  H2  phi0 is positive, Hitchin metric (7,0)        g2_differential.real_form_report
  H3  every singular component is T^3 x C^2/Z2      joyce_resolution.resolution_report
  H4a phi0's triple on each flipped 4-plane is definite (hyperkahler)        here
  H4b the Eguchi-Hanson triple is closed; the other orientation is not       here
  H4c phi = sum over the frame on EH x T^3 has d phi = d*phi = 0              here
  H5  Eguchi-Hanson decays to flat at rate r^-4     eguchi_hanson.ale_decay_report
  H6  pi_1 finite and b_1 = 0                       fundamental_group, joyce_resolution
  H7  exactly one Gamma-invariant constant spinor   here (Cl(7) from phi itself)
  H8  the glued form is compact-orbit at small t    glued_orbit_scan

Every new measurement takes phi as an argument, so the split form can be run
against the compact one, and every test has a failing control.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

#: The three self-/anti-self-dual pairs of R^4 in the frame order 0123.
_PAIRS = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))
#: Sign tying the second member of each pair to the first under * in e^0123:
#: *(e01) = e23, *(e02) = -e13, *(e03) = e12.
_STAR_SIGN = (1, -1, 1)


# ------------------------------------------------------------------ phi

def phi_for(convention: Optional[str] = None) -> np.ndarray:
    """The dense (7,7,7) phi0 of a `g2_form_convention` option (default: resolved)."""
    from metaphysica.simulations.PM.geometry import g2_differential as g2d

    if convention is None:
        return g2d.G2DifferentialGeometry._standard_phi()
    if convention == "octonion_derived":
        return g2d.phi_from_octonion_product()
    if convention != "all_plus_one":
        raise ValueError("unknown g2_form_convention %r" % convention)
    return g2d.phi_all_plus_one()


def _parity(seq: Sequence[int]) -> int:
    """Sign of the permutation sorting `seq` (distinct entries)."""
    seq, sign = list(seq), 1
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                sign = -sign
    return sign


def gamma_elements(phi: np.ndarray) -> List[Tuple[int, ...]]:
    """H1: the diagonal sign flips of R^7 that preserve phi (exhaustive)."""
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        diagonal_stabiliser,
    )

    class _Phi:                       # diagonal_stabiliser reads `.phi`
        pass

    holder = _Phi()
    holder.phi = phi
    return diagonal_stabiliser(holder)


# ------------------------------------------------------------------ H4a

def _frame_order(eps: Sequence[int], swap: bool = False) -> List[int]:
    """Coordinates in frame order: the flipped 4-plane first, then the fixed line."""
    plane = [i for i, e in enumerate(eps) if e == -1]
    line = [i for i, e in enumerate(eps) if e == 1]
    if swap:
        plane[2], plane[3] = plane[3], plane[2]
    return plane + line


def frame_phi(phi: np.ndarray, order: Sequence[int]) -> np.ndarray:
    """phi relabelled so frame index n is coordinate order[n]."""
    idx = np.array(order)
    return phi[np.ix_(idx, idx, idx)]


def flat_triple(phi_f: np.ndarray) -> List[Dict[Tuple[int, int], float]]:
    """omega_m = i_{e_{4+m}} phi on the 4-plane, so phi = ... + sum e^{4+m} ^ omega_m."""
    return [{(a, b): float(phi_f[4 + m, a, b])
             for a, b in itertools.combinations(range(4), 2)}
            for m in range(3)]


def duality(omega: Dict[Tuple[int, int], float]) -> str:
    """SD / ASD / NEITHER of a constant 2-form on R^4, orientation e^0123."""
    parts = [(omega[p], s * omega[q]) for (p, q), s in zip(_PAIRS, _STAR_SIGN)]
    if all(abs(x - y) < 1e-12 for x, y in parts):
        return "SD"
    if all(abs(x + y) < 1e-12 for x, y in parts):
        return "ASD"
    return "NEITHER"


def pairing_matrix(triple) -> np.ndarray:
    """Q_mn = (omega_m ^ omega_n) / vol on R^4. Definite iff a hyperkahler triple."""
    def top(w, v):
        return sum(s * (w[p] * v[q] + w[q] * v[p])
                   for (p, q), s in zip(_PAIRS, _STAR_SIGN))
    return np.array([[top(w, v) for v in triple] for w in triple])


def triple_definiteness(phi: np.ndarray) -> Dict[str, Any]:
    """H4a over every non-identity element of Gamma (every flipped 4-plane)."""
    rows = []
    for eps in gamma_elements(phi):
        if all(e == 1 for e in eps):
            continue
        triple = flat_triple(frame_phi(phi, _frame_order(eps)))
        q = pairing_matrix(triple)
        eig = np.linalg.eigvalsh(q)
        rows.append({
            "element": eps,
            "dualities": [duality(w) for w in triple],
            "pairing_eigenvalues": [round(float(x), 12) for x in eig],
            "definite": bool(np.all(eig > 0) or np.all(eig < 0)),
        })
    return {"planes": rows, "holds": bool(rows) and all(r["definite"] for r in rows),
            "measured": True,
            "counts": "planes: flipped 4-planes of the non-identity elements of Gamma"}


# ------------------------------------------------------------------ H4b, H4c

def eh_coords():
    """(r, theta, phi, psi, y1, y2, y3, a): Eguchi-Hanson x T^3 chart, plus a."""
    import sympy as sp

    from metaphysica.simulations.PM.geometry.eguchi_hanson import symbols

    r, theta, ph, psi, a = symbols()
    ys = sp.symbols("y1 y2 y3", real=True)
    return (r, theta, ph, psi) + tuple(ys) + (a,)


def eh_frame():
    """Orthonormal coframe e^0..e^6 of EH x T^3 as 1-forms in the 7D chart.

    e^0 = dr/f, e^1 = (r/2) sigma_1, e^2 = (r/2) sigma_2, e^3 = (r f/2) sigma_3,
    e^{4,5,6} = dy, with f^2 = 1 - (a/r)^4 -- the frame of `eguchi_hanson`.
    """
    import sympy as sp

    from metaphysica.simulations.PM.geometry.exterior_algebra import Form

    r, th, ph, psi, _y1, _y2, _y3, a = eh_coords()
    f = sp.sqrt(1 - a ** 4 / r ** 4)
    half = r / 2
    comps = [
        {(0,): 1 / f},
        {(1,): half * sp.cos(psi), (2,): half * sp.sin(psi) * sp.sin(th)},
        {(1,): -half * sp.sin(psi), (2,): half * sp.cos(psi) * sp.sin(th)},
        {(3,): half * f, (2,): half * f * sp.cos(th)},
    ] + [{(4 + m,): sp.Integer(1)} for m in range(3)]
    return [Form(dim=7, degree=1, components=dict(sorted(c.items()))) for c in comps]


def frame_form(frame, coeffs: Dict[Tuple[int, ...], float]):
    """sum_I c_I e^I for constant c, as a coordinate Form (exact rationals)."""
    import sympy as sp

    from metaphysica.simulations.PM.geometry.exterior_algebra import Form, wedge

    degree = len(next(iter(coeffs)))
    total: Dict[Tuple[int, ...], Any] = {}
    for idx, c in coeffs.items():
        if c == 0:
            continue
        term = frame[idx[0]]
        for k in idx[1:]:
            term = wedge(term, frame[k])
        for key, val in term.components.items():
            total[key] = total.get(key, 0) + sp.nsimplify(c) * val
    return Form(dim=7, degree=degree,
                components={k: v for k, v in total.items() if v != 0})


def is_closed(form) -> bool:
    """d(form) = 0 exactly: symbolic exterior_d, each component simplified."""
    import sympy as sp

    from metaphysica.simulations.PM.geometry.exterior_algebra import exterior_d

    coords = eh_coords()[:7]
    d = exterior_d(form, coords)
    return all(sp.simplify(v) == 0 for v in d.components.values())


def eh_triple(orientation: str) -> List[Dict[Tuple[int, int], int]]:
    """Frame triple omega_i = e^0i + s e^jk on the EH 4-plane, s = -1 for ASD."""
    s = {"ASD": -1, "SD": 1}[orientation]
    return [{p: 1, q: s * sign} for (p, q), sign in zip(_PAIRS, _STAR_SIGN)]


def eh_triple_closure() -> Dict[str, Any]:
    """H4b: which orientation of the frame triple is closed on Eguchi-Hanson."""
    frame = eh_frame()
    closed = {o: [is_closed(frame_form(frame, w)) for w in eh_triple(o)]
              for o in ("ASD", "SD")}
    good = [o for o, c in closed.items() if all(c)]
    return {"closed_by_orientation": closed,
            "hyperkahler_orientation": good[0] if len(good) == 1 else None,
            "holds": len(good) == 1, "measured": True,
            "counts": "three frame 2-forms per orientation of e^0123"}


def hodge_star_frame(coeffs: Dict[Tuple[int, ...], float], n: int = 7):
    """* of a constant-coefficient frame form, orthonormal frame, vol = e^0..n-1."""
    out: Dict[Tuple[int, ...], float] = {}
    for idx, c in coeffs.items():
        rest = tuple(i for i in range(n) if i not in idx)
        out[rest] = out.get(rest, 0) + _parity(idx + rest) * c
    return out


def _frame_coeffs(phi_f: np.ndarray) -> Dict[Tuple[int, int, int], float]:
    return {t: float(phi_f[t]) for t in itertools.combinations(range(7), 3)
            if abs(phi_f[t]) > 1e-12}


def local_model_torsion(phi: np.ndarray, eps: Sequence[int],
                        orientation: Optional[str] = None) -> Dict[str, Any]:
    """H4c: phi0 transported onto EH x T^3 along one singular plane; d phi, d*phi.

    The 4-plane is ordered so its flat triple has the hyperkahler orientation
    of Eguchi-Hanson (H4b); `orientation` overrides that, for the control.
    """
    want = orientation or eh_triple_closure()["hyperkahler_orientation"]
    order = _frame_order(eps)
    if want and duality(flat_triple(frame_phi(phi, order))[0]) != want:
        order = _frame_order(eps, swap=True)
    coeffs = _frame_coeffs(frame_phi(phi, order))
    frame = eh_frame()
    d_phi = is_closed(frame_form(frame, coeffs))
    d_star = is_closed(frame_form(frame, hodge_star_frame(coeffs)))
    return {"element": tuple(eps), "frame_order": order,
            "d_phi_zero": d_phi, "d_star_phi_zero": d_star,
            "holds": d_phi and d_star, "measured": True}


# ------------------------------------------------------------------ H7

def clifford_from_phi(phi: np.ndarray) -> List[np.ndarray]:
    """Left multiplication by the imaginary units of the algebra phi defines.

    On R^8 = R.1 + R^7: L_i(1) = e_i, L_i(e_j) = -delta_ij 1 + phi_ijk e_k.
    These generate Cl(7) on the spinors exactly when phi is the compact form
    (the algebra is then the octonions); 1 is the G2-invariant spinor.
    """
    mats = []
    for i in range(7):
        m = np.zeros((8, 8))
        m[1 + i, 0] = 1.0
        for j in range(7):
            m[0, 1 + j] -= 1.0 if i == j else 0.0
            m[1:, 1 + j] += phi[i, j, :]
        mats.append(m)
    return mats


def clifford_relations_hold(mats: Sequence[np.ndarray]) -> bool:
    """L_i L_j + L_j L_i = -2 delta_ij, exactly (integer entries)."""
    eye = np.eye(8)
    return all(np.allclose(a @ b + b @ a, -2.0 * eye * (i == j))
               for i, a in enumerate(mats) for j, b in enumerate(mats))


def spin_lift(mats: Sequence[np.ndarray], eps: Sequence[int]) -> np.ndarray:
    """+-prod of L_a over the flipped coordinates: a lift of eps to Spin(7)."""
    out = np.eye(8)
    for a, e in enumerate(eps):
        if e == -1:
            out = out @ mats[a]
    return out


def _generators(elements: Sequence[Tuple[int, ...]]) -> List[Tuple[int, ...]]:
    """A minimal generating set of an elementary abelian 2-group of sign flips."""
    gens: List[Tuple[int, ...]] = []
    span = {tuple([1] * 7)}
    for g in elements:
        if g not in span:
            gens.append(g)
            span |= {tuple(x * y for x, y in zip(g, s)) for s in span}
    return gens


def invariant_spinor_count(phi: np.ndarray,
                           elements: Optional[Sequence[Tuple[int, ...]]] = None
                           ) -> Dict[str, Any]:
    """H7: constant spinors on T^7 fixed by a lift of Gamma, for every lift.

    A lift is a choice of sign per generator; it is a homomorphism when the
    lifted generators square to 1 and commute. The count is the rank of the
    averaging projector. A generator whose lift squares to -1 fixes no spinor.
    """
    mats = clifford_from_phi(phi)
    if not clifford_relations_hold(mats):
        return {"holds": False, "measured": True, "count": None,
                "reason": "phi does not define Cl(7): not the compact form"}
    gens = _generators(list(elements if elements is not None
                            else gamma_elements(phi)))
    lifts = [spin_lift(mats, g) for g in gens]
    if any(not np.allclose(m @ m, np.eye(8)) for m in lifts):
        return {"holds": False, "measured": True, "count": 0,
                "reason": "a generator's lift squares to -1"}
    counts = []
    for signs in itertools.product((1, -1), repeat=len(gens)):
        proj = np.zeros((8, 8))
        for pick in itertools.product((0, 1), repeat=len(gens)):
            g = np.eye(8)
            for p, s, m in zip(pick, signs, lifts):
                g = g @ (s * m if p else np.eye(8))
            proj += g
        counts.append(int(round(np.trace(proj) / 2 ** len(gens))))
    commute = all(np.allclose(a @ b, b @ a) for a in lifts for b in lifts)
    return {"holds": commute and set(counts) == {1}, "measured": True,
            "count": counts[0], "counts_over_lifts": counts,
            "lifts_commute": commute, "n_generators": len(gens)}


# ------------------------------------------------------------------ the report

def _resolution():
    from metaphysica.simulations.PM.geometry.joyce_resolution import (
        resolution_report,
    )

    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path,
        seed_values,
    )

    report = resolution_report()
    path = resolve_path()
    b3, b2 = seed_values(path)
    # The resolution is of T^7/(Z2)^3. A seed declaring other Betti numbers is
    # not this construction, so its hypotheses are unmeasured, not borrowed.
    if (report["b2"], report["b3"]) != (b2, b3):
        raise ValueError("seed %s declares (b2, b3) = (%d, %d); the Joyce resolution "
                         "reaches (%d, %d)" % (path, b2, b3, report["b2"], report["b3"]))
    return report


def _h1(phi, _ctx) -> Dict[str, Any]:
    g = gamma_elements(phi)
    return {"holds": len(g) == 8, "order": len(g),
            "source": "joyce_orbifold.diagonal_stabiliser"}


def _h2(phi, _ctx) -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )

    rf = G2DifferentialGeometry(phi=phi).real_form_report()
    return {"holds": bool(rf["is_riemannian"] and rf["supports_g2_holonomy"]),
            "real_form": rf["real_form"],
            "hitchin_signature": tuple(rf["hitchin_signature"]),
            "source": "g2_differential.real_form_report"}


def _h3(_phi, ctx) -> Dict[str, Any]:
    res = ctx["resolution"]
    half = ctx["gamma_order"] // 2
    a1 = all(s == half for s in res["orbit_sizes"])
    return {"holds": bool(res["every_component_is_flat_T3"] and a1
                          and res["n_components"] > 0),
            "n_components": res["n_components"], "orbit_sizes": res["orbit_sizes"],
            "a1": a1, "source": "joyce_resolution.resolution_report"}


def _h4c(phi, _ctx) -> Dict[str, Any]:
    rows = [local_model_torsion(phi, eps) for eps in gamma_elements(phi)
            if any(e == -1 for e in eps)]
    return {"holds": bool(rows) and all(r["holds"] for r in rows),
            "planes": rows, "source": "g2_closure.local_model_torsion"}


def _h5(_phi, _ctx) -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.eguchi_hanson import (
        ale_decay_report,
        ricci_is_exactly_zero,
    )

    ale, ricci = ale_decay_report(), ricci_is_exactly_zero()
    return {"holds": bool(ale["matches_ale"] and ricci),
            "fitted_exponent": ale["fitted_exponent"],
            "eh_ricci_exactly_zero": ricci,
            "source": "eguchi_hanson.ale_decay_report, ricci_is_exactly_zero"}


def _h6(_phi, ctx) -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.fundamental_group import (
        pi1_finiteness,
    )

    pi = pi1_finiteness()
    b1 = ctx["resolution"]["betti"][1]
    return {"holds": bool(pi["pi1_finite"] and b1 == 0), "pi1_finite": pi["pi1_finite"],
            "b1": b1, "source": "fundamental_group.pi1_finiteness"}


def _h8(_phi, ctx) -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.glued_orbit_scan import scan

    recs = [r for r in scan(t_values=(0.0, 0.1), convention=ctx["convention"])
            if not r["is_degenerate"]]
    orbits = sorted({r["orbit"] for r in recs})
    return {"holds": orbits == ["COMPACT"], "orbits": orbits, "n_points": len(recs),
            "t_values": (0.0, 0.1), "source": "glued_orbit_scan.scan"}


HYPOTHESES = (
    ("H1", "Gamma = (Z2)^3 preserves phi0", _h1),
    ("H2", "phi0 is positive: Hitchin metric (7,0)", _h2),
    ("H3", "every singular component is T^3 x C^2/Z2 (A1)", _h3),
    ("H4a", "phi0's triple on each flipped 4-plane is hyperkahler",
     lambda phi, _c: dict(triple_definiteness(phi), source="g2_closure")),
    ("H4b", "the Eguchi-Hanson triple is closed in exactly one orientation",
     lambda _p, _c: dict(eh_triple_closure(), source="g2_closure")),
    ("H4c", "local model EH x T^3: d phi = d*phi = 0", _h4c),
    ("H5", "Eguchi-Hanson is Ricci-flat and decays to flat as r^-4", _h5),
    ("H6", "pi_1 finite and b_1 = 0", _h6),
    ("H7", "exactly one Gamma-invariant spinor",
     lambda phi, _c: dict(invariant_spinor_count(phi), source="g2_closure")),
    ("H8", "the glued form is compact-orbit at small t", _h8),
)


CONCLUSIONS = (
    ("existence", "a torsion-free G2 structure exists on the resolution",
     "Joyce 2000, Thm 11.6.1; Joyce 1996 I"),
    ("ricci_flat", "its metric is Ricci-flat", "Bonan: torsion-free implies Ricci-flat"),
    ("holonomy", "its holonomy is exactly G2",
     "Joyce 1996 II, Prop 1.1.1: Hol = G2 iff pi_1 finite"),
)


def _resolved(name: str, fallback: str) -> str:
    try:
        from metaphysica.simulations.core.variants import resolve

        return resolve(name)
    except Exception:                  # fork not declared / import cycle
        return fallback


def require_buildable_construction() -> str:
    """The active g2_construction, or a ``ValueError`` refusal (D-023).

    Only the Joyce orbifold is built here. A twisted connected sum (retired reading) needs a cited
    pair of building blocks, and none is in the engine; Kovalev's exhibited range
    71 <= b3 <= 155 (arXiv:1810.12659) also excludes the adopted b3 = 43.
    """
    construction = _resolved("g2_construction", "joyce_orbifold")
    if construction != "joyce_orbifold":
        raise ValueError(
            "g2_construction %r is refused: no cited building blocks are in the "
            "engine, so nothing on this path is a construction; exhibited TCS "
            "examples have 71 <= b3 <= 155 (arXiv:1810.12659)" % construction)
    return construction


_CACHE: Dict[Tuple[str, str], Dict[str, Any]] = {}


def closure_report(convention: Optional[str] = None) -> Dict[str, Any]:
    """H1-H8 on the active path, and the verdict (D-023). Cached per path."""
    convention = convention or _resolved("g2_form_convention", "octonion_derived")
    key = (convention, _resolved("b3_seed", "?"))
    if key not in _CACHE:
        _CACHE[key] = _build_report(convention, key[1])
    return _CACHE[key]


def _build_report(convention: str, seed: str) -> Dict[str, Any]:
    phi = phi_for(convention)
    ctx: Dict[str, Any] = {"convention": convention,
                           "gamma_order": len(gamma_elements(phi))}
    try:
        ctx["resolution"] = _resolution()
    except Exception as exc:           # a seed the construction does not reach
        ctx["resolution_error"] = "%s: %s" % (type(exc).__name__, exc)
    rows = []
    for hid, text, fn in HYPOTHESES:
        try:
            row = fn(phi, ctx)
        except KeyError:
            row = {"holds": False, "measured": False,
                   "reason": ctx.get("resolution_error", "resolution unavailable")}
        rows.append(dict(row, id=hid, hypothesis=text,
                         measured=row.get("measured", True)))
    failing = [r["id"] for r in rows if not (r["measured"] and r["holds"])]
    return {
        "convention": convention, "seed": seed, "hypotheses": rows,
        "verdict": "CLOSED_BY_THEOREM" if not failing else "OPEN",
        "first_failure": failing[0] if failing else None,
        "conclusions": [{"id": c, "claim": t, "by": b, "established": not failing}
                        for c, t, b in CONCLUSIONS],
        "what_is_not_claimed": "an explicit metric: none is known for any compact G2 manifold",
        "decision": "D-023",
    }
