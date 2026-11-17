# Finance model (h080): two-player Shapley attribution of cost savings.
#
#   P = savings of procurement program alone (USD millions)
#   I = savings of IT program alone (USD millions)
#   C = savings of both programs implemented together (USD millions), I < C < P + I (overlap), all > 0
#
# Procurement's marginal contribution in the two possible implementation orders:
#   - procurement first:            P - 0       = P
#   - procurement after IT:         C - I       (checkpoint 1, USD million)
# Equal weight (1/2 each, i.e. the two-player Shapley value):
#   attributed procurement savings = (P + (C - I)) / 2      (USD million)
# Share of combined-program savings attributed to procurement:
#   final = attributed / C * 100                            (percent)
#
# No overrides: no rounding is applied inside the computation; the framework rounds the
# checkpoint to 4 dp (half-up, USD million) and the final answer to 2 dp (half-up, percent).
from fractions import Fraction

from finreason.nums import grab, F  # noqa: F401

TEMPLATE_ID = "h080"


def solve(text: str, q: dict) -> dict:
    P = grab(r"procurement program alone would deliver {N} USD millions", text)
    I = grab(r"IT program alone would deliver {N} USD millions", text)
    C = grab(r"implementing both would deliver {N} USD millions", text)

    marginal_after_it = C - I
    attributed = (P + marginal_after_it) / 2
    final = attributed / C * 100

    return {
        "final": Fraction(final),
        "slots": {"procurement_marginal_after_it_checkpoint": Fraction(marginal_after_it)},
    }
