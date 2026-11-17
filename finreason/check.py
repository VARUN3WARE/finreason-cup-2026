"""Verify seen-template solvers against gold and smoke-run them on unlabeled rows.

Usage:
  python -m finreason.check show <template_id>         # print labeled examples + gold
  python -m finreason.check one <template_id>          # verify one solver
  python -m finreason.check all [--quiet]              # verify every solver, write work/check_report.json
"""

from __future__ import annotations

import json
import sys
import traceback
from typing import Any

from . import data
from .fmt import render

sys.path.insert(0, str(data.TOOLKIT))
from finreason_task1.contracts import validate_submission  # noqa: E402
from finreason_task1.scoring import value_matches  # noqa: E402


def predict_row(question: dict, result: dict) -> dict:
    steps = []
    for slot in question["trace_spec"]["slots"]:
        if slot["slot_id"] in result.get("slots", {}):
            steps.append(
                {
                    "slot_id": slot["slot_id"],
                    "value": render(result["slots"][slot["slot_id"]], slot["result_spec"]),
                }
            )
    final = result.get("final")
    return {
        "schema_version": "finreason.task1.prediction/1.0.0",
        "dataset_version": question["dataset_version"],
        "case_id": question["case_id"],
        "final_answer": None if final is None else {"value": render(final, question["answer_spec"])},
        "steps": steps,
    }


def run_solver(module: Any, question: dict) -> dict:
    result = module.solve(data.body(question), question)
    if not isinstance(result, dict) or "final" not in result:
        raise TypeError("solve() must return {'final': ..., 'slots': {...}}")
    expected = {s["slot_id"] for s in question["trace_spec"]["slots"]}
    got = set(result.get("slots", {}))
    if got != expected:
        raise KeyError(f"slot ids {sorted(got)} != expected {sorted(expected)}")
    return result


def compare(question: dict, row: dict, gold_row: dict) -> list[str]:
    problems = []
    final_gold = gold_row["final_value"]
    final = row["final_answer"]["value"] if row["final_answer"] else None
    if final is None or not value_matches(final, final_gold, question["answer_spec"]):
        problems.append(f"final: got {final} want {final_gold}")
    steps = {s["slot_id"]: s["value"] for s in row["steps"]}
    for slot in question["trace_spec"]["slots"]:
        sid = slot["slot_id"]
        want = gold_row["slot_values"][sid]
        got = steps.get(sid)
        if got is None or not value_matches(got, want, slot["result_spec"]):
            problems.append(f"slot {sid}: got {got} want {want}")
    return problems


def check_template(template_id: str, module: Any | None = None, verbose: bool = True) -> dict:
    from .registry import load_one

    if module is None:
        module = load_one(template_id)
    members = data.template_members().get(template_id, {})
    qs = data.by_id()
    report = {"template_id": template_id, "labeled": 0, "passed": 0, "failures": [], "smoke_errors": []}
    for split in ("train", "dev"):
        golds = data.gold(split)
        for cid in members.get(split, []):
            q = qs[cid]
            report["labeled"] += 1
            try:
                row = predict_row(q, run_solver(module, q))
                v = validate_submission([row], {cid: q}, require_complete=True)
                if not v.valid:
                    raise ValueError("; ".join(i.message for i in v.issues))
                problems = compare(q, row, golds[cid])
            except Exception as exc:  # noqa: BLE001
                problems = [f"exception: {exc!r}"]
                if verbose:
                    traceback.print_exc()
            if problems:
                report["failures"].append({"split": split, "case_id": cid, "problems": problems})
            else:
                report["passed"] += 1
    for split in ("lb", "test"):
        for cid in members.get(split, []):
            q = qs[cid]
            try:
                row = predict_row(q, run_solver(module, q))
                v = validate_submission([row], {cid: q}, require_complete=True)
                if not v.valid:
                    raise ValueError("; ".join(i.message for i in v.issues))
            except Exception as exc:  # noqa: BLE001
                report["smoke_errors"].append({"split": split, "case_id": cid, "error": repr(exc)[:300]})
    report["unlabeled_rows"] = sum(len(members.get(s, [])) for s in ("lb", "test"))
    report["ok"] = report["passed"] == report["labeled"] and not report["smoke_errors"]
    if verbose:
        print(json.dumps(report, indent=1))
    return report


def show(template_id: str, limit: int = 4) -> None:
    members = data.template_members().get(template_id, {})
    qs = data.by_id()
    print(f"TEMPLATE {template_id}  slug={data.template_slug(template_id)}")
    print("counts:", {k: len(v) for k, v in members.items()})
    shown = 0
    for split in ("train", "dev"):
        for cid in members.get(split, []):
            if shown >= limit:
                break
            q = qs[cid]
            g = data.gold(split)[cid]
            print(f"\n--- {split} {cid}")
            print(data.body(q))
            print("ANSWER SPEC:", json.dumps(q["answer_spec"]))
            for s in q["trace_spec"]["slots"]:
                print(f"SLOT {s['slot_id']}: {s['description']} {json.dumps(s['result_spec'])}")
            print("GOLD final:", g["final_value"], "slots:", json.dumps(g["slot_values"]))
            shown += 1
    for cid in members.get("lb", [])[:2]:
        print(f"\n--- unlabeled lb {cid}")
        print(data.body(qs[cid]))


def main(argv: list[str]) -> int:
    cmd = argv[0]
    if cmd == "show":
        show(argv[1], int(argv[2]) if len(argv) > 2 else 4)
        return 0
    if cmd == "one":
        rep = check_template(argv[1])
        return 0 if rep["ok"] else 1
    if cmd == "all":
        from .registry import seen_solvers

        quiet = "--quiet" in argv
        solvers = seen_solvers()
        all_templates = sorted(data.template_members())
        reports = []
        for tid in all_templates:
            if tid not in solvers:
                reports.append({"template_id": tid, "ok": False, "missing": True})
                continue
            reports.append(check_template(tid, solvers[tid], verbose=False))
        ok = sum(r["ok"] for r in reports)
        missing = sum(bool(r.get("missing")) for r in reports)
        labeled = sum(r.get("labeled", 0) for r in reports)
        passed = sum(r.get("passed", 0) for r in reports)
        (data.WORK / "check_report.json").write_text(json.dumps(reports, indent=1))
        print(f"templates ok {ok}/{len(reports)} missing {missing}; labeled instances passed {passed}/{labeled}")
        if not quiet:
            for r in reports:
                if not r["ok"] and not r.get("missing"):
                    print(r["template_id"], r.get("failures", [])[:2], r.get("smoke_errors", [])[:2])
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
