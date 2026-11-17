"""h099 -- back out the pre-shock price from a loss followed by a relative rebound (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h099"


def solve(text: str, q: dict) -> dict:
    # "A crypto asset is currently priced at {P} USD per token"
    current_price = grab(r"currently priced at {N} USD per token", text)
    # "after a global shock reduced its pre-shock price by loss ratio {L}"
    loss_ratio = grab(r"reduced its pre-shock price by loss ratio {N}", text)
    # "increased the resulting post-shock price by a rebound ratio equal to {k} times the shock loss ratio"
    relative_magnitude = grab(r"rebound ratio equal to {N} times the shock loss ratio", text)
    rebound_ratio = relative_magnitude * loss_ratio

    # Sequential: current = pre_shock * (1 - loss) * (1 + rebound)
    # => pre_shock = current / ((1 - loss) * (1 + rebound))
    post_shock_price = current_price / (1 + rebound_ratio)
    pre_shock_price = post_shock_price / (1 - loss_ratio)

    return {
        "final": pre_shock_price,
        "slots": {"rebound_ratio_checkpoint": rebound_ratio},
    }
