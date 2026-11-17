"""Hidden cluster h108: maximum additional gross income that fits a remaining tax budget.

Model, exactly as worded:
  total tax budget B, of which C is already committed
  additional taxable income is charged at rate t
  only share f of additional gross income G enters the taxable base
  additional tax  = t * (f * G)
  stays within    : C + t * f * G <= B   ->   exact maximum  G* = (B - C) / (t * f)
The budget is tested with the unrounded exact G* (it lands exactly on B, so it is within);
G* is returned unrounded and the framework rounds it half up to cents (the displayed amount
is only a reporting approximation of the exact maximum).

Checkpoint (position 1): share of the total tax budget already committed = C / B (ratio).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h108"

_CUR = r"(?:USD\s*|US\$\s*|\$\s*)?"


def _num(pattern: str, text: str) -> Fraction:
    """Number captured at ``{N}``; a trailing 'percent' / '%' converts it to a ratio."""
    rx = pattern.replace("{N}", _CUR + f"({NUMBER})" + r"(\s*(?:%|percent\b))?")
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    value = F(m.group(1))
    if m.group(2):
        value /= 100
    return value


def solve(text: str, q: dict) -> dict:
    budget = _num(r"total tax budget is {N}", text)
    committed = _num(r"of which {N} (?:is|has been|are) already committed", text)
    rate = _num(r"taxable income is charged at (?:a (?:tax )?rate of )?{N}", text)
    inclusion = _num(r"only {N} of (?:the )?additional gross income enters the taxable base", text)

    # Checkpoint 1: share of the total tax budget already committed (ratio).
    committed_share = committed / budget

    # Remaining tax budget and the additional tax generated per unit of additional gross income.
    remaining = budget - committed
    tax_per_gross = rate * inclusion

    # Exact maximum additional gross income keeping committed + additional tax within the budget.
    threshold = remaining / tax_per_gross

    # Budget test with the unrounded exact threshold (equality -> within the budget).
    assert committed + rate * (inclusion * threshold) <= budget

    return {
        "final": threshold,
        "slots": {"committed_tax_budget_share_checkpoint": committed_share},
    }
