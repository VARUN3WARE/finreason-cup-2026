"""Compute the hidden-stratum statistics reported in the paper, from disk state only.

  python -m finreason.paper_stats     # prints a summary and writes work/paper_stats.json
"""

from __future__ import annotations

import json
from collections import Counter

from . import data
from .hidden import DECISIONS, SELECTION, SYNTHESIS, compare, fields_of, run_variant
from .zs import clusters

LENS_MODEL = {"lit": "Opus", "dom": "Sonnet", "skep": "Fable", "hand": "Opus"}


def main() -> int:
    dec = json.loads(DECISIONS.read_text())
    selection = json.loads(SELECTION.read_text())
    hidden = [cid for cid, c in clusters().items() if c["kind"] == "hidden"]
    out: dict = {"clusters": len(hidden), "questions": sum(len(clusters()[c]["case_ids"]) for c in hidden)}

    unanimous, disputes = [], {}
    lens_agree = Counter()
    lens_total = Counter()
    for cid in hidden:
        rep = compare(cid, list(SYNTHESIS))
        if rep["unanimous"] and not rep["errors"]:
            unanimous.append(cid)
        else:
            disputes[cid] = {"groups": rep["groups"], "disagreeing_fields": len(rep["disagreeing_fields"])}
        for v in SYNTHESIS:
            runs = run_variant(cid, v)
            for case_id in clusters()[cid]["case_ids"]:
                final = fields_of(selection[case_id]) if case_id in selection else {}
                mine = fields_of(runs[case_id])
                for name, value in final.items():
                    lens_total[v] += 1
                    lens_agree[v] += mine.get(name) == value
    out["synthesis_unanimous"] = len(unanimous)
    out["disputed"] = disputes
    out["lens_field_agreement_with_final"] = {
        v: {"model": LENS_MODEL[v], "agree": lens_agree[v], "total": lens_total[v],
            "rate": round(lens_agree[v] / max(lens_total[v], 1), 4)} for v in SYNTHESIS}

    for label, path in (("opus", data.WORK / "crosscheck_report.json"),
                        ("fable", data.WORK / "crosscheck_hidden_cot_fable.json")):
        rep = json.loads(path.read_text())
        out[f"cot_{label}"] = {
            "fields": sum(r["n"] for r in rep.values()),
            "agree": sum(r["agree"] for r in rep.values()),
            "disagree": sum(r["disagree"] for r in rep.values()),
            "clusters_with_disagreement": sorted(c for c, r in rep.items() if r["disagree"]),
        }
    out["decision_methods"] = dict(Counter(d["method"] for d in dec.values()))
    out["final_variants"] = dict(Counter(d["variant"] for d in dec.values()))

    meta = data.WORK / "metamorphic_report.json"
    if meta.exists():
        m = json.loads(meta.read_text())
        tot = Counter()
        latent = []
        for cid, r in m["hidden"].items():
            tot.update(r["stats"])
            if r["stats"].get("disagree"):
                latent.append(cid)
        out["metamorphic_hidden"] = {"trials": tot["trials"], "agree": tot["agree"], "disagree": tot["disagree"],
                                     "failed": tot["some_version_failed"], "clusters_with_latent_disagreement": latent}
    ties = data.WORK / "rounding_tie_analysis.json"
    if ties.exists():
        out["rounding_ties"] = json.loads(ties.read_text())

    (data.WORK / "paper_stats.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k not in ("disputed",)}, indent=1))
    print("disputed clusters:", {c: d["groups"] for c, d in disputes.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
