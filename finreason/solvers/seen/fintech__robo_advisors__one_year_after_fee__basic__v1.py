from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.robo_advisors.one_year_after_fee.basic.v1"


def solve(text: str, q: dict) -> dict:
    start = grab(r"starts at {N}", text)
    ret = grab(r"gross return of {N}\s*percent", text) / 100
    fee = grab(r"pays {N}\s*percent of ending assets", text) / 100
    growth = 1 + ret
    before_fee = start * growth
    return {
        "final": before_fee * (1 - fee),
        "slots": {"growth_multiple_trace": growth, "before_fee_trace": before_fee},
    }
