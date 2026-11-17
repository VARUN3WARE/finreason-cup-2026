"""Hidden cluster h105 -- social-impact program: beneficiary-equivalent scale that
exactly meets an investor's surplus requirement over combined fixed costs.

Structure (identical across the 3 instances, numbers differ):
    launch cost L, monitoring cost M, value per beneficiary-equivalent unit v,
    surplus ratio s.
    combined fixed costs      C   = L + M
    required social value     R   = C * (1 + s)          (stated explicitly in text)
    scale that exactly meets  n   = R / v                (final, unit "count", 2 dp half-up)
    checkpoint                M_s = M * s                (unit "usd", 2 dp half-up)

AMBIGUITIES CONSIDERED AND HOW EACH WAS RESOLVED (textual evidence):

A1. "exceed the combined fixed costs by the surplus ratio" -- multiplicative gross-up
    vs. something additive?  The text resolves it itself: "equivalently, required social
    value is combined fixed costs multiplied by one plus that ratio"  ->  R = C * (1 + s).

A2. Is the surplus ratio a percent or a plain ratio?  Values are "0.1" / "0.097675" and
    the text says "one plus that ratio"  ->  plain ratio, used as-is (no /100).

A3. What are the "combined fixed costs"?  Only two program costs are named (launch cost,
    monitoring cost); the problem calls them "the combined fixed costs"  ->  C = L + M.

A4. Does the final scale need to be a whole number of units (ceiling)?  No: "Compute the
    beneficiary-equivalent scale that exactly meets this requirement" is an equality,
    the answer format rounds to 2 decimals in unit "count", and v may be a rational such
    as 59358/4001  ->  n = C * (1 + s) / v exactly, no ceiling / floor.

A5. Checkpoint "surplus requirement attributable to monitoring cost"
    (slot monitoring_surplus_value_checkpoint, unit usd):  M * s  or  M * (1 + s)?
    - "surplus ratio" is the ratio by which social value must EXCEED costs, so "surplus"
      denotes the excess over costs; "surplus requirement" = the required surplus (as in
      "margin requirement" = required margin) = C * s for the whole program.
    - The text reserves the phrase "required social value" for C * (1 + s); had the slot
      meant M * (1 + s) it would read "required social value attributable to monitoring
      cost".  The slot name itself says the quantity is a monitoring *surplus* value.
    -> the part of the required surplus attributable to monitoring cost = M * s.

A6. Base of the surplus: it is measured against costs ("exceed the combined fixed costs
    by the surplus ratio"), not against social value  ->  surplus = s * cost, in USD.

A7. Rounding: nothing in the text says a rounded value is reused downstream, so every
    returned value is the exact Fraction; the framework applies half-up 2 dp rendering.

A8. Parsing: numbers may be decimals or rationals; each is anchored on its label words
    ("launch cost", "monitoring cost", "net monetized social value", "surplus ratio").
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h105"


def solve(text: str, q: dict) -> dict:
    launch = grab(r"launch cost\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    monitoring = grab(r"monitoring cost\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    value_per_unit = grab(r"net monetized social value\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    surplus_ratio = grab(r"surplus ratio\s+(?:of\s+)?{N}", text)

    combined_fixed = launch + monitoring                      # C = L + M
    required_value = combined_fixed * (Fraction(1) + surplus_ratio)   # R = C * (1 + s)
    scale = required_value / value_per_unit                   # n = R / v  (exactly meets)

    monitoring_surplus = monitoring * surplus_ratio           # required surplus from M

    return {
        "final": scale,
        "slots": {
            "monitoring_surplus_value_checkpoint": monitoring_surplus,
        },
    }
