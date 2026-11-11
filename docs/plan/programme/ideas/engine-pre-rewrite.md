# Lane engine-pre-rewrite: `H/engine_old.git`, `--all --not <E main>` (48 commits)

Source: `H/engine_old.git` refs `backup-before-rewrite-20260822` (tip 3042cc6, 2026-08-22),
`migration/2026-10-02-metaphysica` (d356096, 2026-10-02) and `migration/2026-10-02-stash-0`
(a62f196, 833f9c1, 2026-09-14). Range 2026-08-14 (3b52e4d) to 2026-10-02 (d356096).
File references below of the form `<commit>:<path>:<line>` are read in that commit's tree.
Recorded 2026-11-11. Record only; no judgement.

## 1. Era summary

- **Start (3b52e4d, 2026-08-14):** bulk 27D (24,1,2) "unified time": 24 space, one shared time, a (0,2)/(2,0) sampler pair (3b52e4d:src/metaphysica/config.py:3822-3824, `D_BULK = 25` legacy, "now signature (26,1), decomposed as (24,1,2)"). Two 13D (12,1) shadows sharing the one time, 12 Euclidean (2,0) bridge pairs (config.py:3826-3831). Internal: G2, TCS "CHNP construction #187" (3042cc6:config.py:4174).
- b2 = 4 (read from h11 = 4), b3 = 24, chi_eff = 144 = 2(4 - 0 + 68) (3042cc6:config.py:4174-4175, 4499). Generations: n_gen = chi_eff/48 = 3, also n_gen = b3/8 (3b52e4d:config.py:587, 2113).
- **End of the backup branch (3042cc6, 2026-08-22):** bulk 26D (24,2), one time per 13D (12,1) shadow, no shared time (3042cc6:config.py:3861-3873); ruling status `STRUCTURAL_CHALLENGED` with three options open, (25,1) / (26,2) / (24,2) (3042cc6:src/metaphysica/simulations/core/canonical_values.py:252-255). 12 (2,0) bridge pairs kept in config; spinor 4096 = Weyl of Cl(24,2).
- Same b2 = 4, b3 = 24, chi_eff = 144 (72 per shadow), n_gen = chi_eff/48; recorded against them: TCS parity obstruction on (4,24), b2 relabelled from h11, n_gen circularity (67fedde, d513ab1). Faces re-anchored to g2 roots 12 = 3+3+3+3 (e9465a3).
- **Migration snapshot (d356096, 2026-10-02, uncommitted work on c8457ff):** seed b3 = 43 (`seed_43_joyce`, adopted 2026-09-22), chi_eff by the K3 reading 48n, n_gen = chi_eff/48 "restates the ruled route b2/4" (d356096:docs/WORDING_MEMO.md:12-17; d356096:src/metaphysica/generators/_dependency_walk_common.py:36-38). This belongs to the E-main era; recorded here only because the snapshot is not in E main.

## 2. Model timeline

| date | commit or file:line | old -> new | reason as recorded |
|------|---------------------|------------|--------------------|
| 2026-08-17 | e4d9778 | bulk bookkeeping ruled: 27D(24,1,2), Cl(24,1) -> 4096, 13 = 4+7+2, chi 144 total / 72 per shadow | "named-apart rulings ... bulk dimension bookkeeping" (e4d9778 body) |
| 2026-08-18 | 1280619 | assessment only: 27D (24,1,2) vs 26D (24,2) one time per shadow; canonical unchanged | "ASSESSMENT with recommendation to adopt -- the canonical table is unchanged pending the author's ruling" |
| 2026-08-19 | 494079c | 27D (24,1,2) -> 26D (24,2); D_ancestral 27->26, time 1->2; shadows (12,1)+(12,1), no shared time | "Canonical ruling v2: D_bulk = 26 = b3 + 2 = D_crit" |
| 2026-08-19 | 494079c | spinor 4096: Cl(24,1) construction -> Weyl of Cl(24,2) (8192/2); per shadow Cl(12,1) 64, 64x64 = 4096 | "chiral, matching the chirality gates" (1280619) |
| 2026-08-19 | 494079c | bridge metric 27x27 -> 26x26, bridges at 0-23, two timelike at 24-25; alpha_T 2.7 -> 2.6 | "the factor 2 in gamma is now a literal dimension count (D_time = 2)" |
| 2026-08-19 | e40487d | lagrangian_master (24,1) -> (24,2), bulk action 27D -> 26D with (12,1)+(12,1) | "lagrangian_master two-time gap" |
| 2026-08-19 | 2101a98 | "unified time" retired (142 sites), 25D -> 26D (MASTER_ACTION_25D -> 26D) | "retired in favour of the two shadow times and the Sp(2,R) constraint" |
| 2026-08-20 | f89cdfc | bulk status STRUCTURAL -> STRUCTURAL_CHALLENGED; options (a) (25,1) (b) (26,2) (c) (24,2) | "(24,2) gives 22 = 6 mod 8 -> none exists" (even unimodular lattice) |
| 2026-08-20 | d513ab1 | h11 = 4 as a G2 invariant -> b2 = 4 (h11 only on a TCS building block) | "A G2-holonomy manifold has no complex structure and therefore no Hodge numbers" |
| 2026-08-20 | 67fedde | recommendation: (24,2) -> (26,2) 28D, partition 13+13+2; TCS obstruction on (4,24) recorded | "II_26,2 exists, is unique, and decomposes as Leech(24) + II_1,1 + II_1,1" |
| 2026-08-20 | 3f3fb63 | fourth argument for (26,2): spinor reality type | "The bulk at (24,2) is complex (6 mod 8): INCONSISTENT with its own shadow decomposition" |
| 2026-08-20 | 2ea3827 | TCS obstruction narrowed: b3 = 24 realisable (Joyce (7,24)); only the pairing (4,24) fails | "(4,24) IS UNREALIZED, NOT REFUTED" |
| 2026-08-20 | cfd6cfe | lattice derivation corrected: II_26,2 gives 14+14 (two (13,1)), not 13+13+2 | "The total is right; the partition is not" |
| 2026-08-20 | d8ad6d1 | 13+13+2 restored as a metric split; only the lattice derivation retracted | "13+13+2 is available as a metric/tangent-space split and the framework may keep 13D(12,1) shadows" |
| 2026-08-21 | e9465a3 | face count: b2 = 4 reading -> g2 roots 12 = 3+3+3+3 | "decouples the face count from the b2 fork, so b3 = 24 stays the only load-bearing topological input" |
| 2026-08-22 | 3042cc6 | backup tip: D_BULK 26, SIGNATURE_BULK (24,2), SIGNATURE_INITIAL (24,2) | config.py:3861-3873 |
| 2026-09-22 (in d356096) | d356096:_dependency_walk_common.py:36-38 | seed b3 = 24 -> b3 = 43 (`seed_43_joyce`) | "The b3_seed fork was ADOPTED at seed_43_joyce on 2026-09-22" |
| 2026-10-02 | d356096:docs/WORDING_MEMO.md:12-17 | chi_eff: K3 reading adopted, 48n, 144 at n = 3 | "Kummer K3 surfaces transverse to the n singular involutions, counted once per shadow" |

## 3. Ideas

| id | idea | kind | first seen | last seen | fate | reason recorded | reason type | today |
|----|------|------|------------|-----------|------|-----------------|-------------|-------|
| EPR-01 | 27D (24,1,2) bulk: one shared time plus spacelike sampler pair | bulk | 3b52e4d:config.py:3823 | 494079c | superseded | "required both b3+2 and b3+3 as 'forced', shadows summed to 25 != 27, spinor was non-chiral" (3042cc6:canonical_values.py:282-287) | argument | no option (bulk_signature has 24_2, 26_2, 25_1) |
| EPR-02 | 25D (24,1) treated as the bulk | bulk | 3b52e4d:config.py:3823 | 2101a98 | superseded | "(24,1) physics-core dimension mislabelled as a bulk" (3042cc6:canonical_values.py:289) | argument | no option |
| EPR-03 | 26D (24,2), one time per 13D (12,1) shadow | bulk | 1280619 | 3042cc6:config.py:3861 | in-force | "26 = b3+2 = D_crit = bulk ... collapse to one statement" (1280619); STRUCTURAL_CHALLENGED from f89cdfc | argument; ruling (494079c) | bulk_signature:24_2 |
| EPR-04 | 26D (25,1), one time, bosonic critical dimension | bulk | f89cdfc | 3042cc6:canonical_values.py:255 | never-implemented | "matches the bosonic critical dimension and the Leech lattice, but abandons two-time" (canonical_values.py:255) | argument | bulk_signature:25_1 |
| EPR-05 | 28D (26,2), two times, 13+13+2 | bulk | 67fedde | d8ad6d1 | never-implemented | "breaks 26 = b3 + 2 (it would need b3 + 4)" (canonical_values.py:255); recommended in 67fedde | argument | bulk_signature:26_2 |
| EPR-06 | Even unimodular lattice existence test p - q = 0 mod 8 on the bulk | lattice | f89cdfc | d8ad6d1 | in-force | "(24,2) gives 22 = 6 mod 8 -> none exists. (25,1) and (26,2) both pass" (f89cdfc) | computed-number (direct computation, f89cdfc) | prose only |
| EPR-07 | 13+13+2 partition derived from II_26,2 = Leech + U + U | shadows | 67fedde | d8ad6d1 | withdrawn | "Only the DERIVATION claim is retracted ... The partition itself reverts to a motivated framework choice" (d8ad6d1) | argument | prose only |
| EPR-08 | Two 14D (13,1) shadows, each dim G2 = 14, Dirac 128x128 = 16384 | shadows | cfd6cfe | d8ad6d1 | never-implemented | "would need a new 7 -> 4 reduction that does not exist" (d8ad6d1) | argument | no option |
| EPR-09 | 2D shared spacelike "breathing" pins between shadows | shadows | 67fedde | d8ad6d1 | unknown | "You cannot peel the time off a hyperbolic plane and leave its spacelike partner behind" (cfd6cfe) | argument | prose only |
| EPR-10 | 12 Euclidean (2,0) sampler bridges as inter-shadow correlators | shadows | 3b52e4d:config.py:3830 | 3042cc6:config.py:3868 | retired | "extra-space mediators permit superluminal shortcuts -- which indicts the current (2,0) spacelike sampler bridges" (1280619) | argument | no option |
| EPR-11 | Shared single time for both shadows ("unified time", no Sp(2,R)) | time | 3b52e4d:config.py:3818-3819 | 2101a98 | superseded | "'unified time' retired in favour of the two shadow times and the Sp(2,R) constraint" (2101a98) | ruling | no option |
| EPR-12 | Sp(2,R) gauge constraint (Bars 2T) controls the second time's ghosts | time | 494079c | f89cdfc | in-force | "Sp(2,R) on (24,2) reduces to ONE 24D shadow (23,1), not two 13D(12,1)" (f89cdfc, challenge) | argument | prose only |
| EPR-13 | Inter-shadow correlation via the other shadow's time (Pettini extra-time mediation); cross-pair Bell prediction | time | 1280619 | 494079c | in-force | "cross-pair Bell correlations added to falsification oracle (SPECULATIVE)" (494079c) | argument | prose only |
| EPR-14 | D_crit = 26 identified with the bulk (26 = b3 + 2) | bulk | 494079c | f89cdfc | in-force | "D_crit = 26 is the ONE-time string at (25,1), where 26 = 24 + 2 is 24 transverse + a LIGHTCONE PAIR" (f89cdfc, challenge) | argument | prose only |
| EPR-15 | 27 = b3 + 3 "forced" derivation | topology-number | e4d9778 | 494079c | retired | "the former b3+3 insertion ... retired" (3042cc6:canonical_values.py:262-264) | argument | no option |
| EPR-16 | The "+2" read three ways: lightcone pair / two-time+Euclidean bridge / 2 Sp(2,R) | bulk | f89cdfc | 3042cc6:canonical_values.py:255 | unknown | "the '+2' currently carries THREE inconsistent readings ... At most one can be right" | argument | prose only |
| EPR-17 | alpha_T = D_bulk/D_string: 2.7 (27D era, gamma fit 10.31324) -> 26/10 = 2.6 | action | e4d9778 | 494079c | superseded | "27D-era gamma fit 10.31324 and alpha_T = 2.7 relabelled superseded/historical in Appendix U" (494079c) | ruling | no option |
| EPR-18 | Pneuma spinor 4096 from odd-D Cl(24,1) | action | e4d9778 | 494079c | superseded | "the odd-D Cl(24,1) construction cannot produce chirality" (1280619) | argument | no option |
| EPR-19 | 4096 = Weyl spinor of Cl(24,2) (Dirac 8192) | action | 494079c | 3042cc6:canonical_values.py:266 | in-force | "(s-t) mod 8 = 6: Majorana yes, Weyl yes, MW no" (1280619) | argument | action_bulk_spinor:weyl (dirac also an option) |
| EPR-20 | Weyl Cl(26,2) = 8192 = 64 x 64 x 2; Majorana-Weyl at (26,2) | action | 67fedde | 3f3fb63 | never-implemented | "Majorana-Weyl becomes available at (26,2) (0 mod 8) and is impossible at (24,2)" (67fedde) | argument | prose only |
| EPR-21 | Spinor reality type: quaternionic x quaternionic = real shadow pair | action | 3f3fb63 | ac21e64 | in-force | "the only one that comes from inside the framework rather than from the literature" (3f3fb63) | computed-number (shadow_clifford.py, ac21e64) | prose only |
| EPR-22 | Bars-Kounnas c_ghost: two-time critical dimension 27/28 at (25,2)/(26,2) | bulk | f89cdfc | 67fedde | in-force | "gives d = 28 exactly with 24 transverse = b3, reproduced independently by Watabiki" (67fedde) | argument | prose only |
| EPR-23 | Nahm's theorem excludes 13D (12,1) for spins <= 2 | shadows | 67fedde | 67fedde | unknown | "afflicts the current framework equally. Recorded as 'tcs_obstruction'" (67fedde) | argument | prose only |
| EPR-24 | TCS G2 manifold "CHNP #187" with (b2,b3) = (4,24) | internal | 3042cc6:config.py:4174 | 2ea3827 | refuted-by-argument | "Crowley & Nordstrom ... force b2 + b3 ODD for every TCS; the claimed (b2,b3) = (4,24) gives 28, EVEN" (67fedde) | argument | no option (g2_construction has joyce_orbifold, fano_tcs) |
| EPR-25 | Extra-twisted connected sum (ETCS) as escape from the parity constraint | internal | 67fedde | 2ea3827 | never-implemented | "published ETCS examples are nearly all 2-connected with b3 >= 42" (2ea3827) | argument | no option |
| EPR-26 | Joyce orbifold pairs near (4,24): (7,24), (4,27), (5,26), (4,19) | internal | 2ea3827 | 2ea3827 | never-implemented | "(7,24) Joyce - keeps b3 = 24 EXACTLY, only b2 moves 4 -> 7. Best." (2ea3827) | argument | b3_seed:seed_19_joyce (for b3 = 19); (7,24) no option |
| EPR-27 | b2 = 7 tied to dim Im(O) and the 7 Fano lines | internal | 2ea3827 | 2ea3827 | never-implemented | "flagged as RESONANCE ONLY (not structure) ... 7 x 3 = 21 incidences does NOT reproduce 12 pins" (2ea3827) | argument | no option |
| EPR-28 | h11 = 4 as the G2 manifold's invariant | topology-number | 3042cc6:config.py:4174 | d513ab1 | refuted-by-argument | "h^{1,1} = 4 can only refer to a TCS BUILDING BLOCK, never to the G2 manifold" (d513ab1) | argument | prose only |
| EPR-29 | 4 faces from b2 = 4 replaced by g2 roots 12 = 3+3+3+3 | topology-number | e9465a3 | e9465a3 | in-force | "exact Lie theory, not numerology: dim g2 = #roots + rank = 12 + 2 = 14" (e9465a3) | computed-number (root system built, e9465a3) | no option |
| EPR-30 | b3 = 24 is the Leech rank (II_26,2 = Leech + U + U) | lattice | 67fedde | cfd6cfe | in-force | "follows from classical classification ... (Milnor/Serre), not from a 2021 preprint" (cfd6cfe) | argument | lattice_24d:leech |
| EPR-31 | Leech 12+12 split via the complex (Eisenstein) Leech lattice | lattice | cfd6cfe | cfd6cfe | refuted-by-argument | "omega is by definition FIXED-POINT-FREE, so Leech^omega = 0" (cfd6cfe) | argument | no option |
| EPR-32 | Leech 12+12 split via Hohn-Mason orbits (K_12 Coxeter-Todd, sqrt2.D_12+) | lattice | cfd6cfe | e9465a3 | never-implemented | "Leech is orthogonally INDECOMPOSABLE ... Treating the halves as independent sectors discards it" (cfd6cfe) | argument | no option |
| EPR-33 | 4 x 3 pin array as a structure on the 24 (M_24) | lattice | 67fedde | cfd6cfe | refuted-by-argument | "4 x 3 IS NOT A STRUCTURE ON 24 ... The 4x3 array is the MiniMOG, which serves M_12" (cfd6cfe) | argument | no option |
| EPR-34 | (Z_3)^6 glue from the Eisenstein rank of K_12 (3^6 = 729) | lattice | e9465a3 | e9465a3 | in-force | "Conclusion right, stated reason wrong ... It is the EISENSTEIN RANK" (e9465a3) | argument | no option |
| EPR-35 | R_perp = [[0,-1],[1,0]] is modular S and the TCS gluing element | identity | d513ab1 | cc8134b | in-force | "R_perp ... is EXACTLY the gluing map of a twisted connected sum G2 manifold" (d513ab1; config.OR_MATRIX) | argument | prose only |
| EPR-36 | OR operator R_perp = Tomita-Takesaki modular conjugation J | identity | cc8134b | e9465a3 | superseded | "R_perp = U(R_W(pi)): the geometric half of J"; "Theta = J would force R_perp = 1" (cc8134b, e9465a3) | argument | prose only |
| EPR-37 | Shadow balance as (K_normal - K_mirror) Omega = 0 with Haag duality | identity | cc8134b | cc8134b | in-force | "the same statement as (H_R - H_L)|TFD> = 0" (cc8134b) | argument | prose only |
| EPR-38 | Type III modular algebras for compactified sectors | other | cc8134b | cc8134b | unknown | "claim is now marked as an open tension needing proof or downgrade" (cc8134b) | argument | prose only |
| EPR-39 | Reflection-positivity gate with shadow swap; obtuse bridge angles are ghosts | shadows | cc8134b | d37c104 | in-force | "MARGINAL_VACUOUS, not PASS: a zero matrix is trivially PSD" (e9465a3) | computed-number (reflection_positivity_gate.py) | no option |
| EPR-40 | R_perp as the reflection-positivity involution | identity | cc8134b | e9465a3 | refuted-by-argument | "RP requires theta^2 = +1; R_perp^2 = -I, so it has order 4" (e9465a3) | argument | no option |
| EPR-41 | Racetrack moduli potential V(theta) = V(pi - theta) degeneracy | action | d37c104 | d37c104 | in-force | "identical to 12 significant figures ... CANNOT distinguish an acute bridge from its obtuse mirror" (d37c104) | computed-number (racetrack_potential) | no option |
| EPR-42 | Topological flux (Chern-Simons) cross-shadow coupling | gauge | d37c104 | d37c104 | never-implemented | "option 2 (topological flux exchange) is simply not implemented anywhere" (d37c104) | none | no option |
| EPR-43 | Theta = C.T on Cl(12,1), quaternionic (B B* = -1) | identity | ac21e64 | ac21e64 | in-force | "Decision 2 is ADVANCED, NOT CLOSED" (ac21e64) | computed-number (shadow_clifford.py) | prose only |
| EPR-44 | n_gen = chi_eff/(2 b3) and alpha_leak = 1/sqrt(chi_eff/b3) | generations | 3b52e4d:config.py:587 | 67fedde | refuted-by-argument | "chi_eff is DEFINED as 6*b3, so n_gen = chi_eff/(2*b3) = 3 for ANY b3" (67fedde) | computed-number (checked b3 12..155) | n_gen_source:chi_eff_over_48 |
| EPR-45 | n_gen = b3//8 as the only b3-dependent route | generations | 3b52e4d:config.py:2113 | 67fedde | in-force | "The only generation route that genuinely uses b3 is n_gen = b3//8" (67fedde) | argument | n_gen_source:b3_over_dim_O |
| EPR-46 | Printed n_gen = chi_eff/(4 b3) | generations | 5c2eac8 | 5c2eac8 | retired | "4*b3 = 96, so the printed formula evaluates to 1.5. The code has always divided by 48" (5c2eac8) | computed-number (display arithmetic) | no option |
| EPR-47 | n_gen = chi_eff/48 restates b2/4; K3 reading chi_eff = 48n | generations | d356096:docs/WORDING_MEMO.md:12 | same | in-force | "it is not a second derivation and not an index theorem for chirality" (WORDING_MEMO.md:15-16) | ruling | chi_eff_route:k3_reading; n_gen_source:b2_over_faces |
| EPR-48 | b3 = 43 seed (Joyce) replaces 24 | topology-number | d356096:_dependency_walk_common.py:36 | same | in-force | "The b3_seed fork was ADOPTED at seed_43_joyce on 2026-09-22" | ruling | b3_seed:seed_43_joyce |
| EPR-49 | b3 "derivation" callout summing to 24 | topology-number | 891917d | 891917d | withdrawn | "b3 'derivation' callout summed to 49, not 24 -- replaced with honest assertion" (891917d) | computed-number (audit recompute) | b3_origin:input_24 |
| EPR-50 | theta13 = asin(1/6) = 9.594 deg | particle | e4d9778 | 3042cc6:canonical_values.py:135 | falsified | "FALSIFIED at 8.8 sigma (IO) / 9.3 sigma (NO); retained in neutrino_algebraic" | data (NuFIT 6.0) | no option |
| EPR-51 | theta13 from quark-lepton complementarity, sin = lambda_C/sqrt2 (9.155 deg) | particle | f89cdfc | canonical_values.py:137 | falsified | "quark-lepton complementarity -- FALSIFIED at 5.3 sigma" | data (NuFIT) | no option |
| EPR-52 | theta13 ruled NOT_PREDICTED (look-elsewhere) | particle | f89cdfc | canonical_values.py:102 | in-force | "143 candidates inside 1 sigma, ~53 expected BY CHANCE - no excess" (f89cdfc) | computed-number (6243-form enumeration) | no option |
| EPR-53 | Modular flavour symmetry for theta13 | particle | f89cdfc | f89cdfc | refuted-by-argument | "modular flavour symmetry needs SL(2,Z) on a COMPLEX modulus while G2 moduli are REAL" (f89cdfc) | argument | no option |
| EPR-54 | Cabibbo lambda = exp(-pi/2); canonical exp(-3/2) | particle | e4d9778 | canonical_values.py:147 | falsified | "exp(-pi/2), the zero-var candidate, FALSIFIED at 25.5 sigma" | data (PDG 2024) | no option |
| EPR-55 | Gaugino / racetrack Cabibbo candidates (N1 = 24, N2 = 23) | particle | 68d95e1 | d356096:gaugino_condensation.py:363 | falsified | "all three candidates miss PDG lambda_W = 0.22500 +/- 0.00067" (d356096 hunk) | data (PDG 2024) | flavour_seed_coupling:calibrated_24 (nearest) |
| EPR-56 | delta_CP = arc_stab*pi/chi = pi/6 (G2 triality) | particle | 0b21f3e | 0b21f3e | in-force | "The search rediscovered a formula that is present" (0b21f3e) | computed-number (shape_search.py) | no option |
| EPR-57 | theta23 = aut_fano*n_fano/arc_stab = 49 | particle | 0b21f3e | 0b21f3e | refuted-by-argument | "A pure unit artefact" (theta23 in degrees) (0b21f3e) | computed-number (shape_search.py) | no option |
| EPR-58 | Free parameters as simple ratios of geometric primitives | other | 0b21f3e | 0b21f3e | refuted-by-argument | "Result across 32 numeric targets at tol = 1e-4: ZERO significant matches" (0b21f3e) | computed-number (shape_search.py, 1213 expressions) | no option |
| EPR-59 | w0 thermal mechanism -0.8528; canonical -(b3-1)/b3 | cosmology | e4d9778 | canonical_values.py:24-25 | retired | "thermal -0.8528 1 var 1.56 sigma retired mechanism" | ruling | dark_energy_mechanism:thawing_quintessence (canonical form) |
| EPR-60 | wa = -4/sqrt(b3) co-associative projection (x4 / x b2) | cosmology | e4d9778 | canonical_values.py:72 | superseded | "post-DESI graft -> kept as RETRODICTED variant" | ruling | no option |
| EPR-61 | H0 from the Ricci golden-angle form; O'Dowd composite 71.55 canonical | cosmology | e4d9778 | e4d9778 | superseded | "ricci golden-angle form is 3.5 sigma SH0ES / 18.6 Planck" (e4d9778) | data (SH0ES, Planck) | h0_route:ricci_flow; h0_route:odowd_composite |
| EPR-62 | n_s from Re(T) slow roll 0.9996 | cosmology | e4d9778 | canonical_values.py:246 | falsified | "Re(T) slow-roll variant, FALSIFIED at 8.3 sigma" | data (Planck 2018) | spectral_index_route:re_t_slow_roll |
| EPR-63 | sum m_nu under inverted ordering 0.0994 eV kept canonical | particle | e4d9778 | canonical_values.py:187 | in-force | "EXCEEDS the DESI bound and is ruled to stay canonical with status TENSION" (e4d9778) | data (DESI) | no option |
| EPR-64 | sin2 theta_W geometric 0.23190 split from MS-bar input | gauge | e4d9778 | e4d9778 | superseded | "the 267-sigma internal clash was tree-vs-MS-bar scheme mixing" (e4d9778) | computed-number (registry clash) | no option |
| EPR-65 | 288 roots: two fitted splits 135+153 and 125+163 | other | e4d9778 | canonical_values.py:295 | in-force | "TWO distinct fitted decompositions, never interchangeable" | ruling | no option |
| EPR-66 | ALP "Principia Metric" as unavoidable consequence | particle | 3b52e4d | 3b52e4d | withdrawn | "Downgrade ALP Principia Metric from 'Unavoidable consequence' to 'SPECULATIVE ANSATZ'" (3b52e4d) | argument | no option |
| EPR-67 | [[24,12,8]] Golay CSS code claim | other | 1e4c96f | 1e4c96f | withdrawn | "label full [[24,12,8]] CSS claim SPECULATIVE ... naive self-dual CSS gives k=0" (1e4c96f) | argument | no option |
| EPR-68 | Lambda suppression e^{-2 pi 26} | cosmology | 891917d | 891917d | unknown | "Lambda derivation flipped the e^{-2pi*26} suppression into an enhancement" (891917d) | computed-number (audit recompute) | no option |

## 4. Owner's candidates

| # | candidate | status in this lane |
|---|-----------|---------------------|
| 1 | Three shadows instead of two | not seen (subject and body grep "three shadow / 3 shadows": no hit) |
| 2 | Shadows in pairs, or of different dimension or make-up | seen: two 14D (13,1) shadows vs two 13D (12,1) plus 2D shared sector (cfd6cfe, d8ad6d1); shadow pair as a real spinor product (3f3fb63, ac21e64); Sp(2,R) gives one 24D (23,1) shadow (f89cdfc). No unequal-shadow model seen |
| 3 | Two times, one in the bulk and one for the shadows | partly seen: 27D (24,1,2) with one shared shadow time plus a (0,2) sampler pair (3b52e4d:config.py:3818-3824); no bulk-time-plus-shadow-time model seen |
| 4 | Three times | not seen ("three time / 3 times" grep: no hit) |
| 5 | Two times, one per shadow: 26D (24,2), two 13D (12,1) | seen: assessed 1280619, adopted 494079c, challenged f89cdfc, end-of-branch 3042cc6:config.py:3861-3873 |
| 6 | 27D (24,1,2) and other bulk dimensions | seen: 27D (24,1,2) retired 494079c; 25D (24,1) relabelled (canonical_values.py:289); 26D (25,1) and 28D (26,2) options (f89cdfc, 67fedde); 14D (13,1) shadows (cfd6cfe). 12D, 11D, 10D: not seen except D_string = 10 in alpha_T = 26/10 (494079c) |
| 7 | Other internal spaces | seen: TCS G2 and its parity obstruction (67fedde), ETCS (2ea3827), Joyce orbifolds (7,24) (4,27) (5,26) (4,19) (2ea3827), Leech and II_26,2 (67fedde, cfd6cfe), K_12 Coxeter-Todd (cfd6cfe), Fano lines (2ea3827), Spin(7) spinor facts (74838ee, prose fix only). Calabi-Yau: only "CY3 x S1/Z2" alternative in a config comment (3042cc6:config.py:3875); Niemeier: not seen |

## 5. Gaps

- Pipeline, constants and validation commits are not ideas: CODATA/PDG updates (440162e, 911c71a, 40b5e64, 0b4b98b), build and CI fixes (cabcf6f, 3066d90, 38feb43, b3fdc6e, 3042cc6), SSOT/validation layer (c132087, 5382983, ee9d9da, 31518a3, 0b1edd0, 68d95e1), test-hardening (9f02840), loader refactors (f47caee, 68cbe5e, 37904db), IDENTITY/INPUT verdict classes and EML denominator fix (f89cdfc, d513ab1, 0b1edd0). Read from bodies only; no rows.
- Not opened: peer-review register appends 5cb9340, 79cafbd, 9a28f62 and the docs `PEER_REVIEW_MASTER_LIST.md` / `TWO_TIME_ASSESSMENT.md` they write (those files are in E and belong to lane engine-docs). 891917d, 74838ee, e40487d, 1e4c96f: bodies read to the first 14 lines only; their remaining prose fixes (124 patches in 74838ee) not paged.
- d356096 (102 files, +10529/-5620): only the model-term grep of the non-JSON hunks and three file:line reads; its content is the E-main era after 2026-09-22 and overlaps lanes engine-2026-09 / engine-2026-10. a62f196 and 833f9c1 (stash of data/constants JSON edits): stat only.
- 3b52e4d, 72663df, 2101a98 bodies read; no model content beyond the rows above.
- "today" mapping read only fork and option ids in `src/metaphysica/simulations/core/variants/catalogue/` (and `adopted.py:206-225` for bulk_signature); option consequences not read. "nearest" marks a mapping by name, not checked.
- Milestone grep run on the first (3b52e4d) and the backup tip (3042cc6) only; the intermediate version step 494079c is taken from its body, not a tree grep.
