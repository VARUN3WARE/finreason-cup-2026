from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.defi.liquidity_pool_reward.intermediate.v1"

PCT = r"\s*(?:percent|%)"


def solve(text: str, q: dict) -> dict:
    total = grab(r"pool generated (?:USD\s*)?{N}", text)
    reserve = grab(r"withholds {N}" + PCT, text) / 100
    share = grab(r"pays a provider {N}" + PCT, text) / 100
    dist_ratio = 1 - reserve
    dist_fees = total * dist_ratio
    reward = dist_fees * share
    return {
        "final": reward,
        "slots": {
            "distributable_ratio_trace": dist_ratio,
            "distributable_fees_trace": dist_fees,
        },
    }
