"""Metamorphic robustness test: perturb question numbers, compare independent solver versions.

  python -m finreason.metamorphic [--k 10] [--seed 0]

For every question we create K perturbed copies (same wording, nearby values for the numbers that vary across
instances of the same structure; structural constants that are identical in every instance stay fixed) and run each independent solver
version on them. Versions that implement the same rule must keep agreeing; disagreement on perturbed inputs reveals
*latent* interpretation differences that the real instances do not exercise.

  seen:   verified library  vs  gold-blind proxy solver      (580 seen test questions)
  hidden: lit / dom / skep / hand lens solvers               (348 hidden test questions)

Writes work/metamorphic_report.json. No gold is used.
"""

from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter
from fractions import Fraction

from . import data
from .check import predict_row, run_solver
from .hidden import SYNTHESIS, available, variant_path
from .registry import seen_solvers
from .zs import clusters, load_module

TOKEN = re.compile(r"(?<![\w.])(-?)(\d+)(?:\.(\d+))?(?:/(\d+))?(?![\w])")


def _perturb_token(m: re.Match, rng: random.Random) -> str:
    sign, whole, frac, den = m.group(1), m.group(2), m.group(3), m.group(4)
    text = m.group(0)
    if den is not None:  # rational a/b: perturb numerator only
        num = int(whole)
        new = max(1, round(num * rng.uniform(0.85, 1.15)))
        return f"{sign}{new}/{den}"
    if frac is None:
        value = int(whole)
        if value <= 12:  # small integers are usually counts, periods, places or structural constants
            return text
        new = max(1, round(value * rng.uniform(0.85, 1.15)))
        return f"{sign}{new}"
    value = Fraction(f"{whole}.{frac}")
    places = len(frac)
    if 0 < value < 1:  # probabilities / rates: stay inside (0, 1)
        new = value * Fraction(rng.uniform(0.85, 1.15)).limit_denominator(10**6)
        new = min(new, Fraction(99, 100))
    else:
        new = value * Fraction(rng.uniform(0.85, 1.15)).limit_denominator(10**6)
    scaled = round(new * 10**places)
    if scaled == 0:
        return text
    whole_part, frac_part = divmod(scaled, 10**places)
    return f"{sign}{whole_part}.{frac_part:0{places}d}"


def varying_positions(question: dict, siblings: list[dict]) -> set[int] | None:
    """Indices of number tokens whose value differs across instances of the same structure.

    Numbers identical in every instance are structural constants (day counts, 100, thresholds fixed by the
    template) and must stay fixed. Returns None when the siblings' token layouts differ (perturb everything).
    """
    layouts = [[m.group(0) for m in TOKEN.finditer(data.body(q))] for q in siblings]
    if len(siblings) < 2 or len({len(t) for t in layouts}) != 1:
        return None
    return {i for i in range(len(layouts[0])) if len({t[i] for t in layouts}) > 1}


def perturb(question: dict, rng: random.Random, positions: set[int] | None = None) -> dict:
    body = data.body(question)
    counter = iter(range(10**6))

    def sub(m: re.Match) -> str:
        i = next(counter)
        if positions is not None and i not in positions:
            return m.group(0)
        return _perturb_token(m, rng)

    new_body = TOKEN.sub(sub, body)
    q = dict(question)
    q["question"] = new_body + data.ANSWER_FORMAT_MARKER + question["question"].split(data.ANSWER_FORMAT_MARKER, 1)[1]
    return q


def _outputs(module, q: dict) -> str | None:
    try:
        row = predict_row(q, run_solver(module, q))
        return json.dumps([row["final_answer"], row["steps"]], sort_keys=True)
    except Exception:  # noqa: BLE001
        return None


def compare_versions(modules: dict[str, object], questions: list[dict], k: int, seed: int,
                     siblings: list[dict] | None = None) -> dict:
    stats = Counter()
    examples = []
    for q in questions:
        positions = varying_positions(q, siblings or questions)
        stats["layout_fallback"] += positions is None
        for i in range(k):
            rng = random.Random(f"{seed}:{q['case_id']}:{i}")
            pq = perturb(q, rng, positions)
            outs = {name: _outputs(m, pq) for name, m in modules.items()}
            stats["trials"] += 1
            ok = [v for v in outs.values() if v is not None]
            if len(ok) < len(outs):
                stats["some_version_failed"] += 1
                if not ok:
                    stats["all_failed"] += 1
                continue
            if len(set(ok)) == 1:
                stats["agree"] += 1
            else:
                stats["disagree"] += 1
                if len(examples) < 2:
                    examples.append({"case_id": q["case_id"], "trial": i,
                                     "groups": [[n for n, v in outs.items() if v == val] for val in set(ok)]})
    return {"stats": dict(stats), "examples": examples}


def main(argv: list[str]) -> int:
    k = int(argv[argv.index("--k") + 1]) if "--k" in argv else 10
    seed = int(argv[argv.index("--seed") + 1]) if "--seed" in argv else 0
    qs = data.by_id()
    report = {"k": k, "seed": seed, "seen": {}, "hidden": {}}

    lib = seen_solvers()
    for tid, members in sorted(data.template_members().items()):
        proxy = data.ROOT / "finreason/solvers/zs_proxy" / f"{data.template_slug(tid)}.py"
        if not proxy.exists():
            continue
        mods = {"library": lib[tid], "proxy": load_module(str(proxy))}
        siblings = [qs[c] for split in ("train", "dev", "lb", "test") for c in members.get(split, [])]
        report["seen"][tid] = compare_versions(mods, [qs[c] for c in members.get("test", [])], k, seed, siblings)

    for cid, c in clusters().items():
        if c["kind"] != "hidden":
            continue
        names = available(cid, list(SYNTHESIS))
        if len(names) < 2:
            continue
        mods = {n: load_module(str(variant_path(cid, n))) for n in names}
        report["hidden"][cid] = compare_versions(mods, [qs[x] for x in c["case_ids"]], k, seed)

    (data.WORK / "metamorphic_report.json").write_text(json.dumps(report, indent=1))
    for part in ("seen", "hidden"):
        tot = Counter()
        latent = 0
        for r in report[part].values():
            tot.update(r["stats"])
            latent += r["stats"].get("disagree", 0) > 0
        valid = tot["agree"] + tot["disagree"]
        print(f"{part}: units {len(report[part])}, trials {tot['trials']}, all versions ran {valid}, "
              f"agree {tot['agree']} ({tot['agree'] / max(valid, 1):.3%}), disagree {tot['disagree']}, "
              f"units with latent disagreement {latent}, trials with a failing version {tot['some_version_failed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
