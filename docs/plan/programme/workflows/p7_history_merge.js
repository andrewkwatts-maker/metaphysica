export const meta = {
  name: 'pm-p7-history-merge',
  description: 'P7: merge the lane files into IDEAS_LEDGER.md, try to refute it, repair once',
  phases: [
    { title: 'Merge', detail: 'one ledger from the lane files' },
    { title: 'Refute', detail: 'missed ideas, then rows checked against their citations' },
    { title: 'Repair', detail: 'one round, then a re-check' },
  ],
}

// Runs one agent at a time. Run it after every lane file exists in docs/plan/programme/ideas/.

const MERGED = {
  type: 'object',
  properties: {
    ledger: { type: 'string' },
    ideas: { type: 'number' },
    class_counts: { type: 'string' },
    reevaluate_counts: { type: 'string' },
    lanes_missing: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
  required: ['ledger', 'ideas', 'lanes_missing'],
}
const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          kind: { type: 'string', enum: ['missing_idea', 'wrong_row', 'unsupported_citation', 'wrong_class'] },
          row: { type: 'string' },
          source: { type: 'string' },
          detail: { type: 'string' },
        },
        required: ['kind', 'source', 'detail'],
      },
    },
    checked: { type: 'string' },
  },
  required: ['findings', 'checked'],
}

const COMMON = [
  'Read docs/plan/programme/HISTORY_REVIEW.md first: sources, row layout, the Merge section, rules.',
  'Read-only outside docs/plan/programme/. Do not commit, push, build or run tests.',
  'Read narrowly; pipe git commands through head or cut.',
].join('\n')

phase('Merge')
const merged = await agent([
  'Target: write docs/plan/programme/IDEAS_LEDGER.md from the lane files in docs/plan/programme/ideas/.',
  COMMON,
  'Follow the Merge section exactly: deduplicate under ids I-001..., keep every source reference,',
  'one model timeline from 2025-11 to today, the owner\'s candidates table, then the class,',
  're-evaluate and test columns. For R1, name the audit finding (docs/plan/programme/audit/) or the',
  'fix commit (docs/plan/programme/progress/) that changed the code behind the number; if you cannot',
  'name one, it is not R1. Do not drop a falsified or withdrawn idea. If the ledger passes 500',
  'lines, split the idea rows by kind into docs/plan/programme/ideas/ledger_<kind>.md and keep the',
  'timeline, the candidates table and an index in IDEAS_LEDGER.md.',
].join('\n'), { label: 'p7:merge', phase: 'Merge', schema: MERGED, agentType: 'executor', model: 'opus' })

phase('Refute')
const lenses = [
  ['missed', 'Try to show the ledger is incomplete. Sweep every source in the Sources and Lanes sections for model terms (shadow, time, signature, each bulk dimension, brane, mirror, G2, TCS, Joyce, Calabi-Yau, Spin(7), lattice, Leech, octonion, generation formulas, seeds) and report each idea, claim or ruling that has no ledger row. Subjects and grep hits first; open a hunk only to confirm.'],
  ['citations', 'Try to show the ledger is wrong. Take 25 rows spread over kinds and eras, open the cited commit hunk or file:line of each, and report every row whose fate, reason, reason type, class or re-evaluate flag the source does not support. Check every R1 row: the named fix must really touch the code that produced the number.'],
]
const reviews = []
for (const [key, ask] of lenses) {
  const r = await agent([
    `Target: adversarial review of docs/plan/programme/IDEAS_LEDGER.md, lens "${key}".`,
    COMMON,
    ask,
    'Write nothing. Return the findings with their sources, and say what you checked.',
  ].join('\n'), { label: `p7:refute:${key}`, phase: 'Refute', schema: FINDINGS, agentType: 'executor', model: 'opus' })
  reviews.push(r)
}
const findings = reviews.filter(Boolean).flatMap(r => r.findings)
log(`refute: ${findings.length} findings`)
if (!findings.length) {
  return { merged, findings: [], repaired: null, still_open: [] }
}

phase('Repair')
const repaired = await agent([
  'Target: repair docs/plan/programme/IDEAS_LEDGER.md (and its ledger_<kind>.md parts) for the findings below.',
  COMMON,
  'Open the source of each finding before you change a row. Add missing ideas as new ids; correct',
  'wrong rows; where a finding is itself wrong, leave the row and say why in your notes.',
  'Findings:',
  JSON.stringify(findings, null, 1),
].join('\n'), { label: 'p7:repair', phase: 'Repair', schema: MERGED, agentType: 'executor', model: 'opus' })

const recheck = await agent([
  'Target: re-check docs/plan/programme/IDEAS_LEDGER.md against the findings below after a repair round.',
  COMMON,
  'For each finding, open the ledger and the source and say whether it is now closed. Report only',
  'the ones still open, plus anything the repair broke. Write nothing.',
  'Findings:',
  JSON.stringify(findings, null, 1),
].join('\n'), { label: 'p7:recheck', phase: 'Repair', schema: FINDINGS, agentType: 'executor', model: 'opus' })

return { merged, findings, repaired, still_open: recheck ? recheck.findings : ['re-check returned nothing'] }
