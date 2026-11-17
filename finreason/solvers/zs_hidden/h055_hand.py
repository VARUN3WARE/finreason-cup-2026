from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h055"


def solve(text: str, q: dict) -> dict:
    value = grab(r"portfolio worth (?:USD |\$)?{N}", text)
    shock = grab(r"shock ratio (?:of )?{N}", text)
    sens = grab(r"linear loss sensitivity is {N}", text)
    conv = grab(r"convexity multiplier (?:is |of )?{N}", text)
    cap = grab(r"cap that loss at (?:USD |\$)?{N}", text)
    budget = grab(r"with budget (?:USD |\$)?{N}", text)

    linear_rate = sens * shock
    convexity_rate = conv * shock ** 2
    total_rate = linear_rate + convexity_rate
    gross_loss = value * total_rate
    capped = min(gross_loss, cap)

    final = "within_budget" if capped <= budget else "budget_breach"
    return {"final": final, "slots": {"convexity_ratio_checkpoint": Fraction(convexity_rate)}}
