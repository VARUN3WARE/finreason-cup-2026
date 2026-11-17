"""h091: customer-attrition expected value loss vs insured tax exposure expected loss.

Chain (exact Fractions, nothing rounded internally):
  base valuation EBITDA      = verified recurring EBITDA + target-controlled confirmed run-rate savings
                               (savings are confirmed, target-controlled and NOT already included -> add once)
  base EV                    = base valuation EBITDA * base multiple
  attrition recurring EBITDA = verified recurring EBITDA - fall                       (checkpoint 1)
  attrition valuation EBITDA = attrition recurring EBITDA + savings (target-controlled savings are unaffected
                               by customer attrition)
  attrition EV               = attrition valuation EBITDA * compressed multiple
  expected customer loss     = p_attrition * (base EV - attrition EV)
  uninsured exposure         = gross exposure * (1 - insurance recovery fraction)     (checkpoint 2)
  expected tax loss          = p_crystallize * uninsured exposure
  compare exactly.
"""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h091"


def solve(text: str, q: dict) -> dict:
    recurring = grab(r"verified recurring EBITDA is {N}", text)
    savings = grab(r"run-rate savings not already included in that amount are {N}", text)
    m_base = grab(r"base case applies valuation multiple {N}", text)
    fall = grab(r"recurring EBITDA falls by {N}", text)
    m_attr = grab(r"valuation multiple compresses to {N}", text)
    p_attr = grab(r"that state occurs with probability {N}", text)
    gross = grab(r"gross tax exposure of {N}", text)
    p_tax = grab(r"crystallizes with probability {N}", text)
    recovery = grab(r"insurance recovers fraction {N}", text)

    base_ebitda = recurring + savings
    base_ev = base_ebitda * m_base

    attr_recurring = recurring - fall
    attr_ebitda = attr_recurring + savings
    attr_ev = attr_ebitda * m_attr

    exp_customer = p_attr * (base_ev - attr_ev)

    uninsured = gross * (1 - recovery)
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
            "attrition_case_ebitda_checkpoint": Fraction(attr_recurring),
            "uninsured_tax_exposure_checkpoint": Fraction(uninsured),
        },
    }
