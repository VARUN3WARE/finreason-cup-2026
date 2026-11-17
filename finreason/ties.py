"""Count half-up rounding ties and how a float pipeline would misround them.

  python -m finreason.ties      # writes work/rounding_tie_analysis.json

A field is an exact tie when value * 10**places has fractional part exactly 1/2. "float_fmt_wrong" counts fields where
formatting float(value) with Python's fixed-point formatting differs from exact half-up rounding;
"float_decimal_wrong" uses Decimal(repr(float)) with ROUND_HALF_UP instead. Both understate the damage of a real float
pipeline, which also accumulates error during the computation.
"""

from __future__ import annotations

import json
from collections import Counter
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

from . import data
from .check import run_solver
from .fmt import half_up_text
from .hidden import DECISIONS, variant_path
from .registry import seen_solvers
from .zs import clusters, load_module


def _analyze(value, spec) -> tuple[bool, bool, bool] | None:
    if spec["type"] != "decimal" or spec["rounding"]["mode"] != "half_up" or isinstance(value, str):
        return None
    v = Fraction(value)
    places = spec["rounding"]["decimal_places"]
    scaled = v * 10**places
    tie = scaled - (scaled.numerator // scaled.denominator) == Fraction(1, 2)
    exact = half_up_text(v, places)
    f = float(v)
    fmt_wrong = f"{f:.{places}f}" != exact
    dec_wrong = str(Decimal(repr(f)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)) != exact
    return tie, fmt_wrong, dec_wrong


def _fields(q: dict, result: dict):
    yield result["final"], q["answer_spec"]
    for s in q["trace_spec"]["slots"]:
        yield result["slots"][s["slot_id"]], s["result_spec"]


def main() -> int:
    stats: dict[str, Counter] = {}

    def add(name: str, r) -> None:
        c = stats.setdefault(name, Counter())
        if r is not None:
            c["fields"] += 1
            c["ties"] += r[0]
            c["float_fmt_wrong"] += r[1]
            c["float_decimal_wrong"] += r[2]

    qs = data.by_id()
    lib = seen_solvers()
    for tid, members in data.template_members().items():
        for split in ("train", "dev", "lb", "test"):
            for cid in members.get(split, []):
                res = run_solver(lib[tid], qs[cid])
                name = "seen_labeled" if split in ("train", "dev") else f"seen_{split}"
                for value, spec in _fields(qs[cid], res):
                    add(name, _analyze(value, spec))
    for cid, d in json.loads(DECISIONS.read_text()).items():
        module = load_module(str(variant_path(cid, d["variant"])))
        for case_id in clusters()[cid]["case_ids"]:
            res = run_solver(module, qs[case_id])
            for value, spec in _fields(qs[case_id], res):
                add("hidden_test", _analyze(value, spec))
    out = {k: dict(v) for k, v in stats.items()}
    (data.WORK / "rounding_tie_analysis.json").write_text(json.dumps(out, indent=1))
    for k, v in out.items():
        print(k, v, f"tie rate {v['ties'] / max(v['fields'], 1):.2%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
