# Audit lane sim-geometry-closure

1. Scope note. Read: g2_closure.py (H1-H8 report, run live: CLOSED_BY_THEOREM, no failure), g2_geometry.py (header, __init__, run paths, section sizes), g2_differential fork reads, closed_geometry/provenance.py, flat_form_involution_map header, importer greps, artifact rows for topology.*, geometry.* and the g2 formulas.
2. Not reached: bodies of joyce_*, eguchi_hanson, orbifold_gauge_scan, glued_orbit_scan, derived_contribution_table, kummer_*, figures/; the get_section_content prose of g2_geometry (770 lines) and the paper text of Sections 2 and 2.4 were sized, not read line by line.
3. The artifacts predate the last commits (geometry.* rows still show 24 / 144 / 8192); findings relying on them say so.

## 1. Findings

| id | file:line | category | sev | what is wrong | evidence | fix |
|---|---|---|---|---|---|---|
| sim-geometry-closure-01 | g2_geometry.py:224,255,625 | correctness | critical | topology.mephorash_chi (chi_eff) is computed from literal off-path TCS Hodge numbers h11=4, h31=68, so it is 144 for any seed and does not follow n_gen = b2/4 or the K3 reading 48n it is labelled with | `self.h31 = 68`; `self._chi_eff = self._chi_eff_from_hodge` | compute chi_eff = 48 * n_gen from the resolved n_gen; keep the Hodge route only as a labelled cross-check |
| sim-geometry-closure-02 | formulas.json 'euler-characteristic' (g2_geometry.py:1833) | stale_path | high | formula (2.2) chi_eff = 2(h11-h21+h31) is category DERIVED though its inputs are off-path TCS data and a Joyce orbifold has no h21/h31 | `'category': 'DERIVED'`, description admits "OFF-PATH route" | make the K3 formula 48n the DERIVED row; relabel the Hodge one retired |
| sim-geometry-closure-03 | g2_geometry.py:223-224,258 | stale_path | high | topology.K_MATCHING = h11 = 4 is published beside b2 = 12; the code admits the identity K = h11 = b2 breaks | `self._K_matching = self.h11`; comment "stays 4 while b_2 becomes 12" | drop from active outputs or derive from the K4 / 12-bridge structure |
| sim-geometry-closure-04 | g2_geometry.py:264-265 | stale_path | high | k_gimel = b3/2 + 1/pi and c_kaf = b3(b3-7)/(b3-9) are numerology calibrated at b3 = 24 (D-007) but evaluated at 43; artifact has topology.k_gimel 21.818 and geometry.k_gimel 12.318: two values for one name | artifact rows; comment "CALIBRATED at the off-path seed b_3 = 24" | RETIRE-FROM-PAPER; one labelled calibration row; delete geometry.* duplicates |
| sim-geometry-closure-05 | g2_geometry.py:230 | stale_path | high | d_over_R = 0.12 is a literal "TCS-gluing estimate; off-path", published as topology.d_over_R (T_OMEGA 0.12 ESTABLISHED) | `self._d_over_R = 0.12  # ... off-path` | register as INPUT with source or remove; a Joyce orbifold has no gluing neck |
| sim-geometry-closure-06 | g2_geometry.py:434; FormulasRegistry.py:653 | stale_path | high | required input geometry.elder_kads = 24 (artifact) while topology.elder_kads = 43; registry holds `"elder_kads": {"value": 24` | `return ["geometry.elder_kads"]` | read b3 via b3_path.seed_values; fix registry entry; drop the duplicate |
| sim-geometry-closure-07 | g2_geometry.py:531,611,619 | fallback | high | broad `except Exception` swallows EML metric / lattice failures and sets holonomy_valid from a different routine; `_lattice_verification` hard-coded None | `except Exception: holonomy_valid = self._validate_g2_holonomy()` | catch the specific error or fail; read validity from closure_report |
| sim-geometry-closure-08 | g2_geometry.py:603-621 | dead_code | high | Leech points built, result discarded, errors passed; asserts nothing | `_leech_ok = len(leech_pts) > 0` / `except Exception: pass` | delete the block |
| sim-geometry-closure-09 | g2_closure.py:476-480 | fallback | high | `_resolved(name, fallback)` swallows any exception and substitutes a literal ("joyce_orbifold", "octonion_derived", "?"), so a broken fork read silently returns the active-path answer | `except Exception: return fallback` | call resolve directly; drop fallbacks |
| sim-geometry-closure-10 | g2_differential.py:344,517 | fallback | high | same silent fallback to "octonion_derived" for the form-convention fork | `choice = "octonion_derived"        # must match the adopted branch` | read via resolve(); fail early |
| sim-geometry-closure-11 | joyce_contributions.py:90 | pipeline | high | env var METAPHYSICA_JOYCE_TABLE can replace the cited table that yields (b2,b3) = (12,43); a build with it set changes published Betti numbers | `os.environ.get("METAPHYSICA_JOYCE_TABLE")` | make the override test-only, or record the table hash in the artifact |
| sim-geometry-closure-12 | g2_closure.py:509-517 | fallback | medium | `except KeyError` turns any missing key (a bug) into "unmeasured"; fails closed so safe, but hides a coding fault | `except KeyError: row = {"holds": False ...` | guard on ctx["resolution"] presence only |
| sim-geometry-closure-13 | closed_geometry/provenance.py:185-186 | inconsistency | medium | "144 counts hidden K3 surfaces: three in each mirror half, each contributing 24, once for each half" is worded differently from the entry at line 182 (chi_eff = 2 x sum chi(K3) = 48n) | lines 182 vs 185 | one wording: chi_eff = 2 * n_gen * 24 |
| sim-geometry-closure-14 | closed_geometry/provenance.py:249-252 | stale_path | medium | prose "critical dimension is 27-28" sits in a withdrawal entry; it is labelled CORRECTION but is a stale-number risk if lifted into the paper | `critical dimension is 27-28` | keep in an appendix; never in body text |
| sim-geometry-closure-15 | g2_geometry.py (3253 lines; get_section_content 770, get_formulas 424) | solid | medium | one file holds topology, certificates, learning materials, references and a 770-line section | line counts | split into sections / formulas / certificates / references modules |
| sim-geometry-closure-16 | g2_differential 1176, orbifold_gauge_scan 1087, glued_orbit_scan 736, eguchi_hanson 676, derived_contribution_table 619, topology.py 559, g2_closure 528 | solid | medium | files over about 500 lines | wc -l | split per concept |
| sim-geometry-closure-17 | g2_geometry.py:190-262 | fluff | medium | docstrings narrate history ("A FALSE PROVENANCE, CORRECTED", "the old code set") in active code | docstring text | move history to decision records; keep one active-path sentence |
| sim-geometry-closure-18 | Sections 2 / 2.4 (closed_geometry/*) | fluff | medium | the same points (b3 = 43 not 24, K3 reading, holonomy) are restated in overview, findings, provenance, topology, selection, simulation and g2_geometry's section: at least five repetitions | "b_3 = 24" present in 8 closed_geometry files | paper keeps one H1-H8 table plus the three conclusions; correction history to an appendix |
| sim-geometry-closure-19 | flat_form_involution_map.py | dead_code | medium | no src importer, only its own test; a 272-line refutation of a side claim | grep: only tests/test_flat_form_involution_map.py | RETIRE-FROM-PAPER; archive |
| sim-geometry-closure-20 | conical_point_search.py, holonomy_wording_audit.py | dead_code | medium | no src importer; tests only | grep: tests only | move to tests/ or archive |
| sim-geometry-closure-21 | g2_closure.py H5 (line 448) | correctness | medium | r^-4 decay is a numeric fit (-4.00009) with tolerance; exact analytically, so fit is a check, not proof | `fitted_exponent -4.000087` | report as numerical check beside the analytic statement |
| sim-geometry-closure-22 | g2_closure.py:497-501 | pipeline | medium | cache key uses `_resolved("b3_seed","?")`; failure to resolve shares one cache slot | `key = (convention, _resolved("b3_seed", "?"))` | key on resolved values; fail if unresolved |
| sim-geometry-closure-23 | g2_closure.py:19 vs plan | inconsistency | low | plan says H2 source is metric_by_convention; code uses real_form_report | plan table H2 | update the plan |
| sim-geometry-closure-24 | g2_geometry.py:3059 | fallback | low | catch-all `except Exception as exc` records a string and continues | `# a seed the construction does not reach` | catch ValueError only |
| sim-geometry-closure-25 | g2_geometry.py:84 | style | low | broad import `except Exception` | line 84 | narrow to ImportError |

## 2. Table A, module verdicts

| module | registers | reads forks | verdict | reason |
|---|---|---|---|---|
| g2_closure.py | H1-H8 report; feeds certificates | yes (via swallowing `_resolved`) | FIX | remove fallbacks (09, 22); core of closure |
| closed_geometry/* | closure sections, site overview, certificate | yes | FIX | text mostly active-path and labels retired items; trim repetition (18), fix 13; split topology.py |
| g2_geometry.py | topology.b2, elder_kads, mephorash_chi, n_gen, k_gimel, K_MATCHING, d_over_R; formulas g2-holonomy, euler-characteristic, betti-numbers | b2/b3/n_gen yes; chi_eff, K, d/R, h-numbers no | FIX | 01-08, 15 |
| g2_differential.py | G2 forms, real form report | partly | FIX | 10, 16 |
| joyce_orbifold, joyce_resolution, joyce_reachability | Betti derivation, admissible classes | yes | KEEP | measured, tested with controls |
| joyce_contributions.py | cited table | yes | FIX | 11 |
| eguchi_hanson.py, fundamental_group.py | H5, H6 | no | KEEP | split eguchi_hanson by size |
| glued_orbit_scan.py | H8 | convention | KEEP | only t = 0, 0.1 sampled; split by size |
| twisted_form_basis, metric_pairing, intersection_tensor, exterior_algebra, multilinear_degree_audit | supporting algebra | no | KEEP | imported by flux, zero-mode, bridge code |
| kummer_index, kummer_transverse | K3 reading of chi_eff, n_gen | should | KEEP | make g2_geometry use it (01) |
| family_topology, half_shift_enumeration, derived_contribution_table | Joyce family counts | no | KEEP (derived_contribution_table: split) | used by bridge code |
| orbifold_gauge_scan | gauge-source scan for D-011 | no | RETIRE-FROM-PAPER | 1087 lines; gauge source open, adopted action has no bulk gauge term |
| flat_form_involution_map | refutes 4 = 4 | no | RETIRE-FROM-PAPER | 19 |
| conical_point_search, holonomy_wording_audit | tests only | no | DELETE or move to tests | no src importer (grep) |
| figures/* | SVG helpers | no | KEEP | small |

## 3. Table B, path-dependent literals

| file:line | literal | should read | reaches output |
|---|---|---|---|
| g2_geometry.py:222-224 | h11=4, h21=0, h31=68 | none: chi_eff = 48 * n_gen | yes (mephorash_chi, formula 2.2) |
| g2_geometry.py:258 | K_matching = h11 (4) | K4 structure or retire | yes |
| g2_geometry.py:260 | d_over_R = 0.12 | INPUT row with source | yes |
| g2_geometry.py:264-265 | k_gimel, c_kaf of b3 | one calibration row | yes |
| g2_geometry.py:600-610 | EML d/R = 12/100, chi route (144) | resolved values | yes |
| FormulasRegistry.py:653 | elder_kads 24 | b3_seed fork (43) | yes (latex, datasheets) |
| g2_closure.py:476-500 | "joyce_orbifold", "octonion_derived", "?" | resolve() | masks failures |
| g2_differential.py:344,517 | "octonion_derived" | resolve("g2_form_convention") | yes |
| artifact geometry.spinor_26d 8192, pneuma_components 64, chi_eff_total 144, roots_total 288 | stale vs 4096 Weyl | rebuild; read action | yes (artifact predates commits) |

## 4. Closure H1-H8 (live run: all hold, CLOSED_BY_THEOREM)

Measured by code that can fail:
- H1 Gamma preserves phi0: exhaustive sign-flip enumeration, holds iff order 8 (partly structural: gamma_elements is built from phi).
- H2 Hitchin metric (7,0): real_form_report.
- H3 singular components T^3 x C^2/Z2: resolution_report, orbit size = |Gamma|/2.
- H4a triple definiteness; H4b EH triple closed in one orientation only (with control); H4c d phi = d*phi = 0 on EH x T^3.
- H5 EH Ricci exactly zero (exact) and r^-4 decay (numeric fit -4.00009).
- H6 pi_1 finite (computed) and b1 = 0.
- H7 Cl(7): exactly one invariant spinor over all lifts.
- H8 glued form in the COMPACT orbit at t = 0 and 0.1 (140 points); a sampled proxy for Joyce's torsion and injectivity-radius estimates, which are not measured.

Cited only: existence (Joyce 2000 Thm 11.6.1), Ricci-flat (Bonan), Hol = G2 (Joyce 1996 II Prop 1.1.1).

Still open: b2 = 12, b3 = 43 come from a cited contribution table (overridable, finding 11), not independent geometry; the moduli count (43 associative moduli) is tied to no parameter and the stray h31 = 68 contradicts it; no explicit metric exists; D-011 / D-028 gauge source (N=4 SYM on the singular loci) has no term in the adopted action (no bulk gauge sector); lattice obstruction and Sp(2,R) remain open per the Facts.

## Verification
sim-geometry-closure-01 | confirmed | g2_geometry.py:224/257 h31=68 literal, _chi_eff = _chi_eff_from_hodge; line cited 224 is the h31 literal, assignment at 257; value equals 48n only by coincidence at n=3 (code comment admits it).
sim-geometry-closure-02 | confirmed | formula ~1833 category DERIVED while description states OFF-PATH route.
sim-geometry-closure-03 | partly | _K_matching = h11 = 4 at line 271 (cited 258); code records _k_matching_equals_b2 False, so the mismatch is flagged, but the value is still published.
sim-geometry-closure-04 | confirmed | lines 276-278 k_gimel, c_kaf computed at active b3=43 though comment says calibrated at b3=24; 12.318 repeated in generators/registry.
sim-geometry-closure-05 | confirmed | line 273 literal 0.12 marked off-path, also in EML path; line cited 230 is wrong.
sim-geometry-closure-06 | confirmed | required_inputs returns geometry.elder_kads (line 434); FormulasRegistry.py:653 and dependency_resolver.py:909 hold 24 vs topology 43.
sim-geometry-closure-07 | partly | the holonomy_valid catch-all is at ~line 611 (EML path), not 531 (531 is the lattice_verification except, which sets None); real but the fallback swaps to _validate_g2_holonomy.
sim-geometry-closure-08 | confirmed | lines ~603-619: _leech_ok computed then unused, except Exception: pass.
sim-geometry-closure-09 | confirmed | g2_closure.py:470 except Exception returns fallback.
sim-geometry-closure-10 | confirmed | g2_differential.py:344 silent fallback to octonion_derived; comment says it must match adopted branch.
sim-geometry-closure-11 | partly | env var override real (joyce_contributions.py:90), but the table passes through validate_table citation checks; risk is provenance, not an unchecked table.
