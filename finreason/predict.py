"""Assemble predictions for a split and package them with the official toolkit.

  python -m finreason.predict <split> [--out work/pred_<split>.jsonl] [--package] [--strict]

--strict refuses to write unless every row comes from its intended source (no abstentions, no fallbacks).

Routing per question:
  1. seen template (structural signature match)  -> verified library solver
  2. hidden cluster                              -> adjudicated zero-shot solver (work/hidden_selection.json)
  3. otherwise / solver error                    -> valid abstention (null final answer, no steps)
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter

from . import data
from .check import predict_row, run_solver
from .registry import seen_solvers

sys.path.insert(0, str(data.TOOLKIT))
from finreason_task1.contracts import validate_submission  # noqa: E402

HIDDEN_SELECTION = data.WORK / "hidden_selection.json"


def abstain(q: dict) -> dict:
    return {
        "schema_version": "finreason.task1.prediction/1.0.0",
        "dataset_version": q["dataset_version"],
        "case_id": q["case_id"],
        "final_answer": None,
        "steps": [],
    }


def hidden_rows() -> dict[str, dict]:
    """case_id -> adjudicated prediction row for hidden-structure questions."""
    if not HIDDEN_SELECTION.exists():
        return {}
    return json.loads(HIDDEN_SELECTION.read_text())


def build(split: str) -> tuple[list[dict], Counter]:
    solvers = seen_solvers()
    hidden = hidden_rows()
    rows, sources = [], Counter()
    for q in data.questions(split):
        cid = q["case_id"]
        tid, _ = data.route(q) if split in ("lb", "test") else (data.labeled_template(cid), 1.0)
        row = None
        if tid is not None and tid in solvers:
            try:
                row = predict_row(q, run_solver(solvers[tid], q))
                if not validate_submission([row], {cid: q}, require_complete=True).valid:
                    row = None
                else:
                    sources["seen_library"] += 1
            except Exception:  # noqa: BLE001
                row = None
        if row is None and cid in hidden:
            row = hidden[cid]
            sources["hidden_synthesis"] += 1
        if row is None:
            row = abstain(q)
            sources["abstain"] += 1
        rows.append(row)
    qmap = {q["case_id"]: q for q in data.questions(split)}
    report = validate_submission(rows, qmap, require_complete=True)
    if not report.valid:
        raise SystemExit(f"invalid submission: {[i.message for i in report.issues][:5]}")
    return rows, sources


def main(argv: list[str]) -> int:
    split = argv[0]
    out = data.WORK / f"pred_{split}.jsonl"
    if "--out" in argv:
        out = data.ROOT / argv[argv.index("--out") + 1]
    rows, sources = build(split)
    if "--strict" in argv:
        expected = {"lb": {"seen_library": 580}, "test": {"seen_library": 580, "hidden_synthesis": 348}}.get(split)
        if expected is not None and dict(sources) != expected:
            raise SystemExit(f"--strict: sources {dict(sources)} != expected {expected}")
        hidden_sources = data.WORK / "hidden_sources.json"
        if split == "test" and hidden_sources.exists():
            fallbacks = Counter(v for v in json.loads(hidden_sources.read_text()).values() if v.startswith("fallback"))
            if fallbacks:
                raise SystemExit(f"--strict: hidden rows still use fallbacks {dict(fallbacks)}")
    with open(out, "w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"{split}: wrote {len(rows)} rows to {out} sources={dict(sources)}")
    if "--package" in argv:
        cli = data.TOOLKIT / "scripts/task1_cli.py"
        qfile = data.SPLIT_FILES[split]
        zip_path = out.with_suffix(".zip")
        if zip_path.exists():
            zip_path.unlink()
        for cmd in (
            ["validate", "--questions", str(qfile), "--predictions", str(out)],
            ["package", "--questions", str(qfile), "--predictions", str(out), "--output", str(zip_path)],
            ["validate-zip", "--questions", str(qfile), "--submission-zip", str(zip_path)],
        ):
            res = subprocess.run([sys.executable, str(cli), *cmd], capture_output=True, text=True)
            print(cmd[0], "->", res.stdout.strip()[:300], res.stderr.strip()[:300])
            if res.returncode != 0:
                return res.returncode
        print("packaged", zip_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
