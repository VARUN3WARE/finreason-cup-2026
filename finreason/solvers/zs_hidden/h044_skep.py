"""Solver for hidden cluster h044 -- cleanup-timing NPV difference (early vs deferred plan).

Structure
---------
A valuation-date base cleanup estimate B escalates at a nominal effective annual rate g.
  * Early plan:    pays B*(1+g)^Te at the end of year Te.
  * Deferred plan: pays B*(1+g)^Td plus a fixed nominal administration outflow A,
                   both at the end of year Td.
All of these are discounted at the nominal effective annual rate r, compounded annually.
Required: NPV(deferred) - NPV(early), signed USD.

Ambiguity hunting -- points where analysts could disagree and how the text resolves them
-------------------------------------------------------------------------------------------
1. SIGN CONVENTION.  Cleanup and administration are outflows, so NPV(plan) = -PV(plan costs).
   Hence NPV(deferred) - NPV(early) = PV(early cost) - PV(deferred costs).
   Confirmed by the text: "A positive result favors deferral" -- deferral is favoured exactly
   when its PV cost is lower, which makes this difference positive.  Non-cleanup flows cancel.
2. DISCOUNT FACTOR CHECKPOINT.  "cumulative discount factor to the deferred terminal date"
   is the standard present-value factor 1/(1+r)^Td (a number < 1), not the compounding
   factor (1+r)^Td.  Unit "multiple".
3. GROWTH FACTOR CHECKPOINT.  "cumulative cleanup escalation factor to the early payment date"
   = (1+g)^Te, counted from the valuation date (the base estimate is the "valuation-date"
   estimate and the early plan pays "at the end of year Te").  Unit "multiple".
4. RATE UNITS.  "The escalation and discount rates ... are decimal ratios": 0.1 means 10%.
   Defensive: if an instance ever wrote "percent"/"%" right after the number, divide by 100.
5. COMPOUNDING.  Both rates are "nominal effective annual" and discounting is "compounded
   annually" with integer end-of-year dates, so every factor is an exact integer power of a
   Fraction -- no real_pow/exp needed.
6. ADMINISTRATION OUTFLOW.  "fixed nominal" => NOT escalated; "paid only at that terminal
   date" => occurs once at Td and is discounted by 1/(1+r)^Td ("Discount all cleanup-related
   cash flows").  It belongs to the deferred plan only.
7. ESCALATION OF THE DEFERRED COST.  "The deferred plan pays the resulting cleanup cost at
   the end of year Td" -- the same escalation process applied to the base estimate for Td
   years: B*(1+g)^Td (not re-escalated from the early date, which is the same thing anyway).
8. ROUNDING.  No intermediate rounding is stated ("use exact arithmetic through all
   intermediate steps"); the framework rounds the unrounded Fractions.
9. DEGENERATE BRANCH.  Te may equal Td (one instance): the cleanup terms cancel exactly and
   the difference is just -A/(1+r)^Td.  Te may also be < Td.  Nothing special is needed;
   the formula handles both.  Zero is reported as 0.00 (signed USD).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h044"


def _rate(pattern: str, text: str) -> Fraction:
    """Grab a rate; the text says rates are decimal ratios, but if a percent marker
    directly follows the number, convert to a ratio defensively."""
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    value = F(m.group(1))
    tail = text[m.end(1): m.end(1) + 12].lstrip()
    if tail.startswith("%") or tail.lower().startswith("percent"):
        value /= 100
    return value


def _year(pattern: str, text: str) -> int:
    n = grab(pattern, text)
    if n.denominator != 1:
        raise ValueError(f"non-integer year {n}")
    return int(n)


def solve(text: str, q: dict) -> dict:
    base = grab(r"base cleanup estimate is {N}", text)
    g = _rate(r"escalation rate {N}", text)
    t_early = _year(r"early plan pays the resulting cleanup cost at the end of year {N}", text)
    t_def = _year(r"deferred plan pays the resulting cleanup cost at the end of year {N}", text)
    admin = grab(r"administration outflow of {N}", text)
    # "nominal effective annual rate {N}" matches only the discount sentence; the escalation
    # sentence reads "nominal effective annual escalation rate".
    r = _rate(r"[Dd]iscount all cleanup-related cash flows at the nominal effective annual rate {N}", text)

    one_plus_g = 1 + g
    one_plus_r = 1 + r

    growth_early = one_plus_g ** t_early          # checkpoint 1 (multiple)
    growth_def = one_plus_g ** t_def
    df_early = Fraction(1) / one_plus_r ** t_early
    df_def = Fraction(1) / one_plus_r ** t_def    # checkpoint 2 (multiple)

    pv_early_cost = base * growth_early * df_early
    pv_def_cost = (base * growth_def + admin) * df_def

    # NPV(plan) = -(PV of its costs); non-cleanup flows cancel.
    diff = (-pv_def_cost) - (-pv_early_cost)

    return {
        "final": diff,
        "slots": {
            "early_cleanup_growth_factor_checkpoint": growth_early,
            "terminal_discount_factor_checkpoint": df_def,
        },
    }
