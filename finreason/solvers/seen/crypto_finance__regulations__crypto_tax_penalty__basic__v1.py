from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.regulations.crypto_tax_penalty.basic.v1"


def solve(text: str, q: dict) -> dict:
    volume = grab(r"covered volume is {N} USD", text)
    ratio = grab(r"penalty rate is {N} percent", text) / 100
    return {"final": volume * ratio, "slots": {"penalty_ratio_trace": ratio}}
