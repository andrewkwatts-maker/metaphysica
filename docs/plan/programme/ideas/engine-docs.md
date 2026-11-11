# Lane engine-docs: ideas in the engine's own docs (P7, 2026-11-11)

Sources, all read in full: docs/DISCARDED_PATH_COVERAGE.md (DPC), OLD_BRANCH_SALVAGE.md (OBS),
TWO_TIME_ASSESSMENT.md (TTA), FUTURE.md (FUT), PEER_REVIEW_MASTER_LIST.md (PRM),
STATE_REVIEW_2026-09-26.md (SR), history/RULINGS_ASSESSMENT_2026-08-25.md (RA),
CONSOLIDATION_2026-10-31.md (CON), plan/MASTER_ACTION_SELECTION_2026-11-01.md (MAS),
CHANGELOG.md at the repo root (CL; the brief says docs/, which has none). Citations are file:line.

## 1. Era summary
- Start (CL:824, 1.4.0 of 2026-05-10; PRM:22-31 of 2026-08-17): 27D (24,1,2) bulk; two 12-space shadows sharing one time plus a (0,2) spacelike sampler (TTA:23).
- Start, internal: G2 7-manifold read as TCS #187 (CL:189), b2=4, b3=24 (Ten Pillar Seeds); chi_eff=72 at 1.4.0 (CL:824), later 144 (PRM:77); n_gen=chi_eff/(4 b3), then /(2 b3) (CL:689-691).
- End (MAS:9, 41-45 of 2026-11-01; SR:10-24 of 2026-09-26): 26D (24,2) bulk; two 13D (12,1) shadows, one time each; metric -dt1^2-dt2^2+sum_12(dy1^2+dy2^2).
- End, internal: Joyce orbifold, b3_seed:seed_43_joyce ACTIVE, (b2,b3)=(12,43), b3=7+3 b2 (SR:10-24); chi_eff route OPEN (DPC:116); n_gen=b2/4=3 (SR:10-24).
- End, action: S26 = (M*^24/2) R26 + Weyl Psi of Cl(24,2), 4096 components; no bulk gauge sector (MAS:35-43).

## 2. Model timeline
| date | commit or file:line | old -> new | reason as recorded |
|---|---|---|---|
| 2026-05-10 | CL:824 | -> Ten Pillar Seeds: b3=24, chi_eff=72, n_gen=3, 288=125+163 | none |
| 2026-06-12 | CL:689-691 | n_gen=chi_eff/(4 b3) -> chi_eff/(2 b3) | "denominator fixed" (display arithmetic) |
| 2026-06-12 | CL:692-697 | theta13 -> sqrt2 sin(pi/b3)=8.67 deg | none |
| 2026-08-17 | PRM:75 | bulk read as 25D/26D/27D at once | "D=b3+2 and D=b3+3 both 'forced'" (PRM:75) |
| 2026-08-19 | TTA:3, PRM:369 | 27D (24,1,2) -> 26D (24,2), two (12,1) shadows | 27D shadows sum 25 != 27; spinor non-chiral (TTA:19-27) |
| 2026-08-19 | PRM:369 | D_shadow=11 scaffold -> SUPERSEDED | none beyond the (24,2) adoption |
| 2026-08-20 | DPC:102, OBS:112 (`95362a7`) | II_26,2 derives 13+13+2 -> RETRACTED | "the lattice gives 14+14, not 13+13+2" (OBS:112) |
| 2026-08-23 | CL:347-353 | Kahler-Ricci running Re(T) -> FROZEN | AUTHOR RULING; unfreeze on computed TCS invariants |
| 2026-08-31 | CL:19-42, TTA:76-99 | (24,2) ADOPTED -> RULED; D_crit=26 and Sp(2,R) appeals withdrawn | Bars and Kounnas: two-time critical dimension 27-28 |
| 2026-09-01 | CL:173-201 | n_faces=4 from h11 of TCS #187 -> forced by rainbow labelling | face_genericity RULED (CL:187) |
| 2026-09-06 | DPC:130 | w0 with n=b2=4 -> ruled out | mass ratio 7.1e44 (DPC:130) |
| 2026-09-07 | DPC:126 | earlier Leech generator -> FALSIFIED | det 7,144,929 (DPC:126) |
| 2026-09-14 | DPC:108-109 (`adf0081`) | Joyce (4,24), (7,24) -> UNREACHABLE | none quoted beyond UNREACHABLE |
| 2026-09-15 | DPC:111, 113 (`300f66f`, `d45b799`) | (15,24) withdrawn; Joyce b3 = 7 mod 12 settled | A1 model misapplied (DPC:111) |
| 2026-09-21 | DPC:123-124, 127-128 (`8e80d5f`, `4a5cc68`, `25681cb`) | 24x24 Gram -> 12x12x43 tensor; Hitchin label corrected | d_ijk degree 9 on a 7-manifold (DPC:123) |
| 2026-09-22 | DPC:110, 115 (`bf60005`) | b3=24 input, n_gen=b3/8 -> seed_43_joyce, n_gen=b2/4 | seed_43_joyce adopted (DPC:110) |
| 2026-10-01 | MAS:23 | racetrack vacuum -> Re(T) OPEN, CALIBRATED (D-015) | "the racetrack is not a potential Y_7 has" (MAS:23) |
| 2026-11-01 | MAS:35-49 | nine action statements A-I -> M (R26 + Weyl Psi) | "Every term defined and dimension-checked" (MAS:35) |

## 3. Ideas
Fork options cited as `fork:option` were matched against the ids in
src/metaphysica/simulations/core/variants/catalogue/*.py; DPC:191-311 proposes further DISABLED
options (bulk_formulation, plus_two_reading, ghost_control, theta13_route, leech_generator,
sterile_mixing_route) that the catalogue does not hold today.

| id | idea | kind | first seen | last seen | fate | reason recorded | reason type | today |
|---|---|---|---|---|---|---|---|---|
| ED-01 | 26D (24,2) bulk, two 13D (12,1) shadows, one time each | bulk | TTA:3 (2026-08-18) | MAS:9 (2026-11-01) | in-force | adopted 2026-08-19, ruled 2026-08-31 (CL:19-25) | ruling | bulk_signature:24_2 |
| ED-02 | 27D M^27 (24,1,2) sampler pair | bulk | PRM:22 (2026-08-17) | DPC:95 | retired | "shadows summed to 25 != 27, spinor was non-chiral" (DPC:95) | argument | no option (DPC:191 proposes bulk_formulation.sampler_pair_27d) |
| ED-03 | 25D (24,1) unified time as the bulk | bulk | PRM:124 | DPC:96 | retired | "(24,1) physics-core dimension mislabelled as a bulk" (DPC:96) | argument | no option (proposed physics_core_24_1) |
| ED-04 | (26,1) unified-time bulk, Cl(26,1)->4096 | bulk | PRM:76 | PRM:124 | refuted-by-argument | Cl(26,1) gives 8192, not 4096 (PRM:76) | argument | no option |
| ED-05 | 28D (26,2), four-agent review recommendation | bulk | TTA:93 | DPC:100 | never-implemented | not adopted; passes the lattice test (TTA:97) | argument | bulk_signature:26_2 |
| ED-06 | 26D (25,1), one time | bulk | TTA:97 | DPC:101 | never-implemented | "abandons two-time entirely" (DPC:101) | argument | bulk_signature:25_1 |
| ED-07 | D_bulk = D_crit = 26 justification | bulk | TTA:76 | DPC:97 | withdrawn | Bars and Kounnas hep-th/9705205: two-time critical dimension 27-28 (DPC:97) | argument | prose only |
| ED-08 | Bars Sp(2,R) ghost freedom gives two shadows | time | TTA:86 | DPC:98 | withdrawn | "yields ONE 24D shadow of signature (23,1), not two 13D(12,1)" (DPC:98) | argument | no option (proposed ghost_control) |
| ED-09 | +2 read as two-time plus Euclidean bridge | time | TTA:101 | DPC:99 | retired | one of three +2 readings retired (TTA:101-104) | argument | no option (proposed plus_two_reading) |
| ED-10 | +2 read as 2 x Sp(2,R) | time | TTA:101 | DPC:99 | retired | as ED-09 | argument | no option (proposed plus_two_reading) |
| ED-11 | 14D x 2 shadows, M_A^14 x M_B^14, (24,2), Sp(2,R) | shadows | PRM:169 | PRM:169 | superseded | "Superseded v15 two-time text" (PRM:169) | none | no option |
| ED-12 | D_shadow = 11 scaffold | shadows | PRM:369 | PRM:369 | superseded | marked SUPERSEDED in the 2026-08-19 cycle (PRM:369) | ruling | no option |
| ED-13 | One shared time plus a (0,2) sampler (S^{2,0}) | time | TTA:23 | PRM:412 | superseded | sampler recast as two timelike directions (PRM:412) | argument | no option |
| ED-14 | Emergent shared time, KMS average of the two shadow times | time | TTA:49 | TTA:49 | unknown | none | none | prose only |
| ED-15 | Extra time carries cross-shadow correlations; Bell prediction (Pettini) | time | TTA:36 | TTA:42 | unknown | spacelike bridges carry a superluminal hazard (TTA:38) | argument | prose only |
| ED-16 | Second time dropped in 26 -> 13 with no ruling | time | MAS:21 | MAS:62 | in-force (open) | owner_item_6 fails under every option (MAS:21) | computed-number (master_ladder.report) | no option |
| ED-17 | Per-shadow 13 = 4 + 7 + 2 | shadows | TTA:25 | TTA:25 | in-force | none | none | prose only |
| ED-18 | Z2 shadow swap includes time | shadows | TTA:26 | TTA:26 | in-force | none | none | prose only |
| ED-19 | Spinor Weyl of Cl(24,2), 4096; (s-t) mod 8 = 6 | action | TTA:24 | MAS:37 | in-force | "Dirac adds two open terms with no values" (MAS:37) | argument | action_bulk_spinor:weyl (MAS:53) |
| ED-20 | Lattice obstruction 22 = 6 mod 8; (25,1), (26,2) pass | lattice | TTA:93 | CL:30-35 | in-force | none | argument | prose only |
| ED-21 | II_26,2 = Leech + U + U derives 13+13+2 | lattice | OBS:112 | DPC:102 | withdrawn | lattice gives two rank-14 (13,1) pieces (DPC:102) | argument | prose only |
| ED-22 | Complex Leech, Eisenstein Z[omega], 12+12 split | lattice | DPC:103 | DPC:103 | refuted-by-argument | "that lead is dead as stated" (DPC:103) | argument | prose only |
| ED-23 | MiniMOG 4x3 grouping on 24 | lattice | DPC:104 | DPC:104 | refuted-by-argument | "4 x 3 IS NOT A STRUCTURE ON 24" (DPC:104) | argument | prose only |
| ED-24 | Leech as three E8 (Niemeier E8^3) | lattice | PRM:171 | DPC:125 | unknown | "the framework has been assuming both at once" (DPC:125) | argument | lattice_24d:niemeier_e8x3 |
| ED-25 | Leech lattice as the 24D lattice | lattice | CL:201 | DPC:125 | in-force | none | none | lattice_24d:leech |
| ED-26 | Pre-2026-09-07 Leech generator | lattice | DPC:126 | DPC:126 | falsified | det 7,144,929 (DPC:126) | computed-number (Leech generator Gram det) | no option (proposed leech_generator) |
| ED-27 | K12 Eisenstein lattice, 729 vacua | lattice | FUT:42 | FUT:42 | never-implemented | not started (FUT:42) | none | prose only |
| ED-28 | Golay CSS code [[24,0,8]] | lattice | PRM:120 | PRM:120 | refuted-by-argument | listed as a C-5 error (PRM:120) | argument | prose only |
| ED-29 | TCS of Fano pairs as Y7 | internal | CL:189 | DPC:105 | refuted-by-argument | "The framework should drop the TCS framing" (DPC:105) | argument | g2_construction:fano_tcs |
| ED-30 | "TCS #187" as the named manifold | internal | CL:189 | DPC:106 | refuted-by-argument | "appears in no published enumeration" (DPC:106) | argument | prose only |
| ED-31 | TCS forces b2 + b3 odd | topology-number | TTA:122 | DPC:107 | withdrawn | "There is no universal parity constraint" (DPC:107) | argument | prose only |
| ED-32 | Joyce (Z/2)^3 orbifold as Y7 | internal | TTA:125 | SR:10 | in-force | seed_43_joyce adopted (DPC:110) | ruling | g2_construction:joyce_orbifold |
| ED-33 | b2 = 7, pair (7,24) ("Joyce 1996 has (7,24)") | topology-number | TTA:125 | DPC:108 | retired | UNREACHABLE per `adf0081` (DPC:108) | computed-number (Joyce enumeration, `adf0081`) | no option (proposed seed_7_24_joyce_b2_seven) |
| ED-34 | Joyce (4,24) | topology-number | DPC:109 | DPC:109 | retired | UNREACHABLE (`adf0081`); b3 = 7 mod 12 (`d45b799`) | computed-number (`adf0081`) | no option |
| ED-35 | b3 = 24 as an input | topology-number | CL:824 | DPC:110 | superseded | superseded by `bf60005` (DPC:110) | ruling | b3_seed:seed_24 |
| ED-36 | (15,24) via the (0,16) profile | topology-number | DPC:111 | DPC:111 | withdrawn | WITHDRAWN_A1_MODEL_MISAPPLIED (DPC:111) | argument | no option (proposed seed_15_24_a1_misapplied) |
| ED-37 | A1 contribution table used outside its domain | topology-number | DPC:112 | DPC:112 | withdrawn | none quoted | argument | joyce_contribution_table (fork id in catalogue) |
| ED-38 | Joyce b3 = 7, 19, 31 (n_gen 0, 1, 2) | topology-number | DPC:113 | SR:10-24 | retired | DISABLED (`d45b799`, `f289f94`) | computed-number (n_gen = b2/4) | b3_seed:seed_7_joyce / seed_19_joyce / seed_31_joyce |
| ED-39 | (b2,b3) = (12,43), b3 = 7 + 3 b2 | topology-number | DPC:110 | SR:10 | in-force | none | ruling | b3_seed:seed_43_joyce |
| ED-40 | Half-shift parity refutation of b3 = 24 | topology-number | DPC:114 | DPC:114 | withdrawn | incomplete coverage (DPC:114) | argument | prose only |
| ED-41 | b3 = 24 from arc flag 12 x 2 | topology-number | DPC:120 | DPC:120 | unknown | NUMERICAL (DPC:120) | none | b3_origin:arc_flag_stabiliser |
| ED-42 | b3 = 24 from the D4 root shell | topology-number | DPC:121 | DPC:121 | unknown | NUMERICAL (DPC:121) | none | b3_origin:d4_root_shell |
| ED-43 | Joyce twisted sector, 7 flat + 17 twisted | topology-number | DPC:122 | DPC:122 | unknown | INERT (DPC:122) | none | b3_origin:joyce_twisted_sector |
| ED-44 | "Betti survey: b3 = 24 IS realizable" | topology-number | OBS:51 (`949725f`) | OBS:298 | superseded | SUPERSEDED (OBS:298) | none | prose only |
| ED-45 | n_gen = b3/8 | generations | CL:824 | DPC:115 | superseded | abandoned by `bf60005` (DPC:115) | ruling | n_gen_source:b3_over_dim_O |
| ED-46 | n_gen = chi_eff/48 | generations | DPC:116 | DPC:116 | refuted-by-argument | fails on the family (`3ba5848`) | computed-number (`3ba5848`) | n_gen_source:chi_eff_over_48 |
| ED-47 | n_gen = chi_eff/(2 b3), display fix | generations | CL:689 | OBS:125 | superseded | "UNRULED route; the ruled route is b_2/4" (fermion_generations.py:601, via OBS:289) | ruling | no option |
| ED-48 | n_gen = chi_eff/(4 b3) | generations | CL:689 | DPC:119 | superseded | suspect notation (DPC:119) | argument | no option |
| ED-49 | n_gen = b2/4 = 3 | generations | DPC:110 | SR:10 | in-force | none | ruling | n_gen_source:b2_over_faces |
| ED-50 | n_gen = 3 twice over: Leech 24 = 8+8+8, q+1 = 3 | generations | CL:201 | CL:201 | unknown | none | argument | prose only |
| ED-51 | chi_eff = 6 b3 | topology-number | DPC:117 | DPC:117 | refuted-by-argument | identical to b3/8 (DPC:117) | argument | prose only |
| ED-52 | Three chi_eff = 144 routes as corroboration | topology-number | PRM:77 | DPC:118 | refuted-by-argument | route A is a CY3 Euler characteristic, a type error (DPC:118) | argument | chi_eff_route (fork, OPEN) |
| ED-53 | chi_eff = 144 = b3^2/4 frozen constant (462.25 at 43) | topology-number | CL:824 | SR:206-211 | unknown | none | none | chi_eff_route:constant_144 |
| ED-54 | chi = 72 from h31 vs chi_eff 144 (CY-fourfold language) | topology-number | CL:824 | PRM:77 | refuted-by-argument | listed as C-1 inconsistency (PRM:77) | argument | prose only |
| ED-55 | 7D V7 vs "8-dimensional" vs "9D G2 x T^2" internal space | internal | PRM:78 | PRM:78 | refuted-by-argument | listed as C-1 inconsistency (PRM:78) | argument | prose only |
| ED-56 | "14 roots per G2 -> 144 per shadow -> 288" | identity | PRM:119 | PRM:119 | refuted-by-argument | G2 has 12 roots (PRM:119) | argument | prose only |
| ED-57 | 288 = 125 + 163 (vs 135 + 153) | identity | CL:824 | CON:16 | in-force | literals carry derivation comments (CON:16) | none | prose only |
| ED-58 | dim J3(O) used as 125 | identity | PRM:118 | PRM:118 | refuted-by-argument | dim J3(O) = 27 (PRM:118) | argument | prose only |
| ED-59 | Spin(7) statements | internal | PRM:122 | PRM:122 | refuted-by-argument | listed as C-5 errors (PRM:122) | argument | prose only |
| ED-60 | "G2 is the only 7D structure" | internal | PRM:126 | PRM:126 | refuted-by-argument | stated false (PRM:126) | argument | prose only |
| ED-61 | d_ijk triple intersection on H^3 | topology-number | DPC:123 | DPC:123 | refuted-by-argument | degree 9 on a 7-manifold (`8e80d5f`) | argument | prose only |
| ED-62 | 24x24 lattice Gram as metric-free form | internal | DPC:124 | DPC:124 | superseded | retired for the 12x12x43 tensor (`8e80d5f`, `4a5cc68`) | argument | prose only |
| ED-63 | Quadratic contraction labelled Hitchin; cubic Hitchin | internal | DPC:127 | DPC:128 | superseded | label corrected in `e0ccf89`, `25681cb` (DPC:128) | argument | metric_construction:quadratic_contraction / hitchin_cubic |
| ED-64 | b2_flat = 0 citation | topology-number | DPC:129 | DPC:129 | withdrawn | false citation (`2888ead`) | argument | prose only |
| ED-65 | n_faces = 4 from h11 = 4 of TCS #187 | internal | CL:189 | CL:187 | superseded | forced by rainbow labelling instead (CL:173-189) | argument | face_genericity (RULED) |
| ED-66 | face_genericity.all | internal | DPC:152 | DPC:152 | superseded | superseded 2026-09-01 (DPC:152) | ruling | face_genericity:all |
| ED-67 | PSL(3,2) / Fano symmetry of the bridge join | internal | CL:205 | CL:205 | unknown | none | none | prose only |
| ED-68 | Cross-shadow coupling phi ^ F_A ^ F_B, 42 of 210 channels | gauge | CL:362 | OBS:307 (`225a7da`) | in-force (flat R^7 only) | "flat R^7 only" (CL:391) | argument | prose only |
| ED-69 | C3 ^ F_A ^ F_B coupling | gauge | CL:401 | CL:406 | refuted-by-argument | degree 7 on a 13-manifold is malformed (CL:401-406) | argument | prose only |
| ED-70 | Smooth G2 gives U(1)^12 only; nonabelian source open | gauge | MAS:21 | MAS:62 | in-force (open) | nonabelian_gauge_source fails under every option (MAS:21) | computed-number (master_ladder.report) | no option |
| ED-71 | Bulk E8 x E8 Yang-Mills in 26D (statement B) | action | MAS:31 | MAS:48 | retired | "No reason for a bulk E8xE8 in 26D" (MAS:31) | argument | action_bulk_sectors (option set, MAS:16) |
| ED-72 | F_4 flux, V_tor, KK tower bulk (statement D) | action | MAS:33 | MAS:33 | retired | "F_4 is an 11D M-theory object in a 26D bulk" (MAS:33) | argument | action_bulk_sectors (MAS:16) |
| ED-73 | Pneuma action, Dirac mass and (Psi-bar Psi)^2 (statement A) | action | MAS:30 | MAS:35 | retired | "m and lambda vanish for a Weyl spinor" (MAS:30) | argument | no option |
| ED-74 | Two-layer OR action (statement C) | action | MAS:32 | MAS:32 | retired | "V_bridge, V_face, OR, ln Vol dt undefined" (MAS:32) | argument | no option |
| ED-75 | master-action-27d (statement E) | action | MAS:34 | MAS:34 | retired | cites the withdrawn D_crit = 26 argument (MAS:34) | argument | no option (id retired) |
| ED-76 | Master action R^2 and SUSY statements | action | PRM:166 | PRM:167 | refuted-by-argument | listed as M-4 contradictions (PRM:166-167) | argument | prose only |
| ED-77 | Racetrack vacuum Re(T) = 37.8527 | cosmology | CL:697 | MAS:23 | retired | "Not a relocated minimum, a deleted one" (DPC:138) | ruling | re_t_adoption:computed_vacuum |
| ED-78 | Kahler-Ricci running Re(T) sector | cosmology | CL:347 | CL:353 | retired (frozen) | AUTHOR RULING 2026-08-23 (CL:347) | ruling | prose only |
| ED-79 | Kahler moduli as quintessence (route 1) | cosmology | DPC:151 | DPC:151 | refuted-by-argument | mass ratio 7.1e44 (DPC:151) | computed-number (ratio) | prose only |
| ED-80 | T_i as b2 gauge kinetic functions / CY3 Kahler moduli | internal | DPC:150 | DPC:150 | unknown | none | none | moduli_indexing:b2_gauge / cy3_shadow |
| ED-81 | w0 = -(n-1)/n with n = b2 = 4 | cosmology | DPC:130 | DPC:130 | refuted-by-argument | ruled out on physics 2026-09-06, ratio 7.1e44 | computed-number (ratio) | dark_energy_betti:b2_4 |
| ED-82 | w0 with n = 3 / 6 / 12 / 8 / live b3 | cosmology | DPC:131 | SR:140-146 | unknown | n = b2 = 12 coincides with bridges_12 (SR:146) | none | dark_energy_betti:ngen_3 / chi_over_b3_6 / bridges_12 / octonion_8 / b3_live |
| ED-83 | w0 = -0.8528, thermal time alpha_T = 4.5 | cosmology | DPC:132 | DPC:132 | retired | retired pre-DESI (DPC:132) | data (pre-DESI) | prose only |
| ED-84 | alpha_T = 27/10 | cosmology | PRM:109 | PRM:411 | superseded | circular (PRM:109); relabelled STRUCTURAL (PRM:411) | argument | prose only |
| ED-85 | wa = -4/sqrt(b3) | cosmology | PRM:404 | DPC:133 | retired | "do not resurrect" (DPC:133) | ruling | prose only |
| ED-86 | wa = +0.1 / +0.27 | cosmology | DPC:134 | DPC:134 | superseded | "DESI prefers wa < 0" (DPC:134) | data (DESI) | prose only |
| ED-87 | wa = -1/sqrt(b3) canonical | cosmology | PRM:404 | PRM:24 | in-force (2026-08) | none | none | prose only |
| ED-88 | w0 = -23/24 (tzimtzum) vs thawing -42/43 | cosmology | SR:206 | SR:340-357 | unknown | none | none | dark_energy_mechanism:thawing_quintessence |
| ED-89 | n_s = 0.9996 from Re(T) slow roll | cosmology | RA:159 | DPC:135 | falsified | 8.3 sigma, Planck 2018 (DPC:135) | data (Planck 2018) | spectral_index_route:re_t_slow_roll |
| ED-90 | n_s = 0.9636 = 1 - 2 phi^2/chi_eff | cosmology | RA:159 | PRM:30 | in-force (2026-09) | none | none | spectral_index_route (other option) |
| ED-91 | H0 = 76.34 Ricci flow; 70.42 sterile | cosmology | DPC:136 | DPC:136 | superseded | superseded (DPC:136) | none | h0_route:ricci_flow |
| ED-92 | Mirror dark energy from the shadow | cosmology | CL:713 | CL:758 | refuted-by-argument | 10^13 too small (CL:713-758) | computed-number (shadow derivation) | prose only |
| ED-93 | sin2 theta_W = 0.23190 geometric | particle | RA:299 | DPC:137 | falsified | 17.1 sigma FAIL under cited_only (DPC:137) | data (cited PDG value) | prose only |
| ED-94 | theta13 = asin(1/6) = 9.594 deg | particle | RA:66 | PRM:28 | falsified | about 9 sigma, NuFIT 6.0 (DPC:140) | data (NuFIT 6.0) | no option (proposed theta13_route) |
| ED-95 | theta13 = 8.54 deg "0.4 sigma" | particle | CL:75 | CL:80 | withdrawn | NuFIT restated (CL:75-80) | argument | prose only |
| ED-96 | QLC lambda_C/sqrt2; gaugino_cabibbo; lambda = exp(-pi/2) | particle | DPC:141 | DPC:143 | falsified | 5.3, 25.6-344.7, 25.5 sigma (DPC:141-143) | data (PDG CKM) | prose only |
| ED-97 | sin^2 2theta = 1/b3 sterile mixing | particle | CL:241 | DPC:144 | falsified | excluded by IceCube / MINOS+ 2024 (DPC:144) | data (IceCube, MINOS+) | no option (proposed sterile_mixing_route) |
| ED-98 | v25 flavour ansatz at b3 = 24 (T4 / 24-cell PMNS) | particle | CL:641 | MAS:56 | retired | "a calibration at the off-path seed b3 = 24" (MAS:56) | computed-number (delta chi2 -1,158) | flavour_seed_coupling:calibrated_24 |
| ED-99 | theta12 triality 35.26 vs 33.59 | particle | PRM:296 | PRM:305 | unknown | none | none | prose only |
| ED-100 | alpha^-1 geometric (k_gimel) | particle | PRM:245 | DPC:149 | falsified | 449.6 at b3 = 43 (DPC:149) | ruling | prose only |
| ED-101 | m_mu/m_e ~ chi_eff = 144 | particle | RA:319 | RA:319 | falsified | actual 206.8 (RA:319) | data (PDG) | prose only |
| ED-102 | Sum m_nu: 0.1020 / 0.0605 / 0.0425 eV | particle | RA (0.0598/0.0817/0.0994) | MAS:57 | in-force (0.0605) | "only one of the three ... inside the window" (MAS:57) | data (DESI DR2 + CMB, oscillation floor) | prose only |
| ED-103 | Twelve external closures (Golay Lambda, Vol(S^5), ...) | identity | CL:281 | DPC:146 | falsified (9 of 12) | candidate closure gate (CL:281-308) | computed-number (candidate_closure_gate) | prose only |
| ED-104 | "24 = b3" in bc ghost, Leech, eta^-24 | identity | OBS:250 | DPC:148 | superseded | rewired to D_space_24 (`bf60005`) | argument | prose only |
| ED-105 | 168 signature swaps | identity | PRM:414 | PRM:414 | unknown | none | none | prose only |
| ED-106 | Landscape 10^33 -> 10^24 | cosmology | CL:698 | CL:699 | unknown | none | none | prose only |
| ED-107 | 26D -> 13D boundary variation | bulk | FUT:43 | FUT:43 | never-implemented | not started (FUT:43) | none | prose only |
| ED-108 | Discrete exterior calculus on compact G2 at b3 = 24 | internal | FUT:94 | FUT:107 | never-implemented | contingent on the TCS obstruction (FUT:94-107) | argument | prose only |
| ED-109 | 43 scalar zero modes from 13D -> 6D | particle | MAS:21 | MAS:62 | in-force (open) | "the child declares none" (MAS:21) | computed-number (master_ladder.report) | no option |
| ED-110 | 16,763 dead V19 lines | other | CL:447 | FUT:116 | retired | reviving them is an author ruling (FUT:116) | ruling | prose only |

Pipeline and tooling, no rows: Firebase, local paths, the beta_lambda fix `654939e` (OBS),
render and theory-uncertainty policy forks (DPC:153-154), RULINGS_ASSESSMENT scoring quarantined in
`1f7935e` (RA:8-31), G_GEOMETRY_HOLONOMY literal PASS deleted in `bfff33e` (DPC:156), CI and release work
(CON:12-21), the coupling graph and fork model (CL:157-171, 259-265), and the 2.2.x, 2.0.x, 1.3.x
and 1.0.0 CHANGELOG entries.

## 4. Owner's candidates
| # | candidate | seen | reference |
|---|---|---|---|
| 1 | Three shadows | not seen | none in these ten files |
| 2 | Shadows in pairs, or of different dimension or make-up | seen | 14+14 pieces DPC:102, OBS:112; M_A^14 x M_B^14 PRM:169; one 24D (23,1) shadow under Sp(2,R) TTA:86; D_shadow=11 PRM:369; 27D shadows 12+12+1 TTA:23 |
| 3 | Two times, one bulk and one for the shadows | seen (partly) | 27D shared time plus (0,2) sampler TTA:23; "two-time + Euclidean bridge" DPC:99; emergent shared time TTA:49; sampler recast PRM:412 |
| 4 | Three times | not seen | only (25,2), (26,2) critical dimensions TTA:76-99 |
| 5 | 26D (24,2), two 13D (12,1) shadows | seen, in force | CL:19-25, TTA:3, MAS:9, 45 |
| 6 | 27D (24,1,2) and other bulks | seen | 27D DPC:95; 25D (24,1) DPC:96; (26,1) PRM:76, 124; 28D (26,2) DPC:100; 26D (25,1) DPC:101; 14D x 2 PRM:169; 11D shadow PRM:369. 13D only as the shadow; 12D and 10D not seen |
| 7 | Other internal spaces | seen | TCS DPC:105-107; Joyce family DPC:108-113; CY3 DPC:118, 150; G2 x T^2 PRM:78; Spin(7) PRM:122 (errors only); Leech, Niemeier E8^3 DPC:125; K12 Eisenstein FUT:42; MiniMOG DPC:104; Fano / PSL(3,2) DPC:105, CL:205; octonion n=8 DPC:131 |

## 5. Gaps
- CHANGELOG.md is at the repo root, not docs/; the root copy was read.
- Commits cited inside the docs (`adf0081`, `bf60005`, `8e80d5f`, `95362a7` and others) were not opened; the engine history lanes own them.
- CANON entries (e.g. CANON["bulk"]["superseded"]["27"], DPC:95) were cited through the docs, not opened.
- `today` ids were checked by name against variants/catalogue/*.py; fork membership was confirmed only for spectral_index_route, h0_route, n_gen_source, seed_selection and dark_energy_mechanism; the rest come from the docs' own fork:option names. ED-37, ED-52, ED-90: fork named, option not mapped.
- The DISABLED options proposed at DPC:191-311 were checked by id only; they are absent from the catalogue.
- Rulings before 2026-09-14 have no git record in this repository (DPC:17-28); their dates come from the docs.
- Pipeline sections of OBS, CON and the 2.2.x, 2.0.x and 1.x CHANGELOG entries got the one summary line above.
- docs/history/ holds one file; no other file there was opened.
