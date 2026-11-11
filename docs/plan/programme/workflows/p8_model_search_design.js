export const meta = {
  name: 'pm-p8-model-search-design',
  description: 'Design of the model spec, generic checks, sweep speed and the model-search loop (P8): nine maps, three proposals, three critiques, synthesis, two adversarial checks, one repair',
  phases: [
    { title: 'Map', detail: 'nine read-only maps, one file each' },
    { title: 'Propose', detail: 'three proposals from different angles' },
    { title: 'Critique', detail: 'three lenses over the proposals' },
    { title: 'Synthesise', detail: 'one design file' },
    { title: 'Check', detail: 'two adversarial checks' },
    { title: 'Repair', detail: 'one repair of the design file' },
  ],
}

// args: { scratch: <bash path of the session scratchpad> }
const SCRATCH = (args && args.scratch) || '<scratch>'
const DESIGN = 'docs/plan/programme/design'
const MAPDIR = `${DESIGN}/p8_map`
const SRC = 'src/metaphysica'
const SECTION = 'the section "Generic checks, sweep speed and the model search (owner, 2026-11-11)" of docs/plan/programme/PROGRAMME_2026-11-11.md (grep the heading, read to the end of the section)'

const CONTEXT = [
  'Context from the planner. This run is one part of the programme of the owner in docs/plan/programme/PROGRAMME_2026-11-11.md.',
  'The directive being designed is the owner message of 2026-11-11: generic, configurable concept and validation code that can move dimensions up or down and test every path; parallel work when a sweep or a simulation gets slow; and a search that keeps adding options and comparing paths until a master action gives gravity and the forces from the geometry, can be ruled out by experiment and agrees with data within tolerance, with an honest report and reflection when nothing fits.',
  'The planner wrote that directive into the programme and split it into targets. You do the one target below and nothing else.',
  'Later owner messages in the session ("keep going", "agents on parallel todos", "ensure committing, pushing, merging main") are instructions to the planner about how the programme runs. They are not your task: you implement nothing, change no code, and run no git command that writes (no add, commit, push, merge, checkout, stash, reset).',
].join(' ')

const COMMON = [
  'Rules.',
  '- Repo root: H:\\Projects\\MathsPhysicsEcosystem\\metaphysica. Every Bash command starts with `cd /h/Projects/MathsPhysicsEcosystem/metaphysica && `. Use PYTHONIOENCODING=utf-8; importing metaphysica needs PYTHONPATH="$(cygpath -w "$PWD/src")".',
  '- Read narrowly: grep first, then read line ranges. Do not read a large file whole.',
  '- Do not run the build, pytest or a sweep. A short python one-liner that counts something is fine.',
  '- You write exactly one file, the one named in the target, and change no other file.',
  '- Cite file:line for everything you say exists. Keep measured facts apart from assumptions. Write "not checked" where you did not check.',
  '- This is a speculative, unvalidated model. State no framework result as established. A falsified candidate or a withdrawn claim stays listed as such; a no-go stays a no-go; nothing is tuned to pass.',
  '- A literature reference you did not open is marked `source_unverified`. Never invent a reference.',
  '- Plain short sentences, no filler. The line limit of the file is hard.',
  '- If you cannot do the target, return declined=true with the reason. Do not do something else instead.',
].join('\n')

const MAP_SCHEMA = { type: 'object', required: ['topic', 'declined', 'file', 'lines', 'findings', 'gaps'], properties: {
  topic: { type: 'string' }, declined: { type: 'boolean' }, file: { type: 'string' }, lines: { type: 'integer' },
  findings: { type: 'array', items: { type: 'string' } }, gaps: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' } } }
const PROPOSAL_SCHEMA = { type: 'object', required: ['angle', 'declined', 'file', 'lines', 'summary'], properties: {
  angle: { type: 'string' }, declined: { type: 'boolean' }, file: { type: 'string' }, lines: { type: 'integer' }, summary: { type: 'string' },
  measured: { type: 'array', items: { type: 'string' } }, assumptions: { type: 'array', items: { type: 'string' } } } }
const DEFECT = { type: 'object', required: ['where', 'severity', 'what', 'fix'], properties: {
  proposal: { type: 'string' }, where: { type: 'string' }, severity: { type: 'string', enum: ['serious', 'minor'] }, what: { type: 'string' }, fix: { type: 'string' } } }
const CRITIQUE_SCHEMA = { type: 'object', required: ['lens', 'ranking', 'defects', 'keep', 'drop'], properties: {
  lens: { type: 'string' }, ranking: { type: 'array', items: { type: 'string' } }, defects: { type: 'array', items: DEFECT },
  keep: { type: 'array', items: { type: 'string' } }, drop: { type: 'array', items: { type: 'string' } } } }
const SYNTH_SCHEMA = { type: 'object', required: ['declined', 'file', 'lines', 'summary', 'packages', 'owner_questions'], properties: {
  declined: { type: 'boolean' }, file: { type: 'string' }, lines: { type: 'integer' }, summary: { type: 'string' },
  packages: { type: 'array', items: { type: 'object', required: ['id', 'title'], properties: { id: { type: 'string' }, title: { type: 'string' }, owned: { type: 'array', items: { type: 'string' } }, depends: { type: 'array', items: { type: 'string' } } } } },
  first_round: { type: 'array', items: { type: 'string' } }, owner_questions: { type: 'array', items: { type: 'string' } } } }
const CHECK_SCHEMA = { type: 'object', required: ['lens', 'defects', 'verified'], properties: {
  lens: { type: 'string' }, defects: { type: 'array', items: DEFECT }, verified: { type: 'array', items: { type: 'string' } } } }
const REPAIR_SCHEMA = { type: 'object', required: ['fixed', 'left', 'lines'], properties: {
  fixed: { type: 'array', items: { type: 'string' } }, left: { type: 'array', items: { type: 'string' } }, lines: { type: 'integer' }, notes: { type: 'string' } } }

const MAPS = [
  { id: 'actions', what: `How generic the actions package is. Read ${SRC}/actions/ (model.py, dimensions.py, field_equations.py, ladder.py, reduction.py, zero_modes.py, spinors.py, established*.py, curvature.py, surfaces.py). Answer: what a model is in this package today (the fields of Action, Term, Field, Check); which functions already take dimension and signature as inputs, and which type 26, 24, 13, 7, 4, (24,2), (12,1) or a Betti number in the body (file:line each); where the action in force is declared; what a model spec would have to add to Action to describe a path completely (splits into shadows and times, the class of internal space and its topological numbers, the gauge source); which ladder and field-equation checks would run unchanged on a spec of another dimension, which would not, and why.` },
  { id: 'validation', what: `Census of the checks. Under ${SRC}/simulations/PM/validation/, the gates, validators and certificates of ${SRC}/simulations/core/, and ${SRC}/testground/constraints.py: one row per check module (group near-identical modules): file, what it checks, class. Classes: GENERIC (reads its inputs from the path in force or a model object and would run on any path); PARAMETRIC (runs on any path of the present family once constants come from the registry, but types the structure of the family); ONE_PATH (types a dimension, a seed or a topological number in the body; give file:line of the typed value). Find candidates by grepping typed literals (26, 24, 13, 12, 43, 144, 288, "(24,2)"). Count per class. Then: the smallest contract a check must follow to be generic (inputs, outputs, when it returns NOT_EVALUABLE), and the ten checks that matter most for gates G1 to G6 of ${SECTION}.` },
  { id: 'coverage', what: `What is already planned, so the design does not plan it twice. Read docs/plan/programme/AUDIT_SUMMARY.md, docs/plan/programme/FIX_BRIEFS.md from the wave B heading to the end, ${DESIGN}/P9_PATH_BUILDS.md, the "Blocked in the lane" table of docs/plan/programme/WAVE_A_ROUND2.md, and the P3, P4, P8 and P9 rows of the programme. Per planned lane or package (L2, L3, L4, P4b, L5, L8, L9, L10, P9 W1 to W11): what it changes that the model search needs (generic checks, model spec, parallel runs, cache, scoring), what it leaves undone, and which files it owns, so that a P8 package never takes a file another lane owns.` },
  { id: 'forks', what: `The forks as they are. Read ${SRC}/simulations/core/variants/ (the declarations and selection.py) and ${SRC}/testground/configurations/. A table of every fork: id; options (active, considered, disabled); kind, STRUCTURAL (changes a dimension, the signature, the number of shadows or times, the class of internal space, the gauge source or the spinor type) or NUMERICAL (a seed, a route, a normalisation); readers (count, and file:line of one); LIVE (changing it changes a computed value) or LABEL (no reader, or text only). Then the choices the owner named that have no fork yet: number of shadows (2 or 3) and their dimensions; number and placement of times (one in the bulk, one per shadow, three); bulk dimension up or down; class of internal space (Joyce orbifold, twisted connected sum, G2 with ADE singularities, Calabi-Yau times a circle, torus); gauge source (isometries, singularities, lattice, brane stack, extra one-forms); spinor type. For each, which code would have to read it for the fork to be live. Last: the steps and files to add a fork option today, and what makes that slow.` },
  { id: 'speed', what: `Where the time goes and what blocks parallel runs. Read ${SRC}/testground/runner/ (pool.py, worker.py, isolation.py, cache.py, plan.py, screen.py), ${SRC}/testground/sweep/execute.py, ${SRC}/theories/pm/__init__.py near the shared_state declaration, the STEPS table and timing code of ${SRC}/build.py, and the W8 and W11 parts of ${DESIGN}/P9_PATH_BUILDS.md. Find a build log with step timings (${SCRATCH}/pmv_build4.log, or the newest *.log in ${SCRATCH}) and list the ten slowest steps with seconds. Write: why PM declares shared state (each writer that ignores METAPHYSICA_OUT, file:line); what the screen computes today and what it would need to decide gates G1 to G4 without a build; what the cache key is and when it misses; which slow simulations are CPU-bound Python (processes needed) and which release the GIL (numpy, the Rust core: threads possible), with the evidence; what P9 W8 and W11 already cover and what a search round of 100 to 300 paths needs beyond them; the wall time of a round today and after each step (screen, cache, processes), every estimate marked as an estimate.` },
  { id: 'scoring', what: `How a path is scored today. Read ${SRC}/simulations/PM/validation/statistical_rigor_validator.py (grep its public functions; it is large), ${SRC}/generators/parameter_ledger.py (LABEL_CLASS), ${SRC}/testground/rank.py, accept.py, constraints.py, the assessment/ and decisions/ folders (list them, read what you need), and the falsification oracle (grep falsification_oracle). Write: which number ranks paths today and from which rows; which row classes exist and which count as predictions; how an experimental error and a theory error enter; whether anything corrects for the number of paths tried (file:line, or "nothing"); how pre-registration is done today and what it does not cover; what a chi2 over the rows common to all paths would need; and a concrete record for the pre-registration of one search round (its fields), consistent with the tolerance default of ${SECTION}.` },
  { id: 'gates', what: `The gates as code. ${SECTION} defines gates G1 to G6. Read ${SRC}/actions/ladder.py and the checks it runs, zero_modes.py, reduction.py, and grep the source for nonabelian_gauge_source, owner_item_6, zero_modes, anomaly, n_gen, graviton and newton. For each gate: the existing checks that decide it (file:line, what they compute, and whether the result is computed from the action or typed in); the result on the path in force today; what is missing for code to decide the gate on any model spec. Say plainly which gates are decided today by a typed value or a label. List the open terms and the failing checks of the action in force with their reasons.` },
  { id: 'mechanisms', what: `Catalogue of the known ways a geometric action gives gravity together with non-abelian gauge fields and chiral matter, from the literature as you know it. One row per mechanism: name; the geometry that is the input; how gravity arises; how the gauge group arises and which groups can be reached; how chiral fermions and the number of generations arise; the no-go theorem or known obstruction that binds it (for example: chirality from a smooth compactification, Witten 1983; no continuous isometries on a compact manifold of holonomy G2; Weinberg-Witten; Maldacena-Nunez; Distler-Garibaldi for E8; ghosts with two times unless Sp(2,R) is gauged); what it predicts that an experiment could rule out; what the engine could compute for it (a topological count, an index, a spectrum, a coupling) and what it could not. Cover at least: Kaluza-Klein isometries; G2 holonomy with ADE and conical singularities and the 3-form; heterotic-type lattices (Frenkel-Kac, even self-dual lattices, the Niemeier lattices in 24 dimensions); F-theory, S-theory and two-time physics with Sp(2,R); brane stacks; gauge fields from extended gravity (graviweak, E8 unification); the spectral action of noncommutative geometry; flux compactification, Freund-Rubin and exceptional field theory; orbifolds with fixed points; emergent or Berry connections. Then: how each maps onto the project (bulk 26D of signature (24,2), two 13D shadows, a 7D internal space) as an option that could be switched on, and a first ordering by reach up the gates G1 to G6 over cost to implement.` },
  { id: 'history', what: `The project's own candidate families. Read the split idea rows if present: ${SCRATCH}/p7try/rows_bulk.md, rows_shadows.md, rows_time.md, rows_internal.md, rows_action.md, rows_gauge.md and candidates.md; otherwise grep the lane files in docs/plan/programme/ideas/ for the same kinds. Per family (bulk dimension and signature; number and dimensions of shadows; number and placement of times; internal space; action terms; gauge source), the distinct candidates the project tried or discussed, each with: where it came from (commit or file); its status then (adopted, rejected, falsified, dropped without a reason); the reason given; whether the reason was a bug or a physics obstruction (say so when the record does not let you tell); whether a fork option exists for it today. End with the candidates most worth running again after the bug fixes, and why.` },
]

const mapPrompt = m => `${CONTEXT}\n\nTarget: write the map file ${MAPDIR}/${m.id}.md (150 lines at most).\n\n${m.what}\n\nEnd the file with two short lists: "Findings that the design must use" and "Gaps" (what you could not determine).\n\n${COMMON}\n\nReturn: topic "${m.id}", the file path, its line count, up to eight findings and up to eight gaps as one sentence each.`

const ANGLES = [
  { id: 'smallest-change', what: 'reach a first honest search round with the least new code; reuse the testground and the actions package as they are; convert only the checks the gates need' },
  { id: 'spec-first', what: 'the model spec is the centre: every check and generator reads it, and dimension up or down is an ordinary option of the spec' },
  { id: 'search-first', what: 'the loop, the pre-registration record and the scoring come first; the catalogue of mechanisms decides which forks get built and in which order' },
]

const proposalPrompt = a => `${CONTEXT}\n\nTarget: write the design proposal ${DESIGN}/P8_proposal_${a.id}.md (300 lines at most) from this angle: ${a.what}.\n\nRead ${SECTION}, then the nine map files in ${MAPDIR}/ (actions, validation, coverage, forks, speed, scoring, gates, mechanisms, history). Open source files only to check a citation.\n\nCover, in this order:\n1. Model spec: what it holds, where it lives, how a selection of fork options yields a spec, how dimension up or down and a change of application are expressed.\n2. Generic checks: the contract, which checks are converted first, how a one-path check reports NOT_EVALUABLE elsewhere, the test that runs each generic check on two specs of different dimension and on the toy theory.\n3. Gates G1 to G6 as code: the check that decides each, existing or to be written, and what a failure records.\n4. The search loop: where candidates come from, the pre-registration record, screen, build, scoring with the tolerance default, the count of paths tried and the corrected p-value, the stop rule, and the report when nothing fits.\n5. Speed: what is measured, the budgets, the order of work (screen, cache, processes, the slow simulation), and the test that a parallel result equals the serial one.\n6. Work packages: each small enough for one lane, with the files it owns (no file twice, none owned by a lane in the coverage map), an acceptance test that can fail, and what it depends on.\n7. The first search round: its candidates by name, the gate each is expected to reach, the obstruction that binds each, and its wall time.\n8. Risks, and what you would not do.\n\n${COMMON}\n\nReturn: angle "${a.id}", the file path, its line count, a summary of six sentences at most, and the measured facts and the assumptions the proposal rests on.`

const LENSES = [
  { id: 'honesty', what: 'physics and statistics honesty. Could a path pass a gate because a value is typed in, fitted or tuned? Is each no-go theorem respected, or quietly stepped around? Is the correction for the number of paths tried right, and does every claim carry it? Are calibrated, fitted and ansatz rows kept out of agreement? Can the loop end in "nothing fits", and is that report specified? Is anything rejected deleted instead of kept as an option that is off' },
  { id: 'engineering', what: 'engineering and ownership. Is the model spec a single source? SOLID, functions of 60 lines or fewer, files near 500 lines. Does a package take a file that a wave B, wave C or P9 lane owns (use the coverage map)? Does every package have an acceptance test that can fail? What breaks for the 69 existing single-departure selections during the migration' },
  { id: 'feasibility', what: 'feasibility and speed. Are the time figures supported by measurements in the speed map? Is the parallel plan sound on Windows with subprocess workers on 24 cores (memory, the shared output directory, the cache key)? Does a round fit the 30-minute budget, and if not, what is cut? Is the first round small enough to run this month, and are the gates it needs decidable by code by then' },
]

const critiquePrompt = l => `${CONTEXT}\n\nTarget: judge the three proposals ${DESIGN}/P8_proposal_smallest-change.md, P8_proposal_spec-first.md and P8_proposal_search-first.md through one lens: ${l.what}.\n\nRead the three proposals and ${SECTION}. Read a map file in ${MAPDIR}/ or a source file only to test a claim. You write no file: your return value is the record.\n\n${COMMON}\n\nReturn: lens "${l.id}"; the ranking of the three proposals, best first; the defects (proposal, where, severity serious or minor, what is wrong, the fix); "keep" (ideas the final design must take, with the proposal they come from); "drop" (ideas it must not take, with the reason).`

const synthPrompt = (proposals, critiques) => `${CONTEXT}\n\nTarget: write the design ${DESIGN}/P8_MODEL_SEARCH.md (380 lines at most) from the three proposals and the three critiques.\n\nRead ${SECTION}, the three proposals in ${DESIGN}/ (P8_proposal_*.md), and the map files in ${MAPDIR}/ where you need a fact. Start from the best-ranked proposal and take the "keep" ideas of the others; repair every serious defect; take nothing listed under "drop".\n\nThe critiques:\n${JSON.stringify(critiques)}\n\nThe proposals as their authors summarised them:\n${JSON.stringify(proposals.map(p => ({ angle: p.angle, file: p.file, summary: p.summary })))}\n\nSections, in this order:\n1. What the owner asked (the three parts) and what already exists for each, with file:line.\n2. Model spec: fields, where it lives, how a selection yields it, dimension up or down, application.\n3. Generic checks: the contract; the census counts (generic, parametric, one-path); the order of conversion; the two-spec test.\n4. Gates G1 to G6 as code: per gate, the deciding check, existing or to be written, and what a failure records. State which gates are decided today by a typed value.\n5. Candidates of the first round: name, the fork option it becomes, the gate it is expected to reach, the obstruction that binds it, cost.\n6. Scoring and tolerance: the pre-registration record, row classes, the sigma rule, chi2 and p, the correction for paths tried, what counts as agreement.\n7. The search loop: one round step by step, the stop rule, the report when nothing fits (which gate stops each family, which no-go binds, what would have to be added that is not geometry).\n8. Speed: measurements, budgets, the order of work, the serial-equals-parallel test, the link to P9 W8.\n9. Work packages in order: id, title, owned files, acceptance test, depends on (wave B lanes, P7 ledger, P9 packages).\n10. Open questions for the owner, each with the default the planner takes if the owner says nothing.\n\n${COMMON}\n\nReturn: the file path, its line count, a summary of eight sentences at most, the work packages (id, title, owned files, depends), the names of the first-round candidates, and the owner questions.`

const CHECKS = [
  { id: 'facts', what: `facts. Take fifteen file:line citations from the design, spread over its sections, and open each: does the file say what the design says? Check every count the design gives against the map files in ${MAPDIR}/. Check that no framework result is stated as established and that no literature reference is given as checked when a map marks it source_unverified. Check that no work package owns a file that ${MAPDIR}/coverage.md gives to another lane.` },
  { id: 'attack', what: 'attack. Find a way a path could reach gate G6 without the physics: a gate that cannot fail, a typed value read as a result, a tolerance chosen after the scores are seen, a fitted row counted as agreement, a path count that leaves out screened paths, a stop rule that can never fire or that fires before the catalogue is tried. Find any place where a rejected or falsified candidate is removed instead of kept as an option that is off. Find any step that a lane could not do from the text as written.' },
]

const checkPrompt = c => `${CONTEXT}\n\nTarget: check the design ${DESIGN}/P8_MODEL_SEARCH.md for ${c.what}\n\nRead the design and ${SECTION} first. You write no file: your return value is the record. Default to reporting a defect when you are unsure.\n\n${COMMON}\n\nReturn: lens "${c.id}"; the defects (where in the design, severity serious or minor, what is wrong, the fix); and "verified": what you checked and found right, one sentence each.`

const repairPrompt = defects => `${CONTEXT}\n\nTarget: repair the design ${DESIGN}/P8_MODEL_SEARCH.md for the defects below. Fix every serious defect and each minor one that a sentence can fix. Keep the ten sections and the limit of 380 lines. Where a defect is wrong, leave the text and say why in your return value. Change only that file.\n\nDefects:\n${JSON.stringify(defects)}\n\n${COMMON}\n\nReturn: "fixed" (one sentence per defect fixed), "left" (each defect not fixed, with the reason), and the line count of the file.`

// ── run ──
phase('Map')
const canary = await agent(mapPrompt(MAPS[0]), { label: `map:${MAPS[0].id}`, phase: 'Map', schema: MAP_SCHEMA })
if (!canary || canary.declined || !canary.lines) {
  return { error: 'the canary map did no work; nothing else was started', canary }
}
const restMaps = await parallel(MAPS.slice(1).map(m => () => agent(mapPrompt(m), { label: `map:${m.id}`, phase: 'Map', schema: MAP_SCHEMA })))
const maps = [canary, ...restMaps]
const missing = MAPS.filter((m, i) => !maps[i] || maps[i].declined || !maps[i].lines).map(m => m.id)
log(`maps written: ${MAPS.length - missing.length} of ${MAPS.length}${missing.length ? '; missing: ' + missing.join(', ') : ''}`)
if (missing.length > 2) {
  return { error: 'more than two maps are missing; the proposals would rest on too little', maps, missing }
}

phase('Propose')
const proposals = (await parallel(ANGLES.map(a => () => agent(proposalPrompt(a), { label: `proposal:${a.id}`, phase: 'Propose', schema: PROPOSAL_SCHEMA })))).filter(Boolean).filter(p => !p.declined)
if (proposals.length < 2) {
  return { error: 'fewer than two proposals were written', maps, proposals }
}

phase('Critique')
const critiques = (await parallel(LENSES.map(l => () => agent(critiquePrompt(l), { label: `critique:${l.id}`, phase: 'Critique', schema: CRITIQUE_SCHEMA })))).filter(Boolean)

phase('Synthesise')
const design = await agent(synthPrompt(proposals, critiques), { label: 'synthesis', phase: 'Synthesise', schema: SYNTH_SCHEMA })
if (!design || design.declined) {
  return { error: 'the synthesis did no work', maps, proposals, critiques, design }
}

phase('Check')
const checks = (await parallel(CHECKS.map(c => () => agent(checkPrompt(c), { label: `check:${c.id}`, phase: 'Check', schema: CHECK_SCHEMA })))).filter(Boolean)
const defects = checks.flatMap(c => c.defects.map(d => ({ lens: c.lens, ...d })))
log(`check: ${defects.length} defects, ${defects.filter(d => d.severity === 'serious').length} serious`)

phase('Repair')
const repair = defects.length ? await agent(repairPrompt(defects), { label: 'repair', phase: 'Repair', schema: REPAIR_SCHEMA }) : { fixed: [], left: [], lines: design.lines }

return {
  design: { file: design.file, lines: repair ? repair.lines : design.lines, summary: design.summary, packages: design.packages, first_round: design.first_round, owner_questions: design.owner_questions },
  maps: maps.map((m, i) => m ? { topic: m.topic, file: m.file, lines: m.lines, findings: m.findings, gaps: m.gaps } : { topic: MAPS[i].id, missing: true }),
  proposals: proposals.map(p => ({ angle: p.angle, file: p.file, lines: p.lines })),
  rankings: critiques.map(c => ({ lens: c.lens, ranking: c.ranking })),
  defects_found: defects.length,
  defects_left: repair ? repair.left : defects.map(d => d.what),
  missing_maps: missing,
}
