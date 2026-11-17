from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h100"


def solve(text: str, q: dict) -> dict:
    bmv = grab(r"begins a measurement period at value {N}", text)
    contrib = grab(r"contribution of {N} is added", text)
    elapsed = grab(r"added after {N} of the period has elapsed", text)
    emv = grab(r"post-distribution account value is {N}", text)
    dist = grab(r"terminal cash distribution of {N}", text)

    # Contribution weighted by fraction of period remaining.
    weight = 1 - elapsed
    weighted_contrib = weight * contrib

    # Terminal distribution: zero denominator weight, but it is an external
    # outflow, so it is added back in the gain (net flow = contrib - dist).
    net_flow = contrib - dist
    gain = emv - bmv - net_flow
    capital_base = bmv + weighted_contrib  # + 0 * (-dist)
    roi_pct = gain / capital_base * 100

    return {"final": roi_pct, "slots": {"weighted_contribution_checkpoint": weighted_contrib}}
