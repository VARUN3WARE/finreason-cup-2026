"""h035 -- crypto asset global shock with severe/mild support policy (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h035"


def solve(text: str, q: dict) -> dict:
    # "A crypto asset starts at {P0} USD per token"
    p0 = grab(r"starts at {N} USD per token", text)
    # "and loses fraction {L} of its price in a global shock."
    loss = grab(r"loses fraction {N} of its price", text)
    # "The severe policy applies when that loss ratio is at least {T}; otherwise the mild policy applies."
    threshold = grab(r"loss ratio is at least {N}", text)
    severe = loss >= threshold  # "at least" -> inclusive
    # "After the shock, the severe policy increases the post-shock price by support ratio {s} and then deducts {d} USD per token."
    sev_support = grab(r"severe policy increases the post-shock price by support ratio {N}", text)
    sev_deduct = grab(r"severe policy increases the post-shock price by support ratio [^ ]+ and then deducts {N} USD", text)
    # "The mild policy increases it by support ratio {s} and then deducts {d} USD per token."
    mild_support = grab(r"mild policy increases it by support ratio {N}", text)
    mild_deduct = grab(r"mild policy increases it by support ratio [^ ]+ and then deducts {N} USD", text)

    # Post-shock price and share of initial price retained
    retention = Fraction(1) - loss
    post_shock = p0 * retention

    if severe:
        support, deduct = sev_support, sev_deduct
    else:
        support, deduct = mild_support, mild_deduct

    # "increases the post-shock price by support ratio s" -> multiply by (1 + s); "then deducts d"
    net = post_shock * (Fraction(1) + support) - deduct

    return {
        "final": net,
        "slots": {"post_shock_retention_checkpoint": retention},
    }
