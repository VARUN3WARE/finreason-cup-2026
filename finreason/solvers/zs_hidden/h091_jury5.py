"""h091 -- customer-attrition value loss vs uninsured tax exposure (juror 5).

Reading of the text:
  * Valuation EBITDA (base case) = verified recurring EBITDA + target-controlled
    confirmed run-rate savings "not already included in that amount".  The
    qualifiers (target-controlled, confirmed, run-rate, not already included)
    are the diligence criteria for adding savings to the valuation base, so the
    savings are added once (no double count).
  * EV_base = valuation EBITDA x base multiple.
  * Attrition state: recurring EBITDA falls by D and the multiple compresses to m.
    Attrition-state recurring EBITDA = valuation EBITDA - D (the savings are
    target-controlled cost savings and remain in place).  EV_attr = that x m.
  * Expected customer value loss = p_attr x (EV_base - EV_attr).
  * Uninsured tax exposure = gross exposure x (1 - recovery fraction).
  * Expected tax loss = p_crystallise x uninsured exposure.
  * Comparison on exact unrounded values; equality -> "Expected losses are equal".
Units: all amounts are usd_million as given; nothing is rounded before use.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h091"


def solve(text: str, q: dict) -> dict:
    ebitda = grab(r"verified recurring EBITDA is {N}", text)
    savings = grab(r"run-rate savings not already included in that amount are {N}", text)
    base_mult = grab(r"base case applies valuation multiple {N}", text)
    drop = grab(r"recurring EBITDA falls by {N}", text)
    attr_mult = grab(r"valuation multiple compresses to {N}", text)
    p_attr = grab(r"state occurs with probability {N}", text)
    gross_tax = grab(r"gross tax exposure of {N}", text)
    p_tax = grab(r"crystallizes with probability {N}", text)
    recovery = grab(r"insurance recovers fraction {N}", text)

    base_ebitda = ebitda + savings
    attr_ebitda = base_ebitda - drop

    ev_base = base_ebitda * base_mult
    ev_attr = attr_ebitda * attr_mult
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
