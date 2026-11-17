"""Stage-wise ablation of the hidden-structure pipeline, from disk state only (no labels, no LLM calls).

  python -m finreason.ablation        # prints a summary and writes work/ablation.json

Test labels are private, so nothing here measures accuracy. Every configuration is compared with the outputs
we submitted (work/hidden_selection.json): how many final answers and how many checkpoint values would differ
if the pipeline had stopped at that stage. The script also reports

  * field agreement of each lens with the pre-jury decisions and with the submitted (post-jury) outputs;
  * on which of a cluster's three instances each lens dispute is visible (what one instance would have shown);
  * the metamorphic diagnostic re-run with a single instance per structure (every number perturbed, because
    constants cannot be told apart from parameters without sibling instances);
  * logged token usage per stage (work/costs.json).
"""

from __future__ import annotations

import json
from collections import Counter

from . import data
from .hidden import DECISIONS, SELECTION, SYNTHESIS, compare, fields_of, run_variant, variant_path
from .metamorphic import compare_versions
from .zs import clusters, load_module

LENS_MODEL = {"lit": "Opus", "dom": "Sonnet", "skep": "Fable", "hand": "Opus"}
# Decided variant of each disputed cluster after adjudication and blind review, before the jury.
PRE_JURY = {"h031": "adjA", "h040": "adjA", "h058": "adjA", "h091": "final"}
COST_GROUPS = {
    "seen_library_and_gold_blind_proxy": ["library_and_zeroshot_proxy"],
    "seen_dev_no_execution_baseline": ["direct_cot_dev"],
    "seen_test_no_execution_check": ["seen_test_cot_crosscheck"],
    "hidden_synthesis_logged": ["hidden_pilot_h001_h003", "hidden_synthesis_final_17_clusters",
                                "hidden_synthesis_resume_wf_dff3971f"],
    "hidden_adjudication_h091": ["adjudication_h091"],
    "hidden_no_execution_opus": ["hidden_cot_crosscheck"],
    "hidden_no_execution_fable": ["hidden_cot_fable_first_51", "hidden_cot_fable_rest_66"],
    "hidden_no_execution_sonnet": ["hidden_cot_sonnet_116"],
    "hidden_red_team": ["redteam_batch1_35_clusters", "redteam_batch2_51_clusters", "redteam_batch3_10_clusters",
                        "redteam_batch4_final_16"],
    "hidden_blind_review": ["review_flagged_4_clusters", "review_h091"],
    "hidden_jury": ["hidden_jury_7_clusters"],
}


def main() -> int:
    decisions = json.loads(DECISIONS.read_text())
    submitted = json.loads(SELECTION.read_text())
    cl = clusters()
    hidden = [cid for cid, c in cl.items() if c["kind"] == "hidden"]
    qs = data.by_id()
    cache: dict[tuple[str, str], dict] = {}

    def run(cid: str, variant: str) -> dict:
        if (cid, variant) not in cache:
            cache[(cid, variant)] = run_variant(cid, variant)
        return cache[(cid, variant)]

    def against(reference, candidate) -> dict:
        """Count fields where candidate(cid, case_id) differs from reference(cid, case_id)."""
        out = {"finals": 0, "final_diff": 0, "checkpoints": 0, "checkpoint_diff": 0, "clusters": set()}
        for cid in hidden:
            for case_id in cl[cid]["case_ids"]:
                ref, mine = reference(cid, case_id), candidate(cid, case_id)
                for name, value in ref.items():
                    kind = "final" if name == "final" else "checkpoint"
                    out[kind + "s"] += 1
                    if mine.get(name) != value:
                        out[kind + "_diff"] += 1
                        out["clusters"].add(cid)
        out["clusters"] = sorted(out["clusters"])
        return out

    def sub(cid, case_id):
        return fields_of(submitted[case_id])

    def variant(pick):
        return lambda cid, case_id: fields_of(run(cid, pick(cid))[case_id])

    def plurality(cid, case_id):
        """Per-field plurality over the four lenses; ties go to the literal lens."""
        rows = [fields_of(run(cid, v)[case_id]) for v in SYNTHESIS]
        out = {}
        for name in rows[0]:
            values = [r.get(name) for r in rows]
            counts = Counter(values)
            best = max(counts.values())
            out[name] = values[0] if counts[values[0]] == best else next(v for v in values if counts[v] == best)
        return out

    def pre_jury(cid, case_id):
        return fields_of(run(cid, PRE_JURY.get(cid, "lit"))[case_id])

    report: dict = {"clusters": len(hidden), "questions": sum(len(cl[c]["case_ids"]) for c in hidden)}
    stages = {
        "literal_lens_only": variant(lambda c: "lit"),
        "hand_solve_lens_only": variant(lambda c: "hand"),
        "finance_model_lens_only": variant(lambda c: "dom"),
        "ambiguity_lens_only": variant(lambda c: "skep"),
        "four_lenses_plurality": plurality,
        "four_lenses_adjudicated": pre_jury,
        "after_red_team_and_blind_review": pre_jury,  # review changed no answer
        "after_jury_submitted": variant(lambda c: decisions[c]["variant"]),
    }
    report["vs_submitted"] = {name: against(sub, cand) for name, cand in stages.items()}
    report["lens_agreement"] = {}
    for v in SYNTHESIS:
        post, pre = against(sub, variant(lambda c, v=v: v)), against(pre_jury, variant(lambda c, v=v: v))
        total = post["finals"] + post["checkpoints"]
        report["lens_agreement"][v] = {
            "model": LENS_MODEL[v],
            "pre_jury": total - pre["final_diff"] - pre["checkpoint_diff"],
            "submitted": total - post["final_diff"] - post["checkpoint_diff"],
            "total": total,
        }

    # What a single instance would have shown: on which instances do the lenses disagree?
    visible = {}
    for cid in PRE_JURY:
        rep = compare(cid, list(SYNTHESIS))
        any_field = sorted({f["case_id"] for f in rep["disagreeing_fields"]})
        final_only = sorted({f["case_id"] for f in rep["disagreeing_fields"] if f["field"] == "final"})
        visible[cid] = {"instances": len(cl[cid]["case_ids"]), "instances_showing_any_dispute": len(any_field),
                        "instances_showing_final_answer_dispute": len(final_only),
                        "disputed_fields": len(rep["disagreeing_fields"]), "groups": rep["groups"]}
    report["dispute_visibility_per_instance"] = visible

    # Metamorphic diagnostic with one instance per structure (no siblings: every number is perturbed).
    single = {"trials": Counter(), "flagged": {}}
    for cid in hidden:
        mods = {v: load_module(str(variant_path(cid, v))) for v in SYNTHESIS if variant_path(cid, v).exists()}
        hits = []
        for case_id in cl[cid]["case_ids"]:
            r = compare_versions(mods, [qs[case_id]], 10, 0, siblings=[qs[case_id]])
            single["trials"].update(r["stats"])
            hits.append(r["stats"].get("disagree", 0) > 0)
        if any(hits):
            single["flagged"][cid] = hits
    single["trials"] = dict(single["trials"])
    report["single_instance_perturbation"] = single

    costs = json.loads((data.WORK / "costs.json").read_text())
    report["logged_tokens"] = {
        name: {"agents": sum(costs[k]["agents"] for k in keys),
               "tokens": sum(costs[k]["subagent_tokens"] for k in keys)} for name, keys in COST_GROUPS.items()}
    report["logged_tokens"]["total"] = {
        "agents": sum(v["agents"] for v in report["logged_tokens"].values()),
        "tokens": sum(v["tokens"] for v in report["logged_tokens"].values())}

    (data.WORK / "ablation.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
