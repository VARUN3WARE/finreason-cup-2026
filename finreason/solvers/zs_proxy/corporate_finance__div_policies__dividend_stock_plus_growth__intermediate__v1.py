from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.div_policies.dividend_stock_plus_growth.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    old_shares = grab(r"[Ss]hares before the stock dividend (?:are|is|of) {N}", text)
    sd_rate = grab(r"stock-dividend rate is {N} percent", text) / 100
    last_dps = grab(r"last year's cash dividend per share (?:was|is|of) {N}", text)
    g = grab(r"cash-DPS growth rate is {N} percent", text) / 100
    new_shares = old_shares * (1 + sd_rate)
    new_dps = last_dps * (1 + g)
    return {"final": new_shares * new_dps, "slots": {"trace_1": new_shares, "trace_2": new_dps}}
