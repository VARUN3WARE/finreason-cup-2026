from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.profitratio.dual_margin_gap.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    revenue = grab(r"Revenue is {N} USD", text)
    cogs = grab(r"cost of goods sold is {N} USD", text)
    net_income = grab(r"net income is {N} USD", text)
    gross_margin_pct = (revenue - cogs) / revenue * 100
    net_margin_pct = net_income / revenue * 100
    # Gap in percentage points: gross margin minus net margin (sign preserved).
    return {
        "final": gross_margin_pct - net_margin_pct,
        "slots": {"trace_1": gross_margin_pct, "trace_2": net_margin_pct},
    }
