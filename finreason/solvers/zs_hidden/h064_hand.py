"""h064: green-bond structure A vs B -- compounded interest + issuance cost, feasibility screen, pick cheaper."""

import re
from fractions import Fraction

from finreason.nums import grab, real_pow, NUMBER

TEMPLATE_ID = "h064"


def _structure(label: str, text: str):
    rx = (
        rf"Structure {label} has annual yield ratio ({NUMBER}),\s*term ({NUMBER}),\s*"
        rf"issuance cost ({NUMBER}),\s*and eligible-proceeds share ({NUMBER})"
    )
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"structure {label} not found")
    r, n, c, s = (Fraction(g.replace(",", "")) for g in m.groups())
    return r, n, c, s


def _power(base: Fraction, n: Fraction) -> Fraction:
    if n.denominator == 1:
        return base ** int(n)
    return real_pow(base, n)


def solve(text: str, q: dict) -> dict:
    principal = grab(r"same principal {N}", text)
    cap = grab(r"total financing cost does not exceed {N}", text)
    share_min = grab(r"eligible share reaches {N}", text)

    totals = {}
    feasible = {}
    factor_a = None
    for label, token in (("A", "structure_a"), ("B", "structure_b")):
        r, n, c, s = _structure(label, text)
        factor = 1 + r                       # one-period (annual) gross compound factor
        if label == "A":
            factor_a = factor
        interest = principal * (_power(factor, n) - 1)   # compound principal, subtract principal
        total = interest + c                              # add issuance cost
        totals[token] = total
        # "does not exceed" -> <= ; "reaches" -> >=
        feasible[token] = (total <= cap) and (s >= share_min)

    fa, fb = feasible["structure_a"], feasible["structure_b"]
    if fa and fb:
        final = "structure_a" if totals["structure_a"] <= totals["structure_b"] else "structure_b"
    elif fa:
        final = "structure_a"
    elif fb:
        final = "structure_b"
    else:
        final = "no_feasible_structure"

    return {"final": final, "slots": {"structure_a_annual_factor_checkpoint": factor_a}}
