from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h091"


def solve(text: str, q: dict) -> dict:
    recurring = grab(r"verified recurring EBITDA is {N}", text)
    savings = grab(r"run-rate savings not already included in that amount are {N}", text)
    base_mult = grab(r"base case applies valuation multiple {N}", text)
    fall = grab(r"recurring EBITDA falls by {N}", text)
    attr_mult = grab(r"multiple compresses to {N}", text)
    p_attr = grab(r"that state occurs with probability {N}", text)
    gross_tax = grab(r"gross tax exposure of {N}", text)
    p_tax = grab(r"crystallizes with probability {N}", text)
    recovery = grab(r"insurance recovers fraction {N}", text)

    # Target-controlled, confirmed run-rate savings not already in the verified
    # figure are added to form the valuation EBITDA (no double count).
    base_ebitda = recurring + savings
    attr_ebitda = base_ebitda - fall

    base_ev = base_ebitda * base_mult
    attr_ev = attr_ebitda * attr_mult
    exp_customer = p_attr * (base_ev - attr_ev)

    uninsured = gross_tax * (1 - recovery)
    exp_tax = p_tax * uninsured

    if exp_customer > exp_tax:
        final = "Customer attrition loss is larger"
    elif exp_tax > exp_customer:
        final = "Tax exposure loss is larger"
    else:
        final = "Expected losses are equal"

    return {
        "final": final,
        "slots": {
            "attrition_case_ebitda_checkpoint": attr_ebitda,
            "uninsured_tax_exposure_checkpoint": uninsured,
        },
    }
