from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.defi.liquidity_pool_reward.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    fees = grab(r"liquidity pool generated (?:USD\s*)?{N}", text)
    reserve = grab(r"withholds {N} percent", text) / 100
    share = grab(r"pays (?:a|the) provider {N} percent", text) / 100
    dist_ratio = 1 - reserve
    dist_fees = fees * dist_ratio
    reward = dist_fees * share
    return {
        "final": reward,
        "slots": {"distributable_ratio_trace": dist_ratio, "distributable_fees_trace": dist_fees},
    }
