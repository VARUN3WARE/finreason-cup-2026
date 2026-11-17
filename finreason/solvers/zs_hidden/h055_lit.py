"""h055 -- linear + convexity shock loss, capped, compared with a budget (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h055"


def solve(text: str, q: dict) -> dict:
    # "A portfolio worth {V} faces positive downside shock ratio {s}."
    portfolio_value = grab(r"portfolio worth {N}", text)
    shock = grab(r"downside shock ratio {N}", text)
    # "Its linear loss sensitivity is {a}, and its convexity multiplier {c} applies to the square of the shock."
    linear_sensitivity = grab(r"linear loss sensitivity is {N}", text)
    convexity_multiplier = grab(r"convexity multiplier {N}", text)

    # Linear loss rate = sensitivity x shock; convexity loss rate = multiplier x shock^2.
    linear_loss_rate = linear_sensitivity * shock
    convexity_loss_rate = convexity_multiplier * shock ** 2

    # "Add the linear and convexity loss rates, convert the result to a gross dollar loss,
    #  and cap that loss at {cap}."
    total_loss_rate = linear_loss_rate + convexity_loss_rate
    gross_dollar_loss = portfolio_value * total_loss_rate
    cap = grab(r"cap that loss at {N}", text)
    capped_loss = min(gross_dollar_loss, cap)

    # "Compare the capped loss with budget {B}. Return within_budget when the capped loss
    #  does not exceed the budget and budget_breach otherwise."
    budget = grab(r"with budget {N}", text)
    final = "within_budget" if capped_loss <= budget else "budget_breach"

    return {
        "final": final,
        "slots": {"convexity_ratio_checkpoint": Fraction(convexity_loss_rate)},
    }
