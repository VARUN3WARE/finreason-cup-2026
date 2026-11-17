from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.profitratio.gross_profit_margin.basic.v1"


def solve(text: str, q: dict) -> dict:
    revenue = grab(r"Revenue is {N} USD", text)
    cogs = grab(r"cost of goods sold is {N} USD", text)
    gross_profit = revenue - cogs
    ratio = gross_profit / revenue
    return {
        "final": ratio * 100,
        "slots": {"trace_1": gross_profit, "trace_2": ratio},
    }
