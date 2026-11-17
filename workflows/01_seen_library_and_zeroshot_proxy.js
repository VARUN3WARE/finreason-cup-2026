export const meta = {
  name: 'finreason-seen-library',
  description: 'Build gold-verified seen-template solvers and gold-blind zero-shot solvers for all 58 FinReason Task 1 topics',
  phases: [
    { title: 'Library', detail: 'per topic: write 5 seen-template solvers verified against 11 gold instances each' },
    { title: 'ZeroShot', detail: 'per topic: gold-blind solvers from 3 unlabeled instances (proxy for hidden templates)' },
  ],
}

const ROOT = '/home/varun/Desktop/someProj/FinReason Cup 2026'

const CONTRACT = `
PROJECT: ${ROOT}  (always cd there first; use python3; Python 3.10; no new pip installs needed)
TASK: FinReason Cup 2026 Task 1 -- template-generated financial word problems. Each question has a final answer
(answer_spec) and 0-3 intermediate "slots" (trace_spec.slots) that are scored separately. Scoring is EXACT:
- slots with rounding mode "exact" must equal the exact rational value (Fraction equality);
- "half_up" values are compared after half-up rounding to the stated decimal places;
- enum answers must be the exact case-sensitive token.

SOLVER MODULE CONTRACT (one module per template/cluster):
    from fractions import Fraction
    from finreason.nums import grab, after, before, numbers, grab_all, F   # exact number parsing helpers
    TEMPLATE_ID = "<template or cluster id>"
    def solve(text: str, q: dict) -> dict:
        # text = question body WITHOUT the trailing "Answer format: ..." paragraph
        # q = full question row (q["answer_spec"], q["trace_spec"]["slots"], q["question"])
        ...
        return {"final": <Fraction | enum token str>, "slots": {"<slot_id>": <Fraction>, ...}}  # every slot id exactly once
  Example:
    def solve(text, q):
        i0 = grab(r"costs USD {N} at time zero", text)          # {N} = a number capture (signed decimal or a/b rational)
        cf1 = grab(r"pays USD {N} at the end of year one", text)
        r = grab(r"discount rate is {N} percent", text) / 100
        pv1 = cf1 / (1 + r)
        return {"final": pv1 - i0, "slots": {"pv_one_trace": pv1}}
  The framework renders values (exact text or half-up rounding) from each result_spec -- return UNROUNDED exact values.
  Only round inside the computation if the question explicitly says an intermediate value is rounded AND that rounded
  value is then used downstream (use finreason.fmt.round_half_up(value, places)). Read finreason/nums.py and finreason/fmt.py for helpers.

HARD RULES:
- Exact arithmetic only: fractions.Fraction everywhere. NEVER use float (the framework raises on floats).
  Integer powers: Fraction ** int. Non-integer powers / roots / logs / exp only when genuinely required:
  finreason.nums.real_pow, root, sqrt, ln, exp (80-digit precision, return Fraction).
- Parse numbers by anchoring regexes on the surrounding words, not on fixed positions; numbers may be negative,
  decimals, or rationals like 1975/28. Never hardcode a value that varies across instances. Never branch on case_id.
- Implement every conditional rule exactly as stated (strict vs non-strict inequality, tie-breaking, floors at zero,
  sign preservation) even for branches no example exercises.
- Only create/edit your own solver files. Do NOT modify finreason/*.py framework files; if you think the framework
  has a bug, say so in your notes instead.
`

function slugOf(tid) { return tid.split('.').slice(1).join('__') }

const LIB_SCHEMA = {
  type: 'object',
  properties: {
    templates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          template_id: { type: 'string' },
          ok: { type: 'boolean' },
          passed: { type: 'integer' },
          labeled: { type: 'integer' },
          notes: { type: 'string' },
        },
        required: ['template_id', 'ok', 'passed', 'labeled', 'notes'],
      },
    },
    framework_issues: { type: 'string' },
  },
  required: ['templates', 'framework_issues'],
}

const ZS_SCHEMA = {
  type: 'object',
  properties: {
    clusters: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          cluster_id: { type: 'string' },
          ran_ok: { type: 'boolean' },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
          interpretation_notes: { type: 'string' },
        },
        required: ['cluster_id', 'ran_ok', 'confidence', 'interpretation_notes'],
      },
    },
  },
  required: ['clusters'],
}

function libPrompt(topic) {
  return `You are building the VERIFIED SOLVER LIBRARY for one topic of FinReason Task 1 seen templates.
${CONTRACT}
YOUR TOPIC: ${topic}
Get your 5 template ids with:
  cd "${ROOT}" && python3 -c "import json;print('\\n'.join(json.load(open('work/topics.json'))['${topic}']))"

For EACH template id:
 1. python3 -m finreason.check show <template_id> 11
    -> prints the module slug, all 11 labeled instances with gold final + gold slot values, and 2 unlabeled leaderboard instances.
 2. Write finreason/solvers/seen/<slug>.py  (slug = template id without the leading "fp." with "." replaced by "__").
    If the file already exists and passes, keep it.
 3. python3 -m finreason.check one <template_id>
    -> must end with "ok": true  (all labeled instances pass AND no smoke errors on unlabeled leaderboard/test rows).
    Iterate until ok. The gold values are authoritative: if gold disagrees with your reading of the text, work out the
    generator's actual convention from the gold (e.g. intermediate rounding, day counts, sign conventions, what a
    slot really measures) and implement that -- then note it.
 4. Re-read your solver once more for robustness: would it still parse and compute correctly for any other
    parameter values of this template (negative results, zero, ties at thresholds, the other side of every condition)?

Return the structured summary: per template ok/passed/labeled and short notes on any conventions or gold quirks discovered.`
}

function zsPrompt(topic) {
  return `You are testing a GOLD-FREE (zero-shot) solving pipeline for FinReason Task 1. You must solve question clusters
WITHOUT ever seeing answers, exactly as we will have to for never-seen test templates.
${CONTRACT}
STRICT BLINDNESS RULES (this is a measured experiment -- violating them invalidates it):
- Do NOT open, cat, grep, list or import anything under toolkit/, work/ (except the one command below), or
  finreason/solvers/seen/ ; do NOT read any *gold*, *targets* or *manifest* file; do NOT run finreason.check.
- Allowed: finreason/*.py framework files (nums.py, fmt.py, zs.py, check.py source), your own files, and these commands:
    cd "${ROOT}" && python3 -c "import json;print('\\n'.join(json.load(open('work/topics.json'))['${topic}']))"   (your 5 cluster ids)
    python3 -m finreason.zs show <cluster_id>          (question texts + slot descriptions + specs, no answers)
    python3 -m finreason.zs run <cluster_id> <path>    (runs your solver on the cluster, prints rendered outputs)

For EACH of your 5 cluster ids:
 1. python3 -m finreason.zs show <cluster_id>   -- read all 3 instances, the answer spec and every slot description carefully.
 2. Write finreason/solvers/zs_proxy/<slug>.py with TEMPLATE_ID = "<cluster_id>"
    (slug = cluster id without the leading "fp." with "." replaced by "__").
 3. python3 -m finreason.zs run <cluster_id> finreason/solvers/zs_proxy/<slug>.py  -- must run with no errors.
 4. Verify independently: re-derive at least one instance a DIFFERENT way (e.g. a separate python3 -c computation with
    Fractions written from scratch, or algebraic re-derivation) and check final + every slot agree. Check each slot
    value matches its description/position and unit (percent vs ratio, USD vs USD millions, per-period vs annual).
 Interpretation guidance: follow the question's explicit formulas and definitions literally; when wording is ambiguous,
 prefer the standard textbook finance convention and the reading that makes all 3 instances consistent.

Return per cluster: ran_ok, your confidence (high/medium/low) that final AND all slots are exactly right, and the
interpretation choices you made (especially any ambiguity).`
}

const topics = args.topics
log(`Building library + zero-shot proxies for ${topics.length} topics`)

const results = await pipeline(
  topics,
  (topic) => agent(libPrompt(topic), { label: `lib:${topic}`, phase: 'Library', schema: LIB_SCHEMA }),
  (lib, topic) => agent(zsPrompt(topic), { label: `zs:${topic}`, phase: 'ZeroShot', schema: ZS_SCHEMA })
    .then((zs) => ({ topic, lib, zs })),
)

const out = results.filter(Boolean)
const libTemplates = out.flatMap((r) => (r.lib && r.lib.templates) || [])
const okCount = libTemplates.filter((t) => t.ok).length
log(`Library: ${okCount}/${libTemplates.length} templates reported ok`)
return {
  library: out.map((r) => ({ topic: r.topic, lib: r.lib })),
  zeroshot: out.map((r) => ({ topic: r.topic, zs: r.zs })),
  missing_topics: topics.filter((t) => !out.find((r) => r.topic === t)),
}
