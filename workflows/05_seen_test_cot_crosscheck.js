export const meta = {
  name: 'finreason-seen-test-cot-crosscheck',
  description: 'Independent no-execution answers for the 580 seen-structure test questions (third check on the verified library)',
  phases: [{ title: 'Reason', detail: '58 agents x 10 questions, reasoning only, no tools after reading' }],
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
  return `You are an independent analyst answering financial reasoning questions by PURE REASONING, without executing code.
Run exactly ONE command to read your 10 questions:
  cd "${ROOT}" && python3 -m finreason.baseline_direct show-seen-test ${i}
After that do NOT use any tool at all (no Bash, python, calculator or file reads); do all arithmetic yourself, exactly.
For each question give:
- final: the final answer per the ANSWER SPEC (decimal rounded half-up as stated, or the exact enum token);
- slots: a value for EVERY listed SLOT. Rounding mode "exact" requires the EXACT value: a finite decimal if it
  terminates, otherwise an irreducible fraction "numerator/denominator". Half-up specs: round as stated.
Follow every stated rule literally (thresholds, strict vs non-strict comparisons, floors, sign preservation).
Return all 10 answers (case_id exactly as printed).`
}
const idx = Array.from({ length: 58 }, (_, i) => i)
const res = await parallel(idx.map((i) => () => agent(prompt(i), { label: `seencot:${i}`, phase: 'Reason', schema: SCHEMA })))
const answers = res.filter(Boolean).flatMap((r) => r.answers)
log(`collected ${answers.length} answers from ${res.filter(Boolean).length}/58 agents`)
return { answers }
