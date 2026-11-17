from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.defi.staking_return.basic.v1"


def solve(text: str, q: dict) -> dict:
    stake = grab(r"stake is (?:USD\s*)?{N}", text)
    y = grab(r"annual yield is {N} percent", text) / 100
    return {"final": stake * y, "slots": {"yield_ratio_trace": y}}
