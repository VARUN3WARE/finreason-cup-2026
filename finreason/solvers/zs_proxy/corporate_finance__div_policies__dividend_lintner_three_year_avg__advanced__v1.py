from fractions import Fraction
from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.corporate_finance.div_policies.dividend_lintner_three_year_avg.advanced.v1"


def solve(text: str, q: dict) -> dict:
    eps_obs = grab_all(r"EPS observations are {N},\s*{N},?\s*and\s*{N}", text)
    assert len(eps_obs) == 3
    payout = grab(r"target payout ratio is {N} percent", text) / 100
    last_dps = grab(r"last year's dividend per share (?:was|is|of) {N}", text)
    speed = grab(r"adjustment speed is {N} percent", text) / 100
    shares = grab(r"shares outstanding (?:are|is|of) {N}", text)
    avg_eps = sum(eps_obs, Fraction(0)) / 3
    target = avg_eps * payout
    new_dps = last_dps + speed * (target - last_dps)
    return {"final": new_dps * shares, "slots": {"trace_1": avg_eps, "trace_2": new_dps}}
