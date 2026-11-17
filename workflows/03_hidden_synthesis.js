export const meta = {
  name: 'finreason-hidden-synthesis',
  description: 'Gold-free multi-lens program synthesis + adjudication for FinReason Task 1 hidden-structure test clusters',
  phases: [
    { title: 'Synthesize', detail: '4 independent lenses (literal, domain-model, ambiguity-hunting, hand-solve) per cluster' },
    { title: 'Adjudicate', detail: 'compare variants; if any field disagrees, two blind adjudicators + arbiter' },
  ],
}

const ROOT = '/home/varun/Desktop/someProj/FinReason Cup 2026'

const CONTRACT = `
PROJECT: ${ROOT}  (always cd there first; use python3; Python 3.10; no installs needed)
TASK: FinReason Cup 2026 Task 1 -- financial word problems with a final answer (answer_spec) and 1-3 intermediate
"checkpoint" slots (trace_spec.slots), each scored separately with EXACT matching:
- "half_up" values are compared after half-up rounding to the stated decimal places;
- "exact" values must equal the exact rational value; enum answers must be the exact case-sensitive token.
These questions belong to a cluster of 3 instances that share one NEVER-SEEN structure (different numbers, and possibly
different branch outcomes). No answers exist anywhere on disk: you must get it right from the text alone.

SOLVER MODULE CONTRACT:
    from fractions import Fraction
    from finreason.nums import grab, after, before, numbers, grab_all, F   # exact number parsing helpers
    TEMPLATE_ID = "<cluster id>"
    def solve(text: str, q: dict) -> dict:
        # text = question body WITHOUT the trailing "Answer format: ..." paragraph (q["question"] has the full text)
        return {"final": <Fraction | enum token str>, "slots": {"<slot_id>": <Fraction>, ...}}   # every slot id exactly once
  Example:
        i0 = grab(r"costs USD {N} at time zero", text)     # {N} = number capture: signed decimal or rational like 1975/28
        r = grab(r"discount rate is {N} percent", text) / 100
  Read finreason/nums.py and finreason/fmt.py for helpers. Framework renders every value from its result_spec.

RULES:
- Exact arithmetic: fractions.Fraction everywhere, NEVER float. Integer powers: Fraction ** int. Non-integer powers,
  roots, logs, exp only when genuinely required: finreason.nums.real_pow / root / sqrt / ln / exp (80-digit, return Fraction).
  Equations with no closed form (e.g. an IRR): solve numerically with Fractions/80-digit precision (bisection) so the
  final rounding is certain.
- Return UNROUNDED exact values for the final answer and every checkpoint; the framework applies each result_spec's
  rounding. "Independently round"/"never feed displayed checkpoints into the calculation" means exactly this.
  Only round INSIDE the computation when the text says a rounded/whole-unit value is itself used downstream
  (whole shares, whole credits, cents before multiplying, floor/ceiling) -- then use exactly the stated rounding mode
  (finreason.fmt.round_half_up(value, places) for half-up; Fraction floor via math.floor for floors).
- Units: "percent" results are in percent (12.5 means 12.5%); "ratio"/"dimensionless"/"multiple" are plain ratios;
  "usd_million" results are in USD millions. Probabilities are exact expectations. "Fictional" scenarios: apply only
  the rules stated, never real-world law.
- Conditions, thresholds, ties, max/min, floors at zero, sign preservation: implement exactly as worded
  (strictly greater vs at least, the stated tie-break). Branches may resolve differently across the 3 instances.
- Each checkpoint must be the quantity its description names, in its unit, at its position in the chain.
- Parse numbers by anchoring regexes on surrounding words; never hardcode instance values; never branch on case_id.
  The solver must run on all 3 instances.
- Commands available:
    python3 -m finreason.zs show <cluster_id>               (all 3 instance texts + specs + slot descriptions)
    python3 -m finreason.zs run <cluster_id> <solver_path>  (run your solver on the 3 instances, print rendered outputs)
`

const LENSES = [
  {
    key: 'lit', model: undefined,
    text: `YOUR APPROACH -- LITERAL TRANSCRIPTION: go through the question sentence by sentence and turn every sentence into
a named variable, definition or rule in code, in the order the text gives them. Use the question's own formulas and
definitions verbatim wherever it states them.`,
  },
  {
    key: 'dom', model: 'sonnet',
    text: `YOUR APPROACH -- FINANCE MODEL FIRST: before coding, write at the top of the file (as comments) a precise model of
the economic quantity being computed and how each given number enters it, using standard finance conventions unless the
text explicitly overrides them (note every override). Then implement that model.`,
  },
  {
    key: 'skep', model: 'fable',
    text: `YOUR APPROACH -- AMBIGUITY HUNTING: before coding, list every point where two competent analysts could disagree
(units, percent vs ratio, which base a rate applies to, strict vs non-strict comparisons, tie rules, the order of
operations, when/if rounding happens, exactly which quantity each checkpoint denotes, per-period vs annual). Resolve each
one with explicit textual evidence, record the resolutions as comments at the top of the file, then implement.`,
  },
  {
    key: 'hand', model: undefined,
    text: `YOUR APPROACH -- HAND-SOLVE FIRST: before writing any solver code, solve the FIRST instance completely by careful
step-by-step reasoning with exact fractions (scratch calculations in python3 -c are fine), writing down the final answer
and every checkpoint. Then write the general solver, run it, and make sure it reproduces your hand solution exactly;
if they differ, find out which one is wrong and fix it.`,
  },
]

const LENS_SCHEMA = {
  type: 'object',
  properties: {
    ran_ok: { type: 'boolean' },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
    ambiguities: { type: 'string' },
  },
  required: ['ran_ok', 'confidence', 'ambiguities'],
}
const ADJ_SCHEMA = {
  type: 'object',
  properties: {
    decision: { type: 'string', enum: ['unanimous', 'adjudicated'] },
    variant: { type: 'string' },
    rationale: { type: 'string' },
  },
  required: ['decision', 'variant', 'rationale'],
}
const ARB_SCHEMA = {
  type: 'object',
  properties: {
    adjudicators_agreed: { type: 'boolean' },
    variant: { type: 'string', enum: ['adjA', 'final'] },
    rationale: { type: 'string' },
  },
  required: ['adjudicators_agreed', 'variant', 'rationale'],
}

function lensPrompt(cid, lens) {
  return `You are one of several INDEPENDENT analysts writing a solver for hidden question cluster ${cid}.
${CONTRACT}
${lens.text}

Write your solver to: finreason/solvers/zs_hidden/${cid}_${lens.key}.py   (TEMPLATE_ID = "${cid}")
INDEPENDENCE: do NOT open or list any other file in finreason/solvers/zs_hidden/ -- other analysts' work must not
influence yours. Do not modify framework files.
Steps: python3 -m finreason.zs show ${cid}  ->  write the solver  ->  python3 -m finreason.zs run ${cid} finreason/solvers/zs_hidden/${cid}_${lens.key}.py
(must run without errors on all 3 instances)  ->  re-read the question once more against your code, checking every
sentence is honoured and every checkpoint is the right quantity in the right unit.
Return ran_ok, your confidence that the final answer AND every checkpoint are exactly right, and the ambiguities you resolved.`
}

function adjPrompt(cid, which, blindTo) {
  return `You are adjudicator ${which} for hidden question cluster ${cid}. Several independent analysts wrote solvers:
finreason/solvers/zs_hidden/${cid}_{lit,dom,skep,hand}.py  (some may be missing).
${CONTRACT}
1. Run: python3 -m finreason.hidden compare ${cid}
${which === 'A'
    ? `2. If it prints unanimous=True (all variants identical on every field of all 3 instances, no errors), return
   decision="unanimous", variant="lit" with a one-line rationale. Do nothing else.
3. Otherwise adjudicate:`
    : `2. You are a SECOND, BLIND adjudicator: do NOT open ${blindTo} or any *_adj*/*_final* file. Adjudicate:`}
   - python3 -m finreason.zs show ${cid}; read every variant's solver.
   - For EVERY disagreeing field, decide which interpretation the question text actually specifies, quoting the exact words
     that settle it. A majority is evidence, not proof (analysts share blind spots); the text decides. Also scan the
     fields everyone agrees on for a shared mistake.
   - Write finreason/solvers/zs_hidden/${cid}_adj${which}.py implementing the correct interpretation for ALL fields
     (TEMPLATE_ID = "${cid}"); start from the best variant.
   - Confirm with: python3 -m finreason.hidden compare ${cid} adj${which} lit dom skep hand
   Return decision="adjudicated", variant="adj${which}", and a rationale covering each disputed field.`
}

function arbiterPrompt(cid, a, b) {
  return `You are the final arbiter for hidden question cluster ${cid}. Two blind adjudicators ruled on disagreements between
independent solvers. Their solvers: finreason/solvers/zs_hidden/${cid}_adjA.py and ${cid}_adjB.py.
${CONTRACT}
Adjudicator A rationale: ${a.rationale}
Adjudicator B rationale: ${b.rationale}

1. Run: python3 -m finreason.hidden compare ${cid} adjA adjB
2. If unanimous=True: return adjudicators_agreed=true, variant="adjA".
3. Otherwise: python3 -m finreason.zs show ${cid}, read both adjudicator solvers (and the lit/dom/skep/hand variants if
   useful), settle every remaining disagreement from the question text (quote the deciding words), write
   finreason/solvers/zs_hidden/${cid}_final.py implementing the correct interpretation for ALL fields, confirm with
   python3 -m finreason.hidden compare ${cid} final adjA adjB, and return adjudicators_agreed=false, variant="final".`
}

// args.items: [{cid, lenses: [lens keys still to synthesize]}]  (args.clusters = all four lenses each)
const ITEMS = args.items || args.clusters.map((cid) => ({ cid, lenses: LENSES.map((l) => l.key) }))
const CLUSTERS = ITEMS.map((it) => it.cid)
const LENSES_FOR = Object.fromEntries(ITEMS.map((it) => [it.cid, it.lenses]))
log(`Hidden synthesis over ${CLUSTERS.length} clusters`)

const results = await pipeline(
  CLUSTERS,
  (cid) => parallel(LENSES.filter((lens) => LENSES_FOR[cid].includes(lens.key)).map((lens) => () =>
    agent(lensPrompt(cid, lens), { label: `${cid}:${lens.key}`, phase: 'Synthesize', schema: LENS_SCHEMA, model: lens.model })
      .then((r) => ({ lens: lens.key, ...(r || { ran_ok: false, confidence: 'low', ambiguities: 'agent failed' }) })))),
  async (lensResults, cid) => {
    // args.synthesize_only: stop after the lenses; agreement is then checked offline and only
    // disagreeing clusters are sent to adjudication (saves one adjudicator agent per unanimous cluster).
    if (args.synthesize_only) return { cluster: cid, lenses: lensResults, variant: null, method: 'synthesized_only' }
    const a = await agent(adjPrompt(cid, 'A', null), { label: `${cid}:adjA`, phase: 'Adjudicate', schema: ADJ_SCHEMA, effort: 'high' })
    if (!a) return { cluster: cid, lenses: lensResults, variant: 'lit', method: 'adjA_failed' }
    if (a.decision === 'unanimous') return { cluster: cid, lenses: lensResults, variant: 'lit', method: 'unanimous', adjA: a }
    const b = await agent(adjPrompt(cid, 'B', `${cid}_adjA.py`), { label: `${cid}:adjB`, phase: 'Adjudicate', schema: ADJ_SCHEMA, effort: 'high' })
    if (!b) return { cluster: cid, lenses: lensResults, variant: 'adjA', method: 'adjA_only', adjA: a }
    const arb = await agent(arbiterPrompt(cid, a, b), { label: `${cid}:arbiter`, phase: 'Adjudicate', schema: ARB_SCHEMA, effort: 'high' })
    return {
      cluster: cid, lenses: lensResults, adjA: a, adjB: b, arbiter: arb,
      variant: arb ? arb.variant : 'adjA',
      method: arb ? (arb.adjudicators_agreed ? 'adjudicators_agreed' : 'arbitrated') : 'arbiter_failed',
    }
  },
)
const done = results.filter(Boolean)
const counts = {}
for (const r of done) counts[r.method] = (counts[r.method] || 0) + 1
log(`methods: ${JSON.stringify(counts)}`)
return { decisions: done, missing: CLUSTERS.filter((c) => !done.find((r) => r.cluster === c)) }
