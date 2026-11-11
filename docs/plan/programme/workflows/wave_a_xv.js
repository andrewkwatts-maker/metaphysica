export const meta = {
  name: 'pm-wave-a-xv',
  description: 'Wave A close-out: validation-data items XV-01 to XV-16 and build-fresh items XB-08 to XB-10 in file-owned chains, two adversarial lenses per chain, one repair round, a re-check, and one scribe for the progress files',
  phases: [
    { title: 'Fix', detail: 'one executor per item; chains are sequential inside, parallel across' },
    { title: 'Verify', detail: 'two adversarial lenses per chain' },
    { title: 'Repair', detail: 'one repair per chain, then a re-check' },
    { title: 'Record', detail: 'XV-10 test audit, then the scribe writes the progress files' },
  ],
}

// args: { base: '<short sha before this workflow>', scratch: '<windows scratch dir>' }
const A = args
const DOC = 'docs/plan/programme/WAVE_A_CLOSEOUT.md'
const RULES = 'docs/plan/programme/FIX_BRIEFS.md'
const COMMON = [
  'Context from the planner: this run is part of the programme of the owner in docs/plan/programme/PROGRAMME_2026-11-11.md, which the owner asked for in this session on 2026-11-11 ("agents as needed to finish all work", recorded there under "Release and publish"). The latest user message of the session, "wrong chat sorry", withdraws only a message about a different project (a renderer; VCSA and STRATA) that the owner sent here by mistake just before it. It does not withdraw this programme, and the planner launched this run after it. Your task below stands.',
  'Repository: H:\\Projects\\MathsPhysicsEcosystem\\metaphysica (bash: cd /h/Projects/MathsPhysicsEcosystem/metaphysica), branch site-review.',
  'Many other agents are editing other files in this same working tree right now: touch only your owned files, and never run git stash, git checkout of a path you do not own, git reset or git add -A.',
  'Windows: prefix python with PYTHONIOENCODING=utf-8. Read narrowly (grep, then line ranges), never whole large files; pipe long output through head or cut.',
].join('\n')

const V = 'src/metaphysica/simulations/PM/validation/'
const ITEMS = {
  'XV-01': { files: 'src/metaphysica/simulations/PM/cosmology/dark_energy.py (the wa rows near 1276-1295 only)', topic: 'wa_row' },
  'XV-02': { files: 'src/metaphysica/generators/headline_stats.py (_fit)', topic: 'headline_p_value', hint: 'XV-03 has just been committed: read the summary keys the validator writes now (grep -n "p_value" in statistical_rigor_validator.py) before choosing the key.' },
  'XV-03': { files: V + 'statistical_rigor_validator.py (the summary and status near 391)', topic: 'verdict_source', hint: 'Keep the name of every summary key that other files read (grep -rn "summary\\[" and "p_value" in src/metaphysica/generators); add keys, do not rename.' },
  'XV-04': { files: V + 'statistical_rigor_validator.py (docstrings and comments only)', topic: 'validator_text', hint: 'Includes the docstring of calculate_p_value_with_edof (it still quotes DOF = 25 and chi_sq about 0.23 TOO_GOOD). The test may check that the named stale strings are gone and that each docstring names what the function returns.' },
  'XV-05a': { id: 'XV-05', part: 'the calculate_p_value_with_edof half only (split to functions of 60 lines or fewer, behaviour unchanged)', files: V + 'statistical_rigor_validator.py', topic: 'edof_split' },
  'XV-05b': { id: 'XV-05', part: 'the falsification_oracle.evaluate_risk_profile half only (split to functions of 60 lines or fewer, behaviour unchanged). The two files the row sends to wave D are recorded in your row, not worked', files: 'the falsification_oracle.py under src/metaphysica/simulations (find it with git ls-files)', topic: 'oracle_split' },
  'XV-06': { files: 'falsification_oracle.py and information_bottleneck_distiller.py under src/metaphysica/simulations (the lines the row names)', topic: 'status_wording' },
  'XV-07': { files: 'falsification_oracle.py under src/metaphysica/simulations (the lines the row names)', topic: 'unconfirmed_dates' },
  'XV-09': { files: 'the certificate_gates/core.py under src/metaphysica/simulations (C002 and C003)', topic: 'gate_expected_values' },
  'XV-11': { files: V + 'statistical_rigor_validator.py (_adapt_validation_rows) and the tests that use it', topic: 'adapt_rows' },
  'XV-12': { files: 'src/metaphysica/generators/headline_stats.py (gate_summary)', topic: 'gate_formula_text' },
  'XV-13': { files: 'adversarial_axiom_tester.py under src/metaphysica/simulations and src/metaphysica/generators/generate_72_certificates.py (the comment lines the row names only)', topic: 'stale_comments' },
  'XV-14': { files: 'the tests/programme test of C003 and the beacon_two_time_bulk_accounting test or check the row names (find with grep -rln)', topic: 'c003_and_beacon' },
  'XV-15': { files: 'the results.py that defines STOCHASTIC under src/metaphysica/simulations/PM/validation or src/metaphysica/simulations/validation (find with grep -rn STOCHASTIC)', topic: 'stochastic_key' },
  'XV-16': { files: 'tests/test_de_plane_gate.py and the gate module it tests, whichever side the evidence says is wrong (never both without evidence); experimental values are not edited', topic: 'de_plane_gate', hint: 'XV-01 has just been committed and may have moved the plane numbers again: run the test file first and work from what fails now. Expected values in the test are computed from the registered inputs, not typed.' },
  'XB-08': { files: 'src/metaphysica/generators/generate_statistics.py (_registered, _write_back_parameters)', topic: 'pre_rigor_status', group: 'XB' },
  'XB-09': { files: 'src/metaphysica/generators/generate_statistics.py (docstrings, notes and the unreachable fallbacks the row names)', topic: 'statistics_text', group: 'XB' },
  'XB-10': { files: V + 'statistical_rigor_validator.py (where the report is written and where a run starts)', topic: 'stale_report', group: 'XB' },
}

const ROUND = {
  type: 'object',
  properties: {
    done: { type: 'boolean' },
    commits: { type: 'array', items: { type: 'string' } },
    files: { type: 'array', items: { type: 'string' } },
    tests: { type: 'string' },
    edited_tests: { type: 'array', items: { type: 'string' } },
    progress_row: { type: 'string' },
    data_to_confirm: { type: 'array', items: { type: 'string' } },
    blocked: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['done', 'commits', 'tests', 'progress_row'],
}
const VERDICT = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['pass', 'defects'] },
    defects: { type: 'array', items: { type: 'object', properties: {
      item: { type: 'string' },
      severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
      where: { type: 'string' }, what: { type: 'string' }, fix: { type: 'string' } },
      required: ['severity', 'where', 'what', 'fix'] } },
    tests: { type: 'string' },
    method: { type: 'string' },
  },
  required: ['verdict', 'defects', 'tests'],
}
const SCRIBE = {
  type: 'object',
  properties: { commits: { type: 'array', items: { type: 'string' } }, rows: { type: 'number' }, notes: { type: 'string' } },
  required: ['commits', 'rows'],
}

const EX = { agentType: 'executor', model: 'opus' }
const lane = k => (ITEMS[k].group === 'XB' ? 'build-fresh' : 'validation-data')
const section = k => (ITEMS[k].group === 'XB' ? 'XB build-fresh' : 'XV validation-data')
const testFile = k => `tests/programme/test_${ITEMS[k].group === 'XB' ? 'build_fresh' : 'validation_data_closeout'}_${ITEMS[k].topic}.py`

function itemPrompt(k) {
  const it = ITEMS[k]
  const id = it.id || k
  return `One target: item ${id} of the metaphysica wave A close-out${it.part ? ` (${it.part})` : ''}. Nothing else.
${COMMON}
Read first, and nothing more than these: in ${DOC} the row ${id} (grep -n "${id}") and the section "Rules for a close-out executor"; in ${RULES} the section "Rules for every executor" (binding) and, for context only, the design paragraph of the lane "${lane(k)}".
The fix is decided in the row: carry it out, do not redesign it. ${it.hint || ''}
Owned files: ${it.files}; your new test file ${testFile(k)}; existing tests of the file you edit. Any other file: do not edit it, report it as blocked with the file and the reason.
Do NOT edit any file under docs/plan/programme/progress/: return your progress row in progress_row instead, as one table line "| ${id} | what was done | commit | test |" with the real short commit hash (a scribe writes the file later). Lines for "Data to confirm" go in data_to_confirm.
Tests write only into tmp_path. Run only the test files you add or touch plus the existing tests that cover the file you edit (grep -rl in tests/), in the foreground, one command per file. Never run a build, run_all_simulations, a generator against the default output directory, or the full suite. An existing test that asserted the defect may be edited: list it in edited_tests with the reason. A test for a fix must fail on the code before your change; if your test also passes on the old code say so in notes and call it a characterization test.
Functions of 60 lines or fewer; fail early; no typed topological number (b3, b2, n_gen, chi_eff and fork choices come from the path readers); text in every function you touch says what the code computes now.
Commit: git add -- <paths> && git commit -m "validation-data close-out ${id}: <what>" -- <paths> (never -A, no push, no attribution or Co-Authored-By line; the owner identity is already configured). If the commit reports that it swept in a change you did not make, say so in notes.
Stop when ${id} is committed with passing tests, or when blocked.
Report: done; commits (short shas); files (paths you changed); tests (pytest summary lines); edited_tests (file::test and reason); progress_row; data_to_confirm; blocked (file and reason, or empty); notes (under 60 words: only what the planner must decide).`
}

const LENSES = {
  does_it_fix: `Lens "does it fix". For each item: read its row, then the code now. Is the item done as the row says, completely, at every place the row names? Rule 7: for each new test decide whether it fails on the code before the item. Preferred method: git archive ${A.base} src/metaphysica into "${A.scratch}\\xbase-<your chain key>" (tar -x), run the new test files with PYTHONPATH set to that export's src, confirm with python -c "import metaphysica; print(metaphysica.__file__)" (copy src/metaphysica/_physica_core*.pyd into the export if needed); otherwise judge from the diff. Say which in method, and delete the export afterwards. Then run the chain's new test files and the existing test files it touched on the current tree, one command per file, and give the summary lines in tests. A behaviour-preserving split is checked by reading both versions for a changed branch, default or message.`,
  rules: `Lens "rules". For each commit: git show --stat (a file outside the item's owned set is a critical defect; new tests are allowed; a progress file edit is a defect in this workflow); git log --format='%h %an <%ae> | %cn <%ce>%n%B' (andrewkwatts-maker <AndrewKWatts@gmail.com> as author and committer, no attribution or Co-Authored-By line). In added lines: a typed 24, 43, 144, 12, 4, 3 or 288 standing for a topological number; an except clause that swallows; an "or <number>" default; a removed registry row, fork option, falsified candidate or withdrawn claim; an experimental value edited. Read every changed function whole: does each status label, unit, formula string, comment and docstring say what the code now computes; is any added or rewritten function over 60 lines. git diff ${A.base}..HEAD on the existing test files the chain touched: an assertion removed or weakened without a reason in the item's edited_tests is a high defect. Give in tests the summary lines of the chain's test files run on the current tree, one command per file.`,
}

function verifyPrompt(key, lens, rounds) {
  return `Adversarial review of one chain ("${key}") of the metaphysica wave A close-out. You fix nothing and edit no tracked file. Assume corners were cut until the diff shows otherwise.
${COMMON}
Read ${DOC} ("Rules for a close-out executor" and the rows of the items below) and ${RULES} ("Rules for every executor").
Base commit: ${A.base}. Items and what their executors reported (JSON): ${JSON.stringify(rounds.map(r => ({ item: r.key, done: r.done, commits: r.commits, files: r.files, tests: r.tests, edited_tests: r.edited_tests, blocked: r.blocked, notes: r.notes })))}
Other lanes commit in the same range: judge only these commits, confirmed with git show.
${LENSES[lens]}
No build, no full suite, no generator against the default output directory.
Verdict "pass" only when there is no critical or high defect. Severity: critical = a wrong number or wrong physics, a deleted claim, an edit outside scope, an attribution line; high = a fix that does not fix, a test that cannot fail, a new literal or fallback, a wrong status, a weakened test; medium and low = the rest. Each defect: item, where (file:line or commit), what, fix, each under 300 characters. An item reported as blocked or not done is listed as a high defect with what is missing.`
}

function repairPrompt(key, rounds, defects) {
  return `Repair round for one chain ("${key}") of the metaphysica wave A close-out. Reviewers found defects in its commits.
${COMMON}
Read ${DOC} ("Rules for a close-out executor" and the rows of the items named in the defects) and ${RULES} ("Rules for every executor"). The rules bind.
Owned files: the files these items changed (${[...new Set(rounds.flatMap(r => r.files || []))].join(', ') || 'see the commits ' + rounds.flatMap(r => r.commits || []).join(' ')}) and their tests. Do NOT edit any file under docs/plan/programme/progress/.
Defects (JSON): ${JSON.stringify(defects)}
Open the evidence of each defect first. For each: fix it and add or correct its test, or show with evidence that it is not a defect. Run only the test files you touch, one command per file. Never run a build or the full suite. Commit: git add -- <paths> && git commit -m "validation-data close-out review (${key}): <what>" -- <paths> (never -A, no push, no attribution line).
Report: done (every defect dealt with); commits; files; tests; edited_tests; progress_row (one table line per defect: "| review ${key} | defect | action | commit |", joined with newlines); blocked; notes (under 60 words; name each defect you judged not a defect and why).`
}

function recheckPrompt(key, defects, repair) {
  return `Re-check of one chain ("${key}") of the metaphysica wave A close-out after its repair round. You fix nothing and edit no tracked file.
${COMMON}
Repair commits: ${(repair.commits || []).join(' ') || 'none reported'}. What the repair reported: ${JSON.stringify({ notes: repair.notes, blocked: repair.blocked, tests: repair.tests })}
Defects that were to be repaired (JSON): ${JSON.stringify(defects)}
For each, read the current code and the repair commit: is it gone, and does its test fail without the repair? Where the repair says "not a defect", check its evidence. Run the test files the repair touched, one command per file (no build, no full suite), and give the summary lines in tests.
Return verdict "pass" when none remains at critical or high; list in defects only what is still open, with item, where, what and fix under 300 characters each.`
}

async function fix(k) {
  let r = await agent(itemPrompt(k), { label: `fix:${k}`, phase: 'Fix', schema: ROUND, ...EX })
  if (!r) r = await agent(itemPrompt(k) + '\nAn earlier attempt ended without a report: run git status --short and git log -3 on your owned files first, then finish or discard what it left.', { label: `fix:${k}-retry`, phase: 'Fix', schema: ROUND, ...EX })
  const out = { key: k, ...(r || { done: false, commits: [], tests: 'no report', progress_row: '', blocked: 'no report from two attempts' }) }
  log(`${k}: ${out.done ? 'done' : 'NOT done'} ${(out.commits || []).join(' ')}${out.blocked ? ' blocked: ' + out.blocked.slice(0, 80) : ''}`)
  return out
}
async function run(keys) {
  const out = []
  for (const k of keys) out.push(await fix(k))
  return out
}

const CHAINS = {
  validator: async () => {
    const first = await run(['XV-03'])
    const rest = await parallel([
      () => run(['XV-04', 'XV-05a', 'XV-11', 'XB-10']),
      () => run(['XV-02', 'XV-12']),
    ])
    return [...first, ...rest.filter(Boolean).flat()]
  },
  statistics: () => run(['XB-08', 'XB-09']),
  oracle: () => run(['XV-05b', 'XV-06', 'XV-07']),
  dark_energy: () => run(['XV-01', 'XV-16']),
  gates: () => run(['XV-09', 'XV-14']),
  comments: () => run(['XV-13']),
  results: () => run(['XV-15']),
}

async function chain(key, body) {
  const rounds = await body()
  if (!rounds.some(r => (r.commits || []).length)) {
    log(`${key}: no commit, nothing to review`)
    return { key, rounds, defects: [], repair: null, still_open: rounds.map(r => `${r.key}: not done (${(r.blocked || 'no reason given').slice(0, 160)})`) }
  }
  const reviews = (await parallel(Object.keys(LENSES).map(lens => () =>
    agent(verifyPrompt(key, lens, rounds), { label: `verify:${key}:${lens}`, phase: 'Verify', schema: VERDICT, model: 'opus' })
  ))).filter(Boolean)
  const defects = reviews.flatMap(v => v.defects || [])
  log(`${key}: ${defects.length} defect(s) from ${reviews.length} of 2 reviews`)
  if (!defects.length) return { key, rounds, defects, repair: null, still_open: reviews.length < 2 ? ['a review returned nothing'] : [] }
  const repair = await agent(repairPrompt(key, rounds, defects), { label: `repair:${key}`, phase: 'Repair', schema: ROUND, ...EX })
  if (!repair) return { key, rounds, defects, repair: null, still_open: defects }
  const recheck = await agent(recheckPrompt(key, defects, repair), { label: `recheck:${key}`, phase: 'Repair', schema: VERDICT, model: 'opus' })
  return { key, rounds, defects, repair, still_open: recheck ? recheck.defects : ['recheck returned nothing'] }
}

// Canary: one small chain first. A run whose agents decline the work is stopped before it fans out.
const canary = await chain('results', CHAINS.results)
const declined = canary.rounds.every(r => !r.done && !(r.commits || []).length)
if (declined) {
  log('canary chain did no work: stopping before the fan-out')
  return { aborted: true, canary: canary.rounds.map(r => ({ item: r.key, blocked: r.blocked, notes: r.notes })) }
}
const others = Object.entries(CHAINS).filter(([key]) => key !== 'results')
const chains = [canary, ...(await parallel(others.map(([key, body]) => () => chain(key, body)))).filter(Boolean)]
const missing = Object.keys(CHAINS).filter(k => !chains.some(c => c.key === k))
if (missing.length) log(`chains with no result: ${missing.join(', ')}`)

phase('Record')
const xv10 = await agent(`One target: item XV-10 of the metaphysica wave A close-out (the audit of existing tests edited in commit a08c652). Nothing else.
${COMMON}
Read in ${DOC} the row XV-10 and "Rules for a close-out executor"; in ${RULES} "Rules for every executor".
git show --stat a08c652, then git show a08c652 -- <each existing test file> one at a time. For every existing test whose assertions were removed or edited: say what it asserted, whether that was a defect (cite the audit finding or the code), and restore any assertion that did not assert a defect (adapted to the current code, computed not typed). The close-out chains that ran before you may have edited the same tests (their commits: ${chains.flatMap(c => c.rounds.flatMap(r => r.commits || [])).join(' ')}): read the current file before restoring.
Owned files: the existing test files a08c652 edited. Do NOT edit any file under docs/plan/programme/progress/: return the full list in progress_row as table lines "| XV-10 | test file::test | what changed in a08c652 | defect asserted? | action | commit |" joined with newlines.
Run each test file you touch, one command per file. No build, no full suite. Commit: git add -- <paths> && git commit -m "validation-data close-out XV-10: <what>" -- <paths> (never -A, no push, no attribution line).
Report: done; commits; files; tests; edited_tests; progress_row; blocked; notes (under 60 words).`, { label: 'fix:XV-10', phase: 'Record', schema: ROUND, ...EX })

const record = {
  items: chains.flatMap(c => c.rounds.map(r => ({ item: r.key, done: r.done, commits: r.commits, tests: r.tests, edited_tests: r.edited_tests, progress_row: r.progress_row, data_to_confirm: r.data_to_confirm, blocked: r.blocked, notes: r.notes }))),
  xv10: xv10 ? { done: xv10.done, commits: xv10.commits, progress_row: xv10.progress_row, edited_tests: xv10.edited_tests, blocked: xv10.blocked, notes: xv10.notes } : 'XV-10 returned nothing',
  reviews: chains.map(c => ({ chain: c.key, defects: c.defects, repair: c.repair ? { commits: c.repair.commits, progress_row: c.repair.progress_row, notes: c.repair.notes, blocked: c.repair.blocked } : null, still_open: c.still_open })),
}
const scribe = await agent(`One target: write the close-out record of the metaphysica wave A items XV-01 to XV-16 and XB-08 to XB-10, and item XB-13. You change no code and no test.
${COMMON}
Read in ${DOC} "Rules for a close-out executor" and the row XB-13; in ${RULES} rule 12 (the sections a progress file carries); then the two progress files docs/plan/programme/progress/validation-data.md and docs/plan/programme/progress/build-fresh.md (headings and the last table only).
Record (JSON, the only source for rows; check each commit hash with git log --oneline -1 <hash> and say in notes which do not exist): ${JSON.stringify(record)}
In validation-data.md, under a "Close-out" heading: one row per XV item with the lane's table columns and the real commit hashes; XV-08 as "done in XB-01 and XB-02" with those commits from build-fresh.md; a "Review" table (chain, defect, action, commit); the XV-10 list; "Data to confirm" lines; "Needs other lane" for every blocked item; "Next round" for what is still open or sent to wave D.
In build-fresh.md: rows XB-08, XB-09, XB-10 from the record, and everything the row XB-13 asks for.
Commit: git add -- <the two files> && git commit -m "wave A close-out: validation-data and build-fresh progress records" -- <the two files> (never -A, no push, no attribution line).
Report: commits; rows (number of item rows written); notes (under 80 words: missing hashes, items with no row).`, { label: 'scribe', phase: 'Record', schema: SCRIBE, ...EX })

return {
  items: record.items.map(i => ({ item: i.item, done: i.done, commits: i.commits, blocked: i.blocked, notes: i.notes })),
  xv10: xv10 ? { done: xv10.done, commits: xv10.commits, blocked: xv10.blocked, notes: xv10.notes } : null,
  reviews: chains.map(c => ({ chain: c.key, defects: c.defects.length, critical_or_high: c.defects.filter(d => d.severity === 'critical' || d.severity === 'high').length, repaired: !!c.repair, still_open: c.still_open })),
  missing_chains: missing,
  scribe,
}
