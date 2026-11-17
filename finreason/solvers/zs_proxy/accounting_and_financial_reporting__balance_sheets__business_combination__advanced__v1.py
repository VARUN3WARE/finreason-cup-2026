import re
from fractions import Fraction
from finreason.nums import grab, NUMBER, F

TEMPLATE_ID = "fp.accounting_and_financial_reporting.balance_sheets.business_combination.advanced.v1"


def _sum_usd(segment: str) -> Fraction:
    vals = [F(m.group(1)) for m in re.finditer(rf"({NUMBER})\s*USD", segment)]
    if not vals:
        raise ValueError("no USD amounts in segment")
    return sum(vals, Fraction(0))


def solve(text: str, q: dict) -> dict:
    cash = grab(r"pays {N} USD", text)
    shares = grab(r"issues {N} shares", text)
    price = grab(r"valued at {N} USD per share", text)
    consideration = cash + shares * price

    m = re.search(r"identifiable assets are (.*?); assumed liabilities are (.*?)\.\s", text, flags=re.S)
    if m is None:
        raise ValueError("asset/liability segments not found")
    assets = _sum_usd(m.group(1))
    liabilities = _sum_usd(m.group(2))
    net_assets = assets - liabilities

    goodwill = consideration - net_assets  # sign preserved (negative = bargain purchase)
    return {
        "final": goodwill,
        "slots": {"trace_1": consideration, "trace_2": assets, "trace_3": net_assets},
    }
