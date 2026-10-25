"""The geometry-to-physics chain (D-025): an ordered, declarative walkthrough.

Each step names a geometric input and the operation applied to it, then points
at the engine artifacts that hold the numbers: ``param_path`` (parameters.json),
``formula_id`` (formulas.json) and, for the closed-geometry stage,
``theorem_id`` (closed_geometry.certificate, or "closure_report").  No number
lives here; the generator ``generate_geometry_to_physics`` reads them all from
the artifacts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

STAGES: Tuple[Tuple[str, str], ...] = (
    ("bulk", "Bulk and signature"),
    ("g2_existence", "G2 manifold existence (closed-geometry theorems)"),
    ("topology", "Topology counts"),
    ("gauge_group", "Gauge group"),
    ("generations", "Generations and chirality"),
    ("couplings", "Couplings"),
    ("masses_mixing", "Masses and mixing"),
    ("gravity", "Gravity"),
    ("cosmology", "Cosmology"),
)
STAGE_IDS: Tuple[str, ...] = tuple(s for s, _ in STAGES)


@dataclass(frozen=True)
class Step:
    id: str
    stage: str
    geometric_input: str
    operation: str
    output_symbol: str
    formula_id: str = ""
    param_path: str = ""
    section_id: str = ""
    figure: str = ""       # fold | eh_profile | betti | proof_flow | ""
    theorem_id: str = ""   # closed_geometry.certificate id, or "closure_report"


_S = Step

_BULK = (
    _S("bulk_dim", "bulk", "A 26-dimensional bulk of signature (24,2).",
       "Take the critical dimension as the starting space.", "D_bulk",
       "26d-signature", "dimensions.D_bulk", "2.1"),
    _S("shadow_split", "bulk", "Two times, one per shadow.",
       "Split the bulk into two 13D shadows with 12 space directions each.",
       "D_shadow", "abstract-framework-overview", "geometry.D_shadow_total", "2.1"),
    _S("g2_dim", "bulk", "Seven internal dimensions per shadow.",
       "Choose a G2-holonomy 7-manifold Y_7 as the internal space.", "D_G2",
       "g2-holonomy-foundations", "dimensions.D_G2", "2.4"),
)
_EXISTENCE = (
    _S("cg_selection", "g2_existence", "The group (Z/2)^3 acting on the torus T^7.",
       "Fold the flat torus by three involutions; select (b2, b3) = (12, 43).",
       "Y_7 family", section_id="2.4", figure="fold", theorem_id="y7-selection"),
    _S("cg_singular", "g2_existence", "Twelve disjoint 3-tori in the fold locus.",
       "Resolve each crease with an Eguchi-Hanson patch.", "singular set",
       section_id="2.4", figure="eh_profile", theorem_id="y7-singular-components"),
    _S("cg_pi1", "g2_existence", "The three involutions span the group.",
       "Compute the fundamental group; it is trivial.", "pi_1(Y_7)",
       section_id="2.4", theorem_id="y7-fundamental-group"),
    _S("cg_metric", "g2_existence", "Hypotheses H1-H8 measured on the active seed.",
       "Apply Joyce 2000, Thm 11.6.1: a torsion-free G2 structure exists.",
       "Hol = G2", section_id="2.4", figure="proof_flow",
       theorem_id="closure_report"),
)
_TOPOLOGY = (
    _S("b2", "topology", "The resolved 7-manifold Y_7.",
       "Count degree-2 cohomology classes.", "b_2", "betti-numbers",
       "topology.b2", "2.4", figure="betti"),
    _S("b3", "topology", "The resolved 7-manifold Y_7.",
       "Count degree-3 classes: b_3 = 7 + 3 b_2.", "b_3", "betti-numbers",
       "particle.b3", "2.4"),
    _S("chi_eff", "topology", "Three Kummer K3 surfaces, one per involution.",
       "Sum the Euler characteristics of the K3 reading.", "chi_eff",
       "euler-characteristic", "geometry.chi_eff_total", "2.4"),
)
_GAUGE = (
    _S("gauge_content", "gauge_group", "Twelve A1 loci with b_1 = 3.",
       "M-theory on the locus gives b_2 = 12 U(1) vector multiplets.",
       "gauge content", section_id="3.2", theorem_id="y7-gauge-content"),
    _S("no_confinement", "gauge_group", "Every singular locus has b_1 > 0.",
       "Exclude a confining sector on a holonomy-G2 manifold.", "no confinement",
       section_id="3.2", theorem_id="confinement-exclusion"),
)
_GENERATIONS = (
    _S("k3_reading", "generations", "One Kummer K3 per singular involution.",
       "Count the K3 factors as generation sources.", "n (K3 count)",
       section_id="4.2", theorem_id="k3-reading-generations"),
    _S("chiral_index", "generations", "Associative chirality projector.",
       "Count left minus right zero modes.", "chiral index",
       "chirality-index-theorem", "chirality.chiral_index", "4.1"),
    _S("n_gen", "generations", "Three singular involutions, b_2 = 12.",
       "Divide: n_gen = b_2 / 4.", "n_gen", "three-generations",
       "topology.n_gen", "4.2"),
)
_COUPLINGS = (
    _S("alpha_gut_inv", "couplings", "Gauge coupling unification on Y_7.",
       "Run the three couplings to a common scale.", "1/alpha_GUT",
       "gauge-coupling-unification", "gauge.ALPHA_GUT_INV", "3"),
    _S("m_gut", "couplings", "The unification condition.",
       "Solve for the scale at which the couplings meet.", "M_GUT", "gut-scale",
       "gauge.M_GUT", "3"),
    _S("alpha_inv", "couplings", "G2 geometry of the electromagnetic factor.",
       "Evaluate the geometric fine-structure expression.", "1/alpha",
       "alpha-inverse-geometric", "electromagnetic.alpha_inv", "3.1"),
    _S("sin2_theta_w", "couplings", "The topological weak-mixing candidate.",
       "Evaluate sin^2(theta_W) from the topology counts.", "sin^2 theta_W",
       "ew-weinberg-angle-v19", "gauge.sin2_theta_w_geometric", "6.9"),
    _S("g2_weak", "couplings", "The SU(2) factor of the gauge sector.",
       "Fix the weak coupling from the Lagrangian.", "g_2",
       "su2-weak-lagrangian-v22", "gauge.weak_coupling_g2", "3.2"),
)
_MASSES = (
    _S("v_us", "masses_mixing", "Froggatt-Nielsen hierarchy from Y_7.",
       "Read the Cabibbo angle from the texture.", "V_us", "ckm-hierarchy",
       "ckm.V_us", "4.3"),
    _S("v_cb", "masses_mixing", "The same hierarchy at second order.",
       "Evaluate V_cb.", "V_cb", "ckm-hierarchy", "ckm.V_cb", "4.3"),
    _S("theta12", "masses_mixing", "Neutrino sector from G2 topology.",
       "Evaluate the solar angle.", "theta_12", "pmns-theta-12",
       "neutrino.theta_12_pred", "4.5"),
    _S("theta13", "masses_mixing", "Neutrino sector from G2 topology.",
       "Evaluate the reactor angle.", "theta_13", "pmns-theta-13",
       "neutrino.theta_13_pred", "4.5"),
    _S("delta_cp", "masses_mixing", "Neutrino sector from G2 topology.",
       "Evaluate the CP phase.", "delta_CP", "pmns-delta-cp",
       "neutrino.delta_CP_pred", "4.5"),
    _S("higgs_quartic", "masses_mixing", "Moduli potential on Y_7.",
       "Read the Higgs quartic coupling.", "lambda",
       "higgs-quartic-from-geometry-v19", "higgs.lambda_quartic", "4.4"),
    _S("higgs_mass", "masses_mixing", "Moduli stabilisation.",
       "Evaluate the Higgs mass.", "m_H", "higgs-mass", "higgs.m_higgs_pred", "4.4"),
)
_GRAVITY = (
    _S("m_pl", "gravity", "Kaluza-Klein reduction of the 14D action.",
       "Integrate over Y_7 to get the 4D Planck mass.", "M_Pl",
       "einstein-hilbert-14D", "cosmology.M_Pl_4D", "5.1"),
    _S("g_newton", "gravity", "The reduced Einstein-Hilbert term.",
       "Read Newton's constant from the G2 volume.", "G_N",
       "gr-newton-from-g2-v19", "gravity.newton_constant_theory", "5.1"),
)
_COSMOLOGY = (
    _S("n_s", "cosmology", "Dimensional-reduction cascade.",
       "Evaluate the geometric spectral index.", "n_s", param_path="geometry.n_s",
       section_id="5.2"),
    _S("n_s_slow_roll", "cosmology", "Slow-roll evaluation of the same quantity.",
       "Evaluate n_s from the slow-roll expression.", "n_s (slow roll)",
       param_path="cosmology.n_s_slow_roll", section_id="5.2"),
    _S("w0", "cosmology", "Four-face dark-energy sector.",
       "Evaluate the dark-energy equation of state.", "w_0",
       "dark-energy-eos-derivation", "cosmology.w0_derived", "5.2"),
    _S("omega_dm", "cosmology", "Matter split between the sectors.",
       "Evaluate the dark-matter fraction.", "Omega_DM",
       "cosmo-omega-matter-split-v19", "cosmology.omega_dm_total", "5.3"),
    _S("lambda_cc", "cosmology", "G2 entropy with an inflation-era correction.",
       "Evaluate the cosmological constant.", "Lambda",
       "cosmological-constant-geometric", "cosmology.Lambda_derived", "5.5"),
    _S("h0", "cosmology", "The unwinding scale.", "Evaluate the Hubble constant.",
       "H_0", "h0-unwinding-scale", "cosmology.H0_physical", "5.9"),
)

CHAIN: Tuple[Step, ...] = (_BULK + _EXISTENCE + _TOPOLOGY + _GAUGE
                           + _GENERATIONS + _COUPLINGS + _MASSES + _GRAVITY
                           + _COSMOLOGY)
