from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.deal_structure.leveraged_buyout_adjusted_shares_calculation.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    total = grab(r"Total deal value is {N} USD", text)
    debt_pct = grab(r"debt financing is {N} percent", text)
    price = grab(r"valued at {N} USD per share", text)
    threshold = grab(r"strictly below {N} USD per share", text)
    mult = grab(r"adjusted shares equal basic shares times {N}", text)

    equity = total * (1 - debt_pct / 100)
    basic = equity / price
    adjusted = basic * mult if price < threshold else basic
    return {"final": adjusted, "slots": {"trace_1": equity, "trace_2": basic}}
