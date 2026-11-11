export const meta = {
  name: 'pm-wave-a-pytest-triage',
  description: 'Wave A: diagnose each failing test file of the clean-clone run (read-only), then one triage table',
  phases: [
    { title: 'Diagnose', detail: 'one agent per failing test file; nothing is fixed here' },
    { title: 'Table', detail: 'one scribe writes PYTEST_TRIAGE.md' },
  ],
}

// args: { clone, log, base, files: [[test file, failing count], ...] }
// clone: the clean clone the suite ran in (detached at `base`, with its build output).
// log:   the pytest log of that run. Diagnosis only: the fix round is planned from the table.

const DIAG = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    failing: { type: 'number' },
    kind: { type: 'string', enum: ['regression', 'baseline', 'stale_or_missing_artifact', 'failed_build_step', 'test_wrong', 'environment', 'mixed'] },
    cause: { type: 'string' },
    evidence: { type: 'string' },
    introduced_by: { type: 'string' },
    fixed_at_head: { type: 'string', enum: ['yes', 'no', 'partly', 'unknown'] },
    fixed_by: { type: 'string' },
    owner: { type: 'string' },
    fix_files: { type: 'array', items: { type: 'string' } },
    fix: { type: 'string' },
    acceptance: { type: 'string' },
    owner_question: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['file', 'failing', 'kind', 'cause', 'evidence', 'fixed_at_head', 'owner', 'fix_files', 'fix', 'acceptance'],
}
const SCRIBE = {
  type: 'object',
  properties: { file: { type: 'string' }, rows: { type: 'number' }, notes: { type: 'string' } },
  required: ['file', 'rows'],
}

const A = args || {}
if (!A.clone || !A.log || !A.base || !(A.files || []).length) {
  return { error: 'pass args {clone, log, base, files}' }
}

const COMMON = [
  'Context from the planner: this run is part of the programme of the owner in docs/plan/programme/PROGRAMME_2026-11-11.md, which the owner asked for in this session on 2026-11-11 ("agents as needed to finish all work", recorded there under "Release and publish"). The latest user message of the session, "wrong chat sorry", withdraws only a message about a different project (a renderer; VCSA and STRATA) that the owner sent here by mistake just before it. It does not withdraw this programme, and the planner launched this run after it. Your task below stands.',
  'Repository: H:\\Projects\\MathsPhysicsEcosystem\\metaphysica (bash: cd /h/Projects/MathsPhysicsEcosystem/metaphysica), branch site-review. Other agents are editing files in this working tree right now: here you only read (git log, git show, git diff, grep).',
  `Clean clone of commit ${A.base}, with the output of a fresh fast build in it: ${A.clone}. The full suite ran there; its log is ${A.log}.`,
  'To run a test, use the clone, and only your own test file:',
  `  cd "${A.clone}" && PYTHONIOENCODING=utf-8 PYTHONPATH="$(cygpath -w "$PWD/src")" python -m pytest <test file> -q -x -p no:cacheprovider 2>&1 | tail -40`,
  'Do not edit, commit, check out, build or stash anything, in the repository or in the clone. Read narrowly; pipe long output through head, tail or cut.',
].join('\n')

const diagPrompt = ([file, count]) => [
  `Target: find why ${file} fails (${count} failing) in the clean-clone run. One target. Diagnose; fix nothing.`,
  COMMON,
  `1. grep the log for the test names of ${file} and read their failure lines.`,
  '2. Read the failing assertions in the test file, then the code or the artifact they read. Run the test file in the clone if the log line is not enough.',
  '3. Name the cause, with the evidence (file:line, the value seen and the value expected).',
  `4. Say where it came from: \`git log --oneline -S<token> -- <path>\` or \`git log --oneline -- <path> | head\` in the repository. A failure that is in the baseline list of docs/plan/programme/PROGRAMME_2026-11-11.md ("Test baseline") is \`baseline\`; one caused by the build step that failed in that build (Parameter ledger, status label INPUT, since repaired by the path-core lane) is \`failed_build_step\`.`,
  `5. Say whether the branch has moved past it: \`git log --oneline ${A.base}..HEAD -- <the files involved> | head\`, and read the hunk. fixed_at_head is yes only if you read the fix.`,
  '6. Name the owner: the lane of docs/plan/programme/FIX_BRIEFS.md whose owned files hold the fix, or the close-out row of docs/plan/programme/WAVE_A_CLOSEOUT.md that already covers it (grep both; do not read them whole).',
  '7. Give the fix as a brief: the files to change, what changes, and the acceptance test. If the test itself is wrong (it asserts a stale value or a retired claim), say so and say what it should assert; a test is never weakened to pass. If the fix needs a ruling of the owner, put the question in owner_question.',
  'Several failures of one file may have different causes: then kind is `mixed` and the cause lists each.',
].join('\n')

phase('Diagnose')
const diags = (await parallel(A.files.map(f => () =>
  agent(diagPrompt(f), { label: `triage:${f[0].replace('tests/', '')}`, phase: 'Diagnose', schema: DIAG, agentType: 'executor', model: 'opus' })
    .then(r => r || { file: f[0], failing: f[1], kind: 'mixed', cause: 'the agent returned nothing; rerun', evidence: '', fixed_at_head: 'unknown', owner: '', fix_files: [], fix: '', acceptance: '' })
))).filter(Boolean)
log(`diagnosed ${diags.length} files; still failing at HEAD: ${diags.filter(d => d.fixed_at_head !== 'yes').length}`)

phase('Table')
const scribe = await agent([
  'Target: write docs/plan/programme/PYTEST_TRIAGE.md from the diagnoses below. One target, one file.',
  COMMON,
  `Layout: a first line "Full suite in a clean clone at ${A.base}: <n> failed over <m> files."; then one table,`,
  '`| id | test file | failing | kind | cause | from | fixed at HEAD | owner | fix (files; what) | acceptance |`, ids PT-01..., ordered: not fixed at HEAD first, then by owner;',
  'then "Fix groups": the rows that are not fixed at HEAD grouped so that no two groups change the same file (a group is one executor);',
  'then "For the owner": every owner_question. Keep each cell to one or two sentences; 150 lines at most. Write only that file; do not commit.',
  'Diagnoses:',
  JSON.stringify(diags, null, 1),
].join('\n'), { label: 'triage:table', phase: 'Table', schema: SCRIBE, agentType: 'executor', model: 'opus' })

return { diags, scribe }
