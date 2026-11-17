from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.defi.swap_fee.basic.v1"


def solve(text: str, q: dict) -> dict:
    swap = grab(r"swap value is (?:USD\s*)?{N}", text)
    rate = grab(r"fee rate is {N} percent", text) / 100
    return {"final": swap * rate, "slots": {"fee_ratio_trace": rate}}
