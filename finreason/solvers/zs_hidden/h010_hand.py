"""h010: required joint success probability for two dependent synergy initiatives,
expressed as the percentage of the Frechet feasible band consumed above its lower bound."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h010"


def solve(text: str, q: dict) -> dict:
    p_cost = grab(r"cost-synergy initiative has marginal success probability {N}", text)
    b_cost = grab(r"cost-synergy initiative has marginal success probability [^ ]+ and contributes {N} USD millions", text)
    p_rev = grab(r"revenue-synergy initiative has marginal success probability {N}", text)
    b_rev = grab(r"revenue-synergy initiative has marginal success probability [^ ]+ and contributes {N} USD millions", text)
    b_joint = grab(r"incremental benefit {N} USD millions", text)
    cost = grab(r"integration cost is {N} USD millions", text)
    target = grab(r"required expected net benefit is {N} USD millions", text)

    # Gross expected benefit required before the unconditional integration cost is deducted.
    gross = target + cost

    # E[benefit] = p_cost*b_cost + p_rev*b_rev + P(both)*b_joint  (linear in joint probability,
    # no dependence structure assumed).
    joint = (gross - p_cost * b_cost - p_rev * b_rev) / b_joint

    # Band as defined in the text.
    cost_fail = 1 - p_cost
    lower = p_rev - cost_fail
    width = cost_fail

    pct_band = (joint - lower) / width * 100

    return {
        "final": Fraction(pct_band),
        "slots": {
            "gross_requirement_checkpoint": Fraction(gross),
            "frechet_lower_bound_checkpoint": Fraction(lower),
        },
    }
