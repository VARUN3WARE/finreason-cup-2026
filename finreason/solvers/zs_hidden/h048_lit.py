"""h048 -- revenue downturn then required recovery rate (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h048"


def solve(text: str, q: dict) -> dict:
    # "A company starts with revenue {R0}"
    start_revenue = grab(r"starts with revenue {N}", text)
    # "and then experiences a downturn ratio {d}" -- fraction of revenue lost
    downturn_ratio = grab(r"downturn ratio {N}", text)
    # "It must reach target revenue {T} after recovery."
    target_revenue = grab(r"target revenue {N}", text)

    # Revenue immediately after the downturn
    post_downturn_revenue = start_revenue * (1 - downturn_ratio)

    # "Assuming the target exceeds the post-downturn revenue" -- additional revenue needed
    additional_needed = target_revenue - post_downturn_revenue

    # "required recovery rate as the additional revenue needed divided by post-downturn revenue"
    recovery_rate = additional_needed / post_downturn_revenue

    # "report that rate as a percentage"
    final = recovery_rate * 100

    return {
        "final": Fraction(final),
        "slots": {"post_downturn_checkpoint": Fraction(post_downturn_revenue)},
    }
