"""Hidden cluster h112: DeFi liquidity position with an optional, threshold-activated IL hedge.

Structure (all values exact Fractions):
  capital C, fee-yield ratio f, impermanent-loss ratio L,
  hedge coverage fraction h (of the impermanent loss), hedge cost fraction k (of capital, paid only if activated),
  risk limit R (USD).

  covered loss ratio  = h * L                      (checkpoint; ratio of position capital, branch-independent)
  unhedged loss (USD) = C * L
  hedge activated  <=> C * L > R                   ("strictly exceeds")
  net P/L (unhedged)  = C * f - C * L
  net P/L (hedged)    = C * f - C * L + C * h * L - C * k
  final = selected net P/L in USD, excluding return of the original capital.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h112"


def solve(text: str, q: dict) -> dict:
    capital = grab(r"capital of {N} USD", text)
    fee_yield = grab(r"fee-yield ratio {N}", text)
    il_ratio = grab(r"impermanent-loss ratio {N}", text)
    coverage = grab(r"hedge covers {N} of that loss", text)
    hedge_cost_ratio = grab(r"costs {N} of capital", text)
    risk_limit = grab(r"risk limit of {N} USD", text)

    # Checkpoint: covered impermanent loss as a ratio of position capital.
    covered_ratio = coverage * il_ratio

    fee_income = capital * fee_yield
    unhedged_loss = capital * il_ratio  # exact unhedged (impermanent) loss in USD

    if unhedged_loss > risk_limit:  # strictly exceeds -> activate the hedge
        covered_loss = capital * covered_ratio
        hedge_cost = capital * hedge_cost_ratio
        net = fee_income - unhedged_loss + covered_loss - hedge_cost
    else:  # leave unhedged, pay no hedge cost
        net = fee_income - unhedged_loss

    return {
        "final": Fraction(net),
        "slots": {"covered_loss_ratio_checkpoint": Fraction(covered_ratio)},
    }
