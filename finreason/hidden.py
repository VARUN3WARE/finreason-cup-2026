"""Hidden-structure clusters: compare independent solver variants and finalize selections.

  python -m finreason.hidden compare <cluster_id> [variant ...]   # default: all non-adjudication variants
  python -m finreason.hidden collect <workflow_output.json> ...    # merge decisions -> work/hidden_decisions.json
  python -m finreason.hidden finalize                              # decisions + fallback chain -> work/hidden_selection.json

Variants live at finreason/solvers/zs_hidden/<cluster_id>_<variant>.py.
Synthesis variants: lit, dom, skep, hand. Adjudication variants: adjA, adjB, final.
Review round: red (red-team alternative reading, never a fallback), rev1, rev2, rev3.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from . import data
from .check import predict_row, run_solver
from .zs import clusters, load_module

sys.path.insert(0, str(data.TOOLKIT))
from finreason_task1.contracts import validate_submission  # noqa: E402

SOLVER_DIR = data.ROOT / "finreason/solvers/zs_hidden"
DECISIONS = data.WORK / "hidden_decisions.json"
SELECTION = data.WORK / "hidden_selection.json"
SYNTHESIS = ("lit", "dom", "skep", "hand")
ADJUDICATION = ("adjA", "adjB", "final", "rev1", "rev2", "rev3")


def variant_path(cluster_id: str, variant: str) -> Path:
    return SOLVER_DIR / f"{cluster_id}_{variant}.py"


def available(cluster_id: str, variants: tuple[str, ...] | list[str]) -> list[str]:
    return [v for v in variants if variant_path(cluster_id, v).exists()]


def run_variant(cluster_id: str, variant: str) -> dict[str, dict]:
    """case_id -> prediction row, or {'error': ...}."""
    qs = data.by_id()
    out: dict[str, dict] = {}
    try:
        module = load_module(str(variant_path(cluster_id, variant)))
    except Exception as exc:  # noqa: BLE001
        return {cid: {"error": f"load: {exc!r}"[:300]} for cid in clusters()[cluster_id]["case_ids"]}
    for cid in clusters()[cluster_id]["case_ids"]:
        q = qs[cid]
        try:
            row = predict_row(q, run_solver(module, q))
            v = validate_submission([row], {cid: q}, require_complete=True)
            if not v.valid:
                raise ValueError("; ".join(i.message for i in v.issues))
            out[cid] = row
        except Exception as exc:  # noqa: BLE001
            out[cid] = {"error": repr(exc)[:300]}
    return out


def fields_of(row: dict) -> dict[str, str | None]:
    if "error" in row:
        return {}
    f = {"final": row["final_answer"]["value"] if row["final_answer"] else None}
    f.update({s["slot_id"]: s["value"] for s in row["steps"]})
    return f


def compare(cluster_id: str, variants: list[str] | None = None) -> dict:
    variants = available(cluster_id, variants or list(SYNTHESIS))
    runs = {v: run_variant(cluster_id, v) for v in variants}
    qs = data.by_id()
    report_fields = []
    signature_of = {v: [] for v in variants}
    for cid in clusters()[cluster_id]["case_ids"]:
        q = qs[cid]
        names = ["final"] + [s["slot_id"] for s in q["trace_spec"]["slots"]]
        for name in names:
            values = {v: (fields_of(runs[v][cid]).get(name) if "error" not in runs[v][cid] else "ERROR") for v in variants}
            distinct = set(values.values())
            report_fields.append({"case_id": cid, "field": name, "values": values, "agree": len(distinct) == 1 and "ERROR" not in distinct})
            for v in variants:
                signature_of[v].append(values[v])
    groups: dict[str, list[str]] = {}
    for v in variants:
        groups.setdefault(json.dumps(signature_of[v]), []).append(v)
    errors = {v: {cid: r["error"] for cid, r in runs[v].items() if "error" in r} for v in variants}
    return {
        "cluster": cluster_id,
        "variants": variants,
        "unanimous": bool(variants) and all(f["agree"] for f in report_fields),
        "groups": sorted(groups.values(), key=len, reverse=True),
        "disagreeing_fields": [f for f in report_fields if not f["agree"]],
        "fields": report_fields,
        "errors": {v: e for v, e in errors.items() if e},
    }


def print_compare(rep: dict) -> None:
    print(f"CLUSTER {rep['cluster']} variants={rep['variants']} unanimous={rep['unanimous']}")
    print("agreement groups (variants producing identical outputs on every field):", rep["groups"])
    if rep["errors"]:
        print("errors:", json.dumps(rep["errors"], indent=1))
    for f in rep["fields"]:
        mark = "  " if f["agree"] else "!!"
        print(f"{mark} {f['case_id']} {f['field']}: " + "  ".join(f"{v}={val}" for v, val in f["values"].items()))


COT_ANSWERS = data.WORK / "hidden_cot.json"
SOURCES = data.WORK / "hidden_sources.json"


def collect(output_files: list[str]) -> None:
    """Merge per-cluster decisions from workflow output files into work/hidden_decisions.json.

    Later files override earlier ones, so review rounds can replace synthesis-round decisions.
    """
    decisions = json.loads(DECISIONS.read_text()) if DECISIONS.exists() else {}
    for path in output_files:
        payload = json.loads(Path(path).read_text())
        payload = payload.get("result", payload)
        for d in payload.get("decisions", []):
            decisions[d["cluster"]] = {"variant": d["variant"], "method": d["method"], "source": Path(path).name}
    DECISIONS.write_text(json.dumps(decisions, indent=1, sort_keys=True))
    print(f"{len(decisions)} cluster decisions in {DECISIONS}")


def _cot_row(q: dict, answer: dict) -> dict | None:
    """Turn a no-execution answer into a prediction row; keep only schema-valid fields."""
    row = {"schema_version": "finreason.task1.prediction/1.0.0", "dataset_version": q["dataset_version"],
           "case_id": q["case_id"], "final_answer": {"value": str(answer.get("final", "")).strip()}, "steps": []}
    if not validate_submission([row], {q["case_id"]: q}, require_complete=True).valid:
        return None
    for s in q["trace_spec"]["slots"]:
        value = str(answer.get("slots", {}).get(s["slot_id"], "")).strip()
        trial = dict(row, steps=row["steps"] + [{"slot_id": s["slot_id"], "value": value}])
        if value and validate_submission([trial], {q["case_id"]: q}, require_complete=True).valid:
            row = trial
    return row


def finalize() -> None:
    """Pick one row per hidden question with a fixed fallback chain.

    decided variant -> other variants by agreement-group size -> no-execution answer -> (abstain in predict)
    """
    decisions = json.loads(DECISIONS.read_text()) if DECISIONS.exists() else {}
    cot = {}
    if COT_ANSWERS.exists():
        for c in json.loads(COT_ANSWERS.read_text()):
            for a in c["answers"]:
                cot[a["case_id"]] = a
    qs = data.by_id()
    selection: dict[str, dict] = {}
    sources: dict[str, str] = {}
    for cluster_id, c in clusters().items():
        if c["kind"] != "hidden":
            continue
        order: list[str] = []
        if cluster_id in decisions:
            order.append(decisions[cluster_id]["variant"])
        rep = compare(cluster_id, list(SYNTHESIS))
        for group in rep["groups"]:
            order.extend(group)
        order.extend(SYNTHESIS + ADJUDICATION)
        order = [v for i, v in enumerate(order) if v not in order[:i] and variant_path(cluster_id, v).exists()]
        runs = {v: run_variant(cluster_id, v) for v in order}
        for case_id in c["case_ids"]:
            for v in order:
                if "error" not in runs[v][case_id]:
                    selection[case_id] = runs[v][case_id]
                    sources[case_id] = v if cluster_id in decisions and v == order[0] else f"fallback:{v}"
                    break
            else:
                row = _cot_row(qs[case_id], cot[case_id]) if case_id in cot else None
                if row is not None:
                    selection[case_id] = row
                    sources[case_id] = "fallback:cot"
    SELECTION.write_text(json.dumps(selection, indent=1, sort_keys=True))
    SOURCES.write_text(json.dumps(sources, indent=1, sort_keys=True))
    from collections import Counter

    print(f"selected rows for {len(selection)} hidden questions; sources {dict(Counter(sources.values()))}")


def main(argv: list[str]) -> int:
    if argv and argv[0] == "compare":
        rep = compare(argv[1], [a for a in argv[2:] if not a.startswith("--")] or None)
        if "--json" in argv:
            print(json.dumps(rep, indent=1))
        else:
            print_compare(rep)
        return 0
    if argv and argv[0] == "finalize":
        finalize()
        return 0
    if argv and argv[0] == "collect":
        collect(argv[1:])
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
