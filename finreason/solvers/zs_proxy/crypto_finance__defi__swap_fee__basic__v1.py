from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.defi.swap_fee.basic.v1"

PCT = r"\s*(?:percent|%)"


def solve(text: str, q: dict) -> dict:
    value = grab(r"swap value is (?:USD\s*)?{N}", text)
    rate = grab(r"fee rate is {N}" + PCT, text) / 100
    return {"final": value * rate, "slots": {"fee_ratio_trace": rate}}
