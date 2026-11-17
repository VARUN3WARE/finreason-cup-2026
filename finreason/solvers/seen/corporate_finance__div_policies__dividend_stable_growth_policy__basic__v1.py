from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.div_policies.dividend_stable_growth_policy.basic.v1"


def solve(text: str, q: dict) -> dict:
    last = grab(r"[Ll]ast year's dividend per share was (?:USD )?{N}", text)
    g = grab(r"stable growth rate is {N} percent", text) / 100
    shares = grab(r"shares outstanding (?:are|is) {N}", text)
    gross = 1 + g
    new_dps = last * gross
    return {"final": new_dps * shares, "slots": {"trace_1": gross, "trace_2": new_dps}}
