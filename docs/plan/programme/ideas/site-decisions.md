# Lane site-decisions (P7 history and ideas review)

Source: the site decision records, read in full (the D-007 and D-012 tables in part, see Gaps).
Abbreviations used in every citation (all paths under `PrincipiaMetaphysica/docs/`):
- `DL` = `DECISION_LOG.md` (D-009 to D-029, 2026-09-30 to 2026-11-01)
- `DLO` = `archive/DECISION_LOG_older.md` (D-001 to D-008, 2026-09-30)
- `RA` = `RULINGS_ASSESSMENT.md` (2026-08-25, addenda 2026-08-25 and 2026-09-02)
- `AR` = `ADOPTION_REVIEW_2026-09-22.md`
- `D7` = `decisions/D-007-g5-classification.md`, `D12` = `decisions/D-012-amended-table.md`,
  `D19` = `decisions/D-019-path-assessment.md`
- `today` column: fork:option from `metaphysica/src/metaphysica/simulations/core/variants/catalogue/`
  (option ids grepped only).

## 1. Era summary (2026-08-25 to 2026-11-01)

- Start (RA, 2026-08-25): options scored as "geometric" if they "live in the b₃ = 24 / 163 / 288 architecture" (RA:9). Internal space a TCS G2 with b2 = 4, b3 = 24 (D7:75, "TCS construction ... (CHNP 2015)"); chi_eff = 144 = b3²/4 (D7:23); bulk 26D = 24 space + 2 times, one per shadow (D7:29); two 13D shadows, 13 = 12 bridge dims + 1 time (D7:117).
- 2026-09-22 (AR:1-6, AR:228-231): b3_seed adopted as seed_43_joyce (12, 43); family stated as five paths (four reachable plus off-family seed_24). Ruled generation route n_gen = b2/4 (AR:147).
- 2026-09-30 to 10-01: b(Y7) = (1,0,12,43,43,12,0,1), chi(Y7) = 0 (DLO:17); compact octonion φ adopted (DL:411); chi_eff = 2Σχ(K3_σ) = 48n = 144 (DL:89-95, DL:412); selection of (12, 43) by holonomy G2 plus WA-1 (DL:414).
- End (DL:1136, 2026-11-01): one action S_26 at (24,2), mostly-plus, Weyl spinor of Cl(24,2) (4096), M_*^24, status ANSATZ; two times, one per shadow (DL:1108); internal Joyce T⁷/ℤ₂³ resolution, b2 = 12, b3 = 43, chi = 0; n_gen = b2/4 = n = 3.
- Open at the end: how the second time enters (owner item 6, DL:1122, DL:1143); SM gauge group and chirality OPEN (DL:1007, DL:1066).

## 2. Model timeline

| date | commit or file:line | old -> new | reason as recorded |
|---|---|---|---|
| 2026-08-25 | RA:9 | (baseline) b3 = 24 / 163 / 288 architecture is the "geometric" axis | stated as a scoring axis, no reason |
| 2026-09-22 | AR:228-231; DLO:557 | b3_seed seed_24 (TCS, (4,24)) -> seed_43_joyce (12,43); five-path family | "the seed ruling of 2026-09-22" (DLO:557) |
| 2026-09-30 | DLO:16-17, DLO:114-120 | chi(Y7) declared -> derived 0 on every profile; seed_24 "not constructible" | D-001 CONFIRMED, Joyce resolution formula |
| 2026-09-30 | DLO:519-528, DLO:574-577 | reachable set "b₃ ∈ {7, 19, 31, 43}" -> 28 pairs on b2 + b3 = 7 + 16n | "The filter rejects this admissible structure." (DLO:516) |
| 2026-09-30 | DLO:158-167, DLO:476-477 | (12,43) chosen by n_gen data -> holonomy G2 selects n = 3 line | "the trials factor falls from 4 to 1" (DLO:166-167) |
| 2026-10-01 | DL:411; DLO:240 | φ split `all_plus_one` (signature (4,3)) -> compact `octonion_derived` | "the seed's own derivation needs it" (DLO:496-497) |
| 2026-10-01 | DL:412; DL:140-145 | chi_eff unruled, 22 definitions -> K3 reading 48n | "the reading equals n on every class, with no exceptions" (DL:133-134) |
| 2026-10-01 | DL:413 | Re(T) computed racetrack vacuum -> calibrated open modulus | "the vacuum of a racetrack Y₇ does not have" (DL:413) |
| 2026-10-01 | DL:414 | seed selection by ruling -> WA-1 correspondence | author ruling D-015 |
| 2026-10-25 | DL:796-799 | G2 geometry placeholders -> CLOSED_BY_THEOREM (Joyce Thm 11.6.1) | H1-H8 all hold on active path (g2_closure.py) |
| 2026-10-25 | DL:964-965 | retired "TCS with b3 = 24" -> false by theorem | Crowley–Nordström ν = 24, χ_ℚ odd |
| 2026-10-25 | DL:1002-1007 | SU(3)×SU(2) from A2/A1 loci on a TCS -> U(1)^12 smooth, SU(2)^12 orbifold | "The active manifold has 12 A1 loci only" (DL:1003) |
| 2026-11-01 | DL:1129-1142 | nine master-action statements, id `master-action-27d` -> one S_26, id `master-action-26d` | "none is a complete functional" (DL:1132) |

## 3. Ideas

| id | idea | kind | first seen | last seen | fate | reason recorded | reason type | today |
|---|---|---|---|---|---|---|---|---|
| SD-01 | Bulk 26D (24,2): 24 space, 2 times, one per shadow | bulk | D7:29 (09-30) | DL:1136 (11-01) | in-force | "They agree on 26D (24,2), two times, 12 bridge pairs" (DL:1108) | ruling (D-029) | bulk_signature:24_2 |
| SD-02 | 27D bulk, formula id `master-action-27d` | bulk | DL:1125 (10-26) | DL:1136 (11-01) | retired | "`master-action-27d` cites the withdrawn critical-dimension argument" (DL:1125) | argument | no option |
| SD-03 | Two-time critical dimension 27 or 28 (Bars–Kounnas); D = 26 is the one-time result | bulk | DL:503 (10-01) | DL:505 | in-force (as citation) | "two-time critical dimension 27 or 28, never 26" (DL:503) | argument (literature) | prose only |
| SD-04 | Two 13D shadows, 13 = 12 bridge dims + 1 time | shadows | D7:117 (09-30) | DL:605 (10-01) | in-force (rewire licensed) | "13D ancestral = 12 bridge dims + 1 time" (D7:117) | ruling (D-018 consensus) | no option |
| SD-05 | Shadows as Hořava–Witten walls carrying chiral E8 matter | shadows | DL:249 (09-30) | DL:481 (10-01) | refuted-by-argument | "walls are 25D, shadows 13D, Y₇ 7D" (DL:481) | argument (literature) | prose only |
| SD-06 | Dual-shadow counting, 943 × 2 ≈ 1836 | shadows | D7:52 (09-30) | D12 (10-01) | retired (DEMOTE, NONE) | "fit" (D7:52) | argument | prose only |
| SD-07 | Second time entering the KK ansatz `kk-ansatz-26-13` | time | DL:1122 (10-26) | DL:1143 (11-01) | never-implemented (open) | "Left open. Owner items 6 (second time)" (DL:1143) | none | no option |
| SD-08 | Bridge pairs 12 = D_space/2, not b3//2 (21 at 43) | bulk | D7:112 (09-30) | DL:602-603 (10-01) | in-force (licensed) | "bridge pairs BULK (21 -> 12, heals the neural gate)" (D7:112) | ruling (D-018) | no option |
| SD-09 | TCS G2 manifold with (b2,b3) = (4,24), seed_24 | internal | D7:75 (09-30) | DL:965 (10-25) | refuted-by-argument | "no TCS has these Betti numbers" (DL:965) | argument (Crowley–Nordström) | b3_seed:seed_24; g2_construction:fano_tcs |
| SD-10 | seed_24 scores better against data than main | internal | DL:909 (10-25) | DL:942 (10-25) | retired (fit at 24) | "seed_24's better score is a fit made at 24" (DL:942) | computed-number (formula_audit_*.json) | b3_seed:seed_24 |
| SD-11 | Joyce T⁷/ℤ₂³ resolution, Example 3, (12,43) all-plain | internal | DLO:17 (09-30) | DL:799 (10-25) | in-force | "Verdict CLOSED_BY_THEOREM" (DL:799) | computed-number (g2_closure.py) | b3_seed:seed_43_joyce; g2_construction:joyce_orbifold |
| SD-12 | Lower Joyce members (0,7), (4,19), (8,31) | internal | DLO:116-118 | DLO:158-159 | superseded | "restricted holonomy ... is trivial, SU(2) or SU(3)" (DLO:159) | computed-number (enumeration, closed_geometry) | b3_seed:seed_7_joyce / seed_19_joyce / seed_31_joyce |
| SD-13 | Joyce Example 4, (8+l, 47−l), whole n = 3 line b2+b3 = 55 | internal | DLO:512-515 | DLO:597-600 | unknown (choice left to author) | "What picks it within the line is the author's to rule" (DLO:599-600) | ruling | no option (joyce_contribution_table:supplied) |
| SD-14 | Order-8 stabiliser, trivial lift: eight more pairs (9,14)...(16,7) | topology-number | DLO:578 | DLO:582 | unknown | "No published example covers that case" (DLO:580) | argument | no option |
| SD-15 | Joyce JDG II Examples 1-2 (π₁ = ℤ³, ℤ); Acharya's J⁸₃₁ | internal | DLO:483-484 | DL:497 | prose only (cited) | "his JDG II Examples 1–2 have π₁ = ℤ³ and ℤ" (DLO:483-484) | argument | prose only |
| SD-16 | Γ with an order-3 or order-4 element: A2 loci give SU(3)×SU(2) | internal | DL:1020 (10-25) | DL:1066 (10-26) | never-implemented (fork candidate) | "Per ruling 4, nothing is adopted" (DL:1066) | computed-number (orbiscan, d028_scan) | no option |
| SD-17 | Order-4 Γ: SU(4)×SU(2)^n, SU(4) ⊃ SU(3)×U(1) | gauge | DL:1060 | DL:1060 | never-implemented | "a mechanism to test, not shown" (DL:1060) | computed-number (d028_scan) | no option |
| SD-18 | Earlier scan result "Kill 1 fires" (cap 64) | internal | DL:1054 | DL:1054 | withdrawn | "an artefact of the cap and is withdrawn" (DL:1054) | computed-number | prose only |
| SD-19 | 128 conical (codim-7) full-group fixed points, off the A1 branch | internal | AR:65 | AR:71 | unknown (open) | "the family has 128, resolution physics open" (AR:69-70) | computed-number (conical_point_search.py) | no option |
| SD-20 | φ split real form G₂* (`all_plus_one`), signature (4,3) | internal | DLO:176-178 | DL:800 | superseded | "first failure H2 (signature (4,3))" (DL:800) | ruling + computed-number (g2_closure.py) | g2_form_convention:all_plus_one |
| SD-21 | φ compact, read off the octonion product | internal | DLO:200-205 | DL:411 | in-force | "the compact form is what the framework's own algebra produces" (DLO:243-244) | ruling (D-015) | g2_form_convention:octonion_derived |
| SD-22 | Metric construction: quadratic contraction vs Hitchin | internal | DLO:250-251 | DL:810-811 | in-force (inert) | "both constructions are a constant multiple of I_7" (DL:811) | computed-number | metric_construction:quadratic_contraction / hitchin_cubic |
| SD-23 | Holonomy-G2 selection: π₁ finite exactly at n = 3 | identity | DLO:47 | DLO:476-477 | in-force (revised to the line) | "holds only inside the A1-filtered subfamily" (DLO:477) | computed-number (pi1 enumeration) | no option |
| SD-24 | Supersymmetry discriminates family members | other | DLO:71 | DLO:471 | refuted-by-argument | "Supersymmetry does NOT discriminate" (DLO:72) | argument (Bochner) | prose only |
| SD-25 | WA-1: one bridge per resolved A1 component | identity | DLO:732 | DL:414 | in-force | "WA-1 is a model identification, not a theorem" (DLO:765) | ruling (D-015) | seed_selection:wa1_correspondence |
| SD-26 | (12,43) by the 2026-09-22 ruling alone | identity | DLO:557 | DL:414 | superseded | kept switchable (DL:414) | ruling | seed_selection:ruling_only |
| SD-27 | Bijection "canonical up to a Klein-four relabelling" | identity | DLO:706 | DL:458 | withdrawn | "the wording ... is withdrawn in the engine" (DL:458) | computed-number (blind verifier) | prose only |
| SD-28 | n_gen = b3/8 (8 spinor components, dim O) | generations | D7:113-114 | AR:286 | refuted | "n_gen = 24/8 = 3 -- is ABANDONED" (D7:113) | computed-number (gives 5 at 43, D7:114) | n_gen_source:b3_over_dim_O |
| SD-29 | n_gen = b2/4 (faces) | generations | AR:147 | DL:1005 | in-force (ruled) | "b₂/4 = n holds on only 15,963 of the 26,155" (DL:135-136) | computed-number (kummer_index.py) | n_gen_source:b2_over_faces |
| SD-30 | n_gen = n, count of singular involutions = χ_eff/48 | generations | DL:95 | DL:143 | unknown (recommended; switch not recorded) | "Switch the generation route from b₂/4 to n" (DL:143) | computed-number (kummer_index.py) | n_gen_source:chi_eff_over_48 |
| SD-31 | n_gen = χ/24, χ(CY4) = 72, M2 tadpole of an 8-manifold | generations | DL:59 | DL:762 | refuted-by-argument (kept runnable) | "They are therefore TYPE ERRORS, class NONE." (DL:79-80) | argument | n_gen_source:chi_over_24 |
| SD-32 | χ_eff = K3 reading 2Σχ(K3_σ) = 48n, 72 per shadow | topology-number | DL:89 | DL:990 | in-force | "the reading equals n on every class" (DL:133-134) | computed-number (kummer_index.py) | chi_eff_route:k3_reading |
| SD-33 | The other 21 χ_eff definitions (b3²/4, b3²/8, 6b3, 2(h11−h21+h31) ...) | topology-number | DL:57-59 | DL:144 | retired (demoted) | "Demote the other 21 definitions as NONE or type errors." (DL:144) | computed-number + argument | chi_eff_route:constant_144 / unruled / seed_dependent |
| SD-34 | (b3/2)² as "pairs of 3-cycles" | topology-number | DL:113 | DL:113 | refuted | "refuted: b₃ is odd on the whole family" (DL:113) | argument | prose only |
| SD-35 | χ_eff = 6 b3 (n_s, e-folds) | topology-number | D7:70 | DL:1072 | refuted | "on b3 = 43 it would give 258 ... 3.5σ from Planck" (DL:854) | computed-number + data (Planck) | no option |
| SD-36 | χ_eff called the Euler characteristic of Y7 | topology-number | DL:60 | DLO:137-139 | refuted | "which is 0 (CG.2)" (DL:61) | computed-number (closed_geometry.py) | prose only |
| SD-37 | Readings of 24 as χ(K3), |2T| (McKay E6), dim adj SU(5) | lattice | DL:971 | DL:989 | refuted (none adopted) | "R0 3, R1 0, R2 19" (DL:989) | computed-number (reread_24.json) | b3_origin (seed_24 options only) |
| SD-38 | 24 as Niemeier E8³ (3 E8 blocks of 8) | lattice | DL:286 | DL:330-335 | superseded (BULK reading chosen) | "the verifier's NAMED is not adopted either: BULK" (DL:332-333) | ruling (D-012) | lattice_24d:niemeier_e8x3 |
| SD-39 | Leech lattice: N_a = b3 = 24 as gauge rank | lattice | D7:61 | D7:61 | retired (NONE) | "a Betti number read as a gauge rank (type error" (D7:61) | argument | lattice_24d:leech (bulk reading) |
| SD-40 | Leech, η⁻²⁴, bc ghosts as bulk-24 counts (leech_partition, modular_invariance) | lattice | AR:86-92 | DLO:275 | in-force (NAMED/BULK) | "They were claims about the bulk wearing b₃'s name." (AR:93) | computed-number (sims pass on both branches) | lattice_24d:leech |
| SD-41 | 24-cell / binary tetrahedral T4 flavour reading, θ13 8.669° | particle | DLO:637-641 | DL:596-598 | unknown (licensed, execution not recorded) | "theta_13 heals, trials factor 2" (D7:87) | ruling (D-018 consensus) | flavour_seed_coupling:calibrated_24 |
| SD-42 | Flavour formulas follow the live b3 (θ13 4.835°) | particle | AR:115 | DLO:639-640 | superseded | "was a mis-disentanglement" (DLO:639-640) | argument | flavour_seed_coupling:follow_seed |
| SD-43 | k_gimel = b3/2 + 1/π and everything on it (α⁻¹, v, sin²θ_W) | other | DLO:625 | D7:11 | retired (NONE) | "agree with data only at the retired 24" (DLO:630-631) | argument | prose only |
| SD-44 | 288 = 12 b3 ancestral roots; SO(24) 276 + 24 − 12 | other | D7:16-17 | DL:995 | refuted | "the formula is wrong on the active manifold" (DL:995) | computed-number (reread_24.json) | prose only |
| SD-45 | 163 = 7b3 − 5, 135/153 integers, gate ratios | other | D7:14-20 | D12 | retired (NONE) | "WARNING: This is NUMEROLOGY, not rigorous physics" (D7:20) | argument | prose only |
| SD-46 | Twelve integer identities holding on seed_24 alone | identity | AR:143-146 | AR:154-157 | retired (BROKEN on adopted) | "Twelve hold on seed_24 ALONE." (AR:143) | computed-number (identity_ledger.json) | prose only |
| SD-47 | Re(T) from racetrack vacuum, a = 2π/b3 | cosmology | DLO:369 | DL:413 | refuted (demoted) | "read a Betti number as a gauge rank" (DLO:369) | computed-number (racetrack_vacuum, flux_vacuum.py) | re_t_adoption:computed_vacuum |
| SD-48 | Re(T) as labelled calibration / open modulus | cosmology | DLO:441-446 | DL:1140 | in-force | "an open modulus" (DL:413) | ruling (D-015, D-029) | re_t_adoption:calibrated |
| SD-49 | Racetrack exponent pairs from the derived menu {3,...,43} | cosmology | AR:378 | AR:420 | never-implemented (option table) | "every pair that restores the ordering gives an AdS minimum" (AR:401-402) | computed-number (racetrack_pairs.py) | no option |
| SD-50 | Moduli fixed by gaugino condensation on a b₁ = 0 locus | cosmology | DL:151 | DL:199-201 | refuted (no-go inside Y7) | "holonomy exactly G₂ and a confining gauge sector are mutually exclusive" (DL:198-199) | computed-number | prose only |
| SD-51 | Flux potential accelerates (single and multi-field) | cosmology | DL:168 | DL:484 | refuted | "cannot drive accelerated expansion" (DL:205-206) | computed-number + argument | prose only |
| SD-52 | M2 instantons on rigid associatives fix Re(T) | cosmology | DL:483 | DL:630 | refuted (flat associatives only) | "KILLED for flat (totally geodesic) associatives" (DL:630-631) | computed-number (instanton_cycles.py) | prose only |
| SD-53 | Corrections to K beyond (U/T)² | cosmology | DLO:396 | DL:482 | refuted-by-argument | "the λ⁻⁵ runaway holds to all orders in U/T" (DL:482) | argument (literature) | prose only |
| SD-54 | Chirality via the heterotic dual | particle | DL:240 | DL:480 | refuted-by-argument | "the spectra are non-chiral" (DL:480) | argument (AKM 2021) | prose only |
| SD-55 | Flavour hierarchy from three locus volumes | particle | DL:254 | DL:485 | refuted-by-argument | "No chiral points, no Yukawa couplings" (DL:485) | argument | prose only |
| SD-56 | SU(3) from A2 loci and SU(2) from A1 loci on a TCS | gauge | DL:1002 | DL:1007 | refuted | "The active manifold has 12 A1 loci only" (DL:1003) | computed-number (g2_geometry.py:1142) | no option |
| SD-57 | w0 = −1 + 1/b3, frozen −23/24 vs live −42/43 | cosmology | DLO:633-636 | DL:1077-1081 | in-force b3_24, flip held | "SP11 agreed the flip to b3_live and it is held" (DL:1081) | ruling | dark_energy_betti:b3_24 / b3_live |
| SD-58 | w0 = −11/13 (MEP) | cosmology | DL:749 | DL:1071 | superseded | "replaced by thawing quintessence at 0.02 sigma" (DL:760-761) | data (DESI 2025) | dark_energy_mechanism:mep_11_13 |
| SD-59 | n_s = 1 − 2/b3 | cosmology | DL:747 | DL:865-866 | superseded | "11.48 sigma off (replaced 2026-01-10)" (DL:756) | data (Planck) | spectral_index_route:one_minus_2_over_b3 |
| SD-60 | n_s from slow roll of the claimed inflaton | cosmology | RA:87 | DL:757 | falsified | "8.3σ FAIL" (RA:87) | data (Planck 2018) | spectral_index_route:re_t_slow_roll |
| SD-61 | H0 routes: O'Dowd composite, Ricci flow, KK bridge | cosmology | DL:748 | DL:759 | superseded / falsified | "kk_bridge REFUTED, about 57 orders off" (DL:759) | data (SH0ES, Planck) | h0_route:odowd_composite / ricci_flow / kk_bridge |
| SD-62 | θ13 = asin(1/6) = 9.594° | particle | RA:25 | RA:313-314 | falsified | "≈ 9σ FAIL" (RA:25) | data (NuFIT) | prose only |
| SD-63 | geometry.theta_13 = 8.54° as a geometric cross-check | particle | RA:28 | RA:296-301 | withdrawn | "It is the anchor restated under a `geometry.*` name" (RA:300-301) | argument | prose only |
| SD-64 | S8 from the friction kernel (0.784 analytic) | cosmology | RA:63 | RA:265-268 | superseded (ODE 0.821) | "It was functioning as a knob." (RA:261) | computed-number (growth ODE) | prose only |
| SD-65 | Σm_ν canonical: spectral 0.0598 / geometric 0.0817 / 0.0605 | particle | RA:131-133 | DL:1139 | superseded (0.0605 in force) | "One claim: `particle.sigma_m_base_eV` = 0.0605 eV" (DL:1139) | data (DESI DR2) | prose only |
| SD-66 | sin²θ_W = (3/8)(1 − 2/24π) at M_Z | gauge | RA:182-184 | RA:182-184 | falsified | "was already falsified this cycle" (RA:183-184) | data | prose only |
| SD-67 | KK tower 5.02, 10.04, 15.06 TeV (1:2:3) | particle | DL:1048 | DL:1049-1050 | retired (OPEN/CALIBRATED) | "is not the flat-orbifold spectrum, which goes as √q" (DL:1048) | computed-number (kkspec) | no option |
| SD-68 | Action field content: E8×E8 YM, F4 flux, KK tower, moduli, L_bridge ... | action | DL:1108 | DL:1138 | retired (readmission rule) | "returns only with a definition, a source for its coefficient" (DL:1138) | ruling (D-029) | action_bulk_sectors:e8xe8_ym / flux_f4 / kk_tower |
| SD-69 | Dirac bulk spinor (8192) instead of Weyl | action | DL:1118 | DL:1137 | superseded (Weyl stays) | "With one Weyl spinor, Ψ̄Ψ = 0, so m and λ vanish." (DL:1118) | ruling | action_bulk_spinor:dirac |
| SD-70 | Kähler modulus as the quintessence field | cosmology | D7:106 | D7:106 | refuted | "No, by 45 orders" (D7:106) | computed-number | prose only |

Not ideas (one line): D-004, D-007, D-012 and D-018 set the G5 classification rules and their blind
verification (56% twice, DL:560); D-013, D-014, D-020 to D-022, D-024, D-025 set publication, wording,
the Paths tab and recovered formula options; D-019 and D-026 set path ranking (D19 is a skeleton);
AR §2 to §4 are artifact search, build and docstring fixes; RA R4, R6, R7 are gate and anchor rulings.

## 4. Owner's candidates

| # | candidate | seen | reference |
|---|---|---|---|
| 1 | Three shadows | not seen | (searched "three shadows", "shadow" in all sources) |
| 2 | Shadows in pairs, or of different dimension or make-up | seen, partial | shadows as two HW walls, killed DL:249-253, DL:481; "dual-shadow counting" D7:52; no other dimension or make-up |
| 3 | Two times: one bulk, one for the shadows | not seen | |
| 4 | Three times (any split) | not seen | |
| 5 | Two times, one per shadow, 26D (24,2), two 13D (12,1) shadows | seen | DL:91 ("the two-time ruling"); D7:29; D7:117; DL:1108; DL:1136; second time in the KK ansatz open DL:1122, DL:1143 |
| 6 | 27D (24,1,2) and other bulk dimensions | seen | `master-action-27d` retired DL:1125, DL:1136; two-time critical dimension 27 or 28 DL:503; D = 26 one-time DL:505; 14D, 12D, 11D, 10D not seen |
| 7 | Other internal spaces | seen | TCS DL:964-965, D7:75, DL:812; Joyce Example 4 DLO:512-517; JDG II Ex. 1-2 DLO:483-484; J⁸₃₁ DL:497; order-3/4 Γ DL:1020, DL:1053-1066; T³-fibred CY3 (heterotic dual) DL:242-243; CY4 χ/24 DL:59, DL:78; Leech D7:61, AR:89; Niemeier E8³ DL:286; octonion φ DLO:200-205; Fano arc DLO:687-694; 24-cell D7:87; Spin(7) not seen |

## 5. Gaps

- `D7` read in full; `D12` read for its header, its changed-rows table (D12:9-20) and grepped rows (FR04, FR18, FR20, NC16, SP05, SP11, SP13, SP14, OT06, OT13, OT14, OT15, OT18); its other 108 rows are copies of D7 per D12:3 and were not compared line by line.
- Documents the log cites were not opened: `docs/plan/geometry/*` (reread_24.json, d028_scan.md, c4_gauge_chirality.md, c5_kk_spectrum.md, master_action_audit.md, formula_audit_*.json), `docs/plan/2026-10-25-paths-site.md`, the engine's `MASTER_ACTION_SELECTION_2026-11-01.md`, `BRIDGE_CHANNEL_ASSIGNMENT.md` (site-issues lane).
- No commits opened: this is a docs lane. Engine commits named in the log (d271d97, 27d5b75, ffb09ee, 8df2df4, 90b1b93, 610f226, 3c4320c, 204204c) are cited by the log only.
- `today` column from option ids and summaries grepped in the variants catalogue; option bodies not read. No variants option matches SD-30 by name; chi_eff_over_48 is the nearest (DL:95 calls them the same statement).
- Dates of "first seen" are the record dates of these files; earlier origins are for the history lanes.
