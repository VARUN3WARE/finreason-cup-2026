"""h091 (final arbiter; adopts adjudicator A) -- customer-attrition expected value loss vs insured tax exposure expected loss.

Literal transcription, sentence by sentence:
  1. "verified recurring EBITDA is R and target-controlled confirmed run-rate savings not already
     included in that amount are S"  -> base-case valuation EBITDA = R + S (target-controlled,
     confirmed and not double counted, so the savings qualify for the valuation EBITDA).
  2. "The base case applies valuation multiple M0"  -> EV_base = (R + S) * M0.
  3. "In a customer-attrition state, recurring EBITDA falls by D and the valuation multiple
     compresses to M1; that state occurs with probability p"  -> recurring EBITDA (attrition)
     = R - D; the target-controlled savings are unaffected by customer attrition, so
     EV_attr = (R - D + S) * M1.
  4. expected customer value loss = p * (EV_base - EV_attr).
  5. "gross tax exposure of G crystallizes with probability q, and insurance recovers fraction f
     if it crystallizes"  -> uninsured exposure = G * (1 - f).
  6. expected tax loss = q * uninsured exposure.
  7. Compare exact unrounded expected losses.

Arbiter ruling on attrition_case_ebitda_checkpoint: the text names only R as "verified recurring
EBITDA", describes S separately as savings "not already included in that amount", and the attrition
sentence's subject is "recurring EBITDA falls by D". The slot asks for "recurring EBITDA in the
customer-attrition state", so it reports R - D (savings are added back only for the EV).
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h091"


def solve(text: str, q: dict) -> dict:
    # Sentence 1
    recurring_ebitda = grab(r"verified recurring EBITDA is {N}", text)
    savings = grab(r"run-rate savings not already included in that amount are {N}", text)
    # Sentence 2
    base_multiple = grab(r"base case applies valuation multiple {N}", text)
    # Sentence 3
    fall = grab(r"recurring EBITDA falls by {N}", text)
    attr_multiple = grab(r"valuation multiple compresses to {N}", text)
    p_attr = grab(r"that state occurs with probability {N}", text)

    base_ebitda = recurring_ebitda + savings
    ev_base = base_ebitda * base_multiple

    attr_recurring_ebitda = recurring_ebitda - fall
    attr_ebitda = attr_recurring_ebitda + savings
    ev_attr = attr_ebitda * attr_multiple

    # Sentence 4
    expected_customer_loss = p_attr * (ev_base - ev_attr)

    # Sentence 5
    gross_tax = grab(r"gross tax exposure of {N}", text)
    q_tax = grab(r"crystallizes with probability {N}", text)
    recovery = grab(r"insurance recovers fraction {N}", text)
    uninsured = gross_tax * (Fraction(1) - recovery)

    # Sentence 6
    expected_tax_loss = q_tax * uninsured

    # Sentence 7
    if expected_customer_loss > expected_tax_loss:
        final = "Customer attrition loss is larger"
    elif expected_tax_loss > expected_customer_loss:
        final = "Tax exposure loss is larger"
    else:
        final = "Expected losses are equal"

    return {
        "final": final,
        "slots": {
            "attrition_case_ebitda_checkpoint": attr_recurring_ebitda,
            "uninsured_tax_exposure_checkpoint": uninsured,
        },
    }
