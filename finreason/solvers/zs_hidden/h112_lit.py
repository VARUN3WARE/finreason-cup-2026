"""Hidden cluster h112 -- DeFi liquidity position with an optional, threshold-activated IL hedge.

Literal transcription lens: every sentence of the question becomes a named variable or rule,
in the order the text states them. Exact Fractions throughout; no rounding inside.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h112"


def solve(text: str, q: dict) -> dict:
    # S1: "Over one common annual period, a DeFi liquidity position has capital of C USD,
    #      earns fee-yield ratio f, and incurs impermanent-loss ratio L."
    capital = grab(r"has capital of {N} USD", text)
    fee_yield_ratio = grab(r"earns fee-yield ratio {N}", text)
    impermanent_loss_ratio = grab(r"incurs impermanent-loss ratio {N}", text)
    fee_income = capital * fee_yield_ratio                      # USD earned over the period
    impermanent_loss = capital * impermanent_loss_ratio         # USD lost over the period (unhedged)

    # S2: "An optional hedge covers h of that loss and, only when activated, costs k of capital."
    hedge_coverage = grab(r"hedge covers {N} of that loss", text)
    hedge_cost_ratio = grab(r"costs {N} of capital", text)
    covered_loss = hedge_coverage * impermanent_loss            # USD of IL the hedge covers
    covered_loss_ratio = covered_loss / capital                 # = h * L, ratio of position capital
    hedge_cost = hedge_cost_ratio * capital                     # USD, paid only when activated

    # S3: "If the exact unhedged loss strictly exceeds the risk limit of R USD, activate the hedge;
    #      otherwise leave the position unhedged and pay no hedge cost."
    risk_limit = grab(r"risk limit of {N} USD", text)
    unhedged_loss = impermanent_loss                            # exact, unrounded
    activate_hedge = unhedged_loss > risk_limit                 # strictly greater

    # S4: "Return the selected net profit or loss in USD, excluding return of the original capital."
    if activate_hedge:
        net_profit_or_loss = fee_income - impermanent_loss + covered_loss - hedge_cost
    else:
        net_profit_or_loss = fee_income - impermanent_loss      # no coverage, no hedge cost

    return {
        "final": Fraction(net_profit_or_loss),
        "slots": {
            "covered_loss_ratio_checkpoint": Fraction(covered_loss_ratio),
        },
    }
