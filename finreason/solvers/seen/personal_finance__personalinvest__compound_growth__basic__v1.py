from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.personalinvest.compound_growth.basic.v1"


def solve(text: str, q: dict) -> dict:
    principal = grab(r"Principal in USD is {N}", text)
    r = grab(r"return ratio per period is {N}", text)
    n = grab(r"period count is {N}", text)
    if n.denominator != 1:
        raise ValueError(f"non-integer period count {n}")
    factor = 1 + r
    multiple = factor ** int(n)
    fv = principal * multiple
    return {
        "final": fv,
        "slots": {"period_growth_factor": factor, "compounded_multiple": multiple},
    }
