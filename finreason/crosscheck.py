"""Cross-check program outputs for hidden clusters against independent no-execution reasoning.

  python -m finreason.crosscheck [--cot work/hidden_cot.json]   (other --cot files write work/crosscheck_<stem>.json)

Compares every field (final + slots) of the selected program row (work/hidden_selection.json) with the
chain-of-thought answer using the official value matcher, and writes work/crosscheck_report.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from . import data
from .hidden import SELECTION, SOURCES
from .zs import clusters

sys.path.insert(0, str(data.TOOLKIT))
from finreason_task1.scoring import value_matches  # noqa: E402

REPORT = data.WORK / "crosscheck_report.json"


def _match(a: str | None, b: str | None, spec: dict) -> bool | None:
    if a is None or b is None or a == "":
        return None
    try:
        return value_matches(a, b, spec)
    except Exception:  # noqa: BLE001
        return False


def crosscheck(cot_path: str) -> dict:
    selection = json.loads(SELECTION.read_text())
    sources = json.loads(SOURCES.read_text()) if SOURCES.exists() else {}
    cot = {}
    for c in json.loads(open(cot_path).read()):
        for a in c["answers"]:
            cot[a["case_id"]] = a
    qs = data.by_id()
    report = {}
    for cid, c in clusters().items():
        if c["kind"] != "hidden":
            continue
        fields = []
        for case_id in c["case_ids"]:
            q = qs[case_id]
            # Rows that themselves came from the CoT fallback cannot cross-check anything.
            row = None if sources.get(case_id) == "fallback:cot" else selection.get(case_id)
            ans = cot.get(case_id, {})
            prog_final = row["final_answer"]["value"] if row and row["final_answer"] else None
            fields.append({"case_id": case_id, "field": "final", "program": prog_final,
                           "cot": ans.get("final"), "match": _match(ans.get("final"), prog_final, q["answer_spec"])})
            steps = {s["slot_id"]: s["value"] for s in (row or {}).get("steps", [])}
            for s in q["trace_spec"]["slots"]:
                cv = ans.get("slots", {}).get(s["slot_id"])
                fields.append({"case_id": case_id, "field": s["slot_id"], "program": steps.get(s["slot_id"]),
                               "cot": cv, "match": _match(cv, steps.get(s["slot_id"]), s["result_spec"])})
        report[cid] = {
            "fields": fields,
            "n": len(fields),
            "agree": sum(f["match"] is True for f in fields),
            "disagree": sum(f["match"] is False for f in fields),
            "missing": sum(f["match"] is None for f in fields),
            "cot_interpretation": [cot.get(i, {}).get("interpretation", "") for i in c["case_ids"]],
        }
    out = REPORT if Path(cot_path).name == "hidden_cot.json" else data.WORK / f"crosscheck_{Path(cot_path).stem}.json"
    out.write_text(json.dumps(report, indent=1))
    return report


def main(argv: list[str]) -> int:
    cot_path = str(data.WORK / "hidden_cot.json")
    if "--cot" in argv:
        cot_path = argv[argv.index("--cot") + 1]
    rep = crosscheck(cot_path)
    n = sum(r["n"] for r in rep.values())
    agree = sum(r["agree"] for r in rep.values())
    dis = sum(r["disagree"] for r in rep.values())
    flagged = [c for c, r in rep.items() if r["disagree"] or r["missing"]]
    print(f"fields {n}: agree {agree}, disagree {dis}, missing {n - agree - dis}; "
          f"clusters fully agreeing {len(rep) - len(flagged)}/{len(rep)}")
    print("flagged:", " ".join(flagged))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
