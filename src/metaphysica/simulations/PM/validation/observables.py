"""PM binding for the fit bookkeeping: observable groups and status vocabulary.

One observable is scored once. Each group lists every validation row that
measures the same quantity against the same data; the FIRST member present
among the scored predictions is the primary row, the others are reported
under ``duplicates`` with their own sigma and are left out of chi2, counts
and N. Group order is the choice of primary and is recorded here, not hidden.

``undeclared_duplicates`` (scored rows that share an experimental reference
and sit in no group) must stay empty; a test asserts it.
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence

from metaphysica.simulations.validation import fit_partition as fp

#: observable -> validation-report paths, primary first.
OBSERVABLE_GROUPS: Dict[str, List[str]] = {
    "alpha_inv": ["electromagnetic.alpha_inv", "geometry.alpha_inverse"],
    "mu_pe": ["fermion.mass_ratio_proton_electron", "geometry.mu_pe"],
    "w0_desi_thawing_957": ["cosmology.w0_derived", "geometry.w_zero",
                            "cosmology.w_eff"],
    "w0_desi_dr2_752": ["cosmology.w0_thawing", "cosmology.w0_tzimtzum"],
    "wa_desi_dr2": ["cosmology.wa_derived", "cosmology.wa_thawing"],
    "n_s": ["cosmology.n_s_slow_roll", "geometry.n_s"],
    "cabibbo": ["ckm.V_us", "ckm.lambda_wolfenstein", "yukawa.epsilon_fn",
                "ckm.V_us_triality",
                "algebra.gaugino_cabibbo_derived",
                "algebra.gaugino_cabibbo_proxy",
                "algebra.gaugino_cabibbo_refined"],
    "pmns_theta_12": ["neutrino.theta_12_pred", "pmns.theta_12_triality"],
    "pmns_theta_13": ["neutrino.theta_13_pred", "pmns.theta_13_triality",
                      "particle.theta_13_deg", "neutrino.theta13_derived",
                      "neutrino.sin_theta13_derived"],
    "pmns_theta_23": ["neutrino.theta_23_pred", "pmns.theta_23_triality"],
}

#: registry status -> block. A value typed in is an input; tuned to data is
#: calibrated or fitted; an ansatz is an assumption. Not predictions.
NON_PREDICTION_STATUSES: Dict[str, str] = {
    "ESTABLISHED": "input", "ANCHORED": "input", "SYSTEM": "input",
    "FITTED": "fitted", "FITTED_COMPOSITE": "fitted",
    "RETRODICTED_VARIANT": "fitted", "CALIBRATED": "calibrated",
    "ANSATZ": "ansatz",
}

#: report verdict -> block.
NON_PREDICTION_VERDICTS: Dict[str, str] = {
    "INPUT": "input", "CIRCULAR": "circular", "IDENTITY": "identity",
    "UNIT_CHECK": "unit_check",
}


def partition_rows(rows: Sequence[Dict[str, Any]],
                   scoring_verdicts) -> Dict[str, Any]:
    """Apply the PM groups and status vocabulary to adapted report rows."""
    return fp.partition(rows, OBSERVABLE_GROUPS, NON_PREDICTION_STATUSES,
                        NON_PREDICTION_VERDICTS, scoring_verdicts)
