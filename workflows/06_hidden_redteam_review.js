export const meta = {
  name: 'finreason-hidden-redteam-review',
  description: 'Red-team every decided hidden cluster; two blind reviewers + arbiter only when a concrete challenge or CoT disagreement exists',
  phases: [
    { title: 'RedTeam', detail: 'one adversarial reviewer per cluster tries to break the consensus' },
    { title: 'Review', detail: 'two blind reviewers + arbiter for challenged clusters' },
  ],
}

const ROOT = '/home/varun/Desktop/someProj/FinReason Cup 2026'

const CONTRACT = `
PROJECT: ${ROOT}  (always cd there first; python3; no installs)
CONTEXT: FinReason Cup 2026 Task 1 hidden test cluster -- 3 questions sharing one never-seen structure. Scoring is exact:
the final answer and each checkpoint slot are compared after half-up rounding to the stated places (or exact rational /
exact enum token). Solvers are Python modules: TEMPLATE_ID + solve(text, q) -> {"final": Fraction|enum str,
"slots": {slot_id: Fraction}} returning UNROUNDED exact values (the framework rounds per result_spec); Fraction only,
never float; non-integer powers/log/exp via finreason.nums.real_pow/root/sqrt/ln/exp. Helpers: finreason/nums.py
(grab with {N} number capture, after, before, numbers), finreason/fmt.py (round_half_up).
Commands:
  python3 -m finreason.zs show <cid>                       (3 question texts, answer spec, slot descriptions)
  python3 -m finreason.zs run <cid> <solver_path>          (rendered outputs of a solver on the 3 questions)
  python3 -m finreason.hidden compare <cid> <v1> <v2> ...  (field-by-field comparison of solver variants
                                                            finreason/solvers/zs_hidden/<cid>_<v>.py)
Do not modify framework files or any existing solver file other than the one you are told to write.
`

const RED_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['consensus_correct', 'suspect'] },
    issues: { type: 'string' },
  },
  required: ['verdict', 'issues'],
}
const REV_SCHEMA = {
  type: 'object',
  properties: {
    upheld_current: { type: 'boolean' },
    rationale: { type: 'string' },
  },
  required: ['upheld_current', 'rationale'],
}
const ARB_SCHEMA = {
  type: 'object',
  properties: {
    variant: { type: 'string' },
    rationale: { type: 'string' },
  },
  required: ['variant', 'rationale'],
}

function redPrompt(it) {
  return `You are a RED-TEAM reviewer for hidden cluster ${it.cid}.
${CONTRACT}
The current answer comes from finreason/solvers/zs_hidden/${it.cid}_${it.variant}.py. It was produced by a process in
which four independent analysts (different prompts and models) wrote solvers that agreed (or were adjudicated).
Independent no-code reasoning: ${it.cot}
Analysts built on similar models can share blind spots. Your job is to try HARD to find a reading of the question under
which the current outputs are WRONG. Go sentence by sentence and check in particular:
- exactly which quantity each checkpoint slot denotes (its description, unit, and position in the chain);
- percent vs ratio vs basis points; USD vs USD millions; per-period vs annual; the base each rate applies to;
- strict vs non-strict comparisons, tie-break rules, floors/caps at zero, sign conventions, "greater of"/"lesser of";
- whether any intermediate is rounded or converted to whole units BEFORE being used (only if the text says so);
- conditional branches on all 3 instances (they may resolve differently);
- enum answers: the exact token and its decision rule.
Run: python3 -m finreason.zs show ${it.cid}  and  python3 -m finreason.zs run ${it.cid} finreason/solvers/zs_hidden/${it.cid}_${it.variant}.py
Return verdict "suspect" ONLY if you can quote specific words of the question that the current solver violates or
misreads AND a careful exam-setter would clearly have intended your reading. In that case write
finreason/solvers/zs_hidden/${it.cid}_red.py implementing your reading for ALL fields, run it, and list each issue with
the quoted words and the field values that change. Otherwise return "consensus_correct" with a brief note on what you
checked.`
}

function revPrompt(it, k, red) {
  return `You are blind reviewer #${k} for hidden cluster ${it.cid}.
${CONTRACT}
Current solver: finreason/solvers/zs_hidden/${it.cid}_${it.variant}.py (four independent analysts agreed on it, or it
was adjudicated).
Challenge from a red-team reviewer: ${red ? red.issues : '(none)'}${red && red.verdict === 'suspect' ? ` -- their alternative solver: finreason/solvers/zs_hidden/${it.cid}_red.py` : ''}
Independent no-code reasoning: ${it.cot}
Another reviewer is working independently; do NOT open any *_rev*.py file.
Decide every disputed field from the question text alone, quoting the words that settle it. Be neutral: strong prior
agreement is evidence, a specific textual argument is also evidence; arithmetic slips in no-code reasoning are not
evidence about interpretation. Then write finreason/solvers/zs_hidden/${it.cid}_rev${k}.py implementing your final
ruling for ALL fields (copy the current solver unchanged if you uphold it), and run
  python3 -m finreason.hidden compare ${it.cid} rev${k} ${it.variant}${red && red.verdict === 'suspect' ? ' red' : ''}
Return upheld_current (true if your outputs equal the current solver's on every field) and your rationale.`
}

function arbPrompt(it, r1, r2) {
  return `You are the arbiter for hidden cluster ${it.cid}.
${CONTRACT}
Two blind reviewers ruled on a challenge to the current solver finreason/solvers/zs_hidden/${it.cid}_${it.variant}.py.
Reviewer 1 (solver ${it.cid}_rev1.py): upheld_current=${r1 ? r1.upheld_current : 'n/a'}; ${r1 ? r1.rationale : 'failed'}
Reviewer 2 (solver ${it.cid}_rev2.py): upheld_current=${r2 ? r2.upheld_current : 'n/a'}; ${r2 ? r2.rationale : 'failed'}
1. Run: python3 -m finreason.hidden compare ${it.cid} rev1 rev2 ${it.variant}
2. If rev1 and rev2 produce identical outputs on every field: return variant "rev1".
3. Otherwise read the question (zs show) and the solvers, settle each remaining disagreement from the text (quote the
   deciding words). If no decisive textual evidence overturns the current solver on a field, keep the current reading
   for that field. If your ruling equals one existing variant exactly, return that variant name ("${it.variant}",
   "rev1" or "rev2"); otherwise write finreason/solvers/zs_hidden/${it.cid}_rev3.py and return "rev3".`
}

const ITEMS = args.items
log(`Red-team review over ${ITEMS.length} clusters`)

const results = await pipeline(
  ITEMS,
  (it) => agent(redPrompt(it), { label: `${it.cid}:red`, phase: 'RedTeam', schema: RED_SCHEMA, effort: 'high' }),
  async (red, it) => {
    const challenged = (red && red.verdict === 'suspect') || it.cot_disagreements > 0
    if (!challenged) {
      return { cluster: it.cid, variant: it.variant, method: 'redteam_cleared', red }
    }
    const [r1, r2] = await parallel([1, 2].map((k) => () =>
      agent(revPrompt(it, k, red), { label: `${it.cid}:rev${k}`, phase: 'Review', schema: REV_SCHEMA, effort: 'high' })))
    if (r1 && r2 && r1.upheld_current && r2.upheld_current) {
      return { cluster: it.cid, variant: it.variant, method: 'challenge_rejected', red, r1, r2 }
    }
    const arb = await agent(arbPrompt(it, r1, r2), { label: `${it.cid}:arbiter`, phase: 'Review', schema: ARB_SCHEMA, effort: 'high' })
    const allowed = [it.variant, 'rev1', 'rev2', 'rev3']
    const variant = arb && allowed.includes(arb.variant) ? arb.variant : it.variant
    return { cluster: it.cid, variant, method: variant === it.variant ? 'challenge_rejected_by_arbiter' : 'changed_after_review', red, r1, r2, arb }
  },
)
const done = results.filter(Boolean)
const counts = {}
for (const r of done) counts[r.method] = (counts[r.method] || 0) + 1
log(`review methods: ${JSON.stringify(counts)}`)
return { decisions: done, missing: ITEMS.filter((it) => !done.find((r) => r.cluster === it.cid)).map((it) => it.cid) }
