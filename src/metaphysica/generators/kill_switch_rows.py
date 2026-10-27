"""Registry row behind each numeric kill switch, written once.

The falsification oracle reads its numbers through these ids; the parameter
ledger checks the report against the same ids. Cross_Pair_Bell is qualitative
and has no registry row (see NO_REGISTRY_ROW).
"""
from typing import Dict

#: kill switch -> registry row holding its predicted number.
KILL_SWITCH_ROWS: Dict[str, str] = {
    "ALP_Principia_Metric": "alp.mass_meV",
    "Fifth_Force": "portals.alp_fifth_force_range_m",
    "Proton_Decay": "proton_decay.tau_p_years",
    "Sterile_Neutrino": "portals.sterile_mixing_sin2_2theta",
    "KK_Gravitons": "geometry.m_KK_central",
}
#: The key in the report's detailed_risk_analysis that carries each number.
KILL_SWITCH_REPORT_KEYS: Dict[str, str] = {
    "ALP_Principia_Metric": "predicted_mass_meV",
    "Fifth_Force": "predicted_value",
    "Proton_Decay": "predicted_lifetime",
    "Sterile_Neutrino": "predicted_mixing",
    "KK_Gravitons": "predicted_mass",
}
#: Kill switches that are qualitative: no number, so no registry row.
NO_REGISTRY_ROW = ("Cross_Pair_Bell",)
#: Second ALP number the oracle uses (coupling), also read from its row.
ALP_COUPLING_ROW = "portals.alp_photon_coupling_gev_inv"
