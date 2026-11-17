from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.div_policies.dividend_lintner_smoothing.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    eps = grab(r"[Ee]arnings per share (?:are|is) (?:USD )?{N}", text)
    payout = grab(r"target payout ratio is {N} percent", text) / 100
    last = grab(r"last year's dividend per share was (?:USD )?{N}", text)
    speed = grab(r"adjustment speed is {N} percent", text) / 100
    shares = grab(r"shares outstanding (?:are|is) {N}", text)
    target = eps * payout
    new_dps = last + speed * (target - last)
    return {"final": new_dps * shares, "slots": {"trace_1": target, "trace_2": new_dps}}
