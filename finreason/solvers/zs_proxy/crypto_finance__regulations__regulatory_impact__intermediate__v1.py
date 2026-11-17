from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.regulations.regulatory_impact.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    fee = grab(r"current fee is {N} USD", text)
    inc_pct = grab(r"disclosed increase is {N} percent", text)
    supplement = grab(r"filing supplement of {N} USD", text)
    ratio = inc_pct / 100
    variable = fee * ratio
    return {
        "final": variable + supplement,
        "slots": {"increase_ratio_trace": ratio, "percentage_increase_trace": variable},
    }
