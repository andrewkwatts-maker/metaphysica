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
- End, internal: Joyce orbifold, b3_seed:seed_43_joyce ACTIVE, (b2,b3)=(12,43), b3=7+3 b2 (SR:10-24); chi_eff route OPEN at DPC:116, RULED 2026-10-01 to k3_reading, chi_eff = 48 n = 144 (g2_metric.py:115-123); n_gen=b2/4=3 (SR:10-24).
- End, action: S26 = (M*^24/2) R26 + Weyl Psi of Cl(24,2), 4096 components; no bulk gauge sector (MAS:35-43).

## 2. Model timeline
| date | commit or file:line | old -> new | reason as recorded |
|---|---|---|---|
| 2026-05-10 | CL:824 | -> Ten Pillar Seeds: b3=24, chi_eff=72, n_gen=3, 288=125+163 | none |
| 2026-06-12 | CL:689-691 | n_gen=chi_eff/(4 b3) -> chi_eff/(2 b3) | "denominator fixed" (display arithmetic) |
| 2026-06-12 | CL:692-697 | theta13 -> sqrt2 sin(pi/b3)=8.67 deg | none |
| 2026-08-17 | PRM:75 | bulk read as 25D/26D/27D at once | "D=b3+2 and D=b3+3 both 'forced'" (PRM:75) |
| 2026-08-19 | TTA:3, PRM:369, `0fb9a1e` | 27D (24,1,2) -> 26D (24,2), two (12,1) shadows | 27D shadows sum 25 != 27; spinor non-chiral (TTA:19-27) |
| 2026-08-19 | PRM:369 | D_shadow=11 scaffold -> SUPERSEDED | none beyond the (24,2) adoption |
| 2026-08-20 | DPC:102, OBS:112 (`95362a7`) | II_26,2 derives 13+13+2 -> RETRACTED | "the lattice gives 14+14, not 13+13+2" (OBS:112) |
| 2026-08-23 | CL:347-353 | Kahler-Ricci running Re(T) -> FROZEN | AUTHOR RULING; unfreeze on computed TCS invariants |
| 2026-08-31 | CL:19-42, TTA:76-99, `dca1fc1` (committed 2026-09-01) | (24,2) ADOPTED -> RULED; D_crit=26 and Sp(2,R) appeals withdrawn | Bars and Kounnas: two-time critical dimension 27-28 |
| 2026-09-01 | CL:173-201 | n_faces=4 from h11 of TCS #187 -> forced by rainbow labelling | face_genericity RULED (CL:187) |
| 2026-09-06 | DPC:130, `fbd320e` | w0 with n=b2=4 -> ruled out | mass ratio 7.1e44 (DPC:130) |
| 2026-09-07 | DPC:126, `1c88906` | earlier Leech generator -> FALSIFIED | det 7,144,929 (DPC:126) |
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
Second pass: `CV` = src/metaphysica/simulations/core/canonical_values.py; action.py, algebra.py,
cosmology.py, g2_forms.py, g2_metric.py, policy.py, seed.py are under variants/catalogue/.

| id | idea | kind | first seen | last seen | fate | reason recorded | reason type | today |
|---|---|---|---|---|---|---|---|---|
| ED-01 | 26D (24,2) bulk, two 13D (12,1) shadows, one time each | bulk | TTA:3 (2026-08-18) | MAS:9 (2026-11-01) | in-force | adopted 2026-08-19 (`0fb9a1e`), ruled 2026-08-31 (CL:19-25), committed in `dca1fc1` (2026-09-01) | ruling | bulk_signature:24_2 |
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
| ED-15 | Extra time carries cross-shadow correlations; Bell prediction (Pettini) | time | TTA:36 | CV:489-491 | in-force | "Inter-shadow correlations propagate in the other shadow's time ... causal" (CV:489-491, 2026-08-19 ruling note); spacelike bridges carry a superluminal hazard (TTA:38) | ruling | prose only |
| ED-16 | Second time dropped in 26 -> 13 with no ruling | time | MAS:21 | MAS:62 | in-force | open; owner_item_6 fails under every option (MAS:21) | computed-number (master_ladder.report) | no option |
| ED-17 | Per-shadow 13 = 4 + 7 + 2 | shadows | TTA:25 | TTA:25 | in-force | none | none | prose only |
| ED-18 | Z2 shadow swap includes time | shadows | TTA:26 | TTA:26 | in-force | none | none | prose only |
| ED-19 | Spinor Weyl of Cl(24,2), 4096; (s-t) mod 8 = 6 | action | TTA:24 | MAS:37 | in-force | "Dirac adds two open terms with no values" (MAS:37) | argument | action_bulk_spinor:weyl (MAS:53) |
| ED-20 | Lattice obstruction 22 = 6 mod 8; (25,1), (26,2) pass | lattice | TTA:93 | CL:30-35 | in-force | none | argument | prose only |
| ED-21 | II_26,2 = Leech + U + U derives 13+13+2 | lattice | OBS:112 | DPC:102 | withdrawn | lattice gives two rank-14 (13,1) pieces (DPC:102) | argument | prose only |
| ED-22 | Complex Leech, Eisenstein Z[omega], 12+12 split | lattice | DPC:103 | DPC:103 | refuted-by-argument | "that lead is dead as stated" (DPC:103) | argument | prose only |
| ED-23 | MiniMOG 4x3 grouping on 24 | lattice | DPC:104 | DPC:104 | refuted-by-argument | "4 x 3 IS NOT A STRUCTURE ON 24" (DPC:104) | argument | prose only |
| ED-24 | Leech as three E8 (Niemeier E8^3) | lattice | PRM:171 | DPC:125 | unknown | "the framework has been assuming both at once" (DPC:125) | argument | lattice_24d:niemeier_e8x3 |
| ED-25 | Leech lattice as the 24D lattice | lattice | CL:201 | DPC:125 | in-force | none | none | lattice_24d:leech |
| ED-26 | Pre-2026-09-07 Leech generator | lattice | `1c88906` (2026-09-07) | DPC:126 | falsified | det 7,144,929 (DPC:126) | computed-number (Leech generator Gram det) | no option (proposed leech_generator) |
| ED-27 | K12 Eisenstein lattice, 729 vacua | lattice | FUT:42 | FUT:42 | never-implemented | not started (FUT:42) | none | prose only |
| ED-28 | Golay CSS code [[24,0,8]] | lattice | PRM:120 | PRM:120 | refuted-by-argument | listed as a C-5 error (PRM:120) | argument | prose only |
| ED-29 | TCS of Fano pairs as Y7 | internal | CL:189 | DPC:105 | refuted-by-argument | "The framework should drop the TCS framing" (DPC:105); "REFUSED (D-023): no cited building blocks are in the engine" (g2_forms.py:236-237); option not DISABLED as DPC:218 proposed | argument | g2_construction:fano_tcs |
| ED-30 | "TCS #187" as the named manifold | internal | CL:189 | DPC:106 | refuted-by-argument | "appears in no published enumeration" (DPC:106) | argument | prose only |
| ED-31 | TCS forces b2 + b3 odd | topology-number | TTA:122 | DPC:107 | withdrawn | "There is no universal parity constraint" (DPC:107); withdrawn 2026-09-08 in `6cb0d2c`; OBS:304-305 (2026-09-26) still calls it open | argument | prose only |
| ED-32 | Joyce (Z/2)^3 orbifold as Y7 | internal | TTA:124 | SR:10 | in-force | seed_43_joyce adopted (DPC:110); the option text still argues (4, 24) (g2_forms.py:201-212), fork notes carry the D-023 reading (g2_forms.py:190-194) | ruling | g2_construction:joyce_orbifold |
| ED-33 | b2 = 7, pair (7,24) ("Joyce 1996 has (7,24)") | topology-number | TTA:124 | DPC:108 | retired | UNREACHABLE per `adf0081` (DPC:108) | computed-number (Joyce enumeration, `adf0081`) | no option (proposed seed_7_24_joyce_b2_seven) |
| ED-34 | Joyce (4,24) | topology-number | DPC:109 | DPC:109 | retired | UNREACHABLE (`adf0081`); b3 = 7 mod 12 (`d45b799`) | computed-number (`adf0081`) | no option |
| ED-35 | b3 = 24 as an input | topology-number | CL:824 | DPC:110 | superseded | superseded by `bf60005` (DPC:110) | ruling | b3_seed:seed_24 / b3_origin:input_24 (seed.py:48-50, 263-264) |
| ED-36 | (15,24) via the (0,16) profile | topology-number | DPC:111 | DPC:111 | withdrawn | WITHDRAWN_A1_MODEL_MISAPPLIED (DPC:111) | argument | no option (proposed seed_15_24_a1_misapplied) |
| ED-37 | A1 contribution table used outside its domain | topology-number | DPC:112 | DPC:112 | withdrawn | none quoted | argument | no option (joyce_contribution_table:absent adopted / supplied switches a cited table, not the A1 domain; g2_forms.py:18-75) |
| ED-38 | Joyce b3 = 7, 19, 31 (n_gen 0, 1, 2) | topology-number | DPC:113 | SR:10-24 | retired | DISABLED (`d45b799`, `f289f94`) | computed-number (n_gen = b2/4) | b3_seed:seed_7_joyce / seed_19_joyce / seed_31_joyce |
| ED-39 | (b2,b3) = (12,43), b3 = 7 + 3 b2 | topology-number | DPC:110 | SR:10 | in-force | "Author ruling 2026-09-22: the active path matches the found solution" (`bf60005`) | ruling | b3_seed:seed_43_joyce / b3_origin:derived_joyce_a1 (seed.py:95-96, 249-250) |
| ED-40 | Half-shift parity refutation of b3 = 24 | topology-number | `aa1bf5b` (2026-09-13) | DPC:114 | withdrawn | incomplete coverage (DPC:114) | argument | prose only |
| ED-41 | b3 = 24 from arc flag 12 x 2 | topology-number | DPC:120 | DPC:120 | unknown | NUMERICAL (DPC:120) | none | b3_origin:arc_flag_stabiliser |
| ED-42 | b3 = 24 from the D4 root shell | topology-number | DPC:121 | DPC:121 | unknown | NUMERICAL (DPC:121) | none | b3_origin:d4_root_shell |
| ED-43 | Joyce twisted sector, 7 flat + 17 twisted | topology-number | DPC:122 | DPC:122 | unknown | INERT (DPC:122) | none | b3_origin:joyce_twisted_sector |
| ED-44 | "Betti survey: b3 = 24 IS realizable" | topology-number | OBS:51 (`949725f`) | OBS:298 | superseded | SUPERSEDED (OBS:298) | none | prose only |
| ED-45 | n_gen = b3/8 | generations | CL:824 | DPC:115 | superseded | abandoned by `bf60005` (DPC:115) | ruling | n_gen_source:b3_over_dim_O |
| ED-46 | n_gen = chi_eff/48 | generations | DPC:116 | DPC:116 | refuted-by-argument | fails on the family (`3ba5848`); "Under D-009 it survives as n_gen = chi_eff/48 = n with the K3 reading" (seed.py:206-207) | computed-number (`3ba5848`) | n_gen_source:chi_eff_over_48 |
| ED-47 | n_gen = chi_eff/(2 b3), display fix | generations | CL:689 | OBS:125 | superseded | "UNRULED route; the ruled route is b_2/4" (fermion_generations.py:601, via OBS:289) | ruling | no option |
| ED-48 | n_gen = chi_eff/(4 b3) | generations | CL:689 | DPC:119 | superseded | suspect notation (DPC:119) | argument | no option |
| ED-49 | n_gen = b2/4 = 3 | generations | DPC:110 | SR:10 | in-force | none | ruling | n_gen_source:b2_over_faces |
| ED-50 | n_gen = 3 twice over: Leech 24 = 8+8+8, q+1 = 3 | generations | CL:201 | CL:201 | unknown | none | argument | prose only |
| ED-51 | chi_eff = 6 b3 | topology-number | DPC:117 | DPC:117 | refuted-by-argument | identical to b3/8 (DPC:117) | argument | prose only |
| ED-52 | Three chi_eff = 144 routes as corroboration | topology-number | PRM:77 | DPC:118 | refuted-by-argument | route A is a CY3 Euler characteristic, a type error (DPC:118); "Their agreement is the definition of their crossing point, not evidence" (`3ba5848`) | argument | chi_eff_route:seed_dependent (DISABLED; fork RULED to k3_reading 2026-10-01, g2_metric.py:111-123, 197-218) |
| ED-53 | chi_eff = 144 = b3^2/4 frozen constant (462.25 at 43) | topology-number | CL:824 | SR:206-211 | unknown | none | none | chi_eff_route:constant_144 |
| ED-54 | chi = 72 from h31 vs chi_eff 144 (CY-fourfold language) | topology-number | CL:824 | PRM:77 | refuted-by-argument | listed as C-1 inconsistency (PRM:77) | argument | prose only |
| ED-55 | 7D V7 vs "8-dimensional" vs "9D G2 x T^2" internal space | internal | PRM:78 | PRM:78 | refuted-by-argument | listed as C-1 inconsistency (PRM:78) | argument | prose only |
| ED-56 | "14 roots per G2 -> 144 per shadow -> 288" | identity | PRM:119 | PRM:119 | refuted-by-argument | G2 has 12 roots (PRM:119) | argument | prose only |
| ED-57 | 288 = 125 + 163 (vs 135 + 153) | identity | CL:824 | CON:16 | in-force | literals carry derivation comments (CON:16) | none | prose only |
| ED-58 | dim J3(O) used as 125 | identity | PRM:118 | PRM:118 | refuted-by-argument | dim J3(O) = 27 (PRM:118) | argument | prose only |
| ED-59 | Spin(7) statements | internal | PRM:122 | PRM:122 | refuted-by-argument | listed as C-5 errors (PRM:122) | argument | prose only |
| ED-60 | "G2 is the only 7D structure" | internal | PRM:126 | PRM:126 | refuted-by-argument | stated false (PRM:126) | argument | prose only |
| ED-61 | d_ijk triple intersection on H^3 | topology-number | DPC:123 | DPC:123 | refuted-by-argument | degree 9 on a 7-manifold (`8e80d5f`) | argument | prose only |
| ED-62 | 24x24 lattice Gram as metric-free form | internal | DPC:124 | DPC:124 | superseded | retired for the 12x12x43 tensor (`8e80d5f`, `4a5cc68`); "Schur's lemma forces a shell form proportional to the identity" (`4a5cc68`) | argument | prose only |
| ED-63 | Quadratic contraction labelled Hitchin; cubic Hitchin | internal | DPC:127 | DPC:128 | superseded | label corrected in `e0ccf89`, `25681cb` (DPC:128) | argument | metric_construction:quadratic_contraction / hitchin_cubic |
| ED-64 | b2_flat = 0 citation | topology-number | DPC:129 | DPC:129 | withdrawn | false citation (`2888ead`) | argument | prose only |
| ED-65 | n_faces = 4 from h11 = 4 of TCS #187 | internal | CL:189 | CL:187 | superseded | forced by rainbow labelling instead (CL:173-189); h11 value "this repository labels FITTED" (policy.py:114-116) | argument | no option (face_genericity:generic, RULED, derives 4 instead; policy.py:120-140) |
| ED-66 | face_genericity.all | internal | DPC:152 | DPC:152 | superseded | superseded 2026-09-01 (DPC:152) | ruling | face_genericity:all |
| ED-67 | PSL(3,2) / Fano symmetry of the bridge join | internal | CL:205 | CL:205 | unknown | none | none | prose only |
| ED-68 | Cross-shadow coupling phi ^ F_A ^ F_B, 42 of 210 channels | gauge | CL:362 | OBS:307 (`225a7da`) | in-force | flat R^7 only; "flat R^7 only" (CL:391) | argument | prose only |
| ED-69 | C3 ^ F_A ^ F_B coupling | gauge | CL:401 | CL:406 | refuted-by-argument | degree 7 on a 13-manifold is malformed (CL:401-406) | argument | prose only |
| ED-70 | Smooth G2 gives U(1)^12 only; nonabelian source open | gauge | MAS:21 | MAS:62 | in-force | open; nonabelian_gauge_source fails under every option (MAS:21) | computed-number (master_ladder.report) | no option |
| ED-71 | Bulk E8 x E8 Yang-Mills in 26D (statement B) | action | MAS:31 | MAS:48 | retired | "No reason for a bulk E8xE8 in 26D" (MAS:31) | argument | action_bulk_sectors:e8xe8_ym (fork OPEN, `none` adopted; action.py:42-61) |
| ED-72 | F_4 flux, V_tor, KK tower bulk (statement D) | action | MAS:33 | MAS:33 | retired | "F_4 is an 11D M-theory object in a 26D bulk" (MAS:33) | argument | action_bulk_sectors:flux_f4 / kk_tower (action.py:53-54) |
| ED-73 | Pneuma action, Dirac mass and (Psi-bar Psi)^2 (statement A) | action | MAS:30 | MAS:35 | retired | "m and lambda vanish for a Weyl spinor" (MAS:30) | argument | action_bulk_spinor:dirac (adds psi_mass and psi_quartic; action.py:70-73) |
| ED-74 | Two-layer OR action (statement C) | action | MAS:32 | MAS:32 | retired | "V_bridge, V_face, OR, ln Vol dt undefined" (MAS:32) | argument | no option |
| ED-75 | master-action-27d (statement E) | action | MAS:34 | MAS:34 | retired | cites the withdrawn D_crit = 26 argument (MAS:34) | argument | no option (id retired) |
| ED-76 | Master action R^2 and SUSY statements | action | PRM:166 | PRM:167 | refuted-by-argument | listed as M-4 contradictions (PRM:166-167) | argument | prose only |
| ED-77 | Racetrack vacuum Re(T) = 37.8527 | cosmology | CL:697 | MAS:23 | retired | "Not a relocated minimum, a deleted one" (DPC:138) | ruling | re_t_adoption:computed_vacuum |
| ED-78 | Kahler-Ricci running Re(T) sector | cosmology | CL:347 | CL:353 | retired | frozen; AUTHOR RULING 2026-08-23 (CL:347) | ruling | prose only |
| ED-79 | Kahler moduli as quintessence (route 1) | cosmology | DPC:151 | DPC:151 | refuted-by-argument | mass ratio 7.1e44 (DPC:151) | computed-number (ratio) | prose only |
| ED-80 | T_i as b2 gauge kinetic functions / CY3 Kahler moduli | internal | DPC:150 | DPC:150 | unknown | none | none | moduli_indexing:b2_gauge / cy3_shadow |
| ED-81 | w0 = -(n-1)/n with n = b2 = 4 | cosmology | `fbd320e` (2026-09-06) | DPC:130 | refuted-by-argument | ruled out on physics 2026-09-06, ratio 7.1e44 | computed-number (ratio) | dark_energy_betti:b2_4 |
| ED-82 | w0 with n = 3 / 6 / 12 / 8 / live b3 | cosmology | DPC:131 | SR:140-146 | unknown | n = b2 = 12 coincides with bridges_12 (SR:146) | none | dark_energy_betti:ngen_3 / chi_over_b3_6 / bridges_12 / octonion_8 / b3_live |
| ED-83 | w0 = -0.8528, thermal time alpha_T = 4.5 | cosmology | DPC:132 | DPC:132 | retired | retired pre-DESI (DPC:132) | data (pre-DESI) | prose only |
| ED-84 | alpha_T = 27/10 | cosmology | PRM:109 | PRM:411 | superseded | circular (PRM:109); relabelled STRUCTURAL (PRM:411) | argument | prose only |
| ED-85 | wa = -4/sqrt(b3) | cosmology | PRM:404 | DPC:133 | retired | "do not resurrect" (DPC:133); "post-DESI graft -> kept as RETRODICTED variant" (CV:128-129) | ruling | no option (formula variant cosmology.wa_projection_x4, CV:124-125) |
| ED-86 | wa = +0.1 / +0.27 | cosmology | DPC:134 | DPC:134 | superseded | "DESI prefers wa < 0" (DPC:134) | data (DESI) | prose only |
| ED-87 | wa = -1/sqrt(b3) canonical | cosmology | PRM:404 | PRM:24 | in-force | 2026-08; none | none | prose only |
| ED-88 | w0 = -23/24 (tzimtzum) vs thawing -42/43 | cosmology | SR:206 | cosmology.py:247-291 | in-force | -23/24 adopted, fork RULED (cosmology.py:241, 267); -42/43 is b3_live, "NOT ADOPTED" (cosmology.py:276) | ruling | dark_energy_mechanism:thawing_quintessence / dark_energy_betti:b3_24 (adopted) / b3_live |
| ED-89 | n_s = 0.9996 from Re(T) slow roll | cosmology | RA:159 | DPC:135 | falsified | 8.3 sigma, Planck 2018 (DPC:135) | data (Planck 2018) | spectral_index_route:re_t_slow_roll |
| ED-90 | n_s = 0.9636 = 1 - 2 phi^2/chi_eff | cosmology | RA:159 | cosmology.py:40-48 | in-force | adopted, fork RULED (D-022, cosmology.py:25-33) | ruling | spectral_index_route:golden_modulated |
| ED-91 | H0 = 76.34 Ricci flow; 70.42 sterile | cosmology | DPC:136 | DPC:136 | superseded | superseded (DPC:136) | none | h0_route:ricci_flow |
| ED-92 | Mirror dark energy from the shadow | cosmology | CL:713 | CL:758 | refuted-by-argument | 10^13 too small (CL:713-758) | computed-number (shadow derivation) | prose only |
| ED-93 | sin2 theta_W = 0.23190 geometric | particle | RA:299 | DPC:137 | falsified | 17.1 sigma FAIL under cited_only (DPC:137); "0.68 sigma with its 0.001 theory uncertainty" (CV:403-405) | data (cited PDG value) | no option (registered row gauge.sin2_theta_w_geometric, CV:408) |
| ED-94 | theta13 = asin(1/6) = 9.594 deg | particle | RA:66 | PRM:28 | falsified | about 9 sigma, NuFIT 6.0 (DPC:140) | data (NuFIT 6.0) | no option (proposed theta13_route) |
| ED-95 | theta13 = 8.54 deg "0.4 sigma" | particle | CL:75 | CL:80 | withdrawn | NuFIT restated (CL:75-80) | argument | prose only |
| ED-96 | QLC lambda_C/sqrt2; gaugino_cabibbo; lambda = exp(-pi/2) | particle | DPC:141 | DPC:143 | falsified | 5.3, 25.6-344.7, 25.5 sigma (DPC:141-143) | data (PDG CKM) | prose only |
| ED-97 | sin^2 2theta = 1/b3 sterile mixing | particle | CL:241 | DPC:144 | falsified | excluded by IceCube / MINOS+ 2024 (DPC:144) | data (IceCube, MINOS+) | no option (proposed sterile_mixing_route) |
| ED-98 | v25 flavour ansatz at b3 = 24 (T4 / 24-cell PMNS) | particle | CL:641 | MAS:56 | retired | "a calibration at the off-path seed b3 = 24" (MAS:56) | computed-number (delta chi2 -1,158) | flavour_seed_coupling:calibrated_24 |
| ED-99 | theta12 triality 35.26 vs 33.59 | particle | PRM:296 | PRM:305 | unknown | none | none | prose only |
| ED-100 | alpha^-1 geometric | particle | PRM:152 | DPC:149 | falsified | 449.6 at b3 = 43 (DPC:149) | ruling | prose only |
| ED-101 | m_mu/m_e ~ chi_eff = 144 | particle | RA:319 | RA:319 | falsified | actual 206.8 (RA:319) | data (PDG) | prose only |
| ED-102 | Sum m_nu: 0.1020 / 0.0605 / 0.0425 eV | particle | RA (0.0598/0.0817/0.0994) | MAS:57 | in-force | 0.0605; "only one of the three ... inside the window" (MAS:57) | data (DESI DR2 + CMB, oscillation floor) | prose only |
| ED-103 | Twelve external closures (Golay Lambda, Vol(S^5), ...) | identity | CL:281 | DPC:146 | falsified | 9 of 12; candidate closure gate (CL:281-308) | computed-number (candidate_closure_gate) | prose only |
| ED-104 | "24 = b3" in bc ghost, Leech, eta^-24 | identity | OBS:250 | DPC:148 | superseded | rewired to D_space_24 (`bf60005`) | argument | prose only |
| ED-105 | 168 signature swaps | identity | PRM:414 | PRM:414 | unknown | none | none | prose only |
| ED-106 | Landscape 10^33 -> 10^24 | cosmology | CL:698 | CL:699 | unknown | none | none | prose only |
| ED-107 | 26D -> 13D boundary variation | bulk | FUT:43 | FUT:43 | never-implemented | not started (FUT:43) | none | prose only |
| ED-108 | Discrete exterior calculus on compact G2 at b3 = 24 | internal | FUT:94 | FUT:107 | never-implemented | contingent on the TCS obstruction (FUT:94-107) | argument | prose only |
| ED-109 | 43 scalar zero modes from 13D -> 6D | particle | MAS:21 | MAS:62 | in-force | open; "the child declares none" (MAS:21) | computed-number (master_ladder.report) | no option |
| ED-110 | 16,763 dead V19 lines | other | CL:447 | FUT:116 | retired | reviving them is an author ruling (FUT:116) | ruling | prose only |
| ED-111 | b2 + b3 = 55 series, (8,47) to (16,39), from the (8,8) profile | topology-number | `adf0081` (2026-09-14) | `d45b799` (2026-09-15) | superseded | "Every reflected family vanishes, because the reflected ones WERE the non-A1 ones" (`d45b799`) | argument | no option |
| ED-112 | Epsilon-dichotomy: both resolutions available per reflected family | topology-number | `adf0081` | `d45b799` | retired | "That removes the epsilon-dichotomy assumption entirely" (`d45b799`) | argument | no option |
| ED-113 | A1 admissibility: every singular component has transverse group {+-1}; 446,964 -> 411,488 assignments | topology-number | `d45b799` | `d45b799` | in-force | "pairwise-disjointness is necessary but not sufficient, and every component must also be A1" (`d45b799`) | computed-number (derived_contribution_table) | prose only |
| ED-114 | Non-A1 (order 4 and 8) components resolved another way, McKay classes | internal | `300f66f` | `d45b799` | never-implemented | "not excluded, but it is not Joyce's, carries no G2 guarantee" (`d45b799`) | argument | no option |
| ED-115 | 3 + 4 split of the seven flat 3-forms mirrors 3 singular + 4 free involutions of Gamma | identity | `4a5cc68` | `4a5cc68` | unknown | "What was not put in and came out anyway" (`4a5cc68`) | computed-number (intersection_tensor.py) | prose only |
| ED-116 | 12 x 12 x 43 integer tensor H^2 x H^2 x H^3 as the metric-free cubic invariant | topology-number | `8e80d5f` (2026-09-21) | `4a5cc68` | in-force | "uniquely the available metric-free cubic invariant" (`8e80d5f`) | computed-number (multilinear_degree_audit.py, intersection_tensor.py) | prose only |
| ED-117 | Topological bilinear form on H^3 alone | topology-number | `8e80d5f` | `8e80d5f` | refuted-by-argument | "3 + 3 = 6 /= 7, so there is no topological bilinear on H^3 alone" (`8e80d5f`) | argument | prose only |
| ED-118 | phi with all (+1) signs on the Fano triples: split G2*, Hitchin B signature (4,3) | internal | `25681cb` (2026-09-21) | g2_forms.py:119-135 | superseded | "The compact form (octonion_derived) is the active path" (g2_forms.py:84-86, D-015 2026-10-01) | ruling | g2_form_convention:all_plus_one |
| ED-119 | phi signs read off the framework's octonion product: compact G2, signature (7,0) | internal | `25681cb` | g2_forms.py:137-176 | in-force | "All 807 published parameters were compared ... none moved" (g2_forms.py:151-153) | ruling | g2_form_convention:octonion_derived |
| ED-120 | dim ann 14 vs 6 as the test of a G2 form | internal | g2_forms.py:91-100 | `e0ccf89` | refuted-by-argument | "both real forms have 14-dimensional GL(7) stabilisers" (`e0ccf89`) | argument | prose only |
| ED-121 | Three generations as the selector: b3 = 7 + 3 b2, n_gen at most 3, attained only at (12,43) | generations | `3ba5848` (2026-09-22) | `f289f94` (2026-09-23) | in-force | "Three generations is the maximum this construction admits" (`3ba5848`) | computed-number (generation_selection.py) | b3_seed:seed_43_joyce |
| ED-122 | chi_eff = 2 x sum chi(K3) over singular involutions = 48 n, 144 at n = 3 (D-009) | topology-number | g2_metric.py:115 (2026-10-01) | g2_metric.py:149-166 | in-force | "the K3 reading of D-009 is adopted" (g2_metric.py:115-116) | ruling | chi_eff_route:k3_reading |
| ED-123 | n_gen = chi_eff_sector/24 (72/24); earlier chi/2 for 8D manifolds | generations | seed.py:186-196 (2025-11-22 per record) | seed.py:197 | superseded | "kept as the sector-level formula in v20.1" (seed.py:192-193); status disabled | none | n_gen_source:chi_over_24 |
| ED-124 | n_s = 1 - 2/b3 (0.9167 at b3 = 24) | cosmology | cosmology.py:50-56 | cosmology.py:60 | superseded | "11.48 sigma off; replaced 2026-01-10" (cosmology.py:54) | data (dataset not named in the record) | spectral_index_route:one_minus_2_over_b3 |
| ED-125 | H0 shifted by KK modes acting as early dark energy | cosmology | cosmology.py:114-117 | cosmology.py:124 | refuted-by-argument | "lightest KK mass ~5e28 eV vs ~1e-28 eV needed, ~57 orders off" (cosmology.py:119-120) | computed-number (hubble_tension.HubbleTensionEDE) | h0_route:kk_bridge |
| ED-126 | H0 = Planck x golden-angle correction, one variable | cosmology | CV:258-261 | CV:258-261 | falsified | "lands 3.5 sigma from SH0ES and 18.6 from Planck" (CV:259-261) | data (SH0ES 2022, Planck) | no option |
| ED-127 | H0 = 288/4 - 163/144 + eta_S (O'Dowd composite) as display value; "Hubble tension resolved" claims retired | cosmology | CV:257-266 | cosmology.py:92-100 | in-force | "H0 is NOT a topology-first prediction" (CV:258-259) | ruling | h0_route:odowd_composite |
| ED-128 | w0 = -(D-1)/(D+1) = -11/13 at D = 12, maximum entropy production | cosmology | cosmology.py:157-158 | cosmology.py:165 | superseded | "replaced 2025-12-31 by thawing quintessence" (cosmology.py:161) | data (DESI 2025, 1.76 sigma) | dark_energy_mechanism:mep_11_13 |
| ED-129 | theta13 from the neutrino_mixing arcsin form, 8.6473 deg | particle | CV:340-346 | CV:372-373 | withdrawn | "theta_13 is NOT predicted by this framework" (CV:347-348, ruling 2026-08-20) | computed-number (6243 closed forms: 143 in window, ~53 by chance) | no option |
| ED-130 | theta13 via modular flavour symmetry, or the TCS-neck T^2 modulus | particle | CV:361-370 | CV:361-370 | never-implemented | "modular flavour symmetry needs an SL(2,Z) acting on a COMPLEX modulus" (CV:366-367) | argument | prose only |
| ED-131 | lambda_Cabibbo = exp(-3/2) | particle | CV:381-386 | CV:384 | in-force | none (status TOPOLOGY_CANDIDATE, CV:384) | none | prose only |
| ED-132 | M_KK = 4.5 TeV, warped exponential M_Pl_red exp(-k_eff pi) | particle | CV:440-445 | CV:440-449 | in-force | none (status PREDICTED vs LHC 3.5 TeV bound, CV:443-445) | none | prose only |
| ED-133 | Three GUT scales named apart: RG 2.118e16, geometric 6.325e15, threshold 1.24e17 GeV | gauge | CV:427-437 | CV:438 | in-force | "Three distinct scales were being conflated" (CV:433) | ruling | prose only |
| ED-134 | Nahm objection: one time with D > 11 forbidden, so 13D (12,1) shadows are excluded | shadows | CV:469 (2026-08-20) | CV:469 | unknown | "Nahm's theorem excludes 13D with signature (12,1)" (CV:469) | argument | prose only |
| ED-135 | Time current as an entropy direction, not a coordinate (escape from Nahm) | time | CV:469 | CV:469 | never-implemented | "unpublished and would have to be made precise" (CV:469) | argument | prose only |
| ED-136 | Frobenius-Schur test: quaternionic x quaternionic = real, so (24,2) (complex) fails | bulk | CV:468 | CV:466 | unknown | "Recorded, not resolved" (CV:466, ruling 2026-08-31) | argument | prose only |
| ED-137 | R_perp^2 = -I forced by symplectic Cl(12,1) spinors; read as a Tomita-Takesaki conjugation J | other | CV:468 | CV:468 | unknown | none | argument | prose only |
| ED-138 | Two 14D (13,1) shadows from II_26,2 = Leech + U + U; 14 = dim G2 | shadows | `95362a7` (2026-08-20) | g2_forms.py:360-362 | never-implemented | "14 - 7 = 7 breaks the descent" (g2_forms.py:362) | argument | no option (named in bulk_signature:26_2) |
| ED-139 | Spinor factorisation: Dirac Cl(26,2) 16384 = 128 x 128, Weyl 8192 = 64 x 64 x 2 | action | `95362a7` | CV:468 | never-implemented | tied to (26,2), not adopted (CV:466) | argument | no option |
| ED-140 | Hohn-Mason rank-12 splits of Leech: orbit 4 (K_12, glue 3^6), orbit 5 (sqrt2 D_12+, glue 2^12), orbit 3 | lattice | `95362a7` | CV:468 | never-implemented | "Treating the halves as independent sectors discards it" (`95362a7`) | argument | prose only |
| ED-141 | Leech as 12 x 2 (C), 6 x 4 (H), 3 x 8 (O); no 3-dimensional division algebra | lattice | CV:468 | CV:468 | unknown | "there is no algebraic route to 'groups of 3'" (CV:468) | argument | prose only |
| ED-142 | b3 = 2 (h11 - h21 + h31)/6 as the generating formula | topology-number | CV:469 | CV:469 | refuted-by-argument | "not a theorem in G2 geometry" (CV:469) | argument | prose only |
| ED-143 | Extra-twisted connected sum (Nordstrom 1809.09083) as Y7 | internal | `949725f` (2026-08-20) | CV:469 | never-implemented | "published ETCS examples are nearly all 2-connected with b3 >= 42" (`949725f`) | argument | no option |
| ED-144 | Nearest Joyce pairs to (4,24): (4,27), (5,26), (4,19) | topology-number | `949725f` | CV:469 | never-implemented | none | none | no option; (4,19) is b3_seed:seed_19_joyce |
| ED-145 | Joyce mod-4 grid: b2 + b3 = 3 mod 4 for 239 of 252 examples | topology-number | CV:469 | CV:469 | unknown | none | argument | prose only |
| ED-146 | b2 = 7 read as the 7 Fano lines, 3 per point | internal | `949725f` | g2_forms.py:234-235 | withdrawn | "the b2 = 7 proposal built on one is dropped" (g2_forms.py:234-235) | argument | prose only |
| ED-147 | Cross-shadow coupling through the metric channel L1 L2 cos(theta) | gauge | `225a7da` (2026-08-22) | `225a7da` | refuted-by-argument | "identically zero at the stabilised vacuum" (`225a7da`) | computed-number (topological_terms.py) | prose only |
| ED-148 | Four T_i as 4 clusters of the 24 lattice coordinates read as 3-cycles | internal | g2_forms.py:263-266 | g2_forms.py:285-292 | in-force | adopted; "STALE ON THE ACTIVE PATH: the 3-cycle reading needs b3 = 24" (g2_forms.py:285-286) | argument | moduli_indexing:b3_clusters |
| ED-149 | Bulk Planck exponent n = 23 or 25 in M*^n R | action | action.py:83-86 | action.py:83-86 | refuted-by-argument | "the dimension check on the R term fails" (action.py:84, 86) | computed-number (master_ladder) | action_planck_exponent:exponent_23 / exponent_25 |
| ED-150 | Mostly-minus metric with the audit's Lagrangian signs | action | action.py:96-98 | action.py:96-98 | refuted-by-argument | "the weak-field sign check reports FAILS (found by E1)" (action.py:97-98) | computed-number (master_ladder) | action_sign_convention:mostly_minus |
| ED-151 | +2 read as a lightcone pair (one space + one time) | time | CV:467 | CV:466 | unknown | "the only self-consistent reading is 'one time per shadow'" (CV:466) | ruling | prose only |
| ED-152 | T^7 coordinates = the 7 non-trivial characters of (Z/2)^3; flat (b1,b2,b3) = (0,0,7) | topology-number | `2888ead` (2026-09-21) | `2888ead` | in-force | "Everything in the flat sector follows from that single fact" (`2888ead`) | computed-number (joyce_orbifold.py) | prose only |
| ED-153 | Weyl anomaly c = b3 + 2 - 26 = 24 + 2 - 26 = 0 as ghost freedom ("Guardian" unitary filter, legacy (24,1) count with Euclidean bridge) | time | unitary_filter_legacy.py:3, 28-34 | unitary_filter_legacy.py:551 (still runs; DPC:266-270) | retired | "RETIRED (signature ruling 2026-08-31) ... ghost control of the second time is OPEN" (unitary_filter_legacy.py:16-20) | ruling | no option (proposed ghost_control.bars_sp2r_appeal, DPC:266) |
| ED-154 | Dual 13D (12,1) shadows with a shared time from an OR reduction via the R_perp operator | shadows | unitary_filter_legacy.py:36-38 | unitary_filter_legacy.py:36-39 | retired | "RETIRED (signature ruling 2026-08-31): an earlier framework produced the dual 13D(12,1) shadows with a shared time" (unitary_filter_legacy.py:36-37) | ruling | no option |
| ED-155 | alpha_T = D_bulk/D_string = 26/10 = 2.6 (replaces 27/10) | cosmology | `0fb9a1e` (2026-08-19) | thermal_time.py:18-28 | in-force | "the factor 2 in gamma is now a literal dimension count (D_time = 2)" (`0fb9a1e`); "alpha_T=2.6 whose derivation is not provided" (moduli_dm_coupling.py:482) | argument | prose only |
| ED-156 | Distributed OR reduction over 12 bridge pairs, rank 2^12 = 4096, matched to the Weyl spinor of Cl(24,2) | identity | `31e2568` (2026-08-31) | `31e2568` | in-force | "now because two independently-derived quantities agree rather than because a literal was restated" (`31e2568`); at (26,2) Weyl 8192 and the check goes False | computed-number (compute_distributed_or_reduction) | prose only |
| ED-157 | Quintessence as a shift-symmetric C3 axion counted by b3 (Route 1 closed for b3, against b2) | cosmology | `fbd320e` (2026-09-06) | cosmology.py:247-267 | in-force | "the quintessence direction has to be shift-symmetry protected, which is a C3 axion counted by b3" (`fbd320e`) | computed-number (geometry.kahler_over_quintessence_mass, 7.1e44) | dark_energy_betti:b3_24 |
| ED-158 | G2 holonomy forces b2 = 0 (appendix_p, "no harmonic 2-forms") | topology-number | `fbd320e` | `6cb0d2c` (2026-09-08) | refuted-by-argument | "holonomy exactly G2 ... constrains b2 not at all" (`fbd320e`); "Therefore b_2 = 0 [does not follow]" (`6cb0d2c`) | argument | prose only |
| ED-159 | k_gimel = 12 + 1/pi exactly, so a_i T_i = k_gimel on every face | identity | `fbd320e` | cosmology.py:299-303 | in-force | "Incidentally k_gimel = 12 + 1/pi exactly, which is what makes a*T constant" (`fbd320e`) | argument | prose only |
| ED-160 | omega_dm_geometric two ways: sterile_ratio x 0.48 = 0.2717 vs sterile_ratio x omega_m x 0.85 = 0.152 | cosmology | `fbd320e` | `fbd320e` | unknown | "Both are labelled rather than one deleted" (`fbd320e`) | none | prose only |
| ED-161 | Leech lattice supplies KNP axion alignment (generator-row Q, 11/12 ratio) | lattice | `6cb0d2c` | `6cb0d2c` | refuted-by-argument | "the lattice contributes no enhancement at all" (`6cb0d2c`); shell Q proportional to the identity | computed-number (compute_axion_alignment_from_shell) | prose only |
| ED-162 | Four-face moduli T_i = b3 k_gimel/(i pi) as racetrack-stabilised VEVs; minimising abs(W)^2 as a proxy | cosmology | `6cb0d2c` | `6cb0d2c` | refuted-by-argument | "It is not a stationary point" (norm of grad V = 4.4e-06); "the four-face moduli are an ansatz" (`6cb0d2c`) | computed-number (bridge_geometry.racetrack_potential) | prose only |
| ED-163 | Obtuse bridge angles allowed, theta up to 174 deg (pi - 0.1) | other | `2c6da17` (2026-08-21) | bridge_geometry.py:368-374 | retired | "an obtuse bridge carries a NEGATIVE coupling and is a ghost mode" (bridge_geometry.py:369-370); bound pi/2, OBS:110 | argument | no option |

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

## 6. Second pass (2026-11-11)
First half of section 5 (entries 1-4); entries 5-8 belong to the next agent.
- G1 (CHANGELOG at the root): closed, no idea there; a location note, the root file was read in the first pass.
- G2 (cited commits not opened): closed. `adf0081`, `bf60005`, `8e80d5f`, `95362a7` and the other ten hashes the rows cite (`300f66f`, `d45b799`, `4a5cc68`, `25681cb`, `e0ccf89`, `2888ead`, `3ba5848`, `f289f94`, `949725f`, `225a7da`) opened by stat and message; `95362a7` and `949725f` touch only canonical_values.py, read under G3. Added ED-111 to ED-121, ED-138 to ED-140, ED-143, ED-144, ED-146, ED-147, ED-152; corrected ED-39 (reason), ED-52 (reason), ED-62 (reason). `bf60005` and `f289f94` otherwise confirm ED-35, ED-45, ED-49, ED-104; their pipeline parts (seed-blind writers, 68-formula publishing gap, cp1252 printing) are tooling, no rows. Simulation code hunks of these commits not paged (the messages state the change). Pipeline hashes `654939e`, `1f7935e`, `bfff33e` not opened (tooling).
- G3 (CANON entries): closed. Opened CV:60-170 and CV:255-550 (w0, wa, H0, tau_p, alpha_leak, theta13, lambda_C, sin2 theta_W, sum m_nu, M_GUT, M_KK, n_s, bulk ruling, challenge, resolution evidence, tcs_obstruction, root_split_288, policy rows). CANON["bulk"]["superseded"]["27"] and ["25"] (CV:497-506) agree with ED-02 and ED-03. Added ED-126, ED-127, ED-129 to ED-137, ED-141, ED-142, ED-145, ED-151; corrected ED-15 (fate in-force per the 2026-08-19 ruling note), ED-85, ED-93. CV:170-255 (H0 entry head, helpers) and CV:1-60 not read; tau_p, alpha_leak and policy-row superseded keys are misquotes and drift, no rows. Not added: CV:425 sum m_nu IO 0.0994 TENSION, already ED-102's value set.
- G4 (`today` column): closed. Every fork:option id in the rows matched against a grep of id= and status= over catalogue/*.py; option records read for action.py (all four forks), algebra.py:13-72, cosmology.py:20-170, g2_forms.py:15-383, g2_metric.py:100-221, policy.py:100-152, seed.py:120-214, plus summaries of the dark_energy_betti, re_t_adoption, flavour, b3_seed, b3_origin and metric_construction options. Corrected ED-35, ED-37, ED-46 (reason), ED-52, ED-65, ED-71, ED-72, ED-73, ED-90 and the era summary (chi_eff_route RULED 2026-10-01); added ED-122 to ED-125, ED-128, ED-148 to ED-150. Left: full records of b3_seed (seed.py:20-118), b3_origin (215-324), seed_selection (325-370), re_t_adoption (cosmology.py:169-237), dark_energy_betti (238-360) and twisted_norm_convention (g2_metric.py:222-290) not read in full; ids, status and summaries match the rows.
- Format: the fate qualifiers of ED-16, ED-68, ED-70, ED-78, ED-87, ED-102, ED-103, ED-109 moved to the reason column, so every fate is one vocabulary word.

Second half of section 5 (entries 5-8):
- G5 (DPC:191-311 proposed DISABLED options): closed. Re-read DPC:191-311; a grep of variants/ for all 16 proposed fork and option ids (bulk_formulation, sampler_pair_27d, physics_core_24_1, ghost_control, bars_sp2r_appeal, plus_two_reading, euclidean_bridge, two_sp2r, sterile_mixing_route, torsion_one_over_b3, theta13_route, qlc_lambda_c_over_root_two, leech_generator, pre_2026_09_07, seed_15_24_a1_misapplied, seed_7_24_joyce_b2_seven) finds none. Of the relabels proposed for existing options, none was applied: dark_energy_betti:b2_4, n_gen_source:b3_over_dim_O and g2_construction:fano_tcs carry no DISABLED status (DISABLED appears only at seed.py:64-86, cosmology.py:233, g2_metric.py:218); fano_tcs is REFUSED in its text (D-023). Followed the ghost_control evidence into unitary_filter_legacy.py:1-40. Added ED-153, ED-154; corrected ED-29, ED-32.
- G6 (rulings before 2026-09-14 with no git record): closed. The engine history has since been merged (209 main commits before 2026-09-14), so each ruling DPC:21-28 names now has a commit, and every doc date matches: 2026-08-19 bulk adoption `0fb9a1e`; 2026-08-31 signature ruling committed in `dca1fc1` (2026-09-01); 2026-09-06 dark_energy_betti `fbd320e`; 2026-09-07 Leech generator `1c88906`; 2026-09-08 lattice_24d, g2_construction, moduli_indexing forks `6cb0d2c`; 2026-09-13 g2_form_convention `32f6948` (confirms ED-118 to ED-120, no new row). Also opened `31e2568`, `aa1bf5b`, `2c6da17` (subjects name the spinor, b3 = 24 and the RP gate). Added ED-155 to ED-163 (ED-163 via `2c6da17` and OBS:110); corrected ED-01, ED-26, ED-40, ED-81 (first seen or citation), ED-88 (fate unknown -> in-force, today), ED-31 (reason), and the timeline rows of 2026-08-19, 08-31, 09-06, 09-07. Opened by message only; the code hunks were not paged. The 2026-08-25 RA rulings (`3baeb0a`) and the 2026-09-13 racetrack solve (`73010a4`) were not opened; ED-77 and the RA rows already carry them through the docs.
- G7 (pipeline sections given one summary line): closed, no idea in CL:462-560 (2.2.x: dispatcher, republish), CL:772-818 (2.0.x: Rust dispatch, CLI, build backend), CL:857-913 (1.3.x, 1.0.0: CI, datasheet API, licence) or CON:1-37 (merges, CI, release). OBS swept for model terms: OBS:110 holds the obtuse-bridge bound (ED-163); OBS:120 Golay [[24,12,8]] label is ED-28; OBS:125, 289-294 are ED-47 and ED-48; OBS:304-305 calls the TCS parity obstruction still open on 2026-09-26 (noted in ED-31); the rest is Firebase, paths and the beta_lambda second site, tooling.
- G8 (docs/history/): closed, no idea there beyond the first pass. docs/history/ still holds one file, RULINGS_ASSESSMENT_2026-08-25.md, read in full in the first pass.