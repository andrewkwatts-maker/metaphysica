# Lane site-issues: the site's issue register, closed archive and idea registers

Sources (`P` = `PrincipiaMetaphysica/docs/`): `OUTSTANDING_ISSUES.md` (index, split 2026-11-04),
`archive/OUTSTANDING_ISSUES_closed.md` (cited `arch:`), `issues/01..21` (cited `NN:`),
`ARXIV_IDEAS_REGISTER.md` (cited `arxiv:`). The register covers 2026-08-19 to 2026-09-30.
Quotes are verbatim unless marked `para:`, which means a paraphrase of the cited lines. Fork names in
`today` were checked against the variant catalogue in the second pass (section 6, gap 4).

## 1. Era summary

- **Start (2026-08-19, arxiv:3).** A 26D (24,2) bulk with two 13D (12,1) shadows and one time per shadow. G2 manifold, TCS #187, b2 = 4, b3 = 24, chi_eff = 144. n_gen = 24/8 = chi_eff/48.
- **Bulk (2026-08-31, 02:40-47).** Ruled to stay (24,2). D_crit = 26 and the Bars ghost-freedom appeal were withdrawn. The lattice obstruction (22 ≡ 6 mod 8) is unanswered.
- **Internal (2026-09-15 to 09-22).** b3 = 24 was found unreachable for Joyce T^7/(Z/2)^3. The construction became that orbifold resolved with Eguchi-Hanson: (b2, b3) = (12, 43), seed_43_joyce (19:1-16).
- **End (2026-09-30, arch:1405-1424, 1494-1502).** Bulk and shadows unchanged. n_gen = b2/4 = rank Γ = 3. b3 = 7 + 3·b2 is relabelled as holding for the all-plain subfamily only. chi_eff is unruled. The 24 is read as the bulk's spacelike core (19:20-22).
- **Open at the end (arch:1494-1502).** The real form of φ (compact recommended), Re(T) (an open modulus recommended), what selects (12,43) on the n = 3 line, chi_eff, and the demotion of the k_gimel layer.

## 2. Model timeline

| date | commit or file:line | old -> new | reason as recorded |
|---|---|---|---|
| 2026-08-19 | arxiv:3 | model statement: 26D (24,2), two 13D (12,1), G2 TCS b3 = 24 | none (baseline statement) |
| 2026-08-20 | 02:101-103 | 26d-signature formula (24,1) = 25 -> (24,2) = b3 + 2 | para: the formula disagreed with the stated signature |
| 2026-08-20 | 02:36-38 | bulk status STRUCTURAL -> STRUCTURAL_CHALLENGED | "challenged on three independent grounds" 02:36 |
| 2026-08-31 | 02:40-47 | bulk_signature OPEN -> RULED 24_2; D_crit = 26 and the Bars appeal withdrawn | "The bulk stays 26D at (24,2), shadows stay 13D(12,1), and nothing migrates." |
| 2026-09-05 | arch:511-538 | TCS framing -> Joyce orbifold proposed as the construction | "b₃ = 24 is far below that floor" arch:523-524 |
| 2026-09-06 | arch:561-597 | dark_energy_betti OPEN -> RULED: C3 axion (b3), not b2 = 4 | "A field stabilised at 24.6 TeV cannot be rolling today." arch:584-585 |
| 2026-09-06 | arch:630-641 | hardcoded b2 = 0 -> reads topology.b2 | "`b₂ = 0` was a false theorem" arch:630 |
| 2026-09-07 | 05:1-72 | lattice generator (not Λ24) -> true Leech; Leech found decorative | para: det 7,144,929, 12 norm-2 rows; no published number moved |
| 2026-09-09 | 07:127-195 | three shadows tested -> two shadows kept; three blocks adopted | "FALSIFIED as a shadow count, ADOPTED in substance as the block structure" 07:194-195 |
| 2026-09-09 | 08:94-156 | b3 = 24 derived -> b3 = 24 an input; Leech/bridge apparatus removable | para: the 7-layer survives, the 24-layer fails |
| 2026-09-13 | 10:121-214, 10:341-346 | parity refutation of b3 = 24 -> WITHDRAWN; b3 = 24 undetermined | "It is WITHDRAWN." 10:345 |
| 2026-09-14 | 11:202-222 | elder_kads GEOMETRIC:TCS_G2_187 -> INPUT:B3_ORIGIN_OPEN | para: ruling executed; three gated forks opened 11:224-242 |
| 2026-09-15 | arch:825-872 | (15,24) withdrawn -> b3 ≡ 7 mod 12; b3 = 24 unreachable; (12,43) reachable | "24 ≡ 0 (mod 12), so b₃ = 24 is UNREACHABLE." arch:870 |
| 2026-09-20 | 14:52-102 | φ assumed compact -> φ is the split form G2* (4,3) | para: octonion_derived is compact (7,0); the closure does not depend on it |
| 2026-09-21 | 16:7-85 | n_gen = b3/8 -> n_gen = b2/4 = rank Γ; three generations select (12,43) | para: three generations is the maximum and selects (12,43) |
| 2026-09-22 | 19:1-37 | b3_seed seed_24 -> seed_43_joyce; n_gen_source b2_over_faces | "The author directed that the active path match the found solution." 19:3-4 |
| 2026-09-30 | arch:1405-1424 | "b3 ≡ 7 mod 12", "b3 = 7 + 3b2" -> labelled all-plain subfamily; reachable lines b2 + b3 = 23, 39, 55 | "Nothing is deleted, and no computed number changed." arch:1414 |

## 3. Ideas

| id | idea | kind | first seen | last seen | fate | reason recorded | reason type | today |
|---|---|---|---|---|---|---|---|---|
| SI-01 | 26D bulk (24,2), two times, two 13D (12,1) shadows | bulk | arxiv:3 | 19:22 | in-force | "The bulk stays 26D at (24,2), shadows stay 13D(12,1), and nothing migrates." 02:41-42 | ruling | bulk_signature:24_2 |
| SI-02 | (25,1) 26D one-time bulk | bulk | 02:55, 02:68 | 07:288-290 | superseded | "(a) (25,1) 26D one-time — matches D_crit and the lattice, abandons two-time" 02:68 | ruling | bulk_signature:25_1 |
| SI-03 | (26,2) 28D two-time bulk | bulk | 02:56, 02:69 | 07:197-264 | superseded | "(b) (26,2) 28D two-time — matches Bars and the lattice, breaks b₃ + 2" 02:69 | ruling | bulk_signature:26_2 |
| SI-04 | D_bulk = D_crit = 26 = b3 + 2 | bulk | 02:57-62 | 19:35 | withdrawn | "D_crit = 26 is withdrawn (the two-time critical dimension is 27–28)" 02:44 | argument | prose only |
| SI-05 | Bars Sp(2,R) gauging for ghost-freedom of the two shadows | time | 02:63-66 | 01:242-247 | withdrawn | "Sp(2,ℝ) gauging gives one 24D shadow, not two 13D ones" 02:45-46 | argument | prose only |
| SI-06 | even self-dual lattice in the bulk signature | lattice | 02:52-56 | 07:170-176 | unknown | "the lattice obstruction (24 − 2 = 6 mod 8 ...) is unanswered" 02:46-47 | argument | prose only |
| SI-07 | three readings of the "+2" (lightcone pair, two-time + bridge, 2×Sp(2,R)) | time | 02:73-74 | 19:35-36 | unknown | "the "+2" carries three inconsistent readings ... At most one is right." 02:73-74 | argument | prose only |
| SI-08 | 25D (24,1) in the 26d-signature formula | bulk | 02:101-103 | 02:103 | superseded | para: the formula said (24,1), value 25; fixed to (24,2) | argument | no option |
| SI-09 | critical_dim computed as 27 | bulk | 02:116-117 | 19:28 | superseded | "critical_dim = 26 on both branches" 19:28 | computed-number (modular_invariance) | no option |
| SI-10 | three shadows of 8 space each (24 = 3×8) | shadows | 07:127-131 | 07:194 | falsified | "8 spatial dimensions cannot hold a 7D G₂ manifold plus 3 visible spatial dimensions" 07:166-167 | argument | no option |
| SI-11 | four shadows, 7D (6,1) each | shadows | 07:164 | 07:164 | refuted-by-argument | para: after G2(7), 0 dimensions left; "short by 4" 07:164 | argument | no option |
| SI-12 | three blocks inside one 24 (tri-sector), the E8 factors | lattice | 07:182-192 | 07:195 | in-force | "tri-sector, not tri-shadow: three blocks inside one 24" 07:190 | argument | lattice_24d:niemeier_e8x3 (not adopted; leech adopted, fork OPEN, algebra.py:14-56) |
| SI-13 | (24,3) tri-shadow signature | time | 07:174 | 07:179 | refuted-by-argument | "the tri-shadow signature inherits the current failure rather than repairing it" 07:178-179 | argument | no option |
| SI-14 | J3(O): 27 = 3 + 24 read as 3 times + 24 space | time | 07:148-150 | 07:150 | unknown | none (listed as favouring three shadows, not ruled) | none | prose only |
| SI-15 | Bars-Kounnas 27D at (25,2), 28D at (26,2) | bulk | 02:57-59 | 07:179-180 | refuted-by-argument | "27D total does not buy the critical dimension for a three-time reading" 07:179-180 | argument | no option |
| SI-16 | spare nodes as the "+2"; 13 + 13 + 2 with a shared 2 in neither shadow | shadows | 07:197-264 | 08:1-39 | unknown | para: candidate for bulk_signature 26_2, with an F2 -> R gap | argument | bulk_signature:26_2 |
| SI-17 | breathing portals: +1 total (25,1), +2 (26,2), +1 per face (28,4) 32D four-time | time | 07:266-312 | 08:1-39 | unknown | "None adopted" 07:308-312 | none | no option |
| SI-18 | II25,1 = Λ24 ⊕ II1,1: one time, hence one shadow | lattice | 07:288-290 | 07:290 | unknown | "one time, hence one shadow" 07:288-290 | argument | bulk_signature:25_1 |
| SI-19 | four faces as four axes; 2+2 face pairing | shadows | 07:314-339 | 08:1-39 | unknown | para: the 2+2 pairing is block-relative | argument | prose only |
| SI-20 | (8,6,6,6) asymmetric face clustering | shadows | 08:45-92 | arch:1053 | falsified | "8+6+6+6 = 26, so it partitions 26 while the Golay code lives on 24" arch:1046-1047 | argument | no option |
| SI-21 | (6+2,6,6,6): 4 faces × 6 + 2 on one face = D_bulk 26 | shadows | arch:1063-1082 | arch:1086-1092 | superseded | "Read as a partition of b₃, the structure is coherent only at seed_24" arch:1086 | argument | prose only |
| SI-22 | lattice generator presented as Λ24 | lattice | 05:1-72 | 05:45 | falsified | para: det 7,144,929 and 12 norm-2 rows; kept as `_FALSIFIED_GENERATOR_NOTE` 05:45 | computed-number (lattice generator) | lattice_24d:leech (adopted, fork OPEN, algebra.py:35-52) |
| SI-23 | Leech decomposes into three E8 | lattice | 05:151-167 | 05:167 | refuted-by-argument | para: Λ24 has no roots, so the decomposition cannot hold | argument | no option |
| SI-24 | Niemeier E8³ as the 24D lattice | lattice | 05:169-186 | 06:286-309 | unknown | para: recommended for adoption by author's ruling 05:220-241; 8 lattice-self test failures 06:286-309 | ruling | lattice_24d:niemeier_e8x3 (not adopted, algebra.py:55-56) |
| SI-25 | octonionic Leech (Wilson) for the bridges | lattice | 05:114-133 | 05:133 | refuted-by-argument | para: the coordinate-pair bridge is not G2-equivariant | argument | no option |
| SI-26 | bridges = (arc point, complement point); (face, E8 block) | lattice | 05:135-149 | 06:39-79 | refuted-by-argument | para: Approach 7 equivalent to Approach 2 and defeated; Approach 2 owes the factor 2 | argument | no option |
| SI-27 | 24 = 12 × 2 as structural | identity | 06:83-115 | 08:226-263 | withdrawn | "DISSOLVED: no structural 2 exists; it was index arithmetic" 06:115 | argument | b3_origin:arc_flag_stabiliser |
| SI-28 | 24 as the D4 root shell | topology-number | 08:265-291 | 11:224-242 | unknown | para: NUMERICAL only, recorded as a b3_origin candidate | computed-number | b3_origin:d4_root_shell |
| SI-29 | lower-symmetry Niemeier lattices (D24+, A1^24) | lattice | arch:1018 | arch:1029 | never-implemented | "swapping the lattice moved no published number" arch:1025-1026 | argument | no option |
| SI-30 | Leech deep-hole anchor with a kill condition | lattice | 16:233-244 | 18:39-70 | in-force | para: the kill does not fire; the cost is 24 parameters | computed-number | prose only |
| SI-31 | TCS G2 (#187) as the source of b3 = 24 | internal | arxiv:3 | 16:197-210 | refuted-by-argument | "b₃ = 24 is far below that floor" (71 ≤ b3 ≤ 155) arch:523-524 | argument | g2_construction:fano_tcs (REFUSED D-023, g2_forms.py:217-238) |
| SI-32 | Crowley-Nordström forces b2 + b3 odd for TCS | topology-number | arch:513-515 | arch:520 | withdrawn | "It says nothing about b₂ + b₃ parity." arch:520 | argument | g2_construction:fano_tcs (the withdrawal is in its record, g2_forms.py:230-235) |
| SI-33 | Joyce orbifold at (b2, b3) = (4, 24) | internal | arch:528-531 | 13:158 | refuted-by-argument | "UNREACHABLE. The g2_construction fork's adopted "Joyce (4,24)" claim cannot be realised" 13:158 | computed-number (Künneth enumeration) | g2_construction:joyce_orbifold (adopted; its (4,24) reading SUPERSEDED D-023, g2_forms.py:190-214) |
| SI-34 | b2 = 7, (7, 24) | topology-number | 05:309-321 | 13:159 | refuted-by-argument | "UNREACHABLE. The b₂ = 7 alternative falls the same way" 13:159 | computed-number (Künneth enumeration) | no option |
| SI-35 | parity theorem: every (Z/2)^3 Joyce orbifold has odd b3 | topology-number | 10:121-214 | 11:33 | withdrawn | "The parity prediction "every (Z/2)^3 Joyce orbifold has odd b_3" — WITHDRAWN." 11:33 | computed-number (enumeration, flaws 11:1-38) | prose only |
| SI-36 | TCS parity makes (4,24) inadmissible | topology-number | 05:348-361 | 06:177-193 | withdrawn | para: the parity claim is withdrawn together with the b2 = 7 proposal | argument | g2_construction:fano_tcs (the withdrawal is in its record, g2_forms.py:230-235) |
| SI-37 | b3 = 24 as a labelled input | topology-number | 11:202-222 | 19:1-9 | superseded | para: GEOMETRIC:TCS_G2_187 -> INPUT:B3_ORIGIN_OPEN 11:202-222 | ruling | b3_origin:input_24 (seed_24 only, not adopted, seed.py:239-264); b3_seed:seed_24 |
| SI-38 | (15, 24) reachable by Künneth | topology-number | 13:118-181 | arch:829 | withdrawn | "withdrawn when the stabiliser census showed the A₁ model applied outside its domain" arch:829-830 | computed-number (stabiliser census) | prose only |
| SI-39 | b3 = 7 + 3·b2, b3 ≡ 7 mod 12 as the family law | topology-number | arch:861-868 | arch:1410-1414 | withdrawn | "All of these are relabelled "all-plain subfamily". Nothing is deleted" arch:1413-1414 | computed-number (joyce_reachability) | b3_origin:derived_joyce_a1 (adopted; summary b_3 = 7 + 3 b_2, seed.py:249-260) |
| SI-40 | Joyce T^7/(Z/2)^3 at (12, 43), EH resolved | internal | 13:154-162 | 19:1-16 | in-force | "the active path match the found solution" 19:3-4 | ruling | b3_seed:seed_43_joyce (adopted, seed.py:95-115); b3_origin:derived_joyce_a1 |
| SI-41 | other all-plain seeds (0,7), (4,19), (8,31) | topology-number | arch:861-866 | 20:284-295 | refuted-by-argument | "the other three fail STRUCTURALLY -- a generation count is a number of things" 20:235-236 (n_gen = 0, 1, 2) | computed-number (b3_path.PATHS, test_reachable_family_is_runnable) | b3_seed:seed_7_joyce, seed_19_joyce, seed_31_joyce (all DISABLED, seed.py:62-91) |
| SI-42 | Joyce JDG II Example 4: b2 = 8 + l, b3 = 47 − l (the n = 3 line) | internal | arch:1396-1397 | arch:1421-1424 | unknown | "The seed's selection argument therefore goes back to the author." arch:1421 | argument | seed_selection:wa1_correspondence (adopted, RULED 2026-10-01 D-015) / ruling_only, seed.py:324-373 |
| SI-43 | chi_eff from the Kummer K3 reading | internal | 16:212-231 | 21:232-281 | unknown | para: χ(K3) = 24 does not reach 144 18:1-37 | computed-number | chi_eff_route:k3_reading (adopted, RULED 2026-10-01 D-015, g2_metric.py:112-166) |
| SI-44 | chi_eff = 144 with n_gen = chi_eff/48 | generations | arxiv:3 | 18:72-118 | unknown | "chi_eff is NOT decided by this ruling — the dichotomy stands" 19:7-8 | ruling | chi_eff_route:constant_144 (not adopted, g2_metric.py:182-195); n_gen_source:chi_eff_over_48 (seed.py:200-211) |
| SI-45 | n_gen = b3/8 = 24/8 | generations | arxiv:3 | 14:280-293 | superseded | para: on 43, b3/8 gives 5.375 | computed-number | n_gen_source:b3_over_dim_O |
| SI-46 | n_gen = b2/4 = rank Γ | generations | 16:55-85 | arch:1416-1419 | in-force | "b₂/4 counts the singular involutions only when every family is plain" arch:1417-1418 | ruling | n_gen_source:b2_over_faces |
| SI-47 | three generations as the maximum selects (12,43) uniquely | generations | 16:21-53 | arch:1412-1413 | superseded | "in the full family, holonomy selects the whole n = 3 line" arch:1413 | argument | b3_origin:derived_joyce_a1 (its BUYS, seed.py:252-255); seed_selection:ruling_only (seed.py:363-371) |
| SI-48 | b2 = 0 for any G2 manifold | topology-number | arch:632-633 | arch:641 | refuted-by-argument | "That is wrong, and is very likely a confusion with b₁" arch:633-634 | argument | no option |
| SI-49 | b2 = 4, the four faces | topology-number | arxiv:3 | 19:16 | superseded | para: topology.b2 = 12 after the seed ruling 19:15-16 | ruling | b3_seed:seed_24 |
| SI-50 | quintessence as a b2 = 4 Kähler modulus | cosmology | 02:299-325 | arch:583 | refuted-by-argument | "A field stabilised at 24.6 TeV cannot be rolling today." arch:584-585 | computed-number (geometry.kahler_over_quintessence_mass) | dark_energy_betti:b2_4 (RULED OUT 2026-09-06, cosmology.py:293-318) |
| SI-51 | quintessence as a C3 axion counted by b3 | cosmology | arch:585-586 | 19:39-51 | in-force | "shift-symmetry protected — a C₃ axion, counted by b₃" arch:585-586 | argument | dark_energy_betti:b3_24 (adopted, frozen 24) / b3_live, cosmology.py:247-291 |
| SI-52 | w0 = −(b3 − 1)/b3: −23/24 -> −42/43 | cosmology | 01:77-97 | 19:39-51 | unknown | "Which of b3_24 and b3_live is correct is the AUTHOR'S ruling" cosmology.py:287-288; the 43 path's −42/43 at 0.94σ, 19:48 | ruling | dark_energy_betti:b3_24 (adopted, frozen −23/24) / b3_live (−42/43, NOT ADOPTED), cosmology.py:247-291 |
| SI-53 | rival wa forms −4/√b3 (FITTED) and wa = 0 | cosmology | 01:103-104 | arch:469-470 | retired | "retired this cycle — do not resurrect them without a derivation" 01:103-104 | argument | no option |
| SI-54 | thawing band wa ∈ [−3/b3, −1/b3] (Caldwell-Linder) | cosmology | arch:461-466 | arch:479 | in-force | "Recorded, not repaired, and deliberately so" arch:474 | argument | dark_energy_mechanism:thawing_quintessence (adopted, RULED, cosmology.py:128-155) |
| SI-55 | S8 friction from the moduli coupling | cosmology | 01:106-123 | arch:497-498 | refuted-by-argument | "the moduli coupling was never the relevant knob" arch:497-498 | computed-number (moduli_dm_coupling.py) | no option |
| SI-56 | S8 suppression wired to m_φ = b3·H0 | cosmology | arch:500-507 | arch:509 | never-implemented | "Wiring S₈ to it is a physics ruling and is not taken here." arch:508-509 | none | prose only |
| SI-57 | racetrack fixes Re(T) at 7.086 (or 9.865) | action | 02:173-178 | 19:80-109 | refuted-by-argument | para: not stationary points; AdS minimum at 37.85 11:84-120; no vacuum on 43 19:80-109 | computed-number (racetrack_vacuum.py) | re_t_adoption:computed_vacuum (DISABLED, demoted D-015, cosmology.py:216-233); calibrated adopted |
| SI-58 | Re(T) as an open modulus | action | arch:1439-1445 | 21:232-281 | unknown | "The adopted geometry carries no leading-order pair that fixes Re(T)" arch:1441-1442 | argument | re_t_adoption:calibrated (adopted; RULED 2026-10-01 D-015, Re(T) an OPEN modulus, cosmology.py:175-202) |
| SI-59 | Kähler potential: −3ln(T+T̄), −2ln Vol7, the 7/3 form | action | 07:81-98 | 07:98 | unknown | para: three inconsistent forms; the 7/3 form is G2-consistent | argument | prose only |
| SI-60 | real form of φ: split G2* or compact | internal | 09:1-31 | arch:1426-1437 | unknown | "The lead recommends `octonion_derived`." arch:1437 | computed-number (0 of 788 params move) | g2_form_convention:octonion_derived (adopted, RULED 2026-10-01 D-015) / all_plus_one, g2_forms.py:80-175 |
| SI-61 | φ outside the G2 orbit | internal | 08:162-224 | 14:52-102 | superseded | para: dim ann 6 vs 14; later read as the split form | computed-number | g2_form_convention:all_plus_one (the split form G2*, not adopted, g2_forms.py:119-121) |
| SI-62 | Γ = (Z/2)^3 forced by φ; 7 involutions = 7 Fano arcs (4+3) | internal | 06:340-365 | 16:55-85 | in-force | para: R1, R2 06:340-365 | argument | prose only |
| SI-63 | flat b3 = 7; 24 split 7 + 17 | topology-number | 07:1-18 | 07:18 | superseded | "7 + 17, not 12 + 12" 07:1-18 | argument | prose only |
| SI-64 | Yukawas from intersecting singular loci | particle | 16:179 | 16:195 | refuted-by-argument | para: chiral matter needs codim-7 conical points | argument | no option |
| SI-65 | TCS reading of the EH gluing; Co0 Donaldson angle | internal | 16:197 | 16:210 | refuted-by-argument | para: REFUTED by the admissibility predicate 16:197-210 | argument | no option |
| SI-66 | four unpaired forms | internal | 17:158 | 17:188 | refuted-by-argument | "nothing is unpaired, because the map is TOTAL" 17:158 | argument | no option |
| SI-67 | 128 conical assignments R^7/(Z/2)^3 for chirality | particle | 20:32-44 | 21:232-281 | unknown | para: codim-7, off the A1 branch | computed-number | prose only |
| SI-68 | chirality via the heterotic dual of Kummer fibrations, or the shadows as walls | shadows | 21:262 | 21:262 | never-implemented | "or the shadows as walls" 21:262 | none | prose only |
| SI-69 | cross-shadow coupling ∫φ∧F_A∧F_B, 42 of 210 channels | gauge | arch:273 | arch:345 | in-force | para: resolved affirmatively at a stated scope; kill condition retired | argument | prose only |
| SI-70 | moduli indexed by b2 (U(1) gauge) or by b3 clusters | gauge | 06:195-215 | 20:48-60 | unknown | para: b2 counts U(1) gauge fields | argument | moduli_indexing:b3_clusters (adopted, fork OPEN) / b2_gauge / cy3_shadow, g2_forms.py:243-314 |
| SI-71 | θ13 = asin(1/6) | particle | 01:59 | 01:60 | falsified | para: ruling R1 2026-08-25, ~9σ from NuFIT 6.0 | data (NuFIT 6.0) | no option |
| SI-72 | θ13 follows the seed or is calibrated at 24 | particle | 19:111-134 | 19:134 | unknown | para: 4.8351° follow_seed vs 8.6686° calibrated_24 | computed-number | flavour_seed_coupling:follow_seed (adopted, RULED) / calibrated_24, flavour.py:17-50 |
| SI-73 | θ13 from modular flavour symmetry | particle | arch:397-406 | arxiv:18-24 | refuted-by-argument | para: obstructed, because G2 moduli are real | argument | no option |
| SI-74 | quark-lepton complementarity | particle | arch:397-406 | arch:406 | falsified | para: 9.155°, +5.3σ | data | no option |
| SI-75 | sterile mixing sin²2θ = 1/b3 | particle | 01:162 | 01:186 | falsified | "FALSIFIED, and still published" 01:162 | data | no option |
| SI-76 | Σmν spectral 0.0598 vs geometric 0.0817 | particle | 01:125-139 | 01:139 | retired | para: spectral rejected by ruling R5 | ruling | no option |
| SI-77 | gaugino-family predictions | particle | 01:141-147 | 01:146 | falsified | "They remain on the books labelled FALSIFIED per the standing ruling" 01:146 | data | no option |
| SI-78 | Cabibbo angle e^{-3/2} | particle | 01:141 | 01:147 | in-force | para: at 2.79σ | data | prose only |
| SI-79 | α_T = 26/10 | other | 01:249-254 | 01:254 | unknown | para: target-first | argument | prose only |
| SI-80 | mirror-world H0, ALP (IAXO), cross-shadow Bell, quantum_bio | cosmology | 01:234-264 | arxiv:37-103 | never-implemented | para: literature pitches; quantum_bio misses by 2× 01:256-264. The ALP part was computed later: see SI-158 (20:140-149) | none | prose only |
| SI-81 | the k_gimel = b3/2 + 1/π layer (α⁻¹, Higgs VEV, sin²θW, T_CMB, μ) | identity | arch:599-600 | arch:1460-1462 | unknown | "a fit that agrees only at the retired 24" arch:1462 | argument | prose only (D-007 pending) |
| SI-82 | identity ledger: 12 of 15 identities hold only on seed_24 | identity | 21:136-158 | 21:158 | unknown | para: measured per seed | computed-number | b3_seed:seed_24 |
| SI-83 | the 24 is the bulk's spacelike core, not b3 | identity | 19:18-22 | arch:1447-1462 | in-force | "each counts the BULK's 24 spacelike core dimensions of the adopted (24,2) two-time signature" 19:21-22 | ruling | prose only |
| SI-84 | de Sitter uplift from racetrack pairs | cosmology | 21:184-204 | 21:204 | unknown | para: nothing on the menu uplifts to dS | computed-number | no option |
| SI-85 | dark-energy integer scan n = 24, 12, 8, 6, 4, 3 | cosmology | 02:299-325 | 03:35-39 | retired | "It is not a result and must not be promoted." 02:299-325 | computed-number | dark_energy_betti:b3_24 (adopted), b2_4, ngen_3, chi_over_b3_6, bridges_12, octonion_8, b3_live (cosmology.py:247-352) |
| SI-86 | geometry.theta_13 = 8.54 as a "0.4σ cross-check" | particle | arch:66-71 | arch:73-75 | withdrawn | para: a hardcoded 8.54 restates the anchor; the derivation particle.theta_13_deg sits at 0.805σ | computed-number (geometry.theta_13) | prose only |
| SI-87 | one global labelling of the 7 Fano lines by 3 E8 blocks (block is a property of the channel) | lattice | arch:191-257 | BCA:84-96 | in-force | "This is an input. It is not derived from anything else in the framework" BCA:90 | argument | prose only |
| SI-88 | n_faces = 4 forced as the maximum rainbow set (was h11 = 4 of TCS #187, FITTED) | topology-number | BCA:104-106 | arch:191-257 | in-force | "No labelling makes 5, 6 or 7 points simultaneously rainbow. n_faces = 4 is forced." BCA:106 | computed-number (enumeration of 3^7 labellings) | prose only |
| SI-89 | face genericity: collinear 4-sets excluded (CRITERION_STATED_NOT_DERIVED -> derived) | lattice | BCA:107-111 | policy.py:101-121 | in-force | "The 28 line-containing 4-point sets admit zero labellings" BCA:107 | computed-number (labelling enumeration) | face_genericity:generic (RULED) |
| SI-90 | coupling graph is 7 triangles; 42 channels = 7 points × 3 lines × 2 orderings | gauge | BCA:37-60 | BCA:60 | in-force | "its three edges are exactly the three Fano lines through k" BCA:54-55 | computed-number (enumeration) | prose only |
| SI-91 | 12 live couplings only on four complete triangles (35 = C(7,4) placements); each face is a triangle | lattice | BCA:64-80 | BCA:80 | in-force | "Each face IS a triangle." BCA:78 | computed-number (all 293,930 placements) | prose only |
| SI-92 | structure closes as K4: bridges = directed edges, E8 blocks = perfect matchings | lattice | BCA:115-130 | arch:191-257 | in-force | "The bridge count 12 is K₄'s directed-edge count, not a separate input." BCA:127-128 | argument | prose only |
| SI-93 | n_gen = 3 fixed twice over: Leech 8+8+8 and q + 1 = 3 lines per Fano point | generations | BCA:132-134 | BCA:134 | in-force | para: rather than 12/4 arithmetic BCA:132-134 | argument | prose only |
| SI-94 | bridge assignment unique up to PSL(3,2) (126 = 7 arcs × 18 labellings all relabellings) | lattice | BCA:138-158 | arch:763-766 | in-force | "the claim must keep saying it is conditional." BCA:163-164 | argument | prose only |
| SI-95 | a preferred imaginary octonion or shadow asymmetry breaking PSL(3,2) | lattice | BCA:160-164 | arch:763-766 | unknown | para: "Nothing currently does this" BCA:163; Approach 6 (preferred direction) left open arch:763-766 | argument | no option |
| SI-96 | stride-4 grouping {i, i+4, i+8} vs contiguous grouping | lattice | BCA:168-179 | BCA:179 | in-force | "a coordinate convention, not a selection among rivals" BCA:173-174; contiguous is a different object | computed-number (576 regular orbit) | prose only |
| SI-97 | person-within-a-face reading: Path B (Σ7) suffices; inter-face coupling impossible in Σ7 | other | BCA:204-226 | BCA:226 | in-force | "Path B is sufficient for the consciousness architecture under this reading." BCA:220-221 | argument | prose only |
| SI-98 | Path A cross-shadow flux in the 13D sector | gauge | BCA:228-230 | BCA:230 | never-implemented | "it remains blocked on an underived C₃" BCA:229 | argument | no option |
| SI-99 | topological content of the coupling from harmonic forms on a compact G2 with b3 = 24 | internal | BCA:234-242 | BCA:242 | never-implemented | "a number, not a topological invariant" BCA:237 | argument | prose only |
| SI-100 | leakage coupling 1/sqrt(n_bridges//2), n_aligned = χ_eff/b3 = 6, "derived from moduli" | gauge | arch:261-269 | arch:269 | withdrawn | para: the coupling is kept; the derived-from-moduli provenance is withdrawn | argument | prose only |
| SI-101 | Higgs quartic derived from geometry | particle | arch:696-712 | arch:712 | refuted-by-argument | para: v19 notes: the formula inverts the measured value | argument | prose only |
| SI-102 | christ-constant-153, with 9 read as the SU(3) Cartan dimension | identity | arch:696-712 | arch:712 | refuted-by-argument | para: fitted; the 9 is not the Cartan dimension | argument | prose only |
| SI-103 | Froggatt-Nielsen coefficients A_f | particle | arch:696-712 | arch:712 | unknown | para: fitted, not derived | argument | prose only |
| SI-104 | yukawa-epsilon-cabibbo match | particle | arch:696-712 | arch:712 | refuted-by-argument | para: a 1% coincidence | argument | prose only |
| SI-105 | dm-omega-sterile = 0.48 | cosmology | arch:696-712 | arch:712 | unknown | para: undocumented; the dead computation behind it gives 0.152 | computed-number (dead dm-omega computation) | prose only |
| SI-106 | de-h0-odowd θ_mix = 31° and "Tension Resolved" | cosmology | arch:696-712 | arch:712 | refuted-by-argument | para: θ_mix fitted; 71.55 sits 1.43σ from SH0ES | data (SH0ES) | h0_route:odowd_composite (adopted, 1.43 sigma SH0ES) / ricci_flow (disabled, 31 deg), cosmology.py:91-112 |
| SI-107 | baryon asymmetry from Re(T) | cosmology | arch:696-712 | 20:151-163 | unknown | para: Re(T) is calibrated | argument | re_t_adoption:calibrated (adopted, cosmology.py:199-214) |
| SI-108 | v22 consciousness-io-gate | other | arch:696-712 | arch:712 | never-implemented | para: no observable | argument | prose only |
| SI-109 | SU(3) confinement σ ~ 1/Vol; U(1) anomaly from G2 | gauge | arch:696-712 | arch:712 | never-implemented | para: asserted, not demonstrated | argument | prose only |
| SI-110 | root-lattice-288 = 2·chi_eff as a b3 result | identity | arch:737-739 | arch:739 | refuted-by-argument | para: the chain never reaches b3 | argument | prose only |
| SI-111 | a third construction, or a non-Joyce resolution of the non-A1 components | internal | arch:899-906 | arch:906 | unknown | para: not excluded; would have to be exhibited | argument | no option |
| SI-112 | K_IJ from associative 3-cycles: 7 ⊕ 12 ⊕ 12 ⊕ 12; 3 singular + 4 free involutions | internal | arch:984-1016 | 15:67-99 | in-force | para: ADOPTED arch:984-1016; flat L⁷/abs(Γ), twisted 32π²L³, L unfixed 15:67-99 | argument | prose only |
| SI-113 | 24 = abs(S4) = 4 × 6 (arc stabiliser), +2 = flag stabiliser | identity | arch:1097-1125 | arch:1125 | unknown | para: does NOT derive D_bulk = 26 | argument | b3_origin:arc_flag_stabiliser |
| SI-114 | twisted sector 36 = 6² | topology-number | arch:1129-1131 | arch:1131 | unknown | para: untested | none | prose only |
| SI-115 | lopsided splits 3+4 vs 1+3 | internal | arch:1133-1137 | 14:163-181 | unknown | para: untested; 3+4 mirrors 3 singular + 4 free involutions 14:163-181 | none | prose only |
| SI-116 | flat Betti {1,0,0,7,7,0,0,1} from the 7 non-trivial characters; invariant 3-forms = Fano lines | topology-number | arch:1143-1167 | arch:1167 | in-force | para: FLAT_B2 = 0 had carried a false citation | argument | prose only |
| SI-117 | the 43 path destroys the neutrino sector (θ13 58.8σ) | particle | arch:1178-1211 | arch:1211 | refuted-by-argument | para: the 58.8σ came from the (24,12) chimera; coherent 43 gives 2.48σ | computed-number (seed_43 rerun) | b3_seed:seed_43_joyce |
| SI-118 | freudenthal_quartic 16(b3/27)² and wa_thawing −4/√b3 on seed_43 | identity | arch:1237-1241 | 11:157-171 | withdrawn | para: both withdraw themselves at 43; free set 37 (seed_24) vs 39/40 (seed_43) | computed-number | b3_seed |
| SI-119 | K_IJ cross-blocks vanish by character orthogonality | internal | arch:1258-1264 | 15:89-98 | refuted-by-argument | para: wrong; the neck gives O(t²) | argument | prose only |
| SI-120 | metric wall r* ∝ √t | internal | arch:1307-1319 | arch:1319 | in-force | para: exponent pinned | argument | prose only |
| SI-121 | flux superpotential W = Σ n_I Π_I fixes moduli and freezes ledger rows | action | arch:1323-1328 | 17:271-308 | refuted-by-argument | para: 43 integers collapse to 2; L*⁴ = −768π²B/(7A) is no vacuum; count stays 22 | computed-number | no option |
| SI-122 | chi_eff route C: 6b3/48 | generations | arch:1340-1342 | arch:1342 | refuted-by-argument | para: equals b3/8, "the b3-route in disguise" | argument | chi_eff_route:seed_dependent (DISABLED, g2_metric.py:197-218); n_gen_source:b3_over_dim_O |
| SI-123 | certificate: Betti (1,0,12,43,43,12,0,1), χ(Y7) = 0, π1 finite iff all three generators singular | topology-number | arch:1367-1386 | 21:11 | in-force | para: CG.1, CG.2, CG.4 | computed-number (certificate gates) | b3_seed:seed_43_joyce |
| SI-124 | "euler-characteristic" formula as a property of Y7 | identity | arch:1367-1386 | arch:1386 | refuted-by-argument | para: CG.2: it is χ_eff from off-path TCS Hodge data | argument | prose only |
| SI-125 | gauge content of the 12 loci: N=4 SU(2), no confinement, no gaugino condensate | gauge | arch:1367-1386 | arch:1386 | in-force | para: CG.5 | argument | prose only |
| SI-126 | flux potential stabilises the volume | action | arch:1367-1386 | arch:1386 | refuted-by-argument | para: CG.6: runs away, V ∝ λ⁻⁵ (Lukas-Morris + ADV) | argument | no option |
| SI-127 | 28 literature-checked reachable (b2, b3) pairs, none with 24 | topology-number | arch:1367-1386 | arch:1386 | in-force | para: CG.7 | data (literature census) | prose only |
| SI-128 | tau_gnosis / tau_baseline Orch-OR timescales, 25·exp(3.2√(n/12)) | other | SCALE:18-38 | SCALE:224 | unknown | para: phenomenological, SPECULATIVE, no geometric grounding SCALE:66-88 | argument | prose only |
| SI-129 | scalar breathing amplitude A ~ α_F × NS-merger strain (~1e-6) | cosmology | SCALE:42-62 | SCALE:223 | in-force | para: status now AGREE | argument | prose only |
| SI-130 | sterile mixing 4.28e-05 from a bridge-mediated type-I seesaw | particle | SCALE:92-131 | SCALE:225 | in-force | para: replaces sin²2θ = 1/b3 (FALSIFIED, SI-75) SCALE:96 | argument | prose only |
| SI-131 | spectral.lambda_max = k_gimel × 80.5 | other | SCALE:135-156 | SCALE:226 | unknown | para: 80.5 CALIBRATED; a 0.124% residual unexplained | computed-number (spectral.lambda_max) | prose only |
| SI-132 | Ricci law R0·exp(−z/τ) | cosmology | 02:182-186 | 02:186 | superseded | para: recorded as the wrong law | argument | prose only |
| SI-133 | z_transition ≈ 0.52 from τ = k_gimel/b3 = 0.5133 | cosmology | 02:188-194 | 02:194 | unknown | para: match recorded, not ruled | computed-number | prose only |
| SI-134 | vol_v7 = 1.0; Φ_G2 = Vol·χ/b3 = 6 | internal | 02:207-212 | 02:212 | unknown | para: vol_v7 is an ANSATZ placeholder | argument | prose only |
| SI-135 | α_s, g2, g′ locked by cycle volumes | gauge | 02:214-217 | 02:217 | never-implemented | para: the cycle volumes are computed nowhere | argument | prose only |
| SI-136 | η phase π/12 under b3 ≡ 0 mod 24 | identity | 02:219-220 | 02:220 | refuted-by-argument | para: π/12 breaks the mod-24 argument | argument | prose only |
| SI-137 | funnel 24-pin bottleneck | other | 02:225-227 | 02:227 | refuted-by-argument | para: compression_ratio does not depend on the pins | computed-number (funnel.compression_ratio) | prose only |
| SI-138 | formulas counted as b3-rooted | identity | 03:69-80 | 03:80 | refuted-by-argument | para: generation-theorem = 3×8; cabibbo-angle-geometric, strong-CP lock, gauge-unification-sum contain no b3 | computed-number (formula census) | prose only |
| SI-139 | w0 = −23/24 scored against "DESI 2025" −0.958 ± 0.02 | cosmology | 03:279-303 | 04:1-22 | falsified | para: the anchor was fabricated; 3.62σ FAIL against DR2 | data (DESI DR2) | dark_energy_betti:b3_24 (adopted; 3.62 sigma on w0, cosmology.py:258-267); b3_seed:seed_24 |
| SI-140 | thawing anchor for wa | cosmology | 03:355-359 | 03:359 | unknown | para: ruling open | none | prose only |
| SI-141 | S8 at 0.718σ (Planck) and 2.733σ (KiDS) | cosmology | 03:344-347 | 03:347 | in-force | para: a real tension against KiDS | data (Planck, KiDS) | prose only |
| SI-142 | α⁻¹ and μ_pe pass under a theory tolerance | identity | 04:41-101 | 04:101 | unknown | para: at CODATA α⁻¹ 3.35e4σ, μ_pe 12.73σ, "striking coincidence" | data (CODATA) | prose only |
| SI-143 | four-term α⁻¹ with D_G2/(10⁴ − 3k_gimel) | identity | 04:105-118 | 04:118 | retired | para: retired in v22.5 | none | prose only |
| SI-144 | v = k_gimel·(b3 − 4), the electroweak VEV | particle | 04:120-141 | 04:141 | unknown | para: open ruling, 0.3σ vs ~2400σ | computed-number | prose only |
| SI-145 | H0_early agrees with Planck | cosmology | 04:153-212 | 04:212 | refuted-by-argument | para: a tautology; z_star ≈ 1.95 survives; raw v14.2 log-scaling gives H0 ≈ 101.4 (68σ) | argument | prose only |
| SI-146 | 14 PASS rows (CKM/PMNS triality, wa_thawing) as predictions | particle | 04:236-259 | 04:259 | unknown | para: FITTED or CALIBRATED | argument | prose only |
| SI-147 | G_F_matched and m_higgs_pred | particle | 04:281-287 | 04:287 | falsified | para: 57.1σ and 41.6σ | data | prose only |
| SI-148 | φ orientation: combinatorial Fano theory, or G2 load-bearing but unbuilt | internal | 09:130-170 | 14:188-197 | unknown | para: orientation moves no output; octonion_derived costs zero 14:188-197 | computed-number | g2_form_convention:octonion_derived (adopted, RULED 2026-10-01 D-015, g2_forms.py:80-175) |
| SI-149 | "zero fitted parameters"; θ13 "the ONLY fitted parameter"; EDOF = 3 | other | 09:197-251 | 10:8-15 | refuted-by-argument | para: 67 measured non-derived quantities; the θ13 claim false; EDOF = 3 an ansatz | argument | prose only |
| SI-150 | H0_tension_ratio, Omega_DM, DM/baryon as b3 results | cosmology | 09:300-315 | 09:315 | refuted-by-argument | para: arithmetic on experiment, like chi_eff = 6·b3 | argument | prose only |
| SI-151 | bridge_ede entropy damping | cosmology | 09:323-334 | 09:334 | unknown | para: FITTED "per Gemini debate"; as_weight unreachable | argument | prose only |
| SI-152 | yukawa.lambda_eff = golden ratio | particle | 11:127-137 | 11:137 | unknown | para: a discrete choice | none | prose only |
| SI-153 | Freudenthal quartic 16(b3/27)² vs fallback 27c⁴/4; alpha_gut = 1/(10π) | gauge | 11:157-171 | arch:1237-1241 | unknown | para: the two quartics differ by 3× | argument | prose only |
| SI-154 | Γ7 modular flavour programme | particle | 11:175-178 | 11:178 | never-implemented | para: targets the flavour block | none | prose only |
| SI-155 | racetrack exponents a = 2π/b3, b = 2π/D_bulk | action | 11:288-296 | 11:296 | unknown | para: stated, not ruled | argument | re_t_adoption:computed_vacuum (DISABLED; a = 2 pi/elder_kads, b = 2 pi/D_bulk, cosmology.py:185-188) |
| SI-156 | switch search: consistent sets need octonion_derived + computed_vacuum | other | 12:33-75 | 12:215-251 | unknown | para: joyce_twisted_sector genuinely VACUOUS (seed_24 only, seed.py:307-320) | computed-number (switch search) | re_t_adoption:computed_vacuum; b3_origin:joyce_twisted_sector |
| SI-157 | Σmν published four ways (0.101, 0.102, 0.0605, 0.0425); inverted ordering predicted | particle | 12:289-333 | 13:1-23 | unknown | para: a normal-hierarchy number carries an inverted label; fork-independent 13:1-23 | computed-number | prose only |
| SI-158 | axion-photon coupling g_aγγ published (2.688e-11 adopted, 1.50e-11 calibrated_24) | particle | 20:140-149 | 21:92-101 | in-force | para: above the 2e-11 ceiling on the adopted branch; the test asserts the breach | computed-number (axion coupling test) | flavour_seed_coupling:follow_seed / calibrated_24 |
| SI-159 | sin θ12 = (1/√3)(1 − (b3 − b2·n_gen)/(2χ_eff)) | particle | 13:213-219 | 13:219 | in-force | para: derived, against a calibrated 33.44 | computed-number | prose only |
| SI-160 | RULINGS_ASSESSMENT scoring (ruling (a) on sin θ13 = 1/√b3) | other | 13:257-267 | 13:267 | withdrawn | "The questions survive; the scoring does not." 13:257-267 | argument | prose only |
| SI-161 | intersection tensor: 12 entries, all −2, on the H² diagonal | topology-number | 14:163-181 | 14:181 | in-force | para: computed on seed_43 | computed-number | b3_seed:seed_43_joyce |
| SI-162 | internal (4,3) signature, pulled by two-time | internal | 14:222-229 | 14:229 | unknown | "provenance is not an argument" 14:222-229 | argument | no option |
| SI-163 | EH and glued metric (M3); multi-sector SUGRA vacuum (M4) | internal | 14:231-233 | 14:233 | never-implemented | para: not built | none | prose only |
| SI-164 | b3 = 24 provenance "From TCS construction" | topology-number | 14:256-260 | 14:260 | withdrawn | para: the provenance was false | argument | prose only |
| SI-165 | metric-free pairing on H³ | internal | 15:67-99 | 15:99 | refuted-by-argument | para: 3 + 3 = 6 ≠ 7 | argument | no option |
| SI-166 | K = h11 = b2 and the χ_eff routes at 43 | generations | 15:129-157 | 15:157 | refuted-by-argument | para: K = h11 breaks; routes give 144, 462.25, 258; n_gen = b3/8 specific to 24 | computed-number | chi_eff_route:seed_dependent (DISABLED) / constant_144, g2_metric.py:182-218 |
| SI-167 | G_GEOMETRY_HOLONOMY "G2 holonomy validated" PASS | internal | 18:180-221 | 18:221 | withdrawn | para: a literal, false on the split branch; the gate now refuses | computed-number (G_GEOMETRY_HOLONOMY) | prose only |
| SI-168 | n_gen = chi_eff // b3 (72//43 = 1) | generations | 20:118-123 | 20:123 | retired | para: route retired; G22 is 43/288 | computed-number | no option (n_gen_source has b3_over_dim_O, b2_over_faces, chi_over_24, chi_eff_over_48, seed.py:138-212) |
| SI-169 | eta_B and m_higgs_local on 43; published Re_T the static 7.086 fallback | cosmology | 20:151-163 | 20:163 | unknown | para: eta_B 6.846e-10 (18.16σ), m_higgs_local 70.568 | computed-number | b3_seed:seed_43_joyce; re_t_adoption:calibrated (adopted, cosmology.py:199-214) |
| SI-170 | π1(Y) = 1 on the admissible branch; Wilson-line dock | gauge | 21:11 | 21:11 | in-force | para: the Wilson dock stays CLOSED | computed-number | prose only |
| SI-171 | tau_24 = b3; G22 (24 vs 43); G01 288 vs ancestral_roots 915 | identity | 21:12-15 | 21:103-111 | unknown | para: tau_24 BROKEN; strategies disagree; author ruling requested | computed-number | prose only |
| SI-172 | twisted-sector representative of an A1 family: orbit sum or orbit average (twisted K_IJ entries 32π²L³ vs 8π²L³) | internal | 15:101-110 | 15:220-222 | unknown | "Writing either factor in would have been an invented constant, so it is a fork" 15:105-106 | argument | twisted_norm_convention:orbit_sum (adopted, fork OPEN) / orbit_average, g2_metric.py:222-289 |
| SI-173 | an uncited theory uncertainty may not change a verdict (R6 generalised to the validation layer) | other | 01:191-224 | 04:66-75 | in-force | "an uncited theory uncertainty may not change a verdict" 01:218; found inert at 04:73 | ruling | theory_uncertainty_policy:cited_only (adopted, fork OPEN) / always / experimental_only, policy.py:50-100 |
| SI-174 | wa = −1/√b3 = −0.2041 (registered cosmology.wa_derived, leading-order) | cosmology | 01:99-102 | arch:468-479 | in-force | "Recorded, not repaired, and deliberately so" arch:474; outside the thawing band by 1.63×, arch:469 | argument | no option |

Pipeline and tooling (no rows): statuses upgraded at export (arch:36), nine simulation modules
never ran (arch:602-628), a progress message deleted 14 parameters (arch:540-555), 173 stale
terminology refs cleared (arch:384-393), artifact-root overwrite (arch:1470-1472).

## 4. Owner's candidates

| # | candidate | status | reference |
|---|---|---|---|
| 1 | three shadows instead of two | seen | 07:127-195. Falsified as a shadow count (9D (8,1) shadows short by 2), adopted as three blocks (SI-10, SI-12). Four shadows also tested at 07:164. |
| 2 | shadows in pairs, or of different dimension or make-up | seen (partly) | One 24D (23,1) shadow under Bars 02:63-64. One shadow under (25,1) 07:288-290. 13 + 13 + 2 shared sector 07:197-264. Asymmetric (8,6,6,6) / (6+2,6,6,6) faces 08:45-92, arch:1063-1092. "shadows as walls" 21:262. 2+2 face pairing 07:314-339. |
| 3 | two times, one in the bulk and one for the shadows | not seen as stated | Nearest: the "+2" readings (lightcone pair / two-time + bridge) 02:73-74, and the breathing-portal "+2 shared" reading 07:266-312. |
| 4 | three times | seen | (24,3) tri-shadow 07:173-180. J3(O) 3 times + 24 space 07:148-150. A four-time (28,4) 32D reading 07:266-312. |
| 5 | 26D (24,2), two 13D (12,1), one time per shadow | seen, in force | 02:40-47 (ruled 2026-08-31). arxiv:3. 19:22. |
| 6 | 27D (24,1,2) and other bulk dimensions | seen (partly) | 27D only as Bars-Kounnas (25,2) 02:57-59, 07:179-180. Also 25D (24,1) formula 02:101-103, (25,1) 26D 02:68, (26,2) 28D 02:69, (28,4) 32D 07:266-312. 14 stale `27D` and 17 `25D` refs plus the "26D = 24 + 1 + 2" accounting cleared arch:384-393. 14D×2, 12D, 11D and 10D bulks not seen. 13D appears only as the shadow. |
| 7 | other internal spaces | seen | TCS #187 / Fano TCS 11:204, arch:511-538, 16:197-210. Joyce (4,24), (7,24), (15,24), (12,43), Example 4 13:118-181, arch:825-872, arch:1396-1414. Leech, Niemeier E8³, lower-symmetry Niemeier, octonionic Leech 05:114-186, arch:1018-1029. D4 roots 08:265-291. Fano arcs 06:340-365. Kummer K3 16:212-231, 18:1-37. CY3-type Kähler form 07:89-92. Conical R^7/(Z/2)^3 20:32-44. Spin(7) only as G2 ⊂ Spin(7) ⊂ Spin(8) 08:267 and the CN coboundary arch:515-516. Calabi-Yau as an internal space not seen. |

## 5. Gaps

- `archive/OUTSTANDING_ISSUES_closed.md`: read 273-407, 449-655, 825-884, 1018-1092 and 1388-1502. Lines 1-272 (export and anchor hygiene, the bridge-channel join at 191-257), 655-824, 885-1017, 1093-1387 (the 43 path at 917, the real-form and A1 addenda at 1141-1344) were seen only as headings.
- `SCALE_DISAGREEMENTS.md` and `BRIDGE_CHANNEL_ASSIGNMENT.md`: headings only, no rows taken.
- Issues files not read in these ranges: 02:180-293, 03:52-359, 04 whole, 09:130-334, 10:1-120, 11:120-199 and 286-296, 12 whole, 13:1-41 and 194-317, 14:1-45 and 160-262, 15:55-222, 17:1-72 and 190-308, 18:150-259, 20:95-256 and 297-321, 21:1-135.
- `today` names forks as the site text names them. `src/metaphysica/simulations/core/variants/` was not opened (that is the code-catalogue lane), so option existence is not verified.
- Rows marked `para:` are paraphrases of the cited lines, not quotes. They are candidates for the 20-row citation check.
- Policy forks (joyce_contribution_table, twisted_norm_convention, theory_uncertainty_policy) are not given rows.

## 6. Second pass (2026-11-11)

New citation keys: `BCA:` = `BRIDGE_CHANNEL_ASSIGNMENT.md`, `SCALE:` = `SCALE_DISAGREEMENTS.md`, `seed.py:` / `policy.py:` = `E/src/metaphysica/simulations/core/variants/catalogue/`.

- Gap 1 (`archive/OUTSTANDING_ISSUES_closed.md` 1-272, 655-824, 885-1017, 1093-1387): closed. Rows SI-86, SI-87 to SI-96 (the bridge join at 191-257, read together with BCA), SI-100 to SI-127. No idea in arch:1-65 and 80-187 (export and bibliography hygiene), 655-692, 805-823 (eml-math release), 1243-1256, 1273-1305 (provenance tooling).
- Gap 2 (`SCALE_DISAGREEMENTS.md`, `BRIDGE_CHANNEL_ASSIGNMENT.md`): closed. Rows SI-87 to SI-99 (BCA), SI-128 to SI-131 (SCALE). SCALE:92-131 restates SI-75 (sterile 1/b3, falsified) and adds its replacement SI-130. SCALE:198-209 is a methodological note with no new idea. BCA:183-200 is already SI-69.
- Gap 3 (issues-file ranges): closed. Rows SI-132 to SI-171. SI-41 corrected (unknown -> refuted-by-argument, 20:235-236; seeds 7, 19 and 31 DISABLED in seed.py:62-91). SI-80 annotated: its ALP part is computed and published, SI-158. Already covered, no new row: 18:153-172 (SI-64, SI-67), 20:216-244 and 289-295 (SI-41), 15:101-111 (policy fork). No idea, tooling only: 02:229-293; 03:52-68 and 85-272; 10:19-117; 12:1-31 and 79-213; 14:1-45; 15:174-213; 17:1-72 and 190-270; 18:230-259; 20:95-113, 126-135, 165-214 and 246-321 outside the profile lines; 21:18-90 and 113-135.
- Option names in `today` for these rows were checked against the variant catalogue (seed.py, policy.py, flavour.py, cosmology.py), not against the fork report.
- Gap 4 (`today` not checked against `variants/`): closed. Every fork and option named in `today` was grepped under `catalogue/` and its record (fork status, summary, option status) read in algebra.py, cosmology.py, flavour.py, g2_forms.py, g2_metric.py, seed.py, policy.py. `today` corrected in SI-12, 22, 24 (the fork is `lattice_24d`), SI-31, 32, 33, 36, 37, 39, 40, 42, 43, 44, 47, 50, 51, 54, 57, 58, 60, 61, 70, 72, 85, 106, 107, 122, 139, 148, 155, 166, 168, 169. SI-52 corrected in place: fate in-force -> unknown, because the catalogue adopts the frozen b3_24 (−23/24) and marks b3_live (−42/43) NOT ADOPTED, an author ruling pending (cosmology.py:247-291). Rulings dated after this lane's sources (D-015 2026-10-01: chi_eff_route k3_reading, seed_selection WA-1, g2_form_convention octonion_derived, re_t_adoption calibrated as an open modulus; D-023 2026-10-25: fano_tcs refused, b3_origin answered by derived_joyce_a1) go in `today` only; `fate` stays as the register left it at 2026-09-30. Checked and left as they were: SI-01 to SI-03, 16, 18, 27, 28, 41, 45, 46, 49, 82, 89, 113, 117, 118, 123, 156, 158, 161. The catalogue also holds moduli_indexing:cy3_shadow (CY3 Kähler moduli, g2_forms.py:313-314), a Calabi-Yau option no site-issues source names; left to the code-catalogue lane.
- Gap 5 (rows marked `para:`): closed, no idea there. It is a pointer for the merge's 20-row citation check, not an unopened source. Two were checked against their lines in this pass and hold: SI-39 (arch:1410-1414) and SI-52 (19:48).
- Gap 6 (policy forks joyce_contribution_table, twisted_norm_convention, theory_uncertainty_policy): closed. Records read (g2_forms.py:18-75, g2_metric.py:222-289, policy.py:50-100) with their site lines (11:224-242, 15:101-110 and 216-222, 01:191-230, 04:66-75). Rows added: SI-172 (twisted_norm_convention, a K_IJ normalisation), SI-173 (the cited-only verdict rule). joyce_contribution_table: no idea there; it is a citation gate that refuses an uncited table (11:238-242), and the (4,24) and (7,24) questions it would settle are already SI-33 and SI-34.
