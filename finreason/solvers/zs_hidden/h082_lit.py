"""h082 -- compliance: fixed abate-then-buy vs credits-only (literal transcription)."""

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h082"


def solve(text: str, q: dict) -> dict:
    # "Treat one carbon credit as covering one ton of CO2e."
    tons_per_credit = Fraction(1)

    # "A company has a compliance obligation of X tons of CO2e,
    #  internal abatement capacity Y tons of CO2e, and operational availability true|false."
    obligation = grab(r"compliance obligation of {N} tons", text)
    capacity = grab(r"internal abatement capacity {N} tons", text)
    m = re.search(r"operational availability (true|false)", text, flags=re.I)
    if m is None:
        raise ValueError("availability flag not found")
    available = m.group(1).lower() == "true"

    # "Internal abatement has fixed cost F USD and variable cost V USD per ton of CO2e."
    fixed_cost = grab(r"fixed cost {N} USD", text)
    var_cost = grab(r"variable cost {N} USD per ton", text)

    # "Carbon credits cost P USD per ton of CO2e, with at most C ton-equivalent credits available."
    credit_price = grab(r"Carbon credits cost {N} USD per ton", text)
    credit_cap = grab(r"at most {N} ton-equivalent credits", text)

    # Abate-then-buy (fixed): whenever internal abatement is available, abate exactly
    # min(obligation, capacity), then buy credits for the residual. Not optimized.
    if available:
        abated = min(obligation, capacity)
        residual = obligation - abated
        credits_needed_atb = residual / tons_per_credit
        atb_feasible = credits_needed_atb <= credit_cap
        variable_total = abated * var_cost
        atb_cost = fixed_cost + variable_total + credits_needed_atb * credit_price
    else:
        # Internal abatement unavailable -> the abate-then-buy strategy cannot be executed.
        abated = Fraction(0)
        variable_total = Fraction(0)
        atb_feasible = False
        atb_cost = None

    # Credits-only strategy: buy credits for the full obligation.
    credits_needed_co = obligation / tons_per_credit
    co_feasible = credits_needed_co <= credit_cap
    co_cost = credits_needed_co * credit_price

    # Decision rule.
    if atb_feasible and co_feasible:
        final = "abate_then_buy" if atb_cost <= co_cost else "credits_only"
    elif atb_feasible:
        final = "abate_then_buy"
    elif co_feasible:
        final = "credits_only"
    else:
        final = "no_feasible_strategy"

    return {"final": final, "slots": {"variable_abatement_total_checkpoint": variable_total}}
