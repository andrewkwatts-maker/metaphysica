# Audit lane sim-action-gauge

Scope note.
1. Read: master_ladder*.py, master_action.py (run, formulas, params), electroweak_mixing, thermal_time, gauge_unification (selected blocks), gauge_sector_complete, matter_sector_complete, lagrangian_master (selected), pneuma_mechanism (selected), actions/{reduction,zero_modes,ladder,controls/g2_zero_modes}, theories/pm; artifact rows for gauge.*, derivations.*, yukawa.*, thermal.*, pneuma.*, chirality.*, bridge.* and the action rows of formulas.json; one run of the ladder.
2. Not reached: su3/su2/u1/non_abelian_kk/topological_terms/asymptotic_safety bodies, orch_or_geometry, sampler_entropy_dynamics, cosmology_sector_complete, gr_spacetime, actions/established_*.py, controls/* other than g2_zero_modes, theories/toy, lineage yaml.
3. Artifacts are from 2026-11-01 and may predate the last two commits; every finding was re-checked against source.

## Findings

| id | file:line | category | sev | what is wrong | evidence | fix |
|---|---|---|---|---|---|---|
| sim-action-gauge-01 | gauge/electroweak_mixing.py:122,191 | correctness | critical | gauge.m_w_gev and m_z_gev are published DERIVED but restate inputs: g_2 = 2 M_W/v is hardcoded, then m_W = g_2 v/2 | `self.g_2 = Decimal('0.6524')  # Weak coupling (from M_W)`; artifact m_W 80.3659 | register as INPUT or identity and unscore, or derive g_2 from a stated rule |
| sim-action-gauge-02 | gauge/electroweak_mixing.py:105-110 | stale_path | critical | v = 246.37 GeV is the retired b3 = 24 calibration; the same rule gives 850.9 GeV on b3 = 43; it still drives g_2, g', m_W, m_Z | `v_higgs = Decimal('246.37')  # GeV - retired-seed calibration` | use the PDG v as a labelled INPUT |
| sim-action-gauge-03 | gauge/electroweak_mixing.py:99 | correctness | critical | on-shell sin^2 = 0.22320 is computed from the experimental masses and then used to "predict" them (circular) | `sin2_theta_W = Decimal('0.22320')  # On-shell ... from experimental masses` | one scheme, labelled INPUT |
| sim-action-gauge-04 | field_dynamics/thermal_time.py:291-294 | correctness | critical | thermal.alpha_T = 2.6 is registered DERIVED but is a target-first identity: gamma is built so b3 and pi cancel | `D_TOTAL = 26`, `D_STRING = 10`; the module's own docstring says "target-first identity, not a derivation" | register as ANSATZ or input ratio; read D_TOTAL from CANON |
| sim-action-gauge-05 | field_dynamics/pneuma_mechanism.py:298 | correctness | critical | pneuma.n_bridge_pairs = b3 // 2 = 21 (status EXACT) names a count that is 12 by construction; neural_gate_active compares it with 12 | `n_bridge_pairs = b3 // 2`; artifact value 21 | set from CANON bulk (24 space dirs / 2) |
| sim-action-gauge-06 | derivations/lagrangian_master.py:1554,3006 | units | critical | prose says 189,800 independent Riemann components; D^2(D^2-1)/12 at D = 26 is 38,025 (the registered value) | `= 189,800 independent components` vs derivations.riemann_symmetries 38025 | correct the text, build it from the value |
| sim-action-gauge-07 | derivations/gauge_sector_complete.py:783 | correctness | critical | gauge.mixing_validated is a hardcoded True with status DERIVED | `results["gauge.mixing_validated"] = True` | compute from the registered sigma or delete |
| sim-action-gauge-08 | gauge/master_action.py:387 | correctness | critical | gauge.qcd_alpha_s_mz = 0.117 is a literal published DERIVED "from G2 color cycle volume"; nothing computes it and SU(3)_C is OPEN (D-011) | `results["gauge.qcd_alpha_s_mz"] = 0.117  # From theory` | register INPUT (PDG 0.1179) |
| sim-action-gauge-09 | gauge/master_ladder_steps.py:75-90 | stale_path | high | the ladder's 26D action keeps xi R phi^2 and the phi field under item 1 = none; the adopted action has no scalar term | ladder step 26D lists `dim:A26:xi_R_phi2`; OPEN_TERMS blocks it only by item 8 | drop xi_R_phi2 and the A, T, phi fields from action_26 under the adopted action |
| sim-action-gauge-10 | gauge/master_ladder.py:183-190 | pipeline | high | `open_terms` (count 9) includes symbols of dropped statements (rho_breath, OR^i, V_bridge, V_face, V_tor) that are not in the adopted action | `out.update({"undefined:" + k ...})` | report them in a separate "dropped" block |
| sim-action-gauge-11 | gauge/master_ladder.py:137-148 | correctness | high | owner_item_6 is a constant-False check; no computation | `lambda: ("unresolved", False, detail)` | replace by a vacuum-ansatz check or list as a declared gap |
| sim-action-gauge-12 | gauge/master_ladder_steps.py:97-135 | correctness | high | lower-rung coefficients are labelled DERIVED (provider master_ladder) but only symbol and mass dimension are declared; M13^11 = M_*^24 Vol_13 is never evaluated | `_gravity(aid, sym, dim, DERIVED, P_LADDER)` | label DECLARED; the checks prove dimensional homogeneity only |
| sim-action-gauge-13 | gauge/master_ladder.py:157-163 | correctness | high | the 6D rung and the 6D to 4D step over a 2D space are invented: PM declares no such space; 13D to 4D is 7 + 2 internal | `InternalSpace("KK", 2, False, None, "Vol_2")  # PM declares no KK space` | reduce 13D to 4D directly or justify the 2D space |
| sim-action-gauge-14 | gauge/master_ladder.py:160 | inconsistency | high | 26D to 13D is modelled as a quotient by a 13-dim "bridge" space; the model has two 13D shadows, and signature_change=True is accepted without a rule | `Reduction(a26, a13, bridge, {"M13_11": "M_star_24*Vol_13"}, signature_change=True)` | state the real map or keep the step declared-only |
| sim-action-gauge-15 | gauge/master_action.py:1260,1278,1960 | stale_path | high | shadow-action text and section prose give each shadow "12 spatial + 1 shared time", the retired single-time picture | `+ 1 shared time = 13D(12,1)` | one time per shadow, two in the bulk |
| sim-action-gauge-16 | formulas shadow-action-13d-v23, effective-action-4d-v23, reduced-lagrangian-13d/4d, lagrangian-hierarchy-complete | stale_path | high | statements other than master-action-26d are not marked SUPERSEDED and carry excluded sectors (V_face, L_SM, L_portal, L_DM, Lambda); effective-action-4d-v23 lists gauge.sin2_theta_w, m_z, m_w as outputs although they are inputs | no SUPERSEDED in descriptions | mark SUPERSEDED or relabel as phenomenology; drop false output_params |
| sim-action-gauge-17 | formulas yang-mills-26d, pneuma-coupling (lagrangian_master.py) | stale_path | high | live ANSATZ rows for E8xE8 Yang-Mills (dim 496) and K, V(T,phi), xi R phi^2 contradict "no bulk gauge, moduli-potential or scalar terms" | `Yang-Mills action in 26D for the E8 x E8 gauge group` | mark SUPERSEDED by master-action-26d |
| sim-action-gauge-18 | formulas bridge-lagrangian-v22 (master_action.py), e8x8-visible-action | stale_path | high | bridge-lagrangian-v22 is DERIVED and drives bridge.* though rho_breath and OR^i are undefined; e8x8 row uses "Psi_27" | `[ rho_breath^i + OR^i(Psi_P) ]` category DERIVED; `acts on Psi_27` | set ANSATZ/SUPERSEDED; fix or retire Psi_27 |
| sim-action-gauge-19 | formulas 4d-fermion-lagrangian, su3/su2/u1 Lagrangians, pneuma-lagrangian | stale_path | high | standard 4D Lagrangians carry category DERIVED though SU(3), SU(2) are OPEN and none follows from the adopted action | su2 row: "unresolved orbifold point" yet DERIVED | category ANSATZ, say "written down, not derived" |
| sim-action-gauge-20 | gauge/gauge_unification.py:1755,1189 | stale_path | high | KK threshold uses h11 = 24 and prose says "alpha*^-1 = b3 = 24"; G2 has no h11 and live b3 is 43 | `h11 = 24` | read b2/b3 from the seed fork; rewrite prose |
| sim-action-gauge-21 | gauge/gauge_unification.py:1771 | correctness | high | published ALPHA_GUT_INV = 43.79 is pulled 15% toward alpha*^-1 = b3 = 43 by a FITTED weight, so it lands near b3 by construction | `AS_weight = 0.15  # FITTED mixing weight` | publish the uncorrected RG value; show the pull as a labelled fit |
| sim-action-gauge-22 | gauge/gauge_unification.py:1720,1735 | fallback | high | catch-all sets entropy_rate = -0.0825, S_eq = 9.35e-05, and alpha_T = 2.600 literal; the rate enters the KK threshold (exp(0.0825)) | `entropy_rate = -0.0825` in the except branch | fail early; read thermal.alpha_T |
| sim-action-gauge-23 | derivations/lagrangian_master.py:1414-1425 | fallback | high | `.get(key, 0)`, `.get('n_bridge_pairs', 12)`, `.get('bridge_coherence_time', 0.025)`, `.get('D_bridge_total', 24)` stand in for data; vielbein_rank is literal 26 | `bridge_results.get('D_bridge_total', 24)` | index directly; read D from CANON |
| sim-action-gauge-24 | derivations/lagrangian_master.py:259,1012 | stale_path | high | derivations.dof_after_sp2r = 324 (the 27D count) is still published DERIVED though its description says RETIRED | artifact `dof_after_sp2r 324 DERIVED` | stop registering it |
| sim-action-gauge-25 | particle/chirality.py:243 (published as chirality.generation_count) | stale_path | high | generation_count = int(b3/8) = 5 is published PREDICTED and contradicts n_gen = 3 | artifact `chirality.generation_count 5 PREDICTED` "ABANDONED route, still computed" | stop registering; n_gen comes from the fork |
| sim-action-gauge-26 | gauge/master_action.py:425 | correctness | high | gauge.chirality_reversal_probability = 3e-6 DERIVED is a literal | `= 3.0e-6` | INPUT/speculative label; keep out of the paper |
| sim-action-gauge-27 | derivations/gauge_sector_complete.py:509-514 | correctness | high | gauge.hypercharge_y_ratio = 125/144 ("visible 125 excludes 19 states") is numerology and is not a hypercharge | `Y = 125/144 from visible matter fraction` | RETIRE-FROM-PAPER; hypercharges are an SM input table |
| sim-action-gauge-28 | derivations/matter_sector_complete.py:133,512 | correctness | high | yukawa.epsilon_fn = exp(-1.5), Q_b = 2 and the A_f prefactors are Froggatt-Nielsen fit choices published DERIVED | `EPSILON_FN = ... np.exp(-1.5)` | label FITTED |
| sim-action-gauge-29 | gauge/master_action.py:412-414; electroweak_mixing.py:99 | inconsistency | high | three weak angles (0.23190 geometric, 0.23122 MS-bar, 0.22320 on-shell) with a literal k_gimel = 12 + 1/pi inline | `_k_gimel = 12 + 1 / math.pi` | one scheme table; read k_gimel from the registry |
| sim-action-gauge-30 | unitary.* rows (outside scope, seen in artifact) | stale_path | high | unitary.is_ghost_free = True DERIVED (c = 24 + 2 - 26 = 0) contradicts the withdrawn ghost-freedom appeal | artifact `unitary.status UNITARY_STABLE: GHOST_FREE`, source unitary_filter_legacy | pass to the owning lane; relabel legacy |
| sim-action-gauge-31 | gauge/master_action.py:92; 5 sibling gauge files; 4 field_dynamics files | fallback | medium | `except Exception: _A = None` hides any error, not only a missing backend | `except Exception:  # pragma: no cover` (10 sites) | catch ImportError; one shared helper |
| sim-action-gauge-32 | gauge/master_action.py:320 | fallback | medium | `_bulk_weyl_dimension` returns None on any exception or odd D | `except Exception: return None` | raise |
| sim-action-gauge-33 | field_dynamics/pneuma_mechanism.py:1971,1988 | fallback | medium | catch-all turns a computation failure into a failed-check message | `except Exception as e:` | catch the specific error |
| sim-action-gauge-34 | theories/pm/ranking.py:72 | fallback | medium | catch-all swallows every error in evaluate_combination and reports "consistency" missing | `except Exception:  # noqa: BLE001` | catch the documented errors |
| sim-action-gauge-35 | derivations/lagrangian_master.py:179-184 | correctness | medium | n_root_lattice 288 = 240 + 8 + 40 = 2 chi_eff is arithmetic numerology published GEOMETRIC | `288 = 240 (E8 roots) + 8 (Cartan) + 40` | RETIRE-FROM-PAPER |
| sim-action-gauge-36 | gauge/master_action.py:49-60 | fluff | medium | header comment reaches 0.67 sigma by inflating the theory uncertainty to 0.001 | `With theory uncertainty ... = 0.67 sigma` | delete; keep one honest sigma |
| sim-action-gauge-37 | master_action.py 2499, lagrangian_master.py 4204, gauge_unification.py 2040, pneuma_mechanism.py 2138, gauge_sector_complete.py 2211, matter_sector_complete.py 2172, gr_spacetime.py 2136 | solid | medium | far over 500 lines; each mixes compute, formulas, section prose, certificates | wc -l | split into compute / formulas / section / gates |
| sim-action-gauge-38 | derivations/gauge_sector_complete.py:128 | duplication | medium | module only re-reads values master_action derived (`_derived_elsewhere`) and re-registers the paths; v19 Lagrangian twins exist | `registry.get_param(path)` | MERGE into master_action |
| sim-action-gauge-39 | gauge/master_action.py bridge.* | dead_code | medium | bridge.distributed_or_rank = 2^12 = 4096 is a count identity labelled DERIVED; L_bridge and OR are undefined | artifact `bridge.distributed_or_rank 4096 DERIVED` | relabel identity; out of paper |
| sim-action-gauge-40 | gauge/master_ladder.py:22-39 | fluff | low | OWNER_ITEMS rows 3, 6-10 are bare questions with empty options and reasons | `3: (..., (), None, "")` | move to a doc |

## Table A: Module verdicts

| module | registers | reads forks | verdict | reason |
|---|---|---|---|---|
| gauge/master_ladder*.py (5 files) | action_ladder report, no params | yes (4 items via resolve) | FIX | -09 to -14; the honest part of the lane |
| actions/ (model, reduction, zero_modes, ladder, controls) | none | n/a | KEEP | small and generic; controls fail as designed; reduction proves only dimensional homogeneity (Table C) |
| gauge/master_action.py | master-action-26d; gauge.* (couplings, masses, flags); bridge.*; many formulas | partial | FIX and split | -08, -15 to -19, -26, -29, -36, -37; keep the master-action-26d row |
| gauge/electroweak_mixing.py | m_W, m_Z, g2, g', rho (via master_action) | no | FIX | -01, -02, -03; rho set to `Decimal('1')` |
| gauge/su3_qcd_gauge, su2_weak_gauge, u1_hypercharge, non_abelian_kk_gauge, kk_reduction_gr_gauge | generator counts 8 and 3, canonical flags | no | RETIRE-FROM-PAPER | standard 4D forms; counts are group theory; flags asserted True (not read in depth) |
| gauge/gauge_unification.py | gauge.M_GUT*, ALPHA_GUT*, sin2_theta_W_gut | no | FIX | -20, -21, -22; SO(10) 3/8 is standard |
| gauge/asymptotic_safety, topological_terms | alpha*^-1 = b3 helper, topology counts | should | FIX (not read) | alpha_star_inv_AS from FormulasRegistry; check it follows the seed |
| derivations/lagrangian_master.py | derivations.* (11) | no | FIX and split | -06, -17, -23, -24, -35; DOF counts are textbook |
| derivations/gauge_sector_complete.py | gauge.y_ratio, cos, theta_w, flags, cycle types | no | MERGE-INTO gauge/master_action.py; RETIRE y_ratio | -07, -27, -38 |
| derivations/matter_sector_complete.py | yukawa.* | yes (b2, n_gen) | FIX | n_generations = 12/4 correct; -28 |
| derivations/cosmology_sector_complete, gr_spacetime | not reached | should | FIX (not audited) | over 1,800 lines each |
| field_dynamics/thermal_time.py | thermal.* | no | FIX | -04 |
| field_dynamics/pneuma_mechanism.py | pneuma.* (racetrack calibrated at off-path seed) | no | FIX | -05, -33 |
| field_dynamics/orch_or_geometry, sampler_entropy_dynamics | quantum_bio.*, consciousness.* | partial | RETIRE-FROM-PAPER | consciousness numerology (tau_gnosis, dice_branches) is outside the core argument |
| theories/pm, theories/toy | none | yes | KEEP | -34 only |

## Table B: Path-dependent literals

| file:line | literal | should read | reaches output |
|---|---|---|---|
| gauge/electroweak_mixing.py:110 | v = 246.37 (b3 = 24 rule) | PDG v as INPUT | yes (g2, g', m_W, m_Z, prose :720) |
| gauge/gauge_unification.py:1755 | h11 = 24 | b2, b3 from b3_seed | yes (ALPHA_GUT_INV) |
| gauge/gauge_unification.py:1189 | "alpha*^-1 = b3 = 24" | registry b3 | yes (section prose) |
| gauge/gauge_unification.py:1720 | alpha_T = 2.600 | thermal.alpha_T | yes |
| field_dynamics/thermal_time.py:291-292 | D_TOTAL = 26, D_STRING = 10 | CANON bulk | yes (thermal.alpha_T) |
| field_dynamics/pneuma_mechanism.py:298 | b3 // 2 | CANON bulk 24 / 2 | yes (n_bridge_pairs = 21) |
| derivations/lagrangian_master.py:1414 | vielbein_rank 26 | CANON bulk D | yes |
| derivations/lagrangian_master.py:1422-1425 | defaults 12, 6, 0.025, 24 | registry or CANON | only if a key is missing |
| derivations/lagrangian_master.py:179-184 | 288 = 2 chi_eff | topology.chi_eff | yes (derivations.n_root_lattice) |
| derivations/gauge_sector_complete.py:509 | 125/144 | topology.chi_eff | yes (gauge.hypercharge_y_ratio) |
| derivations/matter_sector_complete.py:133 | exp(-1.5) | labelled FITTED | yes |
| particle/chirality.py:243 | int(b3 / 8) | retire | yes (chirality.generation_count = 5) |
| gauge/master_ladder_steps.py:60 | phi dimension Fr(12) | none once xi_R_phi2 is dropped | ladder report only |

## Table C: The ladder, the four lane questions

Q1. Other statements of the master action. Marked SUPERSEDED or RETIRED in the descriptions: pneuma-master-action-v23, master-action-26d-full, master-action-two-layer-or, bulk-action-26d-v23. Not marked: shadow-action-13d-v23, effective-action-4d-v23, reduced-lagrangian-13d, reduced-lagrangian-4d, lagrangian-hierarchy-complete, yang-mills-26d, pneuma-coupling, bridge-lagrangian-v22, e8x8-visible-action, pneuma-lagrangian, 4d-fermion-lagrangian (-16 to -19). Used by a computed value: none of the 26D statements has output_params; the 13D and 4D rows list outputs (gauge.sin2_theta_w, m_z, m_w, bridge.*) that are not computed from them. The ladder itself still adds xi R phi^2 to the 26D action (-09).

Q2. What the ladder computes. Report: 9 open terms, 3 failing checks (nonabelian_gauge_source, owner_item_6, zero_modes:scalar); established physics 29 REPRODUCED, 16 BLOCKED, 0 FAILS.

| step | integrated or reduced by code | only declared |
|---|---|---|
| 26D | mass dimension of each term (26); Weyl count 4096 equals the product rule 13 x 13 | M_*, xi R phi^2 (OPEN), kinetic coefficient; no field equations |
| 26D to 13D | dimension 13 = 26 - 13; time count 2 to 1 allowed by a flag; M13^11 = M_*^24 Vol_13 homogeneous (mass dimension 11) | the map is not evaluated; Vol_13 has no value; where the second time goes (constant-False check) |
| 13D to 6D | dimension 6 = 13 - 7; M6^4 = M13^11 Vol_7 homogeneous (4); Betti-based zero modes: metric 1 and spinor 1 of 8 (8 components) pass | 43 scalar moduli not declared in the 6D action (fails); 12 U(1) vectors not declared; SU(3), SU(2) have no source (fails) |
| 6D to 4D | dimension 4 = 6 - 2; M_Pl^2 = M6^4 Vol_2 homogeneous (2); Dirac count 4 | the 2D space is not PM's; L_SM, L_portal, L_DM are OPEN symbols |

Q3. Missing per step for a real solution.
- 26D: field equations from the action; a vacuum ansatz (flat M^{24,2} times quotient) and a check that it solves them; a value or derivation for M_*; the split of 24 space + 2 time directions.
- 26D to 13D: the actual map (two shadows, not a quotient); where the second time goes; ghost control (withdrawn); spinor decomposition (item 11: 64 x 64 = 4096 only through the product rule, a shadow pair is not a tensor product); coupling between the shadows.
- 13D to 6D (Y_7): a metric and a Ricci-flat check (only the flag `ricci_flat True`); existence of a torsion-free G2 structure on the Joyce resolution; zero-mode counts beyond Betti counting (index theorem for the spinor; 12 vectors, 43 scalars, 1 spinor are all that is coded); Vol_7.
- 6D to 4D: no 2D space exists in PM, so reduce Y_7 directly; 4D couplings (Yukawa overlaps, gauge couplings from cycle volumes, M_Pl^2 value) are not computed; chirality is OPEN since smooth G2 gives non-chiral spectra.

Q4. Gauge and matter derivations. None of SU(3), SU(2), U(1) or the Yukawa sector follows from the adopted action (gravity plus Weyl spinor: no gauge field, no scalar). Smooth Y_7 gives U(1)^12 only (nonabelian_gauge_source fails). The SU(3)xSU(2)xU(1) Lagrangians, the Weinberg angle, Yukawa textures (exp(-1.5)) and the SO(10) 3/8 are standard 4D forms written independently, with PDG inputs (sin2, alpha_s, M_W, v) or fitted constants. Only n_gen = b2/4 = 3 ties the gauge-adjacent numbers to the geometry.

## Verification
sim-action-gauge-01 | confirmed | g_2 = 0.6524 literal from M_W/v; m_W_predicted, m_Z_predicted published DERIVED
sim-action-gauge-02 | confirmed | v = 246.37 literal, code comment itself says retired-seed calibration
sim-action-gauge-03 | confirmed | sin2 = 0.22320 from experimental masses, then used for mass prediction
sim-action-gauge-04 | confirmed | gamma built so b3 cancels, D_TOTAL/D_STRING hardcoded, labelled DERIVED
sim-action-gauge-05 | confirmed | n_bridge_pairs = b3 // 2 gives 21 at b3 = 43 (code comment admits it)
sim-action-gauge-06 | confirmed | D^2(D^2-1)/12 at D=26 = 38025, text says 189,800
sim-action-gauge-07 | confirmed | mixing_validated = True literal
sim-action-gauge-08 | confirmed | alpha_s_mz = 0.117 literal "From theory"
sim-action-gauge-09 | partly | xi R phi^2 and phi field present in A26 but as OPEN term, not asserted; still contrary to adopted action
sim-action-gauge-10 | refuted | "undefined:" keys are a deliberate prefixed list of audit-undefined symbols, not symbols of dropped statements
sim-action-gauge-11 | partly | check is constant (unresolved, False) but it is an explicit declared gap with detail text
sim-action-gauge-12 | confirmed | lower-rung coefficients labelled DERIVED with the ladder as provider; never evaluated
sim-action-gauge-13 | partly | KK 2D space is a placeholder with the code comment "PM declares no KK space"; 13->6->4 is the declared chain
sim-action-gauge-14 | partly | ladder flags 26->13 as unresolved (item 6 gate); modelling as quotient not otherwise justified
sim-action-gauge-15 | confirmed | "1 shared time = 13D(12,1)" in text (lines ~1260, 1278, 1960)
sim-action-gauge-16 | partly | rows are ANSATZ and not marked SUPERSEDED; effective-action-4d outputParams list sin2_theta_w, m_z, m_w it does not determine
sim-action-gauge-17 | confirmed | master-action-26d-full is SUPERSEDED but yang-mills-26d (E8xE8) and pneuma-coupling (xi R phi^2) are live ANSATZ with no SUPERSEDED note
sim-action-gauge-18 | confirmed | bridge-lagrangian-v22 DERIVED with undefined rho_breath, OR^i; Psi_27 e8x8 row not separately checked
sim-action-gauge-19 | confirmed | su2 weak row category DERIVED while its own text says unresolved orbifold point, OPEN
sim-action-gauge-20 | confirmed | h11 = 24 literal in KK threshold, ignores active path
sim-action-gauge-21 | confirmed | AS_weight = 0.15 FITTED applied to alpha_GUT_inv via Delta_AS
sim-action-gauge-22 | confirmed | except Exception sets entropy_rate = -0.0825, feeds enhancement_rate into Delta_KK
sim-action-gauge-23 | partly | .get defaults exist (D_bridge_total 24, others 0) at ~1418-1425, not the exact line or all values 12/6/0.025
sim-action-gauge-24 | confirmed | dof_after_sp2r = dof_graviton_27 (27D) registered
sim-action-gauge-25 | confirmed | int(b3/8) gives 5 at b3 = 43 (code comment states ABANDONED route still published)
sim-action-gauge-26 | confirmed | 3.0e-6 literal with hand estimate comment
sim-action-gauge-27 | confirmed | "Y = 125/144 from visible matter fraction" numerology
sim-action-gauge-28 | partly | EPSILON_FN = exp(-1.5) is a literal, A_f noted fitted in one row; DERIVED category on rows not fully checked
sim-action-gauge-29 | partly | k_gimel literal and three sin2 values exist, but each is labelled (geometric, MS-bar ESTABLISHED, on-shell)
sim-action-gauge-30 | partly | unitary.is_ghost_free status DERIVED; module already marks legacy count as off-path b3 = 24
