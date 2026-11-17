from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h080"


def solve(text: str, q: dict) -> dict:
    p = grab(r"procurement program alone would deliver {N} USD millions", text)
    it = grab(r"IT program alone would deliver {N} USD millions", text)
    both = grab(r"implementing both would deliver {N} USD millions", text)

    # Procurement's marginal contribution when introduced after IT.
    marginal_after_it = both - it
    # Equal weight to both implementation orders (two-player Shapley value).
    attributed = (p + marginal_after_it) / 2
    pct_of_combined = attributed / both * 100

    return {
        "final": pct_of_combined,
        "slots": {"procurement_marginal_after_it_checkpoint": marginal_after_it},
    }
