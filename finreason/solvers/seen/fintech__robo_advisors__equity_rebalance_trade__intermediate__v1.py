from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.robo_advisors.equity_rebalance_trade.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    equity = grab(r"holds {N}\s*[A-Za-z]*\s*in equities", text)
    bonds = grab(r"and {N}\s*[A-Za-z]*\s*in bonds", text)
    target = grab(r"target equity allocation is {N}\s*percent", text) / 100
    total = equity + bonds
    target_equity = total * target
    # Signed trade: positive = buy equities, negative = sell equities.
    trade = target_equity - equity
    return {
        "final": trade,
        "slots": {"total_value_trace": total, "target_equity_trace": target_equity},
    }
