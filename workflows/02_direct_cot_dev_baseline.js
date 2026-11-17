export const meta = {
  name: 'finreason-direct-baseline',
  description: 'Ablation: direct chain-of-thought answers (no code execution) on the 290 labeled dev questions',
  phases: [{ title: 'Answer', detail: '29 agents x 10 dev questions, reasoning only, no tools after reading' }],
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
        },
        required: ['case_id', 'final', 'slots'],
      },
    },
  },
  required: ['answers'],
}
function prompt(i) {
  return `This is a measured ABLATION: answering financial reasoning questions by pure reasoning, WITHOUT executing any code.
Run exactly ONE command to read your 10 questions:
  cd "${ROOT}" && python3 -m finreason.baseline_direct show ${i}
After that you must NOT use any tool at all (no Bash, no python, no calculator, no file reads) -- do all arithmetic
yourself in your head/thinking. Do not look at any other file.

For each question give:
- final: the final answer in the requested format (decimal rounded half-up as specified, or the exact enum token).
- slots: a value for every SLOT listed. A spec with rounding mode "exact" requires the EXACT value: a finite decimal if it
  terminates, otherwise an irreducible fraction "numerator/denominator" (e.g. "17800/23"). Half-up specs: round as stated.
Return all 10 answers in the structured output (case_id exactly as printed).`
}
const idx = Array.from({ length: 29 }, (_, i) => i)
const res = await parallel(idx.map((i) => () => agent(prompt(i), { label: `direct:${i}`, phase: 'Answer', schema: SCHEMA })))
const answers = res.filter(Boolean).flatMap((r) => r.answers)
log(`collected ${answers.length} answers from ${res.filter(Boolean).length}/29 agents`)
return { answers }
