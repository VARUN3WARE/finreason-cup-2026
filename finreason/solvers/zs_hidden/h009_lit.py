"""h009 -- two-network transfer routing (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h009"


def solve(text: str, q: dict) -> dict:
    # "A transfer of {X} USD may use Network A or Network B."
    transfer = grab(r"A transfer of {N} USD", text)

    # "Network A deducts fee ratio {a_r} and then fixed fee {a_f} USD."
    a_ratio = grab(r"Network A deducts fee ratio {N}", text)
    a_fixed = grab(r"Network A deducts fee ratio [^ ]+ and then fixed fee {N} USD", text)

    # "Network B deducts fee ratio {b_r}, then fixed fee {b_f} USD, and finally
    #  increases the post-fee amount by bonus ratio {b_b}."
    b_ratio = grab(r"Network B deducts fee ratio {N}", text)
    b_fixed = grab(r"Network B deducts fee ratio [^ ]+?, then fixed fee {N} USD", text)
    b_bonus = grab(r"increases the post-fee amount by bonus ratio {N}", text)

    # "use Network A if its net receipt is at least {T} USD, including exact equality"
    threshold = grab(r"use Network A if its net receipt is at least {N} USD", text)

    # Compute both candidate route receipts (unrounded).
    a_after_ratio = transfer - transfer * a_ratio
    a_net = a_after_ratio - a_fixed

    b_after_ratio = transfer - transfer * b_ratio
    b_after_fixed = b_after_ratio - b_fixed
    b_net = b_after_fixed + b_after_fixed * b_bonus

    # Routing rule: at least (>=), inclusive of exact equality.
    selected = a_net if a_net >= threshold else b_net

    return {
        "final": Fraction(selected),
        "slots": {"network_b_after_ratio_fee_checkpoint": Fraction(b_after_ratio)},
    }
