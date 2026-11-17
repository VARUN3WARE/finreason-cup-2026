"""Zero-shot (gold-free) program synthesis tooling.

A *cluster* is a group of questions sharing one structure. Agents see only the
question texts and result specifications of a cluster -- never gold values.

  python -m finreason.zs list [proxy|hidden]
  python -m finreason.zs show <cluster_id>
  python -m finreason.zs run <cluster_id> <module_path.py>

Proxy clusters (id = seen template id) contain the dev + leaderboard instances
of a seen template, so the gold-free pipeline can be measured against gold.
Hidden clusters (id = hNNN) are test questions whose structure is unseen.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from functools import lru_cache
from pathlib import Path

from . import data
from .check import predict_row, run_solver

sys.path.insert(0, str(data.TOOLKIT))
from finreason_task1.contracts import validate_submission  # noqa: E402

CLUSTERS = data.WORK / "clusters.json"


@lru_cache(maxsize=None)
def clusters() -> dict[str, dict]:
    if CLUSTERS.exists():
        return json.loads(CLUSTERS.read_text())
    out: dict[str, dict] = {}
    members = data.template_members()
    for tid in sorted(members):
        ids = members[tid].get("dev", []) + members[tid].get("lb", [])
        out[tid] = {"kind": "proxy", "case_ids": ids}
    groups: dict[str, list[str]] = {}
    for q in data.questions("test"):
        tid, _ = data.route(q)
        if tid is None:
            groups.setdefault(data.signature(q), []).append(q["case_id"])
    for n, ids in enumerate(sorted(groups.values(), key=lambda v: min(v)), start=1):
        out[f"h{n:03d}"] = {"kind": "hidden", "case_ids": sorted(ids)}
    CLUSTERS.write_text(json.dumps(out, indent=1))
    return out


def show(cluster_id: str) -> None:
    c = clusters()[cluster_id]
    qs = data.by_id()
    first = qs[c["case_ids"][0]]
    print(f"CLUSTER {cluster_id} ({len(c['case_ids'])} instances)")
    print("ANSWER SPEC:", json.dumps(first["answer_spec"]))
    print(data.answer_format(first))
    for s in first["trace_spec"]["slots"]:
        print(f"SLOT {s['slot_id']} (position {s['position']}): {s['description']}  spec={json.dumps(s['result_spec'])}")
    for cid in c["case_ids"]:
        print(f"\n--- instance {cid}")
        print(data.body(qs[cid]))


def load_module(path: str):
    p = Path(path).resolve()
    spec = importlib.util.spec_from_file_location(f"zs_{p.stem}", p)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(cluster_id: str, path: str, case_ids: list[str] | None = None, verbose: bool = True) -> dict:
    module = load_module(path)
    qs = data.by_id()
    ids = case_ids or clusters()[cluster_id]["case_ids"]
    out = {}
    for cid in ids:
        q = qs[cid]
        try:
            row = predict_row(q, run_solver(module, q))
            v = validate_submission([row], {cid: q}, require_complete=True)
            if not v.valid:
                raise ValueError("; ".join(i.message for i in v.issues))
            out[cid] = {
                "final": row["final_answer"]["value"] if row["final_answer"] else None,
                "slots": {s["slot_id"]: s["value"] for s in row["steps"]},
            }
        except Exception as exc:  # noqa: BLE001
            out[cid] = {"error": repr(exc)[:400]}
    if verbose:
        print(json.dumps(out, indent=1))
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "list":
        kind = argv[1] if len(argv) > 1 else None
        for cid, c in clusters().items():
            if kind is None or c["kind"] == kind:
                print(cid, c["kind"], len(c["case_ids"]))
        return 0
    if argv[0] == "show":
        show(argv[1])
        return 0
    if argv[0] == "run":
        res = run(argv[1], argv[2])
        return 1 if any("error" in r for r in res.values()) else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
