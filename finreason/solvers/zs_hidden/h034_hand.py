from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h034"


def solve(text: str, q: dict) -> dict:
    budget = grab(r"spend at most {N} on all remediation", text)
    capital = grab(r"Capital remediation already requires {N}", text)
    liquidity = grab(r"liquidity remediation requires {N}", text)
    threshold = grab(r"any exposure above {N} incurs", text)
    ratio = grab(r"charge at ratio {N} of the excess", text)

    # Budget left for the exposure charge after the two fixed remediation costs.
    charge_budget = budget - capital - liquidity

    # Charge = ratio * max(0, exposure - threshold) <= charge_budget
    # => max exposure = threshold + charge_budget / ratio (charge_budget >= 0).
    if charge_budget < 0:
        raise ValueError("budget below fixed remediation costs")
    max_exposure = threshold + charge_budget / ratio

    return {
        "final": Fraction(max_exposure),
        "slots": {"charge_budget_checkpoint": Fraction(charge_budget)},
    }
