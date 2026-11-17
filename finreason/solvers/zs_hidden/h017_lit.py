"""h017 -- joint vs alternative stress scenario capital adequacy (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h017"


def solve(text: str, q: dict) -> dict:
    # "A portfolio worth {V} has available capital {C} and must retain at least {M}."
    portfolio_value = grab(r"portfolio worth {N}", text)
    available_capital = grab(r"available capital {N}", text)
    minimum_capital = grab(r"must retain at least {N}", text)

    # "In the joint scenario, market shock ratio {a} with sensitivity {b} and credit shock ratio {c}
    #  with sensitivity {d} contribute linear loss rates, while their product times {k} contributes
    #  an interaction rate."
    market_shock = grab(r"market shock ratio {N}", text)
    market_sens = grab(r"market shock ratio [^ ]+ with sensitivity {N}", text)
    credit_shock = grab(r"credit shock ratio {N}", text)
    credit_sens = grab(r"credit shock ratio [^ ]+ with sensitivity {N}", text)
    interaction_mult = grab(r"their product times {N}", text)

    market_linear_rate = market_shock * market_sens
    credit_linear_rate = credit_shock * credit_sens
    # "their product" = product of the two shock ratios (market x credit)
    interaction_rate = market_shock * credit_shock * interaction_mult
    joint_rate = market_linear_rate + credit_linear_rate + interaction_rate

    # "In the alternative scenario, shock ratio {s} is squared and multiplied by {m}."
    alt_shock = grab(r"alternative scenario, shock ratio {N}", text)
    alt_mult = grab(r"is squared and multiplied by {N}", text)
    alt_rate = alt_shock ** 2 * alt_mult

    # "Convert each scenario rate to a dollar loss, use the larger loss, subtract it from
    #  available capital, ..."
    joint_loss = joint_rate * portfolio_value
    alt_loss = alt_rate * portfolio_value
    larger_loss = max(joint_loss, alt_loss)
    remaining_capital = available_capital - larger_loss

    # "... return capital_pass when the remaining capital meets the minimum or capital_fail otherwise."
    final = "capital_pass" if remaining_capital >= minimum_capital else "capital_fail"

    return {"final": final, "slots": {"joint_rate_checkpoint": Fraction(joint_rate)}}
