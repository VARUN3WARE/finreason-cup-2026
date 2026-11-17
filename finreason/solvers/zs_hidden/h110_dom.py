# =====================================================================================
# h110 -- FINANCE MODEL (written before the code)
#
# Economic object: a two-way capital-allocation choice between social-impact programs A and B.
# Each program is a project with a fixed + variable cost, a lump-sum social payoff, and a
# redundancy scheme ("n independent delivery opportunities, at least one success is enough").
#
# Inputs per program (program A is given with labels; program B is given positionally,
# "corresponding inputs ...", in the SAME field order as A's labelled list):
#     F  fixed cost
#     c  aggregate delivery cost per beneficiary-equivalent unit
#     V  beneficiary-equivalent volume
#     v  monetized social value per unit
#     p  per-opportunity success probability
#     n  number of independent delivery opportunities sharing p   (text: "exactly three" -> 3)
# Portfolio-level inputs: cost cap K ("total cost does not exceed K"), minimum volume V_min
# ("its volume reaches V_min").
#
# Quantities (all exact Fractions; no float anywhere):
#     TC   = F + c * V              total cost.  The stated total cost ALREADY covers all n
#                                   opportunities, so it is NOT multiplied by n.
#     PV   = v * V                  planned monetized social value.  Realised ONCE (not once per
#                                   success) if at least one opportunity succeeds.
#     q    = 1 - p                  failure probability of ONE delivery opportunity
#                                   <-- this is the (only) checkpoint, for program A.
#     q^n                           probability that all n independent opportunities fail
#     Peff = 1 - q^n                effective delivery probability (at least one success)
#     ENSV = PV * Peff - TC         expected net social value.  Nothing in the text requires
#                                   ENSV > 0, so a feasible program with negative ENSV is still
#                                   a legitimate candidate.
#
# Feasibility screen (hard constraints, per program):
#     feasible  <=>  TC <= K   AND   V >= V_min
#     ("does not exceed" -> non-strict <=; "reaches" -> at least, i.e. non-strict >=)
#
# Decision rule (enum answer):
#     both feasible  -> higher ENSV wins; exact tie -> program_a
#     exactly one    -> that program (even if the infeasible one has the higher ENSV)
#     neither        -> no_feasible_program
#
# Checkpoint:
#     program_a_failure_probability_checkpoint = 1 - p_A  (ratio, ONE opportunity -- not q^3,
#     not Peff).  Returned UNROUNDED and exact; the framework applies half-up to 6 decimals.
#     (Exactness matters: e.g. 1 - 0.4999995 = 0.5000005 must round half-up to 0.500001.)
#
# Overrides of "standard" conventions: none needed beyond the text's own definitions
# (no discounting, no risk adjustment; probabilities used as stated; payoff realised once).
# =====================================================================================
from __future__ import annotations

import re
from fractions import Fraction

from finreason import nums
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h110"

# Field labels of program A, in the vocabulary of the text.  The ORDER in which they appear in
# the text is used to read program B's positional "corresponding inputs".
_LABELS = {
    "fixed": r"fixed cost {N}",
    "unit_cost": r"aggregate delivery cost per beneficiary-equivalent unit {N}",
    "volume": r"beneficiary-equivalent volume {N}",
    "unit_value": r"monetized social value per unit {N}",
    "prob": r"per-opportunity success probability {N}",
}

_COUNT_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _rx(pattern: str) -> str:
    return pattern.replace("{N}", f"({nums.NUMBER})")


def _parse_programs(text: str):
    """Return (A, B) dicts with fixed / unit_cost / volume / unit_value / prob as Fractions."""
    split = text.index("against program B")
    a_text, b_text = text[:split], text[split:]

    a: dict[str, Fraction] = {}
    pos: dict[str, int] = {}
    for key, pat in _LABELS.items():
        m = re.search(_rx(pat), a_text, flags=re.S)
        if m is None:
            raise ValueError(f"program A field not found: {key}")
        a[key] = F(m.group(1))
        pos[key] = m.start()

    order = sorted(_LABELS, key=lambda k: pos[k])  # field order as written for A
    # Program B: "corresponding inputs x1, x2, x3, x4, and x5" in the same order as A's list.
    m = re.search(r"corresponding inputs\s+(.*?)(?:\.\s|\.$)", b_text, flags=re.S)
    if m is None:
        raise ValueError("program B inputs not found")
    b_vals = [F(g.group(0)) for g in re.finditer(nums.NUMBER, m.group(1))]
    if len(b_vals) != len(order):
        raise ValueError(f"expected {len(order)} program B inputs, got {len(b_vals)}")
    b = dict(zip(order, b_vals))
    return a, b


def _n_opportunities(text: str) -> int:
    m = re.search(r"exactly\s+(\w+)\s+independent delivery opportunities", text)
    if m is None:
        return 3
    w = m.group(1).lower()
    if w.isdigit():
        return int(w)
    return _COUNT_WORDS.get(w, 3)


def _metrics(prog: dict[str, Fraction], n: int):
    total_cost = prog["fixed"] + prog["unit_cost"] * prog["volume"]
    planned_value = prog["unit_value"] * prog["volume"]
    q = 1 - prog["prob"]                 # failure probability of one opportunity
    p_eff = 1 - q ** n                   # at least one of n independent opportunities succeeds
    ensv = planned_value * p_eff - total_cost
    return total_cost, planned_value, q, p_eff, ensv


def solve(text: str, q: dict) -> dict:
    a, b = _parse_programs(text)
    n = _n_opportunities(text)

    cap, min_vol = grab_all(r"total cost does not exceed {N} and its volume reaches {N}", text)

    cost_a, pv_a, q_a, peff_a, ensv_a = _metrics(a, n)
    cost_b, pv_b, q_b, peff_b, ensv_b = _metrics(b, n)

    feas_a = cost_a <= cap and a["volume"] >= min_vol
    feas_b = cost_b <= cap and b["volume"] >= min_vol

    if feas_a and feas_b:
        final = "program_a" if ensv_a >= ensv_b else "program_b"   # tie -> program_a
    elif feas_a:
        final = "program_a"
    elif feas_b:
        final = "program_b"
    else:
        final = "no_feasible_program"

    return {
        "final": final,
        "slots": {
            "program_a_failure_probability_checkpoint": q_a,   # 1 - p_A, one opportunity
        },
    }
