"""h101 -- literal transcription solver (fictional compliance planning policy).

Each block below transcribes one sentence of the question, in the order the text
gives them.  All arithmetic is exact (Fraction); the framework applies rounding.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab, grab_all

TEMPLATE_ID = "h101"

SLOT_ID = "plan_a_residual_factor_checkpoint"
PLANS = ("A", "B")
ENUM_NEITHER = "Neither plan"

_WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _count(token: str) -> int:
    """Stage count written as a word ("three") or as digits ("3")."""
    t = token.strip().lower()
    if t in _WORD_NUMBERS:
        return _WORD_NUMBERS[t]
    return int(t)


def _comparator(phrase: str):
    """Map the policy's comparison wording to an exact predicate (value vs cap)."""
    p = " ".join(phrase.lower().split())
    if p in ("no more than", "at most", "not more than", "not above", "not exceeding"):
        return lambda value, cap: value <= cap
    if p in ("less than", "below", "strictly less than", "under"):
        return lambda value, cap: value < cap
    raise ValueError(f"unknown comparison wording {phrase!r}")


def solve(text: str, q: dict) -> dict:
    # S1 "Apply the fictional scenario-local compliance planning policy given here, not
    #     current law or regulatory guidance."  -> only the rules stated below are applied.

    # S2 "Inherent risk is 0.8."
    inherent_risk = grab(r"Inherent risk is {N}", text)

    # S3/S4 "Plan X has per-stage fractional risk reduction r, implementation cost I USD,
    #        monitoring cost M USD, and fractional cost credit c."
    plan = {}
    for label in PLANS:
        reduction, implementation, monitoring, credit = grab_all(
            r"Plan " + label + r" has per-stage fractional risk reduction {N},\s*"
            r"implementation cost {N} USD,\s*monitoring cost {N} USD,\s*"
            r"and fractional cost credit {N}",
            text,
        )
        plan[label] = {
            "per_stage_fraction": reduction,
            "implementation_cost": implementation,
            "monitoring_cost": monitoring,
            "credit_fraction": credit,
        }

    # S5 "For each plan, apply its stated reduction to surviving risk in exactly three
    #     sequential stages with no risk replenishment; equivalently, multiply inherent risk
    #     by one minus that plan's per-stage fraction three successive times."
    m = re.search(r"surviving risk in exactly (\w+) sequential stages", text)
    stages = _count(m.group(1)) if m else 3
    for label in PLANS:
        p = plan[label]
        surviving = inherent_risk
        for _ in range(stages):
            surviving = surviving - p["per_stage_fraction"] * surviving  # no replenishment
        equivalent = inherent_risk * (1 - p["per_stage_fraction"]) ** stages
        assert surviving == equivalent
        p["one_stage_retained_factor"] = 1 - p["per_stage_fraction"]
        p["residual_risk"] = surviving

    # S6 "Net cost equals the sum of implementation and monitoring costs multiplied by
    #     one minus its credit fraction."
    for label in PLANS:
        p = plan[label]
        p["net_cost"] = (p["implementation_cost"] + p["monitoring_cost"]) * (1 - p["credit_fraction"])

    # S7 "A plan qualifies only if residual risk is no more than R and net cost is no more
    #     than C USD."
    qm = re.search(
        r"A plan qualifies only if residual risk is ([a-z ]+?) (" + NUMBER + r")\s+"
        r"and net cost is ([a-z ]+?) (" + NUMBER + r") USD",
        text,
    )
    if qm is None:
        raise ValueError("qualification sentence not found")
    risk_ok = _comparator(qm.group(1))
    risk_cap = F(qm.group(2))
    cost_ok = _comparator(qm.group(3))
    cost_cap = F(qm.group(4))
    for label in PLANS:
        p = plan[label]
        p["qualifies"] = risk_ok(p["residual_risk"], risk_cap) and cost_ok(p["net_cost"], cost_cap)

    # S8 "If both qualify, choose the lower exact net cost, with Plan A on an exact tie."
    # S9 "If only one qualifies, choose it; otherwise return Neither plan."
    tm = re.search(r"with Plan ([AB]) on an exact tie", text)
    tie_plan = tm.group(1) if tm else "A"
    qualified = [label for label in PLANS if plan[label]["qualifies"]]
    if len(qualified) == 2:
        cost_a, cost_b = plan["A"]["net_cost"], plan["B"]["net_cost"]
        if cost_a < cost_b:
            chosen = "A"
        elif cost_b < cost_a:
            chosen = "B"
        else:
            chosen = tie_plan
        final = f"Plan {chosen}"
    elif len(qualified) == 1:
        final = f"Plan {qualified[0]}"
    else:
        final = ENUM_NEITHER

    # S10 "Report Plan A's one-stage retained-risk factor independently to six decimal
    #      places, and return the selected plan from exact predicates and costs."
    #      -> unrounded 1 - (Plan A per-stage fraction); the framework rounds half-up to 6 dp.
    slots = {SLOT_ID: plan["A"]["one_stage_retained_factor"]}

    return {"final": final, "slots": slots}
