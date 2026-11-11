# Lane site-issues: the site's issue register, closed archive and idea registers

Sources (`P` = `PrincipiaMetaphysica/docs/`): `OUTSTANDING_ISSUES.md` (index, split 2026-11-04),
`archive/OUTSTANDING_ISSUES_closed.md` (cited `arch:`), `issues/01..21` (cited `NN:`),
`ARXIV_IDEAS_REGISTER.md` (cited `arxiv:`). The register covers 2026-08-19 to 2026-09-30.
Quotes are verbatim unless marked `para:`, which means a paraphrase of the cited lines. Fork names in
`today` are as the sources name them. They were not checked against `variants/` (see Gaps).

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
| SI-12 | three blocks inside one 24 (tri-sector), the E8 factors | lattice | 07:182-192 | 07:195 | in-force | "tri-sector, not tri-shadow: three blocks inside one 24" 07:190 | argument | lattice_24D:niemeier_e8x3 (07:189) |
| SI-13 | (24,3) tri-shadow signature | time | 07:174 | 07:179 | refuted-by-argument | "the tri-shadow signature inherits the current failure rather than repairing it" 07:178-179 | argument | no option |
| SI-14 | J3(O): 27 = 3 + 24 read as 3 times + 24 space | time | 07:148-150 | 07:150 | unknown | none (listed as favouring three shadows, not ruled) | none | prose only |
| SI-15 | Bars-Kounnas 27D at (25,2), 28D at (26,2) | bulk | 02:57-59 | 07:179-180 | refuted-by-argument | "27D total does not buy the critical dimension for a three-time reading" 07:179-180 | argument | no option |
| SI-16 | spare nodes as the "+2"; 13 + 13 + 2 with a shared 2 in neither shadow | shadows | 07:197-264 | 08:1-39 | unknown | para: candidate for bulk_signature 26_2, with an F2 -> R gap | argument | bulk_signature:26_2 |
| SI-17 | breathing portals: +1 total (25,1), +2 (26,2), +1 per face (28,4) 32D four-time | time | 07:266-312 | 08:1-39 | unknown | "None adopted" 07:308-312 | none | no option |
| SI-18 | II25,1 = Λ24 ⊕ II1,1: one time, hence one shadow | lattice | 07:288-290 | 07:290 | unknown | "one time, hence one shadow" 07:288-290 | argument | bulk_signature:25_1 |
| SI-19 | four faces as four axes; 2+2 face pairing | shadows | 07:314-339 | 08:1-39 | unknown | para: the 2+2 pairing is block-relative | argument | prose only |
| SI-20 | (8,6,6,6) asymmetric face clustering | shadows | 08:45-92 | arch:1053 | falsified | "8+6+6+6 = 26, so it partitions 26 while the Golay code lives on 24" arch:1046-1047 | argument | no option |
| SI-21 | (6+2,6,6,6): 4 faces × 6 + 2 on one face = D_bulk 26 | shadows | arch:1063-1082 | arch:1086-1092 | superseded | "Read as a partition of b₃, the structure is coherent only at seed_24" arch:1086 | argument | prose only |
| SI-22 | lattice generator presented as Λ24 | lattice | 05:1-72 | 05:45 | falsified | para: det 7,144,929 and 12 norm-2 rows; kept as `_FALSIFIED_GENERATOR_NOTE` 05:45 | computed-number (lattice generator) | lattice_24D:leech |
| SI-23 | Leech decomposes into three E8 | lattice | 05:151-167 | 05:167 | refuted-by-argument | para: Λ24 has no roots, so the decomposition cannot hold | argument | no option |
| SI-24 | Niemeier E8³ as the 24D lattice | lattice | 05:169-186 | 06:286-309 | unknown | para: recommended for adoption by author's ruling 05:220-241; 8 lattice-self test failures 06:286-309 | ruling | lattice_24D:niemeier_e8x3 |
| SI-25 | octonionic Leech (Wilson) for the bridges | lattice | 05:114-133 | 05:133 | refuted-by-argument | para: the coordinate-pair bridge is not G2-equivariant | argument | no option |
| SI-26 | bridges = (arc point, complement point); (face, E8 block) | lattice | 05:135-149 | 06:39-79 | refuted-by-argument | para: Approach 7 equivalent to Approach 2 and defeated; Approach 2 owes the factor 2 | argument | no option |
| SI-27 | 24 = 12 × 2 as structural | identity | 06:83-115 | 08:226-263 | withdrawn | "DISSOLVED: no structural 2 exists; it was index arithmetic" 06:115 | argument | b3_origin:arc_flag_stabiliser |
| SI-28 | 24 as the D4 root shell | topology-number | 08:265-291 | 11:224-242 | unknown | para: NUMERICAL only, recorded as a b3_origin candidate | computed-number | b3_origin:d4_root_shell |
| SI-29 | lower-symmetry Niemeier lattices (D24+, A1^24) | lattice | arch:1018 | arch:1029 | never-implemented | "swapping the lattice moved no published number" arch:1025-1026 | argument | no option |
| SI-30 | Leech deep-hole anchor with a kill condition | lattice | 16:233-244 | 18:39-70 | in-force | para: the kill does not fire; the cost is 24 parameters | computed-number | prose only |
| SI-31 | TCS G2 (#187) as the source of b3 = 24 | internal | arxiv:3 | 16:197-210 | refuted-by-argument | "b₃ = 24 is far below that floor" (71 ≤ b3 ≤ 155) arch:523-524 | argument | g2_construction:fano_tcs |
| SI-32 | Crowley-Nordström forces b2 + b3 odd for TCS | topology-number | arch:513-515 | arch:520 | withdrawn | "It says nothing about b₂ + b₃ parity." arch:520 | argument | prose only |
| SI-33 | Joyce orbifold at (b2, b3) = (4, 24) | internal | arch:528-531 | 13:158 | refuted-by-argument | "UNREACHABLE. The g2_construction fork's adopted "Joyce (4,24)" claim cannot be realised" 13:158 | computed-number (Künneth enumeration) | g2_construction:joyce_orbifold |
| SI-34 | b2 = 7, (7, 24) | topology-number | 05:309-321 | 13:159 | refuted-by-argument | "UNREACHABLE. The b₂ = 7 alternative falls the same way" 13:159 | computed-number (Künneth enumeration) | no option |
| SI-35 | parity theorem: every (Z/2)^3 Joyce orbifold has odd b3 | topology-number | 10:121-214 | 11:33 | withdrawn | "The parity prediction "every (Z/2)^3 Joyce orbifold has odd b_3" — WITHDRAWN." 11:33 | computed-number (enumeration, flaws 11:1-38) | prose only |
| SI-36 | TCS parity makes (4,24) inadmissible | topology-number | 05:348-361 | 06:177-193 | withdrawn | para: the parity claim is withdrawn together with the b2 = 7 proposal | argument | prose only |
| SI-37 | b3 = 24 as a labelled input | topology-number | 11:202-222 | 19:1-9 | superseded | para: GEOMETRIC:TCS_G2_187 -> INPUT:B3_ORIGIN_OPEN 11:202-222 | ruling | b3_origin:input_24; b3_seed:seed_24 |
| SI-38 | (15, 24) reachable by Künneth | topology-number | 13:118-181 | arch:829 | withdrawn | "withdrawn when the stabiliser census showed the A₁ model applied outside its domain" arch:829-830 | computed-number (stabiliser census) | prose only |
| SI-39 | b3 = 7 + 3·b2, b3 ≡ 7 mod 12 as the family law | topology-number | arch:861-868 | arch:1410-1414 | withdrawn | "All of these are relabelled "all-plain subfamily". Nothing is deleted" arch:1413-1414 | computed-number (joyce_reachability) | prose only |
| SI-40 | Joyce T^7/(Z/2)^3 at (12, 43), EH resolved | internal | 13:154-162 | 19:1-16 | in-force | "the active path match the found solution" 19:3-4 | ruling | b3_seed:seed_43_joyce |
| SI-41 | other all-plain seeds (0,7), (4,19), (8,31) | topology-number | arch:861-866 | 20:284-295 | unknown | para: b3_seed has five options, priority listed 20:284-295 | none | b3_seed:seed_7_joyce, seed_19_joyce |
| SI-42 | Joyce JDG II Example 4: b2 = 8 + l, b3 = 47 − l (the n = 3 line) | internal | arch:1396-1397 | arch:1421-1424 | unknown | "The seed's selection argument therefore goes back to the author." arch:1421 | argument | prose only |
| SI-43 | chi_eff from the Kummer K3 reading | internal | 16:212-231 | 21:232-281 | unknown | para: χ(K3) = 24 does not reach 144 18:1-37 | computed-number | chi_eff_route (unruled) |
| SI-44 | chi_eff = 144 with n_gen = chi_eff/48 | generations | arxiv:3 | 18:72-118 | unknown | "chi_eff is NOT decided by this ruling — the dichotomy stands" 19:7-8 | ruling | chi_eff_route (unruled) |
| SI-45 | n_gen = b3/8 = 24/8 | generations | arxiv:3 | 14:280-293 | superseded | para: on 43, b3/8 gives 5.375 | computed-number | n_gen_source:b3_over_dim_O |
| SI-46 | n_gen = b2/4 = rank Γ | generations | 16:55-85 | arch:1416-1419 | in-force | "b₂/4 counts the singular involutions only when every family is plain" arch:1417-1418 | ruling | n_gen_source:b2_over_faces |
| SI-47 | three generations as the maximum selects (12,43) uniquely | generations | 16:21-53 | arch:1412-1413 | superseded | "in the full family, holonomy selects the whole n = 3 line" arch:1413 | argument | prose only |
| SI-48 | b2 = 0 for any G2 manifold | topology-number | arch:632-633 | arch:641 | refuted-by-argument | "That is wrong, and is very likely a confusion with b₁" arch:633-634 | argument | no option |
| SI-49 | b2 = 4, the four faces | topology-number | arxiv:3 | 19:16 | superseded | para: topology.b2 = 12 after the seed ruling 19:15-16 | ruling | b3_seed:seed_24 |
| SI-50 | quintessence as a b2 = 4 Kähler modulus | cosmology | 02:299-325 | arch:583 | refuted-by-argument | "A field stabilised at 24.6 TeV cannot be rolling today." arch:584-585 | computed-number (geometry.kahler_over_quintessence_mass) | dark_energy_betti (ruled) |
| SI-51 | quintessence as a C3 axion counted by b3 | cosmology | arch:585-586 | 19:39-51 | in-force | "shift-symmetry protected — a C₃ axion, counted by b₃" arch:585-586 | argument | dark_energy_betti (ruled) |
| SI-52 | w0 = −(b3 − 1)/b3: −23/24 -> −42/43 | cosmology | 01:77-97 | 19:39-51 | in-force | para: on 43, w0 -> −42/43 at 0.94σ | computed-number | b3_seed |
| SI-53 | wa = −1/√b3; rivals −4/√b3 and wa = 0 | cosmology | 01:99-104 | arch:468-473 | retired | "retired this cycle — do not resurrect them without a derivation" 01:99-104 | argument | no option |
| SI-54 | thawing band wa ∈ [−3/b3, −1/b3] (Caldwell-Linder) | cosmology | arch:461-466 | arch:479 | in-force | "Recorded, not repaired, and deliberately so" arch:474 | argument | prose only |
| SI-55 | S8 friction from the moduli coupling | cosmology | 01:106-123 | arch:497-498 | refuted-by-argument | "the moduli coupling was never the relevant knob" arch:497-498 | computed-number (moduli_dm_coupling.py) | no option |
| SI-56 | S8 suppression wired to m_φ = b3·H0 | cosmology | arch:500-507 | arch:509 | never-implemented | "Wiring S₈ to it is a physics ruling and is not taken here." arch:508-509 | none | prose only |
| SI-57 | racetrack fixes Re(T) at 7.086 (or 9.865) | action | 02:173-178 | 19:80-109 | refuted-by-argument | para: not stationary points; AdS minimum at 37.85 11:84-120; no vacuum on 43 19:80-109 | computed-number (racetrack_vacuum.py) | re_t_adoption:calibrated |
| SI-58 | Re(T) as an open modulus | action | arch:1439-1445 | 21:232-281 | unknown | "The adopted geometry carries no leading-order pair that fixes Re(T)" arch:1441-1442 | argument | re_t_adoption (D-005 pending) |
| SI-59 | Kähler potential: −3ln(T+T̄), −2ln Vol7, the 7/3 form | action | 07:81-98 | 07:98 | unknown | para: three inconsistent forms; the 7/3 form is G2-consistent | argument | prose only |
| SI-60 | real form of φ: split G2* or compact | internal | 09:1-31 | arch:1426-1437 | unknown | "The lead recommends `octonion_derived`." arch:1437 | computed-number (0 of 788 params move) | g2_form_convention:all_plus_one / octonion_derived |
| SI-61 | φ outside the G2 orbit | internal | 08:162-224 | 14:52-102 | superseded | para: dim ann 6 vs 14; later read as the split form | computed-number | g2_form_convention |
| SI-62 | Γ = (Z/2)^3 forced by φ; 7 involutions = 7 Fano arcs (4+3) | internal | 06:340-365 | 16:55-85 | in-force | para: R1, R2 06:340-365 | argument | prose only |
| SI-63 | flat b3 = 7; 24 split 7 + 17 | topology-number | 07:1-18 | 07:18 | superseded | "7 + 17, not 12 + 12" 07:1-18 | argument | prose only |
| SI-64 | Yukawas from intersecting singular loci | particle | 16:179 | 16:195 | refuted-by-argument | para: chiral matter needs codim-7 conical points | argument | no option |
| SI-65 | TCS reading of the EH gluing; Co0 Donaldson angle | internal | 16:197 | 16:210 | refuted-by-argument | para: REFUTED by the admissibility predicate 16:197-210 | argument | no option |
| SI-66 | four unpaired forms | internal | 17:158 | 17:188 | refuted-by-argument | "nothing is unpaired, because the map is TOTAL" 17:158 | argument | no option |
| SI-67 | 128 conical assignments R^7/(Z/2)^3 for chirality | particle | 20:32-44 | 21:232-281 | unknown | para: codim-7, off the A1 branch | computed-number | prose only |
| SI-68 | chirality via the heterotic dual of Kummer fibrations, or the shadows as walls | shadows | 21:262 | 21:262 | never-implemented | "or the shadows as walls" 21:262 | none | prose only |
| SI-69 | cross-shadow coupling ∫φ∧F_A∧F_B, 42 of 210 channels | gauge | arch:273 | arch:345 | in-force | para: resolved affirmatively at a stated scope; kill condition retired | argument | prose only |
| SI-70 | moduli indexed by b2 (U(1) gauge) or by b3 clusters | gauge | 06:195-215 | 20:48-60 | unknown | para: b2 counts U(1) gauge fields | argument | moduli_indexing:b2_gauge / b3_clusters |
| SI-71 | θ13 = asin(1/6) | particle | 01:59 | 01:60 | falsified | para: ruling R1 2026-08-25, ~9σ from NuFIT 6.0 | data (NuFIT 6.0) | no option |
| SI-72 | θ13 follows the seed or is calibrated at 24 | particle | 19:111-134 | 19:134 | unknown | para: 4.8351° follow_seed vs 8.6686° calibrated_24 | computed-number | flavour_seed_coupling:follow_seed / calibrated_24 |
| SI-73 | θ13 from modular flavour symmetry | particle | arch:397-406 | arxiv:18-24 | refuted-by-argument | para: obstructed, because G2 moduli are real | argument | no option |
| SI-74 | quark-lepton complementarity | particle | arch:397-406 | arch:406 | falsified | para: 9.155°, +5.3σ | data | no option |
| SI-75 | sterile mixing sin²2θ = 1/b3 | particle | 01:162 | 01:186 | falsified | "FALSIFIED, and still published" 01:162 | data | no option |
| SI-76 | Σmν spectral 0.0598 vs geometric 0.0817 | particle | 01:125-139 | 01:139 | retired | para: spectral rejected by ruling R5 | ruling | no option |
| SI-77 | gaugino-family predictions | particle | 01:141-147 | 01:146 | falsified | "They remain on the books labelled FALSIFIED per the standing ruling" 01:146 | data | no option |
| SI-78 | Cabibbo angle e^{-3/2} | particle | 01:141 | 01:147 | in-force | para: at 2.79σ | data | prose only |
| SI-79 | α_T = 26/10 | other | 01:249-254 | 01:254 | unknown | para: target-first | argument | prose only |
| SI-80 | mirror-world H0, ALP (IAXO), cross-shadow Bell, quantum_bio | cosmology | 01:234-264 | arxiv:37-103 | never-implemented | para: literature pitches; quantum_bio misses by 2× 01:256-264 | none | prose only |
| SI-81 | the k_gimel = b3/2 + 1/π layer (α⁻¹, Higgs VEV, sin²θW, T_CMB, μ) | identity | arch:599-600 | arch:1460-1462 | unknown | "a fit that agrees only at the retired 24" arch:1462 | argument | prose only (D-007 pending) |
| SI-82 | identity ledger: 12 of 15 identities hold only on seed_24 | identity | 21:136-158 | 21:158 | unknown | para: measured per seed | computed-number | b3_seed:seed_24 |
| SI-83 | the 24 is the bulk's spacelike core, not b3 | identity | 19:18-22 | arch:1447-1462 | in-force | "each counts the BULK's 24 spacelike core dimensions of the adopted (24,2) two-time signature" 19:21-22 | ruling | prose only |
| SI-84 | de Sitter uplift from racetrack pairs | cosmology | 21:184-204 | 21:204 | unknown | para: nothing on the menu uplifts to dS | computed-number | no option |
| SI-85 | dark-energy integer scan n = 24, 12, 8, 6, 4, 3 | cosmology | 02:299-325 | 03:35-39 | retired | "It is not a result and must not be promoted." 02:299-325 | computed-number | dark_energy_betti |

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
