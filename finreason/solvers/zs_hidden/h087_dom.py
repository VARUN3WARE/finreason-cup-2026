# FINANCE MODEL (h087)
# Two post-merger initiatives, independent Bernoulli outcomes over the same horizon:
#   cost-synergy:    success prob p_c, standalone payoff A_c (USD millions) when it succeeds
#   revenue-synergy: success prob p_r, standalone payoff A_r (USD millions) when it succeeds
#   If BOTH succeed there is an extra incremental joint benefit J "beyond the two standalone benefits"
#   (i.e. payoff in the both-succeed state = A_c + A_r + J).
# Independence => P(both succeed) = p_c * p_r.
#   Expected standalone cost benefit    E_c = p_c * A_c        (checkpoint 1, USD million)
#   Expected standalone revenue benefit E_r = p_r * A_r        (checkpoint 2, USD million)
#   Expected incremental joint benefit  E_j = p_c * p_r * J
#   Total expected gross integration benefit = E_c + E_r + E_j  (joint benefit is additive, not netted)
#   Answer = 100 * E_j / (E_c + E_r + E_j)  in percent, unrounded exact Fraction.
# No overrides of standard conventions. All values exact (Fraction).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h087"


def solve(text: str, q: dict) -> dict:
    p_c, a_c = grab_all(r"cost-synergy initiative succeeds with marginal probability {N} and contributes {N} USD", text)
    p_r, a_r = grab_all(r"revenue-synergy initiative succeeds with marginal probability {N} and contributes {N} USD", text)
    joint = grab(r"incremental joint benefit {N} USD", text)

    e_c = p_c * a_c
    e_r = p_r * a_r
    e_j = p_c * p_r * joint  # independence
    total = e_c + e_r + e_j
    share = Fraction(100) * e_j / total

    return {
        "final": share,
        "slots": {
            "expected_cost_benefit_checkpoint": e_c,
            "expected_revenue_benefit_checkpoint": e_r,
        },
    }
