"""Catalogue: cosmology forks (spectral index, H0, dark energy, Re(T)).

Split out of the former single-file variants.py; text moved verbatim.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from typing import Dict

from ..model import DISABLED, Fork, VariantOption
from ..adopted import (
    _dark_energy_betti_adopted,
    _dark_energy_mechanism_adopted,
    _h0_route_adopted,
    _re_t_adoption_adopted,
    _spectral_index_route_adopted,
)

FORKS: Dict[str, Fork] = {
    "spectral_index_route": Fork(
        id="spectral_index_route",
        question="Where does the spectral index n_s come from?",
        source="simulations.PM.cosmology.spectral_routes.ADOPTED_ROUTE",
        status="RULED",
        read_adopted=_spectral_index_route_adopted,
        notes=(
            "Opened 2026-10-25 (D-022) from the lineage catalogue. Consumers: "
            "G2Inflation.derive_observables (cosmology.n_s) and "
            "GeometricAnchors.n_s (geometry.n_s), both through "
            "PM/cosmology/spectral_routes.py. The adopted route is what the "
            "source computes today: n_s = 1 - 2 phi^2/chi_eff, which the source "
            "itself calls the golden-modulated e-fold count (N_eff = chi_eff/"
            "phi^2). CAVEAT: the catalogue's golden_modulated entry cites "
            "0b984a37:config.py, which is not in any local repository, so the "
            "original 2026-01 form could not be diffed against the current one."
        ),
        options=[
            VariantOption(
                id="golden_modulated",
                summary="n_s = 1 - 2 phi^2/chi_eff = 1 - 2/N_eff, N_eff = chi_eff/phi^2",
                consequence=(
                    "ADOPTED (read from inflation._infrared_closure_n_s and "
                    "GeometricAnchors.n_s v18.0). Catalogue: golden-modulated "
                    "e-folds, under 1 sigma; geometric justification phi^2 = phi + 1. "
                    "restored_from: 0b984a37:config.py; source 0b984a37."
                ),
                adopted=True,
            ),
            VariantOption(
                id="one_minus_2_over_b3",
                summary="n_s = 1 - 2/b3",
                consequence=(
                    "WIRED D-022. Catalogue: 11.48 sigma off; replaced 2026-01-10. "
                    "GeometricAnchors.n_s docstring v16.0: 0.9167 at b3 = 24. "
                    "restored_from: 2c246586:config.py (parent of 0b984a37); source "
                    "0b984a37. Each consumer uses its own b3 (inflation B3_SEED = 24; "
                    "GeometricAnchors.elder_kads)."
                ),
                status="disabled",
            ),
            VariantOption(
                id="re_t_slow_roll",
                summary="V ~ W_flux + W_inst; epsilon = 3/(2 Re(T)^2); n_s = 1 - 6 eps + 2 eta",
                consequence=(
                    "WIRED D-022. Catalogue: n_s = 0.9996, FALSIFIED at 8.3 sigma vs "
                    "Planck 2018 (8.263 sigma FAIL); still rescored every build as "
                    "cosmology.n_s_slow_roll; Re(T) inputs off-path. restored_from: "
                    "main:src/metaphysica/simulations/PM/cosmology/inflation.py; "
                    "source metaphysica/docs/DISCARDED_PATH_COVERAGE.md row 41."
                ),
                status="disabled",
            ),
        ],
    ),
    "h0_route": Fork(
        id="h0_route",
        question="Where does the displayed H0 (cosmology.H0_local) come from?",
        source="simulations.PM.cosmology.late_time_routes.ADOPTED_H0_ROUTE",
        status="RULED",
        read_adopted=_h0_route_adopted,
        notes=(
            "Opened 2026-10-25 (D-022) from the lineage catalogue. Consumer: "
            "FormulasRegistry.calculate_h0_local (-> cosmology.H0_local) via "
            "PM/cosmology/late_time_routes.py. The adopted route is what the "
            "source computes today: the O'Dowd composite 288/4 - 163/144 + "
            "eta_S = 71.55, which canonical_values CANON['H0_km_s_Mpc'] rules a "
            "DISPLAY value, not a topology-first prediction."
        ),
        options=[
            VariantOption(
                id="odowd_composite",
                summary="H0 = 288/4 - 163/144 + eta_S (three fitted inputs)",
                consequence=(
                    "ADOPTED (FormulasRegistry.calculate_h0_local). Catalogue: "
                    "canonical DISPLAY value; 1.43 sigma SH0ES, 8.3 Planck; H0 is "
                    "NOT a topology-first prediction. restored_from: main:src/"
                    "metaphysica/simulations/core/canonical_values.py."
                ),
                adopted=True,
            ),
            VariantOption(
                id="ricci_flow",
                summary="H0 = H0_planck (1 + sin^2(31 deg)/2) via G2 Ricci flow",
                consequence=(
                    "WIRED D-022. Catalogue: 3.17 sigma from SH0ES (76.34); still "
                    "published as cosmology.H0_ricci_variant; fitted angle "
                    "THETA_MIXING_13D_26D_DEG = 31. restored_from: main:src/"
                    "metaphysica/simulations/PM/cosmology/ricci_flow_h0.py; "
                    "source engine 871a296, 2beca44."
                ),
                status="disabled",
            ),
            VariantOption(
                id="kk_bridge",
                summary="early-dark-energy-like KK modes shift H0 through the sound horizon",
                consequence=(
                    "WIRED D-022 with the steps of hubble_tension.HubbleTensionEDE."
                    "run. Catalogue: REFUTED; lightest KK mass ~5e28 eV vs ~1e-28 eV "
                    "needed, ~57 orders off; H0 stays at the Planck value to ~5e-7. "
                    "restored_from: main:src/metaphysica/simulations/PM/cosmology/"
                    "hubble_tension.py."
                ),
                status="disabled",
            ),
        ],
    ),
    "dark_energy_mechanism": Fork(
        id="dark_energy_mechanism",
        question="What sets the dark-energy equation of state w0 (the mechanism)?",
        source="simulations.PM.cosmology.late_time_routes.ADOPTED_DE_MECHANISM",
        status="RULED",
        read_adopted=_dark_energy_mechanism_adopted,
        notes=(
            "Opened 2026-10-25 (D-022). Consumers: FormulasRegistry.calculate_w0 "
            "(w0_dark_energy) and DarkEnergy._derive_dark_energy_eos "
            "(cosmology.w0_derived). The adopted mechanism is what the source "
            "does today: thawing quintessence, w0 = -1 + 1/b3 (the catalogue says "
            "the 2025-12-31 v16.2 change replaced mep_11_13 with it). The "
            "catalogue's other mechanisms (thermal_time, mashiach_quintessence, "
            "pi_attractor, flux_attractor) stay declared: none has a w0 formula "
            "in the current source that is not already this one."
        ),
        options=[
            VariantOption(
                id="thawing_quintessence",
                summary="w0 = -1 + 1/b3 (thawing quintessence from the b3 3-cycles)",
                consequence=(
                    "ADOPTED (dark_energy.py v22; FormulasRegistry.calculate_w0 "
                    "breathing form -sigma_T). Catalogue: replaced mep_11_13 on "
                    "2025-12-31, 0.02 sigma vs DESI 2025 (commit text); the form was "
                    "chosen after the data (dark_energy.py assessment)."
                ),
                adopted=True,
            ),
            VariantOption(
                id="mep_11_13",
                summary="w0 = -(D-1)/(D+1) = -11/13 at D = 12 (maximum entropy production)",
                consequence=(
                    "WIRED D-022. Catalogue: w0 = -0.846, 1.76 sigma vs DESI 2025; "
                    "replaced 2025-12-31 by thawing quintessence. restored_from: "
                    "5755a1e0:config.py (not in any local repository; the formula is "
                    "the D_eff form quoted in dark_energy.py), source a40b0bfa."
                ),
                status="disabled",
            ),
        ],
    ),
    "re_t_adoption": Fork(
        id="re_t_adoption",
        question="Which Re(T) does the baryogenesis sector use?",
        source="simulations.PM.cosmology.baryon_asymmetry.RE_T_CALIBRATED",
        status="RULED",
        read_adopted=_re_t_adoption_adopted,
        notes=(
            "RULED 2026-10-01 by the author (D-015): Re(T) is an OPEN modulus. "
            "Y_7 fixes no Re(T) at leading order -- the G4 flux potential is "
            "positive and runs away (certificate CG.6) -- and Y_7 carries no "
            "gaugino racetrack: its singular loci hold N = 4 super Yang-Mills "
            "(CG.5) and full holonomy excludes a confining sector in phi's "
            "Joyce family (CG.10). So the value consumers use is a "
            "CALIBRATION, labelled as such, and computed_vacuum -- the "
            "stationary point of a racetrack this geometry does not have -- "
            "is demoted but kept runnable for comparison.\n\n"
            "Opened 2026-09-14. racetrack_vacuum solves the framework's own "
            "declared equations completely -- W = A e^{-aT} + B e^{-bT} with "
            "a = 2 pi / topology.elder_kads and b = 2 pi / dimensions.D_bulk, "
            "and the full N=1 potential -- and finds ONE minimum on "
            "(0.5, 300): a supersymmetric AdS vacuum, stable in the axion "
            "direction, with the dS saddle barrier above it. The incumbent "
            "value used for baryogenesis is not a stationary point of those "
            "equations, and neither is the Higgs-inverted one.\n\n"
            "So this is not a preference between two fits. One branch is the "
            "solved vacuum of the declared model; the other is a calibration "
            "that reproduces eta_b. Both are runnable so the cost of the true "
            "vacuum can be measured rather than argued."
        ),
        options=[
            VariantOption(
                id="calibrated",
                summary=("the BBN-calibrated value: a calibration, since "
                         "Re(T) is an open modulus of Y_7"),
                consequence=(
                    "BUYS: the baryon asymmetry match that the sector was "
                    "tuned for, and no published number moves.\n"
                    "COSTS: the value is not a stationary point of the "
                    "framework's own declared racetrack equations under "
                    "either Kahler slope, so moduli stabilisation is asserted "
                    "rather than solved, and the Higgs sector separately "
                    "inverts m_H to obtain a different Re(T) -- the "
                    "three-way tension stays open."
                ),
                adopted=True,
            ),
            VariantOption(
                id="computed_vacuum",
                summary="the solved stationary point of the declared potential",
                consequence=(
                    "BUYS: Re(T) becomes an OUTPUT -- the unique minimum of "
                    "the declared N=1 potential, supersymmetric, axion-stable, "
                    "with its barrier located. The six-way Re(T) freedom "
                    "collapses to the single ratio B/A, on which the vacuum "
                    "depends only logarithmically.\n"
                    "COSTS: the moduli damping exp(-Re T) falls by roughly "
                    "e^{-31}, so the eta_b match this sector was calibrated "
                    "for is destroyed. That is the honest price of the true "
                    "vacuum under the present baryogenesis model, and seeing "
                    "it is the reason this branch exists.\n"
                    "DEMOTED 2026-10-01 (D-015): the declared racetrack is "
                    "not a potential Y_7 has (CG.5, CG.10), so its vacuum is "
                    "not this geometry's Re(T). Runnable for comparison."
                ),
                status=DISABLED,
            ),
        ],
    ),
    "dark_energy_betti": Fork(
        id="dark_energy_betti",
        question="Which topological integer n sets w0 = -(n-1)/n?",
        source="simulations.PM.cosmology.dark_energy_thawing",
        status="RULED",
        read_adopted=_dark_energy_betti_adopted,
        options=[
            VariantOption(
                id="b3_24",
                summary=(
                    "n = 24 as a FROZEN integer, w0 = -23/24 = -0.9583 "
                    "(adopted). This summary read 'n = b3 = 24' until "
                    "2026-09-26, which the b3_seed ruling made false: b_3 = "
                    "43 on the adopted path, so 24 is no longer b_3 and this "
                    "option is a constant rather than a topological read. "
                    "See the b3_live option for the live-seed reading, and "
                    "the fork notes for what else the ruling moved here."
                ),
                consequence="The framework's headline: pure b3 topology, zero "
                            "free parameters, and a stated derivation (static "
                            "pressure of the 24-cycle with 12-pair "
                            "aggregation). It is also the WORST fit of the "
                            "options: 3.62 sigma on w0 alone and 3.21-3.52 "
                            "sigma in the 2D (w0,wa) plane across the whole "
                            "rho scan. Its Caldwell-Linder thawing band, "
                            "wa in [-1/8, -1/24], excludes the DR2 central wa "
                            "= -0.86 by 3.20 sigma.",
                adopted=True,
            ),
            VariantOption(
                id="b3_live",
                summary=(
                    "n = b_3 on whatever seed is live -- 43 on the adopted "
                    "path, giving w0 = -42/43 = -0.976744"
                ),
                consequence=(
                    "NOT ADOPTED, and the gap it names is the point. This is "
                    "the reading `b3_path.downstream()` already publishes as "
                    "the adopted path's consequence: w0 moves from -0.958333 "
                    "to -0.976744, i.e. from 0.017 sigma to 0.94 sigma "
                    "against the registry's DESI anchor -- worse agreement, "
                    "derived rather than frozen, and recorded there as an "
                    "accepted cost of the b3_seed ruling.\n"
                    "The fork did not carry this option until 2026-09-26, so "
                    "there was no way to select the reading the geometry "
                    "module says is in force, and no way for the drift "
                    "detector to report that the sector had NOT moved with "
                    "the seed. Which of b3_24 and b3_live is correct is the "
                    "AUTHOR'S ruling; declaring the option decides nothing "
                    "and changes no published number."
                ),
            ),
            VariantOption(
                id="b2_4",
                summary="n = b2 = h11 = 4, w0 = -3/4 = -0.75",
                consequence="RULED OUT 2026-09-06, on physics, despite being "
                            "the BEST FIT BY A LARGE MARGIN -- 0.04 sigma on "
                            "w0 and 0.25-0.74 sigma in the 2D plane against "
                            "the adopted option's 3.2-3.5. "
                            "b2 counts KAHLER moduli, and the framework's own "
                            "racetrack fixes their mass without any new "
                            "input: a_i = i*pi/b3 with T_i = b3*k_gimel/(i*pi) "
                            "gives a_i T_i = k_gimel for every face (the 1/i "
                            "hierarchy cancels exactly), and that combination "
                            "is what sets the KKLT modulus mass, m_T = "
                            "2 (a T) m_3/2 = 2 k_gimel m_3/2 (Choi et al, "
                            "hep-th/0503216). With this framework's own "
                            "gravitino mass of 1 TeV that is 24.6 TeV, while "
                            "a rolling dark-energy field needs m_phi = b3 H0 "
                            "= 3.5e-32 eV. The gap is 7.1e44 -- about "
                            "forty-five orders of magnitude, published as "
                            "geometry.kahler_over_quintessence_mass. "
                            "A field stabilised at 24.6 TeV cannot be rolling "
                            "today, so b2 = 4 cannot be the origin of w0 no "
                            "matter how well it fits. Two further objections "
                            "stand independently: it has no derivation, and "
                            "its wa would have to sit exactly at the EDGE of "
                            "the thawing wedge, an edge chosen because it "
                            "fits.",
            ),
            VariantOption(
                id="ngen_3",
                summary="n = 3 (E8 blocks = generations), w0 = -2/3 = -0.6667",
                consequence="The only option whose thawing band, "
                            "wa in [-1, -1/3], CONTAINS the DR2 central "
                            "wa = -0.86 rather than merely approaching it. "
                            "w0 sits at 1.50 sigma and the 2D distance is "
                            "1.01-1.69 sigma -- worse than b2 = 4 on w0, "
                            "better on wa, and it needs no band-edge "
                            "fine-tuning. Like b2 = 4 it has no derivation.",
            ),
            VariantOption(
                id="chi_over_b3_6",
                summary="n = chi_eff/b3 = 6, w0 = -5/6 = -0.8333",
                consequence="1.43 sigma on w0, 1.17-1.24 sigma in 2D. The 6 "
                            "already carries independent geometric meaning as "
                            "the aligned bridge pair count behind "
                            "alpha_leak = 1/sqrt(6), so it is the option with "
                            "the most existing structural support -- but it "
                            "is a middling fit rather than a good one.",
            ),
            VariantOption(
                id="bridges_12",
                summary="n = 12 bridges, w0 = -11/12 = -0.9167",
                consequence="2.89 sigma on w0, 2.48-2.75 sigma in 2D. "
                            "Recorded for completeness; no better than the "
                            "adopted option in any respect.",
            ),
            VariantOption(
                id="octonion_8",
                summary="n = dim(O) = 8, w0 = -7/8 = -0.875",
                consequence="2.16 sigma on w0, 1.78-1.98 sigma in 2D. As "
                            "above: recorded, not advocated.",
            ),
        ],
        notes="RULED 2026-09-06 in favour of the option that fits WORSE, "
              "which is the point. "
              "The fork was opened because scanning the framework's own "
              "structural integers through the SAME form w0 = -(n-1)/n, "
              "scored the same way, spans 0.25 sigma to 3.5 sigma in the 2D "
              "plane -- the dark-energy result is more sensitive to which "
              "integer is chosen than to any of the physics around it, and "
              "that is worth recording whether or not the adopted option "
              "changes. It does not change. "
              "WHAT SETTLED IT: not a smaller sigma but a mass. b2 counts "
              "Kahler moduli and b3 counts C3 moduli (axions). The "
              "framework's own racetrack stabilises the four Kahler moduli "
              "at 2 k_gimel m_3/2 = 24.6 TeV, forty-five orders of magnitude "
              "above the b3 H0 = 3.5e-32 eV a rolling field needs, so the "
              "quintessence direction cannot be one of them. It must be "
              "shift-symmetry protected, which is what an axion is and what "
              "a saxion is not. b3 = 24 (Superseded path) survives on structure. "
              "This also independently settles the S8 friction onset by the "
              "same argument, and it is COMPUTED "
              "(geometry.kahler_over_quintessence_mass) rather than asserted "
              "-- if the gravitino mass or the racetrack changes, the ruling "
              "moves with them. "
              "WHAT IT COSTS: the surviving option is the one at 3.2-3.5 "
              "sigma from DESI DR2. Ruling on physics rather than on fit "
              "means accepting the worse number, and the tension is now "
              "structural rather than a matter of choosing differently. "
              "AND A CAUTION THAT SURVIVES THE RULING: the DR2 central "
              "wa = -0.86 lies OUTSIDE the Caldwell-Linder thawing wedge for "
              "every n >= 4. If DR2 holds, thawing quintessence is "
              "disfavoured on its own terms whichever integer is adopted, so "
              "the remaining work is not re-tuning n but asking whether the "
              "dark energy sector is thawing at all. "
              "WHAT THE b3_seed RULING MOVED HERE, recorded 2026-09-26 and "
              "NOT resolved. This fork and every sigma figure in its options "
              "were computed at b_3 = 24 (Superseded path). The 2026-09-22 ruling adopted "
              "(b_2, b_3) = (12, 43), and three things follow that the option "
              "set does not yet reflect. (1) The adopted option's 24 is now a "
              "FROZEN integer, not b_3; its summary said 'n = b3 = 24' and "
              "was false. (2) The live-seed reading was not an option at all, "
              "so the divergence between this sector and "
              "b3_path.downstream() -- which publishes w0 = -0.976744 at 0.94 "
              "sigma as the ruling's accepted cost -- could be neither "
              "selected nor detected; it is now the b3_live option. (3) On "
              "the adopted seed, n = b_2 is 12, so the b2_4 option's integer "
              "and the bridges_12 option's integer COINCIDE, and the "
              "mass-scale argument that settled the 2026-09-06 ruling was "
              "computed against b_2 = 4 and b_3 = 24 (Superseded path) throughout. Whether "
              "that argument survives the reseeding is the AUTHOR'S ruling. "
              "Nothing here adopts anything or changes a published number; "
              "the sigma figures stay as measured at b_3 = 24 (Superseded path) and are "
              "labelled as such rather than silently reinterpreted.",
    ),
}
