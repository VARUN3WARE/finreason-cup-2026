from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.robo_advisors.one_year_after_fee.basic.v1"


def solve(text: str, q: dict) -> dict:
    start = grab(r"starts at {N} USD", text)
    ret = grab(r"one-year gross return of {N} percent", text) / 100
    fee = grab(r"then pays {N} percent of ending assets", text) / 100
    growth = 1 + ret
    before = start * growth
    after_fee = before * (1 - fee)
    return {"final": after_fee, "slots": {"growth_multiple_trace": growth, "before_fee_trace": before}}
