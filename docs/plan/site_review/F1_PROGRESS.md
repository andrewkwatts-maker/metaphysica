# F1 progress

Done: headline statistics from one source (headline_stats.py, generate_statistics, index, certificates, parameters, Appendix F); paper scoreboard leak (conclusions.py); stale claims (58+, 55 predictions, DESI, ghosts, v24.2 on index/sections, compression ratio shown as "not available in this build", ruling note); faq, beginners-guide, falsification, simulations, visualization-index, theory-diagrams, pm-plots-loader fixes; mismatches bare-number skip; core_formulas dangling ids (master-action-26d left for F5) with test.

Not done: task 5 bridge-channel footer links (page generator not in this repo; only PrincipiaMetaphysica/Pages/bridge-channel.html); "125 constants" and remaining v24.2 strings in the paper; registry literals abstract.compression_ratio=131 and validation.* in abstract.py; statistical_rigor_validator.py and pm-falsification.js checks; scope wording for "3030.1 over 4 dof"; tests for conclusions lookup, mismatches skip, plots loader; before/after screenshots; theory-diagrams details edit unverified.

Data conflict: artifacts (chi2 2.24e9, 63 rows, 36/42 locked) differ from CHANGELOG 2.4.0 (126,749, 65 rows, 41/43). Bound to artifacts.

Failing test: tests/test_action_forks.py::test_adopted_option_of_each_fork_is_the_ladder_today (adopted.py, not an F1 file; other lane).
