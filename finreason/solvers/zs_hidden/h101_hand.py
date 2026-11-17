"""h101 -- two-plan compliance choice with compounded per-stage risk reduction.

Structure (fictional policy, applied exactly as worded):
  * residual risk  = inherent risk * (1 - per-stage fraction) ** stages   (stages = "three")
  * net cost       = (implementation + monitoring) * (1 - credit fraction)
  * a plan qualifies only if residual risk <= risk cap AND net cost <= cost cap ("no more than")
  * both qualify -> lower exact net cost (stated plan wins an exact tie);
    exactly one qualifies -> that plan; none -> "Neither plan"
  * checkpoint: Plan A's one-stage retained-risk factor = 1 - Plan A's per-stage fraction (a ratio),
    returned unrounded (the framework half-up rounds it to 6 places).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h101"

_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _value(pattern: str, seg: str) -> Fraction:
    """Number after ``pattern``; a trailing 'percent'/'%' converts it to a fraction."""
    m = re.search(pattern + r"\s*(" + NUMBER + r")(\s*(?:percent\b|%))?", seg, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = F(m.group(1))
    return v / 100 if m.group(2) else v


def _plan(text: str, name: str) -> dict:
    # The plan's own sentence: "Plan X has ... credit 0.2." (decimal points are followed by digits,
    # so the first period followed by whitespace/end closes the sentence).
    m = re.search(rf"{name} has (.*?)\.(?:\s|$)", text, flags=re.S)
    if m is None:
        raise ValueError(f"no parameter sentence for {name}")
    seg = m.group(1)
    return {
        "r": _value(r"risk reduction", seg),
        "impl": _value(r"implementation cost(?: of)?(?: USD)?", seg),
        "mon": _value(r"monitoring cost(?: of)?(?: USD)?", seg),
        "credit": _value(r"cost credit", seg),
    }


def _stages(text: str) -> int:
    m = re.search(r"in exactly (\w+) sequential stages", text)
    if m is None:
        m = re.search(r"(\w+) successive times", text)
    tok = m.group(1).lower()
    return int(tok) if tok.isdigit() else _WORDS[tok]


def _cmp(text: str, subject: str):
    """Comparator for '<subject> is <phrase> <cap>'; returns (cap, predicate)."""
    m = re.search(
        rf"{subject} is (no more than|not more than|at most|less than|below|under|"
        rf"no greater than|not greater than|less than or equal to)\s*(?:USD\s*)?({NUMBER})",
        text,
    )
    if m is None:
        raise ValueError(f"no cap for {subject}")
    phrase, cap = m.group(1), F(m.group(2))
    if phrase in ("less than", "below", "under"):
        return cap, (lambda x, c=cap: x < c)
    return cap, (lambda x, c=cap: x <= c)


def solve(text: str, q: dict) -> dict:
    inherent = grab(r"Inherent risk is {N}", text)
    n = _stages(text)
    plans = {"Plan A": _plan(text, "Plan A"), "Plan B": _plan(text, "Plan B")}

    _, risk_ok = _cmp(text, "residual risk")
    _, cost_ok = _cmp(text, "net cost")

    qualifies = {}
    net = {}
    for name, p in plans.items():
        retained = 1 - p["r"]                      # one-stage retained-risk factor
        residual = inherent * retained ** n        # compounded, no replenishment
        net[name] = (p["impl"] + p["mon"]) * (1 - p["credit"])
        qualifies[name] = risk_ok(residual) and cost_ok(net[name])

    tie = re.search(r"with (Plan [AB]) on an exact tie", text)
    tie_winner = tie.group(1) if tie else "Plan A"

    if qualifies["Plan A"] and qualifies["Plan B"]:
        if net["Plan A"] < net["Plan B"]:
            final = "Plan A"
        elif net["Plan B"] < net["Plan A"]:
            final = "Plan B"
        else:
            final = tie_winner
    elif qualifies["Plan A"]:
        final = "Plan A"
    elif qualifies["Plan B"]:
        final = "Plan B"
    else:
        final = "Neither plan"

    slots = {}
    for s in q["trace_spec"]["slots"]:
        sid = s["slot_id"]
        if sid == "plan_a_residual_factor_checkpoint":
            slots[sid] = 1 - plans["Plan A"]["r"]
        else:
            raise ValueError(f"unexpected slot {sid}")
    return {"final": final, "slots": slots}
