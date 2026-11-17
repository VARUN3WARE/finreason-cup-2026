"""h034 -- maximum total exposure such that fixed remediation costs plus an
exposure charge (ratio x excess over a threshold) stay within a remediation budget.

Literal transcription of the question text.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h034"


def solve(text: str, q: dict) -> dict:
    # "A financial institution can spend at most B on all remediation."
    budget = grab(r"can spend at most {N} on all remediation", text)
    # "Capital remediation already requires C1,"
    capital = grab(r"Capital remediation already requires {N}", text)
    # "liquidity remediation requires C2,"
    liquidity = grab(r"liquidity remediation requires {N}", text)
    # "and any exposure above T incurs a charge at ratio r of the excess."
    threshold = grab(r"any exposure above {N} incurs a charge", text)
    ratio = grab(r"incurs a charge at ratio {N} of the excess", text)

    # Aggregate remediation spending = capital + liquidity + ratio * max(0, E - T) <= budget.
    # Budget available for the exposure charge (checkpoint 1):
    charge_budget = budget - capital - liquidity

    # "Assuming the remediation budget exceeds the two fixed remediation costs":
    # charge_budget >= 0 assumed (if it is exactly 0, no excess is allowed and E = T).
    # Maximum excess exposure the charge budget can absorb (charge = ratio * excess):
    max_excess = charge_budget / ratio
    # Maximum total exposure = threshold + max excess
    max_exposure = threshold + max_excess

    return {
        "final": Fraction(max_exposure),
        "slots": {"charge_budget_checkpoint": Fraction(charge_budget)},
    }
