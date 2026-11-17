---
license: cc-by-4.0
task_categories:
- question-answering
language:
- en
tags:
- finance
- xbrl
- sec-edgar
- audit
pretty_name: FinReason Cup 2026 Task 3 hidden phases
size_categories:
- 1K<n<10K
---

# FinReason Cup 2026 · Task 3 — development and test inputs

Questions only. The answers stay with the organizers.

This is the input side of the two ranked phases of Task 3, *Financial Audit
Verification*, at the [FinReason Cup 2026](https://the-finai.github.io/IEEE-bigdata-cup/task3/)
(IEEE Big Data Cup 2026, Challenge 03). The practice phase is separate and
ships its answers with it: see [TheFinAI/FinMR](https://huggingface.co/datasets/TheFinAI/FinMR)
and the [starter kit](https://github.com/The-FinAI/IEEE-bigdata-cup/tree/main/finreason_task3).

| File | Cases | Phase |
| --- | --- | --- |
| `development_inputs.jsonl` | 680 | Development — scored, ranked, public leaderboard |
| `test_inputs.jsonl` | 680 | Test — acceptance receipt only, decides the final result |

## Revision, 28 September 2026

The filing content was incomplete in part of the set and has been corrected.
Both files were replaced: 453 of the 680 development cases and 367 of the 680
test cases now carry more of their filing than before.

Nothing else moved. The ids are the same, the expected answers are byte for
byte identical, and the development/test split is unchanged, so a prediction
file written against the earlier download is still structurally valid and any
score already on the leaderboard is still a true measurement.

What does change is how hard the questions are. Reading a value out of a filing
that was missing part of itself is harder than reading it out of a complete one:
the organizers' rule-based baseline drops from a 23.97% extraction-error rate to
10.88% on the corrected content, and its accuracy rises from 25.00% to 31.76%.
If you have already submitted, re-downloading and submitting again is worth a
try, and costs one of your three development attempts for the day.

## Format

One JSON object per line, two fields:

```json
{"id": "DEV3_000000", "query": "You are an auditor for XBRL filings. ..."}
```

`query` carries the whole case: the instruction, the question, and the filing's
schema, presentation, calculation, definition and label linkbases, its instance
document, and the US GAAP taxonomy. Answer with the value the filing reports for
the target element and the value its own calculation relationships imply:

```json
{"id": "DEV3_000000", "extracted_value": "-1284", "calculated_value": "1284"}
```

Emit `"0"` when your system cannot determine a value. Never omit a line — a
missing id invalidates the whole submission rather than costing you one case.
Predictions are matched by `id`, never by row order.

## How to submit

Upload `predictions.jsonl`, or a ZIP containing exactly one root-level file of
that name, at the [Task 3 submission page](https://the-finai.github.io/IEEE-bigdata-cup/task3/submit/).
Development returns scores, a receipt and a rank. Test returns an acceptance
receipt and nothing else.

## Two things worth knowing

**No rule labels.** The practice set tells you which data-quality rule each case
came from. These files do not, on purpose: for one of the three rules the label
alone gives away the answer's shape.

**Do not look the answers up.** Each case is a real SEC filing and says so in
its own identifiers, so you can work out which one it is. Deriving the two
values from the filing materials shipped with the case is the task. Reading
either value out of a service that already publishes data-quality findings for
that filing is not, and a submission produced that way is not a valid entry.
See the [Terms of Participation](https://the-finai.github.io/IEEE-bigdata-cup/terms/).

## Construction

Drawn from SEC EDGAR XBRL filings across 455 companies. Development and test
share no company: a filing yields many cases, so splitting by case would put
the same financial statements on both sides. The rule mix is fixed rather than
natural, so that a system which simply negates whatever it extracted cannot
place well.

Deadline: **15 October 2026, 23:59 AoE**.
