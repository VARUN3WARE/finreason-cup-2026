from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.div_policies.dividend_stock_plus_growth.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    old_shares = grab(r"[Ss]hares before the stock dividend (?:are|is) {N}", text)
    sd = grab(r"stock-dividend rate is {N} percent", text) / 100
    last = grab(r"last year's cash dividend per share was (?:USD )?{N}", text)
    g = grab(r"cash-DPS growth rate is {N} percent", text) / 100
    new_shares = old_shares * (1 + sd)  # kept exact (may be fractional), as the text instructs
    new_dps = last * (1 + g)
    return {"final": new_shares * new_dps, "slots": {"trace_1": new_shares, "trace_2": new_dps}}
