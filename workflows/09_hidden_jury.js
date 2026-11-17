export const meta = {
  name: 'finreason-hidden-jury',
  description: 'Extended blind jury (6 jurors on 3 models) for contested Task 1 hidden clusters; each juror writes and runs its own exact solver',
  phases: [{ title: 'Jury', detail: '7 clusters x 6 blind jurors (2 Opus, 2 Sonnet, 2 Fable)' }],
}
const ROOT = '/home/varun/Desktop/someProj/FinReason Cup 2026'
const CONTRACT = `
PROJECT: ${ROOT}  (always cd there first; use python3; no installs)
TASK: FinReason Cup 2026 Task 1 -- a financial word problem cluster: 3 questions sharing one structure (different
numbers). Each question has a final answer (answer_spec) and 1-3 checkpoint slots (trace_spec.slots), scored by EXACT
match: half_up values after rounding to the stated places, exact values by rational equality, enums by exact token.
SOLVER CONTRACT:
    from fractions import Fraction
    from finreason.nums import grab, after, before, numbers, grab_all, F   # {N} in grab() = a number capture
    TEMPLATE_ID = "<cluster id>"
    def solve(text: str, q: dict) -> dict:
        return {"final": <Fraction | enum token str>, "slots": {"<slot_id>": <Fraction>, ...}}   # every slot once
  Return UNROUNDED exact values (the framework rounds per result_spec). Fraction only, never float; real powers/logs via
  finreason.nums.real_pow/root/sqrt/ln/exp. Round inside the computation only where the text says a rounded value is used.
  Units: percent results in percent; ratio/dimensionless as plain ratios; usd_million in millions.
Commands:
    python3 -m finreason.zs show <cluster_id>               (the 3 questions, answer spec, slot descriptions)
    python3 -m finreason.zs run <cluster_id> <solver_path>  (rendered outputs of your solver)
`
function prompt(cid, k) {
  return `You are independent juror #${k} for question cluster ${cid}. Other jurors work separately; do NOT open, list or
read any file in finreason/solvers/zs_hidden/ other than the one you write, and do not read anything under work/.
${CONTRACT}
Read every sentence of all 3 questions carefully: each sentence usually encodes a rule (definitions, units, which base a
rate applies to, strict vs non-strict comparisons, tie-breaks, floors, what each checkpoint denotes and in which unit,
whether anything is rounded before use). Solve the FIRST instance by hand with exact fractions first, then write
finreason/solvers/zs_hidden/${cid}_jury${k}.py (TEMPLATE_ID = "${cid}"), run it on all 3 instances, and check it
reproduces your hand solution and honours every sentence.
Return the rendered outputs exactly as printed by the run command, and your interpretation of any point a careful
analyst could read two ways.`
}
const SCHEMA = {
  type: 'object',
  properties: {
    outputs: { type: 'array', items: { type: 'object', properties: {
      case_id: { type: 'string' }, final: { type: 'string' },
      slots: { type: 'object', additionalProperties: { type: 'string' } } },
      required: ['case_id', 'final', 'slots'] } },
    interpretation: { type: 'string' },
  },
  required: ['outputs', 'interpretation'],
}
const CLUSTERS = args.clusters
const JURORS = [
  { k: 1, model: undefined }, { k: 2, model: undefined },
  { k: 3, model: 'sonnet' }, { k: 4, model: 'sonnet' },
  { k: 5, model: 'fable' }, { k: 6, model: 'fable' },
]
const items = CLUSTERS.flatMap((cid) => JURORS.map((j) => ({ cid, ...j })))
const res = await parallel(items.map((it) => () =>
  agent(prompt(it.cid, it.k), { label: `${it.cid}:jury${it.k}`, phase: 'Jury', schema: SCHEMA, model: it.model })
    .then((r) => (r ? { cluster: it.cid, juror: it.k, model: it.model || 'opus', ...r } : null))))
return { verdicts: res.filter(Boolean) }
