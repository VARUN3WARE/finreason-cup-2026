from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.div_policies.dividend_stable_growth_policy.basic.v1"


def solve(text: str, q: dict) -> dict:
    last_dps = grab(r"[Ll]ast year's dividend per share (?:was|is|of) {N}", text)
    g = grab(r"growth rate is {N} percent", text) / 100
    shares = grab(r"shares outstanding (?:are|is|of) {N}", text)
    one_g = 1 + g
    new_dps = last_dps * one_g
    return {"final": new_dps * shares, "slots": {"trace_1": one_g, "trace_2": new_dps}}
