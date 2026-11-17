"""Derive the remaining hidden-pipeline work from disk state (resumable after any interruption).

  python -m finreason.stage status
  python -m finreason.stage args synth        # workflows/03 items: clusters still missing lens solvers
  python -m finreason.stage args adjudicate   # workflows/03 items (lenses: []): complete but disagreeing, undecided
  python -m finreason.stage args redteam      # workflows/06 items: decided clusters not yet red-teamed/reviewed
  python -m finreason.stage args fable        # workflows/07 clusters: missing a Fable no-code answer
  python -m finreason.stage decide-unanimous  # record decisions for complete, unanimous, undecided clusters
  python -m finreason.stage merge-fable <workflows/07 output.json>
"""

from __future__ import annotations

import json
import sys

from . import data
from .hidden import DECISIONS, SYNTHESIS, available, compare
from .zs import clusters

REVIEWED = {"redteam_cleared", "challenge_rejected", "challenge_rejected_by_arbiter", "changed_after_review"}
FABLE = data.WORK / "hidden_cot_fable.json"


def _decisions() -> dict:
    return json.loads(DECISIONS.read_text()) if DECISIONS.exists() else {}


def _hidden_ids() -> list[str]:
    return [cid for cid, c in clusters().items() if c["kind"] == "hidden"]


def state() -> dict:
    dec = _decisions()
    out = {"missing_lenses": {}, "complete_unanimous": [], "complete_disagree": []}
    for cid in _hidden_ids():
        missing = [v for v in SYNTHESIS if v not in available(cid, list(SYNTHESIS))]
        if missing:
            out["missing_lenses"][cid] = missing
            continue
        rep = compare(cid)
        key = "complete_unanimous" if rep["unanimous"] and not rep["errors"] else "complete_disagree"
        out[key].append(cid)
    out["decided"] = sorted(dec)
    out["reviewed"] = sorted(c for c, d in dec.items() if d.get("method") in REVIEWED)
    fable_ids = set()
    if FABLE.exists():
        for c in json.loads(FABLE.read_text()):
            fable_ids.update(a["case_id"] for a in c["answers"])
    out["fable_missing"] = [cid for cid in _hidden_ids()
                            if not set(clusters()[cid]["case_ids"]) <= fable_ids]
    return out


def _cot_note(cid: str) -> tuple[str, int]:
    notes, n = [], 0
    for label, path in (("Opus", data.WORK / "crosscheck_report.json"),
                        ("Fable", data.WORK / "crosscheck_hidden_cot_fable.json")):
        if not path.exists():
            continue
        rep = json.loads(path.read_text()).get(cid)
        if not rep:
            continue
        dis = [f for f in rep["fields"] if f["match"] is False]
        if dis:
            n += len(dis)
            notes.append(f"A no-code pass on model {label} DISAGREED with the current solver on: " + "; ".join(
                f"{f['case_id']} {f['field']}: program={f['program']} no-code={f['cot']}" for f in dis) + ".")
        elif rep["agree"]:
            notes.append(f"A no-code pass on model {label} agreed on all {rep['agree']} comparable fields.")
    if not notes:
        notes.append("No no-code comparison available.")
    return " ".join(notes) + " (Agreement within one model family is not proof.)", n


def main(argv: list[str]) -> int:
    st = state()
    dec = _decisions()
    if argv[:1] == ["status"]:
        print(json.dumps({k: (v if isinstance(v, dict) else len(v)) for k, v in st.items()}, indent=1))
        print("complete_disagree:", st["complete_disagree"])
        print("decided but not reviewed:", [c for c in st["decided"] if c not in st["reviewed"]])
        return 0
    if argv[:1] == ["merge-fable"]:
        # Merge a workflows/07 output file into work/hidden_cot_fable.json (newer answers win per case).
        by_case = {}
        if FABLE.exists():
            for c in json.loads(FABLE.read_text()):
                for a in c["answers"]:
                    by_case[a["case_id"]] = a
        payload = json.loads(open(argv[1]).read())
        payload = payload.get("result", payload)
        import difflib

        for c in payload["clusters"]:
            expected = clusters()[c["cluster"]]["case_ids"]
            unmatched = [x for x in expected if x not in {a["case_id"] for a in c["answers"]}]
            for a in c["answers"]:
                if a["case_id"] not in expected and unmatched:
                    # Agents occasionally mistype an id; repair only near-identical ids within the same cluster.
                    best = max(unmatched, key=lambda x: difflib.SequenceMatcher(None, x, a["case_id"]).ratio())
                    if difflib.SequenceMatcher(None, best, a["case_id"]).ratio() >= 0.9:
                        print(f"repaired case id {a['case_id']} -> {best}")
                        a = dict(a, case_id=best)
                        unmatched.remove(best)
                by_case[a["case_id"]] = a
        hidden_ids = {x for cid in _hidden_ids() for x in clusters()[cid]["case_ids"]}
        by_case = {k: v for k, v in by_case.items() if k in hidden_ids}
        FABLE.write_text(json.dumps([{"answers": list(by_case.values())}], indent=1))
        print(f"Fable answers for {len(by_case)} hidden questions")
        return 0
    if argv[:1] == ["decide-unanimous"]:
        added = [c for c in st["complete_unanimous"] if c not in dec]
        for cid in added:
            dec[cid] = {"variant": "lit", "method": "unanimous", "source": "offline_compare"}
        DECISIONS.write_text(json.dumps(dec, indent=1, sort_keys=True))
        print("recorded unanimous decisions:", added)
        return 0
    if argv[:1] == ["args"]:
        kind = argv[1]
        if kind == "synth":
            items = [{"cid": c, "lenses": m} for c, m in st["missing_lenses"].items()]
            print(json.dumps({"synthesize_only": True, "items": items}))
        elif kind == "adjudicate":
            items = [{"cid": c, "lenses": []} for c in st["complete_disagree"] if c not in dec]
            print(json.dumps({"items": items}))
        elif kind == "redteam":
            items = []
            for cid in st["decided"]:
                if cid in st["reviewed"]:
                    continue
                note, n = _cot_note(cid)
                items.append({"cid": cid, "variant": dec[cid]["variant"], "cot": note, "cot_disagreements": n})
            print(json.dumps({"items": items}))
        elif kind == "fable":
            print(json.dumps({"clusters": st["fable_missing"]}))
        else:
            print(__doc__)
            return 2
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
