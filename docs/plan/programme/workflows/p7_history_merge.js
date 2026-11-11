export const meta = {
  name: 'pm-p7-history-merge',
  description: 'P7: merge the lane files into one ledger per kind, check and repair each, sweep for missed ideas, then the timeline, the candidates and the index',
  phases: [
    { title: 'Merge', detail: 'one ledger per kind from the lane rows of that kind' },
    { title: 'Check', detail: 'every lane row cited; rows checked against lanes, options and fixes' },
    { title: 'Repair', detail: 'one round for a kind with defects' },
    { title: 'Sweep', detail: 'three source groups searched for ideas with no ledger row' },
    { title: 'Add', detail: 'missed ideas added, per kind' },
    { title: 'Parts', detail: 'timeline, owner candidates and model space, cross-kind duplicates' },
    { title: 'Index', detail: 'IDEAS_LEDGER.md' },
  ],
}

// args: { rows: <dir> }  The directory written by
//   python docs/plan/programme/workflows/p7_rows.py split docs/plan/programme/ideas <dir>
//   python docs/plan/programme/workflows/p7_rows.py forks <dir>
// Kinds run side by side: an agent writes only docs/plan/programme/ideas/ledger_<its kind>.md.

const KINDS = [
  ['bulk', 'BULK'], ['shadows', 'SHAD'], ['time', 'TIME'], ['internal', 'INTL'], ['lattice', 'LATT'],
  ['topology-number', 'TOPO'], ['generations', 'GENS'], ['action', 'ACTN'], ['gauge', 'GAUG'],
  ['particle', 'PART'], ['cosmology', 'COSM'], ['identity', 'IDEN'], ['other', 'OTHR'],
]
const ROWS = (args && args.rows) || ''
if (!ROWS) {
  return { error: 'pass args.rows, the directory written by p7_rows.py split and forks' }
}
const TOOL = 'PYTHONIOENCODING=utf-8 python docs/plan/programme/workflows/p7_rows.py'
const IDEAS = 'docs/plan/programme/ideas'

const MERGED = {
  type: 'object',
  properties: {
    kind: { type: 'string' },
    file: { type: 'string' },
    lane_rows: { type: 'number' },
    ideas: { type: 'number' },
    class_counts: { type: 'string' },
    reevaluate_counts: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['kind', 'file', 'ideas'],
}
const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          type: { type: 'string', enum: ['missing_idea', 'lane_row_not_cited', 'wrong_merge', 'wrong_fate', 'wrong_class', 'wrong_flag', 'unsupported_citation', 'form'] },
          kind: { type: 'string' },
          row: { type: 'string' },
          source: { type: 'string' },
          detail: { type: 'string' },
          fix: { type: 'string' },
        },
        required: ['type', 'source', 'detail'],
      },
    },
    checked: { type: 'string' },
  },
  required: ['findings', 'checked'],
}
const PART = {
  type: 'object',
  properties: { file: { type: 'string' }, rows: { type: 'number' }, notes: { type: 'string' } },
  required: ['file', 'rows'],
}

const COMMON = [
  'Context from the planner: this run is part of the programme of the owner in docs/plan/programme/PROGRAMME_2026-11-11.md, which the owner asked for in this session on 2026-11-11 ("agents as needed to finish all work", recorded there under "Release and publish"). The latest owner messages of the session ("act as scrum master and product owner", "agents on parallel tasks", "get all work done that needs doing", "ensure we are committing, pushing and merging to main, not making lots of worktrees or branches") are instructions to the planner, who runs the programme. They are not your task: you do the one target below and nothing else, on the one checkout of main, with no branch and no worktree.',
  'Repository: H:\\Projects\\MathsPhysicsEcosystem\\metaphysica (bash: cd /h/Projects/MathsPhysicsEcosystem/metaphysica).',
  'Other agents are editing other files in this working tree right now. Do not commit, push, build or run tests; never run git stash, git checkout, git reset or git add.',
  'Windows: prefix python with PYTHONIOENCODING=utf-8. Read narrowly; pipe git commands through head or cut. Never open generated output.',
  'Read docs/plan/programme/HISTORY_REVIEW.md first (about 130 lines): sources, the lane row layout, the Merge section, the rules.',
  `Planner extracts (read-only): ${ROWS} holds rows_<kind>.md (the lane rows of one kind, the lane in the first cell), catalogue.md (every fork and option that exists in the code today), timeline.md, eras.md, candidates.md and gaps.md (those sections of every lane file).`,
].join('\n')

const LAYOUT = [
  'Ledger row layout, eleven cells:',
  '`| id | idea | first seen | last seen | fate | reason recorded | reason type | sources | class | re-evaluate | test |`',
  '- `id`: I-<CODE>-001 and up, in order of first seen.',
  '- `idea`: one line that names the model choice or claim, with its formula or numbers.',
  '- `first seen`, `last seen`: date and commit or file:line, the earliest and the latest over the merged lane rows.',
  '- `fate`: one word of the vocabulary. Where lane rows disagree, the latest dated source wins and the reason cell says what it was before, with the reference.',
  '- `reason recorded`: the quote of the lane row that carries the fate, with its reference; `none` if no lane row has one.',
  '- `sources`: every lane row merged into this row, as `lane:row id`, separated by "; ". Every lane row of the kind is cited by exactly one ledger row.',
  '- `class`: `A fork:option` when catalogue.md has that option (it must be there under that fork); `B fork` for a new option on an existing fork; `C` and what a new fork would switch; `D` when it is not a path choice. Options the owner ruled on 2026-11-11 that are not in the code yet (action_bulk_spinor:weyl_holomorphic, residual_space:flat_t2, neutrino_ordering:unruled) are `B` or `C` with "(planned, wave B)".',
  '- `re-evaluate`: for an idea that is not in force: `R0` falsified by data (name the dataset); `R1` the rejection rested on a computed number and the code behind it has since changed: name the audit finding (grep docs/plan/programme/audit/ and AUDIT_SUMMARY.md) or the fix commit (grep docs/plan/programme/progress/); if you cannot name one it is not R1; `R2` rested on an argument (the argument in one line); `R3` a ruling or a removal with no recorded reason. For an idea in force: `-`.',
  '- `test`: one line: what result would count for the idea and what against.',
  'No "|" inside a cell. A falsified or withdrawn idea keeps its row. Record, do not judge.',
].join('\n')

const opts = (label, ph, schema) => ({ label, phase: ph, schema, agentType: 'executor', model: 'fable' })

const merge = ([kind, code]) => agent([
  `Target: write ${IDEAS}/ledger_${kind}.md, the merged ledger of the ideas of kind \`${kind}\`. One target, one file.`,
  COMMON,
  `Read ${ROWS}/rows_${kind}.md in full (in parts) and ${ROWS}/catalogue.md.`,
  'Two lane rows are one idea when they state the same model choice or claim: the same quantity with the same formula, or the same structure. The same topic with a different formula, number or construction is a different idea and keeps its own row. When in doubt, keep two rows.',
  `Ids use the code ${code}: I-${code}-001 and up.`,
  LAYOUT,
  `The file: a title, two lines on what it holds (the count of lane rows and of ideas), then the table. When it is written, run \`${TOOL} check ${IDEAS} "${ROWS}" ${kind}\` and repair the file until it reports no lane row without a ledger row, no lane row cited twice and eleven cells in every row.`,
  'Outcome stop: the check passes. Return the counts.',
].join('\n'), opts(`p7:merge:${kind}`, 'Merge', MERGED))

const check = async (merged, [kind]) => {
  const c = await agent([
    `Target: adversarial check of ${IDEAS}/ledger_${kind}.md. One target. Write nothing.`,
    COMMON,
    LAYOUT,
    `1. Run \`${TOOL} check ${IDEAS} "${ROWS}" ${kind}\`; each lane row it lists is a finding (lane_row_not_cited or form).`,
    `2. Merges: take 8 ledger rows that cite three or more lane rows; read those lane rows in ${ROWS}/rows_${kind}.md; report a row that merges different formulas, numbers or constructions (wrong_merge), or whose fate is not the latest dated one (wrong_fate).`,
    '3. Class: for every class A row, grep the option id in catalogue.md; it must exist under the fork named (wrong_class). Take 6 rows of class B, C or D and say whether catalogue.md already has the option.',
    '4. Flags: for every R1 row, open the audit finding or the fix commit it names; it must touch the code that produced the number (wrong_flag). For 5 rows of R0, R2 or R3, open the cited source and see that it supports the flag.',
    '5. Citations: take 6 rows spread over the table, open the cited commit hunk or file:line of the first and last seen, and report what the source does not support (unsupported_citation).',
    'Report a finding only when you opened the source. Give the corrected text in `fix`. Say what you checked and how many rows held.',
  ].join('\n'), opts(`p7:check:${kind}`, 'Check', FINDINGS))
  return { kind, merged, findings: c ? c.findings : [{ type: 'form', source: 'check', detail: 'the check returned nothing; rerun' }] }
}

const repairPrompt = (kind, code, findings, what) => [
  `Target: ${what} ${IDEAS}/ledger_${kind}.md for the findings below. One target, one file.`,
  COMMON,
  LAYOUT,
  `Ids use the code ${code}; a new idea takes the next free id. Open the source of each finding before you change or add a row; where a finding is itself wrong, leave the ledger and say why in notes. A row for an idea no lane recorded cites its source as \`sweep:<commit or file:line>\` in the sources cell.`,
  `Then run \`${TOOL} check ${IDEAS} "${ROWS}" ${kind}\` and repair until it passes.`,
  'Findings:',
  JSON.stringify(findings, null, 1),
].join('\n')

const repair = async (checked, [kind, code]) => {
  if (!checked.findings.length) return { ...checked, repaired: null }
  const r = await agent(repairPrompt(kind, code, checked.findings, 'repair'), opts(`p7:repair:${kind}`, 'Repair', MERGED))
  log(`${kind}: ${checked.findings.length} findings, repaired`)
  return { ...checked, repaired: r }
}

const perKind = (await pipeline(KINDS, merge, check, repair)).map((r, i) => r || { kind: KINDS[i][0], failed: true })
const failed = perKind.filter(r => r.failed).map(r => r.kind)
if (failed.length) log(`kinds with no ledger (rerun): ${failed.join(', ')}`)

phase('Sweep')
const TERMS = 'shadow, brane, mirror, two-time, 2T, Sp(2,R), signature, each bulk dimension (10D, 11D, 12D, 13D, 14D, 25D, 26D, 27D), G2, TCS, Joyce, Calabi-Yau, CY4, Spin(7), lattice, Leech, Niemeier, E8, octonion, Fano, b2, b3, chi_eff, generation formulas, seed, moduli, flux, Pneuma, condensate, dark energy route, H0 route, neutrino ordering, proton decay'
const GROUPS = [
  ['site-history', 'the old site repository (the lanes site-2025-11 to site-2026-02_06): commit subjects and bodies of `H/site_old.git`, and `config.py` at each version step'],
  ['engine-history', 'the engine history (the lanes engine-2026-03_08 to engine-2026-11 and engine-pre-rewrite): commit subjects and bodies of this repository and of `H/engine_old.git`'],
  ['docs-and-code', 'the documents and the code (the lanes site-decisions, site-issues, engine-docs, code-catalogue and site-2026-07_11): the decision log, the issues files, the engine docs, the variants catalogue and the ledgers of falsified and withdrawn claims in code'],
]
const swept = (await parallel(GROUPS.map(([key, what]) => () => agent([
  `Target: try to show the ledger is incomplete for one source group: ${what}. One target. Write nothing.`,
  COMMON,
  `The ledger is ${IDEAS}/ledger_<kind>.md (13 files). Search your sources for these model terms and their paraphrases: ${TERMS}.`,
  `Method: subjects and grep hits first (\`git log --all -i --grep=<term> --format='%h %ad %s' --date=short | head -40\`, \`git grep -n -i <term> <commit> -- <path> | head -20\`); for each hit that states a model choice, a claim, a removal, a refutation or a ruling, grep the ledgers for it (\`grep -n -i <words> ${IDEAS}/ledger_*.md | cut -c1-200 | head\`); open a hunk only to confirm a hit that has no ledger row.`,
  'Report each idea, claim or ruling with no ledger row as a missing_idea: its kind (one of the 13), the source reference, and the row text in `fix` in the ledger layout as far as the source gives it. Also report a ledger row whose fate the source you opened contradicts (wrong_fate). At most 40 findings, the ones that are model choices first. Say what you searched.',
].join('\n'), opts(`p7:sweep:${key}`, 'Sweep', FINDINGS))))).filter(Boolean).flatMap(r => r.findings)
log(`sweep: ${swept.length} findings`)

phase('Add')
const kindOf = f => (KINDS.find(([k]) => k === (f.kind || '').toLowerCase()) || KINDS[KINDS.length - 1])[0]
const added = (await parallel(KINDS.filter(([k]) => swept.some(f => kindOf(f) === k)).map(([kind, code]) => () =>
  agent(repairPrompt(kind, code, swept.filter(f => kindOf(f) === kind), 'add the missed ideas to'), opts(`p7:add:${kind}`, 'Add', MERGED))
))).filter(Boolean)

phase('Parts')
const parts = (await parallel([
  () => agent([
    `Target: write ${IDEAS}/ledger_timeline.md, one model timeline from 2025-11 to today. One target, one file.`,
    COMMON,
    `Read ${ROWS}/eras.md and ${ROWS}/timeline.md in full (in parts). Merge the lane timelines into one table in date order, \`| date | commit or file:line | old -> new | reason as recorded | ledger ids |\`: one row per change of the model (bulk dimension and signature, number and dimension of shadows, number of times and where they sit, internal space and its construction, b2, b3, chi, the generation formula, the seed, a ruling). Two lanes that record the same change are one row with both references. For the ledger ids, grep the ledgers (\`grep -n -i <words> ${IDEAS}/ledger_*.md | cut -c1-160 | head\`).`,
    'Above the table: the model at the start, at each version step that changed it, and today, five lines at most each. 400 lines at most. No "|" inside a cell.',
  ].join('\n'), opts('p7:timeline', 'Parts', PART)),
  () => agent([
    `Target: write ${IDEAS}/ledger_candidates.md: the candidates of the owner, and the model space seen in history. One target, one file.`,
    COMMON,
    `Read ${ROWS}/candidates.md in full, and ${IDEAS}/ledger_bulk.md, ledger_shadows.md, ledger_time.md and ledger_internal.md (the id, idea, fate, class and re-evaluate cells).`,
    'Table 1, the seven candidates of HISTORY_REVIEW.md ("Owner\'s candidates"): for each, `seen` with every reference and every ledger id that realises it or a variant of it, or `not seen`; its fate; its class; what P8 has to build to make it a disabled option that runs.',
    'Table 2, the model space: one row per distinct geometric model the history holds, `| bulk dimension and signature | shadows (number, dimension) | times (number, where) | internal space | first seen | last seen | fate | reason | ledger ids | option today |`, the model in force included. A model is distinct when any of the first four cells differs.',
    'Table 3: the combinations of the candidates of the owner that no source holds (for example three shadows with one time each), each marked `not seen`, for P8 to add as new options.',
    '250 lines at most. No "|" inside a cell. Record, do not judge.',
  ].join('\n'), opts('p7:candidates', 'Parts', PART)),
  () => agent([
    `Target: write ${IDEAS}/ledger_cross.md: ideas that sit in more than one kind ledger, and fates that disagree. One target, one file.`,
    COMMON,
    `Extract the id, idea and fate cells of all 13 ledgers (\`cut -d"|" -f2,3,6 ${IDEAS}/ledger_<kind>.md\`), and look for the same model choice or claim under two kinds (the same quantity and formula, or the same structure). Confirm each pair by reading both full rows.`,
    'Table: `| ids | idea | fates | which row is primary | note |`. Where the fates of a pair disagree, open the later source and say which fate it supports. Do not edit the kind ledgers. 200 lines at most.',
  ].join('\n'), opts('p7:cross', 'Parts', PART)),
])).filter(Boolean)

phase('Index')
const index = await agent([
  'Target: write docs/plan/programme/IDEAS_LEDGER.md, the index of the ideas ledger. One target, one file.',
  COMMON,
  `Run \`${TOOL} counts ${IDEAS}\` and \`${TOOL} check ${IDEAS} "${ROWS}"\`; use their numbers, do not count by eye.`,
  `Read ${IDEAS}/ledger_timeline.md (the lines above the table), ledger_candidates.md, ledger_cross.md and ${ROWS}/gaps.md (the "6. Second pass" lines that say still open).`,
  'The file, 250 lines at most: what the ledger is and how to read a row (the layout, the class and re-evaluate codes); the parts with their counts (13 kind ledgers, timeline, candidates, cross); counts by fate, by class and by flag; the model in force today in five lines, quoted from the timeline with its reference; every R1 row (id, idea, the fix named) and every R0 row, from `grep -h "| R1 \\|| R0 " ' + IDEAS + '/ledger_*.md | cut -d"|" -f2,3,10,11`; the class C rows (new forks P8 has to open), grouped by what they switch; the candidates of the owner in one line each; what is still open (lane gaps, lane rows the check lists, kinds that failed).',
  'It says once, near the top, that the model is speculative and unvalidated and that a row records what the history says, not whether it is right.',
].join('\n'), opts('p7:index', 'Index', PART))

return {
  kinds: perKind.map(r => ({
    kind: r.kind, failed: !!r.failed, ideas: r.repaired ? r.repaired.ideas : (r.merged ? r.merged.ideas : 0),
    findings: (r.findings || []).length, notes: r.merged ? r.merged.notes : '',
  })),
  sweep_findings: swept.length,
  added: added.map(a => ({ kind: a.kind, ideas: a.ideas, notes: a.notes })),
  parts,
  index,
}
