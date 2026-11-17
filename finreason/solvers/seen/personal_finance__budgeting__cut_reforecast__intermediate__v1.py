from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.budgeting.cut_reforecast.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    baseline = grab(r"Baseline budget in USD is {N}", text)
    ratio = grab(r"Cut ratio is {N}", text)
    recovery = grab(r"Recovery amount in USD is {N}", text)
    cut = baseline * ratio
    post_cut = baseline - cut
    reforecast = post_cut + recovery
    return {"final": reforecast, "slots": {"cut_amount_usd": cut}}
