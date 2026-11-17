"""h108 -- maximum additional gross income that stays within a tax budget.

Structure (all three instances share it):
    "a taxpayer's total tax budget is B, of which C is already committed.
     Additional taxable income is charged at t, and only k of additional
     gross income enters the taxable base. Compute the exact maximum
     additional gross-income threshold that stays within the tax budget."

    remaining tax room      R     = B - C
    tax on extra gross G          = t * (k * G)          (k feeds the taxable base, t taxes that base)
    maximum threshold       G_max = R / (t * k)           (the point where committed + extra tax == budget)

Checkpoint (position 1, unit ratio, 6 dp):
    committed_tax_budget_share_checkpoint = C / B          "share of the total tax budget already committed"

AMBIGUITIES CONSIDERED AND RESOLUTIONS
1. Ratio vs percent for t and k.  The text says "charged at 0.8" and "only 0.6 of additional gross
   income enters the taxable base" with no "percent"/"%" anywhere; the inclusion share "0.6 of ..."
   is unambiguously a plain fraction, so t and k are ratios used as-is.  Defensively, an explicit
   "percent"/"%" marker directly after the number would be honoured by dividing by 100.
2. Base of the rate.  t applies to *taxable* income, and only k of gross income is taxable, so the
   extra tax per unit of gross income is t*k (not t, not k alone, not t*(1-k)).
3. Strict vs non-strict "stays within".  Read as <= (within = not exceeding).  Under a strict "<"
   there is no maximum at all (only a supremum), so the equality point R/(t*k) is the only
   defensible "exact maximum" under either reading.
4. Checkpoint quantity.  "share of the total tax budget already committed" = committed / total
   budget, dimensionless ratio (NOT a percent, NOT remaining share 1 - C/B, NOT C/(B-C)).
5. Rounding.  "Test the budget using the unrounded exact threshold ... the displayed amount is a
   reporting approximation" => nothing is rounded inside the computation; the framework rounds the
   exact Fraction half-up to 2 dp.  Instance 3 lands on an exact tie (…125), so exactness matters.
6. Committed exceeding the budget.  Not the case in any instance (C < B in all three); the pure
   formula is returned without a floor at zero because the text states no such floor.
7. Units.  Budget/committed are already in USD (answer unit usd, no thousands/millions scaling);
   "additional" threshold means the extra gross income only -- no base income exists in the text.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h108"

_PCT = r"\s*(percent|%)"


def _rate(pattern: str, text: str) -> Fraction:
    """Number captured by ``pattern`` ({N} = number); divided by 100 only if a percent marker follows."""
    rx = pattern.replace("{N}", f"({NUMBER})") + f"(?:{_PCT})?"
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    value = F(m.group(1))
    if m.group(2):
        value /= 100
    return value


def solve(text: str, q: dict) -> dict:
    # --- parse (anchored on surrounding words; never positional) -------------------------------
    budget = grab(r"total tax budget is\s+{N}", text)
    committed = grab(r"of which\s+{N}\s+is already committed", text)
    rate = _rate(r"[Aa]dditional taxable income is charged at\s+{N}", text)
    inclusion = _rate(r"only\s+{N}\s+of additional gross income enters the taxable base", text)

    # --- checkpoint: share of the total budget already committed (ratio) -----------------------
    committed_share = committed / budget

    # --- maximum additional gross income: committed + rate * inclusion * G == budget -----------
    remaining = budget - committed
    threshold = remaining / (rate * inclusion)

    # "Test the budget using the unrounded exact threshold": exact identity must hold.
    assert committed + rate * inclusion * threshold == budget

    return {
        "final": threshold,
        "slots": {"committed_tax_budget_share_checkpoint": committed_share},
    }
