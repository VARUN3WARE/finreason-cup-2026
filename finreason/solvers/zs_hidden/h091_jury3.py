from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h091"


def solve(text: str, q: dict) -> dict:
    ebitda = grab(r"verified recurring EBITDA is {N}", text)
    savings = grab(r"not already included in that amount are {N}", text)
    m_base = grab(r"applies valuation multiple {N}", text)
    fall = grab(r"recurring EBITDA falls by {N}", text)
    m_attr = grab(r"multiple compresses to {N}", text)
    p_attr = grab(r"that state occurs with probability {N}", text)
    tax_gross = grab(r"gross tax exposure of {N} crystallizes", text)
    p_tax = grab(r"crystallizes with probability {N}", text)
    ins = grab(r"insurance recovers fraction {N}", text)

    # Target-controlled, confirmed, not-already-included run-rate savings qualify as an
    # add-back, so the valued (base-case) recurring EBITDA is verified + savings.
    base_ebitda = ebitda + savings
    attr_ebitda = base_ebitda - fall

    ev_base = m_base * base_ebitda
    ev_attr = m_attr * attr_ebitda
    exp_customer = p_attr * (ev_base - ev_attr)

    uninsured = tax_gross * (1 - ins)
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
