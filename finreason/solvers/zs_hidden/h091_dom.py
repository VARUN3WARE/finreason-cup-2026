# FINANCE MODEL (h091) -- customer-attrition value loss vs. uninsured tax exposure
#
# Units: every monetary figure is USD million (EBITDA, EV, tax exposure); multiples are plain ratios;
# probabilities / insurance fraction are decimals in [0, 1] (NOT percent).
#
# 1. Adjusted (valuation) EBITDA.
#    Verified recurring EBITDA V is the audited base. "Target-controlled confirmed run-rate savings not
#    already included in that amount" S are the standard diligence add-back: they are confirmed, controlled
#    by the target itself (not buyer synergies) and explicitly NOT yet in V, so they are ADDED once:
#        E_base = V + S
#    Base-case enterprise value:  EV_base = E_base * M_base.
#
# 2. Customer-attrition state (probability p).
#    "Recurring EBITDA falls by D": the valuation EBITDA drops by D relative to the base-case EBITDA,
#        E_attr = E_base - D          (the add-back S stays in: it is target-controlled and confirmed, so
#                                      it does not depend on customers; reading the fall as applying to V
#                                      alone gives the same E_attr = (V - D) + S)
#    and the multiple compresses to M_attr (an absolute new multiple, "compresses to"), so
#        EV_attr = E_attr * M_attr.
#    Expected customer value loss  L_cust = p * (EV_base - EV_attr)   (as defined in the text; no floor,
#    the difference is positive here but implemented as stated).
#
# 3. Tax exposure (separate, non-overlapping, so nothing is netted against the customer loss).
#    Gross exposure G crystallizes with probability q; insurance recovers fraction r of it when it
#    crystallizes.  Uninsured exposure  U = G * (1 - r)   (conditional on crystallization).
#    Expected tax loss  L_tax = q * U.
#
# 4. Compare the exact unrounded L_cust vs L_tax:
#       L_cust > L_tax -> "Customer attrition loss is larger"
#       L_tax  > L_cust -> "Tax exposure loss is larger"
#       equal -> "Expected losses are equal"
#
# Checkpoints:
#   attrition_case_ebitda_checkpoint     = E_attr  (recurring EBITDA in the attrition state, USD million)
#   uninsured_tax_exposure_checkpoint    = U       (exposure remaining after insurance, BEFORE the
#                                                   crystallization probability, USD million)
#
# Overrides / interpretation notes: none of the text overrides standard conventions; no rounding is used
# inside the computation (everything exact Fractions).
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h091"


def solve(text: str, q: dict) -> dict:
    verified = grab(r"verified recurring EBITDA is {N}", text)
    savings = grab(r"run-rate savings not already included in that amount are {N}", text)
    m_base = grab(r"base case applies valuation multiple {N}", text)
    fall = grab(r"recurring EBITDA falls by {N}", text)
    m_attr = grab(r"multiple compresses to {N}", text)
    p_attr = grab(r"state occurs with probability {N}", text)
    gross_tax = grab(r"gross tax exposure of {N} crystallizes", text)
    q_tax = grab(r"crystallizes with probability {N}", text)
    ins = grab(r"insurance recovers fraction {N}", text)

    e_base = verified + savings
    e_attr = e_base - fall
    ev_base = e_base * m_base
    ev_attr = e_attr * m_attr
    l_cust = p_attr * (ev_base - ev_attr)

    uninsured = gross_tax * (1 - ins)
    l_tax = q_tax * uninsured

    if l_cust > l_tax:
        final = "Customer attrition loss is larger"
    elif l_tax > l_cust:
        final = "Tax exposure loss is larger"
    else:
        final = "Expected losses are equal"

    return {
        "final": final,
        "slots": {
            "attrition_case_ebitda_checkpoint": e_attr,
            "uninsured_tax_exposure_checkpoint": uninsured,
        },
    }
