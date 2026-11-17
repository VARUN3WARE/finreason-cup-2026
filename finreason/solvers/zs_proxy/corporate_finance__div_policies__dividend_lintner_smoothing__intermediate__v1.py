from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.div_policies.dividend_lintner_smoothing.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    eps = grab(r"[Ee]arnings per share (?:are|is|of) {N}", text)
    payout = grab(r"target payout ratio is {N} percent", text) / 100
    last_dps = grab(r"last year's dividend per share (?:was|is|of) {N}", text)
    speed = grab(r"adjustment speed is {N} percent", text) / 100
    shares = grab(r"shares outstanding (?:are|is|of) {N}", text)
    target = eps * payout
    new_dps = last_dps + speed * (target - last_dps)
    return {"final": new_dps * shares, "slots": {"trace_1": target, "trace_2": new_dps}}
