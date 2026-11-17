"""Hidden cluster h034 -- maximum exposure under a remediation budget.

Structure (all three instances):
    A financial institution can spend at most B on all remediation.
    Capital remediation requires C, liquidity remediation requires L (both fixed),
    and any exposure above threshold T incurs a charge at ratio r of the excess.
    Assuming B exceeds C + L, compute the maximum total exposure E that keeps
    aggregate remediation spending within budget.

Chain:
    charge_budget = B - C - L                       (checkpoint, usd)
    E_max         = T + charge_budget / r           (final, usd)

AMBIGUITY HUNT -- points where two analysts could disagree, and the resolution:

 1. "ratio 0.8 of the excess": a ratio, not a percent. The text literally says
    "ratio", so the multiplier is used as-is (0.8, not 0.008). A defensive
    fallback divides by 100 only if the word "percent" immediately follows the
    number, which never happens in the three instances.
 2. "within budget": inclusive (spending <= B). The exposure is continuous, so
    the maximum is attained at equality: C + L + r*(E - T) = B. Strict vs
    non-strict would only change sup vs max, not the numeric value.
 3. "exposure above T incurs a charge ... of the excess": excess = E - T, charge
    = r * max(0, E - T). Exposure at or below T costs nothing, so when the
    charge budget is exactly zero (instance 2: 5 - 2 - 3 = 0) the maximum
    exposure is the threshold itself, which the formula T + 0/r reproduces.
 4. Checkpoint "budget available for the exposure charge": the leftover after
    the two fixed costs, B - C - L, in usd (same units as the budget). It is
    NOT floored at zero: the stated assumption (B exceeds C + L) guarantees it
    is non-negative, and the three instances give 0.963, 0 and 3.
 5. "total exposure" means the exposure level E itself (not the excess over T
    and not the charge). Only the charge counts as remediation spending; the
    exposure itself is not spent.
 6. Units: every number is in plain usd (no millions/thousands scaling), both
    result specs are "usd" with half_up 2dp applied by the framework; values
    are returned unrounded.
 7. No rounding happens inside the chain: nothing in the text says a rounded
    or whole-unit value is reused downstream.
 8. The order of the two fixed costs in the text (capital first, liquidity
    second) is irrelevant to the sum; each is parsed by its own anchor word.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, grab

TEMPLATE_ID = "h034"


def _ratio(text: str) -> Fraction:
    """Charge multiplier applied to the excess; honours 'ratio' (plain) vs a
    hypothetical 'percent' phrasing."""
    m = re.search(rf"ratio\s+({NUMBER})\s*(percent|%)?\s+of the excess", text, flags=re.S)
    if m is None:
        m = re.search(rf"charge at\s+({NUMBER})\s*(percent|%)?\s+of the excess", text, flags=re.S)
    if m is None:
        raise ValueError("charge ratio not found")
    r = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        r /= 100
    return r


def solve(text: str, q: dict) -> dict:
    budget = grab(r"spend at most {N} on all remediation", text)
    capital = grab(r"[Cc]apital remediation (?:already )?requires {N}", text)
    liquidity = grab(r"[Ll]iquidity remediation (?:already )?requires {N}", text)
    threshold = grab(r"exposure above {N} incurs", text)
    ratio = _ratio(text)

    # Budget left for the exposure charge after the two fixed remediation costs.
    charge_budget = budget - capital - liquidity

    if ratio == 0:
        raise ValueError("zero charge ratio: maximum exposure is unbounded")

    # Spending = C + L + r*(E - T) <= B  ->  E_max = T + (B - C - L) / r
    max_exposure = threshold + charge_budget / ratio

    return {
        "final": max_exposure,
        "slots": {"charge_budget_checkpoint": charge_budget},
    }
