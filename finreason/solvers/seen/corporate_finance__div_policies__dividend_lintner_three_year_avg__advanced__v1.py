from fractions import Fraction

from finreason.nums import grab_all, grab

TEMPLATE_ID = "fp.corporate_finance.div_policies.dividend_lintner_three_year_avg.advanced.v1"


def solve(text: str, q: dict) -> dict:
    e1, e2, e3 = grab_all(r"three annual EPS observations are (?:USD )?{N},\s*{N},?\s*and\s*{N}", text)
    payout = grab(r"target payout ratio is {N} percent", text) / 100
    last = grab(r"last year's dividend per share was (?:USD )?{N}", text)
    speed = grab(r"adjustment speed is {N} percent", text) / 100
    shares = grab(r"shares outstanding (?:are|is) {N}", text)
    avg = (e1 + e2 + e3) / 3
    target = avg * payout
    new_dps = last + speed * (target - last)
    return {"final": new_dps * shares, "slots": {"trace_1": avg, "trace_2": new_dps}}
