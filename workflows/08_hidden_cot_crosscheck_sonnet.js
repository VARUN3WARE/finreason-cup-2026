export const meta = {
  name: 'finreason-hidden-cot-crosscheck-sonnet',
  description: 'Third independent no-execution pass on another model (Sonnet) for all 116 hidden clusters',
  phases: [{ title: 'Reason', detail: 'one agent per cluster, reasoning only, no tools after reading' }],
}
const ROOT = '/home/varun/Desktop/someProj/FinReason Cup 2026'
const SCHEMA = {
  type: 'object',
  properties: {
    answers: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          case_id: { type: 'string' },
          final: { type: 'string' },
          slots: { type: 'object', additionalProperties: { type: 'string' } },
          interpretation: { type: 'string' },
        },
        required: ['case_id', 'final', 'slots', 'interpretation'],
      },
    },
  },
  required: ['answers'],
}
function prompt(cid) {
  return `You are an independent analyst answering financial reasoning questions by PURE REASONING, without executing code.
Run exactly ONE command to read your 3 questions (one shared structure, different numbers):
  cd "${ROOT}" && python3 -m finreason.zs show ${cid}
After that do NOT use any tool at all (no Bash, python, calculator or file reads); do all arithmetic yourself, exactly
(keep fractions exact; round only where the answer/slot spec says).
For each of the 3 instances give:
- final: the final answer formatted per the ANSWER SPEC (half-up to the stated decimal places, or the exact enum token);
- slots: a value for EVERY listed SLOT, formatted per that slot's spec (half-up to its stated places; "exact" means a
  finite decimal if it terminates, else an irreducible fraction "p/q");
- interpretation: one or two sentences on how you read any ambiguous part (units, which base, ties, rounding stage).
Read every sentence carefully: each one usually encodes a rule (thresholds, strict vs non-strict, tie-breaks, floors,
which quantity a checkpoint denotes). Return all 3 answers with case_ids exactly as printed.`
}
const ids = (args && args.clusters) || Array.from({ length: 116 }, (_, i) => 'h' + String(i + 1).padStart(3, '0'))
const res = await parallel(ids.map((cid) => () => agent(prompt(cid), { label: `cotS:${cid}`, phase: 'Reason', schema: SCHEMA, model: 'sonnet' })
  .then((r) => (r ? { cluster: cid, answers: r.answers } : null))))
const ok = res.filter(Boolean)
log(`collected ${ok.length}/116 clusters`)
return { clusters: ok, missing: ids.filter((c) => !ok.find((r) => r.cluster === c)) }
