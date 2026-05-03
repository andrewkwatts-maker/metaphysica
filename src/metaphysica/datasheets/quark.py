"""metaphysica.datasheets.quark — generate JSON datasheets for quarks.

Each datasheet matches the schema used by periodica
(``periodica/data/active/quarks/*.json``) plus a ``pm_prediction``
super-block carrying the metaphysica-derived prediction (Yukawa
φ-scaling), the EML expression, and the CKM couplings.

The 12 entries Get() exposes:

  Up, Down, Strange, Charm, Bottom, Top
  AntiUp, AntiDown, AntiStrange, AntiCharm, AntiBottom, AntiTop

PM theory predicts exactly 3 generations (n_gen = 3 from
fermion_generations.py), so no 4th-gen / mirror / sterile quarks.
"""
from __future__ import annotations

import datetime as _dt
import math
from typing import Any, Dict, List

# ── Quantum-number table (PDG 2024 — not derived from PM theory) ────────────
# These values aren't predictions; they're the conventional definitions
# (electric charge from gauge invariance, baryon number from quark counting,
# isospin from SU(2) doublet structure, etc.). PM derives masses + mixing,
# not these.

_QUARK_BASE: Dict[str, Dict[str, Any]] = {
    "up": {
        "Name": "Up Quark", "Symbol": "u",
        "generation": 1,
        "Charge_e": 2/3,
        "BaryonNumber_B": 1/3,
        "LeptonNumber_L": 0,
        "Spin_hbar": 0.5,
        "Isospin_I": 0.5, "Isospin_I3": 0.5,
        "ConstituentMass_MeV": 336.0,
        "Stability": "Stable",
        "HalfLife_s": None,
        "DecayProducts": [],
        "Antiparticle": {"Name": "Antiup Quark", "Symbol": "u̅"},
    },
    "down": {
        "Name": "Down Quark", "Symbol": "d",
        "generation": 1,
        "Charge_e": -1/3,
        "BaryonNumber_B": 1/3,
        "LeptonNumber_L": 0,
        "Spin_hbar": 0.5,
        "Isospin_I": 0.5, "Isospin_I3": -0.5,
        "ConstituentMass_MeV": 340.0,
        "Stability": "Stable",
        "HalfLife_s": None,
        "DecayProducts": [],
        "Antiparticle": {"Name": "Antidown Quark", "Symbol": "d̅"},
    },
    "charm": {
        "Name": "Charm Quark", "Symbol": "c",
        "generation": 2,
        "Charge_e": 2/3,
        "BaryonNumber_B": 1/3,
        "LeptonNumber_L": 0,
        "Spin_hbar": 0.5,
        "Isospin_I": 0.0, "Isospin_I3": 0.0,
        "ConstituentMass_MeV": 1500.0,
        "Stability": "Unstable",
        "HalfLife_s": 1.0e-12,
        "DecayProducts": ["Strange Quark", "W Boson"],
        "Antiparticle": {"Name": "Anticharm Quark", "Symbol": "c̅"},
    },
    "strange": {
        "Name": "Strange Quark", "Symbol": "s",
        "generation": 2,
        "Charge_e": -1/3,
        "BaryonNumber_B": 1/3,
        "LeptonNumber_L": 0,
        "Spin_hbar": 0.5,
        "Isospin_I": 0.0, "Isospin_I3": 0.0,
        "ConstituentMass_MeV": 480.0,
        "Stability": "Unstable",
        "HalfLife_s": 1.2e-8,
        "DecayProducts": ["Up Quark", "W Boson"],
        "Antiparticle": {"Name": "Antistrange Quark", "Symbol": "s̅"},
    },
    "top": {
        "Name": "Top Quark", "Symbol": "t",
        "generation": 3,
        "Charge_e": 2/3,
        "BaryonNumber_B": 1/3,
        "LeptonNumber_L": 0,
        "Spin_hbar": 0.5,
        "Isospin_I": 0.0, "Isospin_I3": 0.0,
        "ConstituentMass_MeV": 173000.0,
        "Stability": "Unstable",
        "HalfLife_s": 5.0e-25,
        "DecayProducts": ["Bottom Quark", "W Boson"],
        "Antiparticle": {"Name": "Antitop Quark", "Symbol": "t̅"},
    },
    "bottom": {
        "Name": "Bottom Quark", "Symbol": "b",
        "generation": 3,
        "Charge_e": -1/3,
        "BaryonNumber_B": 1/3,
        "LeptonNumber_L": 0,
        "Spin_hbar": 0.5,
        "Isospin_I": 0.0, "Isospin_I3": 0.0,
        "ConstituentMass_MeV": 4200.0,
        "Stability": "Unstable",
        "HalfLife_s": 1.5e-12,
        "DecayProducts": ["Charm Quark", "W Boson"],
        "Antiparticle": {"Name": "Antibottom Quark", "Symbol": "b̅"},
    },
}


# Yukawa φ-scaling: best-fit N values from yukawa_textures.py
# m_predicted(N) = v_higgs / phi^N    with v_higgs = 246.22 GeV
_PHI = (1 + math.sqrt(5)) / 2
_VEV_GEV = 246.22
_YUKAWA_N = {
    "up":      12,
    "down":    11,
    "strange":  8,
    "charm":    5,
    "bottom":   4,
    "top":      0,
}

# Per-quark CKM coupling sets (rows of the CKM matrix). Values from PDG 2024
# (the geometric derivation in metaphysica reproduces these; we cite both).
_CKM_COUPLINGS = {
    # up-type: V_uX is the row
    "up":      {"V_ud": 0.97435, "V_us": 0.22500, "V_ub": 0.00382},
    "charm":   {"V_cd": 0.22486, "V_cs": 0.97349, "V_cb": 0.04100},
    "top":     {"V_td": 0.00854, "V_ts": 0.04050, "V_tb": 0.999105},
    # down-type: same matrix transposed (column view) for completeness
    "down":    {"V_ud": 0.97435, "V_cd": 0.22486, "V_td": 0.00854},
    "strange": {"V_us": 0.22500, "V_cs": 0.97349, "V_ts": 0.04050},
    "bottom":  {"V_ub": 0.00382, "V_cb": 0.04100, "V_tb": 0.999105},
}

# Canonical name aliases — Get('Up'), Get('u'), Get('UpQuark'), Get('up quark')
# all map to the same key. Antiquarks: 'AntiUp', 'anti-up', 'Anti Up Quark'.
_ALIASES: Dict[str, str] = {}
for canon in _QUARK_BASE:
    base = _QUARK_BASE[canon]
    sym  = base["Symbol"]
    name = base["Name"]
    for alias in (
        canon, canon.lower(), canon.upper(), canon.capitalize(),
        sym, sym.lower(), sym.upper(),
        name, name.lower(),
        name.replace(" ", ""),                  # "UpQuark"
        name.replace(" Quark", "").lower(),     # "up"
    ):
        _ALIASES[alias.lower()] = canon
    # Antiquark aliases
    anti_canon = "anti" + canon
    anti_sym = sym + "̅"
    anti_name = base["Antiparticle"]["Name"]   # "Antiup Quark"
    for alias in (
        anti_canon, anti_canon.lower(), anti_canon.upper(),
        f"anti-{canon}", f"anti{canon}", f"Anti{canon.capitalize()}",
        anti_sym, anti_name, anti_name.lower(), anti_name.replace(" ", ""),
    ):
        _ALIASES[alias.lower()] = anti_canon


KNOWN_QUARKS: List[str] = (
    list(_QUARK_BASE.keys()) +
    ["anti" + name for name in _QUARK_BASE]
)


def canonical_quark_name(name: str) -> str:
    """Resolve any alias to the canonical key. Raises KeyError if unknown."""
    key = name.strip().lower()
    if key in _ALIASES:
        return _ALIASES[key]
    raise KeyError(f"unknown quark: {name!r}. Try one of {KNOWN_QUARKS}")


def _gev_to_kg(m_gev: float) -> float:
    """Convert a mass in GeV/c² to kg.  1 GeV/c² = 1.78266192e-27 kg."""
    return m_gev * 1.78266192e-27


def _gev_to_amu(m_gev: float) -> float:
    """Convert GeV/c² to atomic mass units. 1 amu = 0.93149410242 GeV/c²."""
    return m_gev / 0.93149410242


def _pdg_mass_gev(canonical: str) -> float:
    """Lookup PDG mass for a quark by canonical key."""
    table = {
        "up":     2.16e-3,
        "down":   4.67e-3,
        "strange": 93.4e-3,
        "charm":  1.27,
        "bottom": 4.18,
        "top":    172.69,
    }
    return table[canonical]


def _antiparticle_of(quark_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Flip every additive quantum number to produce an antiparticle datasheet."""
    out = dict(quark_dict)   # shallow copy
    out["Name"] = quark_dict["Antiparticle"]["Name"]
    out["Symbol"] = quark_dict["Antiparticle"]["Symbol"]
    out["Charge_e"] = -quark_dict["Charge_e"]
    out["BaryonNumber_B"] = -quark_dict["BaryonNumber_B"]
    out["Isospin_I3"] = -quark_dict["Isospin_I3"]
    out["Antiparticle"] = {"Name": quark_dict["Name"], "Symbol": quark_dict["Symbol"]}
    # Decay products: replace each "X Quark" with "Anti-X Quark" where possible
    out["DecayProducts"] = [
        ("Anti" + p) if p.endswith("Quark") and not p.startswith("Anti") else p
        for p in quark_dict["DecayProducts"]
    ]
    return out


def _load_bundled_snapshot(canon: str) -> Dict[str, Any] | None:
    """Return the pre-generated bundled JSON for *canon*, if it exists."""
    try:
        from importlib.resources import files
        res = files("metaphysica.data.quarks") / f"{canon}.json"
        if not res.is_file():
            return None
        import json
        return json.loads(res.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_quark_datasheet(name: str, *, prefer_bundled: bool = True) -> Dict[str, Any]:
    """Return a JSON-shaped datasheet for the named quark (or antiquark).

    Schema = periodica's ``data/active/quarks/*.json`` field set + a
    ``pm_prediction`` super-block carrying the metaphysica derivation.

    If *prefer_bundled* is True (the default), a pre-generated snapshot
    from the wheel is returned without re-deriving anything; falls back
    to live derivation only if the snapshot is missing.
    """
    canon = canonical_quark_name(name)
    if prefer_bundled:
        snap = _load_bundled_snapshot(canon)
        if snap is not None:
            return snap
    is_anti = canon.startswith("anti")
    base_canon = canon[4:] if is_anti else canon
    base = dict(_QUARK_BASE[base_canon])

    # PDG side
    pdg_mass_gev = _pdg_mass_gev(base_canon)
    pdg_mass_mev = pdg_mass_gev * 1000.0
    base["Mass_MeVc2"] = pdg_mass_mev
    base["Mass_kg"] = _gev_to_kg(pdg_mass_gev)
    base["Mass_amu"] = _gev_to_amu(pdg_mass_gev)
    base["MagneticDipoleMoment_J_T"] = None
    base["Parity_P"] = None
    base["Type"] = "Subatomic Particle"
    base["Classification"] = ["Fermion", "Quark", "Fundamental Particle"]
    base["Composition"] = []
    base["InteractionForces"] = ["Strong", "Electromagnetic", "Weak", "Gravitational"]

    # PM prediction side — Yukawa φ-scaling
    n_phi = _YUKAWA_N[base_canon]
    predicted_gev = _VEV_GEV / (_PHI ** n_phi)
    pct_err = 100.0 * abs(predicted_gev - pdg_mass_gev) / pdg_mass_gev
    verdict = (
        "EXCELLENT" if pct_err < 5 else
        "GOOD"      if pct_err < 15 else
        "FAIR"      if pct_err < 50 else
        "POOR"
    )

    eml_expression = (
        f"EML: ops.div(eml_scalar({_VEV_GEV}), "
        f"ops.pow(eml_scalar({_PHI:.6f}), eml_scalar({n_phi})))"
    )

    base["pm_prediction"] = {
        "phi_scaling_N":      n_phi,
        "predicted_mass_GeV": predicted_gev,
        "pdg_mass_GeV":       pdg_mass_gev,
        "percent_error":      pct_err,
        "verdict":            verdict,
        "eml_expression":     eml_expression,
        "ckm_couplings":      _CKM_COUPLINGS.get(base_canon, {}),
        "derivation_notes": (
            "Mass from G2 phi-scaling: m_n = v_higgs / phi^N, where v=246.22 GeV "
            "is the electroweak VEV and phi=(1+√5)/2 is the golden ratio. "
            f"For {base_canon}, N={n_phi}. CKM mixing from Froggatt-Nielsen + "
            "Wolfenstein parameterisation; geometric Jarlskog J ~ sin(δ_CP) * "
            "λ_12 * λ_23 * λ_13² with λ_ij = phi^(-Δ_N/2)."
        ),
    }
    base["_provenance"] = {
        "metaphysica_version": _metaphysica_version(),
        "generated_at":        _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "sources":             ["PDG2024", "yukawa_textures_v19", "ckm_matrix_v16"],
    }

    # Drop the helper-only "generation" field; periodica doesn't have it.
    base.pop("generation", None)

    if is_anti:
        base = _antiparticle_of(base)
        # Re-attach pm_prediction (antiparticle has same mass/scaling)
        # — _antiparticle_of preserves it because dict() copies it.
    return base


def _metaphysica_version() -> str:
    try:
        from metaphysica import __version__
        return __version__
    except Exception:
        return "0.1.0"
