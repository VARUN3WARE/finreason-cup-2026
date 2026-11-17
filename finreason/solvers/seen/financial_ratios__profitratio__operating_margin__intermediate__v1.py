from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.profitratio.operating_margin.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    revenue = grab(r"Revenue is {N} USD", text)
    cogs = grab(r"cost of goods sold is {N} USD", text)
    opex = grab(r"operating expenses excluding cost of goods sold are {N} USD", text)
    gross_profit = revenue - cogs
    operating_profit = gross_profit - opex
    return {
        "final": operating_profit / revenue * 100,
        "slots": {"trace_1": gross_profit, "trace_2": operating_profit},
    }
