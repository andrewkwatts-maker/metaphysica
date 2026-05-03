"""metaphysica.datasheets.constant — datasheets for named physics constants.

Resolves a name through the FormulasRegistry / parameters.json data and
returns a JSON-shaped dict::

    {
      "name":           "M_PLANCK",
      "value":          1.220910e19,
      "units":          "GeV",
      "uncertainty":    null | float,
      "source":         "PDG2024" | "GEOMETRIC" | "DERIVED",
      "status":         "MEASURED" | "GEOMETRIC" | "DERIVED",
      "eml_expression": "EML: ..." | null,
      "kind":           "physics",
      "_provenance":    {...},
    }

Get('m_planck'), Get('Planck mass'), Get('M_PLANCK') all map to the
same canonical entry via :data:`_ALIASES`.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any, Dict, List, Optional


# ── Curated alias table ──────────────────────────────────────────────────────
# Maps user-facing names to the canonical key in parameters.json.
# Keep this small and curated; less-common keys can be looked up directly
# without an alias.
_ALIASES: Dict[str, str] = {
    # Planck mass
    "m_planck":      "constants.M_PLANCK",
    "planck mass":   "constants.M_PLANCK",
    "M_PLANCK":      "constants.M_PLANCK",
    "planck_mass":   "constants.M_PLANCK",
    # Fine-structure constant
    "alpha_em":      "constants.alpha_em",
    "alpha":         "constants.alpha_em",
    "fine_structure_constant": "constants.alpha_em",
    # Speed of light, Planck's constant, etc. (Look these up by their flat keys)
    "hbar":          "constants.HBAR",
    "h_bar":         "constants.HBAR",
    "G":             "constants.G_NEWTON",
    "G_newton":      "constants.G_NEWTON",
    "k_B":           "constants.k_B",
    "boltzmann":     "constants.k_B",
    # Standard-model gauge constants
    "alpha_s_MZ":    "pdg.alpha_s_MZ",
    "alpha_s":       "pdg.alpha_s_MZ",
    "sin2_theta_W":  "pdg.sin2_theta_W",
    "weinberg_angle": "pdg.sin2_theta_W",
    "M_Z":           "pdg.m_Z",
    "M_W":           "pdg.m_W",
    "m_Z":           "pdg.m_Z",
    "m_W":           "pdg.m_W",
    # Higgs
    "m_higgs":       "pdg.m_higgs",
    "higgs_mass":    "pdg.m_higgs",
    "v_higgs":       "geometry.higgs_vev",
    "vev":           "geometry.higgs_vev",
    "higgs_vev":     "geometry.higgs_vev",
    # Electroweak / leptons
    "m_electron":    "pdg.m_electron",
    "m_muon":        "pdg.m_muon",
    "m_tau":         "pdg.m_tau",
    "m_proton":      "constants.m_proton",
    # Cosmology / Dark energy
    "w0":            "cosmology.w0_derived",
    "w_0":           "cosmology.w0_derived",
    "dark_energy_w0": "cosmology.w0_derived",
    "H0":            "cosmology.H0_local",
    "hubble":        "cosmology.H0_local",
    # GUT scale
    "M_GUT":         "gauge.M_GUT",
    "alpha_GUT":     "gauge.ALPHA_GUT_INV",
    "alpha_GUT_inv": "gauge.ALPHA_GUT_INV",
    # Topology
    "b3":            "topology.elder_kads",
    "elder_kads":    "topology.elder_kads",
    "k_gimel":       "topology.k_gimel",
    "chi_eff":       "topology.chi_eff",
    "n_gen":         "topology.n_gen",
    # Neutrino mass-squared splittings
    "delta_m21_sq":  "neutrino.dm2_21",
    "delta_m32_sq":  "neutrino.dm2_32",
    # Quark masses (lookup-only; quarks themselves use Get('Up') etc.)
    "m_up":          "pdg.m_up",
    "m_down":        "pdg.m_down",
    "m_strange":     "pdg.m_strange",
    "m_charm":       "pdg.m_charm",
    "m_bottom":      "pdg.m_bottom",
    "m_top":         "pdg.m_top",
    # CKM
    "V_us":          "pdg.V_us",
    "V_cb":          "pdg.V_cb",
    "V_ub":          "pdg.V_ub",
    "J_ckm":         "pdg.J_ckm",
}


# Display names corresponding to the curated aliases.
KNOWN_CONSTANTS: List[str] = sorted({
    "m_planck", "alpha_em", "hbar", "G", "k_B",
    "alpha_s_MZ", "sin2_theta_W",
    "M_Z", "M_W", "m_higgs", "v_higgs",
    "m_electron", "m_muon", "m_tau", "m_proton",
    "w0", "H0",
    "M_GUT", "alpha_GUT_inv",
    "b3", "k_gimel", "chi_eff", "n_gen",
    "delta_m21_sq", "delta_m32_sq",
    "m_up", "m_down", "m_strange", "m_charm", "m_bottom", "m_top",
    "V_us", "V_cb", "V_ub", "J_ckm",
})


def canonical_constant_name(name: str) -> str:
    """Resolve any alias to the canonical parameters.json key."""
    if name in _ALIASES:
        return _ALIASES[name]
    if name.lower() in _ALIASES:
        return _ALIASES[name.lower()]
    # Fall through: treat the name as already-canonical.
    return name


def _load_bundled_snapshot(display_name: str) -> Dict[str, Any] | None:
    """Return a pre-generated bundled constant JSON, keyed by display name."""
    try:
        from importlib.resources import files
        slug = display_name.replace("/", "_").replace(" ", "_")
        res = files("metaphysica.data.constants") / f"{slug}.json"
        if not res.is_file():
            return None
        import json
        return json.loads(res.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_constant_datasheet(name: str, *, prefer_bundled: bool = True) -> Dict[str, Any]:
    """Return a JSON datasheet for the named physics constant.

    Lookup chain (first match wins):
      0. If *prefer_bundled* is True, return the pre-generated snapshot
         shipped in the wheel (``metaphysica/data/constants/<name>.json``).
      1. The curated alias table maps user-friendly names to canonical
         flat keys (e.g. 'm_planck' → 'constants.M_PLANCK').
      2. The metaphysica simulation registry (PMRegistry) is queried
         for the canonical key.
      3. Falls back to reading the bundled parameters.json snapshot if
         the registry isn't initialised.

    Raises :class:`KeyError` if the name can't be resolved anywhere.
    """
    if prefer_bundled:
        snap = _load_bundled_snapshot(name)
        if snap is not None:
            return snap
    canon = canonical_constant_name(name)
    record = _resolve(canon)
    if record is None:
        raise KeyError(
            f"unknown physics constant: {name!r} (canonical={canon!r}). "
            f"Try one of {KNOWN_CONSTANTS}"
        )
    return _shape_datasheet(name, canon, record)


# ── Resolution chain ─────────────────────────────────────────────────────────

def _resolve(canon: str) -> Optional[Dict[str, Any]]:
    """Try registry first, then bundled parameters.json snapshot."""
    rec = _from_registry(canon)
    if rec is not None:
        return rec
    return _from_snapshot(canon)


def _from_registry(canon: str) -> Optional[Dict[str, Any]]:
    """Lookup via the live PMRegistry singleton if it's been initialised."""
    try:
        from metaphysica.simulations.base.registry import PMRegistry
        reg = PMRegistry.get_instance()
        if not reg.has(canon):
            return None
        entry = reg.get(canon)
        # PMRegistry returns a RegistryEntry (or compat dict). Normalise.
        return _normalise_record(entry)
    except Exception:
        return None


def _from_snapshot(canon: str) -> Optional[Dict[str, Any]]:
    """Lookup via parameters.json — bundled wheel copy first, then cwd."""
    import json
    data = _load_parameters_json()
    if data is None:
        return None
    inner = data.get("parameters", data)
    if canon not in inner:
        return None
    return _normalise_record(inner[canon])


def _load_parameters_json() -> Optional[Dict[str, Any]]:
    """Read parameters.json from the wheel data dir, or AutoGenerated/ in cwd."""
    import json
    # 1. Bundled copy shipped inside the wheel — always works after `pip install`.
    try:
        from importlib.resources import files
        res = files("metaphysica.data") / "parameters.json"
        if res.is_file():
            return json.loads(res.read_text(encoding="utf-8"))
    except Exception:
        pass
    # 2. Build-time copy under <out_dir>/AutoGenerated/ (during a live build).
    try:
        from metaphysica.generators._common import out_dir
        snapshot = out_dir() / "AutoGenerated" / "parameters.json"
        if snapshot.exists():
            return json.loads(snapshot.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def _normalise_record(record: Any) -> Dict[str, Any]:
    """Coerce any registry / JSON-snapshot record into a uniform dict."""
    if hasattr(record, "to_dict"):
        record = record.to_dict()
    if isinstance(record, dict):
        return record
    # Bare scalar — wrap it
    return {"value": record}


def _shape_datasheet(display_name: str, canon: str, record: Dict[str, Any]) -> Dict[str, Any]:
    """Compose the final datasheet dict from the resolved record."""
    value = record.get("value")
    out: Dict[str, Any] = {
        "name":           display_name,
        "canonical_path": canon,
        "value":          value,
        "units":          record.get("units"),
        "uncertainty":    record.get("uncertainty"),
        "source":         record.get("source"),
        "status":         record.get("status"),
        "description":    record.get("description"),
        "eml_expression": record.get("eml_description") or record.get("eml_expression"),
        "kind":           "physics",
        "_provenance": {
            "metaphysica_version": _metaphysica_version(),
            "generated_at":        _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "sources":             [record.get("source")] if record.get("source") else [],
        },
    }
    return out


def _metaphysica_version() -> str:
    try:
        from metaphysica import __version__
        return __version__
    except Exception:
        return "0.1.0"
