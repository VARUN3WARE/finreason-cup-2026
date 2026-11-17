from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.roi.property_roi.basic.v1"


def solve(text: str, q: dict) -> dict:
    purchase = grab(r"purchased for USD {N}", text)
    renovation = grab(r"renovated for USD {N}", text)
    sale = grab(r"sold for USD {N}", text)
    total = purchase + renovation
    profit = sale - total
    roi = profit / total * 100
    return {
        "final": roi,
        "slots": {"total_investment_trace": total, "investment_profit_trace": profit},
    }
