from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.balance_sheets.business_combination.advanced.v1"


def solve(text: str, q: dict) -> dict:
    cash = grab(r"acquirer pays {N} USD", text)
    shares = grab(r"issues {N} shares", text)
    price = grab(r"valued at {N} USD per share", text)
    land = grab(r"land {N} USD", text)
    inventory = grab(r"inventory {N} USD", text)
    patents = grab(r"patents {N} USD", text)
    borrowings = grab(r"borrowings {N} USD", text)
    ap = grab(r"accounts payable {N} USD", text)

    consideration = cash + shares * price
    assets = land + inventory + patents
    net_assets = assets - borrowings - ap
    # Goodwill is NOT floored at zero: gold keeps negative values (bargain purchase) as-is.
    goodwill = consideration - net_assets
    return {"final": goodwill, "slots": {"trace_1": consideration, "trace_2": assets, "trace_3": net_assets}}
