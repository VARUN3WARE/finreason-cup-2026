"""h098 -- stress-floor + policy-cap maximum risky-asset weight (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h098"


def solve(text: str, q: dict) -> dict:
    # "An investor has a portfolio worth V"
    portfolio_value = grab(r"portfolio worth (?:USD |\$)?{N}", text)
    # "requires its stressed value to remain at or above FLOOR"
    floor_value = grab(r"remain at or above (?:USD |\$)?{N}", text)
    # "the risky asset loses L of its allocated amount" (fraction; percent form tolerated)
    try:
        loss_rate = grab(r"risky asset loses {N} percent", text) / 100
    except ValueError:
        try:
            loss_rate = grab(r"risky asset loses {N}%", text) / 100
        except ValueError:
            loss_rate = grab(r"risky asset loses {N}", text)
    # "all capital outside the risky asset retains its value"
    # "Policy also caps the risky asset's portfolio weight at CAP"
    try:
        cap = grab(r"portfolio weight at {N} percent", text) / 100
    except ValueError:
        try:
            cap = grab(r"portfolio weight at {N}%", text) / 100
        except ValueError:
            cap = grab(r"portfolio weight at {N}", text)

    # Allowable dollar loss under the floor: stressed value >= floor
    loss_budget = portfolio_value - floor_value

    # Stressed value = V - w * V * L >= floor  =>  w <= (V - floor) / (V * L)
    stress_weight = loss_budget / (portfolio_value * loss_rate)

    # Maximum permitted weight: apply the stress floor and the policy cap to the exact weight
    weight = min(stress_weight, cap)
    if weight < 0:
        weight = Fraction(0)

    return {
        "final": weight * 100,
        "slots": {"loss_budget_checkpoint": loss_budget},
    }
