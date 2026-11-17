from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h009"


def solve(text: str, q: dict) -> dict:
    amount = grab(r"A transfer of {N} USD", text)

    a_ratio = grab(r"Network A deducts fee ratio {N}", text)
    a_fixed = grab(r"Network A deducts fee ratio .*? and then fixed fee {N} USD", text)

    b_ratio = grab(r"Network B deducts fee ratio {N}", text)
    b_fixed = grab(r"Network B deducts fee ratio .*?, then fixed fee {N} USD", text)
    b_bonus = grab(r"increases the post-fee amount by bonus ratio {N}", text)

    threshold = grab(r"use Network A if its net receipt is at least {N} USD", text)

    # Network A: proportional fee, then fixed fee.
    a_net = amount * (1 - a_ratio) - a_fixed

    # Network B: proportional fee, then fixed fee, then bonus on the post-fee amount.
    b_after_ratio = amount * (1 - b_ratio)
    b_after_fixed = b_after_ratio - b_fixed
    b_net = b_after_fixed * (1 + b_bonus)

    # Routing rule: A if its net receipt >= threshold (equality included), else B.
    selected = a_net if a_net >= threshold else b_net

    return {
        "final": Fraction(selected),
        "slots": {"network_b_after_ratio_fee_checkpoint": Fraction(b_after_ratio)},
    }
