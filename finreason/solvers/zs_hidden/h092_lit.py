"""h092 -- dual-schedule operating cash-flow reconciliation score (literal transcription).

Indirect OCF = NI + D + A - (AR increase + inventory increase + AP decrease)
               + accrued-liabilities increase + income-taxes-payable increase
Direct OCF   = receipts - non-tax operating payments - cash income taxes paid
margins      = OCF / revenue (ratios)
score        = mean(margins) - (signed difference)^2, reported in percent.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h092"


def solve(text: str, q: dict) -> dict:
    # "The indirect schedule starts with after-tax net income X,"
    net_income = grab(r"after-tax net income {N}", text)
    # "adds nonoverlapping depreciation X and amortization Y,"
    depreciation = grab(r"depreciation {N}", text)
    amortization = grab(r"depreciation {N} and amortization {N}", text, group=2)
    # "subtracts the cash uses from an increase in accounts receivable X,
    #  an increase in inventory Y, and a decrease in accounts payable Z,"
    ar_use = grab(r"(?:increase|decrease) in accounts receivable {N}", text)
    inv_use = grab(r"(?:increase|decrease) in inventory {N}", text)
    ap_use = grab(r"(?:increase|decrease) in accounts payable {N}", text)
    # "then adds an increase in accrued liabilities excluding income taxes payable X
    #  and an increase in income taxes payable Y."
    accrued_add = grab(r"accrued liabilities excluding income taxes payable {N}", text)
    taxes_payable_add = grab(r"(?:increase|decrease) in income taxes payable {N}", text)

    noncash = depreciation + amortization
    wc_uses = ar_use + inv_use + ap_use
    ocf_indirect = net_income + noncash - wc_uses + accrued_add + taxes_payable_add

    # "The direct schedule subtracts non-tax operating cash payments X and cash income
    #  taxes paid Y from operating cash receipts Z."
    nontax_payments = grab(r"non-tax operating cash payments {N}", text)
    taxes_paid = grab(r"cash income taxes paid {N}", text)
    receipts = grab(r"operating cash receipts {N}", text)
    direct_uses = nontax_payments + taxes_paid
    ocf_direct = receipts - direct_uses

    # "Normalize each schedule's operating cash flow by reported revenue R."
    revenue = grab(r"reported revenue {N}", text)
    m_indirect = ocf_indirect / revenue
    m_direct = ocf_direct / revenue

    # "score = mean of those two margins minus the square of their signed difference"
    mean = (m_indirect + m_direct) / 2
    diff = m_indirect - m_direct
    score = mean - diff ** 2

    # "Report the score as a percentage."
    final = score * 100

    return {
        "final": final,
        "slots": {
            "noncash_charges_checkpoint": noncash,
            "working_capital_cash_uses_checkpoint": wc_uses,
            "direct_cash_uses_checkpoint": direct_uses,
        },
    }
