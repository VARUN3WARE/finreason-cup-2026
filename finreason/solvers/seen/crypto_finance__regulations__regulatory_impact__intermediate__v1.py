from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.regulations.regulatory_impact.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    fee = grab(r"current fee is {N} USD", text)
    ratio = grab(r"disclosed increase is {N} percent", text) / 100
    supplement = grab(r"filing supplement of {N} USD", text)
    variable = fee * ratio
    return {
        "final": variable + supplement,
        "slots": {"increase_ratio_trace": ratio, "percentage_increase_trace": variable},
    }
