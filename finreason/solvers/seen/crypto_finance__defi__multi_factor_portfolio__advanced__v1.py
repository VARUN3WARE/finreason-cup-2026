from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.defi.multi_factor_portfolio.advanced.v1"


def solve(text: str, q: dict) -> dict:
    value = grab(r"portfolio is valued at (?:USD\s*)?{N}", text)
    stake_share = grab(r"staking allocation is {N} percent", text) / 100
    boost = grab(r"yield boost is {N} percent", text) / 100
    fee_effect = grab(r"swap-fee effect is \+?{N} percent", text) / 100  # signed; negative = loss
    staking_impact = value * stake_share * boost
    fee_impact = value * fee_effect
    return {
        "final": staking_impact + fee_impact,
        "slots": {"staking_impact_trace": staking_impact, "fee_impact_trace": fee_impact},
    }
