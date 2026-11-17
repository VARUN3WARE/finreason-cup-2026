from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.div_policies.dividend_target_payout_policy.basic.v1"


def solve(text: str, q: dict) -> dict:
    eps = grab(r"earnings per share (?:are|is) (?:USD )?{N}", text)
    payout = grab(r"target payout ratio is {N} percent", text) / 100
    shares = grab(r"shares outstanding (?:are|is) {N}", text)
    dps = eps * payout
    return {"final": dps * shares, "slots": {"trace_1": dps}}
