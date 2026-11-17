from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.robo_advisors.equity_rebalance_trade.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    equity = grab(r"holds {N} USD in equities", text)
    bonds = grab(r"USD in equities and {N} USD in bonds", text)
    target = grab(r"target equity allocation is {N} percent", text) / 100
    total = equity + bonds
    target_equity = total * target
    trade = target_equity - equity  # positive = buy, negative = sell
    return {"final": trade, "slots": {"total_value_trace": total, "target_equity_trace": target_equity}}
