from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.sustainability_reporting.energy_cost_savings.basic.v1"


def solve(text: str, q: dict) -> dict:
    expenditure = grab(r"annual energy expenditure of {N} USD", text)
    ratio = grab(r"reduced it by {N} percent", text) / 100
    return {"final": expenditure * ratio, "slots": {"reduction_ratio_trace": ratio}}
