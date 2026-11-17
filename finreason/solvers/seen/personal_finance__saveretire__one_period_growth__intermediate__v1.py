from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.saveretire.one_period_growth.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    savings = grab(r"Starting savings in USD (?:are|is) {N}", text)
    contribution = grab(r"End-of-period contribution in USD (?:is|are) {N}", text)
    ratio = grab(r"One-period return ratio (?:is|are) {N}", text)
    # Per the stated policy, the contribution is added before the return is applied.
    pre = savings + contribution
    ret = pre * ratio
    ending = pre + ret
    return {
        "final": ending,
        "slots": {"pre_return_balance_usd": pre, "return_amount_usd": ret},
    }
