from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h091"

CUSTOMER = "Customer attrition loss is larger"
TAX = "Tax exposure loss is larger"
EQUAL = "Expected losses are equal"


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
    # figure are a valid add-back: base-case EBITDA = verified + savings.
    base_ebitda = recurring + savings
    attr_ebitda = base_ebitda - fall          # attrition-case EBITDA (savings unaffected)
    base_ev = base_ebitda * base_mult
    attr_ev = attr_ebitda * attr_mult
    customer_loss = p_attr * (base_ev - attr_ev)

    uninsured = gross_tax * (1 - recovery)
    tax_loss = p_tax * uninsured

    if customer_loss > tax_loss:
        final = CUSTOMER
    elif tax_loss > customer_loss:
        final = TAX
    else:
        final = EQUAL

    return {
        "final": final,
        "slots": {
            "attrition_case_ebitda_checkpoint": Fraction(attr_ebitda),
            "uninsured_tax_exposure_checkpoint": Fraction(uninsured),
        },
    }
