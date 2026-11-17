"""Score gold-blind (zero-shot) proxy solvers against gold and against the verified library.

  python -m finreason.eval_zs [solver_dir]   (default finreason/solvers/zs_proxy)

For each seen template with a proxy solver:
  - gold accuracy on its 11 labeled train+dev instances (template-level: all-correct or not)
  - agreement with the verified library on its 4 unlabeled leaderboard/test instances
Writes work/eval_zs.json.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from . import data
from .check import compare, predict_row, run_solver
from .registry import seen_solvers
from .zs import load_module


def evaluate(solver_dir: Path) -> dict:
    members = data.template_members()
    qs = data.by_id()
    lib = seen_solvers()
    per_template = []
    for tid in sorted(members):
        path = solver_dir / f"{data.template_slug(tid)}.py"
        if not path.exists():
            continue
        entry = {"template_id": tid, "difficulty": tid.split(".")[-2], "cases": 0, "fac": 0,
                 "slots": 0, "slots_ok": 0, "errors": 0, "failures": [], "lib_disagree": 0}
        try:
            module = load_module(str(path))
        except Exception as exc:  # noqa: BLE001
            entry["load_error"] = repr(exc)[:300]
            per_template.append(entry)
            continue
        for split in ("train", "dev"):
            golds = data.gold(split)
            for cid in members[tid].get(split, []):
                q = qs[cid]
                entry["cases"] += 1
                nslots = len(q["trace_spec"]["slots"])
                entry["slots"] += nslots
                try:
                    problems = compare(q, predict_row(q, run_solver(module, q)), golds[cid])
                except Exception as exc:  # noqa: BLE001
                    entry["errors"] += 1
                    problems = [f"exception {exc!r}"[:200]] + ["final"] + ["slot"] * nslots
                if not any(p.startswith("final") for p in problems):
                    entry["fac"] += 1
                entry["slots_ok"] += nslots - sum(p.startswith("slot") for p in problems)
                if problems and len(entry["failures"]) < 3:
                    entry["failures"].append({"case_id": cid, "problems": problems[:4]})
        for split in ("lb", "test"):
            for cid in members[tid].get(split, []):
                q = qs[cid]
                try:
                    a = predict_row(q, run_solver(module, q))
                except Exception:  # noqa: BLE001
                    a = None
                b = predict_row(q, run_solver(lib[tid], q))
                if a != b:
                    entry["lib_disagree"] += 1
        entry["all_correct"] = entry["fac"] == entry["cases"] and entry["slots_ok"] == entry["slots"]
        per_template.append(entry)
    return {"templates": per_template}


def summarize(result: dict) -> None:
    ts = result["templates"]
    by_diff = Counter()
    tot = Counter()
    for t in ts:
        d = t["difficulty"]
        tot[d] += 1
        by_diff[d] += t.get("all_correct", False)
    cases = sum(t["cases"] for t in ts)
    fac = sum(t["fac"] for t in ts)
    slots = sum(t["slots"] for t in ts)
    slots_ok = sum(t["slots_ok"] for t in ts)
    print(f"templates evaluated {len(ts)}; template-level all-correct {sum(by_diff.values())}/{len(ts)}")
    for d in ("basic", "intermediate", "advanced"):
        if tot[d]:
            print(f"  {d}: {by_diff[d]}/{tot[d]} = {by_diff[d] / tot[d]:.3f}")
    print(f"case FAC {fac}/{cases} = {fac / max(cases, 1):.4f}; slot acc {slots_ok}/{slots} = {slots_ok / max(slots, 1):.4f}")
    print(f"library disagreements on unlabeled rows: {sum(t['lib_disagree'] for t in ts)} across "
          f"{sum(t['lib_disagree'] > 0 for t in ts)} templates")


def main(argv: list[str]) -> int:
    solver_dir = Path(argv[0]) if argv else data.ROOT / "finreason/solvers/zs_proxy"
    result = evaluate(solver_dir)
    out = data.WORK / f"eval_{solver_dir.name}.json"
    out.write_text(json.dumps(result, indent=1))
    summarize(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
