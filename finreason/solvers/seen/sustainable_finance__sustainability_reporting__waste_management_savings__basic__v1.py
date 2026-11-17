from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.sustainability_reporting.waste_management_savings.basic.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"Annual waste-management cost is {N} USD", text)
    ratio = grab(r"reduce that cost by {N} percent", text) / 100
    return {"final": cost * ratio, "slots": {"reduction_ratio_trace": ratio}}
