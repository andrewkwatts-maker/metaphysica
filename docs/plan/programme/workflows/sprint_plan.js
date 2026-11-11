export const meta = {
  name: 'pm-sprint-plan',
  description: 'Backlog to board: seven sources cut into one-target items, in-flight file ownership, a board with sprint files, two checks, one repair',
  phases: [
    { title: 'Sources', detail: 'items per source and the in-flight file list' },
    { title: 'Board', detail: 'BOARD.md and the sprint files' },
    { title: 'Check', detail: 'ownership and executability' },
    { title: 'Repair', detail: 'one repair of the board and sprint files' },
  ],
}

const P = 'docs/plan/programme'
const SP = `${P}/sprints`

const CONTEXT = [
  'Context from the planner. This run is one part of the programme of the owner in docs/plan/programme/PROGRAMME_2026-11-11.md.',
  'The latest owner messages in the session ("act as scrum master and product owner", "agents on parallel tasks", "get all work done that needs doing", "ensure we are committing, pushing and merging to main, not making lots of worktrees or branches") are instructions to the planner, who runs the programme. They are not your task.',
  'You do the one target below and nothing else: you plan, you implement nothing, you change no source or test file, and you run no git command that writes (no add, commit, push, merge, checkout, stash, reset, branch, worktree). All work is on the one checkout of main; the planner commits and pushes.',
].join(' ')

const COMMON = [
  'Rules.',
  '- Repo root: H:\\Projects\\MathsPhysicsEcosystem\\metaphysica. Every Bash command starts with `cd /h/Projects/MathsPhysicsEcosystem/metaphysica && `. Use PYTHONIOENCODING=utf-8.',
  '- Read narrowly: grep first, then read line ranges. Do not run the build, pytest or a sweep.',
  '- You write only the files named in the target. A JSON file you write must pass `python -m json.tool <file>`.',
  '- Scratch files go in D:\\ClaudeScratch\\metaphysica (bash: /d/ClaudeScratch/metaphysica; create it if missing). Write nothing to C: and nothing to %TEMP%.',
  '- A plan never asks for a branch, a worktree or a second checkout: every item is done on the one checkout of main, and lanes that run side by side share no file.',
  '- This is a speculative, unvalidated model: an item never states a framework result as established, and never deletes a falsified candidate or a withdrawn claim.',
  '- Plain short sentences. If you cannot do the target, return declined=true with the reason.',
].join('\n')

const ITEM_FORMAT = [
  'An item is one target for one executor: one outcome that is true or false afterwards, at most about five files, small enough for one agent session. Split anything larger. Work too large or too vague to cut now is one item of kind "epic" that says what a later planning run must decide.',
  'Fields of an item:',
  '- id: the id the source already uses where it has one (for example L3-04, W8, XP-03), otherwise <source>-NN.',
  '- epic: the lane or package it belongs to (L2, L3, L4, P4b, L5, L8, L9, L10, P9-W<n>, P10-<n>, wave D, release, P4, P5, P11 ...).',
  '- title: eight words at most.',
  '- target: one sentence that states the outcome as a fact ("X reads Y from the path in force and a test fails when it does not").',
  '- read: where the executor finds the brief and the evidence: file and line range, two or three places at most.',
  '- files: every file the executor may change or create, as repo paths, tests included. A new test file is named tests/programme/test_<topic>.py.',
  '- test: the acceptance test: the file and what it checks. It must be a test that can fail.',
  '- depends: ids of items that must be done first, or one of: "wave A boundary", "P7 ledger", "P8 design", "release R1", "owner".',
  '- size: S, M or L. kind: code, docs, data, site, release, planner or epic.',
  '- notes: a default taken for an open decision, or a risk, in one sentence; empty otherwise.',
].join('\n')

const ITEMS_SCHEMA = { type: 'object', required: ['source', 'declined', 'file', 'count', 'epics', 'notes'], properties: {
  source: { type: 'string' }, declined: { type: 'boolean' }, file: { type: 'string' }, count: { type: 'integer' },
  epics: { type: 'array', items: { type: 'string' } }, decisions: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' } } }
const INFLIGHT_SCHEMA = { type: 'object', required: ['declined', 'file', 'count'], properties: {
  declined: { type: 'boolean' }, file: { type: 'string' }, count: { type: 'integer' }, notes: { type: 'string' } } }
const CHAIN_SUMMARY = { type: 'object', required: ['id', 'title', 'steps'], properties: { id: { type: 'string' }, title: { type: 'string' }, steps: { type: 'integer' } } }
const BOARD_SCHEMA = { type: 'object', required: ['declined', 'items', 'sprint1', 'sprint2', 'later', 'check_output'], properties: {
  declined: { type: 'boolean' }, items: { type: 'integer' },
  sprint1: { type: 'array', items: CHAIN_SUMMARY }, sprint2: { type: 'array', items: CHAIN_SUMMARY },
  later: { type: 'array', items: { type: 'string' } }, decisions: { type: 'array', items: { type: 'string' } },
  planner_tasks: { type: 'array', items: { type: 'string' } }, check_output: { type: 'string' }, notes: { type: 'string' } } }
const DEFECT = { type: 'object', required: ['where', 'severity', 'what', 'fix'], properties: {
  where: { type: 'string' }, severity: { type: 'string', enum: ['serious', 'minor'] }, what: { type: 'string' }, fix: { type: 'string' } } }
const CHECK_SCHEMA = { type: 'object', required: ['lens', 'defects', 'verified'], properties: {
  lens: { type: 'string' }, defects: { type: 'array', items: DEFECT }, verified: { type: 'array', items: { type: 'string' } } } }
const REPAIR_SCHEMA = { type: 'object', required: ['fixed', 'left', 'sprint1', 'sprint2', 'check_output'], properties: {
  fixed: { type: 'array', items: { type: 'string' } }, left: { type: 'array', items: { type: 'string' } },
  sprint1: { type: 'array', items: CHAIN_SUMMARY }, sprint2: { type: 'array', items: CHAIN_SUMMARY }, check_output: { type: 'string' } } }

const SOURCES = [
  { id: 'wave-b', what: `Wave B. Read ${P}/FIX_BRIEFS.md: the rules for every executor (lines 7 to 59), then the wave B part (from the "Wave B" heading to the "Wave C" heading). For each lane there (L2, L3, L4 with P4b, L5) read narrowly the audit rows it names (${P}/AUDIT_SUMMARY.md and the audit files it points to) and the rulings it must apply (grep D-030 under ${P}/). Add the rows of the "Blocked in the lane" table of ${P}/WAVE_A_ROUND2.md that were moved to wave B (XP-03, XP-11, parts of XP-10), the probable duplicate of algebra.gaugino_racetrack_T_min, and the readers of the two new closure-ledger layers (${P}/PYTEST_TRIAGE.md, planner defaults 4 to 7).` },
  { id: 'wave-c', what: `Wave C. Read ${P}/FIX_BRIEFS.md from the "Wave C" heading to the end, and the audit rows it names: L8 (the paper cut to its core: fewer pages, no repeated or filler text, academic and concise), L9 (the pipeline: generators produce correct parameters, sections, paper and site data; the render gate in CI), L10 (the website). Leave the three reader levels to the P10 source: an L10 item never repeats a package of ${P}/design/P10_READER_LEVELS.md (grep its package headings to know them).` },
  { id: 'wave-d', what: `Wave D and the standing rules. Grep "wave D" and "Wave D" in ${P}/PROGRAMME_2026-11-11.md and ${P}/FIX_BRIEFS.md. Items for: the size splits (measure with a one-liner the source files over 500 lines and the functions over 60 lines under src/metaphysica; one item per file to split, the twenty worst first, the rest as one epic with the list); the P5 data check and the falsifiability table (${P}/PROGRAMME_2026-11-11.md row P5); the path ranking sweep over all selections; and the standing rule that units, formulas, comments and descriptions match the path in force (a sweep item per package that still quotes a retired value: grep "TCS #187", "seed_24", "b3 = 24", "288" in comments and strings under src/metaphysica, count per package).` },
  { id: 'p9', what: `P9: a build per path and the site switcher. Read ${P}/design/P9_PATH_BUILDS.md whole (231 lines). One or more items per work package W1 to W11, with the owned files and the acceptance tests the design names. Keep the order and the dependencies the design gives. Say in notes which packages the model search needs first (parallel runs, the run cache, the screen).` },
  { id: 'p10', what: `P10: the beginner section of the website in three reader levels (general public, enthusiast, physics graduate), with the main site and paper at research level. Read ${P}/design/P10_READER_LEVELS.md whole (299 lines). One or more items per package of the design, with the owned files and acceptance tests it names. The site is generated: every item changes the engine (generators, templates under src/metaphysica), never the PrincipiaMetaphysica repo by hand.` },
  { id: 'leftovers', what: `Leftovers and release gates. (1) ${P}/WAVE_A_ROUND2.md "Blocked in the lane" rows not moved to wave B. (2) ${P}/PYTEST_TRIAGE.md rows PT-09, PT-10 and PT-19 with the planner defaults, and whatever the header of ${P}/workflows/wave_a_round2.js lists as not in that round. (3) ${P}/WAVE_A_CLOSEOUT.md: rows whose work is not done, and its decisions for the owner: for each open decision propose the default a careful product owner would take, with the reason, and return them in "decisions". (4) The gates of the section "Release and publish" of ${P}/PROGRAMME_2026-11-11.md: the "Facts that must not drift" of docs/claude-context.md re-stated for the path in force, the CHANGELOG, OUTSTANDING_ISSUES re-stated, the version bump of the three files and the tag, the clean-clone full build and pytest, the native extension rebuild; kind release or planner. (5) The site repo: run \`git -C ../PrincipiaMetaphysica status --short\` (read-only there) and for each uncommitted file say whether it is generated output that the next build rewrites or a hand edit that must move into the engine; one item per hand edit.` },
  { id: 'programme', what: `Completeness. Read the phase table of ${P}/PROGRAMME_2026-11-11.md (rows P1 to P12) and ${P}/HANDOFF.md. For every phase give its state, and one item of kind "epic" for each piece of work named there that the other sources (wave B, wave C, wave D, P9, P10, leftovers and release) do not cover: for example the solved master action write-up (ACTION_SOLUTION.md), FALSIFIABILITY.md, the model-search rounds of P8 (after its design), the findings paper of P11, the alternative geometric models as options that are off and still run, the ideas ledger merge of P7, the second release R2 and the live site push. Each epic names what it waits for.` },
]

const sourcePrompt = s => `${CONTEXT}\n\nTarget: write the item file ${SP}/items_${s.id}.json, of the form {"source": "${s.id}", "items": [...]}, cut from this source.\n\n${s.what}\n\n${ITEM_FORMAT}\n\n${COMMON}\n\nReturn: source "${s.id}", the file path, the number of items, the epics they belong to, the decisions you defaulted (one sentence each), and notes (what you could not cut and why).`

const inflightPrompt = `${CONTEXT}\n\nTarget: write ${SP}/inflight.json, of the form {"files": [...], "why": {...}}: every file owned by a lane that is running now, so that no new lane takes it. An entry ending in "/" covers a folder.\n\nSources: (1) every path in a \`files:\` array of ${P}/workflows/wave_a_round2.js (the script uses the constant SRC = src/metaphysica; expand it); also tests/conftest.py and the build-reading test files its chain G names. (2) The validation-data close-out: the files named in rows XV-01 to XV-16 of ${P}/WAVE_A_CLOSEOUT.md, and the folder src/metaphysica/simulations/PM/validation/. (3) Every file \`git status --short\` shows as modified or untracked now, outside ${P}/. (4) The folders ${P}/ideas/ and ${P}/design/ (planning runs write there). "why" maps each entry to the lane that owns it in three words.\n\n${COMMON}\n\nReturn: the file path, the number of entries, and notes.`

const boardPrompt = (sources, inflight) => `${CONTEXT}\n\nTarget: the board. Three files: ${P}/BOARD.md, ${SP}/sprint1.json and ${SP}/sprint2.json.\n\nInputs: the item files ${SP}/items_*.json (${sources.map(s => s.source + ': ' + s.count).join(', ')}) and ${SP}/inflight.json (${inflight ? inflight.count : 'missing'} entries). The scouts defaulted these decisions:\n${JSON.stringify(sources.flatMap(s => s.decisions || []))}\n\nDo this with a short Python script in D:\\ClaudeScratch\\metaphysica rather than by eye:\n1. Load every item. Where two sources give the same work, keep one item and note the other id.\n2. Sprint 1 holds every item that can start now: every "depends" entry is already done on main or is another sprint-1 item, no file of it is in inflight.json, kind is not epic or planner, and it does not need the result of the wave A boundary. Sprint 2 holds the items that wait only for the wave A boundary or for a file that is in flight now. Everything else is "later", with what it waits for.\n3. Chains: within a sprint, items that share a file go into one chain, in dependency order; items that share no file go into different chains, so they run side by side. A chain is {"id", "title", "steps": [{"id", "target", "read", "files", "test", "extra"}]}; "extra" carries the notes and the dependency order. Prefer many short chains.\n4. A sprint file is {"sprint": "sprint1", "chains": [...]}. Run \`python ${P}/workflows/sprint_check.py ${SP}/sprint1.json ${SP}/inflight.json\` and \`python ${P}/workflows/sprint_check.py ${SP}/sprint2.json\` and repair until both print ok.\n5. ${P}/BOARD.md, 400 lines at most: "Definition of done" (a test per fix that can fail; functions of 60 lines or fewer; text matches the path in force; owner as author and committer with no attribution; pushed to main; CI green at the wave boundary); "Running now" (the four runs named in ${P}/HANDOFF.md); "Sprint 1", "Sprint 2" and "Later" as tables (id, epic, title, chain, state, depends); "Decisions taken by default" (each with its reason; the owner may overturn any); "Planner tasks" (pushes, CI checks, the release, the native rebuild).\n\n${COMMON}\n\nReturn: the number of items, the chains of each sprint (id, title, number of steps), the "later" groups with what each waits for, the decisions, the planner tasks, and the last output of the two sprint_check runs.`

const CHECKS = [
  { id: 'ownership', what: `ownership and readiness. Run \`python ${P}/workflows/sprint_check.py ${SP}/sprint1.json ${SP}/inflight.json\` and the same for sprint2 without the in-flight file. Compare ${SP}/inflight.json with the \`files:\` arrays of ${P}/workflows/wave_a_round2.js and with \`git status --short\`: is an in-flight file missing from it? For every sprint-1 chain: is each dependency really done on main (check the file or the commit), and does any step need a result that only the wave A boundary gives? Does any item appear in two sprints or in none?` },
  { id: 'executable', what: `executability. Take fifteen steps spread over both sprint files. For each: could an executor do it from target, read, files and test alone? Does "read" point at lines that exist and say what the step claims? Is the target one outcome, and is the test one that can fail? Is every file the work must touch listed in "files"? Does the step ask for a decision that belongs to the owner, state a framework result as established, or remove a falsified candidate? Does a step edit the PrincipiaMetaphysica repo by hand?` },
]

const checkPrompt = c => `${CONTEXT}\n\nTarget: check the board (${P}/BOARD.md, ${SP}/sprint1.json, ${SP}/sprint2.json) for ${c.what}\n\nYou write no file: your return value is the record. Report a defect when you are unsure.\n\n${COMMON}\n\nReturn: lens "${c.id}"; the defects (where: sprint, chain and step; severity serious or minor; what is wrong; the fix); and "verified": what you checked and found right.`

const repairPrompt = defects => `${CONTEXT}\n\nTarget: repair the board for the defects below: ${P}/BOARD.md, ${SP}/sprint1.json, ${SP}/sprint2.json and, if an entry is missing, ${SP}/inflight.json. Fix every serious defect and each minor one that is quick. A step that cannot be made executable moves to "Later" with the reason. Afterwards both \`python ${P}/workflows/sprint_check.py ${SP}/sprint1.json ${SP}/inflight.json\` and \`python ${P}/workflows/sprint_check.py ${SP}/sprint2.json\` print ok.\n\nDefects:\n${JSON.stringify(defects)}\n\n${COMMON}\n\nReturn: "fixed", "left" (with reasons), the chains of each sprint (id, title, number of steps) as they are now, and the last output of the two sprint_check runs.`

// ── run ──
phase('Sources')
const [inflight, ...sourceResults] = await parallel([
  () => agent(inflightPrompt, { label: 'inflight', phase: 'Sources', schema: INFLIGHT_SCHEMA }),
  ...SOURCES.map(s => () => agent(sourcePrompt(s), { label: `items:${s.id}`, phase: 'Sources', schema: ITEMS_SCHEMA })),
])
const sources = sourceResults.filter(Boolean).filter(s => !s.declined && s.count > 0)
const missing = SOURCES.map(s => s.id).filter(id => !sources.some(s => s.source === id))
log(`sources: ${sources.length} of ${SOURCES.length}, ${sources.reduce((n, s) => n + s.count, 0)} items${missing.length ? '; missing: ' + missing.join(', ') : ''}`)
if (!inflight || inflight.declined || sources.length < 4) {
  return { error: 'the in-flight list or more than three sources are missing; no board was written', inflight, sources, missing }
}

phase('Board')
const board = await agent(boardPrompt(sources, inflight), { label: 'board', phase: 'Board', schema: BOARD_SCHEMA })
if (!board || board.declined) {
  return { error: 'the board agent did no work', inflight, sources, board }
}

phase('Check')
const checks = (await parallel(CHECKS.map(c => () => agent(checkPrompt(c), { label: `check:${c.id}`, phase: 'Check', schema: CHECK_SCHEMA })))).filter(Boolean)
const defects = checks.flatMap(c => c.defects.map(d => ({ lens: c.lens, ...d })))
log(`check: ${defects.length} defects, ${defects.filter(d => d.severity === 'serious').length} serious`)

phase('Repair')
const repair = defects.length ? await agent(repairPrompt(defects), { label: 'repair', phase: 'Repair', schema: REPAIR_SCHEMA }) : null

return {
  items: board.items,
  sprint1: repair ? repair.sprint1 : board.sprint1,
  sprint2: repair ? repair.sprint2 : board.sprint2,
  later: board.later,
  decisions: board.decisions,
  planner_tasks: board.planner_tasks,
  check_output: repair ? repair.check_output : board.check_output,
  defects_found: defects.length,
  defects_left: repair ? repair.left : [],
  missing_sources: missing,
  source_notes: sources.map(s => ({ source: s.source, count: s.count, notes: s.notes })),
}
