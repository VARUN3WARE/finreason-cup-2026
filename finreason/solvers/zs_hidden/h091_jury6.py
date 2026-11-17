"""h091 -- expected customer-attrition value loss vs expected uninsured tax loss.

Reading of the text (juror 6):
  * "verified recurring EBITDA is V and target-controlled confirmed run-rate savings
    not already included in that amount are S": confirmed, target-controlled savings
    qualify for inclusion, and "not already included" says they must be ADDED, so the
    recurring EBITDA valued in the base case is V + S.
  * base-case EV = (V + S) * M_base.
  * attrition state: recurring EBITDA falls by D (from the valued figure V + S) and the
    multiple compresses to M_attr, so attrition EBITDA = V + S - D and
    attrition EV = (V + S - D) * M_attr.
  * expected customer value loss = p_attr * (EV_base - EV_attr).
  * uninsured tax exposure = G * (1 - r); expected tax loss = p_tax * G * (1 - r).
  * compare exact unrounded expected losses; equality -> "Expected losses are equal".
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h091"


def solve(text: str, q: dict) -> dict:
    verified = grab(r"verified recurring EBITDA is {N}", text)
    savings = grab(r"not already included in that amount are {N}", text)
    m_base = grab(r"base case applies valuation multiple {N}", text)
    drop = grab(r"recurring EBITDA falls by {N}", text)
    m_attr = grab(r"valuation multiple compresses to {N}", text)
    p_attr = grab(r"state occurs with probability {N}", text)
    gross_tax = grab(r"gross tax exposure of {N}", text)
    p_tax = grab(r"crystallizes with probability {N}", text)
    recovery = grab(r"insurance recovers fraction {N}", text)

    base_ebitda = verified + savings
    attr_ebitda = base_ebitda - drop

    ev_base = base_ebitda * m_base
    ev_attr = attr_ebitda * m_attr
    exp_customer_loss = p_attr * (ev_base - ev_attr)

    uninsured = gross_tax * (Fraction(1) - recovery)
    exp_tax_loss = p_tax * uninsured

    if exp_customer_loss > exp_tax_loss:
        final = "Customer attrition loss is larger"
    elif exp_tax_loss > exp_customer_loss:
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
