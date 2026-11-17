from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.profitratio.target_net_margin.advanced.v1"


def solve(text: str, q: dict) -> dict:
    revenue = grab(r"Revenue is {N} USD", text)
    net_income = grab(r"current net income is {N} USD", text)
    target_pct = grab(r"target net profit margin is {N} percent", text)
    current_margin_pct = net_income / revenue * 100
    required_ni = revenue * target_pct / 100
    # Minimum additional net income, floored at zero.
    additional = max(required_ni - net_income, Fraction(0))
    return {
        "final": additional,
        "slots": {"trace_1": current_margin_pct, "trace_2": required_ni},
    }
