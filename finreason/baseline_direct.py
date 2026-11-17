"""Direct-answer (no program execution) LLM baseline on the labeled dev split.

  python -m finreason.baseline_direct show <batch_index>     # print one batch of dev questions (no gold)
  python -m finreason.baseline_direct show-seen-test <batch>  # print one batch of seen-structure test questions
  python -m finreason.baseline_direct score <answers.json>   # official scorer on collected answers

Answers JSON: list of {"case_id", "final", "slots": {slot_id: value}} (strings as written by the model).
"""

from __future__ import annotations

import json
import subprocess
import sys

from . import data

sys.path.insert(0, str(data.TOOLKIT))
from finreason_task1.contracts import validate_submission  # noqa: E402

BATCH = 10


def batches() -> list[list[str]]:
    ids = [q["case_id"] for q in data.questions("dev")]
    return [ids[i : i + BATCH] for i in range(0, len(ids), BATCH)]


def seen_test_batches() -> list[list[str]]:
    members = data.template_members()
    ids = sorted(cid for tid in members for cid in members[tid].get("test", []))
    return [ids[i : i + BATCH] for i in range(0, len(ids), BATCH)]


def show(index: int, groups: list[list[str]] | None = None) -> None:
    qs = data.by_id()
    for cid in (groups or batches())[index]:
        q = qs[cid]
        print(f"=== case_id {cid}")
        print(q["question"])
        for s in q["trace_spec"]["slots"]:
            print(f"SLOT {s['slot_id']}: {s['description']} spec={json.dumps(s['result_spec'])}")
        print(f"ANSWER SPEC: {json.dumps(q['answer_spec'])}\n")


def to_rows(answers: list[dict]) -> list[dict]:
    qs = data.by_id()
    by_case = {a["case_id"]: a for a in answers}
    rows = []
    for q in data.questions("dev"):
        cid = q["case_id"]
        a = by_case.get(cid)
        row = {"schema_version": "finreason.task1.prediction/1.0.0", "dataset_version": q["dataset_version"],
               "case_id": cid, "final_answer": None, "steps": []}
        if a is not None:
            cand = dict(row)
            cand["final_answer"] = {"value": str(a.get("final", "")).strip()}
            if validate_submission([cand], {cid: q}, require_complete=True).valid:
                row = cand
            for s in q["trace_spec"]["slots"]:
                val = str(a.get("slots", {}).get(s["slot_id"], "")).strip()
                trial = dict(row)
                trial["steps"] = row["steps"] + [{"slot_id": s["slot_id"], "value": val}]
                if val and validate_submission([trial], {cid: q}, require_complete=True).valid:
                    row = trial
        rows.append(row)
    return rows


def score(path: str) -> None:
    answers = json.loads(open(path).read())
    rows = to_rows(answers)
    out = data.WORK / "pred_dev_direct.jsonl"
    out.write_text("".join(json.dumps(r) + "\n" for r in rows))
    res = subprocess.run(
        [sys.executable, str(data.TOOLKIT / "scripts/task1_cli.py"), "score-dev",
         "--questions", str(data.SPLIT_FILES["dev"]), "--gold", str(data.GOLD_FILES["dev"]),
         "--manifest", str(data.MANIFEST_FILES["dev"]), "--predictions", str(out)],
        capture_output=True, text=True)
    rep = json.loads(res.stdout)
    print(json.dumps({"scores": rep["scores"], "counts": rep["counts"], "diagnostics": rep["diagnostics"]}, indent=1))


def main(argv: list[str]) -> int:
    if argv[0] == "show":
        show(int(argv[1]))
    elif argv[0] == "show-seen-test":
        show(int(argv[1]), seen_test_batches())
    elif argv[0] == "score":
        score(argv[1])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
