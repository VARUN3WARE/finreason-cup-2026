"""h075 -- initial principal needed so that principal plus a later contribution
(both compounding annually at the same rate) reach a stated target.

Literal transcription:
  "An account must reach T USD after N whole annual compounding periods at
   annual rate ratio r."                              -> T, N, r
  "A later contribution of C USD is deposited at a compounding boundary from
   which exactly K whole periods remain, and it earns the same rate."
                                                      -> C, K; C grows by (1+r)^K
  "Using exact compounding, what initial principal is required at the start?"
                                                      -> P * (1+r)^N + C * (1+r)^K = T
                                                         P = (T - C*(1+r)^K) / (1+r)^N
Checkpoint: compound growth factor applied to the later contribution = (1+r)^K.
No floor at zero is stated, so the principal keeps its sign.
"""

from fractions import Fraction

from finreason.nums import grab, ipow

TEMPLATE_ID = "h075"


def solve(text: str, q: dict) -> dict:
    # Sentence 1: target, horizon, rate.
    target = grab(r"must reach {N} USD", text)
    n_periods = grab(r"after {N} whole annual compounding periods?", text)
    rate = grab(r"annual rate ratio {N}", text)

    # Sentence 2: later contribution and the periods remaining after it.
    contribution = grab(r"later contribution of {N} USD", text)
    k_remaining = grab(r"from which exactly {N} whole periods? remain", text)

    growth = 1 + rate

    # Compound growth factor applied to the later contribution.
    contribution_growth = ipow(growth, k_remaining)
    contribution_fv = contribution * contribution_growth

    # Sentence 3: initial principal required at the start.
    principal_growth = ipow(growth, n_periods)
    principal = (target - contribution_fv) / principal_growth

    return {
        "final": Fraction(principal),
        "slots": {"later_contribution_growth_checkpoint": Fraction(contribution_growth)},
    }
