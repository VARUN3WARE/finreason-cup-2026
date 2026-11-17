from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.defi.multi_factor_portfolio.advanced.v1"

PCT = r"\s*(?:percent|%)"


def solve(text: str, q: dict) -> dict:
    value = grab(r"portfolio is valued at (?:USD\s*)?{N}", text)
    share = grab(r"staking allocation is {N}" + PCT, text) / 100
    boost = grab(r"yield boost is {N}" + PCT, text) / 100
    fee = grab(r"swap-fee effect is {N}" + PCT, text) / 100
    staking_impact = value * share * boost
    fee_impact = value * fee  # signed: negative = loss
    return {
        "final": staking_impact + fee_impact,
        "slots": {
            "staking_impact_trace": staking_impact,
            "fee_impact_trace": fee_impact,
        },
    }
