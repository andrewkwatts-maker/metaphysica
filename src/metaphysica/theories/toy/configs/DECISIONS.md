# Toy theory -- decision log

The toy's decisions, in the same format as the PM decision log: one heading per
entry, `## D-NNN · date · KIND — title`; several entries may share an id (a
RESULT or an ACCEPT appended under the pre-registration). `accept`, `retire`
and `reinstate` append here; nothing is ever edited or deleted.

## D-001 · 2026-10-02 · RULINGS — the toy's founding choices

The coupling is derived from the seed (`coupling_route=geometric`), the light
mass comes from a seesaw (`mass_rule=seesaw`), and no extra field is carried
(`extra_param=none`). `coupling_route=numerology` is RULED OUT for certain: a
typed number with no mechanism behind it. Render policy `plain`.

## D-002 · 2026-10-02 · RULINGS — regulator and matching

A continuum cutoff (`cutoff=planck`) and one-loop matching
(`matching=one_loop`). `cutoff=lattice` is DEMOTED but reassessable: it breaks
the Lorentz identity at O(a^2), which an improved action could remove.

## D-003 · 2026-10-02 · PATH ASSESSMENT · PRE-REGISTERED — the toy's decision rule

The toy's assessment configuration is `configs/assessment.yaml`; the decision
rule is validity > closure > consistency > elegance > data (tie-break only). A
complete tie keeps the active path. The known answer is stated in the toy's
module docstring before any run.
