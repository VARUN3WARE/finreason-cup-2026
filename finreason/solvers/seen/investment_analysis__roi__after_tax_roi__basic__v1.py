from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.roi.after_tax_roi.basic.v1"


def solve(text: str, q: dict) -> dict:
    inv = grab(r"investment of USD {N}", text)
    gross = grab(r"gross profit of USD {N}", text)
    tax = grab(r"tax rate of {N} percent", text)
    retention = 1 - tax / 100
    after_tax = gross * retention
    roi = after_tax / inv * 100
    return {
        "final": roi,
        "slots": {"retention_rate_trace": retention, "after_tax_profit_trace": after_tax},
    }
